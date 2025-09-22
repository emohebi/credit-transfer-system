"""
Main entry point for the Credit Transfer Analysis System with batch processing support
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
    """Load VET qualification data from JSON file"""
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
    """Load university qualification data from JSON file"""
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
    
    logger.info(f"Loaded university qualification: {uni_qual.code} with {len(uni_qual.courses)} courses")
    return uni_qual


def initialize_interfaces():
    """Initialize GenAI and Embedding interfaces with batch processing support"""
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
                    if Config.USE_VLLM_BATCH:
                        from interfaces.vllm_genai_interface_batch import VLLMGenAIInterfaceBatch
                        genai = VLLMGenAIInterfaceBatch(
                            model_name=Config.VLLM_MODEL_NAME,
                            number_gpus=Config.VLLM_NUM_GPUS,
                            max_model_len=Config.VLLM_MAX_MODEL_LEN,
                            batch_size=Config.VLLM_BATCH_SIZE,
                            model_cache_dir=Config.MODEL_CACHE_DIR,
                            external_model_dir=Config.EXTERNAL_MODEL_DIR
                        )
                        logger.info(f"Fell back to vLLM batch interface with model: {Config.VLLM_MODEL_NAME}")
                    else:
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
            if Config.USE_VLLM_BATCH:
                from interfaces.vllm_genai_interface_batch import VLLMGenAIInterfaceBatch
                genai = VLLMGenAIInterfaceBatch(
                    model_name=Config.VLLM_MODEL_NAME,
                    number_gpus=Config.VLLM_NUM_GPUS,
                    max_model_len=Config.VLLM_MAX_MODEL_LEN,
                    batch_size=Config.VLLM_BATCH_SIZE,
                    model_cache_dir=Config.MODEL_CACHE_DIR,
                    external_model_dir=Config.EXTERNAL_MODEL_DIR
                )
                logger.info(f"vLLM batch GenAI interface initialized with model: {Config.VLLM_MODEL_NAME}")
                logger.info(f"Batch size: {Config.VLLM_BATCH_SIZE}")
            else:
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
                    export_skills: bool = True):
    """
    Main analysis function with batch processing support
    
    Args:
        vet_file: Path to VET qualification JSON
        uni_file: Path to university qualification JSON
        output_file: Path for output file
        target_courses: Optional list of specific course codes to analyze
        report_format: Output format (json, html, csv)
        export_skills: Whether to export extracted skills
    """
    logger.info("Starting credit transfer analysis")
    
    if Config.USE_VLLM_BATCH:
        logger.info("Batch processing mode enabled")
        logger.info(f"Batch size: {Config.VLLM_BATCH_SIZE}")
    else:
        logger.info("Individual processing mode")
    
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
    
    # Generate report
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
        
        # Print summary
        print("\n" + "="*60)
        print("REPORT PACKAGE GENERATED")
        print("="*60)
        print(f"Processing Mode: {'Batch' if Config.USE_VLLM_BATCH else 'Individual'}")
        if Config.USE_VLLM_BATCH:
            print(f"Batch Size: {Config.VLLM_BATCH_SIZE}")
        print(f"Main report: {files.get('report_html', 'N/A')}")
        print(f"Recommendations: {files.get('recommendations_json', 'N/A')}")
        print(f"VET Skills: {files.get('vet_skills_json', 'N/A')}")
        print(f"University Skills: {files.get('uni_skills_json', 'N/A')}")
        print(f"Combined Skills: {files.get('combined_skills_json', 'N/A')}")
        print(f"Skill Analysis: {files.get('skill_analysis', 'N/A')}")
        
    else:
        # Standard report generation
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
    print(f"Processing Mode: {'Batch' if Config.USE_VLLM_BATCH else 'Individual'}")
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
    """Main entry point with CLI including batch processing options"""
    parser = argparse.ArgumentParser(
        description="Credit Transfer Analysis System - Analyze VET to University credit transfers"
    )
    
    parser.add_argument(
        "vet_file",
        help="Path to VET qualification JSON file"
    )
    parser.add_argument(
        "uni_file",
        help="Path to university qualification JSON file"
    )
    parser.add_argument(
        "-o", "--output",
        default="output/recommendations.json",
        help="Output file path (default: output/recommendations.json)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["json", "html", "csv", "text"],
        default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "-c", "--courses",
        nargs="+",
        help="Specific course codes to analyze (e.g., COMP1234 COMP2345)"
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file to load"
    )
    parser.add_argument(
        "--save-config",
        help="Save current configuration to file"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # vLLM options
    parser.add_argument(
        "--use-vllm",
        action="store_true", 
        help="Force use of vLLM (overrides config)"
    )
    parser.add_argument(
        "--use-batch",
        action="store_true",
        help="Enable batch processing for vLLM"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        help="Batch size for vLLM processing (default: 8)"
    )
    parser.add_argument(
        "--no-batch",
        action="store_true",
        help="Disable batch processing (use individual processing)"
    )
    
    # Azure OpenAI options
    parser.add_argument(
        "--use-azure-openai",
        action="store_true",
        help="Force use of Azure OpenAI (overrides config)"
    )
    parser.add_argument(
        "--azure-endpoint",
        help="Azure OpenAI endpoint URL"
    )
    parser.add_argument(
        "--azure-deployment",
        help="Azure OpenAI deployment name"
    )
    parser.add_argument(
        "--azure-api-key",
        help="Azure OpenAI API key"
    )
    
    # Skill export options
    parser.add_argument(
        "--export-skills",
        action="store_true",
        default=True,
        help="Export extracted skills to separate files (default: True)"
    )
    parser.add_argument(
        "--skill-format",
        choices=["json", "csv", "both"],
        default="both",
        help="Format for skill export (default: both)"
    )
    parser.add_argument(
        "--generate-package",
        action="store_true",
        help="Generate complete report package with all formats"
    )
    
    args = parser.parse_args()
    
    # Set verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Handle config operations
    if args.save_config:
        Config.save_config(args.save_config)
        print(f"Configuration saved to {args.save_config}")
        return
    
    if args.config:
        Config.load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    
    # Override config with command line arguments
    if args.use_azure_openai:
        Config.USE_AZURE_OPENAI = True
        Config.USE_VLLM = False
        Config.USE_GENAI = False
    
    if args.use_vllm:
        Config.USE_VLLM = True
        Config.USE_AZURE_OPENAI = False
        Config.USE_GENAI = False
    
    if args.use_batch:
        Config.USE_VLLM_BATCH = True
        logger.info("Batch processing enabled via command line")
    
    if args.no_batch:
        Config.USE_VLLM_BATCH = False
        logger.info("Batch processing disabled via command line")
    
    if args.batch_size:
        Config.VLLM_BATCH_SIZE = args.batch_size
        logger.info(f"Batch size set to {args.batch_size}")
    
    if args.azure_endpoint:
        Config.AZURE_OPENAI_ENDPOINT = args.azure_endpoint
    
    if args.azure_deployment:
        Config.AZURE_OPENAI_DEPLOYMENT = args.azure_deployment
    
    if args.azure_api_key:
        Config.AZURE_OPENAI_API_KEY = args.azure_api_key
    
    # Validate input files
    if not Path(args.vet_file).exists():
        print(f"Error: VET file not found: {args.vet_file}")
        sys.exit(1)
    
    if not Path(args.uni_file).exists():
        print(f"Error: University file not found: {args.uni_file}")
        sys.exit(1)
    
    # Create output directory if needed
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Run analysis
    try:
        analyze_transfer(
            vet_file=args.vet_file,
            uni_file=args.uni_file,
            output_file=args.output,
            target_courses=args.courses,
            report_format=args.format,
            export_skills=args.export_skills
        )
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nError: Analysis failed - {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()