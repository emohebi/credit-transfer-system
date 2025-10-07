"""
Standalone skill extraction script
Extracts skills from VET and University qualifications and saves them to disk
"""

import argparse
import logging
import json
from pathlib import Path
from config_profiles import ConfigProfiles
from interfaces.model_factory import ModelFactory
from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse
from reporting.skill_export import SkillExportManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_vet_data(filepath: str) -> VETQualification:
    """Load VET qualification data"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    vet_qual = VETQualification(
        code=data["code"],
        name=data["name"],
        level=data["level"]
    )
    
    for unit_data in data.get("units", []):
        unit = UnitOfCompetency(
            code=unit_data["code"],
            name=unit_data["name"],
            description=unit_data.get("description", ""),
            learning_outcomes=unit_data.get("learning_outcomes", []),
            assessment_requirements=unit_data.get("assessment_requirements", ""),
            nominal_hours=unit_data.get("nominal_hours", 0) if unit_data.get("nominal_hours") is not None else 0,
            prerequisites=unit_data.get("prerequisites", [])
        )
        vet_qual.units.append(unit)
    
    return vet_qual


def load_uni_data(filepath: str) -> UniQualification:
    """Load university qualification data"""
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    uni_qual = UniQualification(
        code=data["code"],
        name=data["name"]
    )
    
    for course_data in data.get("courses", []):
        course = UniCourse(
            code=course_data["code"],
            name=course_data["name"],
            description=course_data.get("description", ""),
            study_level=course_data.get("study_level", "intermediate"),
            learning_outcomes=course_data.get("learning_outcomes", []),
            prerequisites=course_data.get("prerequisites", []),
            credit_points=course_data.get("credit_points", 0),
            topics=course_data.get("topics", []),
            assessment=course_data.get("assessment", "")
        )
        uni_qual.courses.append(course)
    
    return uni_qual


def extract_and_save_skills(genai, embeddings, config, vet_file: str, uni_file: str):
    """
    Extract skills from VET and University qualifications and save them
    """
    logger.info("Starting skill extraction process...")
    
    # Create configuration
    # config = ConfigProfiles.create_config(
    #     profile_name=profile,
    #     backend=backend
    # )
    
    # Create interfaces
    # genai = ModelFactory.create_genai_interface(config)
    # embeddings = ModelFactory.create_embedding_interface(config)
    
    if genai is None:
        logger.warning("No GenAI interface available - using fallback extraction")
    
    # Create skill extractor
    from extraction.unified_extractor import UnifiedSkillExtractor
    
    # Check if robust mode is enabled
    if config.get("ENSEMBLE_RUNS", 0) > 1:
        from extraction.ensemble_extractor import EnsembleSkillExtractor
        base_extractor = UnifiedSkillExtractor(genai, config.to_dict())
        extractor = EnsembleSkillExtractor(
            base_extractor, 
            num_runs=config.get("ENSEMBLE_RUNS", 3),
            embeddings=embeddings,
            similarity_threshold=config.get("ENSEMBLE_SIMILARITY_THRESHOLD", 0.9)
        )
    else:
        extractor = UnifiedSkillExtractor(genai, config.to_dict())
    
    # Load data
    logger.info(f"Loading VET qualification from {vet_file}")
    vet_qual = load_vet_data(vet_file)
    logger.info(f"Loaded VET: {vet_qual.name} ({len(vet_qual.units)} units)")
    
    logger.info(f"Loading University qualification from {uni_file}")
    uni_qual = load_uni_data(uni_file)
    logger.info(f"Loaded Uni: {uni_qual.name} ({len(uni_qual.courses)} courses)")
    
    # Extract skills for VET
    logger.info("Extracting VET skills...")
    vet_skills = extractor.extract_skills(vet_qual.units)
    
    # Assign extracted skills back to units
    for unit in vet_qual.units:
        if unit.code in vet_skills:
            unit.extracted_skills = vet_skills[unit.code]
            logger.info(f"Extracted {len(unit.extracted_skills)} skills for VET unit {unit.code}")
    
    # Extract skills for University
    logger.info("Extracting University skills...")
    uni_skills = extractor.extract_skills(uni_qual.courses)
    
    # Assign extracted skills back to courses
    for course in uni_qual.courses:
        if course.code in uni_skills:
            course.extracted_skills = uni_skills[course.code]
            logger.info(f"Extracted {len(course.extracted_skills)} skills for Uni course {course.code}")
    
    # Save skills using SkillExportManager
    skill_export = SkillExportManager(output_dir="output/skills")
    
    # Save VET skills
    vet_filepath = skill_export.export_vet_skills(vet_qual, format="json", include_metadata=True)
    logger.info(f"Saved VET skills to {vet_filepath}")
    
    # Save University skills
    uni_filepath = skill_export.export_uni_skills(uni_qual, format="json", include_metadata=True)
    logger.info(f"Saved University skills to {uni_filepath}")
    
    # Also save combined for reference
    combined_filepath = skill_export.export_combined_skills(vet_qual, uni_qual, format="json")
    logger.info(f"Saved combined skills to {combined_filepath}")
    
    # Print summary
    vet_total = sum(len(unit.extracted_skills) for unit in vet_qual.units)
    uni_total = sum(len(course.extracted_skills) for course in uni_qual.courses)
    
    print("\n" + "="*60)
    print("SKILL EXTRACTION COMPLETE")
    print("="*60)
    print(f"VET Skills Extracted: {vet_total}")
    print(f"University Skills Extracted: {uni_total}")
    print(f"\nSkills saved to:")
    print(f"  VET: {vet_filepath}")
    print(f"  Uni: {uni_filepath}")
    print(f"  Combined: {combined_filepath}")
    
    return vet_filepath, uni_filepath


def main():
    parser = argparse.ArgumentParser(description="Extract and save skills from VET and University qualifications")
    
    parser.add_argument("--vet", default="./data/diploma_of_business.json", help="Path to VET qualification JSON")
    parser.add_argument("--uni", default="./data/933AA_Diploma_of_Business.json", help="Path to university qualification JSON")
    parser.add_argument("--profile", choices=["fast", "balanced", "thorough", "robust"], default="balanced", help="Extraction profile")
    parser.add_argument("--backend", choices=["openai", "vllm", "auto"], default="auto", help="AI backend")
    
    args = parser.parse_args()
    
    extract_and_save_skills(args.vet, args.uni, args.profile, args.backend)


if __name__ == "__main__":
    main()