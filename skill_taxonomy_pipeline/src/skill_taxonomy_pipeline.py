"""
Main entry point for the Skill Taxonomy Pipeline with Multi-Factor Matching
Uses enhanced components that consider semantic similarity, skill levels, and context
"""

import argparse
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json
import sys
from typing import Dict, Any, Optional

# Import the ENHANCED components for multi-factor matching
from src.embeddings.embedding_manager import EmbeddingManager, SimilarityDeduplicator
from src.clustering.hierarchical_clustering import MultiFactorClusterer
from src.taxonomy.hierarchy_builder import TaxonomyBuilder
from src.validation.taxonomy_validator import TaxonomyValidator
from src.data_processing.data_preprocessor import SkillDataPreprocessor
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
    Enhanced pipeline with multi-factor skill matching
    Considers semantic similarity, skill levels, and context throughout the process
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, profile: str = "balanced"):
        """
        Initialize the enhanced pipeline
        
        Args:
            config: Configuration dictionary (if None, uses default CONFIG)
            profile: Configuration profile ('balanced', 'level_aware', 'semantic_focused', 'context_sensitive')
        """
        # Load configuration with specified profile
        if config is None:
            if profile != "balanced":
                self.config = get_config_profile(profile)
                logger.info(f"Using configuration profile: {profile}")
            else:
                self.config = CONFIG
        else:
            self.config = config
        
        # Log multi-factor weights
        logger.info("=" * 60)
        logger.info("MULTI-FACTOR MATCHING CONFIGURATION")
        logger.info("=" * 60)
        logger.info(f"Semantic Weight: {self.config['embedding'].get('semantic_weight', 0.6):.2f}")
        logger.info(f"Level Weight: {self.config['embedding'].get('level_weight', 0.25):.2f}")
        logger.info(f"Context Weight: {self.config['embedding'].get('context_weight', 0.15):.2f}")
        logger.info(f"Direct Match Threshold: {self.config['dedup'].get('direct_match_threshold', 0.9):.2f}")
        logger.info(f"Partial Match Threshold: {self.config['dedup'].get('partial_threshold', 0.8):.2f}")
        logger.info("=" * 60)
        
        # Initialize ENHANCED components
        self.preprocessor = SkillDataPreprocessor(self.config)
        self.embedding_manager = EmbeddingManager(self.config)
        self.deduplicator = SimilarityDeduplicator(self.config)
        self.clusterer = MultiFactorClusterer(self.config)
        self.hierarchy_builder = TaxonomyBuilder(self.config)
        self.validator = TaxonomyValidator(self.config)
        
        # Initialize LLM refiner if configured
        self.llm_refiner = None
        self.backed_type = self.config['backed_type']
        if self.config.get('llm', {})[self.backed_type].get('api_key'):
            try:
                from src.llm_integration.openai_refiner import LLMTaxonomyRefiner
                self.llm_refiner = LLMTaxonomyRefiner(self.config['llm'][self.backed_type])
                logger.info("LLM refiner initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize LLM refiner: {e}")
    
    def validate_skill_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and prepare skill data for multi-factor processing
        
        Ensures required columns exist for multi-factor matching:
        - level: Skill level (1-7 or SkillLevel enum)
        - context: Skill context (practical/theoretical/hybrid)
        """
        required_columns = ['skill_id', 'name', 'combined_text']
        
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in data")
        
        # Add level column if missing (with warning)
        if 'level' not in df.columns:
            raise Exception("'level' column is required for multi-factor matching but not found.")
        
        # Add context column if missing
        if 'context' not in df.columns:
            raise Exception("'context' column is required for multi-factor matching but not found.")
        
        # Validate level values (1-7 range)
        if 'level' in df.columns:
            df['level'] = df['level'].apply(self._normalize_level)
        
        # Validate context values
        if 'context' in df.columns:
            valid_contexts = ['practical', 'theoretical', 'hybrid']
            df['context'] = df['context'].apply(
                lambda x: x.lower() if str(x).lower() in valid_contexts else 'hybrid'
            )
        
        return df
    
    def _normalize_level(self, level) -> int:
        """Normalize level to 1-7 range"""
        if hasattr(level, 'value'):  # Enum
            return level.value
        try:
            level_int = int(level)
            return max(1, min(7, level_int))  # Clamp to 1-7
        except:
            raise ValueError(f"Invalid level value: {level}")
    
    def run(self, 
            input_data: pd.DataFrame, 
            output_dir: str = "output",
            use_llm_refinement: bool = None) -> Dict:
        """
        Run the enhanced taxonomy pipeline with multi-factor matching
        
        Args:
            input_data: DataFrame with skills data
            output_dir: Directory for output files
            use_llm_refinement: Whether to use LLM for refinement (None = use config)
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("=" * 60)
        logger.info("STARTING ENHANCED SKILL TAXONOMY PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Processing {len(input_data)} skills with multi-factor matching")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Track processing time
        start_time = datetime.now()
        
        try:
            # 1. VALIDATE AND PREPROCESS DATA
            logger.info("\n[Step 1] Validating and preprocessing data...")
            df = self.preprocessor.preprocess(input_data)
            logger.info(f"Preprocessed {len(df)} skills")
            df = self.validate_skill_data(df)
            
            # Log level and context distribution
            self._log_data_statistics(df)
            
            # 2. GENERATE EMBEDDINGS
            logger.info("\n[Step 2] Generating embeddings...")
            embeddings = self.embedding_manager.generate_embeddings_for_dataframe(df)
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            
            # 3. MULTI-FACTOR DEDUPLICATION
            logger.info("\n[Step 3] Finding duplicates with multi-factor matching...")
            self.embedding_manager.build_similarity_index(embeddings)
            df_with_duplicates = self.deduplicator.find_duplicates(
                df, embeddings, self.embedding_manager
            )
            
            # Log deduplication statistics
            self._log_deduplication_stats(df_with_duplicates)
            df_with_duplicates.to_excel(output_path / "df_with_duplicates.xlsx", index=False)
            # Merge duplicates
            df_unique = self.deduplicator.merge_duplicates(df_with_duplicates)
            logger.info(f"Reduced to {len(df_unique)} unique skills")
            df_unique.to_excel(output_path / "df_unique.xlsx", index=False)
            # 4. RE-GENERATE EMBEDDINGS FOR UNIQUE SKILLS
            logger.info("\n[Step 4] Re-generating embeddings for unique skills...")
            embeddings_unique = self.embedding_manager.generate_embeddings_for_dataframe(df_unique)
            
            # 5. MULTI-FACTOR CLUSTERING
            logger.info("\n[Step 5] Clustering with multi-factor features...")
            df_clustered = self.clusterer.cluster_skills(df_unique, embeddings_unique)
            df_clustered.to_excel(output_path / "df_clustered.xlsx", index=False)
            # Log clustering statistics
            self._log_clustering_stats(df_clustered)
             
            # 6. BUILD HIERARCHY
            logger.info("\n[Step 6] Building taxonomy hierarchy...")
            taxonomy = self.hierarchy_builder.build_hierarchy(df_clustered)
            with open(output_path / "taxonomy.json", 'w') as f:
                json.dump(taxonomy, f, indent=2)
            # 7. LLM REFINEMENT (if configured)
            if use_llm_refinement or (use_llm_refinement is None and self.config['hierarchy']['use_llm_refinement']):
                if self.llm_refiner:
                    logger.info("\n[Step 7] Refining taxonomy with LLM...")
                    # Get cluster representatives with multi-factor consideration
                    cluster_representatives = self.clusterer.get_cluster_representatives(
                        df_clustered, embeddings_unique, n_representatives=5
                    )
                    cluster_stats = self.clusterer._generate_enhanced_cluster_stats(
                        df_clustered, embeddings_unique
                    )
                    
                    # Generate names
                    cluster_names = self.llm_refiner.generate_cluster_names(
                        cluster_representatives, cluster_stats
                    )
                    
                    # Apply names to taxonomy
                    self._apply_cluster_names(taxonomy, cluster_names)
                    
                    # Validate and refine
                    is_valid, issues = self.llm_refiner.validate_taxonomy_structure(taxonomy)
                    if not is_valid:
                        logger.warning(f"Taxonomy validation issues: {issues}")
                else:
                    logger.info("[Step 7] Skipping LLM refinement (not configured)")
            
            # 8. VALIDATE TAXONOMY
            logger.info("\n[Step 8] Validating taxonomy...")
            validation_results = self.validator.validate(taxonomy, df_clustered)
            self._log_validation_results(validation_results)
            
            # 9. SAVE RESULTS
            logger.info("\n[Step 9] Saving results...")
            self._save_results(
                df_clustered, 
                taxonomy, 
                validation_results,
                output_path,
                embeddings_unique
            )
            
            # Calculate final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            results = {
                'status': 'success',
                'input_skills': len(input_data),
                'unique_skills': len(df_unique),
                'duplicates_found': len(df) - len(df_unique),
                'clusters': len(df_clustered['cluster_id'].unique()) - 1,  # Exclude noise
                'noise_points': (df_clustered['cluster_id'] == -1).sum(),
                'taxonomy_depth': self._get_taxonomy_depth(taxonomy),
                'processing_time': duration,
                'multi_factor_config': {
                    'semantic_weight': self.config['embedding'].get('semantic_weight', 0.6),
                    'level_weight': self.config['embedding'].get('level_weight', 0.25),
                    'context_weight': self.config['embedding'].get('context_weight', 0.15),
                },
                'validation': validation_results,
                'output_dir': str(output_path)
            }
            
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Total processing time: {duration:.2f} seconds")
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
        """Log detailed deduplication statistics"""
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
    
    def _log_clustering_stats(self, df: pd.DataFrame):
        """Log detailed clustering statistics"""
        n_clusters = df['cluster_id'].nunique() - 1  # Exclude noise
        n_noise = (df['cluster_id'] == -1).sum()
        
        logger.info("\nClustering Statistics:")
        logger.info(f"  Total clusters: {n_clusters}")
        logger.info(f"  Noise points: {n_noise} ({100*n_noise/len(df):.1f}%)")
        
        if 'cluster_coherence' in df.columns:
            avg_coherence = df[df['cluster_id'] != -1]['cluster_coherence'].mean()
            logger.info(f"  Average cluster coherence: {avg_coherence:.3f}")
        
        if 'cluster_level' in df.columns:
            # Show level distribution across clusters
            cluster_levels = df[df['cluster_id'] != -1].groupby('cluster_id')['cluster_level'].first()
            level_dist = cluster_levels.value_counts().sort_index()
            logger.info("  Cluster level distribution:")
            for level, count in level_dist.items():
                logger.info(f"    Level {level}: {count} clusters")
    
    def _log_validation_results(self, validation_results: Dict):
        """Log validation results"""
        logger.info("\nValidation Results:")
        logger.info(f"  Coverage: {validation_results.get('coverage', 0):.1%}")
        logger.info(f"  Coherence: {validation_results.get('avg_coherence', 0):.3f}")
        logger.info(f"  Distinctiveness: {validation_results.get('avg_distinctiveness', 0):.3f}")
        
        if validation_results.get('warnings'):
            logger.warning("Validation warnings:")
            for warning in validation_results['warnings']:
                logger.warning(f"  - {warning}")
    
    def _apply_cluster_names(self, taxonomy: Dict, cluster_names: Dict):
        """Apply LLM-generated names to taxonomy"""
        # Implementation depends on taxonomy structure
        pass
    
    def _get_taxonomy_depth(self, taxonomy: Dict) -> int:
        """Calculate the depth of the taxonomy tree"""
        def get_depth(node, current_depth=0):
            if not node.get('children'):
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in node['children'])
        
        return get_depth(taxonomy)
    
    def _save_results(self, df: pd.DataFrame, taxonomy: Dict, 
                     validation: Dict, output_path: Path, embeddings: np.ndarray):
        """Save all results with multi-factor information"""
        import numpy as np
        
        # Save clustered skills with multi-factor metadata
        df.to_csv(output_path / "skills_clustered.csv", index=False)
        
        # Save taxonomy
        with open(output_path / "taxonomy.json", 'w') as f:
            json.dump(taxonomy, f, indent=2)
        
        # Save validation results
        with open(output_path / "validation_results.json", 'w') as f:
            json.dump(validation, f, indent=2)
        
        # Save cluster statistics
        if hasattr(self.clusterer, '_generate_enhanced_cluster_stats'):
            cluster_stats = self.clusterer._generate_enhanced_cluster_stats(df, embeddings)
            # Convert numpy arrays to lists for JSON serialization
            stats_serializable = {}
            for cluster_id, stats in cluster_stats.items():
                stats_copy = stats.copy()
                if 'center' in stats_copy:
                    stats_copy['center'] = stats_copy['center'].tolist() if hasattr(stats_copy['center'], 'tolist') else stats_copy['center']
                stats_serializable[str(cluster_id)] = stats_copy
            
            with open(output_path / "cluster_statistics.json", 'w') as f:
                json.dump(stats_serializable, f, indent=2)
        
        # Save configuration used
        config_summary = {
            'multi_factor_weights': {
                'semantic': self.config['embedding'].get('semantic_weight', 0.6),
                'level': self.config['embedding'].get('level_weight', 0.25),
                'context': self.config['embedding'].get('context_weight', 0.15),
            },
            'thresholds': {
                'direct_match': self.config['dedup'].get('direct_match_threshold', 0.9),
                'partial_match': self.config['dedup'].get('partial_threshold', 0.8),
                'minimum': self.config['dedup'].get('similarity_threshold', 0.65),
            },
            'clustering': {
                'min_cluster_size': self.config['clustering']['min_cluster_size'],
                'use_multi_factor': self.config['clustering'].get('use_multi_factor_clustering', True),
            }
        }
        
        with open(output_path / "pipeline_config.json", 'w') as f:
            json.dump(config_summary, f, indent=2)
        
        logger.info(f"All results saved to {output_path}")


