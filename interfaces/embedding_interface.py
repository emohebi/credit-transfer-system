"""
Interface for local embedding model integration
"""

import logging
import numpy as np
from typing import List, Optional, Union
import requests

logger = logging.getLogger(__name__)

# Optional: Import sentence-transformers if available
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.info("sentence-transformers not installed. Using API or fallback methods.")


class EmbeddingInterface:
    """Interface for local embedding model"""
    
    def __init__(self, 
                 model_path: str = "sentence-transformers/all-MiniLM-L6-v2",
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
