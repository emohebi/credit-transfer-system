"""
Fuzzy logic matching system for skill comparison
"""

import numpy as np
from typing import List, Dict, Tuple
import logging
from models.base_models import Skill

logger = logging.getLogger(__name__)


class FuzzySkillMatcher:
    """Implements fuzzy logic for skill matching"""
    
    def __init__(self):
        self.membership_cache = {}
    
    def trapezoidal_membership(self, x: float, a: float, b: float, c: float, d: float) -> float:
        """Trapezoidal membership function"""
        if x <= a or x >= d:
            return 0.0
        elif a < x <= b:
            return (x - a) / (b - a)
        elif b < x <= c:
            return 1.0
        else:  # c < x < d
            return (d - x) / (d - c)
    
    def gaussian_membership(self, x: float, mean: float, std: float) -> float:
        """Gaussian membership function"""
        return np.exp(-0.5 * ((x - mean) / std) ** 2)
    
    def s_curve_membership(self, x: float, a: float, b: float) -> float:
        """S-shaped membership function"""
        if x <= a:
            return 0.0
        elif x >= b:
            return 1.0
        elif x <= (a + b) / 2:
            return 2 * ((x - a) / (b - a)) ** 2
        else:
            return 1 - 2 * ((b - x) / (b - a)) ** 2
    
    def calculate_fuzzy_similarity(self, 
                                  vet_skill: Skill, 
                                  uni_skill: Skill,
                                  base_similarity: float) -> Dict[str, float]:
        """Calculate fuzzy similarity with multiple criteria"""
        
        # Coverage membership (trapezoidal)
        coverage_membership = self.trapezoidal_membership(
            base_similarity, 0.2, 0.4, 0.7, 0.9
        )
        
        # Context compatibility (gaussian)
        context_score = self._get_context_compatibility(vet_skill.context, uni_skill.context)
        context_membership = self.gaussian_membership(
            context_score, mean=0.7, std=0.15
        )
        
        # Level alignment (s-curve)
        level_score = self._get_level_alignment(vet_skill.level, uni_skill.level)
        level_membership = self.s_curve_membership(
            level_score, 0.3, 0.8
        )
        
        # Quality based on confidence (gaussian)
        quality_score = (vet_skill.confidence + uni_skill.confidence) / 2
        quality_membership = self.gaussian_membership(
            quality_score, mean=0.8, std=0.1
        )
        
        # T-norm operations (using minimum for AND)
        technical_match = min(coverage_membership, level_membership)
        contextual_match = min(context_membership, quality_membership)
        
        # T-conorm for aggregation (using algebraic sum for OR)
        # S(a,b) = a + b - a*b
        partial_score = technical_match + contextual_match - (technical_match * contextual_match)
        
        # Final fuzzy score with weighted aggregation
        fuzzy_score = 0.4 * technical_match + 0.3 * contextual_match + 0.3 * partial_score
        
        return {
            "fuzzy_score": fuzzy_score,
            "coverage_membership": coverage_membership,
            "context_membership": context_membership,
            "level_membership": level_membership,
            "quality_membership": quality_membership,
            "technical_match": technical_match,
            "contextual_match": contextual_match
        }
    
    def _get_context_compatibility(self, context1, context2) -> float:
        """Calculate context compatibility score"""
        if context1 == context2:
            return 1.0
        elif "hybrid" in [context1.value, context2.value]:
            return 0.7
        else:
            return 0.3
    
    def _get_level_alignment(self, level1, level2) -> float:
        """Calculate level alignment score"""
        level_diff = abs(level1.value - level2.value)
        if level_diff == 0:
            return 1.0
        elif level_diff == 1:
            return 0.7
        elif level_diff == 2:
            return 0.4
        else:
            return 0.1
    
    def apply_fuzzy_rules(self, fuzzy_results: Dict[str, float]) -> str:
        """Apply fuzzy inference rules"""
        score = fuzzy_results["fuzzy_score"]
        
        # Fuzzy rule base
        if score >= 0.8:
            return "STRONG_MATCH"
        elif score >= 0.6:
            if fuzzy_results["level_membership"] >= 0.7:
                return "GOOD_MATCH"
            else:
                return "CONDITIONAL_MATCH"
        elif score >= 0.4:
            return "PARTIAL_MATCH"
        else:
            return "WEAK_MATCH"