# def main():
#     """Main entry point with CLI"""
#     parser = argparse.ArgumentParser(
#         description='Build skill taxonomy with multi-factor matching (semantic, level, context)'
#     )
#     parser.add_argument(
#         'input_file',
#         help='Path to input CSV file with skills data'
#     )
#     parser.add_argument(
#         '-o', '--output',
#         default='output',
#         help='Output directory (default: output)'
#     )
#     parser.add_argument(
#         '--profile',
#         choices=['balanced', 'level_aware', 'semantic_focused', 'context_sensitive'],
#         default='balanced',
#         help='Configuration profile for multi-factor weights'
#     )
#     parser.add_argument(
#         '--similarity-method',
#         choices=['faiss', 'matrix'],
#         help='Similarity calculation method'
#     )
#     parser.add_argument(
#         '--semantic-weight',
#         type=float,
#         help='Weight for semantic similarity (0-1)'
#     )
#     parser.add_argument(
#         '--level-weight',
#         type=float,
#         help='Weight for level compatibility (0-1)'
#     )
#     parser.add_argument(
#         '--context-weight',
#         type=float,
#         help='Weight for context compatibility (0-1)'
#     )
#     parser.add_argument(
#         '--use-llm',
#         action='store_true',
#         help='Use LLM for taxonomy refinement'
#     )
#     parser.add_argument(
#         '--no-llm',
#         action='store_true',
#         help='Disable LLM refinement'
#     )
#     parser.add_argument(
#         '--sample',
#         type=int,
#         help='Process only a sample of skills for testing'
#     )
#     parser.add_argument(
#         '--debug',
#         action='store_true',
#         help='Enable debug logging'
#     )
    
