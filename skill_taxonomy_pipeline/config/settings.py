"""
Configuration for Skill Assertion Pipeline
Three-object model: Skill → SkillAssertion → Unit of Competency

Design principle: Deduplicate skill labels, not teaching/context evidence.
"""
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
#  PATHS
# ═══════════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / "cache"

for d in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
#  DEDUPLICATION
# ═══════════════════════════════════════════════════════════════════

DEDUP_CONFIG = {
    "similarity_threshold": 0.90,       # High threshold for semantic dedup
    "use_genai_validation": True,        # Validate dedup candidates with LLM
    "genai_batch_size": 30,              # Batch size for LLM validation
    "max_candidates_per_skill": 20,      # Max neighbours to check
}

# ═══════════════════════════════════════════════════════════════════
#  EMBEDDING
# ═══════════════════════════════════════════════════════════════════

EMBEDDING_CONFIG = {
    "model_name": "jinaai--jina-embeddings-v4",
    "batch_size": 64,
    "normalize_embeddings": True,
    "device": os.environ.get("EMBEDDING_DEVICE", "cuda:1"),
    "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
    "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
}

# ═══════════════════════════════════════════════════════════════════
#  FACETS TO ASSIGN (configurable subset)
# ═══════════════════════════════════════════════════════════════════

FACETS_TO_ASSIGN = ["NAT", "TRF", "COG", "ASCED"]

FACET_ASSIGNMENT_CONFIG = {
    "facets_to_assign": FACETS_TO_ASSIGN,
    "use_genai": True,
    "genai_batch_size": 50,
    "use_llm_reranking": os.getenv("USE_LLM_RERANKING", "true") == "true",
    "rerank_top_k": 20,
    "embedding_similarity_threshold": 0.90,
    "multi_value_threshold": 0.25,
    "max_multi_values": 5,
}

# ═══════════════════════════════════════════════════════════════════
#  DATA PROCESSING
# ═══════════════════════════════════════════════════════════════════

DATA_CONFIG = {
    "confidence_threshold": 0.7,
    "min_skill_length": 3,
    "max_skill_length": 200,
}

# ═══════════════════════════════════════════════════════════════════
#  LLM BACKENDS
# ═══════════════════════════════════════════════════════════════════

LLM_CONFIG = {
    "openai": {
        "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
        "azure_endpoint": os.environ.get("ENDPOINT_URL"),
        "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        "deployment_name": os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
        "timeout": 60,
        "max_tokens": 4000,
        "temperature": 0.0,
    },
    "vllm": {
        "model_name": os.getenv("VLLM_MODEL_NAME", "gpt-oss-120b"),
        "num_gpus": int(os.getenv("VLLM_NUM_GPUS", "1")),
        "max_model_len": int(os.getenv("VLLM_MAX_MODEL_LEN", "10240")),
        "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
        "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
        "gpu_memory_utilization": 0.9,
    }
}

EMBEDDING_MODELS = {
    "jinaai--jina-embeddings-v4": {
        "model_id": "jinaai/jina-embeddings-v4",
        "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
        "trust_remote_code": True,
        "embedding_dim": 2048,
    },
    "sentence-transformers--all-MiniLM-L6-v2": {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 384,
    },
}

LLM_MODELS = {
    "meta-llama--Llama-3.1-8B-Instruct": {
        "model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "revision": "0e9e39f249a16976918f6564b8830bc894c89659",
        "template": "Llama",
    },
    "gpt-oss-120b": {
        "model_id": "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models/gpt-oss-120b",
        "revision": None,
        "template": "GPT",
    },
}

# ═══════════════════════════════════════════════════════════════════
#  AGGREGATE CONFIG (passed around the pipeline)
# ═══════════════════════════════════════════════════════════════════

CONFIG = {
    "backed_type": "openai" if os.getenv("USE_AZURE_OPENAI", "false") == "true" else "vllm",
    "data": DATA_CONFIG,
    "embedding": EMBEDDING_CONFIG,
    "dedup": DEDUP_CONFIG,
    "facet_assignment": FACET_ASSIGNMENT_CONFIG,
    "llm": LLM_CONFIG,
    "paths": {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "cache_dir": str(CACHE_DIR),
    },
    "models": {
        "embedding_models": EMBEDDING_MODELS,
        "llm_models": LLM_MODELS,
    },
}
