"""
Factory for creating GenAI and Embedding interfaces based on configuration
Supports Azure OpenAI and vLLM backends
"""

import logging
import os
from typing import Optional, Dict, Any, Union

logger = logging.getLogger(__name__)


class ModelFactory:
    """Factory for creating model interfaces based on configuration"""
    
    # Backend type constants
    BACKEND_OPENAI = 'openai'
    BACKEND_AZURE_OPENAI = 'azure_openai'
    BACKEND_VLLM = 'vllm'
    
    @classmethod
    def create_genai_interface(cls, config: Dict[str, Any], backend_type: Optional[str] = None):
        """
        Create appropriate GenAI interface based on configuration
        
        Args:
            config: Configuration dictionary with 'llm' and 'backed_type' keys
            backend_type: Override backend type
            
        Returns:
            GenAI interface instance or None
        """
        # Determine backend type
        if backend_type is None:
            backend_type = config.get('backed_type', 'none')
        
        backend_type = backend_type.lower().replace('-', '_')
        logger.info(f"Creating GenAI interface for backend: {backend_type}")
        
        # Get LLM config
        llm_config = config.get('llm', {})
        
        # Get backend-specific config
        if backend_type in llm_config:
            backend_config = llm_config[backend_type]
        elif 'openai' in llm_config and backend_type in ['azure_openai', 'openai']:
            backend_config = llm_config['openai']
        else:
            backend_config = llm_config
        
        # Create appropriate interface
        if backend_type in [cls.BACKEND_OPENAI, cls.BACKEND_AZURE_OPENAI]:
            return cls._create_openai_interface(backend_config)
        elif backend_type == cls.BACKEND_VLLM:
            return cls._create_vllm_interface(backend_config)
        else:
            logger.warning(f"Unknown backend type: {backend_type}")
            return None
    
    @classmethod
    def _create_openai_interface(cls, config: Dict[str, Any]):
        """Create Azure OpenAI interface"""
        try:
            from src.interfaces.genai_interface import GenAIInterface
            
            interface = GenAIInterface(
                endpoint=config.get('azure_endpoint') or config.get('endpoint'),
                deployment=config.get('deployment_name') or config.get('deployment'),
                api_key=config.get('api_key'),
                api_version=config.get('api_version', '2025-01-01-preview'),
                timeout=config.get('timeout', 60),
                max_tokens=config.get('max_tokens', 4000),
                temperature=config.get('temperature', 0.0)
            )
            
            if interface.is_available():
                logger.info(f"✓ Created Azure OpenAI interface: {interface.deployment}")
                return interface
            else:
                logger.warning("Azure OpenAI interface not properly configured")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create OpenAI interface: {e}")
            return None
    
    @classmethod
    def _create_vllm_interface(cls, config: Dict[str, Any]):
        """Create vLLM interface"""
        try:
            from src.interfaces.vllm_interface import VLLMGenAIInterface
            # Set CUDA_VISIBLE_DEVICES for vLLM (GPU 0)
            os.environ["CUDA_VISIBLE_DEVICES"] = "0"
            # Determine template from model name
            model_name = config.get('model_name', '')
            
            interface = VLLMGenAIInterface(
                model_name=model_name,
                number_gpus=config.get('num_gpus', 1),
                gpu_id=config.get('gpu_id', 0),
                max_model_len=config.get('max_model_len', 8192),
                batch_size=config.get('batch_size', 8),
                gpu_memory_utilization=config.get('gpu_memory_utilization', 0.85),
                model_cache_dir=config.get('model_cache_dir'),
                external_model_dir=config.get('external_model_dir')
            )
            
            logger.info(f"Created vLLM interface: {model_name}")
            del os.environ["CUDA_VISIBLE_DEVICES"]
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create vLLM interface: {e}")
            return None
    
    @classmethod
    def create_embedding_interface(cls, config: Dict[str, Any]):
        """
        Create embedding interface
        
        Args:
            config: Configuration dictionary with 'embedding' key
            
        Returns:
            Embedding interface instance or None
        """
        try:
            from src.interfaces.embedding_interface import EmbeddingInterface
            
            emb_config = config.get('embedding', {})
            
            # Determine device based on backend
            backend_type = config.get('backed_type', 'openai')
            if backend_type == 'vllm':
                # Use different GPU for embeddings when vLLM is using GPU 0
                default_device = "cuda:1"
            else:
                default_device = emb_config.get('device', 'cuda')
            
            interface = EmbeddingInterface(
                model_name=emb_config.get('model_name', 'sentence-transformers/all-MiniLM-L6-v2'),
                device=emb_config.get('device', default_device),
                batch_size=emb_config.get('batch_size', 32),
                model_cache_dir=emb_config.get('model_cache_dir'),
                external_model_dir=emb_config.get('external_model_dir')
            )
            
            logger.info(f"Created embedding interface: {interface.model_name}")
            return interface
            
        except Exception as e:
            logger.error(f"Failed to create embedding interface: {e}")
            return None
    
    @classmethod
    def get_available_backends(cls) -> list:
        """Get list of supported backend types"""
        return [cls.BACKEND_OPENAI, cls.BACKEND_AZURE_OPENAI, cls.BACKEND_VLLM]
    
    @classmethod
    def validate_config(cls, config: Dict[str, Any], backend_type: str) -> Dict[str, Any]:
        """
        Validate configuration for a backend
        
        Returns:
            Dictionary with 'valid' bool and 'issues' list
        """
        issues = []
        backend_type = backend_type.lower().replace('-', '_')
        
        llm_config = config.get('llm', {})
        backend_config = llm_config.get(backend_type, llm_config)
        
        if backend_type in [cls.BACKEND_OPENAI, cls.BACKEND_AZURE_OPENAI]:
            if not backend_config.get('api_key'):
                issues.append("Missing api_key")
            if not (backend_config.get('endpoint') or backend_config.get('azure_endpoint')):
                issues.append("Missing endpoint/azure_endpoint")
            if not (backend_config.get('deployment_name') or backend_config.get('deployment')):
                issues.append("Missing deployment_name/deployment")
        
        elif backend_type == cls.BACKEND_VLLM:
            if not backend_config.get('model_name'):
                issues.append("Missing model_name")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }


# Convenience function
def create_genai_interface(config: Dict[str, Any], backend_type: Optional[str] = None):
    """Convenience function to create GenAI interface"""
    return ModelFactory.create_genai_interface(config, backend_type)


def create_embedding_interface(config: Dict[str, Any]):
    """Convenience function to create embedding interface"""
    return ModelFactory.create_embedding_interface(config)
