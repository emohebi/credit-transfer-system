"""
Simplified skill mapping type definitions
"""

from typing import Tuple

class SimpleMappingClassifier:
    """Simple classifier for skill mappings"""
    
    @staticmethod
    def classify_mapping(similarity_score: float, 
                        level_gap: int,
                        context_match: bool) -> Tuple[str, str]:
        """
        Classify mapping into Direct/Partial/Unmapped with reason
        
        Returns:
            (mapping_type, reason)
        """
        
        # DIRECT: High similarity + compatible level + matching context
        if similarity_score >= 0.75 and level_gap <= 1 and context_match:
            return ("Direct", "Strong match with compatible level")
        
        # DIRECT: Very high similarity even with small differences
        elif similarity_score >= 0.85 and level_gap <= 2:
            return ("Direct", "Very strong semantic match")
        
        # PARTIAL: Moderate similarity or level gap
        elif similarity_score >= 0.60 and level_gap <= 2:
            return ("Partial", f"Moderate match (similarity: {similarity_score:.0%}, level gap: {level_gap})")
        
        # PARTIAL: Good similarity but large level gap
        elif similarity_score >= 0.70 and level_gap > 2:
            return ("Partial", f"Good match but {level_gap} level gap")
        
        # PARTIAL: Lower similarity but same level
        elif similarity_score >= 0.45 and level_gap == 0:
            return ("Partial", "Same level but weaker semantic match")
        
        # UNMAPPED: Low similarity
        else:
            return ("Unmapped", f"Insufficient match (similarity: {similarity_score:.0%})")
    
    @staticmethod
    def get_match_quality(similarity_score: float) -> str:
        """Simple quality rating"""
        if similarity_score >= 0.85:
            return "Excellent"
        elif similarity_score >= 0.70:
            return "Good"
        elif similarity_score >= 0.55:
            return "Fair"
        else:
            return "Weak"