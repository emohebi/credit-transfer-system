"""
Data models for the Skill Assertion schema:

  Skill              — Deduplicated, portable, context-independent
  SkillAssertion     — Link: how/where/at what depth a skill is taught
  UnitOfCompetency   — VET unit metadata (from TGA / concordance)
  Qualification      — VET qualification (from concordance)
  Occupation         — ANZSCO occupation (from concordance)

Traversal chain:
  Skill ←(assertions)→ Unit →(concordance)→ Qualification →(concordance)→ Occupation

Design principle:
  Deduplicate skill LABELS, not teaching/context evidence.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class TeachingContext(str, Enum):
    PRACTICAL = "PRACTICAL"
    THEORETICAL = "THEORETICAL"
    HYBRID = "HYBRID"


class LevelOfEngagement(str, Enum):
    FOLLOW = "FOLLOW"       # Level 1
    ASSIST = "ASSIST"       # Level 2
    APPLY = "APPLY"         # Level 3
    ENABLE = "ENABLE"       # Level 4
    ENSURE_ADVISE = "ENSURE_ADVISE"  # Level 5
    INITIATE_INFLUENCE = "INITIATE_INFLUENCE"  # Level 6
    SET_STRATEGY = "SET_STRATEGY"  # Level 7

    @classmethod
    def from_int(cls, level: int) -> "LevelOfEngagement":
        mapping = {
            1: cls.FOLLOW, 2: cls.ASSIST, 3: cls.APPLY,
            4: cls.ENABLE, 5: cls.ENSURE_ADVISE,
            6: cls.INITIATE_INFLUENCE, 7: cls.SET_STRATEGY,
        }
        return mapping.get(level, cls.APPLY)


@dataclass
class Skill:
    """
    A portable, deduplicated skill.
    Survives curriculum change. Unit-agnostic.
    """
    skill_id: str                           # Persistent identifier (e.g. SKL-00042)
    preferred_label: str                    # Canonical skill name
    alternative_labels: List[str] = field(default_factory=list)
    definition: str = ""                    # Context-independent scope note
    category: str = ""                      # e.g. cognitive, technical
    facets: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Metadata (derived at build time)
    assertion_count: int = 0
    unit_codes: List[str] = field(default_factory=list)

    # Denormalised from concordance traversal (precomputed for search)
    qualification_codes: List[str] = field(default_factory=list)
    occupation_codes: List[str] = field(default_factory=list)


@dataclass
class SkillAssertion:
    """
    Link between a Skill and a Unit of Competency.
    Captures HOW and at WHAT DEPTH the skill is taught in a specific unit.
    This is where education-specific meaning sits.
    """
    assertion_id: str
    skill_id: str                           # FK → Skill
    unit_code: str                          # FK → Unit of Competency

    teaching_context: str                   # PRACTICAL / THEORETICAL / HYBRID
    level_of_engagement: str                # FOLLOW / ASSIST / APPLY / ENABLE / ...
    evidence: str = ""
    keywords: List[str] = field(default_factory=list)
    confidence: float = 0.0
    category: str = ""


@dataclass
class UnitOfCompetency:
    """
    A VET unit. Metadata comes from TGA + concordance.
    """
    unit_code: str
    unit_title: str = ""                    # From concordance code_name column
    training_package: str = ""

    # From concordance: one unit → many qualifications
    qualification_codes: List[str] = field(default_factory=list)

    # Derived
    skill_count: int = 0
    skill_ids: List[str] = field(default_factory=list)


@dataclass
class Qualification:
    """
    A VET qualification (e.g. Certificate III in Carpentry).
    From concordance. One qualification → many units, many ANZSCO occupations.
    """
    qualification_code: str
    qualification_title: str = ""

    # From concordance
    unit_codes: List[str] = field(default_factory=list)
    occupation_codes: List[str] = field(default_factory=list)

    # Derived via units → assertions → skills (precomputed)
    skill_ids: List[str] = field(default_factory=list)
    skill_count: int = 0


@dataclass
class Occupation:
    """
    An ANZSCO occupation (e.g. Carpenter 331212).
    From concordance. One occupation → many qualifications.
    """
    anzsco_code: str
    anzsco_title: str = ""

    # From concordance
    qualification_codes: List[str] = field(default_factory=list)

    # Derived via quals → units → assertions → skills (precomputed)
    skill_ids: List[str] = field(default_factory=list)
    skill_count: int = 0
