"""
Facet definitions for skill classification.
Only facets listed in FACETS_TO_ASSIGN (settings.py) will be used.

Each skill gets facet values on the Skill object (not on assertions).
These are portable, context-independent classifications.
"""

# ═══════════════════════════════════════════════════════════════════
#  FACET 1: SKILL NATURE (NAT)
# ═══════════════════════════════════════════════════════════════════

SKILL_NATURE_FACET = {
    "facet_id": "NAT",
    "facet_name": "Skill Nature",
    "description": "Defines the underlying nature of the skill by core competency type.",
    "values": {
        "NAT.TEC": {
            "code": "NAT.TEC", "name": "Technical and Procedural",
            "description": "Practical, industry-specific skills for operating tools, equipment, and technical systems.",
        },
        "NAT.COG": {
            "code": "NAT.COG", "name": "Cognitive and Analytical",
            "description": "Skills for analysis, reasoning, problem-solving, and informed decision-making.",
        },
        "NAT.SOC": {
            "code": "NAT.SOC", "name": "Social and Interpersonal",
            "description": "Skills for collaboration, communication, and managing interpersonal relationships.",
        },
        "NAT.SLF": {
            "code": "NAT.SLF", "name": "Self-Management",
            "description": "Capabilities for self-organisation, adaptability, and maintaining professional conduct.",
        },
        "NAT.FND": {
            "code": "NAT.FND", "name": "Foundational",
            "description": "Essential skills in literacy, numeracy, and basic digital fluency.",
        },
        "NAT.REG": {
            "code": "NAT.REG", "name": "Regulatory and Compliance",
            "description": "Skills ensuring safety, ethical practice, and compliance with standards and regulations.",
        },
    },
}

# ═══════════════════════════════════════════════════════════════════
#  FACET 2: TRANSFERABILITY (TRF)
# ═══════════════════════════════════════════════════════════════════

TRANSFERABILITY_FACET = {
    "facet_id": "TRF",
    "facet_name": "Transferability",
    "description": "Indicates how portable/transferable the skill is across contexts.",
    "values": {
        "TRF.UNI": {"code": "TRF.UNI", "name": "Universal", "description": "Foundational personal and interpersonal skills needed by all workers regardless of occupation: communication, numeracy, digital literacy, teamwork, time management, ethics, cultural awareness, self-management, problem solving, and workplace safety awareness. These are generic employability skills, not technical or trade skills."},
        "TRF.BRD": {"code": "TRF.BRD", "name": "Cross-Sector", "description": "Professional and management skills that apply across many industries without requiring specialist trade knowledge: project management, leadership, supervision, quality assurance, risk assessment, WHS management, training delivery, regulatory compliance, data analysis, financial management, reporting, stakeholder engagement, customer service, environmental management, supply chain coordination, and strategic planning."},
        "TRF.SEC": {"code": "TRF.SEC", "name": "Sector-Specific", "description": "Technical skills shared across a family of related occupations within a sector: diagnostic fault finding, inspection and testing, calibration and measurement, care planning and case management, clinical assessment, process monitoring and control, laboratory sampling, design and drafting, estimation and costing, automation programming, cybersecurity, event coordination, counselling, and forensic analysis."},
        "TRF.OCC": {"code": "TRF.OCC", "name": "Occupation-Specific", "description": "Hands-on practical trade and vocational skills requiring specific tools, equipment, materials, or physical techniques unique to an occupation: welding, bricklaying, wiring, plumbing, machining, cooking, hairdressing, concreting, crane operation, animal handling, medication administration, spray painting, forklift driving, drilling, sewing, massage, scaffolding, tiling, and other manual or procedural craft skills."},
    },
}

# ═══════════════════════════════════════════════════════════════════
#  FACET 3: COGNITIVE COMPLEXITY (COG) — Bloom's Taxonomy
# ═══════════════════════════════════════════════════════════════════

COGNITIVE_COMPLEXITY_FACET = {
    "facet_id": "COG",
    "facet_name": "Cognitive Complexity",
    "description": "Depth of cognitive processing required, aligned with Bloom's Taxonomy.",
    "values": {
        "COG.REM": {"code": "COG.REM", "name": "Remember", "level": 1, "description": "Recall and recognize facts, terms, and basic concepts."},
        "COG.UND": {"code": "COG.UND", "name": "Understand", "level": 2, "description": "Explain, interpret, and demonstrate understanding of concepts."},
        "COG.APP": {"code": "COG.APP", "name": "Apply", "level": 3, "description": "Apply knowledge and execute procedures in familiar contexts."},
        "COG.ANA": {"code": "COG.ANA", "name": "Analyse", "level": 4, "description": "Analyse information, identify relationships, and diagnose issues."},
        "COG.EVA": {"code": "COG.EVA", "name": "Evaluate", "level": 5, "description": "Evaluate, critique, and make judgments using defined criteria."},
        "COG.CRE": {"code": "COG.CRE", "name": "Create", "level": 6, "description": "Create, design, and develop innovative solutions or original work."},
    },
}

