"""
Fixed enumeration classes with proper ordering for SkillLevel
"""

from enum import Enum


class SkillLevel(Enum):
    """SFIA proficiency levels for skills with ordering support"""
    FOLLOW = 1          # Level 1: Follow
    ASSIST = 2          # Level 2: Assist  
    APPLY = 3           # Level 3: Apply
    ENABLE = 4          # Level 4: Enable
    ENSURE_ADVISE = 5   # Level 5: Ensure and advise
    INITIATE_INFLUENCE = 6  # Level 6: Initiate and influence
    SET_STRATEGY = 7    # Level 7: Set strategy, inspire, mobilise
    
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
        """Parse SFIA skill level from string"""
        level_map = {
            "follow": cls.FOLLOW,
            "assist": cls.ASSIST,
            "apply": cls.APPLY,
            "enable": cls.ENABLE,
            "ensure": cls.ENSURE_ADVISE,
            "advise": cls.ENSURE_ADVISE,
            "initiate": cls.INITIATE_INFLUENCE,
            "influence": cls.INITIATE_INFLUENCE,
            "strategy": cls.SET_STRATEGY,
            "set_strategy": cls.SET_STRATEGY,
            # Legacy mappings for backward compatibility
            "novice": cls.FOLLOW,
            "beginner": cls.ASSIST,
            "competent": cls.APPLY,
            "proficient": cls.ENABLE,
            "expert": cls.ENSURE_ADVISE
        }
        return level_map.get(level_str.lower(), cls.APPLY)
    
    def get_sfia_description(self) -> str:
        """Get SFIA level description"""
        descriptions = {
            self.FOLLOW: "Works under close supervision, follows instructions, performs routine tasks",
            self.ASSIST: "Provides assistance, works under routine supervision, uses limited discretion",
            self.APPLY: "Performs varied tasks, works under general direction, exercises discretion",
            self.ENABLE: "Performs diverse complex activities, guides others, works autonomously",
            self.ENSURE_ADVISE: "Provides authoritative guidance, accountable for significant outcomes",
            self.INITIATE_INFLUENCE: "Has significant organizational influence, makes high-level decisions",
            self.SET_STRATEGY: "Operates at highest level, determines vision and strategy"
        }
        return descriptions.get(self, "Unknown level")
    
    def get_sfia_autonomy_level(self) -> str:
        """Get SFIA autonomy characteristics"""
        autonomy_levels = {
            self.FOLLOW: "close_supervision",
            self.ASSIST: "routine_supervision", 
            self.APPLY: "general_direction",
            self.ENABLE: "autonomous",
            self.ENSURE_ADVISE: "broad_direction",
            self.INITIATE_INFLUENCE: "strategic_authority",
            self.SET_STRATEGY: "full_authority"
        }
        return autonomy_levels.get(self, "general_direction")

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
    INTERPERSONAL = "interpersonal"
    DOMAIN_KNOWLEDGE = "domain_knowledge"


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
        """Get the expected SFIA skill level range for a study level"""
        mappings = {
            cls.INTRODUCTORY: (1, 3),  # Follow to Apply (mostly 2-3)
            cls.INTERMEDIATE: (2, 4),  # Assist to Enable (mostly 3)
            cls.ADVANCED: (3, 5),      # Apply to Ensure (mostly 3-4, rarely 5)
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