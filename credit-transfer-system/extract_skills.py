"""
Extract and save skills with cross-qualification differentiation using embeddings
"""

import json
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Any
from datetime import datetime

from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse, Skill
from models.enums import SkillLevel
from extraction.unified_extractor import UnifiedSkillExtractor
from reporting.skill_export import SkillExportManager
from analysis.simplified_analyzer import SimplifiedAnalyzer

logger = logging.getLogger(__name__)


def extract_and_save_skills(genai, embeddings, config, vet_qual: VETQualification, uni_qual: UniQualification) -> Tuple[str, str]:
    """
    Extract skills from VET and University qualifications with cross-qualification differentiation
    
    Args:
        genai: GenAI interface
        embeddings: Embedding interface for similarity calculation
        config: Configuration object
        vet_file_path: Path to VET qualification JSON
        uni_file_path: Path to University qualification JSON
    
    Returns:
        Tuple of (vet_output_path, uni_output_path)
    """
    
    logger.info("="*60)
    logger.info("SKILL EXTRACTION WITH CROSS-QUALIFICATION DIFFERENTIATION")
    logger.info("="*60)
    
    # # Load qualifications
    # vet_qual = load_vet_qualification(vet_file_path)
    # uni_qual = load_uni_qualification(uni_file_path)
    
    logger.info(f"Loaded VET: {vet_qual.name} ({len(vet_qual.units)} units)")
    logger.info(f"Loaded Uni: {uni_qual.name} ({len(uni_qual.courses)} courses)")
    
    # Initialize extractor
    extractor = UnifiedSkillExtractor(genai, config)
    
    # Extract VET skills
    logger.info("\nExtracting VET skills...")
    vet_skills = extractor.extract_skills(vet_qual.units, item_type="VET")
    
    # Assign skills to units
    for unit in vet_qual.units:
        if unit.code in vet_skills:
            unit.extracted_skills = vet_skills[unit.code]
            logger.info(f"Extracted {len(unit.extracted_skills)} skills for VET unit {unit.code}")
    
    # Extract University skills
    logger.info("\nExtracting University skills...")
    uni_skills = extractor.extract_skills(uni_qual.courses, item_type="University")
    
    # Assign skills to courses
    for course in uni_qual.courses:
        if course.code in uni_skills:
            course.extracted_skills = uni_skills[course.code]
            logger.info(f"Extracted {len(course.extracted_skills)} skills for Uni course {course.code}")
    
    # Apply cross-qualification differentiation if embeddings are available
    if embeddings:
        analyzer = SimplifiedAnalyzer(genai, embeddings, config)
        logger.info("\n" + "="*60)
        logger.info("APPLYING CROSS-QUALIFICATION DIFFERENTIATION")
        logger.info("="*60)
        
        vet_qual, uni_qual = analyzer._ensure_cross_qualification_differentiation(
            vet_qual, 
            uni_qual, 
            similarity_threshold=config.get("SKILL_SIMILARITY_THRESHOLD", 0.85),
            min_level_difference=config.get("MIN_UNI_VET_LEVEL_DIFF", 1)
        )
    else:
        logger.warning("No embedding interface available - skipping cross-qualification differentiation")
    
    # Log final statistics
    log_extraction_statistics(vet_qual, uni_qual)
    
    # Save skills
    skill_export = SkillExportManager(output_dir="output/skills")
    
    # Save VET skills
    vet_output_path = skill_export.export_vet_skills(vet_qual, format="json")
    logger.info(f"Saved VET skills to: {vet_output_path}")
    
    # Save University skills
    uni_output_path = skill_export.export_uni_skills(uni_qual, format="json")
    logger.info(f"Saved University skills to: {uni_output_path}")
    
    return vet_output_path, uni_output_path


