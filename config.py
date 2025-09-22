"""
Configuration settings for the Credit Transfer Analysis System
Updated to include batch processing options
"""

import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded environment variables from {env_path}")
    else:
        load_dotenv()
        print("Loaded environment variables from .env file")
except ImportError:
    print("python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")


class Config:
    """System configuration with batch processing support"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    CACHE_DIR = BASE_DIR / "cache"
    
    # Create directories if they don't exist
    for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("ENDPOINT_URL", "https://ehsaninstance1.openai.azure.com/")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("DEPLOYMENT_NAME", "gpt-4o")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", None)
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    AZURE_OPENAI_TIMEOUT = int(os.getenv("AZURE_OPENAI_TIMEOUT", "60"))
    AZURE_OPENAI_MAX_TOKENS = int(os.getenv("AZURE_OPENAI_MAX_TOKENS", "4000"))
    AZURE_OPENAI_TEMPERATURE = float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.0"))
    USE_AZURE_OPENAI = os.getenv("USE_AZURE_OPENAI", "true").lower() == "true"
    
    # vLLM Configuration
    USE_VLLM = os.getenv("USE_VLLM", "false").lower() == "true"
    VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "meta-llama--Llama-3.1-8B-Instruct")
    VLLM_NUM_GPUS = int(os.getenv("VLLM_NUM_GPUS", "1"))
    VLLM_MAX_MODEL_LEN = int(os.getenv("VLLM_MAX_MODEL_LEN", "8192"))
    
    # Batch Processing Configuration
    USE_VLLM_BATCH = os.getenv("USE_VLLM_BATCH", "false").lower() == "true"
    VLLM_BATCH_SIZE = int(os.getenv("VLLM_BATCH_SIZE", "8"))
    VLLM_MAX_BATCH_SIZE = int(os.getenv("VLLM_MAX_BATCH_SIZE", "16"))
    VLLM_BATCH_TIMEOUT = int(os.getenv("VLLM_BATCH_TIMEOUT", "120"))
    
    # Model directories
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub")
    EXTERNAL_MODEL_DIR = os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models")
    
    # Legacy Web API Configuration (kept for compatibility)
    GENAI_ENDPOINT = os.getenv("GENAI_ENDPOINT", "http://localhost:8080")
    GENAI_API_KEY = os.getenv("GENAI_API_KEY", None)
    GENAI_TIMEOUT = int(os.getenv("GENAI_TIMEOUT", "30"))
    USE_GENAI = os.getenv("USE_GENAI", "false").lower() == "true"
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "jinaai--jina-embeddings-v4")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    EMBEDDING_MODE = os.getenv("EMBEDDING_MODE", "embedding")
    
    # Legacy embedding configurations
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_ENDPOINT = os.getenv("EMBEDDING_ENDPOINT", None)
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", None)
    USE_EMBEDDING_API = os.getenv("USE_EMBEDDING_API", "false").lower() == "true"
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))
    
    # Analysis Configuration
    MIN_ALIGNMENT_SCORE = float(os.getenv("MIN_ALIGNMENT_SCORE", "0.5"))
    MAX_UNIT_COMBINATION = int(os.getenv("MAX_UNIT_COMBINATION", "3"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))
    PARTIAL_THRESHOLD = float(os.getenv("PARTIAL_THRESHOLD", "0.6"))
    
    # Scoring Weights
    COVERAGE_WEIGHT = float(os.getenv("COVERAGE_WEIGHT", "0.5"))
    CONTEXT_WEIGHT = float(os.getenv("CONTEXT_WEIGHT", "0.25"))
    QUALITY_WEIGHT = float(os.getenv("QUALITY_WEIGHT", "0.15"))
    EDGE_PENALTY_WEIGHT = float(os.getenv("EDGE_PENALTY_WEIGHT", "0.1"))
    
    # Edge Case Thresholds
    CONTEXT_IMBALANCE_THRESHOLD = float(os.getenv("CONTEXT_IMBALANCE_THRESHOLD", "0.3"))
    BREADTH_RATIO_MIN = float(os.getenv("BREADTH_RATIO_MIN", "0.7"))
    BREADTH_RATIO_MAX = float(os.getenv("BREADTH_RATIO_MAX", "1.5"))
    
    # Study Level Configuration
    STUDY_LEVEL_WEIGHTS = {
        "introductory": 0.2,
        "intermediate": 0.4,
        "advanced": 0.6,
        "specialized": 0.8,
        "postgraduate": 1.0
    }
    
    STUDY_LEVEL_SKILL_MAPPING = {
        "introductory": "NOVICE",
        "intermediate": "COMPETENT",
        "advanced": "PROFICIENT",
        "specialized": "EXPERT",
        "postgraduate": "EXPERT"
    }
    
    # Credit Hour Configuration
    CREDIT_POINT_TO_HOURS = float(os.getenv("CREDIT_POINT_TO_HOURS", "12.5"))
    HOUR_RATIO_MIN = float(os.getenv("HOUR_RATIO_MIN", "0.7"))
    HOUR_RATIO_MAX = float(os.getenv("HOUR_RATIO_MAX", "1.5"))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = OUTPUT_DIR / "analysis.log"
    
    # Cache Configuration
    ENABLE_CACHE = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_EXPIRY_DAYS = int(os.getenv("CACHE_EXPIRY_DAYS", "30"))
    
    # Report Configuration
    REPORT_FORMAT = os.getenv("REPORT_FORMAT", "json")
    INCLUDE_EDGE_CASES = os.getenv("INCLUDE_EDGE_CASES", "true").lower() == "true"
    MAX_RECOMMENDATIONS_PER_COURSE = int(os.getenv("MAX_RECOMMENDATIONS_PER_COURSE", "5"))
    
    @classmethod
    def get_config_dict(cls) -> dict:
        """Get configuration as dictionary"""
        return {
            "min_alignment_score": cls.MIN_ALIGNMENT_SCORE,
            "max_unit_combination": cls.MAX_UNIT_COMBINATION,
            "similarity_threshold": cls.SIMILARITY_THRESHOLD,
            "partial_threshold": cls.PARTIAL_THRESHOLD,
            "use_vllm_batch": cls.USE_VLLM_BATCH,
            "vllm_batch_size": cls.VLLM_BATCH_SIZE,
            "weights": {
                "coverage": cls.COVERAGE_WEIGHT,
                "context": cls.CONTEXT_WEIGHT,
                "quality": cls.QUALITY_WEIGHT,
                "edge_penalty": cls.EDGE_PENALTY_WEIGHT
            },
            "thresholds": {
                "context_imbalance": cls.CONTEXT_IMBALANCE_THRESHOLD,
                "breadth_ratio_min": cls.BREADTH_RATIO_MIN,
                "breadth_ratio_max": cls.BREADTH_RATIO_MAX
            }
        }
    
    @classmethod
    def get_azure_openai_config(cls) -> dict:
        """Get Azure OpenAI configuration as dictionary"""
        return {
            "endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "deployment": cls.AZURE_OPENAI_DEPLOYMENT,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "timeout": cls.AZURE_OPENAI_TIMEOUT,
            "max_tokens": cls.AZURE_OPENAI_MAX_TOKENS,
            "temperature": cls.AZURE_OPENAI_TEMPERATURE
        }
    
    @classmethod
    def get_vllm_config(cls) -> dict:
        """Get vLLM configuration as dictionary"""
        return {
            "model_name": cls.VLLM_MODEL_NAME,
            "number_gpus": cls.VLLM_NUM_GPUS,
            "max_model_len": cls.VLLM_MAX_MODEL_LEN,
            "use_batch": cls.USE_VLLM_BATCH,
            "batch_size": cls.VLLM_BATCH_SIZE,
            "max_batch_size": cls.VLLM_MAX_BATCH_SIZE,
            "batch_timeout": cls.VLLM_BATCH_TIMEOUT,
            "model_cache_dir": cls.MODEL_CACHE_DIR,
            "external_model_dir": cls.EXTERNAL_MODEL_DIR
        }
    
    @classmethod
    def save_config(cls, filepath: str = None):
        """Save configuration to file"""
        import json
        
        if filepath is None:
            filepath = cls.OUTPUT_DIR / "config.json"
        
        config_dict = cls.get_config_dict()
        config_dict["azure_openai"] = cls.get_azure_openai_config()
        config_dict["vllm"] = cls.get_vllm_config()
        
        with open(filepath, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    @classmethod
    def load_config(cls, filepath: str):
        """Load configuration from file"""
        import json
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        # Update class attributes
        for key, value in config.items():
            if key == "azure_openai":
                for azure_key, azure_value in value.items():
                    attr_name = f"AZURE_OPENAI_{azure_key.upper()}"
                    if hasattr(cls, attr_name):
                        setattr(cls, attr_name, azure_value)
            elif key == "vllm":
                for vllm_key, vllm_value in value.items():
                    if vllm_key == "use_batch":
                        setattr(cls, "USE_VLLM_BATCH", vllm_value)
                    elif vllm_key == "batch_size":
                        setattr(cls, "VLLM_BATCH_SIZE", vllm_value)
                    else:
                        attr_name = f"VLLM_{vllm_key.upper()}"
                        if hasattr(cls, attr_name):
                            setattr(cls, attr_name, vllm_value)
            elif hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)

    # Model configurations
    EMBEDDING_MODELS = {
        "jinaai--jina-embeddings-v4": {
            "model_id": "jinaai/jina-embeddings-v4",
            "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
            "trust_remote_code": True,
            "embedding_dim": 768
        },
        "jinaai--jina-embeddings-v3": {
            "model_id": "jinaai/jina-embeddings-v3",
            "revision": None,
            "trust_remote_code": True,
            "embedding_dim": 1024
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
        }
    }