#     args = parser.parse_args()
    
#     # Set logging level
#     if args.debug:
#         logging.getLogger().setLevel(logging.DEBUG)
    
#     # Load input data
#     logger.info(f"Loading data from {args.input_file}")
#     df = pd.read_csv(args.input_file)
    
#     # Sample if requested
#     if args.sample:
#         df = df.sample(min(args.sample, len(df)), random_state=42)
#         logger.info(f"Using sample of {len(df)} skills")
    
#     # Override configuration if weights provided
#     config_overrides = {}
#     if args.similarity_method:
#         config_overrides['embedding'] = {'similarity_method': args.similarity_method}
    
#     if args.semantic_weight is not None:
#         config_overrides.setdefault('embedding', {})['semantic_weight'] = args.semantic_weight
#         config_overrides.setdefault('dedup', {})['semantic_weight'] = args.semantic_weight
#         config_overrides.setdefault('clustering', {})['semantic_weight'] = args.semantic_weight
    
#     if args.level_weight is not None:
#         config_overrides.setdefault('embedding', {})['level_weight'] = args.level_weight
#         config_overrides.setdefault('dedup', {})['level_weight'] = args.level_weight
#         config_overrides.setdefault('clustering', {})['level_weight'] = args.level_weight
    
#     if args.context_weight is not None:
#         config_overrides.setdefault('embedding', {})['context_weight'] = args.context_weight
#         config_overrides.setdefault('dedup', {})['context_weight'] = args.context_weight
#         config_overrides.setdefault('clustering', {})['context_weight'] = args.context_weight
    
