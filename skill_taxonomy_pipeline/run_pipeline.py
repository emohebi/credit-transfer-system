#!/usr/bin/env python
"""
Command-line interface for the Skill Taxonomy Pipeline
Provides a user-friendly way to run the pipeline with various options
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
# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.skill_taxonomy_pipeline import SkillTaxonomyPipeline
from config.settings import CONFIG, get_config_profile
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
        df = pd.read_excel(file_path, nrows=10000)
    elif path.suffix.lower() == '.parquet':
        df = pd.read_parquet(file_path)
    elif path.suffix.lower() == '.json':
        df = pd.read_json(file_path)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")
    
    df.rename(columns={"skill_name": "name", "unit_code": "code"}, inplace=True)
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
                # Import Python config file
                import importlib.util
                spec = importlib.util.spec_from_file_location("custom_config", path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                custom_config = module.CONFIG
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
            
            # Merge configs
            config.update(custom_config)
        else:
            logging.warning(f"Config file not found: {config_file}")
    
    return config


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Skill Taxonomy Pipeline - Build hierarchical taxonomies from skill data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
        Examples:
        # Run with default settings
        python run_pipeline.py data/skills.csv
        
        # Run with custom output directory
        python run_pipeline.py data/skills.csv -o output/my_taxonomy
        
        # Run with sample for testing
        python run_pipeline.py data/skills.csv --sample 1000
        
        # Run with custom config
        python run_pipeline.py data/skills.csv --config config/custom.json
        
        # Run with GPU and verbose logging
        python run_pipeline.py data/skills.csv --use-gpu --log-level DEBUG
        """
    )
    
    # Required arguments
    # parser.add_argument(
    #     "input_file",
    #     help="Path to input file (CSV, Excel, Parquet, or JSON)"
    # )
    
    # Optional arguments
    parser.add_argument(
        "-o", "--output",
        default="output",
        help="Output directory (default: output)"
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
        "--min-cluster-size",
        type=int,
        help="Minimum cluster size for HDBSCAN"
    )
    
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Use GPU for embedding generation if available"
    )
    
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM refinement step"
    )
    
    parser.add_argument(
        "--skip-dedup",
        action="store_true",
        help="Skip deduplication step"
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
        help="Path to log file (default: taxonomy_pipeline.log)"
    )
    
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable profiling for performance analysis"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input and configuration without running pipeline"
    )
    
    args = parser.parse_args()
    args.input_file = "data/Extracted_Skills_TGA.xlsx"  # Hardcoded for this example
    args.use_gpu = True  # Hardcoded for this example
    # Setup logging
    setup_logging(args.log_level, args.log_file or "taxonomy_pipeline.log")
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
        config = load_config(args.config)
        # print(json.dumps(config, indent=2))
        # Apply command-line overrides
        if args.confidence_threshold:
            config['data']['confidence_threshold'] = args.confidence_threshold
        
        if args.min_cluster_size:
            config['clustering']['min_cluster_size'] = args.min_cluster_size
        
        if args.use_gpu:
            config['embedding']['device'] = 'cuda'
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
        
        if args.skip_llm:
            config['llm']['api_key'] = None
        
        if args.batch_size:
            config['data']['batch_size'] = args.batch_size
            config['embedding']['batch_size'] = args.batch_size
        
        # Dry run check
        if args.dry_run:
            logger.info("Dry run mode - validation successful")
            logger.info(f"Configuration: {json.dumps(config, indent=2)}")
            logger.info(f"Input shape: {df.shape}")
            logger.info(f"Output directory: {args.output}")
            return 0
        
        # Run pipeline
        if args.profile:
            import cProfile
            import pstats
            
            profiler = cProfile.Profile()
            profiler.enable()
        
        # Initialize and run pipeline
        logger.info("Initializing pipeline...")
        pipeline = SkillTaxonomyPipeline(config)
        
        logger.info("Starting pipeline execution...")
        results = pipeline.run(df, output_dir=args.output)
        
        if args.profile:
            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            stats.print_stats(20)
            
            # Save profile data
            profile_file = Path(args.output) / "profile_stats.prof"
            stats.dump_stats(str(profile_file))
            logger.info(f"Profile data saved to: {profile_file}")
        
        # Print results
        if results['success']:
            logger.info("="*60)
            logger.info("PIPELINE COMPLETED SUCCESSFULLY")
            logger.info("="*60)
            logger.info(f"Total time: {results['total_time']/60:.2f} minutes")
            logger.info(f"Input skills: {results['input_skills']}")
            logger.info(f"Unique skills: {results['unique_skills']}")
            logger.info(f"Clusters: {results['clusters']}")
            logger.info(f"Taxonomy nodes: {results['taxonomy_nodes']}")
            logger.info(f"Output directory: {results['output_dir']}")
            
            # Print output file locations
            output_path = Path(results['output_dir'])
            logger.info("\nGenerated files:")
            logger.info(f"  - Processed data: {output_path}/processed_skills.csv")
            logger.info(f"  - Clustered data: {output_path}/clustered_skills.csv")
            logger.info(f"  - Taxonomy: {output_path}/taxonomy/taxonomy.json")
            logger.info(f"  - Flat taxonomy: {output_path}/taxonomy/taxonomy_flat.csv")
            logger.info(f"  - Report: {output_path}/pipeline_report.json")
            
            return 0
        else:
            logger.error(f"Pipeline failed: {results.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
