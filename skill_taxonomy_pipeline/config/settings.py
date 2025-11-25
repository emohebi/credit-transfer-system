"""
Configuration settings for skill taxonomy pipeline with multi-factor matching
Incorporates semantic similarity, skill levels, and context throughout the process
"""
import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# MULTI-FACTOR MATCHING CONFIGURATION
# ============================================================================
# These weights are used throughout the pipeline for skill similarity calculation
# They should sum to 1.0 when normalized

MULTI_FACTOR_WEIGHTS = {
    "semantic_weight": float(os.environ.get("SEMANTIC_WEIGHT", "0.60")),  # Weight for text similarity
    "level_weight": float(os.environ.get("LEVEL_WEIGHT", "0.25")),      # Weight for skill level compatibility
    "context_weight": float(os.environ.get("CONTEXT_WEIGHT", "0.15")),   # Weight for context (practical/theoretical)
}

# Thresholds for different match types
MATCH_THRESHOLDS = {
    "direct_match_threshold": float(os.environ.get("DIRECT_MATCH_THRESHOLD", "0.90")),  # Direct/exact match
    "partial_threshold": float(os.environ.get("PARTIAL_THRESHOLD", "0.80")),           # Partial match
    "minimum_threshold": float(os.environ.get("MINIMUM_THRESHOLD", "0.65")),          # Minimum for consideration
}

# Level compatibility configuration
LEVEL_COMPATIBILITY = {
    "max_level_difference_for_dedup": 1,     # Max level difference to consider skills as duplicates
    "level_penalty_factor": 0.2,             # Penalty per level difference
    "prefer_higher_levels": True,            # Prefer higher level skills as masters in deduplication
}

# Context compatibility configuration
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
    "confidence_threshold": 0.7,  # Minimum confidence for including skills
    "min_skill_length": 3,        # Minimum character length for skill names
    "max_skill_length": 200,      # Maximum character length for skill names
    "batch_size": 1000,           # Batch size for processing
    "n_jobs": -1,                 # Number of parallel jobs (-1 for all CPUs)
}

# ============================================================================
# EMBEDDING SETTINGS
# ============================================================================

