"""
Enhanced Configuration settings for multi-dimensional skill taxonomy pipeline
Implements state-of-the-art taxonomy structure with 5-level hierarchy and cross-cutting dimensions
"""
import os
from pathlib import Path
from typing import Dict, Any

from config.structure import SKILL_DOMAINS, SKILL_FAMILIES

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
USE_ROOT = os.environ.get("USE_ROOT", "false")
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output_llm_domain"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

SKILL_DOMAINS = SKILL_DOMAINS
SKILL_FAMILIES = SKILL_FAMILIES
# ═══════════════════════════════════════════════════════════════════════════
#  AUSTRALIAN TRAINING PACKAGE CODES - Complete Reference
# ═══════════════════════════════════════════════════════════════════════════

TRAINING_PACKAGES = {
    # Primary Industries
    "ACM": "Animal Care and Management",
    "AHC": "Agriculture, Horticulture and Conservation and Land Management",
    "AMP": "Australian Meat Processing",
    "FWP": "Forest and Wood Products",
    "RGR": "Racing Industry",
    "SFI": "Seafood Industry",
    
    # Construction and Building
    "CPC": "Construction, Plumbing and Services",
    "CPP": "Property Services",
    "MSF": "Furnishing",
    
    # Automotive and Transport
    "AUM": "Automotive Manufacturing",
    "AUR": "Automotive Retail, Service and Repair",
    "AVI": "Aviation",
    "MAR": "Maritime",
    "TLI": "Transport and Logistics",
    
    # Manufacturing and Engineering
    "MEA": "Aeroskills",
    "MEM": "Manufacturing and Engineering",
    "MSM": "Manufacturing (Manufactured Mineral Products)",
    "MST": "Textiles, Clothing and Footwear",
    "PMA": "Pulp and Paper Manufacturing Industries",
    "PMB": "Polymer Manufacturing",
    "PMC": "Competitive Manufacturing",
    "FBP": "Food, Beverage and Pharmaceutical",
    
    # Technology and ICT
    "ICT": "Information and Communications Technology",
    "ICP": "Printing and Graphic Arts",
    
    # Health and Community
    "CHC": "Community Services",
    "HLT": "Health",
    
    # Business and Finance
    "BSB": "Business Services",
    "FNS": "Financial Services",
    "LGA": "Local Government",
    "PSP": "Public Sector",
    
    # Education and Training
    "TAE": "Training and Education",
    
    # Hospitality and Tourism
    "SIT": "Tourism, Travel and Hospitality",
    "SFL": "Floristry",
    
    # Creative Arts
    "CUA": "Creative Arts and Culture",
    "CUF": "Screen and Media",
    "CUS": "Sustainability",
    "CUV": "Visual Arts",
    "SHB": "Hairdressing and Beauty Services",
    
    # Public Safety and Security
    "CSC": "Correctional Services",
    "DEF": "Defence",
    "POL": "Police",
    "PUA": "Public Safety",
    
    # Resources and Utilities
    "DRG": "Drilling",
    "NWP": "Water",
    "RII": "Resources and Infrastructure Industry",
    "UEE": "Electrotechnology",
    "UEG": "Gas Industry",
    "UEP": "Electricity Supply Industry - Generation Sector",
    "UET": "Transmission, Distribution and Rail Sector",
    
    # Science and Laboratory
    "MSL": "Laboratory Operations",
    "MSS": "Sustainability",
    
    # Sport and Recreation
    "SIS": "Sport, Fitness and Recreation",
    
    # Retail and Personal Services
    "SIR": "Retail Services",
    "SIF": "Funeral Services"
}


# ═══════════════════════════════════════════════════════════════════════════
#  COMPLEXITY LEVELS (5 levels - Enhanced with AQF and Bloom's Taxonomy)
# ═══════════════════════════════════════════════════════════════════════════

