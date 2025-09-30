"""
Simplified configuration profiles with model backend and embedding selection
"""

from pathlib import Path
from typing import Dict, Any
import os

class ConfigProfiles:
    """Pre-defined configuration profiles for different use cases"""
    
    PROFILES = {
        "fast": {
            "name": "Fast Analysis",
            "description": "Quick analysis with basic skill matching",
            "use_batch": True,
            "batch_size": 16,
            "use_cache": True,
            "cache_ttl_days": 30,
            "edge_cases_enabled": False,
            "max_skills_per_unit": 50,
            "min_confidence": 0.5,
            "use_clustering": True,
            "clustering_threshold": 0.7,
            "ai_calls": "minimal",
            "embedding_only_matching": True,
            "progressive_depth": "quick",
            "default_backend": "vllm",
            "default_embedding": "jina",  # Faster, smaller model
            "semantic_weight": 0.8,
            "level_weight": 0.2,
            "study_level_importance": 0.6,
            "embedding_device": "cuda"  # Force CPU for dev
        },
        "balanced": {
            "name": "Balanced Analysis",
            "description": "Good balance between speed and accuracy",
            "use_batch": True,
            "batch_size": 8,
            "use_cache": True,
            "cache_ttl_days": 7,
            "edge_cases_enabled": True,
            "edge_cases": ["content_alignment", "structural_alignment"],
            "max_skills_per_unit": 100,
            "min_confidence": 0.6,
            "use_clustering": True,
            "clustering_threshold": 0.75,
            "ai_calls": "moderate",
            "embedding_only_matching": False,
            "progressive_depth": "balanced",
            "default_backend": "auto",
            "default_embedding": "jina",  # Better quality
            "semantic_weight": 0.7,
            "level_weight": 0.3,
            "study_level_importance": 0.8,
            "embedding_device": "cuda"  # Force CPU for dev
        },
        "thorough": {
            "name": "Thorough Analysis",
            "description": "Comprehensive analysis with all features",
            "use_batch": True,
            "batch_size": 4,
            "use_cache": False,
            "edge_cases_enabled": True,
            "edge_cases": ["all"],
            "max_skills_per_unit": None,
            "min_confidence": 0.7,
            "use_clustering": True,
            "clustering_threshold": 0.8,
            "ai_calls": "comprehensive",
            "embedding_only_matching": False,
            "progressive_depth": "deep",
            "default_backend": "openai",
            "default_embedding": "jina",  # Best quality
            "semantic_weight": 0.6,
            "level_weight": 0.4,
            "study_level_importance": 1.0,
            "embedding_device": "cuda"  # Force CPU for dev
        },
        "dev": {
            "name": "Development Mode",
            "description": "For testing and development",
            "use_batch": False,
            "batch_size": 1,
            "use_cache": False,
            "edge_cases_enabled": True,
            "edge_cases": ["all"],
            "max_skills_per_unit": 10,
            "min_confidence": 0.0,
            "use_clustering": False,
            "ai_calls": "comprehensive",
            "embedding_only_matching": False,
            "progressive_depth": "deep",
            "debug": True,
            "default_backend": "openai",
            "default_embedding": "jina",  # Fast for testing
            "semantic_weight": 0.7,
            "level_weight": 0.3,
            "study_level_importance": 0.8,
            "embedding_device": "cuda"  # Force CPU for dev
        },
        "robust": {
            "name": "Robust Analysis",
            "description": "Consistent results with ensemble extraction",
            "use_batch": False,  # Process one at a time for consistency
            "batch_size": 1,
            "use_cache": False,  # Disable caching
            "cache_ttl_days": 0,  # No cache
            "edge_cases_enabled": True,
            "max_skills_per_unit": 100,
            "min_confidence": 0.7,
            "use_clustering": True,
            "clustering_threshold": 0.75,  # Fixed threshold
            "ai_calls": "moderate",
            "embedding_only_matching": False,
            "progressive_depth": "balanced",
            "default_backend": "vllm",
            "default_embedding": "jina",
            "semantic_weight": 0.7,
            "level_weight": 0.3,
            "study_level_importance": 0.8,
            "embedding_device": "cuda",
            "ensemble_runs": 3,  # Use ensemble extraction
            "temperature": 0.0,  # Deterministic
            "top_p": 1.0,  # No sampling
            "seed": 42,  # Fixed seed
            "ensemble_similarity_threshold": 0.98,
            "matching_strategy": "direct",  # Options: "clustering", "direct", "hybrid"
            "direct_match_threshold": 0.85,  # Threshold for direct skill name matching
            "context_weight": 0.15,  # Weight for context similarity
            "partial_threshold": 0.5,  # Threshold for partial matches
            "enable_bidirectional_coverage": True,  # Use bidirectional coverage
            "enable_one_to_many": True,  # Support one-to-many skill mappings
            "enable_clustering_validation": True,  # Validate direct matches with clustering
            "pre_filter_categories": True  # Pre-filter by categories for performance
        }
    }
    
    # Model backend configurations
    MODEL_BACKENDS = {
        "openai": {
            "type": "openai",
            "endpoint": os.getenv("ENDPOINT_URL", "https://ehsaninstance1.openai.azure.com/"),
            "deployment": os.getenv("DEPLOYMENT_NAME", "gpt-4o"),
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
            "timeout": 60,
            "max_tokens": 4000,
            "temperature": 0.0,
            "rate_limit_delay": 1.0
        },
        "vllm": {
            "type": "vllm",
            "model_name": os.getenv("VLLM_MODEL_NAME", "meta-llama--Llama-3.1-8B-Instruct"),
            "num_gpus": int(os.getenv("VLLM_NUM_GPUS", "1")),
            "max_model_len": int(os.getenv("VLLM_MAX_MODEL_LEN", "8192")),
            "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
            "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
            "tensor_parallel_size": 1,
            "gpu_memory_utilization": 0.9
        }
    }
    
    # Embedding configurations
    EMBEDDING_CONFIGS = {
        "jina": {
            "embedding_model": "jinaai--jina-embeddings-v4",
            "embedding_dim": 768,
            "embedding_batch_size": 32,
            "trust_remote_code": True
        },
        "minilm": {
            "embedding_model": "sentence-transformers--all-MiniLM-L6-v2",
            "embedding_dim": 384,
            "embedding_batch_size": 64,
            "trust_remote_code": False
        },
        "bge": {
            "embedding_model": "BAAI--bge-large-en-v1.5",
            "embedding_dim": 1024,
            "embedding_batch_size": 24,
            "trust_remote_code": False
        },
        "e5": {
            "embedding_model": "intfloat--e5-large-v2",
            "embedding_dim": 1024,
            "embedding_batch_size": 24,
            "trust_remote_code": False
        }
    }
    
    @classmethod
    def get_profile(cls, profile_name: str = "balanced") -> Dict[str, Any]:
        """Get a configuration profile by name"""
        return cls.PROFILES.get(profile_name, cls.PROFILES["balanced"])
    
    @classmethod
    def get_model_config(cls, backend: str = "auto") -> Dict[str, Any]:
        """Get model configuration for specified backend"""
        if backend == "auto":
            # Try OpenAI first if API key is available
            if os.getenv("AZURE_OPENAI_API_KEY"):
                return cls.MODEL_BACKENDS["openai"]
            # Fall back to vLLM
            return cls.MODEL_BACKENDS["vllm"]
        
        return cls.MODEL_BACKENDS.get(backend, cls.MODEL_BACKENDS["vllm"])
    
    @classmethod
    def get_embedding_config(cls, embedding_name: str = "jina", device: str = None) -> Dict[str, Any]:
        """
        Get embedding configuration
        
        Args:
            embedding_name: Name of embedding model configuration
            device: Override device selection
        """
        base_config = cls.EMBEDDING_CONFIGS.get(embedding_name, cls.EMBEDDING_CONFIGS["jina"])
        
        # Add device configuration
        device = base_config.get("embedding_device", device)
        if device:
            base_config["embedding_device"] = device
        else:
            # Auto-detect device
            try:
                import torch
                if torch.cuda.is_available():
                    # Use second GPU for embeddings if available when using vLLM
                    device_count = torch.cuda.device_count()
                    base_config["embedding_device"] = "cuda:1" if device_count > 1 else "cuda:0"
                else:
                    base_config["embedding_device"] = "cpu"
            except ImportError:
                base_config["embedding_device"] = "cpu"
        
        # Add cache directories
        base_config["model_cache_dir"] = os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub")
        base_config["external_model_dir"] = os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models")
        
        return base_config
    
    @classmethod
    def create_config(cls, 
                     profile_name: str = "balanced", 
                     backend: str = None,
                     embedding: str = None,
                     overrides: Dict = None) -> 'SimpleConfig':
        """
        Create a SimpleConfig instance from profile with model and embedding backend
        
        Args:
            profile_name: Name of the profile to use
            backend: Override backend selection ('openai', 'vllm', or 'auto')
            embedding: Override embedding model selection
            overrides: Additional configuration overrides
        """
        # Get base profile
        profile = cls.get_profile(profile_name)
        
        # Determine backend
        if backend is None:
            backend = profile.get("default_backend", "auto")
        
        # Determine embedding
        if embedding is None:
            embedding = profile.get("default_embedding", "jina")
        
        # Get configurations
        model_config = cls.get_model_config(backend)
        embedding_config = cls.get_embedding_config(embedding, device=profile.get("embedding_device", None))
        
        # MERGE ALL CONFIGURATIONS
        config_dict = {
            **profile,           # Base profile settings
            **model_config,      # Model backend settings
            **embedding_config   # Embedding settings
        }
        
        # Apply any overrides
        if overrides:
            config_dict.update(overrides)
        
        return SimpleConfig(config_dict)
    
    @classmethod
    def list_available_options(cls) -> Dict[str, Any]:
        """List all available configuration options"""
        return {
            "profiles": list(cls.PROFILES.keys()),
            "backends": list(cls.MODEL_BACKENDS.keys()),
            "embeddings": list(cls.EMBEDDING_CONFIGS.keys())
        }