# ═══════════════════════════════════════════════════════════════════
#  FACET 4: ASCED FIELD OF EDUCATION
# ═══════════════════════════════════════════════════════════════════

# [ASCED facet unchanged — keeping full definition from original]
# Importing from the original to avoid duplicating 500+ lines
try:
    from config._asced_values import ASCED_FIELD_OF_EDUCATION_FACET
except ImportError:
    # Inline minimal definition if _asced_values not available
    ASCED_FIELD_OF_EDUCATION_FACET = {
        "facet_id": "ASCED",
        "facet_name": "ASCED Field of Education",
        "description": "Australian Standard Classification of Education (ASCED) - Field of Education classification at the narrow field (4-digit) level",
        "standard": "Australian Standard Classification of Education (ASCED) 2001",
        "reference": "https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/latest-release",
        "multi_value": True,
        "values": {},  # Will be populated from _asced_values.py
    }

# ═══════════════════════════════════════════════════════════════════
#  FACET 5: PROFICIENCY LEVEL (LVL) — SFIA-aligned
# ═══════════════════════════════════════════════════════════════════

PROFICIENCY_LEVEL_FACET = {
    "facet_id": "LVL",
    "facet_name": "Proficiency Level",
    "description": "SFIA-aligned proficiency level indicating depth of mastery.",
    "values": {
        "LVL.1": {"code": "LVL.1", "name": "Follow", "level": 1, "description": "Perform tasks under close direction and supervision."},
        "LVL.2": {"code": "LVL.2", "name": "Assist", "level": 2, "description": "Assist others and perform routine tasks with some guidance."},
        "LVL.3": {"code": "LVL.3", "name": "Apply", "level": 3, "description": "Apply knowledge and skills independently in familiar contexts."},
        "LVL.4": {"code": "LVL.4", "name": "Enable", "level": 4, "description": "Enable others and manage work within defined parameters."},
        "LVL.5": {"code": "LVL.5", "name": "Ensure and Advise", "level": 5, "description": "Ensure compliance and advise on best practice."},
        "LVL.6": {"code": "LVL.6", "name": "Initiate and Influence", "level": 6, "description": "Initiate improvements and influence organisational direction."},
        "LVL.7": {"code": "LVL.7", "name": "Set Strategy", "level": 7, "description": "Set strategy, inspire, and mobilise at the highest level."},
    },
}

# ═══════════════════════════════════════════════════════════════════
#  FACET 6: TRANSFERABLE HUMAN ABILITY (THA)
# ═══════════════════════════════════════════════════════════════════

from config.tha_facet import TRANSFERABLE_HUMAN_ABILITY_FACET

# ═══════════════════════════════════════════════════════════════════
#  AGGREGATE
# ═══════════════════════════════════════════════════════════════════

ALL_FACETS = {
    "NAT": SKILL_NATURE_FACET,
    "TRF": TRANSFERABILITY_FACET,
    "COG": COGNITIVE_COMPLEXITY_FACET,
    # "ASCED": ASCED_FIELD_OF_EDUCATION_FACET,
    "LVL": PROFICIENCY_LEVEL_FACET,
    "THA": TRANSFERABLE_HUMAN_ABILITY_FACET,
}

MULTI_VALUE_FACETS = []

# Ordered list of facets for processing priority
# TRF must be assigned before THA (THA candidates are scoped by TRF)
ORDERED_FACETS = ["NAT", "TRF", "COG", "LVL", "THA"]

# Default facet assignment priority
FACET_PRIORITY = ["NAT", "TRF", "COG", "LVL", "THA"]


def get_facet_text_for_embedding(facet_id: str, value_code: str) -> str:
    """Text representation of a facet value for embedding similarity."""
    facet = ALL_FACETS.get(facet_id, {})
    value = facet.get("values", {}).get(value_code, {})
    parts = [value.get("name", ""), value.get("description", "")]
    return ". ".join(p for p in parts if p)


def get_all_facet_embeddings_texts() -> dict:
    """All facet values as {facet_id: {value_code: text}} for precomputation."""
    result = {}
    for facet_id, facet in ALL_FACETS.items():
        result[facet_id] = {}
        for value_code in facet.get("values", {}):
            result[facet_id][value_code] = get_facet_text_for_embedding(facet_id, value_code)
    return result