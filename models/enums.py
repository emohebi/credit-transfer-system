"""
Enumeration classes for the Credit Transfer Analysis System
"""

from enum import Enum


class SkillLevel(Enum):
    """Proficiency levels for skills"""
    NOVICE = 1
    ADVANCED_BEGINNER = 2
    COMPETENT = 3
    PROFICIENT = 4
    EXPERT = 5
    
    @classmethod
    def from_string(cls, level_str: str):
        """Parse skill level from string"""
        level_map = {
            "novice": cls.NOVICE,
            "beginner": cls.ADVANCED_BEGINNER,
            "competent": cls.COMPETENT,
            "proficient": cls.PROFICIENT,
            "expert": cls.EXPERT
        }
        return level_map.get(level_str.lower(), cls.COMPETENT)


class SkillDepth(Enum):
    """Cognitive depth according to Bloom's Taxonomy"""
    REMEMBER = 1
    UNDERSTAND = 2
    APPLY = 3
    ANALYZE = 4
    EVALUATE = 5
    CREATE = 6
    
    @classmethod
    def from_verb(cls, verb: str):
        """Determine depth from action verb"""
        verb_map = {
            "identify": cls.REMEMBER,
            "list": cls.REMEMBER,
            "name": cls.REMEMBER,
            "recognize": cls.REMEMBER,
            "explain": cls.UNDERSTAND,
            "describe": cls.UNDERSTAND,
            "interpret": cls.UNDERSTAND,
            "summarize": cls.UNDERSTAND,
            "apply": cls.APPLY,
            "demonstrate": cls.APPLY,
            "implement": cls.APPLY,
            "use": cls.APPLY,
            "analyze": cls.ANALYZE,
            "compare": cls.ANALYZE,
            "examine": cls.ANALYZE,
            "investigate": cls.ANALYZE,
            "evaluate": cls.EVALUATE,
            "assess": cls.EVALUATE,
            "critique": cls.EVALUATE,
            "justify": cls.EVALUATE,
            "create": cls.CREATE,
            "design": cls.CREATE,
            "develop": cls.CREATE,
            "construct": cls.CREATE
        }
        return verb_map.get(verb.lower(), cls.APPLY)


class SkillContext(Enum):
    """Context where skill is applied"""
    THEORETICAL = "theoretical"
    PRACTICAL = "practical"
    HYBRID = "hybrid"
    
    @classmethod
    def from_indicators(cls, text: str):
        """Determine context from text indicators"""
        text_lower = text.lower()
        
        practical_indicators = ["hands-on", "laboratory", "workshop", "practical", "project"]
        theoretical_indicators = ["theory", "concept", "principle", "framework", "model"]
        
        practical_count = sum(1 for ind in practical_indicators if ind in text_lower)
        theoretical_count = sum(1 for ind in theoretical_indicators if ind in text_lower)
        
        if practical_count > theoretical_count:
            return cls.PRACTICAL
        elif theoretical_count > practical_count:
            return cls.THEORETICAL
        else:
            return cls.HYBRID


class SkillCategory(Enum):
    """Categories of skills"""
    TECHNICAL = "technical"
    COGNITIVE = "cognitive"
    PRACTICAL = "practical"
    FOUNDATIONAL = "foundational"
    PROFESSIONAL = "professional"


class RecommendationType(Enum):
    """Types of credit transfer recommendations"""
    FULL = "full"
    CONDITIONAL = "conditional"
    PARTIAL = "partial"
    NONE = "none"
    
    @classmethod
    def from_score(cls, score: float, has_gaps: bool = False):
        """Determine recommendation type from alignment score"""
        if score >= 0.8 and not has_gaps:
            return cls.FULL
        elif score >= 0.7:
            return cls.CONDITIONAL
        elif score >= 0.5:
            return cls.PARTIAL
        else:
            return cls.NONE
