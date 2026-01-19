"""
Enhanced Configuration settings for multi-dimensional faceted skill taxonomy pipeline
Implements faceted taxonomy with multiple independent dimensions including ASCED
"""
import os
from pathlib import Path
from typing import Dict, Any

from config.facets import ALL_FACETS, FACET_PRIORITY

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
USE_ROOT = os.environ.get("USE_ROOT", "false")
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output_faceted"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


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
#  COMPLEXITY LEVELS (For reference - now part of COG facet)
# ═══════════════════════════════════════════════════════════════════════════

COMPLEXITY_LEVELS = {
    1: {"name": "Remember", "bloom_taxonomy": "Remember"},
    2: {"name": "Understand", "bloom_taxonomy": "Understand"},
    3: {"name": "Apply", "bloom_taxonomy": "Apply"},
    4: {"name": "Analyze", "bloom_taxonomy": "Analyze"},
    5: {"name": "Evaluate", "bloom_taxonomy": "Evaluate"},
    6: {"name": "Create", "bloom_taxonomy": "Create"},
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
    "model_name": "jinaai--jina-embeddings-v4",
    "batch_size": 8,
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
    "similarity_threshold": 0.85,
    **MATCH_THRESHOLDS,
    "use_faiss": False,
    "faiss_index_type": "IVF1024,Flat",
    "nprobe": 64,
    "fuzzy_ratio_threshold": 90,
    **LEVEL_COMPATIBILITY,
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# FACET ASSIGNMENT SETTINGS
# Now uses ASCED (Australian Standard Classification of Education) instead of IND
# ============================================================================

FACET_ASSIGNMENT_CONFIG = {
    "use_genai": True,
    "genai_batch_size": 50,
    "use_llm_reranking": os.getenv("USE_LLM_RERANKING", "true") == "true",
    "rerank_top_k": 20,
    "embedding_similarity_threshold": 0.90,
    "multi_value_threshold": 0.25,
    "max_multi_values": 5,
    "max_retries": 3,
    # Facets to assign (order matters - processed in this order)
    # Note: ASCED replaces IND (Industry Domain) for ASCED Field of Education
    "facets_to_assign": [
        "NAT",    # Skill Nature
        "TRF",    # Transferability
        "COG",    # Cognitive Complexity
        "CTX",    # Work Context
        "FUT",    # Future Readiness
        "LRN",    # Learning Context (from existing 'context' field)
        "DIG",    # Digital Intensity
        "ASCED",  # ASCED Field of Education (multi-value) - replaces IND
        "LVL",    # Proficiency Level (from existing 'level' field)
    ],
}

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

VALIDATION_CONFIG = {
    "min_coverage": 0.85,
    "target_coverage": 0.95,
    "min_facet_coverage": 0.80,
    "validate_all_facets": True,
    "validate_confidence_distribution": True,
    "min_avg_confidence": 0.5,
    "coverage_threshold": 0.95,
    "coherence_threshold": 0.7,
    "distinctiveness_threshold": 0.5,
    "max_orphan_skills": 100,
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
# MODEL CONFIGURATIONS "737fa5c46f0262ceba4a462ffa1c5bcf01da416f"
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
    "facet_assignment": FACET_ASSIGNMENT_CONFIG,
    "validation": VALIDATION_CONFIG,
    "llm": LLM_CONFIG,
    "multi_factor": {
        "weights": MULTI_FACTOR_WEIGHTS,
        "thresholds": MATCH_THRESHOLDS,
        "level_compatibility": LEVEL_COMPATIBILITY,
        "context_compatibility": CONTEXT_COMPATIBILITY,
    },
    "facets": ALL_FACETS,
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
            "semantic_weight": 1.0,
            "level_weight": 0.0,
            "context_weight": 0.0,
            "direct_match_threshold": 0.85,
            "partial_threshold": 0.85,
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
logger.info("FACETED SKILL TAXONOMY CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Facets: {len(ALL_FACETS)}")
logger.info(f"Facets to assign: {FACET_ASSIGNMENT_CONFIG['facets_to_assign']}")
logger.info(f"Training Packages: {len(TRAINING_PACKAGES)}")
logger.info(f"ASCED Classification: Australian Standard Classification of Education 2001")
logger.info("=" * 60)