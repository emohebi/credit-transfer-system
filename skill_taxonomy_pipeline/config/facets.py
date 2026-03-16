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
            "code": "NAT.TEC", "name": "Technical/Procedural",
            "description": "Practical, industry-specific skills for operating tools, equipment, and technical systems.",
        },
        "NAT.COG": {
            "code": "NAT.COG", "name": "Cognitive/Analytical",
            "description": "Skills for analysis, reasoning, problem-solving, and informed decision-making.",
        },
        "NAT.SOC": {
            "code": "NAT.SOC", "name": "Social/Interpersonal",
            "description": "Skills for collaboration, communication, and managing interpersonal relationships.",
        },
        "NAT.SLF": {
            "code": "NAT.SLF", "name": "Self-Management",
            "description": "Capabilities for self-organisation, adaptability, and maintaining professional conduct.",
        },
        "NAT.FND": {
            "code": "NAT.FND", "name": "Foundational/Core",
            "description": "Essential skills in literacy, numeracy, and basic digital fluency.",
        },
        "NAT.REG": {
            "code": "NAT.REG", "name": "Regulatory/Compliance",
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
        "TRF.UNI": {"code": "TRF.UNI", "name": "Universal", "description": "Foundational skills applicable across all occupations and industries."},
        "TRF.BRD": {"code": "TRF.BRD", "name": "Broad/Cross-Sector", "description": "Specialist skills transferable across multiple industries and sectors."},
        "TRF.SEC": {"code": "TRF.SEC", "name": "Sector-Specific", "description": "Skills relevant within a specific sector or closely related industries."},
        "TRF.OCC": {"code": "TRF.OCC", "name": "Occupation-Specific", "description": "Highly specialized skills unique to a particular occupation or role."},
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
# Trimmed to narrow fields used in VET — full list available in original facets.py

ASCED_FIELD_OF_EDUCATION_FACET = {
    "facet_id": "ASCED",
    "facet_name": "ASCED Field of Education",
    "description": "Australian Standard Classification of Education (ASCED) at the narrow field (4-digit) level.",
    "multi_value": True,
    "values": {
        "0201": {"code": "0201", "name": "Computer Science", "description": "Computer Science disciplines."},
        "0203": {"code": "0203", "name": "Information Systems", "description": "Information Systems disciplines."},
        "0301": {"code": "0301", "name": "Manufacturing Engineering and Technology", "description": "Manufacturing Engineering and Technology."},
        "0303": {"code": "0303", "name": "Process and Resources Engineering", "description": "Process and Resources Engineering."},
        "0305": {"code": "0305", "name": "Automotive Engineering and Technology", "description": "Automotive Engineering and Technology."},
        "0307": {"code": "0307", "name": "Mechanical and Industrial Engineering and Technology", "description": "Mechanical and Industrial Engineering."},
        "0309": {"code": "0309", "name": "Civil Engineering", "description": "Civil Engineering disciplines."},
        "0313": {"code": "0313", "name": "Electrical and Electronic Engineering and Technology", "description": "Electrical and Electronic Engineering."},
        "0399": {"code": "0399", "name": "Other Engineering and Related Technologies", "description": "Other Engineering and Related Technologies."},
        "0401": {"code": "0401", "name": "Architecture and Urban Environment", "description": "Architecture and Urban Environment."},
        "0403": {"code": "0403", "name": "Building", "description": "Building disciplines."},
        "0501": {"code": "0501", "name": "Agriculture", "description": "Agriculture disciplines."},
        "0503": {"code": "0503", "name": "Horticulture and Viticulture", "description": "Horticulture and Viticulture."},
        "0509": {"code": "0509", "name": "Environmental Studies", "description": "Environmental Studies."},
        "0603": {"code": "0603", "name": "Nursing", "description": "Nursing disciplines."},
        "0613": {"code": "0613", "name": "Public Health", "description": "Public Health disciplines."},
        "0617": {"code": "0617", "name": "Rehabilitation Therapies", "description": "Rehabilitation Therapies."},
        "0699": {"code": "0699", "name": "Other Health", "description": "Other Health disciplines."},
        "0803": {"code": "0803", "name": "Business and Management", "description": "Business and Management disciplines."},
        "0805": {"code": "0805", "name": "Sales and Marketing", "description": "Sales and Marketing disciplines."},
        "0807": {"code": "0807", "name": "Tourism", "description": "Tourism disciplines."},
        "0809": {"code": "0809", "name": "Office Studies", "description": "Office Studies disciplines."},
        "0811": {"code": "0811", "name": "Banking, Finance and Related Fields", "description": "Banking, Finance and Related Fields."},
        "0905": {"code": "0905", "name": "Human Welfare Studies and Services", "description": "Human Welfare Studies and Services."},
        "0909": {"code": "0909", "name": "Law", "description": "Law disciplines."},
        "0911": {"code": "0911", "name": "Justice and Law Enforcement", "description": "Justice and Law Enforcement."},
        "0921": {"code": "0921", "name": "Sport and Recreation", "description": "Sport and Recreation."},
        "0999": {"code": "0999", "name": "Other Society and Culture", "description": "Other Society and Culture."},
        "1001": {"code": "1001", "name": "Performing Arts", "description": "Performing Arts disciplines."},
        "1003": {"code": "1003", "name": "Visual Arts and Crafts", "description": "Visual Arts and Crafts."},
        "1005": {"code": "1005", "name": "Graphic and Design Studies", "description": "Graphic and Design Studies."},
        "1007": {"code": "1007", "name": "Communication and Media Studies", "description": "Communication and Media Studies."},
        "1101": {"code": "1101", "name": "Food and Hospitality", "description": "Food and Hospitality disciplines."},
        "1103": {"code": "1103", "name": "Personal Services", "description": "Personal Services disciplines."},
    },
}

# ═══════════════════════════════════════════════════════════════════
#  AGGREGATE
# ═══════════════════════════════════════════════════════════════════

ALL_FACETS = {
    "NAT": SKILL_NATURE_FACET,
    "TRF": TRANSFERABILITY_FACET,
    "COG": COGNITIVE_COMPLEXITY_FACET,
    "ASCED": ASCED_FIELD_OF_EDUCATION_FACET,
}

MULTI_VALUE_FACETS = ["ASCED"]


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