#     # Merge overrides with profile config
#     if config_overrides:
#         from config.settings import get_config_profile
#         config = get_config_profile(args.profile)
#         for key, value in config_overrides.items():
#             config[key].update(value)
#     else:
#         config = None
    
#     # Determine LLM usage
#     use_llm = None
#     if args.use_llm:
#         use_llm = True
#     elif args.no_llm:
#         use_llm = False
    
#     # Initialize and run pipeline
#     pipeline = SkillTaxonomyPipeline(config=config, profile=args.profile)
#     results = pipeline.run(
#         df,
#         output_dir=args.output,
#         use_llm_refinement=use_llm
#     )
    
#     # Print summary
#     if results['status'] == 'success':
#         print("\n" + "=" * 60)
#         print("PIPELINE COMPLETED SUCCESSFULLY")
#         print("=" * 60)
#         print(f"Input skills: {results['input_skills']}")
#         print(f"Unique skills: {results['unique_skills']}")
#         print(f"Duplicates removed: {results['duplicates_found']}")
#         print(f"Clusters created: {results['clusters']}")
#         print(f"Taxonomy depth: {results['taxonomy_depth']}")
#         print(f"Processing time: {results['processing_time']:.2f} seconds")
#         print(f"Results saved to: {results['output_dir']}")
#         print("\nMulti-factor configuration used:")
#         for factor, weight in results['multi_factor_config'].items():
#             print(f"  {factor}: {weight:.2f}")
#     else:
#         print(f"\nPipeline failed: {results.get('error')}")
#         sys.exit(1)


# if __name__ == "__main__":
#     main()