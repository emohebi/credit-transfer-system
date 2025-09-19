"""
Interface for local embedding model integration
"""

import logging
import numpy as np
from typing import List, Optional, Union, Dict
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

logger = logging.getLogger(__name__)

# Import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.error("sentence-transformers not installed. Please install it for embedding support.")


class EmbeddingInterface:
    """Interface for local embedding model"""
    
    # Model configurations
    MODELS = {
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
    
    def __init__(self, 
                 model_name: str = "jinaai--jina-embeddings-v4",
                 model_cache_dir: str = "/root/.cache/huggingface/hub",
                 external_model_dir: str = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models",
                 device: str = "cuda",
                 batch_size: int = 32):
        """
        Initialize embedding interface with local model
        
        Args:
            model_name: Name of the model to use from MODELS dict
            model_cache_dir: Directory for HuggingFace cache
            external_model_dir: Directory containing pre-downloaded models
            device: Device to run model on (cuda/cpu)
            batch_size: Default batch size for encoding
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers is required for embeddings. Install with: pip install sentence-transformers")
        
        self.model_name = model_name
        self.model_cache_dir = Path(model_cache_dir)
        self.external_model_dir = Path(external_model_dir)
        self.device = device
        self.default_batch_size = batch_size
        
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
        """Initialize the SentenceTransformer model"""
        try:
            snapshot_location = self._get_snapshot_location()
            logger.info(f"Loading embedding model from: {snapshot_location}")
            
            self.model = SentenceTransformer(
                snapshot_location,
                trust_remote_code=self.trust_remote_code,
                device=self.device
            )
            
            # Update embedding dimension from model
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Successfully loaded embedding model: {self.model_name} (dim={self.embedding_dim})")
            
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
               normalize_embeddings: bool = False) -> np.ndarray:
        """
        Generate embeddings for texts
        
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
                import torch
                return torch.from_numpy(cached)
            return cached
        
        # Set batch size
        if batch_size is None:
            batch_size = self.default_batch_size
        
        # Encode using SentenceTransformer
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_tensor=convert_to_tensor,
            normalize_embeddings=normalize_embeddings
        )
        
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
        
        # Normalize embeddings
        norm1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-10)
        norm2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-10)
        
        # Calculate cosine similarity
        similarity_matrix = np.dot(norm1, norm2.T)
        
        return similarity_matrix
    
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
        
        data = {
            "embeddings": embeddings.tolist(),
            "texts": texts,
            "model": self.model_name,
            "dimension": self.embedding_dim
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
    
    def get_model_info(self) -> Dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "device": self.device,
            "trust_remote_code": self.trust_remote_code,
            "cache_size": len(self.cache)
        }v2",
                 api_endpoint: Optional[str] = None,
                 api_key: Optional[str] = None,
                 embedding_dim: int = 384,
                 use_api: bool = False):
        """
        Initialize embedding interface
        
        Args:
            model_path: Path to local model or model name
            api_endpoint: Optional API endpoint for embedding service
            api_key: Optional API key for authentication
            embedding_dim: Dimension of embeddings
            use_api: Whether to use API instead of local model
        """
        self.model_path = model_path
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.embedding_dim = embedding_dim
        self.use_api = use_api
        self.model = None
        
        # Initialize based on configuration
        if not use_api and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_path)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
                logger.info(f"Loaded local embedding model: {model_path}")
            except Exception as e:
                logger.warning(f"Failed to load local model: {e}. Will use API or fallback.")
                self.use_api = True
        elif not use_api:
            logger.warning("Local model requested but sentence-transformers not available. Using API.")
            self.use_api = True
        
        # Setup session for API calls
        if self.use_api or api_endpoint:
            self.session = requests.Session()
            if api_key:
                self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: int = 32,
               show_progress: bool = False) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: Single text or list of texts to encode
            batch_size: Batch size for encoding
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        # Handle single text input
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        # Use local model if available
        if self.model is not None:
            return self.model.encode(texts, 
                                    batch_size=batch_size,
                                    show_progress_bar=show_progress)
        
        # Use API if configured
        if self.use_api and self.api_endpoint:
            return self._encode_via_api(texts)
        
        # Fallback to random embeddings for testing
        logger.warning("No embedding method available. Using random embeddings for testing.")
        return self._generate_random_embeddings(texts)
    
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
        
        # Normalize embeddings
        norm1 = embeddings1 / (np.linalg.norm(embeddings1, axis=1, keepdims=True) + 1e-10)
        norm2 = embeddings2 / (np.linalg.norm(embeddings2, axis=1, keepdims=True) + 1e-10)
        
        # Calculate cosine similarity
        similarity_matrix = np.dot(norm1, norm2.T)
        
        return similarity_matrix
    
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
    
    def _encode_via_api(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts via API
        
        Args:
            texts: Texts to encode
            
        Returns:
            Embeddings array
        """
        try:
            response = self.session.post(
                f"{self.api_endpoint}/encode",
                json={"texts": texts},
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            embeddings = np.array(result.get("embeddings", []))
            
            if embeddings.shape[0] != len(texts):
                raise ValueError(f"Expected {len(texts)} embeddings, got {embeddings.shape[0]}")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"API encoding failed: {e}")
            return self._generate_random_embeddings(texts)
    
    def _generate_random_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate random embeddings for testing
        
        Args:
            texts: Texts to generate embeddings for
            
        Returns:
            Random embeddings with some consistency based on text
        """
        np.random.seed(42)  # For reproducibility in testing
        embeddings = []
        
        for text in texts:
            # Generate semi-consistent embeddings based on text hash
            seed = hash(text) % (2**32)
            np.random.seed(seed)
            embedding = np.random.randn(self.embedding_dim)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
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
        data = {
            "embeddings": embeddings.tolist(),
            "texts": texts,
            "model": self.model_path,
            "dimension": self.embedding_dim
        }
        
        import json
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


class EmbeddingCache:
    """Cache for embeddings to avoid recomputation"""
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize embedding cache
        
        Args:
            max_size: Maximum number of embeddings to cache
        """
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from cache"""
        if text in self.cache:
            self.access_count[text] = self.access_count.get(text, 0) + 1
            return self.cache[text]
        return None
    
    def put(self, text: str, embedding: np.ndarray):
        """Add embedding to cache"""
        # Remove least accessed item if cache is full
        if len(self.cache) >= self.max_size:
            least_accessed = min(self.access_count.items(), key=lambda x: x[1])[0]
            del self.cache[least_accessed]
            del self.access_count[least_accessed]
        
        self.cache[text] = embedding
        self.access_count[text] = 1
    
    def clear(self):
        """Clear the cache"""
        self.cache.clear()
        self.access_count.clear()