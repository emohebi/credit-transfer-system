"""
Simplified main entry point with backend selection
"""

import argparse
import logging
import sys
import time
from pathlib import Path

from config_profiles import ConfigProfiles
from interfaces.model_factory import ModelFactory
from analysis.simplified_analyzer import SimplifiedAnalyzer
from utils.quality_monitor import QualityMonitor
from reporting.report_generator import ReportGenerator

# Existing imports
from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse
import json

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# At system initialization:
import random
import numpy as np
import torch

def set_global_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


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
            nominal_hours=unit_data.get("nominal_hours", 0) if unit_data.get("nominal_hours") is not None else 0,  # Default to 0 instead of None
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


def main():
    parser = argparse.ArgumentParser(
        description="Credit Transfer Analysis with Backend Selection"
    )
    
    # Required arguments
    # parser.add_argument("vet_file", help="Path to VET qualification JSON", default="./data/diploma_of_business.json")
    # parser.add_argument("uni_file", help="Path to university qualification JSON", default="./data/933AA_Diploma_of_Business.json")
    
    # Profile selection
    parser.add_argument(
        "--profile",
        choices=["fast", "balanced", "thorough", "dev", "robust"],
        default="robust",
        help="Analysis profile (default: balanced)"
    )
    
    # Backend selection
    parser.add_argument(
        "--backend",
        choices=["openai", "vllm", "auto"],
        default="auto",
        help="AI backend: openai (Azure OpenAI), vllm (local), or auto (default: auto)"
    )
    
    # Model options
    parser.add_argument(
        "--model",
        help="Override model name (for vLLM backend)"
    )
    
    parser.add_argument(
        "--deployment",
        help="Override deployment name (for OpenAI backend)"
    )
    
    # Output options
    parser.add_argument(
        "-o", "--output",
        default="output/recommendations.json",
        help="Output file path"
    )
    
    parser.add_argument(
        "--depth",
        choices=["quick", "balanced", "deep", "auto"],
        default="quick",
        help="Analysis depth (default: auto)"
    )
    
    # Quality monitoring
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Enable quality monitoring"
    )
    
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear all caches before running"
    )
    
    parser.add_argument(
        "--list-backends",
        action="store_true",
        help="List available backends and exit"
    )
    
    parser.add_argument(
    "--embedding",
    choices=["jina", "minilm", "bge", "e5"],
    help="Embedding model to use (default: from profile)"
    )

    parser.add_argument(
        "--embedding-device",
        help="Device for embeddings (e.g., cuda:0, cuda:1, cpu)"
    )
    
    args = parser.parse_args()
    
    # List available backends if requested
    if args.list_backends:
        available = ModelFactory.detect_available_backends()
        print("Available backends:")
        for backend in available:
            print(f"  • {backend}")
        sys.exit(0)
    
    # Create configuration with backend selection
    overrides = {"PROGRESSIVE_DEPTH": args.depth}
    
    # Add model overrides if specified
    if args.model:
        overrides["MODEL_NAME"] = args.model
    if args.deployment:
        overrides["DEPLOYMENT"] = args.deployment
    if args.embedding_device:
        overrides["EMBEDDING_DEVICE"] = args.embedding_device
    
    set_global_seed(42)  # Set global seed for reproducibility
    
    config = ConfigProfiles.create_config(
        profile_name=args.profile,
        backend=args.backend,
        embedding=args.embedding  # Add embedding selection
    )

    args.verbose = True  # Set to True for detailed config output
    if args.verbose:
        config.print_config()
    
    logger.info(f"Using profile: {args.profile}")
    logger.info(f"Using backend: {config.get_model_info()}")
    logger.info(f"Analysis depth: {args.depth}")
    
    # Initialize quality monitor
    monitor = QualityMonitor() if args.monitor else None
    args.vet_file = "./data/diploma_of_business.json"
    args.uni_file = "./data/933AA_Diploma_of_Business.json"
    
    # args.vet_file = "./data/sample_vet.json"
    # args.uni_file = "./data/sample_uni.json"
    try:
        # Load data
        logger.info("Loading qualifications...")
        vet_qual = load_vet_data(args.vet_file)
        uni_qual = load_uni_data(args.uni_file)
        
        logger.info(f"Loaded VET: {vet_qual.name} ({len(vet_qual.units)} units)")
        logger.info(f"Loaded Uni: {uni_qual.name} ({len(uni_qual.courses)} courses)")
        
        # Create interfaces using factory
        logger.info("Initializing AI interfaces...")
        genai = ModelFactory.create_genai_interface(config)
        
        if genai is None:
            logger.warning("No GenAI interface available - using fallback extraction")
        
        # Create embedding interface
        embeddings = ModelFactory.create_embedding_interface(config)
        
        if embeddings is None:
            logger.warning("No embedding interface available - using simple matching")
        
        # Create analyzer
        analyzer = SimplifiedAnalyzer(
            genai=genai,
            embeddings=embeddings,
            config=config.to_dict()
        )
        
        # Clear cache if requested
        if args.clear_cache:
            analyzer.extractor.clear_cache()
            logger.info("Cache cleared")
        
        # Run analysis
        logger.info("Starting analysis...")
        start_time = time.time()
        
        recommendations = analyzer.analyze(
            vet_qual,
            uni_qual,
            depth=args.depth
        )
        
        analysis_time = time.time() - start_time
        logger.info(f"Analysis completed in {analysis_time:.2f} seconds")
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        # Save results
        output_path = Path(args.output)
        output_path.parent.mkdir(exist_ok=True)
        
        # Add backend info to output
        analyzer.export_results(recommendations, str(output_path))
        
        # Generate report
        report_gen = ReportGenerator()
        html_path = output_path.with_suffix('.html')
        
        # Generate enhanced HTML report
        html_content = report_gen.generate_html_report(
            recommendations, vet_qual, uni_qual
        )
        
        # Add backend info to HTML
        backend_info = f"""
        <div class='summary-box'>
            <h3>Analysis Configuration</h3>
            <p><strong>Backend:</strong> {config.get_model_info()}</p>
            <p><strong>Profile:</strong> {args.profile}</p>
            <p><strong>Depth:</strong> {args.depth}</p>
            <p><strong>Processing Time:</strong> {analysis_time:.2f} seconds</p>
        </div>
        """
        
        # Insert backend info after the title
        html_content = html_content.replace(
            "<h1>Credit Transfer Analysis Report</h1>",
            f"<h1>Credit Transfer Analysis Report</h1>\n{backend_info}"
        )
        
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        logger.info(f"HTML report saved to {html_path}")
        
        logger.info("Exporting extracted skills...")
        
        # Generate complete report package including skills
        files = report_gen.generate_complete_report_package(
            recommendations, vet_qual, uni_qual
        )
        
        logger.info("Report package generated:")
        for file_type, filepath in files.items():
            logger.info(f"  {file_type}: {filepath}")
        # Save quality metrics if monitoring
        monitor = False
        if monitor:
            # Log metrics
            if len(recommendations) > 0:
                avg_score = sum(r.alignment_score for r in recommendations) / len(recommendations)
                avg_confidence = sum(r.confidence for r in recommendations) / len(recommendations)
                monitor.log_extraction("session", len(recommendations), analysis_time, avg_confidence)
                monitor.log_matching(avg_score, analysis_time)
            
            # Log backend-specific metrics
            if config.IS_OPENAI:
                monitor.log_ai_call()  # Track API calls
            
            session_file = monitor.save_session()
            logger.info(f"Quality metrics saved to {session_file}")
            
            # Print suggestions
            suggestions = monitor.suggest_improvements()
            if suggestions:
                print("\nQuality Improvement Suggestions:")
                for suggestion in suggestions:
                    print(f"  • {suggestion}")
        
        # Print summary
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print(f"Backend: {config.get_model_info()}")
        print(f"Profile: {args.profile}")
        print(f"Depth: {args.depth}")
        print(f"Time: {analysis_time:.2f} seconds")
        print(f"Recommendations: {len(recommendations)}")
        
        # Show top recommendations
        if recommendations:
            print("\nTop Recommendations:")
            for i, rec in enumerate(sorted(recommendations, 
                                          key=lambda x: x.alignment_score, 
                                          reverse=True)[:5], 1):
                print(f"{i}. {' + '.join(rec.get_vet_unit_codes())} → {rec.uni_course.code}")
                print(f"   Score: {rec.alignment_score:.1%} | Type: {rec.recommendation.value}")
        
        print(f"\nResults saved to: {output_path}")
        
        # Print backend-specific info
        if config.IS_OPENAI:
            print(f"\nOpenAI API calls made: Check Azure portal for usage")
        elif config.IS_VLLM:
            print(f"\nLocal model used: {config.MODEL_NAME}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()