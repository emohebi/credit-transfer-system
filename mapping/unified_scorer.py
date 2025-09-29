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
    
    # Match quality thresholds
    MATCH_QUALITY = {
        'exact': (0.90, 1.0),      # similarity >= 0.90: weight = 1.0
        'strong': (0.75, 0.85),    # similarity >= 0.75: weight = 0.85
        'moderate': (0.60, 0.60),  # similarity >= 0.60: weight = 0.60
        'weak': (0.45, 0.30),      # similarity >= 0.45: weight = 0.30
        'none': (0.0, 0.0)         # similarity < 0.45: weight = 0.0
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
                                 vet_skills: List[Skill],
                                 uni_skills: List[Skill],
                                 skill_matches: Dict[str, Any],
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
        
        # 1. Calculate weighted skill coverage
        coverage_score = self._calculate_weighted_coverage(
            uni_skills, vet_skills, skill_matches
        )
        
        # 2. Calculate skill match quality
        quality_score = self._calculate_match_quality(skill_matches)
        
        # 3. Calculate level alignment
        level_score = self._calculate_level_alignment(vet_skills, uni_skills)
        
        # 4. Calculate context alignment
        context_score = self._calculate_context_alignment(vet_skills, uni_skills)
        
        # 5. Calculate confidence score
        confidence_score = self._calculate_confidence(vet_skills, uni_skills)
        
        # 6. Calculate edge case penalties
        penalties = self._calculate_penalties(
            vet_skills, uni_skills, edge_case_results
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
    
    def _calculate_weighted_coverage(self,
                                    uni_skills: List[Skill],
                                    vet_skills: List[Skill],
                                    matches: Dict) -> float:
        """Calculate weighted coverage based on match quality"""
        if not uni_skills:
            return 0.0
        
        total_weight = 0.0
        
        # Process each university skill
        for uni_skill in uni_skills:
            best_match_weight = 0.0
            
            # Find best match in the match results
            for match in matches.get('matches', []):
                for matched_uni in match.get('uni_skills', []):
                    if matched_uni.name == uni_skill.name:
                        # Get similarity score for this match
                        similarity = match.get('semantic_similarity', 0)
                        weight = self._get_match_weight(similarity)
                        best_match_weight = max(best_match_weight, weight)
                        break
            
            total_weight += best_match_weight
        
        return total_weight / len(uni_skills)
    
    def _get_match_weight(self, similarity: float) -> float:
        """Get weight based on match similarity"""
        for quality, (threshold, weight) in self.MATCH_QUALITY.items():
            if quality == 'none':
                continue
            if similarity >= threshold:
                return weight
        return 0.0
    
    def _calculate_match_quality(self, matches: Dict) -> float:
        """Calculate average quality of matches"""
        if not matches.get('matches'):
            return 0.0
        
        qualities = []
        for match in matches['matches']:
            semantic_sim = match.get('semantic_similarity', 0)
            level_align = match.get('level_alignment', 0)
            combined_quality = 0.7 * semantic_sim + 0.3 * level_align
            qualities.append(combined_quality)
        
        return np.mean(qualities) if qualities else 0.0
    
    def _calculate_level_alignment(self,
                                  vet_skills: List[Skill],
                                  uni_skills: List[Skill]) -> float:
        """Calculate level compatibility between skill sets"""
        if not vet_skills or not uni_skills:
            return 0.0
        
        # Get average levels
        vet_levels = [s.level.value for s in vet_skills]
        uni_levels = [s.level.value for s in uni_skills]
        
        avg_vet = np.mean(vet_levels)
        avg_uni = np.mean(uni_levels)
        
        # Look up compatibility
        vet_idx = min(max(0, int(avg_vet) - 1), 6)
        uni_idx = min(max(0, int(avg_uni) - 1), 6)
        
        return self.level_compatibility_matrix[vet_idx, uni_idx]
    
    def _calculate_context_alignment(self,
                                    vet_skills: List[Skill],
                                    uni_skills: List[Skill]) -> float:
        """Calculate context (theoretical vs practical) alignment"""
        if not vet_skills or not uni_skills:
            return 0.0
        
        # Count contexts
        vet_contexts = {'theoretical': 0, 'practical': 0, 'hybrid': 0}
        uni_contexts = {'theoretical': 0, 'practical': 0, 'hybrid': 0}
        
        for skill in vet_skills:
            vet_contexts[skill.context.value] += 1
        
        for skill in uni_skills:
            uni_contexts[skill.context.value] += 1
        
        # Calculate distributions
        vet_total = len(vet_skills)
        uni_total = len(uni_skills)
        
        # Calculate alignment (1 - average difference)
        alignment = 0
        for context in ['theoretical', 'practical', 'hybrid']:
            vet_ratio = vet_contexts[context] / vet_total
            uni_ratio = uni_contexts[context] / uni_total
            alignment += 1 - abs(vet_ratio - uni_ratio)
        
        return alignment / 3  # Average across three contexts
    
    def _calculate_confidence(self,
                             vet_skills: List[Skill],
                             uni_skills: List[Skill]) -> float:
        """Calculate average confidence of skill extractions"""
        all_skills = vet_skills + uni_skills
        if not all_skills:
            return 0.0
        
        confidences = [s.confidence for s in all_skills]
        return np.mean(confidences)
    
    def _calculate_penalties(self,
                            vet_skills: List[Skill],
                            uni_skills: List[Skill],
                            edge_case_results: Dict = None) -> Dict[str, float]:
        """Calculate penalties based on edge cases"""
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