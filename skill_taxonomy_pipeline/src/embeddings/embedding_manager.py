"""
Optimized Enhanced Embeddings module with vectorized multi-factor skill matching
Now includes alternative title tracking during deduplication
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
import warnings
from src.interfaces.model_factory import ModelFactory
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)


class UnifiedScorer:
    """Optimized scoring system with vectorized operations"""
    
    def __init__(self):
        # Level compatibility matrix (7x7 for SFIA levels 1-7)
        self.level_compatibility_matrix = np.array([
            [1.0, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1],
            [0.7, 1.0, 0.9, 0.7, 0.5, 0.3, 0.2],
            [0.5, 0.7, 1.0, 0.9, 0.7, 0.5, 0.3],
            [0.3, 0.5, 0.7, 1.0, 0.9, 0.7, 0.5],
            [0.2, 0.3, 0.5, 0.7, 1.0, 0.9, 0.7],
            [0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 0.9],
            [0.1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0],
        ], dtype=np.float32)
        
        self.context_compatibility_matrix = np.array([
            [1.0, 0.3, 0.7],
            [0.3, 1.0, 0.7],
            [0.7, 0.7, 1.0],
        ], dtype=np.float32)
        
        self.context_to_idx = {
            'practical': 0,
            'theoretical': 1,
            'hybrid': 2
        }
    
    def get_vectorized_level_compatibility(self, levels1: np.ndarray, levels2: np.ndarray) -> np.ndarray:
        """Vectorized level compatibility calculation"""
        idx1 = np.clip(levels1 - 1, 0, 6).astype(np.int32)
        idx2 = np.clip(levels2 - 1, 0, 6).astype(np.int32)
        return self.level_compatibility_matrix[idx1[:, np.newaxis], idx2]
    
    def get_vectorized_context_compatibility(self, contexts1: np.ndarray, contexts2: np.ndarray) -> np.ndarray:
        """Vectorized context compatibility calculation"""
        return self.context_compatibility_matrix[contexts1[:, np.newaxis], contexts2]


class OptimizedEmbeddingManager:
    """Highly optimized embedding manager with fully vectorized operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.model_name = config['embedding']['model_name']
        self.batch_size = config['embedding']['batch_size']
        self.cache_dir = Path(config['paths']['cache_dir']) / "embeddings"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Multi-factor weights
        self.semantic_weight = config['embedding'].get('semantic_weight', 0.6)
        self.level_weight = config['embedding'].get('level_weight', 0.25)
        self.context_weight = config['embedding'].get('context_weight', 0.15)
        
        # Normalize weights
        total_weight = self.semantic_weight + self.level_weight + self.context_weight
        self.semantic_weight /= total_weight
        self.level_weight /= total_weight
        self.context_weight /= total_weight
        
        logger.info(f"Multi-factor weights - Semantic: {self.semantic_weight:.2f}, "
                   f"Level: {self.level_weight:.2f}, Context: {self.context_weight:.2f}")
        
        self.scorer = UnifiedScorer()
        self.similarity_method = config['embedding'].get('similarity_method', 'faiss')
        self.device = config['embedding']['device']
        
        self.model = ModelFactory.create_embedding_interface(config)
        
        # Initialize caches
        self.embedding_cache = {}
        self.faiss_index = None
        self.similarity_matrix = None
        self.embeddings_for_matrix = None
        
        # Metadata arrays
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
        
        all_embeddings = []
        
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Generating embeddings"):
            batch_texts = texts[i:i + self.batch_size]
            batch_embeddings = self.model.encode(
                batch_texts,
                batch_size=self.batch_size,
                convert_to_tensor=False,
                show_progress=False,
                normalize_embeddings=self.config['embedding']['normalize_embeddings']
            )
            
            all_embeddings.append(batch_embeddings)
            
            if i % (self.batch_size * 10) == 0 and self.device == 'cuda':
                torch.cuda.empty_cache()
        
        embeddings = np.vstack(all_embeddings).astype(np.float32)
        
        if use_cache and cache_key:
            self._save_cached_embeddings(embeddings, cache_key)
        
        return embeddings
    
    def generate_embeddings_for_dataframe(self, 
                                         df: pd.DataFrame,
                                         text_column: str = 'combined_text') -> np.ndarray:
        """Generate embeddings and pre-process metadata"""
        if all(col in df.columns for col in ['level', 'context']):
            self.levels_array = self._vectorize_levels(df['level'].values)
            self.contexts_array, self.context_indices = self._vectorize_contexts(df['context'].values)
            
            logger.info("Pre-processed metadata for vectorized multi-factor matching")
        
        cache_key = self._create_cache_key(df, text_column)
        texts = df[text_column].tolist()
        embeddings = self.generate_embeddings(texts, cache_key=cache_key)
        
        return embeddings
    
    def _vectorize_levels(self, levels) -> np.ndarray:
        """Vectorize level values"""
        vectorized = np.zeros(len(levels), dtype=np.int32)
        
        for i, level in enumerate(levels):
            if hasattr(level, 'value'):
                vectorized[i] = level.value
            else:
                try:
                    vectorized[i] = int(level)
                except:
                    vectorized[i] = 3
        
        return np.clip(vectorized, 1, 7)
    
    def _vectorize_contexts(self, contexts) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorize context values"""
        context_strings = np.array([
            str(c).lower() if not hasattr(c, 'value') else c.value 
            for c in contexts
        ])
        
        context_indices = np.zeros(len(contexts), dtype=np.int32)
        context_indices[context_strings == 'practical'] = 0
        context_indices[context_strings == 'theoretical'] = 1
        context_indices[context_strings == 'hybrid'] = 2
        
        unknown_mask = ~np.isin(context_strings, ['practical', 'theoretical', 'hybrid'])
        context_indices[unknown_mask] = 2
        
        return context_strings, context_indices
    
    def calculate_multi_factor_similarity(self, 
                                         embeddings1: np.ndarray,
                                         embeddings2: np.ndarray,
                                         metadata1: Optional[pd.DataFrame] = None,
                                         metadata2: Optional[pd.DataFrame] = None) -> np.ndarray:
        """Fully vectorized multi-factor similarity calculation"""
        n1, n2 = len(embeddings1), len(embeddings2)
        semantic_sim = self.model.similarity(embeddings1, embeddings2)
        
        if metadata1 is None or metadata2 is None:
            return semantic_sim.astype(np.float32)
        
        if 'level' in metadata1.columns and 'level' in metadata2.columns:
            levels1 = self._vectorize_levels(metadata1['level'].values)
            levels2 = self._vectorize_levels(metadata2['level'].values)
            level_compat = self.scorer.get_vectorized_level_compatibility(levels1, levels2)
        else:
            level_compat = np.ones((n1, n2), dtype=np.float32)
        
        if 'context' in metadata1.columns and 'context' in metadata2.columns:
            _, ctx_idx1 = self._vectorize_contexts(metadata1['context'].values)
            _, ctx_idx2 = self._vectorize_contexts(metadata2['context'].values)
            context_compat = self.scorer.get_vectorized_context_compatibility(ctx_idx1, ctx_idx2)
        else:
            context_compat = np.ones((n1, n2), dtype=np.float32)
        
        combined_similarity = (
            semantic_sim * self.semantic_weight +
            level_compat * self.level_weight +
            context_compat * self.context_weight
        ).astype(np.float32)
        
        return combined_similarity
    
    def build_similarity_index(self, embeddings: np.ndarray, index_type: str = "IVF1024,Flat"):
        """Build similarity index"""
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
            if self.levels_array is not None and self.contexts_array is not None:
                metadata = pd.DataFrame({
                    'level': self.levels_array,
                    'context': self.contexts_array
                })
                self.similarity_matrix = self.calculate_multi_factor_similarity(
                    embeddings, embeddings, metadata, metadata
                )
            else:
                if self.config['embedding']['normalize_embeddings']:
                    self.similarity_matrix = np.dot(embeddings, embeddings.T)
                else:
                    self.similarity_matrix = cosine_similarity(embeddings)
            
            logger.info(f"Similarity matrix computed: {self.similarity_matrix.shape}")
        else:
            logger.info(f"Large dataset ({n_samples} samples) - using batch computation")
            self.similarity_matrix = self._calculate_multi_factor_similarity_batch(embeddings)
    
    def _calculate_multi_factor_similarity_batch(self, embeddings: np.ndarray, 
                                                  batch_size: int = 1000) -> np.ndarray:
        """Calculate self-similarity matrix in batches"""
        n = len(embeddings)
        similarity_matrix = np.zeros((n, n), dtype=np.float32)
        
        for i in tqdm(range(0, n, batch_size), desc="Computing similarity matrix"):
            end_i = min(i + batch_size, n)
            
            for j in range(i, n, batch_size):
                end_j = min(j + batch_size, n)
                
                block = self._compute_similarity_block(
                    embeddings[i:end_i],
                    embeddings[j:end_j],
                    i, end_i, j, end_j
                )
                
                similarity_matrix[i:end_i, j:end_j] = block
                if i != j:
                    similarity_matrix[j:end_j, i:end_i] = block.T
        
        return similarity_matrix
    
    def _compute_similarity_block(self, emb1: np.ndarray, emb2: np.ndarray,
                                   i_start: int, i_end: int, j_start: int, j_end: int) -> np.ndarray:
        """Compute a single block of the similarity matrix"""
        if self.config['embedding']['normalize_embeddings']:
            semantic_block = np.dot(emb1, emb2.T)
        else:
            semantic_block = cosine_similarity(emb1, emb2)
        
        if self.levels_array is not None:
            levels1 = self.levels_array[i_start:i_end]
            levels2 = self.levels_array[j_start:j_end]
            level_block = self.scorer.get_vectorized_level_compatibility(levels1, levels2)
        else:
            level_block = np.ones_like(semantic_block)
        
        if self.context_indices is not None:
            ctx1 = self.context_indices[i_start:i_end]
            ctx2 = self.context_indices[j_start:j_end]
            context_block = self.scorer.get_vectorized_context_compatibility(ctx1, ctx2)
        else:
            context_block = np.ones_like(semantic_block)
        
        return (
            semantic_block * self.semantic_weight +
            level_block * self.level_weight +
            context_block * self.context_weight
        ).astype(np.float32)
    
    def _build_faiss_index(self, embeddings: np.ndarray, index_type: str = "IVF1024,Flat"):
        """Build FAISS index"""
        logger.info(f"Building FAISS index for {len(embeddings)} embeddings")
        
        n_samples = len(embeddings)
        embeddings = embeddings.astype(np.float32)
        embedding_dim = embeddings.shape[1]
        
        if n_samples < 1024:
            if self.config['embedding']['normalize_embeddings']:
                self.faiss_index = faiss.IndexFlatIP(embedding_dim)
            else:
                self.faiss_index = faiss.IndexFlatL2(embedding_dim)
        else:
            nlist = min(1024, n_samples // 50)
            
            if self.config['embedding']['normalize_embeddings']:
                quantizer = faiss.IndexFlatIP(embedding_dim)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, embedding_dim, nlist, faiss.METRIC_INNER_PRODUCT
                )
            else:
                quantizer = faiss.IndexFlatL2(embedding_dim)
                self.faiss_index = faiss.IndexIVFFlat(
                    quantizer, embedding_dim, nlist
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
        """Vectorized batch search"""
        if self.similarity_method == 'matrix':
            return self._find_similar_matrix_vectorized(query_indices, k, threshold)
        else:
            return self._find_similar_faiss_vectorized(query_indices, k, threshold)
    
    def _find_similar_matrix_vectorized(self, query_indices: np.ndarray, k: int = 10,
                                        threshold: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized similarity search using precomputed matrix"""
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix not built")
        
        similarities = self.similarity_matrix[query_indices]
        
        if k >= similarities.shape[1]:
            indices = np.argsort(similarities, axis=1)[:, ::-1]
            distances = np.take_along_axis(similarities, indices, axis=1)
        else:
            top_k_indices = np.argpartition(-similarities, k, axis=1)[:, :k]
            top_k_values = np.take_along_axis(similarities, top_k_indices, axis=1)
            sorted_idx = np.argsort(-top_k_values, axis=1)
            
            indices = np.take_along_axis(top_k_indices, sorted_idx, axis=1)
            distances = np.take_along_axis(top_k_values, sorted_idx, axis=1)
        
        if threshold is not None:
            mask = distances >= threshold
            indices[~mask] = -1
            distances[~mask] = -1
        
        return distances, indices
    
    def _find_similar_faiss_vectorized(self, query_indices: np.ndarray, k: int = 10,
                                       threshold: Optional[float] = None) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized FAISS search"""
        if self.faiss_index is None:
            raise ValueError("FAISS index not built")
        
        query_embeddings = self.embeddings_for_matrix[query_indices].astype(np.float32)
        k_search = min(k * 3, self.faiss_index.ntotal)
        
        distances, indices = self.faiss_index.search(query_embeddings, k_search)
        
        if self.levels_array is not None and self.context_indices is not None:
            distances = self._rescore_with_multi_factor_vectorized(
                query_indices, indices, distances
            )
            
            sorted_idx = np.argsort(-distances, axis=1)[:, :k]
            indices = np.take_along_axis(indices, sorted_idx, axis=1)[:, :k]
            distances = np.take_along_axis(distances, sorted_idx, axis=1)[:, :k]
        else:
            indices = indices[:, :k]
            distances = distances[:, :k]
        
        if threshold is not None:
            mask = distances >= threshold
            indices[~mask] = -1
            distances[~mask] = -1
        
        return distances, indices
    
    def _rescore_with_multi_factor_vectorized(self, query_indices: np.ndarray,
                                              candidate_indices: np.ndarray,
                                              semantic_scores: np.ndarray) -> np.ndarray:
        """Vectorized multi-factor rescoring"""
        n_queries, k_candidates = candidate_indices.shape
        
        query_levels = self.levels_array[query_indices]
        query_contexts = self.context_indices[query_indices]
        
        rescored = np.zeros_like(semantic_scores)
        
        for i in range(n_queries):
            valid_mask = candidate_indices[i] >= 0
            valid_candidates = candidate_indices[i][valid_mask]
            
            if len(valid_candidates) > 0:
                candidate_levels = self.levels_array[valid_candidates]
                
                level_compat = self.scorer.level_compatibility_matrix[
                    np.clip(query_levels[i] - 1, 0, 6),
                    np.clip(candidate_levels - 1, 0, 6)
                ]
                
                candidate_contexts = self.context_indices[valid_candidates]
                
                context_compat = self.scorer.context_compatibility_matrix[
                    query_contexts[i],
                    candidate_contexts
                ]
                
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


class EmbeddingManager(OptimizedEmbeddingManager):
    """Backward compatible class name"""
    pass


class SimilarityDeduplicator:
    """
    Deduplication with alternative title tracking
    Tracks duplicate skill names as alternative titles for the master skill
    Also aggregates keywords and codes from duplicates
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.similarity_threshold = config['dedup']['similarity_threshold']
        self.fuzzy_threshold = config['dedup']['fuzzy_ratio_threshold']
        
        self.direct_threshold = config['dedup'].get('direct_match_threshold', 0.9)
        self.partial_threshold = config['dedup'].get('partial_threshold', 0.8)
        
        logger.info(f"Deduplication thresholds - Direct: {self.direct_threshold}, "
                   f"Partial: {self.partial_threshold}, Min: {self.similarity_threshold}")
    
    def find_duplicates(self, 
                       df: pd.DataFrame, 
                       embeddings: np.ndarray,
                       embedding_manager: EmbeddingManager) -> pd.DataFrame:
        """
        Find duplicate skills using multi-factor similarity
        Now tracks alternative titles from duplicates
        """
        logger.info(f"Finding duplicates among {len(df)} skills")
        
        if embedding_manager.similarity_method == 'matrix':
            if embedding_manager.embeddings_for_matrix is None:
                embedding_manager.build_similarity_index(embeddings)
        else:
            if embedding_manager.faiss_index is None:
                embedding_manager.build_similarity_index(embeddings)
        
        if embedding_manager.embeddings_for_matrix is None:
            embedding_manager.embeddings_for_matrix = embeddings
        
        batch_size = min(100, len(df))
        duplicate_groups = []
        processed_indices = set()
        duplicate_details = []
        
        all_indices = np.arange(len(df))
        
        for batch_start in tqdm(range(0, len(df), batch_size), desc="Finding duplicates"):
            batch_end = min(batch_start + batch_size, len(df))
            batch_indices = all_indices[batch_start:batch_end]
            
            batch_indices = [idx for idx in batch_indices if idx not in processed_indices]
            if not batch_indices:
                continue
            
            batch_indices = np.array(batch_indices)
            
            distances, indices = embedding_manager.find_similar_skills_vectorized(
                batch_indices,
                k=20,
                threshold=self.similarity_threshold
            )
            
            for i, query_idx in enumerate(batch_indices):
                if query_idx in processed_indices:
                    continue
                
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
                            'type': 'direct',
                            'name': df.iloc[idx]['name'],  # Track name for alternative title
                            'code': df.iloc[idx].get('code', ''),  # Track code
                            'keywords': df.iloc[idx].get('keywords', [])  # Track keywords
                        })
                    elif score >= self.partial_threshold:
                        if self._check_level_compatibility(df.iloc[query_idx], df.iloc[idx]):
                            similar_indices.append(idx)
                            match_classifications.append({
                                'index': idx,
                                'score': float(score),
                                'type': 'partial',
                                'name': df.iloc[idx]['name'],  # Track name for alternative title
                                'code': df.iloc[idx].get('code', ''),  # Track code
                                'keywords': df.iloc[idx].get('keywords', [])  # Track keywords
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
        
        logger.info(f"Found {len(duplicate_groups)} duplicate groups")
        
        # Add duplicate information to dataframe
        df_result = df.copy()
        df_result['duplicate_group'] = -1
        df_result['is_duplicate'] = False
        df_result['master_skill_id'] = df_result['skill_id']
        df_result['match_type'] = 'none'
        df_result['match_score'] = 0.0
        df_result['alternative_titles'] = None  # Track alternative titles
        
        for group_id, (group, details) in enumerate(zip(duplicate_groups, duplicate_details)):
            master_idx = self._select_master_skill(df, group, details)
            master_skill_id = df.loc[master_idx, 'skill_id']
            master_name = df.loc[master_idx, 'name']
            
            # Update master_idx in details
            old_master_idx = details['master_idx']
            details['master_idx'] = master_idx
            for i, match in enumerate(details['matches']):
                if match['index'] == master_idx:
                    details['matches'][i]['index'] = old_master_idx
                    details['matches'][i]['name'] = df.iloc[old_master_idx]['name']
                    details['matches'][i]['code'] = df.iloc[old_master_idx].get('code', '')
                    details['matches'][i]['keywords'] = df.iloc[old_master_idx].get('keywords', [])
            
            # Collect alternative titles (names of duplicate skills)
            alternative_titles = []
            for idx in group:
                if idx != master_idx:
                    alt_name = df.iloc[idx]['name']
                    if alt_name != master_name and alt_name not in alternative_titles:
                        alternative_titles.append(alt_name)
            
            # Mark duplicates and set alternative titles
            for idx in group:
                df_result.loc[idx, 'duplicate_group'] = group_id
                df_result.loc[idx, 'is_duplicate'] = (idx != master_idx)
                df_result.loc[idx, 'master_skill_id'] = master_skill_id
                
                if idx == master_idx:
                    # Master skill gets the alternative titles
                    df_result.at[idx, 'alternative_titles'] = alternative_titles
                else:
                    match_info = next((m for m in details['matches'] if m['index'] == idx), None)
                    if match_info:
                        df_result.loc[idx, 'match_type'] = match_info['type']
                        df_result.loc[idx, 'match_score'] = match_info['score']
        
        self._log_deduplication_stats(df_result)
        
        return df_result
    
    def _check_level_compatibility(self, skill1: pd.Series, skill2: pd.Series) -> bool:
        """Check if two skills have compatible levels"""
        if 'level' not in skill1 or 'level' not in skill2:
            return True
        
        level1 = self._extract_level_value(skill1['level'])
        level2 = self._extract_level_value(skill2['level'])
        
        return abs(level1 - level2) <= 1
    
    def _extract_level_value(self, level) -> int:
        """Extract numeric level value"""
        if isinstance(level, (int, float, np.int64, np.float64)):
            return int(level)
        elif hasattr(level, 'value'):
            return level.value
        else:
            return 3
    
    def _select_master_skill(self, df: pd.DataFrame, group: List[int], details: Dict) -> int:
        """Select the master skill from a duplicate group"""
        group_df = df.iloc[group].copy()
        group_df['_group_idx'] = group
        
        for idx, row in group_df.iterrows():
            confidence = row.get('confidence', 0.0)
            level = self._extract_level_value(row.get('level', -1))
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
        
        # Count alternative titles
        alt_titles_count = df['alternative_titles'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum()
        
        logger.info("=" * 60)
        logger.info("DEDUPLICATION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total skills: {len(df)}")
        logger.info(f"Duplicate skills found: {total_duplicates}")
        logger.info(f"  - Direct matches: {direct_matches}")
        logger.info(f"  - Partial matches: {partial_matches}")
        logger.info(f"Unique skills after dedup: {len(df) - total_duplicates}")
        logger.info(f"Duplicate groups: {df[df['duplicate_group'] >= 0]['duplicate_group'].nunique()}")
        logger.info(f"Alternative titles tracked: {alt_titles_count}")
    
    def _extract_keywords_list(self, keywords) -> List[str]:
        """Safely extract keywords as a list"""
        if isinstance(keywords, list):
            return list(keywords)
        elif pd.notna(keywords) and keywords != '':
            if isinstance(keywords, str):
                try:
                    import json
                    parsed = json.loads(keywords.replace("'", '"'))
                    if isinstance(parsed, list):
                        return parsed
                except:
                    pass
                import re
                return [k.strip() for k in re.split(r',|;|\||\n', keywords) if k.strip()]
            return [str(keywords)]
        return []
    
    def _extract_code_list(self, code) -> List[str]:
        """Safely extract code as a list"""
        if isinstance(code, list):
            return list(code)
        elif pd.notna(code) and code != '':
            return [str(code)]
        return []
    
    def merge_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge duplicate skills intelligently
        Preserves alternative titles from duplicates
        Aggregates keywords and codes from duplicates into all_related_kw and all_related_codes
        """
        # Keep non-duplicates
        unique_df = df[~df['is_duplicate']].copy()
        
        # For duplicate groups, merge information
        duplicate_groups = df[df['duplicate_group'] >= 0].groupby('duplicate_group')
        
        for group_id, group_df in duplicate_groups:
            if len(group_df) > 1:
                master_idx = group_df[~group_df['is_duplicate']].index[0]
                
                # Keep best description
                best_description = group_df.loc[group_df['description_length'].idxmax(), 'description']
                unique_df.loc[master_idx, 'description'] = best_description
                
                # Keep best keywords
                best_keywords = group_df.loc[group_df['description_length'].idxmax(), 'keywords']
                unique_df.loc[master_idx, 'keywords'] = best_keywords
                
                # Keep highest level
                if 'level' in group_df.columns:
                    levels = [self._extract_level_value(level) for level in group_df['level']]
                    max_level_idx = group_df.index[levels.index(max(levels))]
                    unique_df.loc[master_idx, 'level'] = group_df.loc[max_level_idx, 'level']
                
                # Update combined text
                unique_df.loc[master_idx, 'combined_text'] = (
                    unique_df.loc[master_idx, 'name'] + '. ' +
                    best_description
                )
                
                # Ensure alternative titles are preserved and complete
                all_alt_titles = []
                master_name = unique_df.loc[master_idx, 'name']
                
                # Get existing alternative titles
                existing_alts = unique_df.loc[master_idx, 'alternative_titles']
                if isinstance(existing_alts, list):
                    all_alt_titles.extend(existing_alts)
                
                # Add any missed names from the group
                for idx, row in group_df.iterrows():
                    if idx != master_idx:
                        name = row['name']
                        if name != master_name and name not in all_alt_titles:
                            all_alt_titles.append(name)
                
                # Remove duplicates and store
                unique_df.at[master_idx, 'alternative_titles'] = list(set(all_alt_titles))
                
                # ============================================================
                # AGGREGATE keywords and codes from duplicates
                # ============================================================
                
                # Collect all keywords from the group
                all_keywords = []
                existing_kw = unique_df.at[master_idx, 'all_related_kw'] if 'all_related_kw' in unique_df.columns else []
                if isinstance(existing_kw, list):
                    all_keywords.extend(existing_kw)
                
                for idx, row in group_df.iterrows():
                    # Get keywords from each skill in the group
                    skill_kw = self._extract_keywords_list(row.get('keywords', []))
                    all_keywords.extend(skill_kw)
                    
                    # Also get from all_related_kw if present
                    if 'all_related_kw' in row and isinstance(row.get('all_related_kw'), list):
                        all_keywords.extend(row['all_related_kw'])
                
                # Remove duplicates while preserving order
                seen_kw = set()
                unique_keywords = []
                for kw in all_keywords:
                    if kw and kw not in seen_kw:
                        seen_kw.add(kw)
                        unique_keywords.append(kw)
                
                unique_df.at[master_idx, 'all_related_kw'] = unique_keywords
                
                # Collect all codes from the group
                all_codes = []
                existing_codes = unique_df.at[master_idx, 'all_related_codes'] if 'all_related_codes' in unique_df.columns else []
                if isinstance(existing_codes, list):
                    all_codes.extend(existing_codes)
                
                for idx, row in group_df.iterrows():
                    # Get code from each skill in the group
                    skill_code = self._extract_code_list(row.get('code', ''))
                    all_codes.extend(skill_code)
                    
                    # Also get from all_related_codes if present
                    if 'all_related_codes' in row and isinstance(row.get('all_related_codes'), list):
                        all_codes.extend(row['all_related_codes'])
                
                # Remove duplicates while preserving order
                seen_codes = set()
                unique_codes = []
                for code in all_codes:
                    if code and code not in seen_codes:
                        seen_codes.add(code)
                        unique_codes.append(code)
                
                unique_df.at[master_idx, 'all_related_codes'] = unique_codes
                
                # Add metadata
                unique_df.at[master_idx, 'merged_from'] = [[id_] for id_ in group_df['skill_id'].tolist()]
                unique_df.loc[master_idx, 'merge_count'] = len(group_df)
        
        logger.info(f"Reduced {len(df)} skills to {len(unique_df)} unique skills")
        
        # Count total alternative titles
        total_alt_titles = unique_df['alternative_titles'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum()
        logger.info(f"Total alternative titles preserved: {total_alt_titles}")
        
        # Log aggregation statistics
        if 'all_related_kw' in unique_df.columns:
            total_kw = unique_df['all_related_kw'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            logger.info(f"Total aggregated keywords after merge: {total_kw}")
        
        if 'all_related_codes' in unique_df.columns:
            total_codes = unique_df['all_related_codes'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            logger.info(f"Total aggregated codes after merge: {total_codes}")
        
        return unique_df.reset_index(drop=True)