def log_extraction_statistics(vet_qual: VETQualification, uni_qual: UniQualification):
    """Log detailed extraction statistics"""
    
    logger.info("\n" + "="*60)
    logger.info("EXTRACTION STATISTICS")
    logger.info("="*60)
    
    # VET statistics
    vet_skills = []
    for unit in vet_qual.units:
        vet_skills.extend(unit.extracted_skills)
    
    if vet_skills:
        vet_levels = [s.level.value if hasattr(s.level, 'value') else s.level for s in vet_skills]
        logger.info(f"\nVET Qualification: {vet_qual.name}")
        logger.info(f"  Total units: {len(vet_qual.units)}")
        logger.info(f"  Total skills: {len(vet_skills)}")
        logger.info(f"  Average skills per unit: {len(vet_skills)/len(vet_qual.units):.1f}")
        logger.info(f"  Average skill level: {np.mean(vet_levels):.2f}")
        logger.info(f"  Level range: {min(vet_levels)} - {max(vet_levels)}")
    
    # University statistics
    uni_skills = []
    for course in uni_qual.courses:
        uni_skills.extend(course.extracted_skills)
    
    if uni_skills:
        uni_levels = [s.level.value if hasattr(s.level, 'value') else s.level for s in uni_skills]
        logger.info(f"\nUniversity Qualification: {uni_qual.name}")
        logger.info(f"  Total courses: {len(uni_qual.courses)}")
        logger.info(f"  Total skills: {len(uni_skills)}")
        logger.info(f"  Average skills per course: {len(uni_skills)/len(uni_qual.courses):.1f}")
        logger.info(f"  Average skill level: {np.mean(uni_levels):.2f}")
        logger.info(f"  Level range: {min(uni_levels)} - {max(uni_levels)}")
    
    # Level difference
    if vet_skills and uni_skills:
        level_diff = np.mean(uni_levels) - np.mean(vet_levels)
        logger.info(f"\nAverage level difference (Uni - VET): {level_diff:.2f}")


# def load_vet_qualification(filepath: str) -> VETQualification:
#     """Load VET qualification from JSON file"""
#     with open(filepath, 'r') as f:
#         data = json.load(f)
    
#     vet_qual = VETQualification(
#         code=data["code"],
#         name=data["name"],
#         level=data["level"]
#     )
    
#     for unit_data in data.get("units", []):
#         unit = UnitOfCompetency(
#             code=unit_data["code"],
#             name=unit_data["name"],
#             description=unit_data.get("description", ""),
#             study_level=unit_data.get("study_level", ""),
#             learning_outcomes=unit_data.get("learning_outcomes", []),
#             assessment_requirements=unit_data.get("assessment_requirements", ""),
#             nominal_hours=unit_data.get("nominal_hours", 0) or 0,
#             prerequisites=unit_data.get("prerequisites", [])
#         )
#         vet_qual.units.append(unit)
    
#     return vet_qual


# def load_uni_qualification(filepath: str) -> UniQualification:
#     """Load university qualification from JSON file"""
#     with open(filepath, 'r') as f:
#         data = json.load(f)
    
#     uni_qual = UniQualification(
#         code=data["code"],
#         name=data["name"]
#     )
    
#     for course_data in data.get("courses", []):
#         course = UniCourse(
#             code=course_data["code"],
#             name=course_data["name"],
#             description=course_data.get("description", ""),
#             study_level=course_data.get("study_level", "intermediate"),
#             learning_outcomes=course_data.get("learning_outcomes", []),
#             prerequisites=course_data.get("prerequisites", []),
#             credit_points=course_data.get("credit_points", 0),
#             topics=course_data.get("topics", []),
#             assessment=course_data.get("assessment", "")
#         )
#         uni_qual.courses.append(course)
    
#     return uni_qual


# if __name__ == "__main__":
#     # Example usage
#     import sys
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Extract and save skills with differentiation")
#     parser.add_argument("vet_file", help="Path to VET qualification JSON")
#     parser.add_argument("uni_file", help="Path to University qualification JSON")
#     parser.add_argument("--backend", choices=["openai", "vllm", "auto"], default="auto",
#                        help="AI backend to use")
#     parser.add_argument("--similarity-threshold", type=float, default=0.9,
#                        help="Similarity threshold for skill matching (0.0-1.0)")
#     parser.add_argument("--min-level-diff", type=int, default=1,
#                        help="Minimum level difference between similar VET/Uni skills")
    
#     args = parser.parse_args()
    
#     # Set up logging
#     logging.basicConfig(
#         level=logging.INFO,
#         format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     )
    
#     # Load configuration
#     from config_profiles import ConfigProfiles
#     from interfaces.model_factory import ModelFactory
    
#     config = ConfigProfiles.create_config(
#         profile_name="balanced",
#         backend=args.backend
#     )
    
#     # Add custom settings
#     config.SKILL_SIMILARITY_THRESHOLD = args.similarity_threshold
#     config.MIN_UNI_VET_LEVEL_DIFF = args.min_level_diff
    
#     # Create interfaces
#     genai = ModelFactory.create_genai_interface(config)
#     embeddings = ModelFactory.create_embedding_interface(config)
    
#     if not embeddings:
#         logger.error("Embedding interface is required for skill differentiation")
#         sys.exit(1)
    
#     # Extract and save skills
#     vet_output, uni_output = extract_and_save_skills(
#         genai,
#         embeddings,
#         config,
#         args.vet_file,
#         args.uni_file
#     )
    
#     print(f"\n✓ Skills extracted and saved:")
#     print(f"  VET: {vet_output}")
#     print(f"  Uni: {uni_output}")