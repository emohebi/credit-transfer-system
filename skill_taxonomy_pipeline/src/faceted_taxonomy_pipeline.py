"""
Main entry point for the Faceted Skill Taxonomy Pipeline
Uses multi-dimensional faceted taxonomy instead of hierarchical domain/family structure

Each skill is assigned values across multiple independent facets (dimensions),
enabling flexible querying and multiple views of the same skill set.

Facets: NAT, TRF, COG, CTX, FUT, LRN, DIG, IND, LVL
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
from src.validation.taxonomy_validator import TaxonomyValidator
from src.data_processing.data_preprocessor import SkillDataPreprocessor
from src.interfaces.model_factory import ModelFactory
from src.clustering.facet_assigner import FacetAssigner
from config.settings_faceted import CONFIG, get_config_profile
from config.facets import ALL_FACETS, FACET_PRIORITY
from src.utils.converters import NpEncoder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('faceted_taxonomy_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FacetedTaxonomyPipeline:
    """
    Faceted Skill Taxonomy Pipeline
    
    Assigns skills to multiple independent facets instead of a hierarchical taxonomy.
    This enables flexible, multi-dimensional querying and visualization.
    
    Pipeline Steps:
    1. Preprocess data
    2. Generate embeddings
    3. Find and merge duplicates
    4. Assign facets to skills using embedding + LLM re-ranking
    5. Generate faceted data export
    6. Generate multi-view HTML visualization
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None, profile: str = "balanced"):
        """
        Initialize the pipeline
        
        Args:
            config: Configuration dictionary (if None, uses default CONFIG)
            profile: Configuration profile
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
        
        # Log configuration
        logger.info("=" * 60)
        logger.info("FACETED SKILL TAXONOMY PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Semantic Weight: {self.config['embedding'].get('semantic_weight', 0.6):.2f}")
        logger.info(f"Level Weight: {self.config['embedding'].get('level_weight', 0.25):.2f}")
        logger.info(f"Context Weight: {self.config['embedding'].get('context_weight', 0.15):.2f}")
        logger.info(f"Facets: {len(ALL_FACETS)}")
        logger.info(f"Facets to assign: {self.config['facet_assignment']['facets_to_assign']}")
        logger.info("=" * 60)
        
        # Initialize components
        self.preprocessor = SkillDataPreprocessor(self.config)
        self.deduplicator = SimilarityDeduplicator(self.config)
        self.embedding_manager = EmbeddingManager(self.config)
        
        # Initialize GenAI interface
        self.genai_interface = None
        self.backed_type = self.config.get('backed_type', 'vllm')
        try:
            self.genai_interface = ModelFactory.create_genai_interface(self.config)
            if self.genai_interface:
                logger.info("GenAI interface initialized for facet assignment")
            else:
                logger.warning("GenAI interface not available")
        except Exception as e:
            logger.warning(f"Could not initialize GenAI interface: {e}")
            logger.info("Will use embedding-based facet assignment only")
        
        # Initialize facet assigner
        self.facet_assigner = FacetAssigner(
            self.config,
            genai_interface=self.genai_interface,
            embedding_interface=self.embedding_manager.model
        )
        
        # Validator (simplified for faceted approach)
        self.validator = TaxonomyValidator(self.config)
    
    def validate_skill_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and prepare skill data"""
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
            output_dir: str = "output_faceted",
            skip_genai: bool = False) -> Dict:
        """
        Run the faceted taxonomy pipeline
        
        Args:
            input_data: DataFrame with skills data
            output_dir: Directory for output files
            skip_genai: Skip GenAI-based facet assignment
            
        Returns:
            Dictionary with pipeline results and statistics
        """
        logger.info("=" * 60)
        logger.info("STARTING FACETED SKILL TAXONOMY PIPELINE")
        logger.info("=" * 60)
        logger.info(f"Processing {len(input_data)} skills")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        start_time = datetime.now()
        
        try:
            # ================================================================
            # STEP 1: VALIDATE AND PREPROCESS DATA
            # ================================================================
            logger.info("\n[Step 1/6] Validating and preprocessing data...")
            df = self.preprocessor.preprocess(input_data)
            logger.info(f"Preprocessed {len(df)} skills")
            df = self.validate_skill_data(df)
            
            self._log_data_statistics(df)
            
            # ================================================================
            # STEP 2: GENERATE EMBEDDINGS
            # ================================================================
            logger.info("\n[Step 2/6] Generating embeddings...")
            embeddings = self.embedding_manager.generate_embeddings_for_dataframe(df)
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            
            # ================================================================
            # STEP 3: FIND AND MERGE DUPLICATES
            # ================================================================
            logger.info("\n[Step 3/6] Finding duplicates and tracking alternative titles...")
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
            logger.info("\n[Step 4/6] Re-generating embeddings for unique skills...")
            embeddings_unique = self.embedding_manager.generate_embeddings_for_dataframe(df_unique)
            
            # ================================================================
            # STEP 5: ASSIGN FACETS TO SKILLS
            # ================================================================
            logger.info("\n[Step 5/6] Assigning facets to skills...")
            
            if skip_genai:
                self.facet_assigner.use_genai = False
                self.facet_assigner.use_llm_reranking = False
            
            df_faceted = self.facet_assigner.assign_facets(df_unique, embeddings_unique)
            df_faceted.to_excel(output_path / "df_faceted.xlsx", index=False)
            
            # ================================================================
            # STEP 6: GENERATE OUTPUTS
            # ================================================================
            logger.info("\n[Step 6/6] Generating outputs...")
            
            # Get faceted skill data for visualization
            skills_data = self.facet_assigner.get_faceted_skill_data(df_faceted, embeddings_unique)
            
            # Generate statistics
            statistics = self._generate_statistics(df_faceted, skills_data)
            
            # Create export data structure
            export_data = {
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "pipeline_version": "2.0.0-faceted",
                    "total_skills": len(skills_data),
                    "facets": list(ALL_FACETS.keys()),
                    "statistics": statistics
                },
                "facets": {
                    facet_id: {
                        "name": facet_info["facet_name"],
                        "description": facet_info["description"],
                        "values": {
                            code: {
                                "name": val.get("name", code),
                                "description": val.get("description", "")
                            }
                            for code, val in facet_info["values"].items()
                        }
                    }
                    for facet_id, facet_info in ALL_FACETS.items()
                },
                "skills": skills_data
            }
            
            # Save JSON export
            with open(output_path / "faceted_taxonomy.json", 'w') as f:
                json.dump(export_data, f, indent=2, cls=NpEncoder)
            
            # Generate HTML visualization
            try:
                from src.taxonomy.generate_faceted_visualization import generate_faceted_html
                generate_faceted_html(
                    str(output_path / 'faceted_taxonomy.json'),
                    str(output_path / 'faceted_explorer.html')
                )
                logger.info("Generated faceted HTML visualization")
            except Exception as e:
                logger.warning(f"Could not generate HTML visualization: {e}")
            
            # Save statistics
            with open(output_path / "statistics.json", 'w') as f:
                json.dump(statistics, f, indent=2, cls=NpEncoder)
            
            # Calculate final statistics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Build results dictionary
            results = {
                'status': 'success',
                'mode': 'faceted_taxonomy',
                'input_skills': len(input_data),
                'unique_skills': len(df_unique),
                'duplicates_found': len(df) - len(df_unique),
                'alternative_titles': alt_titles_count,
                'facets_assigned': len(self.config['facet_assignment']['facets_to_assign']),
                'processing_time': duration,
                'statistics': statistics,
                'output_dir': str(output_path)
            }
            
            logger.info("\n" + "=" * 60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Mode: Faceted Taxonomy")
            logger.info(f"Total processing time: {duration:.2f} seconds ({duration/60:.1f} minutes)")
            logger.info(f"Input skills: {results['input_skills']}")
            logger.info(f"Unique skills: {results['unique_skills']}")
            logger.info(f"Duplicates removed: {results['duplicates_found']}")
            logger.info(f"Alternative titles tracked: {results['alternative_titles']}")
            logger.info(f"Facets assigned: {results['facets_assigned']}")
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
        
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            logger.info("Skill Category Distribution:")
            for category, count in category_counts.items():
                pct = (count / len(df)) * 100
                logger.info(f"  {category}: {count} ({pct:.1f}%)")
    
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
    
    def _generate_statistics(self, df: pd.DataFrame, skills_data: list) -> Dict:
        """Generate comprehensive statistics"""
        stats = {
            "total_skills": len(skills_data),
            "total_unique_codes": 0,
            "total_alternative_titles": 0,
            "total_related_keywords": 0,
            "facet_coverage": {},
            "facet_distributions": {}
        }
        
        # Count unique codes and keywords
        all_codes = set()
        all_keywords = set()
        total_alt_titles = 0
        
        for skill in skills_data:
            codes = skill.get('all_related_codes', [])
            if isinstance(codes, list):
                all_codes.update(codes)
            
            kws = skill.get('all_related_kw', [])
            if isinstance(kws, list):
                all_keywords.update(kws)
            
            alt_titles = skill.get('alternative_titles', [])
            if isinstance(alt_titles, list):
                total_alt_titles += len(alt_titles)
        
        stats["total_unique_codes"] = len(all_codes)
        stats["total_related_keywords"] = len(all_keywords)
        stats["total_alternative_titles"] = total_alt_titles
        
        # Facet statistics
        facets_to_assign = self.config['facet_assignment']['facets_to_assign']
        
        for facet_id in facets_to_assign:
            col = f'facet_{facet_id}'
            if col not in df.columns:
                continue
            
            assigned_count = df[col].notna().sum()
            coverage = assigned_count / len(df) if len(df) > 0 else 0
            
            stats["facet_coverage"][facet_id] = {
                "name": ALL_FACETS.get(facet_id, {}).get("facet_name", facet_id),
                "assigned": int(assigned_count),
                "coverage": float(coverage)
            }
            
            # Value distribution
            value_counts = df[col].value_counts().to_dict()
            stats["facet_distributions"][facet_id] = {
                str(k): int(v) for k, v in value_counts.items() if pd.notna(k)
            }
        
        # Category distribution (from original data)
        if 'category' in df.columns:
            stats["category_distribution"] = df['category'].value_counts().to_dict()
        
        # Level distribution
        if 'level' in df.columns:
            stats["level_distribution"] = df['level'].value_counts().sort_index().to_dict()
        
        # Context distribution
        if 'context' in df.columns:
            stats["context_distribution"] = df['context'].value_counts().to_dict()
        
        return stats


# Backwards compatibility alias
SkillTaxonomyPipeline = FacetedTaxonomyPipeline
