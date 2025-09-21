"""
Fixed enumeration classes with proper ordering for SkillLevel
"""

from enum import Enum


class SkillLevel(Enum):
    """Proficiency levels for skills with ordering support"""
    NOVICE = 1
    ADVANCED_BEGINNER = 2
    COMPETENT = 3
    PROFICIENT = 4
    EXPERT = 5
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    
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


class StudyLevel(Enum):
    """Study levels for university courses with ordering support"""
    INTRODUCTORY = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    SPECIALIZED = 4
    POSTGRADUATE = 5
    
    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented
    
    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented
    
    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented
    
    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented
    
    @classmethod
    def from_string(cls, level_str: str):
        """Parse study level from string"""
        level_map = {
            "introductory": cls.INTRODUCTORY,
            "intro": cls.INTRODUCTORY,
            "beginner": cls.INTRODUCTORY,
            "foundation": cls.INTRODUCTORY,
            "intermediate": cls.INTERMEDIATE,
            "inter": cls.INTERMEDIATE,
            "advanced": cls.ADVANCED,
            "adv": cls.ADVANCED,
            "specialized": cls.SPECIALIZED,
            "spec": cls.SPECIALIZED,
            "specialist": cls.SPECIALIZED,
            "postgraduate": cls.POSTGRADUATE,
            "postgrad": cls.POSTGRADUATE,
            "graduate": cls.POSTGRADUATE
        }
        return level_map.get(level_str.lower(), cls.INTERMEDIATE)
    
    @classmethod
    def to_complexity_score(cls, level):
        """Convert study level to complexity score (0-1)"""
        scores = {
            cls.INTRODUCTORY: 0.2,
            cls.INTERMEDIATE: 0.4,
            cls.ADVANCED: 0.6,
            cls.SPECIALIZED: 0.8,
            cls.POSTGRADUATE: 1.0
        }
        return scores.get(level, 0.5)
    
    @classmethod
    def expected_skill_level(cls, study_level):
        """Get expected skill level for a study level"""
        mapping = {
            cls.INTRODUCTORY: SkillLevel.NOVICE,
            cls.INTERMEDIATE: SkillLevel.COMPETENT,
            cls.ADVANCED: SkillLevel.PROFICIENT,
            cls.SPECIALIZED: SkillLevel.EXPERT,
            cls.POSTGRADUATE: SkillLevel.EXPERT
        }
        return mapping.get(study_level, SkillLevel.COMPETENT)


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
        
class EMBEDDING_MODE(Enum):
    """Categories of skills"""
    HYBRID = "hybrid"
    GENAI = "genai"
    EMBEDDING = "embedding"