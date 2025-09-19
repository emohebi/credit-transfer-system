"""
Configuration settings for the Credit Transfer Analysis System
"""

import os
from pathlib import Path


class Config:
    """System configuration"""
    
    # Project paths
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    CACHE_DIR = BASE_DIR / "cache"
    
    # Create directories if they don't exist
    for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
        dir_path.mkdir(exist_ok=True)
    
    # GenAI Configuration
    USE_VLLM = os.getenv("USE_VLLM", "true").lower() == "true"
    VLLM_MODEL_NAME = os.getenv("VLLM_MODEL_NAME", "meta-llama--Llama-3.1-8B-Instruct")
    VLLM_NUM_GPUS = int(os.getenv("VLLM_NUM_GPUS", "1"))
    VLLM_MAX_MODEL_LEN = int(os.getenv("VLLM_MAX_MODEL_LEN", "8192"))
    VLLM_BATCH_SIZE = int(os.getenv("VLLM_BATCH_SIZE", "8"))
    MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub")
    EXTERNAL_MODEL_DIR = os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models")
    
    # Legacy Web API Configuration (kept for compatibility)
    GENAI_ENDPOINT = os.getenv("GENAI_ENDPOINT", "http://localhost:8080")
    GENAI_API_KEY = os.getenv("GENAI_API_KEY", None)
    GENAI_TIMEOUT = int(os.getenv("GENAI_TIMEOUT", "30"))
    USE_GENAI = os.getenv("USE_GENAI", "false").lower() == "true"  # Default to false, use vLLM instead
    
    # Embedding Configuration
    EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "jinaai--jina-embeddings-v4")
    EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cuda")
    EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    
    # Legacy configurations (kept for compatibility)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_ENDPOINT = os.getenv("EMBEDDING_ENDPOINT", None)
    EMBEDDING_API_KEY = os.getenv("EMBEDDING_API_KEY", None)
    USE_EMBEDDING_API = os.getenv("USE_EMBEDDING_API", "false").lower() == "true"
    EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # Default for Jina v4
    
    # Analysis Configuration
    MIN_ALIGNMENT_SCORE = float(os.getenv("MIN_ALIGNMENT_SCORE", "0.5"))
    MAX_UNIT_COMBINATION = int(os.getenv("MAX_UNIT_COMBINATION", "3"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.8"))
    PARTIAL_THRESHOLD = float(os.getenv("PARTIAL_THRESHOLD", "0.6"))
    
    # Scoring Weights
    COVERAGE_WEIGHT = float(os.getenv("COVERAGE_WEIGHT", "0.4"))
    DEPTH_WEIGHT = float(os.getenv("DEPTH_WEIGHT", "0.2"))
    CONTEXT_WEIGHT = float(os.getenv("CONTEXT_WEIGHT", "0.2"))
    QUALITY_WEIGHT = float(os.getenv("QUALITY_WEIGHT", "0.1"))
    EDGE_PENALTY_WEIGHT = float(os.getenv("EDGE_PENALTY_WEIGHT", "0.1"))
    
    # Edge Case Thresholds
    CONTEXT_IMBALANCE_THRESHOLD = float(os.getenv("CONTEXT_IMBALANCE_THRESHOLD", "0.3"))
    DEPTH_ADEQUACY_THRESHOLD = float(os.getenv("DEPTH_ADEQUACY_THRESHOLD", "0.8"))
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
    
    # Expected skill levels for each study level
    STUDY_LEVEL_SKILL_MAPPING = {
        "introductory": "NOVICE",
        "intermediate": "COMPETENT",
        "advanced": "PROFICIENT",
        "specialized": "EXPERT",
        "postgraduate": "EXPERT"
    }
    
    # Expected cognitive depth for each study level
    STUDY_LEVEL_DEPTH_MAPPING = {
        "introductory": "UNDERSTAND",
        "intermediate": "APPLY",
        "advanced": "ANALYZE",
        "specialized": "EVALUATE",
        "postgraduate": "CREATE"
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
    REPORT_FORMAT = os.getenv("REPORT_FORMAT", "json")  # json, csv, html
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
            "weights": {
                "coverage": cls.COVERAGE_WEIGHT,
                "depth": cls.DEPTH_WEIGHT,
                "context": cls.CONTEXT_WEIGHT,
                "quality": cls.QUALITY_WEIGHT,
                "edge_penalty": cls.EDGE_PENALTY_WEIGHT
            },
            "thresholds": {
                "context_imbalance": cls.CONTEXT_IMBALANCE_THRESHOLD,
                "depth_adequacy": cls.DEPTH_ADEQUACY_THRESHOLD,
                "breadth_ratio_min": cls.BREADTH_RATIO_MIN,
                "breadth_ratio_max": cls.BREADTH_RATIO_MAX
            }
        }
    
    @classmethod
    def save_config(cls, filepath: str = None):
        """Save configuration to file"""
        import json
        
        if filepath is None:
            filepath = cls.OUTPUT_DIR / "config.json"
        
        with open(filepath, 'w') as f:
            json.dump(cls.get_config_dict(), f, indent=2)
    
    @classmethod
    def load_config(cls, filepath: str):
        """Load configuration from file"""
        import json
        
        with open(filepath, 'r') as f:
            config = json.load(f)
        
        # Update class attributes
        for key, value in config.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)