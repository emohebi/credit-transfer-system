#!/usr/bin/env python
"""
Merge Qualifications and Occupations with Taxonomy

This script merges an Excel file containing unit-qualification-occupation relationships
with the existing taxonomy.json file.

Excel file columns:
- code: unit code (maps to skill's 'code' or 'all_related_codes')
- qualification_code: qualification code
- qualification_title: title of the qualification
- anzsco_code: occupation code (ANZSCO)
- anzsco_title: title of the occupation

Usage:
    python merge_qualifications_occupations.py <taxonomy.json> <relationships.xlsx> <output_dir>
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QualificationOccupationMerger:
    """
    Merges qualification and occupation data with skill taxonomy.
    """
    
    def __init__(self):
        self.taxonomy_data = None
        self.relationships_df = None
        
        # Lookup dictionaries for fast access
        self.code_to_qualifications = defaultdict(list)  # code -> list of {code, title}
        self.code_to_occupations = defaultdict(list)     # code -> list of {code, title}
        self.qualification_to_occupations = defaultdict(list)  # qual_code -> list of {code, title}
        
        # Unique sets for facet building
        self.all_qualifications = {}  # code -> title
        self.all_occupations = {}     # code -> title
        
        # Statistics
        self.stats = {
            'total_skills': 0,
            'skills_with_qualifications': 0,
            'skills_with_occupations': 0,
            'total_qualifications': 0,
            'total_occupations': 0,
            'total_relationships': 0
        }
    
    def load_taxonomy(self, taxonomy_path: str) -> Dict:
        """Load the taxonomy JSON file"""
        logger.info(f"Loading taxonomy from: {taxonomy_path}")
        
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            self.taxonomy_data = json.load(f)
        
        self.stats['total_skills'] = len(self.taxonomy_data.get('skills', []))
        logger.info(f"Loaded {self.stats['total_skills']} skills from taxonomy")
        
        return self.taxonomy_data
    
    def load_relationships(self, relationships_path: str) -> pd.DataFrame:
        """Load the unit-qualification-occupation relationships Excel file"""
        logger.info(f"Loading relationships from: {relationships_path}")
        
        # Determine file type and load
        path = Path(relationships_path)
        if path.suffix.lower() in ['.xlsx', '.xls']:
            self.relationships_df = pd.read_excel(relationships_path)
        elif path.suffix.lower() == '.csv':
            self.relationships_df = pd.read_csv(relationships_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        
        # Validate required columns
        required_columns = ['code', 'qualification_code', 'qualification_title', 
                          'anzsco_code', 'anzsco_title']
        missing_columns = set(required_columns) - set(self.relationships_df.columns)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Clean data
        self.relationships_df = self.relationships_df.dropna(subset=['code'])
        self.relationships_df['code'] = self.relationships_df['code'].astype(str).str.strip()
        self.relationships_df['qualification_code'] = self.relationships_df['qualification_code'].fillna('').astype(str).str.strip()
        self.relationships_df['qualification_title'] = self.relationships_df['qualification_title'].fillna('').astype(str).str.strip()
        self.relationships_df['anzsco_code'] = self.relationships_df['anzsco_code'].fillna('').astype(str).str.strip()
        self.relationships_df['anzsco_title'] = self.relationships_df['anzsco_title'].fillna('').astype(str).str.strip()
        
        self.stats['total_relationships'] = len(self.relationships_df)
        logger.info(f"Loaded {self.stats['total_relationships']} relationships")
        
        return self.relationships_df
    
    def build_lookup_tables(self):
        """Build lookup tables for fast code-to-qualification/occupation mapping"""
        logger.info("Building lookup tables...")
        
        for _, row in self.relationships_df.iterrows():
            code = row['code']
            qual_code = row['qualification_code']
            qual_title = row['qualification_title']
            occ_code = row['anzsco_code']
            occ_title = row['anzsco_title']
            
            # Build code -> qualifications mapping
            if qual_code and qual_title:
                qual_entry = {'code': qual_code, 'title': qual_title}
                if qual_entry not in self.code_to_qualifications[code]:
                    self.code_to_qualifications[code].append(qual_entry)
                
                # Track all unique qualifications
                if qual_code not in self.all_qualifications:
                    self.all_qualifications[qual_code] = qual_title
            
            # Build code -> occupations mapping
            if occ_code and occ_title:
                occ_entry = {'code': occ_code, 'title': occ_title}
                if occ_entry not in self.code_to_occupations[code]:
                    self.code_to_occupations[code].append(occ_entry)
                
                # Track all unique occupations
                if occ_code not in self.all_occupations:
                    self.all_occupations[occ_code] = occ_title
            
            # Build qualification -> occupations mapping
            if qual_code and occ_code and occ_title:
                occ_entry = {'code': occ_code, 'title': occ_title}
                if occ_entry not in self.qualification_to_occupations[qual_code]:
                    self.qualification_to_occupations[qual_code].append(occ_entry)
        
        self.stats['total_qualifications'] = len(self.all_qualifications)
        self.stats['total_occupations'] = len(self.all_occupations)
        
        logger.info(f"Built lookup tables:")
        logger.info(f"  - Unique unit codes: {len(self.code_to_qualifications)}")
        logger.info(f"  - Unique qualifications: {self.stats['total_qualifications']}")
        logger.info(f"  - Unique occupations: {self.stats['total_occupations']}")
    
    def get_skill_codes(self, skill: Dict) -> Set[str]:
        """Extract all codes associated with a skill"""
        codes = set()
        
        # Primary code
        if skill.get('code'):
            codes.add(str(skill['code']).strip())
        
        # All related codes
        # all_related_codes = skill.get('all_related_codes', [])
        # if isinstance(all_related_codes, list):
        #     for code in all_related_codes:
        #         if code:
        #             codes.add(str(code).strip())
        
        return codes
    
    def get_qualifications_for_skill(self, skill: Dict) -> List[Dict]:
        """Get all qualifications associated with a skill's codes"""
        codes = self.get_skill_codes(skill)
        
        qualifications = {}
        for code in codes:
            for qual in self.code_to_qualifications.get(code, []):
                qual_code = qual['code']
                if qual_code not in qualifications:
                    qualifications[qual_code] = qual
        
        return list(qualifications.values())
    
    def get_occupations_for_skill(self, skill: Dict) -> List[Dict]:
        """Get all occupations associated with a skill's codes"""
        codes = self.get_skill_codes(skill)
        
        occupations = {}
        for code in codes:
            for occ in self.code_to_occupations.get(code, []):
                occ_code = occ['code']
                if occ_code not in occupations:
                    occupations[occ_code] = occ
        
        return list(occupations.values())
    
    def merge(self) -> Dict:
        """Merge qualifications and occupations into the taxonomy"""
        logger.info("Merging qualifications and occupations with taxonomy...")
        
        # Build lookup tables
        self.build_lookup_tables()
        
        # Process each skill
        for skill in self.taxonomy_data.get('skills', []):
            # Get qualifications for this skill
            qualifications = self.get_qualifications_for_skill(skill)
            if qualifications:
                skill['qualifications'] = qualifications
                self.stats['skills_with_qualifications'] += 1
            else:
                skill['qualifications'] = []
            
            # Get occupations for this skill
            occupations = self.get_occupations_for_skill(skill)
            if occupations:
                skill['occupations'] = occupations
                self.stats['skills_with_occupations'] += 1
            else:
                skill['occupations'] = []
        
        # Add qualification and occupation facets to the taxonomy
        self._add_facets_to_taxonomy()
        
        # Update metadata statistics
        self._update_metadata_statistics()
        
        logger.info("Merge complete!")
        self._log_statistics()
        
        return self.taxonomy_data
    
    def _add_facets_to_taxonomy(self):
        """Add qualification and occupation facets to the taxonomy"""
        
        # Add QUAL facet (Qualifications)
        self.taxonomy_data['facets']['QUAL'] = {
            'facet_id': 'QUAL',
            'facet_name': 'Qualifications',
            'description': 'VET qualifications associated with the skill through unit codes',
            'multi_value': True,
            'values': {
                code: {
                    'code': code,
                    'name': title,
                    'description': f"Qualification: {title}"
                }
                for code, title in self.all_qualifications.items()
            }
        }
        
        # Add OCC facet (Occupations / ANZSCO)
        self.taxonomy_data['facets']['OCC'] = {
            'facet_id': 'OCC',
            'facet_name': 'Occupations (ANZSCO)',
            'description': 'ANZSCO occupations associated with the skill through qualifications',
            'multi_value': True,
            'values': {
                code: {
                    'code': code,
                    'name': title,
                    'description': f"ANZSCO Occupation: {title}"
                }
                for code, title in self.all_occupations.items()
            }
        }
        
        logger.info(f"Added QUAL facet with {len(self.all_qualifications)} values")
        logger.info(f"Added OCC facet with {len(self.all_occupations)} values")
    
    def _update_metadata_statistics(self):
        """Update the metadata statistics in the taxonomy"""
        if 'metadata' not in self.taxonomy_data:
            self.taxonomy_data['metadata'] = {}
        
        if 'statistics' not in self.taxonomy_data['metadata']:
            self.taxonomy_data['metadata']['statistics'] = {}
        
        stats = self.taxonomy_data['metadata']['statistics']
        
        stats['total_qualifications'] = self.stats['total_qualifications']
        stats['total_occupations'] = self.stats['total_occupations']
        stats['skills_with_qualifications'] = self.stats['skills_with_qualifications']
        stats['skills_with_occupations'] = self.stats['skills_with_occupations']
        
        # Add facet coverage for QUAL and OCC
        if 'facet_coverage' not in stats:
            stats['facet_coverage'] = {}
        
        total_skills = self.stats['total_skills']
        
        stats['facet_coverage']['QUAL'] = {
            'name': 'Qualifications',
            'assigned': self.stats['skills_with_qualifications'],
            'coverage': self.stats['skills_with_qualifications'] / total_skills if total_skills > 0 else 0
        }
        
        stats['facet_coverage']['OCC'] = {
            'name': 'Occupations (ANZSCO)',
            'assigned': self.stats['skills_with_occupations'],
            'coverage': self.stats['skills_with_occupations'] / total_skills if total_skills > 0 else 0
        }
        
        # Add distribution statistics
        if 'facet_distributions' not in stats:
            stats['facet_distributions'] = {}
        
        # Count skills per qualification
        qual_dist = defaultdict(int)
        occ_dist = defaultdict(int)
        
        for skill in self.taxonomy_data.get('skills', []):
            for qual in skill.get('qualifications', []):
                qual_dist[qual['code']] += 1
            for occ in skill.get('occupations', []):
                occ_dist[occ['code']] += 1
        
        # Store top 20 by count
        stats['facet_distributions']['QUAL'] = dict(
            sorted(qual_dist.items(), key=lambda x: x[1], reverse=True)[:20]
        )
        stats['facet_distributions']['OCC'] = dict(
            sorted(occ_dist.items(), key=lambda x: x[1], reverse=True)[:20]
        )
        
        # Update generated_at timestamp
        self.taxonomy_data['metadata']['generated_at'] = datetime.now().isoformat()
        self.taxonomy_data['metadata']['merged_with_qualifications'] = True
    
    def _log_statistics(self):
        """Log merge statistics"""
        logger.info("\n" + "=" * 60)
        logger.info("MERGE STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total skills: {self.stats['total_skills']}")
        logger.info(f"Total relationships loaded: {self.stats['total_relationships']}")
        logger.info(f"Unique qualifications: {self.stats['total_qualifications']}")
        logger.info(f"Unique occupations: {self.stats['total_occupations']}")
        logger.info(f"Skills with qualifications: {self.stats['skills_with_qualifications']} "
                   f"({100*self.stats['skills_with_qualifications']/self.stats['total_skills']:.1f}%)")
        logger.info(f"Skills with occupations: {self.stats['skills_with_occupations']} "
                   f"({100*self.stats['skills_with_occupations']/self.stats['total_skills']:.1f}%)")
        logger.info("=" * 60)
    
    def save_json(self, output_path: str):
        """Save the merged taxonomy as JSON"""
        logger.info(f"Saving merged taxonomy to: {output_path}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.taxonomy_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved JSON: {output_path}")
    
    def save_excel(self, output_path: str):
        """Save the merged taxonomy as Excel"""
        logger.info(f"Saving merged taxonomy to Excel: {output_path}")
        
        try:
            # Flatten skills data for Excel
            rows = []
            for skill in self.taxonomy_data.get('skills', []):
                row = {
                    'skill_id': skill.get('id', ''),
                    'skill_name': skill.get('name', ''),
                    'description': skill.get('description', ''),
                    'category': skill.get('category', ''),
                    'level': skill.get('level', ''),
                    'context': skill.get('context', ''),
                    'confidence': skill.get('confidence', ''),
                    'code': skill.get('code', ''),
                }
                
                # Add facets
                facets = skill.get('facets', {})
                for facet_id in ['NAT', 'TRF', 'COG', 'CTX', 'FUT', 'LRN', 'DIG', 'ASCED', 'LVL']:
                    facet_data = facets.get(facet_id, {})
                    row[f'facet_{facet_id}_code'] = facet_data.get('code', '')
                    row[f'facet_{facet_id}_name'] = facet_data.get('name', '')
                
                # Add qualifications (as semicolon-separated)
                qualifications = skill.get('qualifications', [])
                row['qualification_codes'] = '; '.join([q['code'] for q in qualifications])
                row['qualification_titles'] = '; '.join([q['title'] for q in qualifications])
                row['qualification_count'] = len(qualifications)
                
                # Add occupations (as semicolon-separated)
                occupations = skill.get('occupations', [])
                row['occupation_codes'] = '; '.join([o['code'] for o in occupations])
                row['occupation_titles'] = '; '.join([o['title'] for o in occupations])
                row['occupation_count'] = len(occupations)
                
                # Add other fields
                alternative_titles = skill.get('alternative_titles', []) if isinstance(skill.get('alternative_titles', []), list) else []
                all_related_codes = skill.get('all_related_codes', []) if isinstance(skill.get('all_related_codes', []), list) else []
                all_related_kw = skill.get('all_related_kw', []) if isinstance(skill.get('all_related_kw', []), list) else []
                row['alternative_titles'] = alternative_titles
                row['all_related_codes'] = all_related_codes
                row['all_related_keywords'] = all_related_kw
                
                rows.append(row)
            
            # Create DataFrame and save
            df = pd.DataFrame(rows)
            df.to_excel(output_path, index=False, engine='openpyxl')
            
            logger.info(f"Saved Excel with {len(rows)} rows: {output_path}")
        except Exception as e:
            logger.error(f"skill: {skill}")
            logger.error(f"Error saving Excel file: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Merge qualifications and occupations with skill taxonomy",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python merge_qualifications_occupations.py taxonomy.json relationships.xlsx output/
    python merge_qualifications_occupations.py output_faceted/faceted_taxonomy.json data/unit_qual_occ.xlsx output_merged/
        """
    )
    
    parser.add_argument(
        'taxonomy_json',
        help='Path to the taxonomy JSON file'
    )
    
    parser.add_argument(
        'relationships_file',
        help='Path to the Excel/CSV file with unit-qualification-occupation relationships'
    )
    
    parser.add_argument(
        'output_dir',
        help='Output directory for merged files'
    )
    
    parser.add_argument(
        '--generate-html',
        action='store_true',
        help='Generate updated HTML visualization'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not Path(args.taxonomy_json).exists():
        logger.error(f"Taxonomy file not found: {args.taxonomy_json}")
        sys.exit(1)
    
    if not Path(args.relationships_file).exists():
        logger.error(f"Relationships file not found: {args.relationships_file}")
        sys.exit(1)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Run merger
    merger = QualificationOccupationMerger()
    merger.load_taxonomy(args.taxonomy_json)
    merger.load_relationships(args.relationships_file)
    merger.merge()
    
    # Save outputs
    output_json = output_dir / 'faceted_taxonomy_with_qual_occ.json'
    output_excel = output_dir / 'faceted_taxonomy_with_qual_occ.xlsx'
    
    merger.save_json(str(output_json))
    merger.save_excel(str(output_excel))
    
    # Generate HTML if requested
    if args.generate_html:
        try:
            from src.taxonomy.generate_faceted_visualization_with_qual_occ import generate_faceted_html
            output_html = output_dir / 'faceted_explorer_with_qual_occ.html'
            generate_faceted_html(str(output_json), str(output_html))
            logger.info(f"Generated HTML visualization: {output_html}")
        except ImportError:
            logger.warning("Could not import HTML generator. Run separately with:")
            logger.warning(f"  python src/taxonomy/generate_faceted_visualization_with_qual_occ.py {output_json} {output_dir}/faceted_explorer.html")
    
    logger.info("\n" + "=" * 60)
    logger.info("MERGE COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Output files:")
    logger.info(f"  - JSON: {output_json}")
    logger.info(f"  - Excel: {output_excel}")
    if args.generate_html:
        logger.info(f"  - HTML: {output_dir / 'faceted_explorer_with_qual_occ.html'}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
