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
    """Study levels with expected skill level mappings"""
    INTRODUCTORY = 'Introductory'
    INTERMEDIATE = 'Intermediate'
    ADVANCED = 'Advanced'
    
    @classmethod
    def from_string(cls, level_str: str):
        """Convert string to StudyLevel enum"""
        if not level_str:
            return cls.INTERMEDIATE
        
        level_str = level_str.lower().strip()
        
        # Map various representations to standard levels
        mappings = {
            'introductory': cls.INTRODUCTORY,
            'intro': cls.INTRODUCTORY,
            'beginner': cls.INTRODUCTORY,
            'basic': cls.INTRODUCTORY,
            'foundation': cls.INTRODUCTORY,
            'elementary': cls.INTRODUCTORY,
            '100': cls.INTRODUCTORY,
            '1000': cls.INTRODUCTORY,
            
            'intermediate': cls.INTERMEDIATE,
            'inter': cls.INTERMEDIATE,
            'medium': cls.INTERMEDIATE,
            'moderate': cls.INTERMEDIATE,
            '200': cls.INTERMEDIATE,
            '2000': cls.INTERMEDIATE,
            '300': cls.INTERMEDIATE,
            '3000': cls.INTERMEDIATE,
            
            'advanced': cls.ADVANCED,
            'adv': cls.ADVANCED,
            'high': cls.ADVANCED,
            'senior': cls.ADVANCED,
            'specialized': cls.ADVANCED,
            'postgraduate': cls.ADVANCED,
            'graduate': cls.ADVANCED,
            '400': cls.ADVANCED,
            '4000': cls.ADVANCED,
            '500': cls.ADVANCED,
            '5000': cls.ADVANCED,
            '600': cls.ADVANCED,
            '700': cls.ADVANCED,
            '800': cls.ADVANCED,
            '900': cls.ADVANCED
        }
        
        # Check for exact match
        for key, value in mappings.items():
            if key in level_str:
                return value
        
        # Default to intermediate
        return cls.INTERMEDIATE
    
    @classmethod
    def get_expected_skill_level_range(cls, study_level):
        """Get the expected skill level range for a study level"""
        mappings = {
            cls.INTRODUCTORY: (1, 3),  # Novice to Competent
            cls.INTERMEDIATE: (2, 4),  # Beginner to Proficient  
            cls.ADVANCED: (3, 5),      # Competent to Expert
        }
        
        # Handle both enum and string inputs
        if isinstance(study_level, str):
            study_level = cls.from_string(study_level)
        
        return mappings.get(study_level, (2, 4))
    
    @classmethod
    def infer_from_text(cls, text: str) -> 'StudyLevel':
        """Infer study level from text content"""
        text_lower = text.lower()
        
        # Keywords for different levels
        intro_keywords = [
            'introduction', 'introductory', 'basic', 'fundamental', 'beginner',
            'foundation', 'elementary', 'principles', 'essentials', 'overview',
            'first year', '100 level', '1000 level', 'entry level'
        ]
        
        advanced_keywords = [
            'advanced', 'complex', 'specialized', 'expert', 'professional',
            'graduate', 'postgraduate', 'research', 'thesis', 'dissertation',
            'mastery', 'comprehensive', 'in-depth', 'critical analysis',
            'final year', '400 level', '4000 level', '500 level', 'senior'
        ]
        
        # Count keyword occurrences
        intro_count = sum(1 for keyword in intro_keywords if keyword in text_lower)
        advanced_count = sum(1 for keyword in advanced_keywords if keyword in text_lower)
        
        # Determine level based on keyword frequency
        if advanced_count > intro_count and advanced_count >= 2:
            return cls.ADVANCED
        elif intro_count > advanced_count and intro_count >= 2:
            return cls.INTRODUCTORY
        else:
            return cls.INTERMEDIATE


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