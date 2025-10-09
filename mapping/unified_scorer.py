"""
Unified scoring system for credit transfer alignment
Ensures consistent calculation across all components
"""

import numpy as np
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from models.base_models import Skill
from models.enums import SkillLevel

@dataclass
class MatchScore:
    """Detailed score breakdown for transparency"""
    skill_coverage: float
    skill_quality: float
    level_alignment: float
    context_alignment: float
    confidence: float
    edge_penalties: Dict[str, float]
    final_score: float
    components: Dict[str, float]
    
class UnifiedScorer:
    """Centralized scoring logic for all credit transfer calculations"""
    
    # Component weights (must sum to 1.0)
    WEIGHTS = {
        'skill_coverage': 0.40,   # How many skills match
        'skill_quality': 0.25,     # How well they match
        'level_alignment': 0.20,   # Level compatibility
        'context_alignment': 0.10, # Theory vs practical
        'confidence': 0.05         # Extraction confidence
    }
    
    # Edge case penalties
    PENALTIES = {
        'minor_level_gap': 0.05,       # 1 level difference
        'major_level_gap': 0.20,       # 2+ levels difference
        'context_imbalance': 0.15,     # >40% difference in theory/practical
        'outdated_content': 0.25,      # Obsolete technologies
        'missing_prerequisites': 0.30,  # Critical prerequisite gaps
        'excessive_size_mismatch': 0.10 # Too many or too few skills
    }
    
    def __init__(self):
        self.level_compatibility_matrix = self._build_level_compatibility_matrix()
    
    def _build_level_compatibility_matrix(self) -> np.ndarray:
        """Build SFIA level compatibility matrix (7x7)"""
        matrix = np.array([
            # VET→  1    2    3    4    5    6    7   (rows = VET levels)
            [1.0, 0.8, 0.6, 0.4, 0.2, 0.1, 0.0],  # Uni level 1
            [0.8, 1.0, 0.8, 0.6, 0.4, 0.2, 0.1],  # Uni level 2
            [0.6, 0.8, 1.0, 0.8, 0.6, 0.4, 0.2],  # Uni level 3
            [0.4, 0.6, 0.8, 1.0, 0.8, 0.6, 0.4],  # Uni level 4
            [0.2, 0.4, 0.6, 0.8, 1.0, 0.8, 0.6],  # Uni level 5
            [0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 0.8],  # Uni level 6
            [0.0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0],  # Uni level 7
        ])
        return matrix
    
    def calculate_alignment_score(self,
                                 match_result: Dict[str, Any],
                                 edge_case_results: Dict[str, Any] = None) -> MatchScore:
        """
        Calculate unified alignment score with all components
        
        Args:
            vet_skills: List of VET skills
            uni_skills: List of university skills
            skill_matches: Matching results from ClusterSkillMatcher
            edge_case_results: Edge case analysis results
            
        Returns:
            MatchScore object with detailed breakdown
        """
        match_result = match_result.get('best_match', {})
        # 1. Calculate weighted skill coverage
        coverage_score = match_result.get('weighted_uni_coverage', 0.0)
        
        # 2. Calculate skill match quality
        quality_score = self._calculate_match_quality(match_result)
        
        # 3. Calculate level alignment
        level_score = self._calculate_level_alignment(match_result)
        
        # 4. Calculate context alignment
        context_score = self._calculate_context_alignment(match_result)
        
        # 5. Calculate confidence score
        confidence_score = self._calculate_confidence(match_result)
        
        # 6. Calculate edge case penalties
        penalties = self._calculate_penalties(
            match_result, edge_case_results
        )
        
        # 7. Combine scores
        base_score = (
            self.WEIGHTS['skill_coverage'] * coverage_score +
            self.WEIGHTS['skill_quality'] * quality_score +
            self.WEIGHTS['level_alignment'] * level_score +
            self.WEIGHTS['context_alignment'] * context_score +
            self.WEIGHTS['confidence'] * confidence_score
        )
        
        # Apply penalties
        total_penalty = sum(penalties.values())
        final_score = max(0, base_score * (1 - total_penalty))
        
        return MatchScore(
            skill_coverage=coverage_score,
            skill_quality=quality_score,
            level_alignment=level_score,
            context_alignment=context_score,
            confidence=confidence_score,
            edge_penalties=penalties,
            final_score=final_score,
            components={
                'base_score': base_score,
                'total_penalty': total_penalty,
                'coverage_weighted': self.WEIGHTS['skill_coverage'] * coverage_score,
                'quality_weighted': self.WEIGHTS['skill_quality'] * quality_score,
                'level_weighted': self.WEIGHTS['level_alignment'] * level_score,
                'context_weighted': self.WEIGHTS['context_alignment'] * context_score,
                'confidence_weighted': self.WEIGHTS['confidence'] * confidence_score
            }
        )
    
    def _calculate_match_quality(self, best_match: Dict) -> float:
        """Calculate average quality of matches"""
        
        quality = 0.0
        for match in best_match['best_uni_skill_matches']:
            if match['match_type'] in ('none', 'unmapped'):
                continue
            semantic_sim = match.get('similarity', 0)
            level_align = match.get('level_compatibility', 0)
            combined_quality = 0.7 * semantic_sim + 0.3 * level_align
            quality += combined_quality
        
        return quality / len(best_match['best_uni_skill_matches'])
    
    def _calculate_level_alignment(self, best_match: Dict) -> float:
        """Calculate level compatibility between skill sets"""
        level_align = 0.0
        for match in best_match['best_uni_skill_matches']:
            if match['match_type'] in ('none', 'unmapped'):
                continue
            level_compat = match.get('level_compatibility', 0)
            level_align += level_compat
        
        return level_align / len(best_match['best_uni_skill_matches'])
    
    def _calculate_context_alignment(self, best_match: Dict) -> float:
        """Calculate context (theoretical vs practical) alignment"""
        context_align = 0.0
        for match in best_match['best_uni_skill_matches']:
            if match['match_type'] in ('none', 'unmapped'):
                continue
            context_similarity = match.get('context_similarity', 0)
            context_align += context_similarity
        
        return context_align / len(best_match['best_uni_skill_matches'])
    
    def _calculate_confidence(self, best_match: Dict) -> float:
        """Calculate average confidence of skill extractions"""
        vet_skills = [match['vet_skill'] for match in best_match['best_uni_skill_matches'] if match['match_type'] != 'unmapped']
        uni_skills = [match['uni_skill'] for match in best_match['best_uni_skill_matches'] if match['match_type'] != 'unmapped']
        all_skills = vet_skills + uni_skills
        if not all_skills:
            return 0.0
        
        confidences = [s.confidence for s in all_skills]
        return np.mean(confidences)
    
    def _calculate_penalties(self,best_match: Dict, edge_case_results: Dict = None) -> Dict[str, float]:
        """Calculate penalties based on edge cases"""
        vet_skills = [match['vet_skill'] for match in best_match['best_uni_skill_matches'] if match['match_type'] != 'unmapped']
        uni_skills = [match['uni_skill'] for match in best_match['best_uni_skill_matches'] if match['match_type'] != 'unmapped']
        penalties = {}
        
        if not edge_case_results:
            return penalties
        
        # Level gap penalties
        if 'context_imbalance' in edge_case_results:
            imbalance = edge_case_results['context_imbalance']
            if imbalance.get('imbalance_score', 0) > 0.4:
                penalties['context_imbalance'] = self.PENALTIES['context_imbalance']
        
        # Outdated content
        if 'outdated_content' in edge_case_results:
            outdated = edge_case_results['outdated_content']
            if outdated.get('currency_issues'):
                penalties['outdated_content'] = self.PENALTIES['outdated_content']
        
        # Missing prerequisites
        if 'prerequisite_chain' in edge_case_results:
            prereq = edge_case_results['prerequisite_chain']
            if prereq.get('missing_prerequisites'):
                penalties['missing_prerequisites'] = self.PENALTIES['missing_prerequisites']
        
        # Level gaps
        avg_vet = np.mean([s.level.value for s in vet_skills]) if vet_skills else 0
        avg_uni = np.mean([s.level.value for s in uni_skills]) if uni_skills else 0
        level_gap = abs(avg_uni - avg_vet)
        
        if level_gap >= 2:
            penalties['major_level_gap'] = self.PENALTIES['major_level_gap']
        elif level_gap >= 1:
            penalties['minor_level_gap'] = self.PENALTIES['minor_level_gap']
        
        # Size mismatch
        size_ratio = len(vet_skills) / max(1, len(uni_skills))
        if size_ratio > 2.5 or size_ratio < 0.4:
            penalties['excessive_size_mismatch'] = self.PENALTIES['excessive_size_mismatch']
        
        return penalties