COMPLEXITY_LEVELS = {
    1: {
        "name": "Foundational",
        "description": "Basic awareness, recall of facts, fundamental tasks under close supervision",
        "bloom_taxonomy": "Remember/Understand",
        "dreyfus_model": "Novice",
        "aqf_level": "Certificate I",
        "vet_context": "Pre-vocational, basic orientation, introductory skills"
    },
    2: {
        "name": "Basic",
        "description": "Understanding and application of routine procedures with guidance",
        "bloom_taxonomy": "Understand/Apply",
        "dreyfus_model": "Advanced Beginner",
        "aqf_level": "Certificate II-III",
        "vet_context": "Routine work, supervised application, developing competence"
    },
    3: {
        "name": "Intermediate",
        "description": "Independent application, analysis, and adaptation of learned skills",
        "bloom_taxonomy": "Apply/Analyze",
        "dreyfus_model": "Competent",
        "aqf_level": "Certificate III-IV",
        "vet_context": "Skilled work, autonomous practice, trade qualification level"
    },
    4: {
        "name": "Advanced",
        "description": "Complex problem-solving, synthesis, evaluation in varied contexts",
        "bloom_taxonomy": "Analyze/Evaluate",
        "dreyfus_model": "Proficient",
        "aqf_level": "Diploma/Advanced Diploma",
        "vet_context": "Complex operations, supervision, para-professional work"
    },
    5: {
        "name": "Expert",
        "description": "Mastery, innovation, creation of new knowledge and strategic application",
        "bloom_taxonomy": "Evaluate/Create",
        "dreyfus_model": "Expert",
        "aqf_level": "Degree and above",
        "vet_context": "Specialist expertise, strategic thinking, innovation and leadership"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  TRANSFERABILITY TYPES (4 categories - O*NET and ASC aligned)
# ═══════════════════════════════════════════════════════════════════════════

TRANSFERABILITY_TYPES = {
    "universal": {
        "name": "Universal/Core Competencies",
        "score": 4,
        "description": "Foundational skills applicable across all occupations (ASC Core Competencies)",
        "examples": ["Communication", "Teamwork", "Problem Solving", "Learning Agility", "Digital Literacy", "Critical Thinking", "Time Management", "Adaptability", "Initiative", "Resilience"],
        "keywords": ["communication", "teamwork", "problem solving", "learning", "adaptability", "critical thinking", "time management", "ethics", "work ethic"]
    },
    "cross_sector": {
        "name": "Cross-Sector/Transferable",
        "score": 3,
        "description": "Specialist skills transferable across multiple industries and sectors",
        "examples": ["Project Management", "Customer Service", "Data Analysis", "Quality Assurance", "WHS", "Supervision", "Budgeting"],
        "keywords": ["project management", "customer service", "data analysis", "quality", "safety", "compliance", "budgeting", "supervision", "coordination"]
    },
    "sector_specific": {
        "name": "Sector-Specific",
        "score": 2,
        "description": "Skills relevant within a specific sector or closely related industries",
        "examples": ["Healthcare Protocols", "Construction Methods", "Manufacturing Processes", "Hospitality Standards", "Agricultural Techniques"],
        "keywords": ["industry practices", "sector standards", "domain methods", "sector protocols"]
    },
    "occupation_specific": {
        "name": "Occupation-Specific/Technical",
        "score": 1,
        "description": "Highly specialized skills unique to particular occupation or role",
        "examples": ["Welding Certification", "Dental Procedures", "Legal Drafting", "Aircraft Maintenance", "Specific Machinery Operation"],
        "keywords": ["technical", "specialized", "certification", "licensed", "regulated", "specific equipment"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  DIGITAL INTENSITY LEVELS (5 levels - 0-4 scale)
# ═══════════════════════════════════════════════════════════════════════════

DIGITAL_INTENSITY_LEVELS = {
    0: {
        "name": "No/Minimal Digital",
        "description": "Primarily manual/physical tasks with negligible digital tool usage",
        "examples": ["Manual labor", "Traditional crafts", "Physical caregiving", "Manual trades"],
        "percentage": "0-10% of work involves digital tools"
    },
    1: {
        "name": "Low Digital",
        "description": "Basic digital literacy, simple tool usage (email, basic software, POS)",
        "examples": ["Email communication", "Basic data entry", "POS systems", "Simple device operation"],
        "percentage": "11-30% of work involves digital tools"
    },
    2: {
        "name": "Medium Digital",
        "description": "Regular use of specialized software and digital platforms",
        "examples": ["Office productivity suites", "Industry-specific software", "Digital communication tools", "CAD"],
        "percentage": "31-60% of work involves digital tools"
    },
    3: {
        "name": "High Digital",
        "description": "Advanced digital skills, complex software, data manipulation, programming",
        "examples": ["Programming", "Data analytics", "Digital design", "System administration", "Database management"],
        "percentage": "61-85% of work involves digital tools"
    },
    4: {
        "name": "Advanced Digital/Tech-Native",
        "description": "Cutting-edge technology, AI/ML, automation, emerging tech, digital innovation",
        "examples": ["AI/ML development", "Cloud architecture", "Cybersecurity", "IoT", "Blockchain", "Quantum computing"],
        "percentage": "86-100% of work involves digital tools"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FUTURE-READINESS CATEGORIES (4 categories - Labor Market aligned)
# ═══════════════════════════════════════════════════════════════════════════

FUTURE_READINESS = {
    "declining": {
        "name": "Declining Demand",
        "score": 1,
        "description": "Skills being automated, phased out, or experiencing decreased labor market demand",
        "drivers": ["Automation", "Technological displacement", "Industry decline", "Process optimization"],
        "keywords": ["manual data entry", "routine clerical", "basic bookkeeping", "repetitive tasks", "manual assembly"],
        "trend": "↓ Decreasing"
    },
    "stable": {
        "name": "Stable Demand",
        "score": 2,
        "description": "Consistent demand with minimal change expected in medium term",
        "drivers": ["Ongoing essential services", "Mature industries", "Regulated professions"],
        "keywords": ["core trades", "essential services", "foundational skills", "licensed trades"],
        "trend": "→ Steady"
    },
    "growing": {
        "name": "Growing Demand",
        "score": 3,
        "description": "Increasing importance and labor market demand driven by economic/social trends",
        "drivers": ["Population growth", "Demographic shifts", "Service economy expansion", "Technology adoption"],
        "keywords": ["digital skills", "healthcare", "data analysis", "sustainability", "aged care", "NDIS", "customer experience"],
        "trend": "↑ Increasing"
    },
    "transformative": {
        "name": "Transformative/Emerging",
        "score": 4,
        "description": "Critical for future economy, rapidly evolving, high-growth sectors",
        "drivers": ["Digital transformation", "Climate change", "Innovation economy", "Emerging technologies"],
        "keywords": ["AI", "machine learning", "renewable energy", "cybersecurity", "biotechnology", "quantum computing", "green skills", "circular economy"],
        "trend": "↑↑ Exponential"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL NATURE TYPES (5 types - O*NET and BLS aligned)
# ═══════════════════════════════════════════════════════════════════════════

SKILL_NATURE_TYPES = {
    "content": {
        "name": "Content/Knowledge Skills",
        "description": "Background knowledge, domain expertise, and specialized understanding",
        "o_net_category": "Content",
        "examples": ["Mathematics", "Science", "Language", "Domain knowledge", "Technical knowledge"],
        "characteristics": ["Learned", "Declarative", "Domain-specific"]
    },
    "process": {
        "name": "Process/Cognitive Skills",
        "description": "Information processing, cognitive operations, thinking skills",
        "o_net_category": "Process",
        "examples": ["Critical thinking", "Active learning", "Monitoring", "Active listening"],
        "characteristics": ["Thinking", "Processing", "Analyzing"]
    },
    "social": {
        "name": "Social/Interpersonal Skills",
        "description": "Interpersonal interaction, collaboration, and relationship management",
        "o_net_category": "Social",
        "examples": ["Service orientation", "Persuasion", "Coordination", "Negotiation", "Instructing"],
        "characteristics": ["Interactive", "Relational", "Collaborative"]
    },
    "technical": {
        "name": "Technical/Practical Skills",
        "description": "Equipment operation, tool usage, hands-on technical abilities",
        "o_net_category": "Technical",
        "examples": ["Equipment operation", "Technology design", "Programming", "Quality control"],
        "characteristics": ["Procedural", "Manual", "Applied"]
    },
    "resource": {
        "name": "Resource Management Skills",
        "description": "Allocation and management of time, finances, materials, and personnel",
        "o_net_category": "Resource Management",
        "examples": ["Time management", "Financial resources", "Material resources", "Personnel management"],
        "characteristics": ["Organizing", "Planning", "Allocating"]
    }
}

CONTEXT_TYPES = {
    "theoretical": {
        "name": "Theoretical/Academic",
        "description": "Primarily conceptual learning in classroom/academic settings",
        "learning_environment": "Classroom, lecture, online learning",
        "examples": ["Theory courses", "Academic study", "Conceptual frameworks"]
    },
    "practical": {
        "name": "Practical/Applied",
        "description": "Hands-on application in workshops, labs, or simulated environments",
        "learning_environment": "Workshop, laboratory, training facility",
        "examples": ["Trade skills", "Laboratory work", "Practical demonstrations"]
    },
    "workplace": {
        "name": "Workplace/On-the-Job",
        "description": "Skills applied directly in real workplace settings",
        "learning_environment": "Actual workplace, apprenticeship, traineeship",
        "examples": ["Apprenticeships", "Work placements", "On-the-job training"]
    },
    "hybrid": {
        "name": "Hybrid/Blended",
        "description": "Combination of theoretical knowledge and practical application",
        "learning_environment": "Mixed classroom and workshop/workplace",
        "examples": ["VET qualifications", "Dual-sector programs", "Work-integrated learning"]
    },
    "digital": {
        "name": "Digital/Virtual",
        "description": "Primarily delivered through digital platforms and virtual environments",
        "learning_environment": "Online, virtual reality, simulation software",
        "examples": ["E-learning", "Virtual simulations", "Remote collaboration"]
    }
}

# ============================================================================
# MULTI-FACTOR MATCHING CONFIGURATION
# ============================================================================

MULTI_FACTOR_WEIGHTS = {
    "semantic_weight": float(os.environ.get("SEMANTIC_WEIGHT", "0.60")),
    "level_weight": float(os.environ.get("LEVEL_WEIGHT", "0.25")),
    "context_weight": float(os.environ.get("CONTEXT_WEIGHT", "0.15")),
}

MATCH_THRESHOLDS = {
    "direct_match_threshold": float(os.environ.get("DIRECT_MATCH_THRESHOLD", "0.90")),
    "partial_threshold": float(os.environ.get("PARTIAL_THRESHOLD", "0.80")),
    "minimum_threshold": float(os.environ.get("MINIMUM_THRESHOLD", "0.65")),
}

LEVEL_COMPATIBILITY = {
    "max_level_difference_for_dedup": 1,
    "level_penalty_factor": 0.2,
    "prefer_higher_levels": True,
}

CONTEXT_COMPATIBILITY = {
    "practical_practical": 1.0,
    "practical_hybrid": 0.7,
    "practical_theoretical": 0.3,
    "theoretical_theoretical": 1.0,
    "theoretical_hybrid": 0.7,
    "theoretical_practical": 0.3,
    "hybrid_practical": 0.7,
    "hybrid_theoretical": 0.7,
    "hybrid_hybrid": 1.0,
}

# ============================================================================
# DATA PROCESSING SETTINGS
# ============================================================================

DATA_CONFIG = {
    "confidence_threshold": 0.7,
    "min_skill_length": 3,
    "max_skill_length": 200,
    "batch_size": 1000,
    "n_jobs": -1,
}

# ============================================================================
# EMBEDDING SETTINGS
# ============================================================================

EMBEDDING_CONFIG = {
    # "model_name": "sentence-transformers--all-mpnet-base-v2",
    "model_name": "jinaai--jina-embeddings-v4",
    # "model_name": "Qwen--Qwen3-Embedding-0.6B",
    # "model_name": "sentence-transformers--all-MiniLM-L6-v2",
    "batch_size": 512,
    "cache_embeddings": True,
    "normalize_embeddings": True,
    "device": "cuda" if os.environ.get("CUDA_AVAILABLE") else "cuda:1",
    "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
    "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
    "similarity_method": os.environ.get("SIMILARITY_METHOD", "matrix"),
    "matrix_memory_threshold": 500000,
    "faiss_exact_search_threshold": 5000,
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# DEDUPLICATION SETTINGS
# ============================================================================

DEDUP_CONFIG = {
    "similarity_threshold": 0.9, # MATCH_THRESHOLDS["partial_threshold"],
    **MATCH_THRESHOLDS,
    "use_faiss": False,
    "faiss_index_type": "IVF1024,Flat",
    "nprobe": 64,
    "fuzzy_ratio_threshold": 90,
    **LEVEL_COMPATIBILITY,
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# FAMILY ASSIGNMENT SETTINGS (Replaces Clustering)
# ============================================================================

FAMILY_ASSIGNMENT_CONFIG = {
    "use_genai": True,
    "genai_batch_size": 50,
    "fallback_to_keyword_matching": True,
    "keyword_match_threshold": 3,
    "use_embedding_similarity": True,
    "embedding_similarity_threshold": 2.8,
    "max_retries": 3,
    # LLM Re-ranking settings (Top-K + LLM selection for better accuracy)
    "use_llm_reranking": os.getenv("USE_LLM_RERANKING", "true") == "true",  # Enable LLM re-ranking of top-K embedding candidates
    "rerank_top_k": 3,          # Number of top candidates to consider for re-ranking
    "rerank_similarity_threshold": 0.6,  # Min similarity for candidates to be re-ranked
}

# ============================================================================
# HIERARCHY SETTINGS
# ============================================================================

HIERARCHY_CONFIG = {
    "max_children": 25,
    "min_children": 2,
    "max_depth": 4,  # Domain → Family → Group → Skills
    "balance_threshold": 0.3,
    "max_level_span_per_node": 2,
    "enable_cross_cutting_dimensions": True,
    "enable_transferability_scoring": False,
    "enable_digital_intensity_scoring": False,
    "enable_future_readiness_scoring": False,
    "enable_skill_nature_classification": False,
    "enable_context_classification": True,
    "build_skill_relationships": True,
    "max_related_skills": 20,
    "relationship_similarity_threshold": 0.85,
    "include_training_package_alignment": True,
    "include_qualification_mapping": True,
    "include_unit_of_competency_links": True,
    "include_industry_sector_codes": True,
    "include_occupation_codes": True,
    "enable_skill_pathways": True,
    "enable_prerequisite_mapping": True,
    "enable_licensing_requirements": True,
    "use_llm_refinement": False
}

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

VALIDATION_CONFIG = {
    "min_coverage": 0.85,
    "target_coverage": 0.95,
    "min_cluster_coherence": 0.65,
    "target_cluster_coherence": 0.80,
    "expected_depth_range": (3, 4),
    "min_balance_score": 0.45,
    "expected_domains": 15,
    "expected_families_range": (85, 110),
    "require_all_dimensions": True,
    "validate_complexity_distribution": True,
    "validate_transferability_variety": True,
    "validate_digital_intensity_range": True,
    "validate_future_readiness_distribution": True,
    "validate_training_package_coverage": True,
    "validate_aqf_alignment": True,
    "min_skills_per_family": 5,
    "max_skills_per_family": 5000,
    "min_avg_relationships": 1.5,
    "max_isolated_skills_percent": 10,
    "coverage_threshold": 0.95,
    "coherence_threshold": 0.7,
    "distinctiveness_threshold": 0.5,
    "max_orphan_skills": 100,
    "validate_with_llm": True,
    "check_level_consistency": True,
    "check_context_alignment": True,
    "minimum_cluster_coherence": 0.6,
    "validate_domain_assignment": True,
    "validate_transferability_scores": True,
    "validate_skill_relationships": True,
}

# ============================================================================
# LLM SETTINGS
# ============================================================================

LLM_CONFIG = {
    "openai": {
        "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
        "azure_endpoint": os.environ.get("ENDPOINT_URL"),
        "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        "deployment_name": os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
        "timeout": 60,
        "max_tokens": 4000,
        "temperature": 0.0,
        "rate_limit_delay": 1.0
    },
    "vllm": {
        "model_name": os.getenv("VLLM_MODEL_NAME", "gpt-oss-120b"),
        "num_gpus": int(os.getenv("VLLM_NUM_GPUS", "1")),
        "max_model_len": int(os.getenv("VLLM_MAX_MODEL_LEN", "10240")),
        "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
        "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
        "tensor_parallel_size": 1,
        "gpu_memory_utilization": 0.9
    }
}

# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

EMBEDDING_MODELS = {
    "jinaai--jina-embeddings-v4": {
        "model_id": "jinaai/jina-embeddings-v4",
        "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
        "trust_remote_code": True,
        "embedding_dim": 2048
    },
    "Qwen--Qwen3-Embedding-0.6B": {
        "model_id": "Qwen/Qwen3-Embedding-0.6B",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 1024
    },
    "sentence-transformers--all-mpnet-base-v2": {
        "model_id": "sentence-transformers/all-mpnet-base-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 768
    },
    "sentence-transformers--all-MiniLM-L6-v2": {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 384
    },
}

MODELS = {
    "meta-llama--Llama-3.1-8B-Instruct": {
        "model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "revision": "0e9e39f249a16976918f6564b8830bc894c89659",
        "template": "Llama"
    },
    "gpt-oss-120b": {
        "model_id": "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models/gpt-oss-120b",
        "revision": None,
        "template": "GPT"
    },
}

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

CONFIG: Dict[str, Any] = {
    "backed_type": "openai" if os.getenv("USE_AZURE_OPENAI", "false") == "true" else "vllm",
    "data": DATA_CONFIG,
    "embedding": EMBEDDING_CONFIG,
    "dedup": DEDUP_CONFIG,
    "family_assignment": FAMILY_ASSIGNMENT_CONFIG,
    "hierarchy": HIERARCHY_CONFIG,
    "validation": VALIDATION_CONFIG,
    "llm": LLM_CONFIG,
    "multi_factor": {
        "weights": MULTI_FACTOR_WEIGHTS,
        "thresholds": MATCH_THRESHOLDS,
        "level_compatibility": LEVEL_COMPATIBILITY,
        "context_compatibility": CONTEXT_COMPATIBILITY,
    },
    "taxonomy": {
        "domains": SKILL_DOMAINS,
        "families": SKILL_FAMILIES,
        "complexity_levels": COMPLEXITY_LEVELS,
        "transferability": TRANSFERABILITY_TYPES,
        "digital_intensity": DIGITAL_INTENSITY_LEVELS,
        "future_readiness": FUTURE_READINESS,
        "skill_nature": SKILL_NATURE_TYPES,
    },
    "paths": {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "cache_dir": str(CACHE_DIR),
    },
    "models": {
        "embedding_models": EMBEDDING_MODELS,
        "llm_models": MODELS,
    }
}


def get_config_profile(profile: str = "balanced") -> Dict[str, Any]:
    """Get a pre-configured profile with different weight balances"""
    profiles = {
        "semantic_focused": {
            "semantic_weight": 0.80,
            "level_weight": 0.10,
            "context_weight": 0.10,
            "direct_match_threshold": 0.85,
            "partial_threshold": 0.75,
        },
        "level_aware": {
            "semantic_weight": 0.50,
            "level_weight": 0.35,
            "context_weight": 0.15,
            "direct_match_threshold": 0.88,
            "partial_threshold": 0.78,
        },
        "balanced": {
            "semantic_weight": 0.80,
            "level_weight": 0.10,
            "context_weight": 0.10,
            "direct_match_threshold": 0.95,
            "partial_threshold": 0.90,
        },
        "context_sensitive": {
            "semantic_weight": 0.50,
            "level_weight": 0.20,
            "context_weight": 0.30,
            "direct_match_threshold": 0.92,
            "partial_threshold": 0.82,
        }
    }
    
    profile_config = CONFIG.copy()
    
    if profile in profiles:
        weights = profiles[profile]
        for key in ["embedding", "dedup"]:
            profile_config[key].update(weights)
        profile_config["multi_factor"]["weights"].update(weights)
        profile_config["multi_factor"]["thresholds"].update(weights)
    
    return profile_config


# ============================================================================
# LOGGING
# ============================================================================

import logging

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("SKILL TAXONOMY CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Skill Domains: {len(SKILL_DOMAINS)}")
logger.info(f"Skill Families: {len(SKILL_FAMILIES)}")
logger.info(f"Training Packages: {len(TRAINING_PACKAGES)}")
logger.info("=" * 60)