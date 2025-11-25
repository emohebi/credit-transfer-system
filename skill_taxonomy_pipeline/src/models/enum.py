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
            "ensure_advise": cls.ENSURE_ADVISE,
            "initiate_influence": cls.INITIATE_INFLUENCE,
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