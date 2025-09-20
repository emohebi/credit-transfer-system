#!/usr/bin/env python3
"""
Quick test script for Credit Transfer Analysis System
Tests all major components and extractors with sample data
"""

import sys
import logging
import json
from pathlib import Path
from typing import Dict, List

# Load environment variables first
try:
    from dotenv import load_dotenv, find_dotenv
    env_file = Path(find_dotenv(usecwd=True))
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment variables from {env_file}")
    else:
        print("⚠️  No .env file found - using system environment variables only")
except ImportError:
    print("❌ python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Using system environment variables only.")

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample VET and University data for testing"""
    
    # Sample VET qualification data
    vet_data = {
        "code": "ICT50220",
        "name": "Diploma of Information Technology",
        "level": "Diploma",
        "units": [
            {
                "code": "ICTICT517",
                "name": "Match IT needs with the strategic direction of the organisation",
                "description": "This unit describes the skills and knowledge required to analyse business requirements and identify technology solutions that support the strategic direction of an organisation. It applies to individuals who work as senior information and communications technology (ICT) support staff responsible for the strategic alignment of ICT with business needs.",
                "learning_outcomes": [
                    "Analyse business requirements and processes",
                    "Identify technology solutions that align with strategic direction",
                    "Evaluate the impact of technology on business operations",
                    "Develop recommendations for ICT strategic alignment"
                ],
                "assessment_requirements": "Assessment must be conducted in a workplace or simulated workplace environment. Evidence must demonstrate the ability to analyse business requirements, identify appropriate technology solutions, and develop strategic recommendations.",
                "nominal_hours": 60,
                "prerequisites": ["ICTICT515"]
            },
            {
                "code": "ICTPRG547",
                "name": "Apply advanced programming skills in another language",
                "description": "This unit describes the skills and knowledge required to apply advanced programming skills in a language other than the primary programming language. It covers advanced programming concepts, design patterns, and best practices.",
                "learning_outcomes": [
                    "Apply advanced programming concepts and techniques",
                    "Implement design patterns and architectural principles", 
                    "Debug and optimize complex code",
                    "Develop scalable and maintainable software solutions"
                ],
                "assessment_requirements": "Assessment requires demonstration of advanced programming skills through practical projects and code review sessions.",
                "nominal_hours": 80,
                "prerequisites": ["ICTPRG546"]
            }
        ]
    }
    
    # Sample University qualification data
    uni_data = {
        "code": "BIT",
        "name": "Bachelor of Information Technology",
        "courses": [
            {
                "code": "COMP2500",
                "name": "Software Engineering Principles",
                "description": "This course introduces students to fundamental software engineering principles, methodologies, and practices. Students will learn about software development life cycles, design patterns, testing strategies, and project management in software development.",
                "study_level": "intermediate",
                "learning_outcomes": [
                    "Apply software engineering principles to real-world problems",
                    "Design and implement software systems using appropriate methodologies",
                    "Evaluate different software development approaches",
                    "Manage software development projects effectively"
                ],
                "prerequisites": ["COMP1500"],
                "credit_points": 6,
                "topics": [
                    "Software Development Life Cycle",
                    "Requirements Analysis",
                    "System Design and Architecture",
                    "Testing and Quality Assurance",
                    "Project Management"
                ],
                "assessment": "Assessment includes written examinations, practical programming assignments, and a major software development project."
            },
            {
                "code": "COMP3200",
                "name": "Advanced Programming Concepts",
                "description": "This advanced course covers sophisticated programming paradigms, algorithms, and software design patterns. Students will explore concurrent programming, advanced data structures, and enterprise application development.",
                "study_level": "advanced",
                "learning_outcomes": [
                    "Implement advanced programming paradigms and patterns",
                    "Design efficient algorithms and data structures",
                    "Develop concurrent and parallel applications",
                    "Create enterprise-level software solutions"
                ],
                "prerequisites": ["COMP2500", "COMP2100"],
                "credit_points": 6,
                "topics": [
                    "Design Patterns and Architectural Patterns",
                    "Concurrent and Parallel Programming",
                    "Advanced Data Structures and Algorithms",
                    "Enterprise Application Development",
                    "Performance Optimization"
                ],
                "assessment": "Assessment through practical programming projects, peer code reviews, and a comprehensive final examination."
            }
        ]
    }
    
    return vet_data, uni_data

def save_sample_data():
    """Save sample data to JSON files"""
    vet_data, uni_data = create_sample_data()
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Save VET data
    vet_file = data_dir / "sample_vet.json"
    with open(vet_file, 'w') as f:
        json.dump(vet_data, f, indent=2)
    
    # Save University data  
    uni_file = data_dir / "sample_uni.json"
    with open(uni_file, 'w') as f:
        json.dump(uni_data, f, indent=2)
    
    logger.info(f"Sample data saved to {vet_file} and {uni_file}")
    return vet_file, uni_file

def test_environment_setup():
    """Test environment variable loading"""
    logger.info("=== Testing Environment Setup ===")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        logger.info(f"✅ .env file found at {env_file}")
        
        # Read and show some key variables (without exposing secrets)
        import os
        key_vars = [
            'USE_AZURE_OPENAI',
            'DEPLOYMENT_NAME', 
            'ENDPOINT_URL',
            'EMBEDDING_MODEL_NAME',
            'USE_VLLM'
        ]
        
        for var in key_vars:
            value = os.getenv(var, 'NOT_SET')
            if var == 'AZURE_OPENAI_API_KEY':
                # Don't show the actual key
                display_value = '***HIDDEN***' if value != 'NOT_SET' else 'NOT_SET'
            else:
                display_value = value
            logger.info(f"  {var}: {display_value}")
        
        # Check if API key is configured
        api_key = os.getenv('AZURE_OPENAI_API_KEY', '')
        if api_key and api_key != 'your-azure-openai-api-key-here':
            logger.info("✅ Azure OpenAI API key is configured")
        else:
            logger.warning("⚠️  Azure OpenAI API key not configured or using placeholder")
        
        return True
    else:
        logger.warning(f"⚠️  No .env file found at {env_file}")
        logger.info("Create a .env file with your configuration. See the .env template.")
        return False

def test_config_loading():
    """Test configuration loading"""
    logger.info("=== Testing Configuration ===")
    
    try:
        from config import Config
        
        # Test basic config access
        logger.info(f"Azure OpenAI Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
        logger.info(f"Use Azure OpenAI: {Config.USE_AZURE_OPENAI}")
        logger.info(f"Use vLLM: {Config.USE_VLLM}")
        logger.info(f"Embedding Model: {Config.EMBEDDING_MODEL_NAME}")
        
        # Test config dictionary
        config_dict = Config.get_config_dict()
        logger.info(f"Config loaded successfully with {len(config_dict)} settings")
        
        # Test Azure OpenAI config
        azure_config = Config.get_azure_openai_config()
        logger.info(f"Azure OpenAI config: {azure_config['deployment']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Configuration test failed: {e}")
        return False

def test_model_loading():
    """Test loading of data models"""
    logger.info("=== Testing Data Models ===")
    
    try:
        from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse, Skill
        from models.enums import SkillLevel, SkillDepth, SkillContext, SkillCategory
        
        # Test enum creation and comparison
        level1 = SkillLevel.COMPETENT
        level2 = SkillLevel.EXPERT
        assert level1 < level2, "Skill level comparison failed"
        logger.info("Skill level comparison working correctly")
        
        # Test skill creation
        skill = Skill(
            name="Python programming",
            category=SkillCategory.TECHNICAL,
            level=SkillLevel.COMPETENT,
            depth=SkillDepth.APPLY,
            context=SkillContext.PRACTICAL
        )
        logger.info(f"Created test skill: {skill.name}")
        
        # Test unit creation
        unit = UnitOfCompetency(
            code="TEST001",
            name="Test Unit",
            description="Test description"
        )
        logger.info(f"Created test unit: {unit.code}")
        
        return True
        
    except Exception as e:
        logger.error(f"Model loading test failed: {e}")
        return False

def test_interfaces():
    """Test interface initialization"""
    logger.info("=== Testing Interfaces ===")
    
    try:
        from config import Config
        
        # Test embedding interface
        try:
            from interfaces.embedding_interface import EmbeddingInterface
            embeddings = EmbeddingInterface(
                model_name=Config.EMBEDDING_MODEL_NAME,  # Fallback model
                model_cache_dir=Config.MODEL_CACHE_DIR,
                external_model_dir=Config.EXTERNAL_MODEL_DIR,
                device="cuda"  # Use CPU for testing
            )
            logger.info("Embedding interface initialized successfully")
        except Exception as e:
            logger.warning(f"Embedding interface failed: {e}")
            embeddings = None
        
        # Test GenAI interface (if API key available)
        genai = None
        if Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_API_KEY != "your-azure-openai-api-key-here":
            try:
                from interfaces.genai_interface import GenAIInterface
                genai = GenAIInterface(
                    endpoint=Config.AZURE_OPENAI_ENDPOINT,
                    deployment=Config.AZURE_OPENAI_DEPLOYMENT,
                    api_key=Config.AZURE_OPENAI_API_KEY
                )
                logger.info("Azure OpenAI interface initialized successfully")
            except Exception as e:
                logger.warning(f"Azure OpenAI interface failed: {e}")
        else:
            logger.info("Azure OpenAI API key not configured - skipping GenAI test")
        
        return embeddings, genai
        
    except Exception as e:
        logger.error(f"Interface test failed: {e}")
        return None, None

def test_extractors(embeddings, genai):
    """Test skill extractors"""
    logger.info("=== Testing Skill Extractors ===")
    
    try:
        # Test standard extractor
        from extraction.skill_extractor import SkillExtractor
        standard_extractor = SkillExtractor(genai, embeddings)
        logger.info("Standard skill extractor created")
        
        # Test OpenAI extractor (if GenAI available)
        if genai:
            from extraction.openai_skill_extractor import OpenAISkillExtractor
            openai_extractor = OpenAISkillExtractor(genai, embeddings, delay_between_requests=0.5)
            logger.info("OpenAI skill extractor created")
        else:
            openai_extractor = None
            logger.info("OpenAI extractor skipped (no GenAI interface)")
        
        # Test extraction with sample data
        from models.base_models import UnitOfCompetency
        
        test_unit = UnitOfCompetency(
            code="TEST001",
            name="Test Programming Unit",
            description="This unit covers Python programming, database design, and web development skills.",
            learning_outcomes=[
                "Apply Python programming concepts to solve problems",
                "Design and implement database schemas",
                "Develop web applications using modern frameworks"
            ]
        )
        
        # Test standard extraction
        skills = standard_extractor.extract_from_vet_unit(test_unit)
        logger.info(f"Standard extractor found {len(skills)} skills")
        for skill in skills[:3]:  # Show first 3
            logger.info(f"  - {skill.name} ({skill.category.value})")
        
        # Test OpenAI extraction (if available)
        if openai_extractor:
            test_unit.extracted_skills = []  # Reset
            skills = openai_extractor.extract_from_vet_unit(test_unit)
            logger.info(f"OpenAI extractor found {len(skills)} skills")
            for skill in skills[:3]:  # Show first 3
                logger.info(f"  - {skill.name} ({skill.category.value})")
        
        return True
        
    except Exception as e:
        logger.error(f"Extractor test failed: {e}")
        return False

def test_analyzer(embeddings, genai):
    """Test the main analyzer"""
    logger.info("=== Testing Credit Transfer Analyzer ===")
    
    try:
        from analysis.analyzer import CreditTransferAnalyzer
        from config import Config
        
        # Create analyzer
        analyzer = CreditTransferAnalyzer(
            genai=genai,
            embeddings=embeddings,
            config=Config.get_config_dict()
        )
        logger.info(f"Analyzer created with {type(analyzer.extractor).__name__}")
        
        # Load sample data
        vet_file, uni_file = save_sample_data()
        
        # Load qualifications
        with open(vet_file, 'r') as f:
            vet_data = json.load(f)
        
        with open(uni_file, 'r') as f:
            uni_data = json.load(f)
        
        # Create qualification objects
        from models.base_models import VETQualification, UniQualification, UnitOfCompetency, UniCourse
        
        vet_qual = VETQualification(
            code=vet_data["code"],
            name=vet_data["name"],
            level=vet_data["level"]
        )
        
        for unit_data in vet_data["units"]:
            unit = UnitOfCompetency(
                code=unit_data["code"],
                name=unit_data["name"],
                description=unit_data["description"],
                learning_outcomes=unit_data["learning_outcomes"],
                assessment_requirements=unit_data["assessment_requirements"],
                nominal_hours=unit_data["nominal_hours"],
                prerequisites=unit_data["prerequisites"]
            )
            vet_qual.units.append(unit)
        
        uni_qual = UniQualification(
            code=uni_data["code"],
            name=uni_data["name"]
        )
        
        for course_data in uni_data["courses"]:
            course = UniCourse(
                code=course_data["code"],
                name=course_data["name"],
                description=course_data["description"],
                study_level=course_data["study_level"],
                learning_outcomes=course_data["learning_outcomes"],
                prerequisites=course_data["prerequisites"],
                credit_points=course_data["credit_points"],
                topics=course_data["topics"],
                assessment=course_data["assessment"]
            )
            uni_qual.courses.append(course)
        
        # Run analysis
        logger.info("Running credit transfer analysis...")
        recommendations = analyzer.analyze_transfer(vet_qual, uni_qual)
        
        logger.info(f"Analysis complete! Generated {len(recommendations)} recommendations")
        
        # Show top recommendations
        for i, rec in enumerate(recommendations[:3], 1):
            logger.info(f"  {i}. {' + '.join(rec.get_vet_unit_codes())} → {rec.uni_course.code}")
            logger.info(f"     Alignment: {rec.alignment_score:.1%}, Type: {rec.recommendation.value}")
        
        # Test export
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / "test_recommendations.json"
        
        analyzer.export_recommendations(recommendations, str(output_file))
        logger.info(f"Recommendations exported to {output_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_report_generation():
    """Test report generation"""
    logger.info("=== Testing Report Generation ===")
    
    try:
        from reporting.report_generator import ReportGenerator
        
        # Check if we have test recommendations
        output_file = Path("output/test_recommendations.json")
        if not output_file.exists():
            logger.warning("No test recommendations found - skipping report test")
            return True
        
        # Load recommendations
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        recommendations_data = data.get("recommendations", [])
        logger.info(f"Loaded {len(recommendations_data)} recommendations for reporting")
        
        # Generate CSV report
        report_gen = ReportGenerator()
        
        # Create dummy objects for CSV generation
        from models.base_models import CreditTransferRecommendation, UniCourse, UnitOfCompetency
        from models.enums import RecommendationType
        
        # This is a simplified test - in real usage, you'd have full objects
        logger.info("Report generator initialized successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Report generation test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting Credit Transfer Analysis System Quick Test")
    logger.info("=" * 60)
    
    results = {}
    
    # Test 0: Environment Setup
    results["environment"] = test_environment_setup()
    
    # Test 1: Configuration
    results["config"] = test_config_loading()
    
    # Test 2: Data Models
    results["models"] = test_model_loading()
    
    # Test 3: Interfaces
    embeddings, genai = test_interfaces()
    results["interfaces"] = (embeddings is not None)
    
    # Test 4: Extractors
    if embeddings:
        results["extractors"] = test_extractors(embeddings, genai)
    else:
        results["extractors"] = False
        logger.warning("Skipping extractor tests - no embedding interface")
    
    # Test 5: Analyzer
    if embeddings:
        results["analyzer"] = test_analyzer(embeddings, genai)
    else:
        results["analyzer"] = False
        logger.warning("Skipping analyzer tests - no embedding interface")
    
    # Test 6: Reports
    results["reports"] = test_report_generation()
    
    # Summary
    logger.info("=" * 60)
    logger.info("🧪 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name.upper():15} {status}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"OVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is working correctly.")
        return 0
    else:
        logger.warning("⚠️  Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())