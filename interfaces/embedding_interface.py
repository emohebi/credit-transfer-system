"""
Interface for local embedding model integration with multi-GPU support
"""

import logging
import numpy as np
import torch
from typing import List, Optional, Union, Dict
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download
from config import Config

logger = logging.getLogger(__name__)

# Import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.error("sentence-transformers not installed. Please install it for embedding support.")


class EmbeddingInterface:
    """Interface for local embedding model with multi-GPU support"""
    
    def __init__(self, 
                 model_name: str = "jinaai--jina-embeddings-v4",
                 model_cache_dir: str = "/home/ehsan/.cache/huggingface/hub",
                 external_model_dir: str = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models",
                 device: str = "cuda",
                 batch_size: int = 32):
        """
        Initialize embedding interface with local model
        
        Args:
            model_name: Name of the model to use from MODELS dict
            model_cache_dir: Directory for HuggingFace cache
            external_model_dir: Directory containing pre-downloaded models
            device: Device to run model on (cuda, cuda:0, cuda:1, cpu)
            batch_size: Default batch size for encoding
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required for embeddings. Install with: pip install sentence-transformers")
        
        self.MODELS = Config.EMBEDDING_MODELS
        self.model_name = model_name
        self.model_cache_dir = Path(model_cache_dir)
        self.external_model_dir = Path(external_model_dir)
        self.device_str = device
        self.default_batch_size = batch_size
        
        # Parse device string to handle specific GPU selection
        if device.startswith("cuda"):
            if ":" in device:
                # Specific GPU like cuda:1
                self.device_id = int(device.split(":")[1])
            else:
                # Default to cuda:0
                self.device_id = 0
            # Set CUDA device for this model
            torch.cuda.set_device(self.device_id)
            self.device = torch.device(f"cuda:{self.device_id}")
        else:
            self.device_id = None
            self.device = torch.device("cpu")
        
        logger.info(f"Embedding interface will use device: {self.device}")
        
        # Get model configuration
        if model_name not in self.MODELS:
            logger.warning(f"Unknown model: {model_name}. Using default configuration.")
            self.model_config = {
                "model_id": model_name,
                "revision": None,
                "trust_remote_code": True,
                "embedding_dim": 768
            }
        else:
            self.model_config = self.MODELS[model_name]
        
        self.embedding_dim = self.model_config.get("embedding_dim", 768)
        self.trust_remote_code = self.model_config.get("trust_remote_code", False)
        
        # Initialize the model
        self.model = None
        self._initialize_model()
        
        # Initialize cache
        self.cache = {}
        
    def _initialize_model(self):
        """Initialize the SentenceTransformer model with proper device handling"""
        try:
            snapshot_location = self._get_snapshot_location()
            logger.info(f"Loading embedding model from: {snapshot_location}")
            
            # Create a context manager to ensure model loads on correct device
            with torch.cuda.device(self.device_id) if self.device_id is not None else torch.cuda.device(0):
                # Initialize model - do NOT pass device parameter to avoid conflicts
                self.model = SentenceTransformer(
                    snapshot_location,
                    trust_remote_code=self.trust_remote_code,
                    device=self.device
                )
                
                # Manually move model to the correct device
                self.model = self.model.to(self.device)
                
                # Set the device in the model's internal state
                self.model._target_device = self.device
                
                # Ensure all sub-modules are on the correct device
                for module in self.model.modules():
                    module.to(self.device)
                
                # If model has tokenizer, ensure it's configured correctly
                if hasattr(self.model, 'tokenizer'):
                    # Some tokenizers have device-specific settings
                    if hasattr(self.model.tokenizer, 'padding_side'):
                        self.model.tokenizer.padding_side = 'right'
            
            # Update embedding dimension from model
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Successfully loaded embedding model: {self.model_name} on {self.device} (dim={self.embedding_dim})")
            
            # Verify device placement
            self._verify_device_placement()
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def _verify_device_placement(self):
        """Verify all model parameters are on the correct device"""
        for name, param in self.model.named_parameters():
            if param.device != self.device:
                logger.warning(f"Parameter {name} is on {param.device}, moving to {self.device}")
                param.data = param.data.to(self.device)
        
        # Check buffers as well
        for name, buffer in self.model.named_buffers():
            if buffer.device != self.device:
                logger.warning(f"Buffer {name} is on {buffer.device}, moving to {self.device}")
                buffer.data = buffer.data.to(self.device)
    
    def _get_snapshot_location(self, copy_model: bool = True) -> str:
        """Get or download model snapshot location"""
        model_id = self.model_config['model_id']
        revision = self.model_config.get('revision')
        
        if revision:
            external_path = self.external_model_dir / f"models--{self.model_name}"
            cache_path = self.model_cache_dir / f"models--{self.model_name}"
            
            if copy_model and external_path.exists():
                try:
                    shutil.copytree(str(external_path), str(cache_path))
                    logger.info(f"Copied model from {external_path} to {cache_path}")
                except FileExistsError:
                    logger.info(f"Model already exists in cache: {cache_path}")
            
            snapshot_location = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(self.model_cache_dir)
            )
        else:
            if copy_model:
                external_path = self.external_model_dir / self.model_name
                cache_path = self.model_cache_dir / self.model_name
                
                if external_path.exists():
                    try:
                        shutil.copytree(str(external_path), str(cache_path))
                        logger.info(f"Copied model from {external_path} to {cache_path}")
                    except FileExistsError:
                        logger.info(f"Model already exists in cache: {cache_path}")
                    
                    snapshot_location = str(cache_path)
                else:
                    snapshot_location = snapshot_download(
                        repo_id=model_id,
                        cache_dir=str(self.model_cache_dir)
                    )
            else:
                cache_path = self.model_cache_dir / self.model_name
                if cache_path.exists():
                    snapshot_location = str(cache_path)
                else:
                    snapshot_location = snapshot_download(
                        repo_id=model_id,
                        cache_dir=str(self.model_cache_dir)
                    )
        
        return snapshot_location
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: Optional[int] = None,
               show_progress: bool = False,
               convert_to_tensor: bool = False,
               normalize_embeddings: bool = True) -> np.ndarray:
        """
        Generate embeddings for texts with proper device handling
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            convert_to_tensor: Return PyTorch tensor instead of numpy
            normalize_embeddings: Whether to normalize embeddings
            
        Returns:
            Numpy array of embeddings (or tensor if convert_to_tensor=True)
        """
        # Handle single text input
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        # Use cache for single texts
        if len(texts) == 1 and texts[0] in self.cache and not convert_to_tensor:
            return self.cache[texts[0]]
        
        # Set batch size
        if batch_size is None:
            batch_size = self.default_batch_size
        
        # Ensure we're in the right CUDA context
        with torch.cuda.device(self.device_id) if self.device_id is not None else torch.cuda.device(0):
            # Double-check model is on correct device
            self.model._target_device = self.device
            
            # Use a custom encoding approach to ensure device consistency
            try:
                # For Jina models with task parameter
                embeddings = self.model.encode(
                    texts,
                    task='text-matching',
                    prompt_name='passage',
                    batch_size=batch_size,
                    show_progress_bar=show_progress,
                    convert_to_tensor=convert_to_tensor,
                    normalize_embeddings=normalize_embeddings
                )
                    
            except Exception as e:
                logger.warning(f"Custom encoding failed: {e}. Falling back to standard encode with device.")
                # Fallback to standard encode
                embeddings = self.model.encode(
                    texts,
                    task='text-matching',
                    prompt_name='passage',
                    batch_size=batch_size,
                    show_progress_bar=show_progress,
                    convert_to_tensor=convert_to_tensor,
                    normalize_embeddings=normalize_embeddings,
                    device=self.device
                )
        
        # Cache single text results
        if len(texts) == 1 and not convert_to_tensor:
            if isinstance(embeddings, np.ndarray):
                self.cache[texts[0]] = embeddings[0] if embeddings.ndim > 1 else embeddings
        
        return embeddings
    
    def encode_batch(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Encode multiple texts in batches (convenience method)
        """
        return self.encode(texts, batch_size=batch_size)
    
    def similarity(self, embeddings1: np.ndarray, 
                  embeddings2: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between embeddings
        """
        # Handle single embedding
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        # Use numpy operations to avoid device issues
        # Normalize embeddings
        norm1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-10)
        norm2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-10)
        
        # Calculate cosine similarity
        similarity_matrix = np.dot(norm1, norm2.T)
        
        return similarity_matrix
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity score between two texts"""
        embeddings = self.encode([text1, text2])
        sim_matrix = self.similarity(embeddings[0:1], embeddings[1:2])
        return float(sim_matrix[0, 0])
    
    def find_most_similar(self, query: str, 
                         candidates: List[str], 
                         top_k: int = 5) -> List[tuple]:
        """Find most similar texts from candidates"""
        if not candidates:
            return []
        
        all_texts = [query] + candidates
        embeddings = self.encode(all_texts)
        
        query_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]
        
        similarities = self.similarity(query_embedding, candidate_embeddings)
        scores = similarities[0]
        
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = [(candidates[idx], float(scores[idx])) for idx in top_indices]
        return results
    
    def save_embeddings(self, embeddings: np.ndarray, 
                       texts: List[str], 
                       filepath: str):
        """Save embeddings to file"""
        import json
        
        if torch.is_tensor(embeddings):
            embeddings = embeddings.cpu().numpy()
        
        data = {
            "embeddings": embeddings.tolist(),
            "texts": texts,
            "model": self.model_name,
            "dimension": self.embedding_dim,
            "device": self.device_str
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        logger.info(f"Saved {len(texts)} embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str) -> tuple:
        """Load embeddings from file"""
        import json
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        embeddings = np.array(data["embeddings"])
        texts = data["texts"]
        
        logger.info(f"Loaded {len(texts)} embeddings from {filepath}")
        return embeddings, texts
    
    def clear_cache(self):
        """Clear the embedding cache"""
        self.cache.clear()
        logger.info("Embedding cache cleared")