EMBEDDING_CONFIG = {
    "model_name": "sentence-transformers--all-mpnet-base-v2",
    # "model_name": "jinaai--jina-embeddings-v4",
    "batch_size": 8,
    "cache_embeddings": True,
    "normalize_embeddings": True,
    "device": "cuda" if os.environ.get("CUDA_AVAILABLE") else "cpu",
    "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
    "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
    # Similarity method selection
    "similarity_method": os.environ.get("SIMILARITY_METHOD", "faiss"),  # 'faiss' or 'matrix'
    
    # Matrix-specific settings
    "matrix_memory_threshold": 10000,  # Max samples for full matrix computation
    
    # FAISS-specific settings
    "faiss_exact_search_threshold": 5000,  # Use exact search if fewer samples
    
    # Multi-factor weights (reference to global config)
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# DEDUPLICATION SETTINGS
# ============================================================================

DEDUP_CONFIG = {
    "similarity_threshold": MATCH_THRESHOLDS["minimum_threshold"],  # Base threshold
    
    # Match type thresholds
    **MATCH_THRESHOLDS,
    
    # FAISS settings
    "use_faiss": True,
    "faiss_index_type": "IVF1024,Flat",
    "nprobe": 64,
    
    # General settings
    "fuzzy_ratio_threshold": 90,
    
    # Level and context settings
    **LEVEL_COMPATIBILITY,
    
    # Multi-factor weights
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# CLUSTERING SETTINGS
# ============================================================================

CLUSTERING_CONFIG = {
    "algorithm": "hdbscan",
    "min_cluster_size": 10,
    "min_samples": 5,
    "metric": "euclidean",
    "cluster_selection_epsilon": 0.0,
    "alpha": 1.0,
    "use_umap_reduction": True,
    "umap_n_components": 50,
    "umap_n_neighbors": 30,
    "umap_min_dist": 0.0,
    
    # Multi-factor clustering
    "use_multi_factor_clustering": True,
    "cluster_coherence_threshold": 0.7,  # Minimum coherence for valid clusters
    "split_high_variance_clusters": True,  # Split clusters with high level variance
    "merge_small_clusters": True,         # Merge very small clusters
    
    # Multi-factor weights
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# HIERARCHY SETTINGS
# ============================================================================

HIERARCHY_CONFIG = {
    "max_depth": 5,
    "min_children": 3,
    "max_children": 20,
    "balance_factor": 0.7,
    "use_llm_refinement": True,
    
    # Level-aware hierarchy
    "group_by_level_first": True,        # Create level-based groups first
    "max_level_span_per_node": 2,        # Max level difference within a node
    "preserve_context_groups": True,      # Keep similar contexts together
}

# ============================================================================
# VALIDATION SETTINGS
# ============================================================================

VALIDATION_CONFIG = {
    "coverage_threshold": 0.95,
    "coherence_threshold": 0.7,
    "distinctiveness_threshold": 0.5,
    "max_orphan_skills": 100,
    "validate_with_llm": True,
    
    # Multi-factor validation
    "check_level_consistency": True,      # Validate level assignments
    "check_context_alignment": True,      # Validate context assignments
    "minimum_cluster_coherence": 0.6,     # Minimum coherence score
}

# ============================================================================
# SKILL EXTRACTION SETTINGS (if using with models from attached code)
# ============================================================================

SKILL_EXTRACTION_CONFIG = {
    "use_multi_factor_extraction": True,
    "extract_skill_levels": True,
    "extract_skill_context": True,
    "confidence_threshold": 0.6,
    
    # Level detection keywords
    "level_keywords": {
        "follow": ["basic", "introductory", "fundamental", "beginning"],
        "assist": ["support", "help", "aid", "contribute"],
        "apply": ["implement", "use", "perform", "execute"],
        "enable": ["facilitate", "coordinate", "manage", "lead"],
        "ensure_advise": ["ensure", "advise", "consult", "recommend"],
        "initiate_influence": ["initiate", "influence", "drive", "champion"],
        "set_strategy": ["strategy", "vision", "direction", "transform"]
    },
    
    # Context detection keywords
    "context_keywords": {
        "practical": ["hands-on", "laboratory", "workshop", "applied", "project"],
        "theoretical": ["theory", "concept", "principle", "framework", "model"],
        "hybrid": ["combined", "integrated", "both", "mixed"]
    }
}

# ============================================================================
# LLM SETTINGS (if using Azure OpenAI)
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
# LLM_CONFIG = {
#     "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
#     "azure_endpoint": os.environ.get("ENDPOINT_URL"),
#     "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
#     "deployment_name": os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
    

#     "temperature": 0.0,
#     "max_tokens": 500,
#     "retry_attempts": 3,
#     "batch_size": 20,
#     "cache_responses": True,
#     "backed_type": "azure_openai"  # 'azure_openai' or 'vllm'
# }

# ============================================================================
# CATEGORY HIERARCHY (with expected levels)
# ============================================================================

CATEGORY_HIERARCHY = {
    "technical": {
        "parent": "Hard Skills",
        "expected_level_range": (2, 5),  # SFIA levels 2-5
        "subcategories": [
            "Engineering & Technology",
            "Information Technology",
            "Manufacturing & Production",
            "Quality & Testing",
            "Research & Development"
        ]
    },
    "cognitive": {
        "parent": "Cognitive Skills",
        "expected_level_range": (3, 6),  # SFIA levels 3-6
        "subcategories": [
            "Problem Solving",
            "Critical Thinking",
            "Decision Making",
            "Analytical Skills",
            "Creative Thinking"
        ]
    },
    "interpersonal": {
        "parent": "Soft Skills",
        "expected_level_range": (2, 5),  # SFIA levels 2-5
        "subcategories": [
            "Communication",
            "Leadership",
            "Teamwork",
            "Customer Service",
            "Conflict Resolution"
        ]
    },
    "domain_knowledge": {
        "parent": "Domain Expertise",
        "expected_level_range": (3, 7),  # SFIA levels 3-7
        "subcategories": [
            "Industry Knowledge",
            "Regulatory Compliance",
            "Business Acumen",
            "Subject Matter Expertise",
            "Market Knowledge"
        ]
    }
}

# Model configurations
EMBEDDING_MODELS = {
    "jinaai--jina-embeddings-v4": {
        "model_id": "jinaai/jina-embeddings-v4",
        "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
        "trust_remote_code": True,
        "embedding_dim": 2048
    },
    "Qwen--Qwen3-Embedding-8B": {
        "model_id": "Qwen/Qwen3-Embedding-8B",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 4096
    },
    "BAAI--bge-large-en-v1.5": {
        "model_id": "BAAI/bge-large-en-v1.5",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 1024
    },
    "BAAI--bge-base-en-v1.5": {
        "model_id": "BAAI/bge-base-en-v1.5",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 768
    },
    "sentence-transformers--all-MiniLM-L6-v2": {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 384
    },
    "sentence-transformers--all-mpnet-base-v2": {
        "model_id": "sentence-transformers/all-mpnet-base-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 768
    },
    "intfloat--e5-large-v2": {
        "model_id": "intfloat/e5-large-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 1024
    },
    "WhereIsAI--UAE-Large-V1": {
        "model_id": "WhereIsAI/UAE-Large-V1",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 1024
    }
}

# Model configurations
MODELS = {
    "mistralai--Mistral-7B-Instruct-v0.2": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
        "revision": "41b61a33a2483885c981aa79e0df6b32407ed873",
        "template": "Mistral"
    },
    "mistralai--Mistral-7B-Instruct-v0.3": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "revision": "e0bc86c23ce5aae1db576c8cca6f06f1f73af2db",
        "template": "Mistral"
    },
    "neuralmagic--Meta-Llama-3.1-70B-Instruct-quantized.w4a16": {
        "model_id": "neuralmagic/Meta-Llama-3.1-70B-Instruct-quantized.w4a16",
        "revision": "8c670bcdb23f58a977e1440354beb7c3e455961d",
        "template": "Llama"
    },
    "meta-llama--Llama-3.1-8B-Instruct": {
        "model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "revision": "0e9e39f249a16976918f6564b8830bc894c89659",
        "template": "Llama"
    },
    "neuralmagic--Meta-Llama-3.1-70B-Instruct-FP8": {
        "model_id": "neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",
        "revision": "08b31c0f951f2227f6cdbc088cdb6fd139aecf0f",
        "template": "Llama"
    },
    "microsoft--Phi-4-mini-instruct": {
        "model_id": "microsoft/Phi-4-mini-instruct",
        "revision": "c0fb9e74abda11b496b7907a9c6c9009a7a0488f",
        "template": "Phi"
    },
    "cortecs--Llama-3.3-70B-Instruct-FP8-Dynamic": {
        "model_id": "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic",
        "revision": "3722358cc2b990b22304489b2f87ef3bb876d6f6",
        "template": "Llama"
    },
    "gpt-oss-120b": {
        "model_id": "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models/gpt-oss-120b",
        "revision": None,
        "template": "GPT"
    },
    "gpt-oss-20b": {
        "model_id": "unsloth/gpt-oss-20b-unsloth-bnb-4bit",
        "revision": None,
        "template": "GPT"
    }
}

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

CONFIG: Dict[str, Any] = {
    "backed_type": "openai" ,  # 'openai' or 'vllm'
    "data": DATA_CONFIG,
    "embedding": EMBEDDING_CONFIG,
    "dedup": DEDUP_CONFIG,
    "clustering": CLUSTERING_CONFIG,
    "hierarchy": HIERARCHY_CONFIG,
    "validation": VALIDATION_CONFIG,
    "categories": CATEGORY_HIERARCHY,
    "extraction": SKILL_EXTRACTION_CONFIG,
    "llm": LLM_CONFIG,
    "multi_factor": {
        "weights": MULTI_FACTOR_WEIGHTS,
        "thresholds": MATCH_THRESHOLDS,
        "level_compatibility": LEVEL_COMPATIBILITY,
        "context_compatibility": CONTEXT_COMPATIBILITY,
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

# ============================================================================
# CONFIGURATION PROFILES (Quick presets)
# ============================================================================

def get_config_profile(profile: str = "balanced") -> Dict[str, Any]:
    """
    Get a pre-configured profile with different weight balances
    
    Profiles:
    - semantic_focused: Emphasizes text similarity (0.8, 0.1, 0.1)
    - level_aware: Balances semantic and level (0.5, 0.35, 0.15)
    - balanced: Equal consideration (0.6, 0.25, 0.15)
    - context_sensitive: Includes context heavily (0.5, 0.2, 0.3)
    """
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
            "semantic_weight": 0.65,
            "level_weight": 0.20,
            "context_weight": 0.15,
            "direct_match_threshold": 0.90,
            "partial_threshold": 0.80,
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
        # Update all relevant sections
        for key in ["embedding", "dedup", "clustering"]:
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
logger.info("MULTI-FACTOR SKILL MATCHING CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Semantic Weight: {MULTI_FACTOR_WEIGHTS['semantic_weight']:.2f}")
logger.info(f"Level Weight: {MULTI_FACTOR_WEIGHTS['level_weight']:.2f}")
logger.info(f"Context Weight: {MULTI_FACTOR_WEIGHTS['context_weight']:.2f}")
logger.info(f"Direct Match Threshold: {MATCH_THRESHOLDS['direct_match_threshold']:.2f}")
logger.info(f"Partial Match Threshold: {MATCH_THRESHOLDS['partial_threshold']:.2f}")
logger.info("=" * 60)
logger.info(f"Config: {CONFIG}")
logger.info("=" * 60)
