"""
Main entry point for the Credit Transfer Analysis System
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List, Optional

from config import Config
from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse
from interfaces.genai_interface import GenAIInterface
from interfaces.embedding_interface import EmbeddingInterface
from analysis.analyzer import CreditTransferAnalyzer
from reporting.report_generator import ReportGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_vet_data(filepath: str) -> VETQualification:
    """
    Load VET qualification data from JSON file
    
    Expected format:
    {
        "code": "ICT50220",
        "name": "Diploma of Information Technology",
        "level": "Diploma",
        "units": [
            {
                "code": "ICTICT517",
                "name": "Match IT needs with the strategic direction",
                "description": "...",
                "learning_outcomes": [...],
                "assessment_requirements": "...",
                "nominal_hours": 60,
                "prerequisites": []
            }
        ]
    }
    """
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
            nominal_hours=unit_data.get("nominal_hours", 0),
            prerequisites=unit_data.get("prerequisites", [])
        )
        vet_qual.units.append(unit)
    
    logger.info(f"Loaded VET qualification: {vet_qual.code} with {len(vet_qual.units)} units")
    return vet_qual


def load_uni_data(filepath: str) -> UniQualification:
    """
    Load university qualification data from JSON file
    
    Expected format:
    {
        "code": "BIT",
        "name": "Bachelor of Information Technology",
        "courses": [
            {
                "code": "COMP1234",
                "name": "Introduction to Programming",
                "description": "...",
                "study_level": "introductory",
                "learning_outcomes": [...],
                "prerequisites": [],
                "credit_points": 6,
                "topics": [...],
                "assessment": "..."
            }
        ]
    }
    """
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
            study_level=course_data.get("study_level", "intermediate"),  # Default to intermediate
            learning_outcomes=course_data.get("learning_outcomes", []),
            prerequisites=course_data.get("prerequisites", []),
            credit_points=course_data.get("credit_points", 0),
            topics=course_data.get("topics", []),
            assessment=course_data.get("assessment", "")
        )
        uni_qual.courses.append(course)
    
    logger.info(f"Loaded university qualification: {uni_qual.code} with {len(uni_qual.courses)} courses")
    return uni_qual


def initialize_interfaces():
    """Initialize GenAI and Embedding interfaces"""
    genai = None
    embeddings = None
    
    # Initialize GenAI - Priority order: Azure OpenAI > vLLM > Web API
    if Config.USE_AZURE_OPENAI:
        try:
            azure_config = Config.get_azure_openai_config()
            genai = GenAIInterface(
                endpoint=azure_config["endpoint"],
                deployment=azure_config["deployment"],
                api_key=azure_config["api_key"],
                api_version=azure_config["api_version"],
                timeout=azure_config["timeout"],
                max_tokens=azure_config["max_tokens"],
                temperature=azure_config["temperature"]
            )
            logger.info(f"Azure OpenAI interface initialized with deployment: {azure_config['deployment']}")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure OpenAI interface: {e}")
            
            # Fall back to vLLM if Azure OpenAI fails
            if Config.USE_VLLM:
                try:
                    from interfaces.vllm_genai_interface import VLLMGenAIInterface
                    genai = VLLMGenAIInterface(
                        model_name=Config.VLLM_MODEL_NAME,
                        number_gpus=Config.VLLM_NUM_GPUS,
                        max_model_len=Config.VLLM_MAX_MODEL_LEN,
                        model_cache_dir=Config.MODEL_CACHE_DIR,
                        external_model_dir=Config.EXTERNAL_MODEL_DIR
                    )
                    logger.info(f"Fell back to vLLM interface with model: {Config.VLLM_MODEL_NAME}")
                except Exception as e2:
                    logger.warning(f"Failed to initialize vLLM interface: {e2}")
    
    elif Config.USE_VLLM:
        try:
            from interfaces.vllm_genai_interface import VLLMGenAIInterface
            genai = VLLMGenAIInterface(
                model_name=Config.VLLM_MODEL_NAME,
                number_gpus=Config.VLLM_NUM_GPUS,
                max_model_len=Config.VLLM_MAX_MODEL_LEN,
                model_cache_dir=Config.MODEL_CACHE_DIR,
                external_model_dir=Config.EXTERNAL_MODEL_DIR
            )
            logger.info(f"vLLM GenAI interface initialized with model: {Config.VLLM_MODEL_NAME}")
        except Exception as e:
            logger.warning(f"Failed to initialize vLLM GenAI interface: {e}")
            
            # Fall back to web API if vLLM fails
            if Config.USE_GENAI:
                try:
                    genai = GenAIInterface(
                        model_endpoint=Config.GENAI_ENDPOINT,
                        api_key=Config.GENAI_API_KEY,
                        timeout=Config.GENAI_TIMEOUT
                    )
                    logger.info("Fell back to web API GenAI interface")
                except Exception as e2:
                    logger.warning(f"Failed to initialize web API GenAI interface: {e2}")
    
    elif Config.USE_GENAI:
        try:
            genai = GenAIInterface(
                model_endpoint=Config.GENAI_ENDPOINT,
                api_key=Config.GENAI_API_KEY,
                timeout=Config.GENAI_TIMEOUT
            )
            logger.info("Web API GenAI interface initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize GenAI interface: {e}")
    
    # Initialize Embeddings
    try:
        embeddings = EmbeddingInterface(
            model_name=Config.EMBEDDING_MODEL_NAME,
            model_cache_dir=Config.MODEL_CACHE_DIR,
            external_model_dir=Config.EXTERNAL_MODEL_DIR,
            device=Config.EMBEDDING_DEVICE,
            batch_size=Config.EMBEDDING_BATCH_SIZE
        )
        logger.info(f"Embedding interface initialized with model: {Config.EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logger.warning(f"Failed to initialize Embedding interface: {e}")
        # Try fallback to legacy configuration
        try:
            embeddings = EmbeddingInterface(
                model_path=Config.EMBEDDING_MODEL,
                api_endpoint=Config.EMBEDDING_ENDPOINT,
                api_key=Config.EMBEDDING_API_KEY,
                embedding_dim=Config.EMBEDDING_DIM,
                use_api=Config.USE_EMBEDDING_API
            )
            logger.info("Initialized embedding interface with legacy configuration")
        except Exception as e2:
            logger.warning(f"Failed to initialize legacy embedding interface: {e2}")
    
    return genai, embeddings


def analyze_transfer(vet_file: str, uni_file: str, output_file: str, 
                    target_courses: Optional[List[str]] = None,
                    report_format: str = "json",
                    export_skills: bool = True):  # Add this parameter
    """
    Main analysis function with skill export
    
    Args:
        vet_file: Path to VET qualification JSON
        uni_file: Path to university qualification JSON
        output_file: Path for output file
        target_courses: Optional list of specific course codes to analyze
        report_format: Output format (json, html, csv)
        export_skills: Whether to export extracted skills
    """
    logger.info("Starting credit transfer analysis")
    
    # Load data
    vet_qual = load_vet_data(vet_file)
    uni_qual = load_uni_data(uni_file)
    
    # Initialize interfaces
    genai, embeddings = initialize_interfaces()
    
    # Check if we have at least one interface
    if genai is None and embeddings is None:
        logger.error("Failed to initialize any interfaces. Analysis cannot proceed.")
        raise RuntimeError("No interfaces available for analysis")
    
    if genai is None:
        logger.warning("No GenAI interface available. Using pattern-based extraction only.")
    
    if embeddings is None:
        logger.warning("No embedding interface available. Using string similarity only.")
    
    # Create analyzer
    analyzer = CreditTransferAnalyzer(
        genai=genai,
        embeddings=embeddings,
        config=Config.get_config_dict()
    )
    
    # Perform analysis
    logger.info("Performing credit transfer analysis...")
    recommendations = analyzer.analyze_transfer(
        vet_qual=vet_qual,
        uni_qual=uni_qual,
        target_courses=target_courses
    )
    
    logger.info(f"Generated {len(recommendations)} recommendations")
    
    # Generate report with skill export
    report_gen = ReportGenerator()
    
    # Export skills if requested
    if export_skills:
        logger.info("Exporting extracted skills...")
        
        # Generate complete report package including skills
        files = report_gen.generate_complete_report_package(
            recommendations, vet_qual, uni_qual
        )
        
        logger.info("Report package generated:")
        for file_type, filepath in files.items():
            logger.info(f"  {file_type}: {filepath}")
        
        # Print summary of exported files
        print("\n" + "="*60)
        print("REPORT PACKAGE GENERATED")
        print("="*60)
        print(f"Main report: {files.get('report_html', 'N/A')}")
        print(f"Recommendations: {files.get('recommendations_json', 'N/A')}")
        print(f"VET Skills: {files.get('vet_skills_json', 'N/A')}")
        print(f"University Skills: {files.get('uni_skills_json', 'N/A')}")
        print(f"Combined Skills: {files.get('combined_skills_json', 'N/A')}")
        print(f"Skill Analysis: {files.get('skill_analysis', 'N/A')}")
        
    else:
        # Standard report generation (existing code)
        if report_format == "json":
            analyzer.export_recommendations(recommendations, output_file)
        elif report_format == "html":
            html_report = report_gen.generate_html_report(
                recommendations, vet_qual, uni_qual
            )
            with open(output_file, 'w') as f:
                f.write(html_report)
        elif report_format == "csv":
            csv_report = report_gen.generate_csv_report(recommendations)
            with open(output_file, 'w') as f:
                f.write(csv_report)
        else:
            text_report = report_gen.generate_full_report(
                recommendations, vet_qual, uni_qual
            )
            with open(output_file, 'w') as f:
                f.write(text_report)
        
        logger.info(f"Report saved to {output_file}")
    
    # Print summary
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"VET Qualification: {vet_qual.name}")
    print(f"University Program: {uni_qual.name}")
    print(f"Total Recommendations: {len(recommendations)}")
    
    if recommendations:
        full_count = sum(1 for r in recommendations if r.recommendation.value == "full")
        conditional_count = sum(1 for r in recommendations if r.recommendation.value == "conditional")
        partial_count = sum(1 for r in recommendations if r.recommendation.value == "partial")
        
        print(f"  - Full Credit: {full_count}")
        print(f"  - Conditional: {conditional_count}")
        print(f"  - Partial: {partial_count}")
        
        print("\nTop 5 Recommendations:")
        for i, rec in enumerate(recommendations[:5], 1):
            vet_codes = ", ".join(rec.get_vet_unit_codes())
            print(f"{i}. {vet_codes} → {rec.uni_course.code}")
            print(f"   Alignment: {rec.alignment_score:.1%} | "
                  f"Type: {rec.recommendation.value} | "
                  f"Confidence: {rec.confidence:.1%}")
    
    print(f"\nFull report saved to: {output_file}")


def main():
    
    vet_file = "./data/sample_vet.json"
    uni_file = "./data/sample_uni.json"
    
    # Validate input files
    if not Path(vet_file).exists():
        print(f"Error: VET file not found: {vet_file}")
        sys.exit(1)
    
    if not Path(uni_file).exists():
        print(f"Error: University file not found: {uni_file}")
        sys.exit(1)
    
    output = "./output"
    # Create output directory if needed
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    try:
        analyze_transfer(
            vet_file=vet_file,
            uni_file=uni_file,
            output_file=output,
            target_courses=None,
            report_format="both",
            export_skills=True
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nError: Analysis failed - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()