class SimpleConfig:
    """Simplified configuration class with merged settings"""
    
    def __init__(self, profile: Dict[str, Any]):
        # Apply ALL settings from merged configuration
        for key, value in profile.items():
            setattr(self, key.upper(), value)
        
        # Set up paths
        self.BASE_DIR = Path(__file__).parent
        self.DATA_DIR = self.BASE_DIR / "data"
        self.OUTPUT_DIR = self.BASE_DIR / "output"
        self.CACHE_DIR = self.BASE_DIR / "cache"
        
        # Create directories
        for dir_path in [self.DATA_DIR, self.OUTPUT_DIR, self.CACHE_DIR]:
            dir_path.mkdir(exist_ok=True)
        
        # Simple scoring weights
        self.WEIGHTS = {
            "skill_match": 0.7,
            "confidence": 0.3
        }
        
        # Simplified thresholds
        self.THRESHOLDS = {
            "full_transfer": 0.8,
            "partial_transfer": 0.5,
            "minimum_viable": 0.3
        }
        
        # Store backend types for easy checking
        self.BACKEND_TYPE = self.TYPE if hasattr(self, 'TYPE') else 'unknown'
        self.IS_OPENAI = self.BACKEND_TYPE == 'openai'
        self.IS_VLLM = self.BACKEND_TYPE == 'vllm'
        
        # Store embedding info
        self.EMBEDDING_MODEL_NAME = getattr(self, 'EMBEDDING_MODEL', 'unknown')
        self.EMBEDDING_DEVICE = getattr(self, 'EMBEDDING_DEVICE', 'cpu')
    
    def to_dict(self) -> Dict:
        """Export configuration as dictionary"""
        return {k: v for k, v in self.__dict__.items() 
                if not k.startswith('_') and not callable(v)}
    
    def get_model_info(self) -> str:
        """Get human-readable model information"""
        if self.IS_OPENAI:
            return f"Azure OpenAI ({getattr(self, 'DEPLOYMENT', 'unknown')})"
        elif self.IS_VLLM:
            return f"vLLM ({getattr(self, 'MODEL_NAME', 'unknown')})"
        else:
            return "No AI backend"
    
    def get_embedding_info(self) -> str:
        """Get human-readable embedding information"""
        return f"{self.EMBEDDING_MODEL_NAME} on {self.EMBEDDING_DEVICE}"
    
    def print_config(self):
        """Print current configuration"""
        print("=" * 60)
        print("CURRENT CONFIGURATION")
        print("=" * 60)
        print(f"Profile: {getattr(self, 'NAME', 'Unknown')}")
        print(f"Backend: {self.get_model_info()}")
        print(f"Embedding: {self.get_embedding_info()}")
        print(f"Batch Size: {getattr(self, 'BATCH_SIZE', 'N/A')}")
        print(f"Cache Enabled: {getattr(self, 'USE_CACHE', False)}")
        print(f"Clustering Threshold: {getattr(self, 'CLUSTERING_THRESHOLD', 'N/A')}")
        print(f"Semantic Weight: {getattr(self, 'SEMANTIC_WEIGHT', 'N/A')}")
        print(f"Level Weight: {getattr(self, 'LEVEL_WEIGHT', 'N/A')}")
        print("=" * 60)