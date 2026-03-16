#!/usr/bin/env python
"""
CLI for the Skill Assertion Pipeline.

Usage:
    python run_pipeline.py                                          # Run with defaults
    python run_pipeline.py --sample 500                             # Test with 500 rows
    python run_pipeline.py --skip-llm                               # Skip LLM steps
    python run_pipeline.py -o my_output                             # Custom output dir
    python run_pipeline.py --concordance data/concordance.xlsx      # With concordance
"""
import argparse
import sys
import os
import logging
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import CONFIG
from src.models.schema import LevelOfEngagement
from src.pipeline import SkillAssertionPipeline


def setup_logging(level="INFO", log_file="assertion_pipeline.log"):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler(log_file)],
    )


def load_input(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    if p.suffix == ".csv":
        df = pd.read_csv(path)
    elif p.suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
    elif p.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported format: {p.suffix}")

    # Standardize column names
    df.rename(columns={"skill_name": "name", "unit_code": "code"}, inplace=True)

    # Convert SkillLevel enum names to ints if needed
    level_map = {e.name: e.value for e in LevelOfEngagement}
    if "level" in df.columns:
        df["level"] = df["level"].map(lambda x: level_map.get(str(x).upper(), x))

    return df


def main():
    parser = argparse.ArgumentParser(description="Skill Assertion Pipeline")
    parser.add_argument("input", nargs="?", default="data/Extracted_Skills_TGA.xlsx", help="Input file")
    parser.add_argument("-o", "--output", default="output", help="Output directory")
    parser.add_argument("-s", "--sample", type=int, help="Sample N rows for testing")
    parser.add_argument("--concordance", help="Path to concordance Excel/CSV (code → qual → anzsco)")
    parser.add_argument("--skip-llm", action="store_true", help="Skip all LLM steps")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING"])
    parser.add_argument("--dry-run", action="store_true", help="Validate only, don't run")
    args = parser.parse_args()

    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Loading: {args.input}")
        df = load_input(args.input)
        logger.info(f"Loaded {len(df)} rows, {df.shape[1]} columns")

        if args.sample:
            df = df.sample(min(args.sample, len(df)), random_state=42)
            logger.info(f"Sampled {len(df)} rows")

        if args.dry_run:
            logger.info("Dry run — validation OK")
            logger.info(f"  Columns: {list(df.columns)}")
            logger.info(f"  Shape: {df.shape}")
            return 0

        pipeline = SkillAssertionPipeline(CONFIG)
        results = pipeline.run(
            df,
            output_dir=args.output,
            skip_genai=args.skip_llm,
            concordance_path=args.concordance,
        )

        if results["status"] == "success":
            return 0
        else:
            logger.error(f"Failed: {results.get('error')}")
            return 1

    except Exception as e:
        logger.error(str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
