"""
Factory for creating appropriate GenAI interfaces based on configuration
"""

import logging
import os
from typing import Optional, Union
from pathlib import Path
from src.interfaces.embedding_interface import EmbeddingInterface
from src.interfaces.genai_interface import GenAIInterface
from src.interfaces.vllm_genai_interface_batch import VLLMGenAIInterfaceBatch
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
        backend_type = config.get('backed_type', 'none')
        
        if backend_type == 'openai':
            return ModelFactory._create_openai_interface(config['llm'][backend_type])
        elif backend_type == 'vllm':
            return ModelFactory._create_vllm_interface(config['llm'][backend_type])
        else:
            logger.warning(f"Unknown backend type: {backend_type}")
            return None
    
    @staticmethod
    def _create_openai_interface(config):
        """Create Azure OpenAI interface"""
        try:
            
            interface = GenAIInterface(
                endpoint=config.get('azure_endpoint', None),
                deployment=config.get('deployment_name', None),
                api_key=config.get('api_key', None),
                api_version=config.get('api_version', '2025-01-01-preview'),
                timeout=config.get('TIMEOUT', 60),
                max_tokens=config.get('max_tokens', 4000),
                temperature=config.get('temperature', 0.0)
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
            # Set CUDA_VISIBLE_DEVICES for vLLM (GPU 0)
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            interface = VLLMGenAIInterfaceBatch(
                model_name=config.get('model_name', 'meta-llama--Llama-3.1-8B-Instruct'),
                number_gpus=config.get('num_gpus', 1),
                max_model_len=config.get('max_model_len', 8192),
                batch_size=config.get('BATCH_SIZE', 8),
                model_cache_dir=config.get('model_cache_dir', '/root/.cache/huggingface/hub'),
                external_model_dir=config.get('external_model_dir', None),
                gpu_memory_utilization=config.get('gpu_memory_utilization', 0.85),
                gpu_id=0  # Using GPU 0
            )
            
            logger.info(f"Created vLLM batch interface with model: {config.MODEL_NAME}")
                
            del os.environ["CUDA_VISIBLE_DEVICES"]
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create vLLM interface: {e}")
            return None
    
    @staticmethod
    def create_embedding_interface(config):
        """
        Create embedding interface using merged configuration
        """
        try:
            
            # Use device from config or override
            device = "cuda:1" if config.get('backed_type', 'none') == 'vllm' else config.get('EMBEDDING_DEVICE', 'cuda')
            config = config['embedding']
            # Get embedding model from merged config
            embedding_model = config.get('model_name', 'jinaai--jina-embeddings-v4')
            batch_size = config.get('batch_size', 32)
            
            interface = EmbeddingInterface(
                model_name=embedding_model,
                model_cache_dir=config.get('model_cache_dir'),
                external_model_dir=config.get('external_model_dir'),
                device=device,
                batch_size=batch_size
            )
            
            logger.info(f"Created embedding interface: {embedding_model} on {device} (batch_size={batch_size})")
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create embedding interface: {e}")
            return None