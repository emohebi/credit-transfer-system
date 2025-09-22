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
        self.device = device
        self.default_batch_size = batch_size
        
        # Parse device string to handle specific GPU selection
        if device.startswith("cuda"):
            if ":" in device:
                # Specific GPU like cuda:1
                self.device_id = int(device.split(":")[1])
                self.torch_device = torch.device(f"cuda:{self.device_id}")
            else:
                # Default to cuda:0
                self.device_id = 0
                self.torch_device = torch.device("cuda:0")
        else:
            self.device_id = None
            self.torch_device = torch.device("cpu")
        
        logger.info(f"Embedding interface will use device: {self.torch_device}")
        
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
            
            # Initialize model with specific device
            self.model = SentenceTransformer(
                snapshot_location,
                trust_remote_code=self.trust_remote_code,
                device=str(self.torch_device)  # Pass device as string
            )
            
            # Ensure model is on the correct device
            self.model = self.model.to(self.torch_device)
            
            # Update embedding dimension from model
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Successfully loaded embedding model: {self.model_name} on {self.torch_device} (dim={self.embedding_dim})")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            raise
    
    def _get_snapshot_location(self, copy_model: bool = True) -> str:
        """Get or download model snapshot location (same logic as vLLM interface)"""
        model_id = self.model_config['model_id']
        revision = self.model_config.get('revision')
        
        if revision:
            # Copy from external storage if available
            external_path = self.external_model_dir / f"models--{self.model_name}"
            cache_path = self.model_cache_dir / f"models--{self.model_name}"
            
            if copy_model and external_path.exists():
                try:
                    shutil.copytree(str(external_path), str(cache_path))
                    logger.info(f"Copied model from {external_path} to {cache_path}")
                except FileExistsError:
                    logger.info(f"Model already exists in cache: {cache_path}")
            
            # Download from HuggingFace
            snapshot_location = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(self.model_cache_dir)
            )
        else:
            # Check for local model in external directory first
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
                    # Download from HuggingFace if not in external directory
                    snapshot_location = snapshot_download(
                        repo_id=model_id,
                        cache_dir=str(self.model_cache_dir)
                    )
            else:
                # Try to use from cache or download
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
        if len(texts) == 1 and texts[0] in self.cache:
            cached = self.cache[texts[0]]
            if convert_to_tensor:
                return torch.from_numpy(cached).to(self.torch_device)
            return cached
        
        # Set batch size
        if batch_size is None:
            batch_size = self.default_batch_size
        
        # Ensure model is on correct device before encoding
        if hasattr(self.model, '_target_device'):
            self.model._target_device = self.torch_device
        
        # Encode using SentenceTransformer
        task = "text-matching"
        try:
            # The encode method should handle device placement automatically
            embeddings = self.model.encode(
                texts,
                task=task,
                prompt_name='passage',
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_tensor=convert_to_tensor,
                normalize_embeddings=normalize_embeddings,
                device=str(self.torch_device)  # Explicitly pass device
            )
        except Exception as e:
            logger.warning(f"Encoding with device parameter failed: {e}. Trying without explicit device.")
            # Fallback without device parameter (for older versions)
            embeddings = self.model.encode(
                texts,
                task=task,
                prompt_name='passage',
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_tensor=convert_to_tensor,
                normalize_embeddings=normalize_embeddings
            )
        
        # If tensor, ensure it's on the correct device
        if convert_to_tensor and torch.is_tensor(embeddings):
            embeddings = embeddings.to(self.torch_device)
        
        # Cache single text results
        if len(texts) == 1 and not convert_to_tensor:
            self.cache[texts[0]] = embeddings[0] if embeddings.ndim > 1 else embeddings
        
        return embeddings
    
    def encode_batch(self, texts: List[str], batch_size: Optional[int] = None) -> np.ndarray:
        """
        Encode multiple texts in batches (convenience method)
        
        Args:
            texts: List of texts to encode
            batch_size: Batch size for processing
            
        Returns:
            Numpy array of embeddings
        """
        return self.encode(texts, batch_size=batch_size)
    
    def similarity(self, embeddings1: np.ndarray, 
                  embeddings2: np.ndarray) -> np.ndarray:
        """
        Calculate cosine similarity between embeddings
        
        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            
        Returns:
            Similarity matrix
        """
        # Handle single embedding
        if embeddings1.ndim == 1:
            embeddings1 = embeddings1.reshape(1, -1)
        if embeddings2.ndim == 1:
            embeddings2 = embeddings2.reshape(1, -1)
        
        # Convert to tensors if needed and move to correct device
        if not torch.is_tensor(embeddings1):
            embeddings1_tensor = torch.from_numpy(embeddings1).to(self.torch_device)
        else:
            embeddings1_tensor = embeddings1.to(self.torch_device)
        
        if not torch.is_tensor(embeddings2):
            embeddings2_tensor = torch.from_numpy(embeddings2).to(self.torch_device)
        else:
            embeddings2_tensor = embeddings2.to(self.torch_device)
        
        # Normalize embeddings on GPU
        norm1 = embeddings1_tensor / (torch.linalg.norm(embeddings1_tensor, dim=1, keepdim=True) + 1e-10)
        norm2 = embeddings2_tensor / (torch.linalg.norm(embeddings2_tensor, dim=1, keepdim=True) + 1e-10)
        
        # Calculate cosine similarity on GPU
        similarity_matrix = torch.mm(norm1, norm2.T)
        
        # Convert back to numpy
        return similarity_matrix.cpu().numpy()
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """
        Calculate similarity score between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        embeddings = self.encode([text1, text2])
        sim_matrix = self.similarity(embeddings[0:1], embeddings[1:2])
        return float(sim_matrix[0, 0])
    
    def find_most_similar(self, query: str, 
                         candidates: List[str], 
                         top_k: int = 5) -> List[tuple]:
        """
        Find most similar texts from candidates
        
        Args:
            query: Query text
            candidates: List of candidate texts
            top_k: Number of top results to return
            
        Returns:
            List of (text, score) tuples sorted by similarity
        """
        if not candidates:
            return []
        
        # Encode all texts
        all_texts = [query] + candidates
        embeddings = self.encode(all_texts)
        
        # Calculate similarities
        query_embedding = embeddings[0:1]
        candidate_embeddings = embeddings[1:]
        
        similarities = self.similarity(query_embedding, candidate_embeddings)
        scores = similarities[0]
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        # Return results
        results = [(candidates[idx], float(scores[idx])) for idx in top_indices]
        return results
    
    def save_embeddings(self, embeddings: np.ndarray, 
                       texts: List[str], 
                       filepath: str):
        """
        Save embeddings to file
        
        Args:
            embeddings: Embeddings array
            texts: Corresponding texts
            filepath: Path to save file
        """
        import json
        
        # Convert to CPU numpy if tensor
        if torch.is_tensor(embeddings):
            embeddings = embeddings.cpu().numpy()
        
        data = {
            "embeddings": embeddings.tolist(),
            "texts": texts,
            "model": self.model_name,
            "dimension": self.embedding_dim,
            "device": str(self.torch_device)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f)
        
        logger.info(f"Saved {len(texts)} embeddings to {filepath}")
    
    def load_embeddings(self, filepath: str) -> tuple:
        """
        Load embeddings from file
        
        Args:
            filepath: Path to saved embeddings
            
        Returns:
            Tuple of (embeddings, texts)
        """
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