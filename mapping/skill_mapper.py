"""
Skill mapping engine for credit transfer analysis using Gen AI
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from collections import defaultdict

from models.base_models import Skill, SkillMapping
from models.enums import SkillLevel, SkillContext
from interfaces.embedding_interface import EmbeddingInterface

logger = logging.getLogger(__name__)


class SkillMapper:
    """Maps skills between VET and University courses using Gen AI and embeddings"""
    
    def __init__(self, 
                 embeddings: Optional[EmbeddingInterface] = None,
                 genai: Optional[Any] = None,
                 similarity_threshold: float = 0.8,
                 partial_threshold: float = 0.6):
        """
        Initialize skill mapper with Gen AI support
        
        Args:
            embeddings: Embedding interface for similarity calculation
            genai: GenAI interface for AI-based similarity
            similarity_threshold: Threshold for direct skill matches
            partial_threshold: Threshold for partial skill matches
        """
        self.embeddings = embeddings
        self.genai = genai
        self.similarity_threshold = similarity_threshold
        self.partial_threshold = partial_threshold
        self.similarity_cache = {}
    
    def map_skills(self, 
                   vet_skills: List[Skill], 
                   uni_skills: List[Skill]) -> SkillMapping:
        """
        Map VET skills to university skills using AI and embeddings
        
        Args:
            vet_skills: List of VET skills
            uni_skills: List of university skills
            
        Returns:
            SkillMapping object with mapping details
        """
        logger.info(f"Mapping {len(vet_skills)} VET skills to {len(uni_skills)} Uni skills")
        
        mapping = SkillMapping()
        
        if not vet_skills or not uni_skills:
            logger.warning("Empty skill list provided for mapping")
            return mapping
        
        # Calculate similarity matrix
        similarity_matrix = self._calculate_similarity_matrix(vet_skills, uni_skills)
        
        # Find best matches
        matched_vet = set()
        matched_uni = set()
        
        # First pass: Find direct matches
        for i, vet_skill in enumerate(vet_skills):
            best_match_idx = np.argmax(similarity_matrix[i])
            best_score = similarity_matrix[i][best_match_idx]
            
            if best_score >= self.similarity_threshold:
                uni_skill = uni_skills[best_match_idx]
                match_quality = self._assess_match_quality(vet_skill, uni_skill)
                
                mapping.direct_matches.append({
                    "vet_skill": vet_skill,
                    "uni_skill": uni_skill,
                    "similarity": float(best_score),
                    "quality": match_quality
                })
                matched_vet.add(i)
                matched_uni.add(best_match_idx)
                
                # Mark this uni skill as matched
                similarity_matrix[:, best_match_idx] = 0
        
        # Second pass: Find partial matches
        for i, vet_skill in enumerate(vet_skills):
            if i in matched_vet:
                continue
            
            best_match_idx = np.argmax(similarity_matrix[i])
            best_score = similarity_matrix[i][best_match_idx]
            
            if best_score >= self.partial_threshold:
                uni_skill = uni_skills[best_match_idx]
                match_quality = self._assess_match_quality(vet_skill, uni_skill)
                gaps = self._identify_gaps(vet_skill, uni_skill)
                
                mapping.partial_matches.append({
                    "vet_skill": vet_skill,
                    "uni_skill": uni_skill,
                    "similarity": float(best_score),
                    "quality": match_quality,
                    "gaps": gaps
                })
                matched_vet.add(i)
                matched_uni.add(best_match_idx)
        
        # Identify unmapped skills
        mapping.unmapped_vet = [
            vet_skills[i] for i in range(len(vet_skills)) 
            if i not in matched_vet
        ]
        mapping.unmapped_uni = [
            uni_skills[i] for i in range(len(uni_skills)) 
            if i not in matched_uni
        ]
        
        # Calculate overall scores
        mapping.coverage_score = self._calculate_coverage_score(mapping, uni_skills)
        mapping.context_alignment = self._calculate_context_alignment(mapping)
        
        # Add metadata
        mapping.metadata = {
            "total_vet_skills": len(vet_skills),
            "total_uni_skills": len(uni_skills),
            "direct_match_count": len(mapping.direct_matches),
            "partial_match_count": len(mapping.partial_matches),
            "unmapped_vet_count": len(mapping.unmapped_vet),
            "unmapped_uni_count": len(mapping.unmapped_uni),
            "use_ai": self.genai is not None,
            "use_embeddings": self.embeddings is not None
        }
        
        logger.info(
            f"Mapping complete: {len(mapping.direct_matches)} direct, "
            f"{len(mapping.partial_matches)} partial, "
            f"{len(mapping.unmapped_uni)} unmapped uni skills"
        )
        
        return mapping
    
    def _calculate_similarity_matrix(self, 
                                     vet_skills: List[Skill], 
                                     uni_skills: List[Skill]) -> np.ndarray:
        """Calculate pairwise similarity between skills using AI and/or embeddings"""
        
        # If both AI and embeddings available, use hybrid approach
        if self.genai and self.embeddings:
            # Use embeddings for initial fast similarity
            vet_names = [s.name for s in vet_skills]
            uni_names = [s.name for s in uni_skills]
            
            vet_embeddings = self.embeddings.encode(vet_names)
            uni_embeddings = self.embeddings.encode(uni_names)
            
            similarity_matrix = self.embeddings.similarity(vet_embeddings, uni_embeddings)
            
            # For high-scoring pairs, refine with AI
            high_similarity_pairs = np.where(similarity_matrix > 0.5)
            
            for i, j in zip(high_similarity_pairs[0], high_similarity_pairs[1]):
                # Use AI for more accurate similarity
                ai_similarity = self.genai.analyze_skill_similarity(
                    vet_skills[i].name,
                    uni_skills[j].name
                )
                # Weighted average of embedding and AI similarity
                similarity_matrix[i, j] = 0.6 * similarity_matrix[i, j] + 0.4 * ai_similarity
        
        # If only GenAI available, use it exclusively
        elif self.genai:
            similarity_matrix = np.zeros((len(vet_skills), len(uni_skills)))
            
            for i, vet_skill in enumerate(vet_skills):
                for j, uni_skill in enumerate(uni_skills):
                    # Check cache first
                    cache_key = (vet_skill.name.lower(), uni_skill.name.lower())
                    if cache_key in self.similarity_cache:
                        similarity = self.similarity_cache[cache_key]
                    else:
                        similarity = self.genai.analyze_skill_similarity(
                            vet_skill.name, 
                            uni_skill.name
                        )
                        self.similarity_cache[cache_key] = similarity
                    
                    similarity_matrix[i, j] = similarity
        
        # If only embeddings available, use them
        elif self.embeddings:
            vet_names = [s.name for s in vet_skills]
            uni_names = [s.name for s in uni_skills]
            
            vet_embeddings = self.embeddings.encode(vet_names)
            uni_embeddings = self.embeddings.encode(uni_names)
            
            similarity_matrix = self.embeddings.similarity(vet_embeddings, uni_embeddings)
        
        # Fallback to simple string matching
        else:
            similarity_matrix = np.zeros((len(vet_skills), len(uni_skills)))
            
            for i, vet_skill in enumerate(vet_skills):
                for j, uni_skill in enumerate(uni_skills):
                    similarity = self._calculate_string_similarity(
                        vet_skill.name, 
                        uni_skill.name
                    )
                    similarity_matrix[i, j] = similarity
        
        # Apply modifiers based on skill properties
        for i, vet_skill in enumerate(vet_skills):
            for j, uni_skill in enumerate(uni_skills):
                # Boost similarity for same category
                if vet_skill.category == uni_skill.category:
                    similarity_matrix[i, j] *= 1.1
                
                # Reduce similarity for very different contexts
                if (vet_skill.context == SkillContext.PRACTICAL and 
                    uni_skill.context == SkillContext.THEORETICAL):
                    similarity_matrix[i, j] *= 0.9
                elif (vet_skill.context == SkillContext.THEORETICAL and 
                      uni_skill.context == SkillContext.PRACTICAL):
                    similarity_matrix[i, j] *= 0.9
        
        # Normalize to [0, 1]
        similarity_matrix = np.clip(similarity_matrix, 0, 1)
        
        return similarity_matrix
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity as fallback"""
        str1_lower = str1.lower().strip()
        str2_lower = str2.lower().strip()
        
        # Check cache
        cache_key = (str1_lower, str2_lower)
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # Exact match
        if str1_lower == str2_lower:
            similarity = 1.0
        # One contains the other
        elif str1_lower in str2_lower or str2_lower in str1_lower:
            similarity = 0.85
        else:
            # Word overlap using Jaccard similarity
            words1 = set(str1_lower.split())
            words2 = set(str2_lower.split())
            
            if not words1 or not words2:
                similarity = 0.0
            else:
                intersection = words1.intersection(words2)
                union = words1.union(words2)
                similarity = len(intersection) / len(union) if union else 0.0
        
        # Cache result
        self.similarity_cache[cache_key] = similarity
        return similarity
    
    def _assess_match_quality(self, vet_skill: Skill, uni_skill: Skill) -> Dict[str, Any]:
        """Assess quality of skill match using AI if available"""
        quality = {
            "level_alignment": self._compare_levels(vet_skill.level, uni_skill.level),
            "context_compatibility": self._compare_contexts(vet_skill.context, uni_skill.context),
            "category_match": vet_skill.category == uni_skill.category,
            "confidence_product": vet_skill.confidence * uni_skill.confidence
        }
        
        # If AI available, get additional quality assessment
        if self.genai:
            # Could add a specific prompt for quality assessment
            pass
        
        # Overall quality score (weighted average)
        quality["overall"] = (
            quality["level_alignment"] * 0.4 +
            quality["context_compatibility"] * 0.3 +
            float(quality["category_match"]) * 0.2 +
            quality["confidence_product"] * 0.1
        )
        
        return quality
    
    def _compare_levels(self, vet_level: SkillLevel, uni_level: SkillLevel) -> float:
        """Compare skill proficiency levels"""
        try:
            level_diff = vet_level.value - uni_level.value
            
            if level_diff >= 0:
                # VET meets or exceeds requirement
                return 1.0
            elif level_diff == -1:
                # One level below - minor gap
                return 0.8
            elif level_diff == -2:
                # Two levels below - significant gap
                return 0.6
            else:
                # Large gap
                return 0.3
        except:
            # Fallback if comparison fails
            return 0.5
    
    def _compare_contexts(self, vet_context: SkillContext, uni_context: SkillContext) -> float:
        """Compare skill contexts"""
        if vet_context == uni_context:
            return 1.0
        elif vet_context == SkillContext.HYBRID or uni_context == SkillContext.HYBRID:
            # Hybrid matches reasonably with both
            return 0.85
        else:
            # Practical vs Theoretical mismatch
            return 0.7
    
    def _identify_gaps(self, vet_skill: Skill, uni_skill: Skill) -> List[str]:
        """Identify gaps between VET and Uni skill requirements"""
        gaps = []
        
        # Level gap
        try:
            if vet_skill.level.value < uni_skill.level.value:
                level_diff = uni_skill.level.value - vet_skill.level.value
                gaps.append(f"Proficiency gap: {level_diff} level(s) below required {uni_skill.level.name}")
        except:
            pass
        
        # Context gap
        if vet_skill.context != uni_skill.context and uni_skill.context != SkillContext.HYBRID:
            if uni_skill.context == SkillContext.THEORETICAL:
                gaps.append("Context gap: requires more theoretical foundation")
            elif uni_skill.context == SkillContext.PRACTICAL:
                gaps.append("Context gap: requires more practical application")
        
        # Confidence gap
        if vet_skill.confidence < 0.7:
            gaps.append("Low confidence in skill extraction")
        
        # Use AI for more detailed gap analysis if available
        if self.genai:
            # Could add specific gap analysis prompt
            pass
        
        return gaps
    
    def _calculate_coverage_score(self, mapping: SkillMapping, uni_skills: List[Skill]) -> float:
        """Calculate skill coverage score"""
        if not uni_skills:
            return 0.0
        
        # Weight skills by importance
        covered_count = len(mapping.direct_matches) + (len(mapping.partial_matches) * 0.5)
        total_count = len(uni_skills)
        
        return min(1.0, covered_count / total_count) if total_count > 0 else 0.0
    
    def _calculate_context_alignment(self, mapping: SkillMapping) -> float:
        """Calculate overall context alignment score"""
        if not mapping.direct_matches and not mapping.partial_matches:
            return 0.0
        
        scores = []
        
        for match in mapping.direct_matches:
            scores.append(match["quality"]["context_compatibility"])
        
        for match in mapping.partial_matches:
            scores.append(match["quality"]["context_compatibility"] * 0.7)
        
        return np.mean(scores) if scores else 0.0
    
    def get_skill_alignment_summary(self, mapping: SkillMapping) -> Dict[str, Any]:
        """Generate a summary of skill alignment"""
        summary = {
            "total_alignment_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": [],
            "analysis_method": "hybrid" if self.genai and self.embeddings else 
                             "ai_only" if self.genai else 
                             "embedding_only" if self.embeddings else "string_matching"
        }
        
        # Calculate total alignment score
        summary["total_alignment_score"] = (
            mapping.coverage_score * 0.6 +
            mapping.context_alignment * 0.4
        )
        
        # Identify strengths
        if mapping.coverage_score > 0.7:
            summary["strengths"].append(f"Good skill coverage ({mapping.coverage_score:.1%})")
        if mapping.context_alignment > 0.8:
            summary["strengths"].append("Good practical/theoretical balance")
        
        direct_ratio = len(mapping.direct_matches) / (len(mapping.direct_matches) + len(mapping.partial_matches)) if (mapping.direct_matches or mapping.partial_matches) else 0
        if direct_ratio > 0.7:
            summary["strengths"].append(f"High proportion of direct matches ({direct_ratio:.1%})")
        
        # Identify weaknesses
        if mapping.coverage_score < 0.5:
            summary["weaknesses"].append(f"Low skill coverage ({mapping.coverage_score:.1%})")
        if mapping.context_alignment < 0.6:
            summary["weaknesses"].append("Poor practical/theoretical balance")
        if len(mapping.unmapped_uni) > 5:
            summary["weaknesses"].append(f"{len(mapping.unmapped_uni)} critical skills not covered")
        
        # Generate recommendations
        if mapping.unmapped_uni:
            summary["recommendations"].append(
                f"Bridge {len(mapping.unmapped_uni)} missing skills through supplementary training"
            )
        
        if mapping.context_alignment < 0.7:
            if any(m["uni_skill"].context == SkillContext.THEORETICAL for m in mapping.partial_matches):
                summary["recommendations"].append("Add theoretical foundation modules")
            if any(m["uni_skill"].context == SkillContext.PRACTICAL for m in mapping.partial_matches):
                summary["recommendations"].append("Include more practical/lab work")
        
        return summary
    
    def clear_cache(self):
        """Clear the similarity cache"""
        self.similarity_cache.clear()
        logger.info("Similarity cache cleared")