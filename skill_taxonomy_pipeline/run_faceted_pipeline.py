#!/usr/bin/env python
"""
Command-line interface for the Faceted Skill Taxonomy Pipeline
Uses multi-dimensional faceted taxonomy instead of hierarchical domain/family structure
"""

import argparse
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
from typing import Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.faceted_taxonomy_pipeline import FacetedTaxonomyPipeline
from config.settings_faceted import CONFIG, get_config_profile
from src.models.enum import SkillLevel


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None):
    """Setup logging configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


def load_input_file(file_path: str) -> pd.DataFrame:
    """Validate and load input file"""
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    # Determine file type and load
    if path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path)
    elif path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, nrows=2000)
    elif path.suffix.lower() == '.parquet':
        df = pd.read_parquet(file_path)
    elif path.suffix.lower() == '.json':
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    # Rename columns to standard names
    df.rename(columns={"skill_name": "name", "unit_code": "code"}, inplace=True)
    
    # Convert SkillLevel enum to int
    skill_level_val_dict = {level.name: level.value for level in SkillLevel}
    df['level'] = df['level'].map(skill_level_val_dict)
    df['level'] = df['level'].astype(int)
    
    # Validate required columns
    required_columns = ['name', 'code', 'description', 'category', 
                       'level', 'context', 'keywords', 'confidence', 'evidence']
    
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return df


def load_config(config_file: Optional[str] = None, profile: str = "balanced") -> dict:
    """Load configuration from file or use defaults"""
    config = get_config_profile(profile)
    
    if config_file:
        path = Path(config_file)
        if path.exists():
            if path.suffix == '.json':
                with open(path, 'r') as f:
                    custom_config = json.load(f)
            elif path.suffix in ['.py', '.python']:
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_config", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                custom_config = module.CONFIG
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
            
            config.update(custom_config)
        else:
            logging.warning(f"Config file not found: {config_file}")
    
    return config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Faceted Skill Taxonomy Pipeline - Build multi-dimensional skill taxonomies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Run with default settings
        python run_faceted_pipeline.py data/skills.csv
        
        # Run with custom output directory
        python run_faceted_pipeline.py data/skills.csv -o output/my_taxonomy
        
        # Run with sample for testing
        python run_faceted_pipeline.py data/skills.csv --sample 1000
        
        # Run without LLM (embedding-only facet assignment)
        python run_faceted_pipeline.py data/skills.csv --skip-llm
        
        # Run with GPU and verbose logging
        python run_faceted_pipeline.py data/skills.csv --use-gpu --log-level DEBUG
        """
    )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        default="output_faceted",
        help="Output directory (default: output_faceted)"
    )
    
    parser.add_argument(
        "-c", "--config",
        help="Path to custom configuration file (JSON or Python)"
    )
    
    parser.add_argument(
        "-s", "--sample",
        type=int,
        help="Use a random sample of N skills for testing"
    )
    
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        help="Minimum confidence threshold for skills (0-1)"
    )
    
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Use GPU for embedding generation if available"
    )
    
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM-based facet assignment (use embeddings only)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        help="Batch size for processing"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        help="Path to log file (default: faceted_taxonomy_pipeline.log)"
    )
    
    parser.add_argument(
        "--profile",
        choices=["balanced", "semantic_focused", "level_aware", "context_sensitive"],
        default="balanced",
        help="Configuration profile (default: balanced)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input and configuration without running pipeline"
    )
    
    args = parser.parse_args()
    
    # Hardcode input file for this example (can be changed)
    args.input_file = "data/Extracted_Skills_TGA.xlsx"
    args.use_gpu = True
    
    # Setup logging
    setup_logging(args.log_level, args.log_file or "faceted_taxonomy_pipeline.log")
    logger = logging.getLogger(__name__)
    
    try:
        # Load and validate input
        logger.info(f"Loading input file: {args.input_file}")
        df = load_input_file(args.input_file)
        logger.info(f"Loaded {len(df)} skills")
        
        # Sample if requested
        if args.sample:
            df = df.sample(min(args.sample, len(df)), random_state=42)
            logger.info(f"Using sample of {len(df)} skills")
        
        # Load configuration
        config = load_config(args.config, args.profile)
        
        # Apply command-line overrides
        if args.confidence_threshold:
            config['data']['confidence_threshold'] = args.confidence_threshold
        
        if args.use_gpu:
            config['embedding']['device'] = 'cuda'
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        
        if args.batch_size:
            config['data']['batch_size'] = args.batch_size
            config['embedding']['batch_size'] = args.batch_size
        
        # Dry run check
        if args.dry_run:
            logger.info("Dry run mode - validation successful")
            logger.info(f"Configuration profile: {args.profile}")
            logger.info(f"Input shape: {df.shape}")
            logger.info(f"Output directory: {args.output}")
            logger.info(f"Facets to assign: {config['facet_assignment']['facets_to_assign']}")
            return 0
        
        # Initialize and run pipeline
        logger.info("Initializing faceted taxonomy pipeline...")
        pipeline = FacetedTaxonomyPipeline(config, profile=args.profile)
        
        logger.info("Starting pipeline execution...")
        results = pipeline.run(df, output_dir=args.output, skip_genai=False)
        
        # Print results
        if results.get('status') == 'success':
            logger.info("=" * 60)
            logger.info("FACETED TAXONOMY PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("=" * 60)
            logger.info(f"Total time: {results['processing_time']/60:.2f} minutes")
            logger.info(f"Input skills: {results['input_skills']}")
            logger.info(f"Unique skills: {results['unique_skills']}")
            logger.info(f"Duplicates removed: {results['duplicates_found']}")
            logger.info(f"Alternative titles: {results['alternative_titles']}")
            logger.info(f"Facets assigned: {results['facets_assigned']}")
            logger.info(f"Output directory: {results['output_dir']}")
            
            # Print output file locations
            output_path = Path(results['output_dir'])
            logger.info("\nGenerated files:")
            logger.info(f"  - Faceted skills: {output_path}/df_faceted.xlsx")
            logger.info(f"  - Taxonomy JSON: {output_path}/faceted_taxonomy.json")
            logger.info(f"  - HTML Explorer: {output_path}/faceted_explorer.html")
            logger.info(f"  - Statistics: {output_path}/statistics.json")
            
            return 0
        else:
            logger.error(f"Pipeline failed: {results.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
