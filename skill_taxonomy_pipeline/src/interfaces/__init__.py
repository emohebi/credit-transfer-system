"""
Interfaces module - GenAI, Embedding, and Model Factory interfaces

Provides:
- GenAIInterface: Azure OpenAI integration
- VLLMGenAIInterface: Local vLLM model integration
- EmbeddingInterface: Local embedding model with multi-GPU support
- ModelFactory: Factory for creating appropriate interfaces
"""

from .genai_interface import GenAIInterface
from .vllm_interface import VLLMGenAIInterface, VLLMGenAIInterfaceBatch
from .embedding_interface import EmbeddingInterface
from .model_factory import (
    ModelFactory,
    create_genai_interface,
    create_embedding_interface
)

__all__ = [
    # GenAI interfaces
    'GenAIInterface',
    'VLLMGenAIInterface',
    'VLLMGenAIInterfaceBatch',  # Backward compatibility alias
    
    # Embedding interface
    'EmbeddingInterface',
    
    # Factory
    'ModelFactory',
    'create_genai_interface',
    'create_embedding_interface',
]
