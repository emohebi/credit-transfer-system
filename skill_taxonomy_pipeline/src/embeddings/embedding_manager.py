"""
Optimized Enhanced Embeddings module with vectorized multi-factor skill matching
High-performance implementation without for-loops for large-scale processing
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path
import logging
import pickle
import torch
from sentence_transformers import SentenceTransformer
import faiss
from tqdm import tqdm
import hashlib
from concurrent.futures import ThreadPoolExecutor
import gc
from sklearn.metrics.pairwise import cosine_similarity
from numba import jit, prange
import warnings
from src.interfaces.model_factory import ModelFactory
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class UnifiedScorer:
    """Optimized scoring system with vectorized operations"""
    
    def __init__(self):
        # Level compatibility matrix (7x7 for SFIA levels 1-7)
        self.level_compatibility_matrix = np.array([
            # Uni: 1    2    3    4    5    6    7
            [1.0, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1],  # VET Level 1
            [0.7, 1.0, 0.9, 0.7, 0.5, 0.3, 0.2],  # VET Level 2
            [0.5, 0.7, 1.0, 0.9, 0.7, 0.5, 0.3],  # VET Level 3
            [0.3, 0.5, 0.7, 1.0, 0.9, 0.7, 0.5],  # VET Level 4
            [0.2, 0.3, 0.5, 0.7, 1.0, 0.9, 0.7],  # VET Level 5
            [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 0.9],  # VET Level 6
            [0.1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0],  # VET Level 7
        ], dtype=np.float32)
        
        # Context compatibility as a matrix for vectorized lookup
        # Order: practical=0, theoretical=1, hybrid=2
        self.context_compatibility_matrix = np.array([
            # practical, theoretical, hybrid
            [1.0, 0.3, 0.7],  # practical
            [0.3, 1.0, 0.7],  # theoretical
            [0.7, 0.7, 1.0],  # hybrid
        ], dtype=np.float32)
        
        # Create context to index mapping
        self.context_to_idx = {
            'practical': 0,
            'theoretical': 1,
            'hybrid': 2
        }
    
    def get_vectorized_level_compatibility(self, levels1: np.ndarray, levels2: np.ndarray) -> np.ndarray:
        """
        Vectorized level compatibility calculation using advanced indexing
        
        Args:
            levels1: Array of levels for first set (shape: n1,)
            levels2: Array of levels for second set (shape: n2,)
            
        Returns:
            Compatibility matrix (shape: n1 x n2)
        """
        # Ensure levels are in valid range and convert to indices
        idx1 = np.clip(levels1 - 1, 0, 6).astype(np.int32)
        idx2 = np.clip(levels2 - 1, 0, 6).astype(np.int32)
        
        # Use advanced indexing to create compatibility matrix
        # This creates all combinations efficiently
        return self.level_compatibility_matrix[idx1[:, np.newaxis], idx2]
    
    def get_vectorized_context_compatibility(self, contexts1: np.ndarray, contexts2: np.ndarray) -> np.ndarray:
        """
        Vectorized context compatibility calculation
        
        Args:
            contexts1: Array of context indices for first set (shape: n1,)
            contexts2: Array of context indices for second set (shape: n2,)
            
        Returns:
            Compatibility matrix (shape: n1 x n2)
        """
        # Use advanced indexing for context compatibility
        return self.context_compatibility_matrix[contexts1[:, np.newaxis], contexts2]


class OptimizedEmbeddingManager:
    """Highly optimized embedding manager with fully vectorized operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_name = config['embedding']['model_name']
        self.batch_size = config['embedding']['batch_size']
        self.cache_dir = Path(config['paths']['cache_dir']) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Multi-factor weights (configurable)
        self.semantic_weight = config['embedding'].get('semantic_weight', 0.6)
        self.level_weight = config['embedding'].get('level_weight', 0.25)
        self.context_weight = config['embedding'].get('context_weight', 0.15)
        
        # Normalize weights
        total_weight = self.semantic_weight + self.level_weight + self.context_weight
        self.semantic_weight /= total_weight
        self.level_weight /= total_weight
        self.context_weight /= total_weight
        
        logger.info(f"Optimized multi-factor weights - Semantic: {self.semantic_weight:.2f}, "
                   f"Level: {self.level_weight:.2f}, Context: {self.context_weight:.2f}")
        
        # Initialize unified scorer with vectorized operations
        self.scorer = UnifiedScorer()
        
        # Similarity method selection
        self.similarity_method = config['embedding'].get('similarity_method', 'faiss')
        
        # Initialize model
        self.device = config['embedding']['device']
        # logger.info(f"Loading embedding model: {self.model_name} on {self.device}")
        # self.model = SentenceTransformer(self.model_name, device=self.device)
        self.model = ModelFactory.create_embedding_interface(config)
        
        # Get embedding dimension
        # self.embedding_dim = self.model.get_sentence_embedding_dimension()
        # logger.info(f"Embedding dimension: {self.embedding_dim}")
        
        # Initialize caches
        self.embedding_cache = {}
        self.faiss_index = None
        self.similarity_matrix = None
        self.embeddings_for_matrix = None
        
        # Pre-computed metadata arrays for vectorized operations
        self.levels_array = None
        self.contexts_array = None
        self.context_indices = None
    
    def generate_embeddings(self, 
                           texts: List[str], 
                           cache_key: Optional[str] = None,
                           use_cache: bool = True) -> np.ndarray:
        """Generate embeddings for texts with caching support"""
        if use_cache and cache_key:
            cached_embeddings = self._load_cached_embeddings(cache_key)
            if cached_embeddings is not None:
                logger.info(f"Loaded {len(cached_embeddings)} embeddings from cache")
                return cached_embeddings
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        
        # Process in batches for memory efficiency
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + self.batch_size]
            # Generate embeddings
            batch_embeddings = self.model.encode(
                batch_texts,
                batch_size=self.batch_size,
                convert_to_tensor=False,
                show_progress=False,
                normalize_embeddings=self.config['embedding']['normalize_embeddings']
            )
            
            all_embeddings.append(batch_embeddings)
            
            # Clear GPU cache periodically
            if i % (self.batch_size * 10) == 0 and self.device == 'cuda':
                torch.cuda.empty_cache()
        
        embeddings = np.vstack(all_embeddings).astype(np.float32)
        
        # Cache embeddings
        if use_cache and cache_key:
            self._save_cached_embeddings(embeddings, cache_key)
        
        return embeddings
    
    def generate_embeddings_for_dataframe(self, 
                                         df: pd.DataFrame,
                                         text_column: str = 'combined_text') -> np.ndarray:
        """
        Generate embeddings and pre-process metadata for vectorized operations
        """
        # Pre-process metadata for vectorized operations
        if all(col in df.columns for col in ['level', 'context']):
            # Extract and vectorize levels
            self.levels_array = self._vectorize_levels(df['level'].values)
            
            # Extract and vectorize contexts
            self.contexts_array, self.context_indices = self._vectorize_contexts(df['context'].values)
            
            logger.info("Pre-processed metadata for vectorized multi-factor matching")
            logger.info(f"Levels range: {self.levels_array.min()}-{self.levels_array.max()}")
            logger.info(f"Context distribution: practical={np.sum(self.context_indices==0)}, "
                       f"theoretical={np.sum(self.context_indices==1)}, "
                       f"hybrid={np.sum(self.context_indices==2)}")
        
        # Create cache key from dataframe content
        cache_key = self._create_cache_key(df, text_column)
        
        # Generate embeddings
        texts = df[text_column].tolist()
        embeddings = self.generate_embeddings(texts, cache_key=cache_key)
        
        return embeddings
    
    def _vectorize_levels(self, levels) -> np.ndarray:
        """Vectorize level values for efficient computation"""
        vectorized = np.zeros(len(levels), dtype=np.int32)
        
        for i, level in enumerate(levels):
            if hasattr(level, 'value'):  # Enum
                vectorized[i] = level.value
            else:
                try:
                    vectorized[i] = int(level)
                except:
                    vectorized[i] = 3  # Default
        
        return np.clip(vectorized, 1, 7)
    
    def _vectorize_contexts(self, contexts) -> Tuple[np.ndarray, np.ndarray]:
        """
        Vectorize context values for efficient computation
        Returns both string array and index array
        """
        context_strings = np.array([
            str(c).lower() if not hasattr(c, 'value') else c.value 
            for c in contexts
        ])
        
        # Create index array for matrix lookup
        context_indices = np.zeros(len(contexts), dtype=np.int32)
        
        # Vectorized mapping using numpy operations
        context_indices[context_strings == 'practical'] = 0
        context_indices[context_strings == 'theoretical'] = 1
        context_indices[context_strings == 'hybrid'] = 2
        
        # Handle any unknown contexts as hybrid
        unknown_mask = ~np.isin(context_strings, ['practical', 'theoretical', 'hybrid'])
        context_indices[unknown_mask] = 2
        
        return context_strings, context_indices
    
    def calculate_multi_factor_similarity(self, 
                                         embeddings1: np.ndarray,
                                         embeddings2: np.ndarray,
                                         metadata1: Optional[pd.DataFrame] = None,
                                         metadata2: Optional[pd.DataFrame] = None) -> np.ndarray:
        """
        Fully vectorized multi-factor similarity calculation
        
        This optimized version uses:
        - NumPy broadcasting for semantic similarity
        - Advanced indexing for level compatibility
        - Vectorized context mapping
        - No Python for-loops
        
        Args:
            embeddings1: First set of embeddings (n1 x d)
            embeddings2: Second set of embeddings (n2 x d)
            metadata1: Optional metadata for first set
            metadata2: Optional metadata for second set
            
        Returns:
            Combined similarity matrix (n1 x n2)
        """
        n1, n2 = len(embeddings1), len(embeddings2)
        semantic_sim = self.model.similarity(embeddings1, embeddings2)
        # 1. Vectorized semantic similarity calculation
        # if self.config['embedding']['normalize_embeddings']:
        #     # If already normalized, simple dot product
        #     semantic_sim = np.dot(embeddings1, embeddings2.T)
        # else:
        #     # Normalize and compute in one operation
        #     norm1 = np.linalg.norm(embeddings1, axis=1, keepdims=True)
        #     norm2 = np.linalg.norm(embeddings2, axis=1, keepdims=True)
        #     semantic_sim = np.dot(embeddings1 / norm1, (embeddings2 / norm2).T)
        
        # If no metadata, return semantic similarity only
        if metadata1 is None or metadata2 is None:
            return semantic_sim.astype(np.float32)
        
        # 2. Vectorized level compatibility
        if 'level' in metadata1.columns and 'level' in metadata2.columns:
            # Extract levels as numpy arrays
            levels1 = self._vectorize_levels(metadata1['level'].values)
            levels2 = self._vectorize_levels(metadata2['level'].values)
            
            # Use vectorized scorer
            level_compat = self.scorer.get_vectorized_level_compatibility(levels1, levels2)
        else:
            # No level info, use ones
            level_compat = np.ones((n1, n2), dtype=np.float32)
        
        # 3. Vectorized context compatibility
        if 'context' in metadata1.columns and 'context' in metadata2.columns:
            # Convert contexts to indices
            _, ctx_idx1 = self._vectorize_contexts(metadata1['context'].values)
            _, ctx_idx2 = self._vectorize_contexts(metadata2['context'].values)
            
            # Use vectorized scorer
            context_compat = self.scorer.get_vectorized_context_compatibility(ctx_idx1, ctx_idx2)
        else:
            # No context info, use ones
            context_compat = np.ones((n1, n2), dtype=np.float32)
        
        # 4. Vectorized weighted combination
        combined_similarity = (
            semantic_sim * self.semantic_weight +
            level_compat * self.level_weight +
            context_compat * self.context_weight
        ).astype(np.float32)
        
        return combined_similarity
    
    def calculate_multi_factor_similarity_batch(self,
                                               embeddings: np.ndarray,
                                               batch_size: int = 1000) -> np.ndarray:
        """
        Calculate self-similarity matrix in batches for memory efficiency
        Useful for very large datasets
        """
        n = len(embeddings)
        similarity_matrix = np.zeros((n, n), dtype=np.float32)
        
        # Process in blocks to manage memory
        for i in tqdm(range(0, n, batch_size), desc="Computing similarity matrix"):
            end_i = min(i + batch_size, n)
            
            for j in range(i, n, batch_size):  # Start from i for symmetry
                end_j = min(j + batch_size, n)
                
                # Compute block
                block = self._compute_similarity_block(
                    embeddings[i:end_i],
                    embeddings[j:end_j],
                    i, end_i, j, end_j
                )
                
                # Fill symmetric positions
                similarity_matrix[i:end_i, j:end_j] = block
                if i != j:
                    similarity_matrix[j:end_j, i:end_i] = block.T
        
        return similarity_matrix
    
    def _compute_similarity_block(self,
                                 emb1: np.ndarray,
                                 emb2: np.ndarray,
                                 i_start: int, i_end: int,
                                 j_start: int, j_end: int) -> np.ndarray:
        """Compute a single block of the similarity matrix"""
        # Semantic similarity
        if self.config['embedding']['normalize_embeddings']:
            semantic_block = np.dot(emb1, emb2.T)
        else:
            semantic_block = cosine_similarity(emb1, emb2)
        
        # Level compatibility (if available)
        if self.levels_array is not None:
            levels1 = self.levels_array[i_start:i_end]
            levels2 = self.levels_array[j_start:j_end]
            level_block = self.scorer.get_vectorized_level_compatibility(levels1, levels2)
        else:
            level_block = np.ones_like(semantic_block)
        
        # Context compatibility (if available)
        if self.context_indices is not None:
            ctx1 = self.context_indices[i_start:i_end]
            ctx2 = self.context_indices[j_start:j_end]
            context_block = self.scorer.get_vectorized_context_compatibility(ctx1, ctx2)
        else:
            context_block = np.ones_like(semantic_block)
        
        # Weighted combination
        return (
            semantic_block * self.semantic_weight +
            level_block * self.level_weight +
            context_block * self.context_weight
        ).astype(np.float32)
    
    def build_similarity_index(self, embeddings: np.ndarray, index_type: str = "IVF1024,Flat"):
        """Build similarity index using either FAISS or similarity matrix"""
        self.embeddings_for_matrix = embeddings
        
        if self.similarity_method == 'matrix':
            self._build_similarity_matrix_optimized(embeddings)
        else:
            self._build_faiss_index(embeddings, index_type)
    
    def _build_similarity_matrix_optimized(self, embeddings: np.ndarray):
        """Build similarity matrix with optimized computation"""
        logger.info(f"Building optimized similarity matrix for {len(embeddings)} embeddings")
        
        n_samples = len(embeddings)
        memory_threshold = self.config['embedding'].get('matrix_memory_threshold', 10000)
        
        if n_samples <= memory_threshold:
            # Small dataset - compute full matrix at once
            logger.info("Computing full similarity matrix with vectorized operations...")
            
            # Create metadata dataframe for similarity calculation
            if self.levels_array is not None and self.contexts_array is not None:
                metadata = pd.DataFrame({
                    'level': self.levels_array,
                    'context': self.contexts_array
                })
                self.similarity_matrix = self.calculate_multi_factor_similarity(
                    embeddings, embeddings, metadata, metadata
                )
            else:
                # Semantic only
                if self.config['embedding']['normalize_embeddings']:
                    self.similarity_matrix = np.dot(embeddings, embeddings.T)
                else:
                    self.similarity_matrix = cosine_similarity(embeddings)
            
            logger.info(f"Similarity matrix computed: {self.similarity_matrix.shape}")
        else:
            # Large dataset - compute in batches
            logger.info(f"Large dataset ({n_samples} samples) - using batch computation")
            self.similarity_matrix = self.calculate_multi_factor_similarity_batch(embeddings)
    
    def _build_faiss_index(self, embeddings: np.ndarray, index_type: str = "IVF1024,Flat"):
        """Build FAISS index for efficient similarity search"""
        logger.info(f"Building FAISS index for {len(embeddings)} embeddings")
        
        n_samples = len(embeddings)
        
        # Ensure float32 for FAISS
        embeddings = embeddings.astype(np.float32)
        
        if n_samples < 1024:
            # Use flat index for small datasets
            if self.config['embedding']['normalize_embeddings']:
                self.faiss_index = faiss.IndexFlatIP(self.embedding_dim)
            else:
                self.faiss_index = faiss.IndexFlatL2(self.embedding_dim)
        else:
            # Use IVF index for large datasets
            nlist = min(1024, n_samples // 50)
            
            if self.config['embedding']['normalize_embeddings']:
                quantizer = faiss.IndexFlatIP(self.embedding_dim)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, self.embedding_dim, nlist, faiss.METRIC_INNER_PRODUCT
                )
            else:
                quantizer = faiss.IndexFlatL2(self.embedding_dim)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, self.embedding_dim, nlist
                )
            
            logger.info("Training FAISS index...")
            self.faiss_index.train(embeddings)
        
        self.faiss_index.add(embeddings)
        
        if hasattr(self.faiss_index, 'nprobe'):
            self.faiss_index.nprobe = min(64, self.faiss_index.nlist)
        
        logger.info(f"FAISS index built with {self.faiss_index.ntotal} vectors")
    
    def find_similar_skills_vectorized(self, 
                                      query_indices: np.ndarray,
                                      k: int = 10,
                                      threshold: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Vectorized batch search for multiple query skills at once
        
        Args:
            query_indices: Array of query indices
            k: Number of similar skills per query
            threshold: Optional similarity threshold
            
        Returns:
            Tuple of (distances, indices) both with shape (len(query_indices), k)
        """
        if self.similarity_method == 'matrix':
            return self._find_similar_matrix_vectorized(query_indices, k, threshold)
        else:
            return self._find_similar_faiss_vectorized(query_indices, k, threshold)
    
    def _find_similar_matrix_vectorized(self, 
                                       query_indices: np.ndarray,
                                       k: int = 10,
                                       threshold: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized similarity search using precomputed matrix"""
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not built")
        
        # Get similarities for all queries at once
        similarities = self.similarity_matrix[query_indices]
        
        # Use argpartition for efficient top-k selection
        if k >= similarities.shape[1]:
            # Return all sorted
            indices = np.argsort(similarities, axis=1)[:, ::-1]
            distances = np.take_along_axis(similarities, indices, axis=1)
        else:
            # Efficient top-k using argpartition
            # Note: argpartition finds k largest when used with negative values
            top_k_indices = np.argpartition(-similarities, k, axis=1)[:, :k]
            
            # Get the values and sort them
            top_k_values = np.take_along_axis(similarities, top_k_indices, axis=1)
            sorted_idx = np.argsort(-top_k_values, axis=1)
            
            indices = np.take_along_axis(top_k_indices, sorted_idx, axis=1)
            distances = np.take_along_axis(top_k_values, sorted_idx, axis=1)
        
        # Apply threshold if specified (vectorized)
        if threshold is not None:
            mask = distances >= threshold
            # This requires handling variable-length results
            # For simplicity, we'll set below-threshold values to -1
            indices[~mask] = -1
            distances[~mask] = -1
        
        return distances, indices
    
    def _find_similar_faiss_vectorized(self, 
                                      query_indices: np.ndarray,
                                      k: int = 10,
                                      threshold: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized FAISS search with post-processing"""
        if self.faiss_index is None:
            raise ValueError("FAISS index not built")
        
        # Get query embeddings
        query_embeddings = self.embeddings_for_matrix[query_indices].astype(np.float32)
        
        # Search for more candidates to account for multi-factor filtering
        k_search = min(k * 3, self.faiss_index.ntotal)
        
        # Batch FAISS search
        distances, indices = self.faiss_index.search(query_embeddings, k_search)
        
        # Apply multi-factor re-scoring if metadata available
        if self.levels_array is not None and self.context_indices is not None:
            distances = self._rescore_with_multi_factor_vectorized(
                query_indices, indices, distances
            )
            
            # Re-sort after rescoring
            sorted_idx = np.argsort(-distances, axis=1)[:, :k]
            indices = np.take_along_axis(indices, sorted_idx, axis=1)[:, :k]
            distances = np.take_along_axis(distances, sorted_idx, axis=1)[:, :k]
        else:
            # Keep top-k only
            indices = indices[:, :k]
            distances = distances[:, :k]
        
        # Apply threshold
        if threshold is not None:
            mask = distances >= threshold
            indices[~mask] = -1
            distances[~mask] = -1
        
        return distances, indices
    
    def _rescore_with_multi_factor_vectorized(self,
                                             query_indices: np.ndarray,
                                             candidate_indices: np.ndarray,
                                             semantic_scores: np.ndarray) -> np.ndarray:
        """
        Vectorized multi-factor rescoring
        
        Args:
            query_indices: Shape (n_queries,)
            candidate_indices: Shape (n_queries, k_candidates)
            semantic_scores: Shape (n_queries, k_candidates)
            
        Returns:
            Rescored distances with same shape
        """
        n_queries, k_candidates = candidate_indices.shape
        
        # Get query metadata
        query_levels = self.levels_array[query_indices]  # Shape: (n_queries,)
        query_contexts = self.context_indices[query_indices]  # Shape: (n_queries,)
        
        # Initialize rescored matrix
        rescored = np.zeros_like(semantic_scores)
        
        # Vectorized level compatibility
        for i in range(n_queries):
            valid_mask = candidate_indices[i] >= 0  # Skip invalid indices
            valid_candidates = candidate_indices[i][valid_mask]
            
            if len(valid_candidates) > 0:
                # Get candidate levels
                candidate_levels = self.levels_array[valid_candidates]
                
                # Compute level compatibility for this query
                level_compat = self.scorer.level_compatibility_matrix[
                    np.clip(query_levels[i] - 1, 0, 6),
                    np.clip(candidate_levels - 1, 0, 6)
                ]
                
                # Get candidate contexts
                candidate_contexts = self.context_indices[valid_candidates]
                
                # Compute context compatibility
                context_compat = self.scorer.context_compatibility_matrix[
                    query_contexts[i],
                    candidate_contexts
                ]
                
                # Combine scores
                rescored[i, valid_mask] = (
                    semantic_scores[i, valid_mask] * self.semantic_weight +
                    level_compat * self.level_weight +
                    context_compat * self.context_weight
                )
        
        return rescored
    
    def _create_cache_key(self, df: pd.DataFrame, text_column: str) -> str:
        """Create a cache key from dataframe content"""
        content = ''.join(df[text_column].astype(str).tolist()[:100])
        content += f"_{len(df)}_{self.model_name}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_cached_embeddings(self, cache_key: str) -> Optional[np.ndarray]:
        """Load embeddings from cache"""
        cache_path = self.cache_dir / f"{cache_key}.npy"
        if cache_path.exists():
            try:
                return np.load(cache_path)
            except Exception as e:
                logger.warning(f"Failed to load cached embeddings: {e}")
        return None
    
    def _save_cached_embeddings(self, embeddings: np.ndarray, cache_key: str):
        """Save embeddings to cache"""
        cache_path = self.cache_dir / f"{cache_key}.npy"
        try:
            np.save(cache_path, embeddings)
            logger.info(f"Saved embeddings to cache: {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save embeddings to cache: {e}")


# For backward compatibility, inherit from OptimizedEmbeddingManager
class EmbeddingManager(OptimizedEmbeddingManager):
    """Backward compatible class name"""
    pass


# Keep the original deduplicator class as it already uses the manager efficiently
class SimilarityDeduplicator:
    """Deduplication with optimized multi-factor similarity from manager"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.similarity_threshold = config['dedup']['similarity_threshold']
        self.fuzzy_threshold = config['dedup']['fuzzy_ratio_threshold']
        
        # Thresholds for different match types
        self.direct_threshold = config.get('direct_match_threshold', 0.9)
        self.partial_threshold = config.get('partial_threshold', 0.8)
        
        logger.info(f"Deduplication thresholds - Direct: {self.direct_threshold}, "
                   f"Partial: {self.partial_threshold}, Min: {self.similarity_threshold}")
    
    def find_duplicates(self, 
                       df: pd.DataFrame, 
                       embeddings: np.ndarray,
                       embedding_manager: EmbeddingManager) -> pd.DataFrame:
        """
        Find duplicate skills using optimized multi-factor similarity
        Now uses vectorized operations from the manager
        """
        logger.info(f"Finding duplicates among {len(df)} skills using optimized multi-factor matching")
        
        # Build similarity index if not already built
        if embedding_manager.similarity_method == 'matrix':
            if embedding_manager.embeddings_for_matrix is None:
                embedding_manager.build_similarity_index(embeddings)
        else:
            if embedding_manager.faiss_index is None:
                embedding_manager.build_similarity_index(embeddings)
        
        # Store embeddings for FAISS method
        if embedding_manager.embeddings_for_matrix is None:
            embedding_manager.embeddings_for_matrix = embeddings
        
        # Process in batches for efficiency
        batch_size = min(100, len(df))
        duplicate_groups = []
        processed_indices = set()
        duplicate_details = []
        
        # Process all unprocessed indices in batches
        all_indices = np.arange(len(df))
        
        for batch_start in tqdm(range(0, len(df), batch_size), desc="Finding duplicates (optimized)"):
            batch_end = min(batch_start + batch_size, len(df))
            batch_indices = all_indices[batch_start:batch_end]
            
            # Skip already processed
            batch_indices = [idx for idx in batch_indices if idx not in processed_indices]
            if not batch_indices:
                continue
            
            batch_indices = np.array(batch_indices)
            
            # Vectorized similarity search for the batch
            distances, indices = embedding_manager.find_similar_skills_vectorized(
                batch_indices,
                k=20,
                threshold=self.similarity_threshold
            )
            
            # Process results for each query in the batch
            for i, query_idx in enumerate(batch_indices):
                if query_idx in processed_indices:
                    continue
                
                # Get similar indices for this query
                similar_indices = []
                match_classifications = []
                
                for j, (idx, score) in enumerate(zip(indices[i], distances[i])):
                    if idx < 0 or idx == query_idx or idx in processed_indices:
                        continue
                    
                    if score >= self.direct_threshold:
                        similar_indices.append(idx)
                        match_classifications.append({
                            'index': idx,
                            'score': float(score),
                            'type': 'direct'
                        })
                    elif score >= self.partial_threshold:
                        # Check level compatibility
                        if self._check_level_compatibility(df.iloc[query_idx], df.iloc[idx]):
                            similar_indices.append(idx)
                            match_classifications.append({
                                'index': idx,
                                'score': float(score),
                                'type': 'partial'
                            })
                
                if similar_indices:
                    group = [query_idx] + similar_indices
                    duplicate_groups.append(group)
                    processed_indices.update(group)
                    
                    duplicate_details.append({
                        'master_idx': query_idx,
                        'group': group,
                        'matches': match_classifications
                    })
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups using optimized multi-factor matching")
        
        # Add duplicate information to dataframe
        df_result = df.copy()
        df_result['duplicate_group'] = -1
        df_result['is_duplicate'] = False
        df_result['master_skill_id'] = df_result['skill_id']
        df_result['match_type'] = 'none'
        df_result['match_score'] = 0.0
        
        for group_id, (group, details) in enumerate(zip(duplicate_groups, duplicate_details)):
            # Select master skill
            master_idx = self._select_master_skill(df, group, details)
            master_skill_id = df.loc[master_idx, 'skill_id']
            
            # Mark duplicates
            for idx in group:
                df_result.loc[idx, 'duplicate_group'] = group_id
                df_result.loc[idx, 'is_duplicate'] = (idx != master_idx)
                df_result.loc[idx, 'master_skill_id'] = master_skill_id
                
                if idx != master_idx:
                    match_info = next((m for m in details['matches'] if m['index'] == idx), None)
                    if match_info:
                        df_result.loc[idx, 'match_type'] = match_info['type']
                        df_result.loc[idx, 'match_score'] = match_info['score']
        
        self._log_deduplication_stats(df_result)
        
        return df_result
    
    def _check_level_compatibility(self, skill1: pd.Series, skill2: pd.Series) -> bool:
        """Check if two skills have compatible levels for deduplication"""
        if 'level' not in skill1 or 'level' not in skill2:
            return True
        
        level1 = self._extract_level_value(skill1['level'])
        level2 = self._extract_level_value(skill2['level'])
        
        return abs(level1 - level2) <= 1
    
    def _extract_level_value(self, level) -> int:
        """Extract numeric level value"""
        if isinstance(level, (int, float)):
            return int(level)
        elif hasattr(level, 'value'):
            return level.value
        else:
            return 3
    
    def _select_master_skill(self, df: pd.DataFrame, group: List[int], details: Dict) -> int:
        """Select the master skill from a duplicate group"""
        group_df = df.iloc[group].copy()
        group_df['_group_idx'] = group
        
        # Calculate composite score
        for idx, row in group_df.iterrows():
            confidence = row.get('confidence', 0.5)
            level = self._extract_level_value(row.get('level', 3))
            desc_length = len(str(row.get('description', '')))
            
            score = (
                confidence * 0.4 +
                (level / 7.0) * 0.3 +
                min(desc_length / 500.0, 1.0) * 0.3
            )
            group_df.loc[idx, '_master_score'] = score
        
        master_idx = group_df.nlargest(1, '_master_score')['_group_idx'].iloc[0]
        
        return master_idx
    
    def _log_deduplication_stats(self, df: pd.DataFrame):
        """Log statistics about deduplication results"""
        total_duplicates = df['is_duplicate'].sum()
        direct_matches = (df['match_type'] == 'direct').sum()
        partial_matches = (df['match_type'] == 'partial').sum()
        
        logger.info("=" * 60)
        logger.info("DEDUPLICATION STATISTICS (OPTIMIZED)")
        logger.info("=" * 60)
        logger.info(f"Total skills: {len(df)}")
        logger.info(f"Duplicate skills found: {total_duplicates}")
        logger.info(f"  - Direct matches: {direct_matches}")
        logger.info(f"  - Partial matches: {partial_matches}")
        logger.info(f"Unique skills after dedup: {len(df) - total_duplicates}")
        logger.info(f"Duplicate groups: {df[df['duplicate_group'] >= 0]['duplicate_group'].nunique()}")
    
    def merge_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Merge duplicate skills intelligently"""
        # Keep non-duplicates
        unique_df = df[~df['is_duplicate']].copy()
        
        # For duplicate groups, merge information
        duplicate_groups = df[df['duplicate_group'] >= 0].groupby('duplicate_group')
        
        for group_id, group_df in duplicate_groups:
            if len(group_df) > 1:
                master_idx = group_df[~group_df['is_duplicate']].index[0]
                
                # Merge keywords
                all_keywords = []
                for keywords in group_df['keywords']:
                    if isinstance(keywords, list):
                        all_keywords.extend(keywords)
                unique_keywords = list(set(all_keywords))
                unique_df.loc[master_idx, 'keywords'] = [[kw] for kw in unique_keywords]
                unique_df.loc[master_idx, 'keywords_str'] = ' '.join(unique_keywords)
                
                # Keep best description
                best_description = group_df.loc[group_df['description_length'].idxmax(), 'description']
                unique_df.loc[master_idx, 'description'] = best_description
                
                # Keep highest level
                if 'level' in group_df.columns:
                    levels = [self._extract_level_value(level) for level in group_df['level']]
                    max_level_idx = group_df.index[levels.index(max(levels))]
                    unique_df.loc[master_idx, 'level'] = group_df.loc[max_level_idx, 'level']
                
                # Update combined text
                unique_df.loc[master_idx, 'combined_text'] = (
                    # unique_df.loc[master_idx, 'name'] + ': ' +
                    best_description #+ ' ' +
                    # ' '.join(unique_keywords)
                )
                
                # Add metadata
                unique_df.loc[master_idx, 'merged_from'] = [[id_] for id_ in group_df['skill_id'].tolist()]
                unique_df.loc[master_idx, 'merge_count'] = len(group_df)
        
        logger.info(f"Reduced {len(df)} skills to {len(unique_df)} unique skills")
        
        return unique_df.reset_index(drop=True)