"""
Core data models for the Credit Transfer Analysis System
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from .enums import SkillLevel, SkillContext, SkillCategory, RecommendationType


# In models/base_models.py, update the Skill dataclass:

# In models/base_models.py, update the Skill dataclass:

@dataclass
class Skill:
    """Represents an extracted skill with evidence and derivation tracking"""
    name: str
    category: SkillCategory
    level: SkillLevel
    context: SkillContext
    code: str = ""  # Optional standardized skill code
    description: str = ""  # NEW: Brief description of skill application in context
    keywords: List[str] = field(default_factory=list)
    evidence_type: str = ""  
    confidence: float = 1.0
    source: str = ""
    evidence: str = ""  # Text excerpt showing this capability
    translation_rationale: str = ""  # How the skill was derived
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Skill):
            return False
        return self.name.lower() == other.name.lower()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "code": self.code,
            "name": self.name,
            "category": self.category.value,
            "level": self.level.name,
            "context": self.context.value,
            "description": self.description,  # NEW: Include description
            "keywords": self.keywords,
            "evidence_type": self.evidence_type,
            "confidence": self.confidence,
            "source": self.source,
            "evidence": self.evidence,
            "translation_rationale": self.translation_rationale,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Create from dictionary"""
        return cls(
            code=data.get("code", ""),
            name=data["name"],
            category=SkillCategory(data["category"]),
            level=SkillLevel[data["level"]],
            context=SkillContext(data["context"]),
            description=data.get("description", ""),  # NEW: Handle description
            keywords=data.get("keywords", []),
            evidence_type=data.get("evidence_type", ""),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", ""),
            evidence=data.get("evidence", ""),
            translation_rationale=data.get("translation_rationale", ""),
            metadata=data.get("metadata", {})
        )

@dataclass
class UnitOfCompetency:
    """VET Unit of Competency"""
    code: str
    name: str
    description: str
    learning_outcomes: List[str] = field(default_factory=list)
    assessment_requirements: str = ""
    nominal_hours: int = 0
    prerequisites: List[str] = field(default_factory=list)
    extracted_skills: List[Skill] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """Get all text content for processing"""
        parts = [
            self.name,
            self.description,
            " ".join(self.learning_outcomes),
            self.assessment_requirements
        ]
        return " ".join(filter(None, parts))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "learning_outcomes": self.learning_outcomes,
            "assessment_requirements": self.assessment_requirements,
            "nominal_hours": self.nominal_hours,
            "prerequisites": self.prerequisites,
            "extracted_skills": [s.to_dict() for s in self.extracted_skills],
            "metadata": self.metadata
        }


@dataclass
class VETQualification:
    """VET Qualification containing multiple units"""
    code: str
    name: str
    level: str  # Certificate III, IV, Diploma etc
    units: List[UnitOfCompetency] = field(default_factory=list)
    core_units: List[str] = field(default_factory=list)  # Codes of core units
    elective_units: List[str] = field(default_factory=list)  # Codes of elective units
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills from all units"""
        skills = []
        for unit in self.units:
            skills.extend(unit.extracted_skills)
        return skills
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "code": self.code,
            "name": self.name,
            "level": self.level,
            "units": [u.to_dict() for u in self.units],
            "core_units": self.core_units,
            "elective_units": self.elective_units,
            "metadata": self.metadata
        }


@dataclass
class UniCourse:
    """University Course"""
    code: str
    name: str
    description: str
    study_level: str  # e.g., "Introductory", "Intermediate", "Advanced", "Specialized"
    learning_outcomes: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)
    credit_points: int = 0
    topics: List[str] = field(default_factory=list)
    assessment: str = ""
    extracted_skills: List[Skill] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_full_text(self) -> str:
        """Get all text content for processing"""
        parts = [
            self.name,
            self.description,
            " ".join(self.learning_outcomes),
            " ".join(self.topics),
            self.assessment
        ]
        return " ".join(filter(None, parts))
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "study_level": self.study_level,
            "learning_outcomes": self.learning_outcomes,
            "prerequisites": self.prerequisites,
            "credit_points": self.credit_points,
            "topics": self.topics,
            "assessment": self.assessment,
            "extracted_skills": [s.to_dict() for s in self.extracted_skills],
            "metadata": self.metadata
        }


@dataclass
class UniQualification:
    """University Qualification/Program"""
    code: str
    name: str
    courses: List[UniCourse] = field(default_factory=list)
    total_credit_points: int = 0
    duration_years: int = 4
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_courses_by_level(self, level: str) -> List[UniCourse]:
        """Get courses for a specific study level"""
        return [c for c in self.courses if c.study_level == level]
    
    def get_all_study_levels(self) -> List[str]:
        """Get all unique study levels in the qualification"""
        return list(set(c.study_level for c in self.courses))
    
    def get_all_skills(self) -> List[Skill]:
        """Get all skills from all courses"""
        skills = []
        for course in self.courses:
            skills.extend(course.extracted_skills)
        return skills
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "code": self.code,
            "name": self.name,
            "courses": [c.to_dict() for c in self.courses],
            "total_credit_points": self.total_credit_points,
            "duration_years": self.duration_years,
            "metadata": self.metadata
        }


@dataclass
class SkillMapping:
    """Represents mapping between VET and Uni skills"""
    direct_matches: List[Dict[str, Any]] = field(default_factory=list)
    partial_matches: List[Dict[str, Any]] = field(default_factory=list)
    unmapped_vet: List[Skill] = field(default_factory=list)
    unmapped_uni: List[Skill] = field(default_factory=list)
    coverage_score: float = 0.0
    context_alignment: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CreditTransferRecommendation:
    """Recommendation for credit transfer"""
    vet_units: List[UnitOfCompetency]
    uni_course: UniCourse
    alignment_score: float
    skill_coverage: Dict[str, float]
    gaps: List[Skill]
    evidence: List[str]
    recommendation: RecommendationType
    conditions: List[str] = field(default_factory=list)
    confidence: float = 0.0
    edge_case_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_vet_unit_codes(self) -> List[str]:
        """Get list of VET unit codes"""
        return [f"{u.code}: {u.name}" for u in self.vet_units]
    
    def is_combination_transfer(self) -> bool:
        """Check if this is a combination of multiple VET units"""
        return len(self.vet_units) > 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "vet_unit_codes": self.get_vet_unit_codes(),
            "uni_course_code": self.uni_course.code,
            "uni_course_name": self.uni_course.name,
            "alignment_score": self.alignment_score,
            "skill_coverage": self.skill_coverage,
            "gaps": [s.to_dict() for s in self.gaps],
            "evidence": self.evidence,
            "recommendation": self.recommendation.value,
            "conditions": self.conditions,
            "confidence": self.confidence,
            "is_combination": self.is_combination_transfer(),
            "metadata": self.metadata
        }

@dataclass
class SkillMatchResult:
    """Result of matching two individual skills"""
    vet_skill: 'Skill'
    uni_skill: Optional['Skill']
    similarity_score: float
    level_compatibility: float
    match_type: str  # "Direct", "Partial", "Unmapped"
    reasoning: str
    combined_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)  # NEW: for context_similarity and other data