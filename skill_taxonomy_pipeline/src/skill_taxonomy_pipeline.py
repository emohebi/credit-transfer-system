"""
Main entry point for the Skill Taxonomy Pipeline
Supports two modes:
1. Family Assignment (default): Assigns skills to predefined families using GenAI
2. Clustering (legacy): Uses HDBSCAN clustering for dynamic grouping

Hierarchy: Domain → Family/Cluster → Group (by Level) → Atomic Skills
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Import components
from src.embeddings.embedding_manager import EmbeddingManager, SimilarityDeduplicator
from src.taxonomy.hierarchy_builder import TaxonomyBuilder
from src.validation.taxonomy_validator import TaxonomyValidator
from src.data_processing.data_preprocessor import SkillDataPreprocessor
from src.interfaces.model_factory import ModelFactory
from config.settings import CONFIG, get_config_profile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('taxonomy_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SkillTaxonomyPipeline:
    """
    Skill Taxonomy Pipeline with configurable assignment mode
    
    Modes:
    - Family Assignment (default): Uses GenAI to assign skills to predefined families
    - Clustering (legacy): Uses HDBSCAN for dynamic skill grouping
    
    Pipeline Steps:
    1. Preprocess data
    2. Generate embeddings
    3. Find and merge duplicates (tracking alternative titles)
    4. Assign skills to families OR cluster skills
    5. Build hierarchy: Domain → Family/Cluster → Group → Skills
    6. Validate taxonomy
    7. Save results
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, 
                 profile: str = "balanced",
                 use_clustering: bool = False):
        """
        Initialize the pipeline
        
        Args:
            config: Configuration dictionary (if None, uses default CONFIG)
            profile: Configuration profile
            use_clustering: If True, use legacy HDBSCAN clustering instead of family assignment
        """
        # Load configuration
        if config is None:
            if profile != "balanced":
                self.config = get_config_profile(profile)
                logger.info(f"Using configuration profile: {profile}")
            else:
                self.config = CONFIG
        else:
            self.config = config
        
        # Mode selection
        self.use_clustering = use_clustering
        mode_name = "CLUSTERING" if use_clustering else "FAMILY ASSIGNMENT"
        
        # Log configuration
        logger.info("=" * 60)
        logger.info(f"SKILL TAXONOMY PIPELINE - {mode_name} MODE")
        logger.info("=" * 60)
        logger.info(f"Semantic Weight: {self.config['embedding'].get('semantic_weight', 0.6):.2f}")
        logger.info(f"Level Weight: {self.config['embedding'].get('level_weight', 0.25):.2f}")
        logger.info(f"Context Weight: {self.config['embedding'].get('context_weight', 0.15):.2f}")
        
        if not use_clustering:
            logger.info(f"Families: {len(self.config['taxonomy']['families'])}")
            logger.info(f"Domains: {len(self.config['taxonomy']['domains'])}")
        
        logger.info("=" * 60)
        
        # Initialize components
        self.preprocessor = SkillDataPreprocessor(self.config)
        self.embedding_manager = EmbeddingManager(self.config)
        self.deduplicator = SimilarityDeduplicator(self.config)
        
        # Initialize mode-specific components
        if use_clustering:
            # Legacy clustering mode
            from src.clustering.hierarchical_clustering import MultiFactorClusterer
            self.clusterer = MultiFactorClusterer(self.config)
            self.family_assigner = None
            self.genai_interface = None
        else:
            # Family assignment mode
            from src.clustering.family_assigner import SkillFamilyAssigner
            
            # Initialize GenAI interface
            self.genai_interface = None
            self.backed_type = self.config.get('backed_type', 'azure_openai')
            try:
                self.genai_interface = ModelFactory.create_genai_interface(self.config)
                if self.genai_interface:
                    logger.info("GenAI interface initialized for family assignment")
                else:
                    logger.warning("GenAI interface not available")
                    self.genai_interface = None
            except Exception as e:
                logger.warning(f"Could not initialize GenAI interface: {e}")
                logger.info("Will use embedding/keyword-based family assignment")
            
            # Initialize family assigner
            self.family_assigner = SkillFamilyAssigner(
                self.config,
                genai_interface=self.genai_interface,
                embedding_interface=self.embedding_manager.model
            )
            self.clusterer = None
        
        # Initialize hierarchy builder and validator
        self.hierarchy_builder = TaxonomyBuilder(self.config)
        self.validator = TaxonomyValidator(self.config)
    
    def validate_skill_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and prepare skill data
        
        Ensures required columns exist:
        - level: Skill level (1-7)
        - context: Skill context (practical/theoretical/hybrid)
        """
        required_columns = ['skill_id', 'name', 'combined_text']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
        
        if 'level' not in df.columns:
            raise Exception("'level' column is required but not found.")
        
        if 'context' not in df.columns:
            raise Exception("'context' column is required but not found.")
        
        # Normalize level values
        df['level'] = df['level'].apply(self._normalize_level)
        
        # Normalize context values
        valid_contexts = ['practical', 'theoretical', 'hybrid']
        df['context'] = df['context'].apply(
            lambda x: x.lower() if str(x).lower() in valid_contexts else 'hybrid'
        )
        
        return df
    
    def _normalize_level(self, level) -> int:
        """Normalize level to 1-7 range"""
        if hasattr(level, 'value'):
            return level.value
        try:
            level_int = int(level)
            return max(1, min(7, level_int))
        except:
            raise ValueError(f"Invalid level value: {level}")
    
    def run(self, 
            input_data: pd.DataFrame, 
            output_dir: str = "output",
            skip_genai: bool = False) -> Dict:
        """
        Run the taxonomy pipeline
        
        Args:
            input_data: DataFrame with skills data
            output_dir: Directory for output files
            skip_genai: Skip GenAI-based family assignment (use embeddings/keywords only)
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        mode_name = "Clustering" if self.use_clustering else "Family Assignment"
        
        logger.info("=" * 60)
        logger.info(f"STARTING SKILL TAXONOMY PIPELINE ({mode_name} Mode)")
        logger.info("=" * 60)
        logger.info(f"Processing {len(input_data)} skills")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now()
        
        try:
            # ================================================================
            # STEP 1: VALIDATE AND PREPROCESS DATA
            # ================================================================
            logger.info("\n[Step 1/7] Validating and preprocessing data...")
            df = self.preprocessor.preprocess(input_data)
            logger.info(f"Preprocessed {len(df)} skills")
            df = self.validate_skill_data(df)
            
            self._log_data_statistics(df)
            
            # ================================================================
            # STEP 2: GENERATE EMBEDDINGS
            # ================================================================
            logger.info("\n[Step 2/7] Generating embeddings...")
            embeddings = self.embedding_manager.generate_embeddings_for_dataframe(df)
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            
            # ================================================================
            # STEP 3: FIND AND MERGE DUPLICATES
            # ================================================================
            logger.info("\n[Step 3/7] Finding duplicates and tracking alternative titles...")
            self.embedding_manager.build_similarity_index(embeddings)
            df_with_duplicates = self.deduplicator.find_duplicates(
                df, embeddings, self.embedding_manager
            )
            
            self._log_deduplication_stats(df_with_duplicates)
            df_with_duplicates.to_excel(output_path / "df_with_duplicates.xlsx", index=False)
            
            # Merge duplicates (preserves alternative titles)
            df_unique = self.deduplicator.merge_duplicates(df_with_duplicates)
            logger.info(f"Reduced to {len(df_unique)} unique skills")
            
            # Log alternative titles statistics
            alt_titles_count = df_unique['alternative_titles'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            logger.info(f"Total alternative titles preserved: {alt_titles_count}")
            
            df_unique.to_excel(output_path / "df_unique.xlsx", index=False)
            
            # ================================================================
            # STEP 4: RE-GENERATE EMBEDDINGS FOR UNIQUE SKILLS
            # ================================================================
            logger.info("\n[Step 4/7] Re-generating embeddings for unique skills...")
            embeddings_unique = self.embedding_manager.generate_embeddings_for_dataframe(df_unique)
            
            # ================================================================
            # STEP 5: ASSIGN SKILLS TO FAMILIES OR CLUSTER
            # ================================================================
            if self.use_clustering:
                # Legacy clustering mode
                logger.info("\n[Step 5/7] Clustering skills with multi-factor features...")
                df_processed = self.clusterer.cluster_skills(df_unique, embeddings_unique)
                df_processed.to_excel(output_path / "df_clustered.xlsx", index=False)
                self._log_clustering_stats(df_processed)
            else:
                # Family assignment mode
                logger.info("\n[Step 5/7] Assigning skills to families...")
                
                if skip_genai:
                    self.family_assigner.use_genai = False
                
                df_processed = self.family_assigner.assign_families(df_unique, embeddings_unique)
                df_processed.to_excel(output_path / "df_assigned.xlsx", index=False)
                self._log_family_assignment_stats(df_processed)
            
            # ================================================================
            # STEP 6: BUILD HIERARCHY
            # ================================================================
            logger.info("\n[Step 6/7] Building taxonomy hierarchy...")
            if self.use_clustering:
                logger.info("Structure: Cluster → Group (by Level) → Skills")
            else:
                logger.info("Structure: Domain → Family → Group (by Level) → Skills")
            
            taxonomy = self.hierarchy_builder.build_hierarchy(
                df_processed, 
                embeddings=embeddings_unique,
                embedding_model=self.embedding_manager.model
            )
            
            # Save taxonomy
            with open(output_path / "taxonomy.json", 'w') as f:
                json.dump(taxonomy, f, indent=2)
            
            # Generate HTML visualization
            try:
                from src.taxonomy.generate_visualization import generate_html
                generate_html(
                    str(output_path / 'taxonomy.json'),
                    str(output_path / 'taxonomy_explorer.html')
                )
                logger.info("Generated HTML visualization")
            except Exception as e:
                logger.warning(f"Could not generate HTML visualization: {e}")
            
            # ================================================================
            # STEP 7: VALIDATE TAXONOMY
            # ================================================================
            logger.info("\n[Step 7/7] Validating taxonomy...")
            validation_results = self.validator.validate(taxonomy, df_processed)
            self._log_validation_results(validation_results)
            
            # ================================================================
            # SAVE ALL RESULTS
            # ================================================================
            logger.info("\nSaving results...")
            self._save_results(
                df_processed, 
                taxonomy, 
                validation_results,
                output_path,
                embeddings_unique
            )
            
            # Calculate final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Build results dictionary
            results = {
                'status': 'success',
                'mode': 'clustering' if self.use_clustering else 'family_assignment',
                'input_skills': len(input_data),
                'unique_skills': len(df_unique),
                'duplicates_found': len(df) - len(df_unique),
                'alternative_titles': alt_titles_count,
                'taxonomy_depth': self._get_taxonomy_depth(taxonomy),
                'processing_time': duration,
                'config': {
                    'semantic_weight': self.config['embedding'].get('semantic_weight', 0.6),
                    'level_weight': self.config['embedding'].get('level_weight', 0.25),
                    'context_weight': self.config['embedding'].get('context_weight', 0.15),
                },
                'validation': validation_results,
                'output_dir': str(output_path)
            }
            
            if self.use_clustering:
                results['clusters'] = df_processed['cluster_id'].nunique() - 1
                results['noise_points'] = (df_processed['cluster_id'] == -1).sum()
            else:
                results['families_assigned'] = df_processed['assigned_family'].nunique()
                results['unassigned_skills'] = df_processed['assigned_family'].isna().sum()
            
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Mode: {mode_name}")
            logger.info(f"Total processing time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            logger.info(f"Input skills: {results['input_skills']}")
            logger.info(f"Unique skills: {results['unique_skills']}")
            logger.info(f"Duplicates removed: {results['duplicates_found']}")
            logger.info(f"Alternative titles tracked: {results['alternative_titles']}")
            
            if self.use_clustering:
                logger.info(f"Clusters created: {results['clusters']}")
            else:
                logger.info(f"Families with skills: {results['families_assigned']}")
            
            logger.info(f"Results saved to: {output_path}")
            
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {
                'status': 'failed',
                'error': str(e)
            }
    
    def _log_data_statistics(self, df: pd.DataFrame):
        """Log statistics about skill levels and contexts"""
        logger.info("\nData Statistics:")
        
        if 'level' in df.columns:
            level_counts = df['level'].value_counts().sort_index()
            logger.info("Skill Level Distribution:")
            for level, count in level_counts.items():
                pct = (count / len(df)) * 100
                logger.info(f"  Level {level}: {count} ({pct:.1f}%)")
        
        if 'context' in df.columns:
            context_counts = df['context'].value_counts()
            logger.info("Skill Context Distribution:")
            for context, count in context_counts.items():
                pct = (count / len(df)) * 100
                logger.info(f"  {context}: {count} ({pct:.1f}%)")
    
    def _log_deduplication_stats(self, df: pd.DataFrame):
        """Log deduplication statistics"""
        total_duplicates = df['is_duplicate'].sum()
        
        if total_duplicates > 0:
            logger.info("\nDeduplication Statistics:")
            logger.info(f"  Total duplicates found: {total_duplicates}")
            
            if 'match_type' in df.columns:
                logger.info(f"  - Direct matches: {(df['match_type'] == 'direct').sum()}")
                logger.info(f"  - Partial matches: {(df['match_type'] == 'partial').sum()}")
            
            if 'match_score' in df.columns:
                avg_score = df[df['is_duplicate']]['match_score'].mean()
                logger.info(f"  Average match score: {avg_score:.3f}")
    
    def _log_family_assignment_stats(self, df: pd.DataFrame):
        """Log family assignment statistics"""
        assigned = df['assigned_family'].notna().sum()
        unassigned = df['assigned_family'].isna().sum()
        
        logger.info("\nFamily Assignment Statistics:")
        logger.info(f"  Assigned: {assigned} ({100*assigned/len(df):.1f}%)")
        logger.info(f"  Unassigned: {unassigned} ({100*unassigned/len(df):.1f}%)")
        
        if 'family_assignment_method' in df.columns:
            method_counts = df['family_assignment_method'].value_counts()
            logger.info("  Assignment methods:")
            for method, count in method_counts.items():
                if method:
                    logger.info(f"    {method}: {count}")
        
        # Top families
        family_counts = df['assigned_family'].value_counts().head(10)
        logger.info("  Top 10 families:")
        families = self.config['taxonomy']['families']
        for family_key, count in family_counts.items():
            family_name = families.get(family_key, {}).get('name', family_key)
            logger.info(f"    {family_name}: {count}")
    
    def _log_clustering_stats(self, df: pd.DataFrame):
        """Log clustering statistics (for legacy clustering mode)"""
        n_clusters = df['cluster_id'].nunique() - 1  # Exclude noise (-1)
        n_noise = (df['cluster_id'] == -1).sum()
        
        logger.info("\nClustering Statistics:")
        logger.info(f"  Total clusters: {n_clusters}")
        logger.info(f"  Noise points: {n_noise} ({100*n_noise/len(df):.1f}%)")
        
        if 'cluster_coherence' in df.columns:
            avg_coherence = df[df['cluster_id'] != -1]['cluster_coherence'].mean()
            logger.info(f"  Average cluster coherence: {avg_coherence:.3f}")
        
        # Cluster size distribution
        cluster_sizes = df[df['cluster_id'] != -1]['cluster_id'].value_counts()
        logger.info(f"  Cluster size range: {cluster_sizes.min()} - {cluster_sizes.max()}")
        logger.info(f"  Average cluster size: {cluster_sizes.mean():.1f}")
    
    def _log_validation_results(self, validation_results: Dict):
        """Log validation results"""
        logger.info("\nValidation Results:")
        logger.info(f"  Valid: {validation_results.get('is_valid', False)}")
        logger.info(f"  Coverage: {validation_results.get('coverage', 0):.1%}")
        
        metrics = validation_results.get('metrics', {})
        if 'avg_coherence' in metrics:
            logger.info(f"  Coherence: {metrics['avg_coherence']:.3f}")
        
        warnings = validation_results.get('warnings', [])
        if warnings:
            logger.warning(f"  Warnings: {len(warnings)}")
            for warning in warnings[:5]:  # Show first 5
                logger.warning(f"    - {warning}")
    
    def _get_taxonomy_depth(self, taxonomy: Dict) -> int:
        """Calculate the depth of the taxonomy tree"""
        def get_depth(node, current_depth=0):
            if not node.get('children'):
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in node['children'])
        
        return get_depth(taxonomy)
    
    def _save_results(self, df: pd.DataFrame, taxonomy: Dict, 
                     validation: Dict, output_path: Path, embeddings: np.ndarray):
        """Save all results"""
        
        # Save processed skills
        output_filename = "skills_clustered.csv" if self.use_clustering else "skills_assigned.csv"
        df.to_csv(output_path / output_filename, index=False)
        
        # Save taxonomy (already saved in run())
        with open(output_path / "taxonomy.json", 'w') as f:
            json.dump(taxonomy, f, indent=2)
        
        # Save validation results
        with open(output_path / "validation_results.json", 'w') as f:
            json.dump(validation, f, indent=2)
        
        # Save mode-specific statistics
        if self.use_clustering:
            # Save cluster statistics
            if hasattr(self.clusterer, '_generate_enhanced_cluster_stats'):
                cluster_stats = self.clusterer._generate_enhanced_cluster_stats(df, embeddings)
                stats_serializable = {}
                for cluster_id, stats in cluster_stats.items():
                    stats_copy = stats.copy()
                    if 'center' in stats_copy:
                        stats_copy['center'] = stats_copy['center'].tolist() if hasattr(stats_copy['center'], 'tolist') else stats_copy['center']
                    stats_serializable[str(cluster_id)] = stats_copy
                
                with open(output_path / "cluster_statistics.json", 'w') as f:
                    json.dump(stats_serializable, f, indent=2)
        else:
            # Save family statistics
            family_stats = self._generate_family_statistics(df)
            with open(output_path / "family_statistics.json", 'w') as f:
                json.dump(family_stats, f, indent=2)
        
        # Save configuration used
        config_summary = {
            'mode': 'clustering' if self.use_clustering else 'family_assignment',
            'multi_factor_weights': {
                'semantic': self.config['embedding'].get('semantic_weight', 0.6),
                'level': self.config['embedding'].get('level_weight', 0.25),
                'context': self.config['embedding'].get('context_weight', 0.15),
            },
            'thresholds': {
                'direct_match': self.config['dedup'].get('direct_match_threshold', 0.9),
                'partial_match': self.config['dedup'].get('partial_threshold', 0.8),
                'minimum': self.config['dedup'].get('similarity_threshold', 0.65),
            }
        }
        
        if self.use_clustering:
            config_summary['clustering'] = {
                'min_cluster_size': self.config['clustering']['min_cluster_size'],
                'use_multi_factor': self.config['clustering'].get('use_multi_factor_clustering', True),
            }
        else:
            config_summary['family_assignment'] = {
                'use_genai': self.family_assigner.use_genai if self.family_assigner else False,
                'batch_size': self.family_assigner.batch_size if self.family_assigner else 50,
                'keyword_threshold': self.family_assigner.keyword_threshold if self.family_assigner else 2,
            }
        
        with open(output_path / "pipeline_config.json", 'w') as f:
            json.dump(config_summary, f, indent=2)
        
        logger.info(f"All results saved to {output_path}")
    
    def _generate_family_statistics(self, df: pd.DataFrame) -> Dict:
        """Generate statistics for each family"""
        families = self.config['taxonomy']['families']
        domains = self.config['taxonomy']['domains']
        
        stats = {
            'summary': {
                'total_skills': len(df),
                'assigned_skills': df['assigned_family'].notna().sum(),
                'families_used': df['assigned_family'].nunique(),
                'domains_used': df['assigned_domain'].nunique() if 'assigned_domain' in df.columns else 0
            },
            'by_domain': {},
            'by_family': {}
        }
        
        # Domain statistics
        if 'assigned_domain' in df.columns:
            for domain_key in df['assigned_domain'].unique():
                if pd.isna(domain_key):
                    continue
                domain_df = df[df['assigned_domain'] == domain_key]
                domain_name = domains.get(domain_key, {}).get('name', domain_key)
                stats['by_domain'][domain_key] = {
                    'name': domain_name,
                    'skill_count': len(domain_df),
                    'family_count': domain_df['assigned_family'].nunique(),
                    'avg_level': float(domain_df['level'].mean()) if 'level' in domain_df.columns else None
                }
        
        # Family statistics
        for family_key in df['assigned_family'].unique():
            if pd.isna(family_key):
                continue
            family_df = df[df['assigned_family'] == family_key]
            family_info = families.get(family_key, {})
            
            stats['by_family'][family_key] = {
                'name': family_info.get('name', family_key),
                'domain': family_info.get('domain', 'unknown'),
                'skill_count': len(family_df),
                'avg_level': float(family_df['level'].mean()) if 'level' in family_df.columns else None,
                'level_distribution': family_df['level'].value_counts().to_dict() if 'level' in family_df.columns else {},
                'context_distribution': family_df['context'].value_counts().to_dict() if 'context' in family_df.columns else {}
            }
        
        return stats
