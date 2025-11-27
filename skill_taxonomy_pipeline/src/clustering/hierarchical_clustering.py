"""
Enhanced Clustering module with multi-factor skill matching
Incorporates semantic similarity, skill levels, and context for better taxonomy clustering
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple, Union
import logging
from tqdm import tqdm
import hdbscan
import umap
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from collections import Counter
import pickle
from pathlib import Path
from src.clustering.clustering_algo import GridSearchSkillsClusterer
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)


class MultiFactorClusterer:
    """
    Performs hierarchical clustering on skills using multi-factor similarity
    Considers semantic similarity, skill levels, and context
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.min_cluster_size = config['clustering']['min_cluster_size']
        self.min_samples = config['clustering']['min_samples']
        self.metric = config['clustering']['metric']
        self.use_umap = config['clustering']['use_umap_reduction']
        self.cache_dir = Path(config['paths']['cache_dir']) / "clustering"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Multi-factor weights
        self.semantic_weight = config.get('semantic_weight', 0.6)
        self.level_weight = config.get('level_weight', 0.25)
        self.context_weight = config.get('context_weight', 0.15)
        
        # Normalize weights
        total_weight = self.semantic_weight + self.level_weight + self.context_weight
        self.semantic_weight /= total_weight
        self.level_weight /= total_weight
        self.context_weight /= total_weight
        
        logger.info(f"Multi-factor clustering weights - Semantic: {self.semantic_weight:.2f}, "
                   f"Level: {self.level_weight:.2f}, Context: {self.context_weight:.2f}")
        
        self.clusterer = None
        self.reduced_embeddings = None
        self.umap_model = None
        self.skills_metadata = None
    
    def prepare_multi_factor_features(self, 
                                     df: pd.DataFrame, 
                                     embeddings: np.ndarray) -> np.ndarray:
        """
        Prepare features for clustering that incorporate multiple factors
        
        Args:
            df: DataFrame with skill information including level and context
            embeddings: Semantic embeddings for skills
            
        Returns:
            Enhanced feature matrix for clustering
        """
        logger.info("Preparing multi-factor features for clustering")
        
        n_skills = len(df)
        n_features = embeddings.shape[1]
        
        # Store metadata for later use
        self.skills_metadata = df.copy()
        
        # 1. Normalize semantic embeddings if needed
        if not self.config['embedding'].get('normalize_embeddings', True):
            semantic_features = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        else:
            semantic_features = embeddings.copy()
        
        # 2. Create level features (one-hot encoding with smoothing)
        level_features = self._create_level_features(df)
        
        # 3. Create context features (one-hot encoding)
        context_features = self._create_context_features(df)
        
        # 4. Weight and combine features
        # Scale features to similar ranges
        level_features_scaled = level_features * 2.0  # Boost level importance
        context_features_scaled = context_features * 1.5  # Moderate context importance
        
        # Combine with weights
        enhanced_features = np.hstack([
            semantic_features * self.semantic_weight,
            level_features_scaled * self.level_weight,
            context_features_scaled * self.context_weight
        ])
        
        logger.info(f"Enhanced feature shape: {enhanced_features.shape}")
        
        return enhanced_features
    
    def _create_level_features(self, df: pd.DataFrame) -> np.ndarray:
        """
        Create level-based features with proximity encoding
        Skills with similar levels get similar representations
        """
        n_skills = len(df)
        level_features = np.zeros((n_skills, 7))  # 7 SFIA levels
        
        if 'level' in df.columns:
            for idx, row in df.iterrows():
                level = self._extract_level_value(row['level'])
                # Use gaussian-like distribution around the level
                for l in range(1, 8):
                    distance = abs(l - level)
                    if distance == 0:
                        level_features[idx, l-1] = 1.0
                    elif distance == 1:
                        level_features[idx, l-1] = 0.5
                    elif distance == 2:
                        level_features[idx, l-1] = 0.25
        else:
            # No level info, use uniform
            raise Exception("'level' column is required for multi-factor matching but not found.")
        
        return level_features
    
    def _create_context_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create context-based features"""
        n_skills = len(df)
        context_features = np.zeros((n_skills, 3))  # practical, theoretical, hybrid
        
        if 'context' in df.columns:
            context_map = {'practical': 0, 'theoretical': 1, 'hybrid': 2}
            for idx, row in df.iterrows():
                context = self._extract_context_value(row['context'])
                context_idx = context_map.get(context, 2)  # Default to hybrid
                context_features[idx, context_idx] = 1.0
                
                # Add partial weights for hybrid
                if context == 'hybrid':
                    context_features[idx, 0] = 0.5  # Part practical
                    context_features[idx, 1] = 0.5  # Part theoretical
        else:
            # No context info, assume hybrid
            context_features[:, 2] = 1.0
        
        return context_features
    
    def _extract_level_value(self, level) -> int:
        """Extract numeric level value from various formats"""
        if isinstance(level, (int, float, np.int64, np.float64)):
            return int(np.clip(level, 1, 7))
        elif hasattr(level, 'value'):  # Enum
            return level.value
        elif isinstance(level, str):
            try:
                return int(''.join(filter(str.isdigit, level)))
            except:
                raise ValueError(f"Invalid level value: {level}")
        else:
            raise ValueError(f"Invalid level value: {level}")
    
    def _extract_context_value(self, context) -> str:
        """Extract context string from various formats"""
        if isinstance(context, str):
            return context.lower()
        elif hasattr(context, 'value'):  # Enum
            return context.value
        else:
            raise ValueError(f"Invalid context value: {context}")
    
    def cluster_skills(self, 
                      df: pd.DataFrame, 
                      embeddings: np.ndarray,
                      category: Optional[str] = None) -> pd.DataFrame:
        """
        Perform hierarchical clustering on skills using multi-factor features
        
        Args:
            df: DataFrame with skill information
            embeddings: Semantic embeddings
            category: Optional category filter
            
        Returns:
            DataFrame with cluster assignments
        """
        if category:
            mask = df['category'] == category
            df_subset = df[mask].copy()
            embeddings_subset = embeddings[mask]
            logger.info(f"Clustering {len(df_subset)} skills in category: {category}")
        else:
            df_subset = df.copy()
            embeddings_subset = embeddings
            logger.info(f"Clustering all {len(df_subset)} skills")
        
        # Prepare multi-factor features
        enhanced_features = embeddings_subset# self.prepare_multi_factor_features(df_subset, embeddings_subset)
        
        
        
        # Reduce dimensionality if needed
        # if self.use_umap and enhanced_features.shape[0] > 5000:
        #     reduced_features = self._reduce_dimensions(enhanced_features)
        # else:
        #     reduced_features = enhanced_features
        
        # # Perform clustering
        # cluster_labels = self._perform_hdbscan(reduced_features)
        
        grid_clusterer = GridSearchSkillsClusterer(memory_limit_gb=10,
                                                      batch_size=256,
                                                      embedding_models=["Auto"],
                                                      embedders={"Auto": enhanced_features},
                                                      clustering_algorithms=['kmeans'])
        cluster_labels = grid_clusterer.grid_search_clustering(skills=df['combined_text'].values.tolist(), embeddings_available=True)
        
        # Add cluster information
        df_subset['cluster_id'] = cluster_labels
        # df_subset['cluster_probability'] = self.clusterer.probabilities_
        
        # Generate cluster statistics with level and context analysis
        cluster_stats = self._generate_enhanced_cluster_stats(df_subset, embeddings_subset)
        
        # Add cluster metadata
        df_subset = self._add_cluster_metadata(df_subset, cluster_stats)
        
        # Post-process clusters for better coherence
        df_subset = self._post_process_clusters(df_subset, embeddings_subset, cluster_stats)
        
        return df_subset
    
    def _reduce_dimensions(self, features: np.ndarray) -> np.ndarray:
        """
        Reduce dimensions using UMAP with appropriate metric
        """
        logger.info(f"Reducing dimensions from {features.shape[1]} using UMAP")
        
        # First apply PCA for initial reduction if dimensions are very high
        if features.shape[1] > 200:
            logger.info("Applying PCA for initial dimension reduction")
            pca = PCA(n_components=100, random_state=42)
            features = pca.fit_transform(features)
        
        # Apply UMAP
        self.umap_model = umap.UMAP(
            n_components=self.config['clustering']['umap_n_components'],
            n_neighbors=self.config['clustering']['umap_n_neighbors'],
            min_dist=self.config['clustering']['umap_min_dist'],
            metric='euclidean',  # Use euclidean for mixed features
            random_state=42,
            n_jobs=1,
            verbose=False
        )
        
        reduced_features = self.umap_model.fit_transform(features)
        self.reduced_embeddings = reduced_features
        
        logger.info(f"Dimension reduction complete: {reduced_features.shape}")
        
        return reduced_features
    
    def _perform_hdbscan(self, features: np.ndarray) -> np.ndarray:
        """Perform HDBSCAN clustering on multi-factor features"""
        logger.info("Performing HDBSCAN clustering on multi-factor features")
        
        n_samples = len(features)
        min_cluster_size = max(self.min_cluster_size, int(n_samples * 0.001))
        min_samples = min(self.min_samples, min_cluster_size // 2)
        
        logger.info(f"HDBSCAN parameters: min_cluster_size={min_cluster_size}, min_samples={min_samples}")
        
        self.clusterer = hdbscan.HDBSCAN(
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            metric='euclidean',
            cluster_selection_epsilon=self.config['clustering']['cluster_selection_epsilon'],
            alpha=self.config['clustering']['alpha'],
            cluster_selection_method='eom',
            prediction_data=True,
            core_dist_n_jobs=1
        )
        
        cluster_labels = self.clusterer.fit_predict(features)
        
        # Log clustering results
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        
        logger.info(f"Found {n_clusters} clusters")
        logger.info(f"Noise points: {n_noise} ({100*n_noise/n_samples:.1f}%)")
        
        return cluster_labels
    
    def _generate_enhanced_cluster_stats(self, 
                                        df: pd.DataFrame, 
                                        embeddings: np.ndarray) -> Dict:
        """
        Generate statistics for each cluster including level and context distribution
        """
        cluster_stats = {}
        
        for cluster_id in sorted(df['cluster_id'].unique()):
            if cluster_id == -1:  # Skip noise points
                continue
            
            cluster_mask = df['cluster_id'] == cluster_id
            cluster_df = df[cluster_mask]
            cluster_embeddings = embeddings[cluster_mask]
            
            # Calculate cluster center
            cluster_center = np.mean(cluster_embeddings, axis=0)
            
            # Calculate intra-cluster similarity
            if len(cluster_embeddings) > 1:
                distances = np.linalg.norm(cluster_embeddings - cluster_center, axis=1)
                avg_distance = np.mean(distances)
                std_distance = np.std(distances)
            else:
                avg_distance = 0
                std_distance = 0
            
            # Get level statistics
            level_stats = self._calculate_level_stats(cluster_df)
            
            # Get context statistics
            context_stats = self._calculate_context_stats(cluster_df)
            
            # Get most common keywords
            all_keywords = []
            for keywords in cluster_df['keywords']:
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
            keyword_counts = Counter(all_keywords)
            top_keywords = [k for k, _ in keyword_counts.most_common(10)]
            
            cluster_stats[cluster_id] = {
                'size': len(cluster_df),
                'center': cluster_center,
                'avg_distance': float(avg_distance),
                'std_distance': float(std_distance),
                'cohesion': float(1 / (1 + avg_distance)),
                'top_keywords': top_keywords,
                'level_stats': level_stats,
                'context_stats': context_stats,
                'avg_confidence': float(cluster_df['confidence'].mean()),
                'coherence_score': self._calculate_cluster_coherence(cluster_df, level_stats, context_stats)
            }
        
        return cluster_stats
    
    def _calculate_level_stats(self, cluster_df: pd.DataFrame) -> Dict:
        """Calculate level distribution statistics for a cluster"""
        if 'level' not in cluster_df.columns:
            return {}
        
        levels = [self._extract_level_value(l) for l in cluster_df['level']]
        
        return {
            'mean_level': np.mean(levels),
            'std_level': np.std(levels),
            'min_level': min(levels),
            'max_level': max(levels),
            'level_range': max(levels) - min(levels),
            'level_distribution': Counter(levels),
            'dominant_level': Counter(levels).most_common(1)[0][0] if levels else -1
        }
    
    def _calculate_context_stats(self, cluster_df: pd.DataFrame) -> Dict:
        """Calculate context distribution statistics for a cluster"""
        if 'context' not in cluster_df.columns:
            return {}
        
        contexts = [self._extract_context_value(c) for c in cluster_df['context']]
        context_counts = Counter(contexts)
        
        return {
            'context_distribution': dict(context_counts),
            'dominant_context': context_counts.most_common(1)[0][0] if contexts else 'None',
            'context_diversity': len(set(contexts)) / 3.0  # Normalized by max contexts
        }
    
    def _calculate_cluster_coherence(self, 
                                    cluster_df: pd.DataFrame,
                                    level_stats: Dict,
                                    context_stats: Dict) -> float:
        """
        Calculate overall coherence score for a cluster
        Higher coherence means skills in cluster are more similar
        """
        coherence = 1.0
        
        # Penalize high level variance
        if level_stats and 'std_level' in level_stats:
            level_penalty = min(level_stats['std_level'] / 2.0, 0.5)
            coherence -= level_penalty
        
        # Penalize mixed contexts
        if context_stats and 'context_diversity' in context_stats:
            context_penalty = (context_stats['context_diversity'] - 0.33) * 0.3
            coherence -= max(0, context_penalty)
        
        return max(0.0, coherence)
    
    def _add_cluster_metadata(self, df: pd.DataFrame, cluster_stats: Dict) -> pd.DataFrame:
        """Add enhanced cluster metadata to dataframe"""
        df['cluster_size'] = df['cluster_id'].map(
            lambda x: cluster_stats.get(x, {}).get('size', 1) if x != -1 else 1
        )
        
        df['cluster_cohesion'] = df['cluster_id'].map(
            lambda x: cluster_stats.get(x, {}).get('cohesion', 0) if x != -1 else 0
        )
        
        df['cluster_coherence'] = df['cluster_id'].map(
            lambda x: cluster_stats.get(x, {}).get('coherence_score', 0) if x != -1 else 0
        )
        
        df['cluster_level'] = df['cluster_id'].map(
            lambda x: cluster_stats.get(x, {}).get('level_stats', {}).get('dominant_level', 3) if x != -1 else -1
        )
        
        df['cluster_context'] = df['cluster_id'].map(
            lambda x: cluster_stats.get(x, {}).get('context_stats', {}).get('dominant_context', 'hybrid') if x != -1 else 'None'
        )
        
        df['is_noise'] = df['cluster_id'] == -1
        
        return df
    
    def _post_process_clusters(self, 
                              df: pd.DataFrame, 
                              embeddings: np.ndarray,
                              cluster_stats: Dict) -> pd.DataFrame:
        """
        Post-process clusters to improve coherence
        - Split clusters with high level variance
        - Merge small clusters with similar characteristics
        """
        logger.info("Post-processing clusters for better coherence")
        
        # Split clusters with high level variance
        clusters_to_split = []
        for cluster_id, stats in cluster_stats.items():
            if cluster_id == -1:
                continue
            
            level_stats = stats.get('level_stats', {})
            if level_stats.get('level_range', 0) > 2:  # More than 2 levels difference
                clusters_to_split.append(cluster_id)
        
        if clusters_to_split:
            logger.info(f"Splitting {len(clusters_to_split)} clusters with high level variance")
            df = self._split_clusters_by_level(df, embeddings, clusters_to_split)
        
        # Merge very small clusters
        small_cluster_threshold = max(5, self.min_cluster_size // 2)
        small_clusters = [
            cid for cid, stats in cluster_stats.items()
            if cid != -1 and stats['size'] < small_cluster_threshold
        ]
        
        if small_clusters:
            logger.info(f"Merging {len(small_clusters)} small clusters")
            df = self._merge_small_clusters(df, embeddings, small_clusters, cluster_stats)
        
        return df
    
    def _split_clusters_by_level(self, 
                                df: pd.DataFrame,
                                embeddings: np.ndarray,
                                clusters_to_split: List[int]) -> pd.DataFrame:
        """Split clusters with high level variance"""
        next_cluster_id = df['cluster_id'].max() + 1
        
        for cluster_id in clusters_to_split:
            cluster_mask = df['cluster_id'] == cluster_id
            cluster_df = df[cluster_mask].copy()
            
            if 'level' not in cluster_df.columns:
                continue
            
            # Group by level ranges
            cluster_df['level_group'] = cluster_df['level'].apply(
                lambda x: (self._extract_level_value(x) - 1) // 2  # Group every 2 levels
            )
            
            # Assign new cluster IDs to each group
            for level_group in cluster_df['level_group'].unique():
                if level_group == cluster_df['level_group'].mode()[0]:
                    continue  # Keep the most common group with original ID
                
                group_mask = cluster_df['level_group'] == level_group
                df.loc[cluster_mask & group_mask, 'cluster_id'] = next_cluster_id
                next_cluster_id += 1
        
        return df
    
    def _merge_small_clusters(self,
                             df: pd.DataFrame,
                             embeddings: np.ndarray,
                             small_clusters: List[int],
                             cluster_stats: Dict) -> pd.DataFrame:
        """Merge small clusters with similar characteristics"""
        # For each small cluster, find the best larger cluster to merge with
        for small_cluster_id in small_clusters:
            small_mask = df['cluster_id'] == small_cluster_id
            small_stats = cluster_stats[small_cluster_id]
            
            best_merge_cluster = None
            best_similarity = 0
            
            # Compare with larger clusters
            for cluster_id, stats in cluster_stats.items():
                if cluster_id == -1 or cluster_id == small_cluster_id:
                    continue
                if stats['size'] < self.min_cluster_size:
                    continue
                
                # Calculate similarity based on level and context
                level_diff = abs(
                    small_stats.get('level_stats', {}).get('dominant_level', -1) -
                    stats.get('level_stats', {}).get('dominant_level', -1)
                )
                
                context_match = (
                    small_stats.get('context_stats', {}).get('dominant_context', 'None') ==
                    stats.get('context_stats', {}).get('dominant_context', 'None')
                )
                
                similarity = (1.0 / (1 + level_diff)) * (1.0 if context_match else 0.5)
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_merge_cluster = cluster_id
            
            # Merge with best cluster or mark as noise
            if best_merge_cluster is not None and best_similarity > 0.5:
                df.loc[small_mask, 'cluster_id'] = best_merge_cluster
            else:
                df.loc[small_mask, 'cluster_id'] = -1  # Mark as noise
        
        return df
    
    def get_cluster_representatives(self, 
                                   df: pd.DataFrame, 
                                   embeddings: np.ndarray,
                                   n_representatives: int = 5) -> Dict:
        """
        Get representative skills for each cluster considering multiple factors
        """
        representatives = {}
        
        for cluster_id in sorted(df['cluster_id'].unique()):
            if cluster_id == -1:
                continue
            
            cluster_mask = df['cluster_id'] == cluster_id
            cluster_df = df[cluster_mask].copy()
            cluster_embeddings = embeddings[cluster_mask]
            
            # Find skills that best represent the cluster
            # Consider: centrality, level representation, context coverage
            
            # Calculate scores for each skill
            scores = []
            cluster_center = np.mean(cluster_embeddings, axis=0)
            
            for idx, (_, row) in enumerate(cluster_df.iterrows()):
                # Distance to center (lower is better)
                distance = np.linalg.norm(cluster_embeddings[idx] - cluster_center)
                centrality_score = 1.0 / (1 + distance)
                
                # Level representativeness
                if 'cluster_level' in row:
                    level = self._extract_level_value(row['level'])
                    cluster_level = row['cluster_level']
                    level_score = 1.0 / (1 + abs(level - cluster_level))
                else:
                    level_score = 1.0
                
                # Confidence score
                confidence_score = row.get('confidence', 0.5)
                
                # Combined score
                total_score = centrality_score * 0.5 + level_score * 0.3 + confidence_score * 0.2
                scores.append(total_score)
            
            # Get top representatives
            cluster_df['representative_score'] = scores
            representatives_df = cluster_df.nlargest(n_representatives, 'representative_score')
            
            representatives[cluster_id] = representatives_df[
                ['name', 'description', 'level', 'context', 'keywords', 'representative_score']
            ].to_dict('records')
        
        return representatives
    
    def save_clustering_results(self, df: pd.DataFrame, output_path: Path):
        """Save enhanced clustering results"""
        df.to_csv(output_path / "clustered_skills.csv", index=False)
        
        # Save cluster statistics
        if hasattr(self, 'skills_metadata'):
            cluster_stats = self._generate_enhanced_cluster_stats(df, df.index.values)
            
            import json
            with open(output_path / "cluster_stats.json", 'w') as f:
                # Convert numpy arrays to lists for JSON serialization
                stats_serializable = {}
                for cluster_id, stats in cluster_stats.items():
                    stats_copy = stats.copy()
                    if 'center' in stats_copy:
                        stats_copy['center'] = stats_copy['center'].tolist()
                    stats_serializable[str(cluster_id)] = stats_copy
                
                json.dump(stats_serializable, f, indent=2)
        
        # Save cluster model if exists
        if self.clusterer:
            with open(output_path / "cluster_model.pkl", 'wb') as f:
                pickle.dump(self.clusterer, f)
        
        logger.info(f"Saved clustering results to {output_path}")
