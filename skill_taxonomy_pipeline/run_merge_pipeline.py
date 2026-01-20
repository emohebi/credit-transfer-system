#!/usr/bin/env python
"""
Run Full Merge Pipeline

Convenience script to:
1. Merge qualifications and occupations with taxonomy.json
2. Save merged JSON and Excel outputs
3. Generate HTML visualization

Usage:
    python run_merge_pipeline.py <taxonomy.json> <relationships.xlsx> <output_dir>

Example:
    python run_merge_pipeline.py output_faceted/faceted_taxonomy.json data/unit_qual_occ.xlsx output_merged/
"""

import sys
import argparse
import logging
from pathlib import Path

from merge_qualifications_occupations import QualificationOccupationMerger
from src.taxonomy.generate_faceted_visualization_with_qual_occ import generate_faceted_html

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():

    taxonomy_json = "skill_taxonomy_pipeline/data/faceted_taxonomy.json"
    relationships_file = "skill_taxonomy_pipeline/data/unit_qual_occp_tga.xlsx"
    output_dir = "skill_taxonomy_pipeline/output_merged/"
    # Validate inputs
    if not Path(taxonomy_json).exists():
        logger.error(f"Taxonomy file not found: {taxonomy_json}")
        sys.exit(1)
    
    if not Path(relationships_file).exists():
        logger.error(f"Relationships file not found: {relationships_file}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("RUNNING FULL MERGE PIPELINE")
    logger.info("=" * 60)
    
    # Step 1: Merge qualifications and occupations
    logger.info("\n[Step 1/3] Merging qualifications and occupations...")
    merger = QualificationOccupationMerger()
    merger.load_taxonomy(taxonomy_json)
    merger.load_relationships(relationships_file)
    merger.merge()
    
    # Step 2: Save outputs
    logger.info("\n[Step 2/3] Saving merged files...")
    output_json = output_dir / 'faceted_taxonomy_with_qual_occ.json'
    output_excel = output_dir / 'faceted_taxonomy_with_qual_occ.xlsx'
    
    merger.save_json(str(output_json))
    merger.save_excel(str(output_excel))
    
    # Step 3: Generate HTML visualization
    logger.info("\n[Step 3/3] Generating HTML visualization...")
    output_html = output_dir / 'faceted_explorer_with_qual_occ.html'
    generate_faceted_html(str(output_json), str(output_html))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"\nOutput files created in: {output_dir}")
    logger.info(f"  1. {output_json.name} - Merged JSON taxonomy")
    logger.info(f"  2. {output_excel.name} - Excel export")
    logger.info(f"  3. {output_html.name} - Interactive HTML visualization")
    logger.info(f"  4. {output_html.name.replace('.html', '_data.js')} - Data file for HTML")
    logger.info("\n" + "=" * 60)
    

if __name__ == '__main__':
    main()
