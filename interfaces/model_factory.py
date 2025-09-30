"""
Factory for creating appropriate GenAI interfaces based on configuration
"""

import logging
import os
from typing import Optional, Union
from pathlib import Path

import torch

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating GenAI interfaces based on backend configuration"""
    
    @staticmethod
    def create_genai_interface(config):
        """
        Create appropriate GenAI interface based on configuration
        
        Args:
            config: SimpleConfig object with backend settings
            
        Returns:
            GenAI interface instance or None
        """
        backend_type = getattr(config, 'BACKEND_TYPE', 'none')
        
        if backend_type == 'openai':
            return ModelFactory._create_openai_interface(config)
        elif backend_type == 'vllm':
            return ModelFactory._create_vllm_interface(config)
        else:
            logger.warning(f"Unknown backend type: {backend_type}")
            return None
    
    @staticmethod
    def _create_openai_interface(config):
        """Create Azure OpenAI interface"""
        try:
            from interfaces.genai_interface import GenAIInterface
            
            interface = GenAIInterface(
                endpoint=getattr(config, 'ENDPOINT', None),
                deployment=getattr(config, 'DEPLOYMENT', None),
                api_key=getattr(config, 'API_KEY', None),
                api_version=getattr(config, 'API_VERSION', '2025-01-01-preview'),
                timeout=getattr(config, 'TIMEOUT', 60),
                max_tokens=getattr(config, 'MAX_TOKENS', 4000),
                temperature=getattr(config, 'TEMPERATURE', 0.0)
            )
            
            logger.info(f"Created Azure OpenAI interface with deployment: {config.DEPLOYMENT}")
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create OpenAI interface: {e}")
            return None
    
    @staticmethod
    def _create_vllm_interface(config):
        """Create vLLM interface"""
        try:
            # Determine if batch processing should be used
            from interfaces.vllm_genai_interface_batch import VLLMGenAIInterfaceBatch
            # Set CUDA_VISIBLE_DEVICES for vLLM (GPU 0)
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            interface = VLLMGenAIInterfaceBatch(
                model_name=getattr(config, 'MODEL_NAME', 'meta-llama--Llama-3.1-8B-Instruct'),
                number_gpus=getattr(config, 'NUM_GPUS', 1),
                max_model_len=getattr(config, 'MAX_MODEL_LEN', 8192),
                batch_size=getattr(config, 'BATCH_SIZE', 8),
                model_cache_dir=getattr(config, 'MODEL_CACHE_DIR', '/root/.cache/huggingface/hub'),
                external_model_dir=getattr(config, 'EXTERNAL_MODEL_DIR', None),
                gpu_id=0  # Using GPU 0
            )
            
            logger.info(f"Created vLLM batch interface with model: {config.MODEL_NAME}")
                
            del os.environ["CUDA_VISIBLE_DEVICES"]
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create vLLM interface: {e}")
            return None
    
    @staticmethod
    def create_embedding_interface(config, device_override: str = None):
        """
        Create embedding interface using merged configuration
        """
        try:
            from interfaces.embedding_interface import EmbeddingInterface
            
            # Use device from config or override
            device = "cuda:1" if getattr(config, 'BACKEND_TYPE', 'none') == 'vllm' else getattr(config, 'EMBEDDING_DEVICE', 'cuda')
            
            # Get embedding model from merged config
            embedding_model = getattr(config, 'EMBEDDING_MODEL', 'jinaai--jina-embeddings-v4')
            batch_size = getattr(config, 'EMBEDDING_BATCH_SIZE', 32)
            
            interface = EmbeddingInterface(
                model_name=embedding_model,
                model_cache_dir=getattr(config, 'MODEL_CACHE_DIR', '/root/.cache/huggingface/hub'),
                external_model_dir=getattr(config, 'EXTERNAL_MODEL_DIR', None),
                device=device,
                batch_size=batch_size
            )
            
            logger.info(f"Created embedding interface: {embedding_model} on {device} (batch_size={batch_size})")
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create embedding interface: {e}")
            return None
    
    @staticmethod
    def detect_available_backends():
        """Detect which backends are available"""
        available = []
        
        # Check OpenAI
        if os.getenv("AZURE_OPENAI_API_KEY"):
            try:
                from interfaces.genai_interface import GenAIInterface
                available.append("openai")
            except ImportError:
                pass
        
        # Check vLLM
        try:
            import vllm
            available.append("vllm")
        except ImportError:
            pass
        
        return available