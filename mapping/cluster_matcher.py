"""
Enhanced clustering-based skill matcher with proper level-aware matching
"""

import json
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.cluster import DBSCAN, AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity
from dataclasses import dataclass
import logging
from mapping.clustering_algo import GridSearchSkillsClusterer
from models.base_models import Skill
from models.enums import SkillLevel
from utils.json_encoder import dumps, loads, make_json_serializable

logger = logging.getLogger(__name__)


@dataclass
class SkillMatch:
    """Represents a match between VET and University skills"""
    vet_skills: List[Skill]
    uni_skills: List[Skill]
    semantic_similarity: float
    level_alignment: float
    combined_score: float
    match_type: str
    confidence: float
    metadata: Dict


class ClusterSkillMatcher:
    """Match skills using two-stage approach: semantic clustering then level refinement"""
    
    def __init__(self, embeddings=None, config=None):
        self.embeddings = embeddings
        self.config = config or {}
        
        # Semantic clustering parameters
        self.semantic_threshold = self.config.get("CLUSTERING_THRESHOLD", 0.75)
        self.min_cluster_size = self.config.get("MIN_CLUSTER_SIZE", 2)
        
        # Level matching parameters
        self.level_importance = self.config.get("LEVEL_WEIGHT", 0.3)
        self.semantic_importance = 1.0 - self.level_importance
        
        # Level compatibility matrix (how well different levels match)
        self.level_compatibility_matrix = self._build_level_compatibility_matrix()
    
    def _build_level_compatibility_matrix(self) -> np.ndarray:
        """
        Build a compatibility matrix for SFIA skill levels
        Higher values = better compatibility
        """
        # 7x7 matrix for SFIA levels 1-7
        matrix = np.array([
            # VET→  1    2    3    4    5    6    7   (rows = VET levels)
            [1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.0],  # Uni level 1 (Follow)
            [0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1],  # Uni level 2 (Assist)
            [0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2],  # Uni level 3 (Apply)
            [0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4],  # Uni level 4 (Enable)
            [0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6],  # Uni level 5 (Ensure/Advise)
            [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8],  # Uni level 6 (Initiate/Influence)
            [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0],  # Uni level 7 (Set Strategy)
        ])
        return matrix
    
    def match_skills(self, 
                     vet_skills: List[Skill], 
                     uni_skills: List[Skill]) -> Dict[str, Any]:
        """
        Match skills using two-stage approach:
        1. Pure semantic clustering
        2. Level-based refinement and scoring
        """
        if not vet_skills or not uni_skills:
            return self._empty_result()
        
        # Stage 1: Semantic Clustering
        semantic_clusters = self._perform_semantic_clustering(vet_skills, uni_skills)
        
        # Stage 2: Level-Based Refinement
        refined_matches = self._refine_with_level_matching(semantic_clusters)
        
        # Stage 3: Score and Rank Matches
        final_matches = self._score_and_rank_matches(refined_matches)
        
        # Calculate statistics
        stats = self._calculate_statistics(final_matches, vet_skills, uni_skills)
        
        self.last_semantic_clusters = semantic_clusters
        return {
            "matches": final_matches,
            "semantic_clusters": semantic_clusters,
            "statistics": stats,
            "unmapped_vet": self._find_unmapped_skills(vet_skills, final_matches, 'vet'),
            "unmapped_uni": self._find_unmapped_skills(uni_skills, final_matches, 'uni')
        }
    
    def _perform_semantic_clustering(self, 
                                     vet_skills: List[Skill], 
                                     uni_skills: List[Skill]) -> List[Dict]:
        """
        Stage 1: Pure semantic clustering based only on skill name embeddings
        This preserves the semantic space integrity
        """
        all_skills = vet_skills + uni_skills
        skill_origins = ['vet'] * len(vet_skills) + ['uni'] * len(uni_skills)
        
        # Generate embeddings ONLY for skill names (preserves semantic space)
        if self.embeddings:
            skill_texts = [s.name for s in all_skills]
            embeddings_matrix = self.embeddings.encode(skill_texts)
        else:
            embeddings_matrix = self._simple_vectorize([s.name for s in all_skills])
        
        # Compute similarity matrix
        similarity_matrix = cosine_similarity(embeddings_matrix)
        
        # Convert similarity to distance for clustering
        # distance_matrix = 1.0 - similarity_matrix
        
        # Perform GridSearchSkillsClusterer clustering on pure semantic distances
        grid_clusterer = GridSearchSkillsClusterer(memory_limit_gb=10,
                                                      batch_size=256,
                                                      embedding_models=[self.config.get("EMBEDDING_MODEL", None)] if self.embeddings else [None],
                                                      embedders={self.config.get("EMBEDDING_MODEL", None): embeddings_matrix},
                                                      clustering_algorithms=['kmeans', 'gmm'])
        labels = grid_clusterer.grid_search_clustering(skills=[s.name for s in all_skills], embeddings_available=True)
        
        # Process clusters
        semantic_clusters = []
        unique_labels = set(labels)
        
        for cluster_id in unique_labels:
            if cluster_id == -1:  # Skip noise in DBSCAN
                continue
            
            cluster_indices = np.where(labels == cluster_id)[0]
            cluster_skills = []
            
            for idx in cluster_indices:
                skill = all_skills[idx]
                origin = skill_origins[idx]
                
                # Calculate semantic similarity to cluster centroid
                cluster_embeddings = embeddings_matrix[cluster_indices]
                centroid = np.mean(cluster_embeddings, axis=0)
                similarity_to_centroid = cosine_similarity(
                    embeddings_matrix[idx:idx+1], 
                    centroid.reshape(1, -1)
                )[0, 0]
                
                cluster_skills.append({
                    'skill': skill,
                    'origin': origin,
                    'embedding_idx': idx,
                    'similarity_to_centroid': similarity_to_centroid
                })
            
            # Only keep clusters with both VET and UNI skills
            vet_in_cluster = [cs for cs in cluster_skills if cs['origin'] == 'vet']
            uni_in_cluster = [cs for cs in cluster_skills if cs['origin'] == 'uni']
            
            if vet_in_cluster and uni_in_cluster:
                # Calculate average pairwise similarity within cluster
                cluster_embedding_indices = [cs['embedding_idx'] for cs in cluster_skills]
                cluster_similarity_submatrix = similarity_matrix[
                    np.ix_(cluster_embedding_indices, cluster_embedding_indices)
                ]
                avg_similarity = np.mean(cluster_similarity_submatrix[np.triu_indices_from(cluster_similarity_submatrix, k=1)])
                
                semantic_clusters.append({
                    'cluster_id': int(cluster_id),
                    'vet_skills': vet_in_cluster,
                    'uni_skills': uni_in_cluster,
                    'avg_semantic_similarity': float(avg_similarity),
                    'size': len(cluster_skills)
                })
        # Write to file
        serializable_dict = make_json_serializable(semantic_clusters)
        with open("./output/semantic_clusters.json", 'w', encoding='utf-8') as f:
            json.dump(serializable_dict, f, indent=2, ensure_ascii=False)
        return semantic_clusters
    
    def _refine_with_level_matching(self, semantic_clusters: List[Dict]) -> List[SkillMatch]:
        """
        Stage 2: Refine semantic clusters by considering skill levels
        This happens AFTER semantic clustering, preserving embedding integrity
        """
        refined_matches = []
        
        for cluster in semantic_clusters:
            # Extract skills from cluster
            vet_skills = [cs['skill'] for cs in cluster['vet_skills']]
            uni_skills = [cs['skill'] for cs in cluster['uni_skills']]
            
            # Calculate level distributions
            vet_level_dist = self._get_level_distribution(vet_skills)
            uni_level_dist = self._get_level_distribution(uni_skills)
            
            # Calculate level alignment score using Earth Mover's Distance or similar
            level_alignment = self._calculate_level_alignment_score(
                vet_level_dist, uni_level_dist
            )
            
            # Option 1: Keep all skills together if alignment is acceptable
            if level_alignment >= 0.5:
                match = SkillMatch(
                    vet_skills=vet_skills,
                    uni_skills=uni_skills,
                    semantic_similarity=cluster['avg_semantic_similarity'],
                    level_alignment=level_alignment,
                    combined_score=self._calculate_combined_score(
                        cluster['avg_semantic_similarity'], 
                        level_alignment
                    ),
                    match_type=self._determine_match_type(vet_skills, uni_skills),
                    confidence=self._calculate_confidence(
                        cluster['avg_semantic_similarity'],
                        level_alignment,
                        len(vet_skills) + len(uni_skills)
                    ),
                    metadata={
                        'cluster_id': cluster['cluster_id'],
                        'vet_level_dist': vet_level_dist,
                        'uni_level_dist': uni_level_dist,
                        'level_gap': self._calculate_level_gap(vet_skills, uni_skills)
                    }
                )
                refined_matches.append(match)
            
            # Option 2: Split cluster by level compatibility if alignment is poor
            else:
                split_matches = self._split_cluster_by_level(
                    vet_skills, uni_skills, cluster['avg_semantic_similarity'], cluster['cluster_id']
                )
                refined_matches.extend(split_matches)
        
        return refined_matches
    
    def _split_cluster_by_level(self, 
                                vet_skills: List[Skill], 
                                uni_skills: List[Skill],
                                semantic_similarity: float,
                                cluster_id: int) -> List[SkillMatch]:
        """
        Split a semantic cluster into level-compatible sub-matches
        Used when overall level alignment is poor but semantic similarity is high
        """
        matches = []
        
        # Group skills by level
        vet_by_level = {}
        for skill in vet_skills:
            level = skill.level.value
            if level not in vet_by_level:
                vet_by_level[level] = []
            vet_by_level[level].append(skill)
        
        uni_by_level = {}
        for skill in uni_skills:
            level = skill.level.value
            if level not in uni_by_level:
                uni_by_level[level] = []
            uni_by_level[level].append(skill)
        
        # Create matches for compatible level pairs
        for vet_level, vet_group in vet_by_level.items():
            for uni_level, uni_group in uni_by_level.items():
                # Check level compatibility
                compatibility = self.level_compatibility_matrix[
                    min(vet_level - 1, 6), 
                    min(uni_level - 1, 6)
                ]
                
                if compatibility >= 0.4:  # Threshold for acceptable compatibility
                    match = SkillMatch(
                        vet_skills=vet_group,
                        uni_skills=uni_group,
                        semantic_similarity=semantic_similarity,
                        level_alignment=compatibility,
                        combined_score=self._calculate_combined_score(
                            semantic_similarity, compatibility
                        ),
                        match_type=self._determine_match_type(vet_group, uni_group),
                        confidence=self._calculate_confidence(
                            semantic_similarity,
                            compatibility,
                            len(vet_group) + len(uni_group)
                        ),
                        metadata={
                            'cluster_id': cluster_id,
                            'split_reason': 'level_incompatibility',
                            'vet_level': vet_level,
                            'uni_level': uni_level
                        }
                    )
                    matches.append(match)
        
        return matches
    
    def _score_and_rank_matches(self, matches: List[SkillMatch]) -> List[Dict]:
        """
        Stage 3: Calculate final scores and rank matches
        """
        # Sort by combined score
        sorted_matches = sorted(matches, key=lambda m: m.combined_score, reverse=True)
        
        # Convert to dictionary format for compatibility
        final_matches = []
        for match in sorted_matches:
            final_matches.append({
                "vet_skills": match.vet_skills,
                "uni_skills": match.uni_skills,
                "match_type": match.match_type,
                "confidence": match.confidence,
                "semantic_similarity": match.semantic_similarity,
                "level_alignment": match.level_alignment,
                "combined_score": match.combined_score,
                "match_quality": self._categorize_match_quality(match.combined_score),
                "metadata": match.metadata
            })
        
        return final_matches
    
    def _calculate_combined_score(self, semantic_sim: float, level_align: float) -> float:
        """
        Calculate combined score from semantic similarity and level alignment
        Uses configurable weights
        """
        return (self.semantic_importance * semantic_sim + 
                self.level_importance * level_align)
    
    def _calculate_level_alignment_score(self, 
                                         vet_dist: Dict[int, float], 
                                         uni_dist: Dict[int, float]) -> float:
        """
        Calculate alignment between two level distributions
        Uses weighted compatibility based on the compatibility matrix
        """
        total_alignment = 0.0
        total_weight = 0.0
        
        for vet_level, vet_prop in vet_dist.items():
            for uni_level, uni_prop in uni_dist.items():
                # Get compatibility from matrix
                compatibility = self.level_compatibility_matrix[
                    min(vet_level - 1, 4),
                    min(uni_level - 1, 4)
                ]
                
                # Weight by proportion of skills at each level
                weight = vet_prop * uni_prop
                total_alignment += compatibility * weight
                total_weight += weight
        
        return total_alignment / total_weight if total_weight > 0 else 0.0
    
    def _get_level_distribution(self, skills: List[Skill]) -> Dict[int, float]:
        """Get normalized distribution of skill levels"""
        if not skills:
            return {}
        
        level_counts = {}
        for skill in skills:
            level = skill.level.value
            level_counts[level] = level_counts.get(level, 0) + 1
        
        total = len(skills)
        return {level: count / total for level, count in level_counts.items()}
    
    def _calculate_level_gap(self, vet_skills: List[Skill], uni_skills: List[Skill]) -> float:
        """Calculate average level gap between skill sets"""
        if not vet_skills or not uni_skills:
            return 0.0
        
        avg_vet = np.mean([s.level.value for s in vet_skills])
        avg_uni = np.mean([s.level.value for s in uni_skills])
        
        return avg_uni - avg_vet
    
    def _calculate_confidence(self, 
                              semantic_sim: float, 
                              level_align: float,
                              total_skills: int) -> float:
        """Calculate match confidence"""
        # Base confidence on quality metrics
        base_confidence = (semantic_sim * 0.6 + level_align * 0.4)
        
        # Adjust for cluster size (smaller clusters are more precise)
        size_penalty = 1.0 / (1.0 + np.log(max(1, total_skills)))
        
        return min(1.0, base_confidence * (0.7 + 0.3 * size_penalty))
    
    def _categorize_match_quality(self, score: float) -> str:
        """Categorize match quality based on combined score"""
        if score >= 0.85:
            return "excellent"
        elif score >= 0.70:
            return "good"
        elif score >= 0.55:
            return "moderate"
        elif score >= 0.40:
            return "weak"
        else:
            return "poor"
    
    def _determine_match_type(self, vet_skills: List, uni_skills: List) -> str:
        """Determine match type"""
        if len(vet_skills) == 1 and len(uni_skills) == 1:
            return "one-to-one"
        elif len(vet_skills) > 1 and len(uni_skills) == 1:
            return "many-to-one"
        elif len(vet_skills) == 1 and len(uni_skills) > 1:
            return "one-to-many"
        else:
            return "many-to-many"
    
    def _find_unmapped_skills(self, 
                              skills: List[Skill], 
                              matches: List[Dict],
                              origin: str) -> List[Skill]:
        """Find skills that weren't matched"""
        matched_skills = set()
        
        for match in matches:
            key = f"{origin}_skills"
            for skill in match.get(key, []):
                matched_skills.add(id(skill))
        
        return [s for s in skills if id(s) not in matched_skills]
    
    def _calculate_statistics(self, 
                         matches: List[Dict], 
                         vet_skills: List[Skill], 
                         uni_skills: List[Skill]) -> Dict:
        """Calculate comprehensive statistics"""
        
        if not matches:
            return self._empty_statistics()
        
        # Extract metrics
        semantic_scores = [m['semantic_similarity'] for m in matches]
        level_scores = [m['level_alignment'] for m in matches]
        combined_scores = [m['combined_score'] for m in matches]
        confidences = [m['confidence'] for m in matches]  # Add this line
        
        # Count matched skills
        matched_vet = set()
        matched_uni = set()
        
        for match in matches:
            for skill in match.get('vet_skills', []):
                matched_vet.add(id(skill))
            for skill in match.get('uni_skills', []):
                matched_uni.add(id(skill))
        
        # Quality distribution
        quality_dist = {}
        for match in matches:
            quality = match['match_quality']
            quality_dist[quality] = quality_dist.get(quality, 0) + 1
        
        return {
            "total_matches": len(matches),
            "total_clusters": len(matches),  # Add for compatibility
            "vet_coverage": len(matched_vet) / len(vet_skills) if vet_skills else 0,
            "uni_coverage": len(matched_uni) / len(uni_skills) if uni_skills else 0,
            "avg_semantic_similarity": np.mean(semantic_scores) if semantic_scores else 0,
            "avg_level_alignment": np.mean(level_scores) if level_scores else 0,
            "avg_combined_score": np.mean(combined_scores) if combined_scores else 0,
            "avg_confidence": np.mean(confidences) if confidences else 0,  # Add this line
            "avg_match_quality": np.mean(combined_scores) if combined_scores else 0,  # Add for compatibility
            "match_quality_distribution": quality_dist,
            "match_types": {
                mt: sum(1 for m in matches if m['match_type'] == mt)
                for mt in ["one-to-one", "many-to-one", "one-to-many", "many-to-many"]
            },
            "level_compatible_matches": sum(
                1 for m in matches 
                if m.get('level_alignment', 0) >= 0.5
            ),
            "level_gap_matches": sum(
                1 for m in matches 
                if m.get('level_alignment', 0) < 0.5
            )
        }

    def _empty_statistics(self) -> Dict:
        """Return empty statistics with all expected keys"""
        return {
            "total_matches": 0,
            "total_clusters": 0,
            "vet_coverage": 0,
            "uni_coverage": 0,
            "avg_semantic_similarity": 0,
            "avg_level_alignment": 0,
            "avg_combined_score": 0,
            "avg_confidence": 0,  # Add this
            "avg_match_quality": 0,  # Add this
            "match_quality_distribution": {},
            "match_types": {},
        "level_compatible_matches": 0,
        "level_gap_matches": 0
    }
    
    def _simple_vectorize(self, texts: List[str]) -> np.ndarray:
        """Fallback vectorization"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        return vectorizer.fit_transform(texts).toarray()
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            "matches": [],
            "semantic_clusters": [],
            "statistics": self._empty_statistics(),
            "unmapped_vet": [],
            "unmapped_uni": []
        }
    
    def _empty_statistics(self) -> Dict:
        """Return empty statistics"""
        return {
            "total_matches": 0,
            "vet_coverage": 0,
            "uni_coverage": 0,
            "avg_semantic_similarity": 0,
            "avg_level_alignment": 0,
            "avg_combined_score": 0,
            "match_quality_distribution": {},
            "match_types": {}
        }