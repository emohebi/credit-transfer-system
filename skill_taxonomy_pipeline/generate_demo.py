#!/usr/bin/env python
"""
Generate demo data to test the search engine HTML output.
Creates a small skill_assertion_data.json and builds the HTML.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.export.search_engine import generate_search_html

# ── Demo data ─────────────────────────────────────────────────────

demo_data = {
    "metadata": {
        "generated_at": "2026-03-16T00:00:00",
        "pipeline": "skill-assertion-pipeline-demo",
        "total_skills": 8,
        "total_assertions": 22,
        "total_units": 14,
        "total_qualifications": 9,
        "total_occupations": 9,
        "facets": ["NAT", "TRF", "COG", "ASCED"],
    },
    "facets": {
        "NAT": {
            "name": "Skill Nature",
            "description": "Core competency type",
            "values": {
                "NAT.TEC": {"name": "Technical/Procedural", "description": "Practical industry-specific skills"},
                "NAT.COG": {"name": "Cognitive/Analytical", "description": "Analysis and reasoning"},
                "NAT.SOC": {"name": "Social/Interpersonal", "description": "Collaboration and communication"},
                "NAT.REG": {"name": "Regulatory/Compliance", "description": "Safety and compliance"},
            },
        },
        "TRF": {
            "name": "Transferability",
            "description": "How portable the skill is",
            "values": {
                "TRF.UNI": {"name": "Universal", "description": "Applicable everywhere"},
                "TRF.BRD": {"name": "Broad/Cross-Sector", "description": "Transferable across sectors"},
                "TRF.SEC": {"name": "Sector-Specific", "description": "Within a sector"},
            },
        },
        "COG": {
            "name": "Cognitive Complexity",
            "description": "Bloom's Taxonomy depth",
            "values": {
                "COG.APP": {"name": "Apply", "description": "Apply knowledge"},
                "COG.ANA": {"name": "Analyse", "description": "Analyse information"},
                "COG.EVA": {"name": "Evaluate", "description": "Evaluate and critique"},
            },
        },
        "ASCED": {
            "name": "ASCED Field",
            "description": "Field of Education",
            "values": {
                "0403": {"name": "Building", "description": "Building disciplines"},
                "0803": {"name": "Business and Management", "description": "Business disciplines"},
                "0613": {"name": "Public Health", "description": "Public Health disciplines"},
            },
        },
    },
    "skills": [
        {
            "skill_id": "SKL-00001-a1b2c3",
            "preferred_label": "Risk Assessment",
            "alternative_labels": ["Risk Assessment Processes", "Assess Communication Risks", "Risk Evaluation"],
            "definition": "The ability to identify, analyse and evaluate potential risks in workplace and project contexts.",
            "category": "cognitive",
            "facets": {
                "NAT": {"code": "NAT.COG", "name": "Cognitive/Analytical", "confidence": 0.92},
                "TRF": {"code": "TRF.BRD", "name": "Broad/Cross-Sector", "confidence": 0.88},
                "COG": {"code": "COG.EVA", "name": "Evaluate", "confidence": 0.85},
                "ASCED": {"code": "0803", "name": "Business and Management", "confidence": 0.71},
            },
            "assertion_count": 4,
            "unit_codes": ["BSBWHS411", "BSBOPS504", "CHCCOM003", "CPCCWHS2001"],
            "qualifications": [
                {"code": "BSB40520", "title": "Certificate IV in Leadership and Management"},
                {"code": "BSB50420", "title": "Diploma of Leadership and Management"},
                {"code": "CPC30220", "title": "Certificate III in Carpentry"},
                {"code": "CPC40120", "title": "Certificate IV in Building and Construction"},
                {"code": "CHC43015", "title": "Certificate IV in Ageing Support"}
            ],
            "occupations": [
                {"code": "149999", "title": "Hospitality, Retail and Service Managers nec"},
                {"code": "331212", "title": "Carpenter"},
                {"code": "133111", "title": "Construction Project Manager"},
                {"code": "423111", "title": "Aged or Disabled Carer"},
                {"code": "512111", "title": "Office Manager"}
            ],
            "context_distribution": {"PRACTICAL": 2, "THEORETICAL": 1, "HYBRID": 1},
            "level_distribution": {"APPLY": 2, "ENABLE": 1, "ASSIST": 1},
            "assertions": [
                {"assertion_id": "SA-000001", "unit_code": "BSBWHS411", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "conduct a workplace risk assessment in accordance with WHS legislation", "keywords": ["workplace", "WHS", "legislation"], "confidence": 0.92},
                {"assertion_id": "SA-000002", "unit_code": "BSBOPS504", "teaching_context": "THEORETICAL", "level_of_engagement": "ENABLE", "evidence": "analyse and evaluate risks using established frameworks", "keywords": ["business risk", "framework"], "confidence": 0.88},
                {"assertion_id": "SA-000003", "unit_code": "CHCCOM003", "teaching_context": "HYBRID", "level_of_engagement": "ASSIST", "evidence": "identify risks to effective communication in the workplace", "keywords": ["communication", "identify"], "confidence": 0.75},
                {"assertion_id": "SA-000004", "unit_code": "CPCCWHS2001", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "perform risk assessment procedures on construction site", "keywords": ["construction", "site", "hazard"], "confidence": 0.90},
            ],
        },
        {
            "skill_id": "SKL-00002-d4e5f6",
            "preferred_label": "Workplace Communication",
            "alternative_labels": ["Effective Communication", "Professional Communication"],
            "definition": "Skills in verbal and written communication for professional workplace settings.",
            "category": "interpersonal",
            "facets": {
                "NAT": {"code": "NAT.SOC", "name": "Social/Interpersonal", "confidence": 0.95},
                "TRF": {"code": "TRF.UNI", "name": "Universal", "confidence": 0.93},
                "COG": {"code": "COG.APP", "name": "Apply", "confidence": 0.80},
            },
            "assertion_count": 3,
            "unit_codes": ["BSBCMM211", "CHCCOM003", "SITXCOM010"],
            "qualifications": [
                {"code": "BSB40520", "title": "Certificate IV in Leadership and Management"},
                {"code": "CHC43015", "title": "Certificate IV in Ageing Support"},
                {"code": "SIT40521", "title": "Certificate IV in Kitchen Management"}
            ],
            "occupations": [
                {"code": "149999", "title": "Hospitality, Retail and Service Managers nec"},
                {"code": "423111", "title": "Aged or Disabled Carer"},
                {"code": "351311", "title": "Chef"},
                {"code": "512111", "title": "Office Manager"}
            ],
            "context_distribution": {"PRACTICAL": 1, "HYBRID": 2},
            "level_distribution": {"APPLY": 2, "ASSIST": 1},
            "assertions": [
                {"assertion_id": "SA-000005", "unit_code": "BSBCMM211", "teaching_context": "HYBRID", "level_of_engagement": "APPLY", "evidence": "apply communication strategies in workplace interactions", "keywords": ["verbal", "written"], "confidence": 0.90},
                {"assertion_id": "SA-000006", "unit_code": "CHCCOM003", "teaching_context": "HYBRID", "level_of_engagement": "APPLY", "evidence": "develop workplace communication strategies", "keywords": ["strategy", "workplace"], "confidence": 0.85},
                {"assertion_id": "SA-000007", "unit_code": "SITXCOM010", "teaching_context": "PRACTICAL", "level_of_engagement": "ASSIST", "evidence": "manage conflict through effective communication", "keywords": ["conflict", "customer"], "confidence": 0.82},
            ],
        },
        {
            "skill_id": "SKL-00003-g7h8i9",
            "preferred_label": "Whs Compliance",
            "alternative_labels": ["OHS Compliance", "Workplace Health And Safety"],
            "definition": "Ensure compliance with work health and safety regulations and standards.",
            "category": "regulatory",
            "facets": {
                "NAT": {"code": "NAT.REG", "name": "Regulatory/Compliance", "confidence": 0.97},
                "TRF": {"code": "TRF.BRD", "name": "Broad/Cross-Sector", "confidence": 0.90},
                "COG": {"code": "COG.APP", "name": "Apply", "confidence": 0.82},
                "ASCED": {"code": "0613", "name": "Public Health", "confidence": 0.65},
            },
            "assertion_count": 5,
            "unit_codes": ["BSBWHS411", "CPCCWHS2001", "HLTAID011", "RIIWHS201E", "TLILIC0003"],
            "qualifications": [
                {"code": "BSB40520", "title": "Certificate IV in Leadership and Management"},
                {"code": "BSB50420", "title": "Diploma of Leadership and Management"},
                {"code": "CPC30220", "title": "Certificate III in Carpentry"},
                {"code": "CPC40120", "title": "Certificate IV in Building and Construction"},
                {"code": "CHC43015", "title": "Certificate IV in Ageing Support"},
                {"code": "RII30920", "title": "Certificate III in Civil Construction"},
                {"code": "TLI30321", "title": "Certificate III in Supply Chain Operations"}
            ],
            "occupations": [
                {"code": "149999", "title": "Hospitality, Retail and Service Managers nec"},
                {"code": "331212", "title": "Carpenter"},
                {"code": "133111", "title": "Construction Project Manager"},
                {"code": "423111", "title": "Aged or Disabled Carer"},
                {"code": "512111", "title": "Office Manager"},
                {"code": "821211", "title": "Earthmoving Plant Operator"},
                {"code": "741111", "title": "Storeperson"}
            ],
            "context_distribution": {"PRACTICAL": 4, "THEORETICAL": 1},
            "level_distribution": {"APPLY": 3, "FOLLOW": 1, "ENABLE": 1},
            "assertions": [
                {"assertion_id": "SA-000008", "unit_code": "BSBWHS411", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "implement WHS policies and procedures", "keywords": ["WHS", "policy"], "confidence": 0.95},
                {"assertion_id": "SA-000009", "unit_code": "CPCCWHS2001", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "apply WHS requirements on construction sites", "keywords": ["construction", "PPE"], "confidence": 0.93},
                {"assertion_id": "SA-000010", "unit_code": "HLTAID011", "teaching_context": "PRACTICAL", "level_of_engagement": "FOLLOW", "evidence": "follow WHS procedures during first aid response", "keywords": ["first aid", "emergency"], "confidence": 0.88},
                {"assertion_id": "SA-000011", "unit_code": "RIIWHS201E", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "work safely and follow WHS policies in resources sector", "keywords": ["resources", "mining"], "confidence": 0.91},
                {"assertion_id": "SA-000012", "unit_code": "TLILIC0003", "teaching_context": "THEORETICAL", "level_of_engagement": "ENABLE", "evidence": "understand and apply WHS legislation for licensing", "keywords": ["licensing", "legislation"], "confidence": 0.87},
            ],
        },
        {
            "skill_id": "SKL-00004-j0k1l2",
            "preferred_label": "Blueprint Reading",
            "alternative_labels": ["Technical Drawing Interpretation", "Plan Reading"],
            "definition": "Read and interpret technical drawings, blueprints and specifications for construction work.",
            "category": "technical",
            "facets": {
                "NAT": {"code": "NAT.TEC", "name": "Technical/Procedural", "confidence": 0.94},
                "TRF": {"code": "TRF.SEC", "name": "Sector-Specific", "confidence": 0.91},
                "COG": {"code": "COG.ANA", "name": "Analyse", "confidence": 0.86},
                "ASCED": {"code": "0403", "name": "Building", "confidence": 0.92},
            },
            "assertion_count": 3,
            "unit_codes": ["CPCCCA2002", "CPCCCM2012", "CPCCWHS2001"],
            "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CPC40120", "title": "Certificate IV in Building and Construction"}],
            "occupations": [{"code": "331212", "title": "Carpenter"}, {"code": "133111", "title": "Construction Project Manager"}],
            "context_distribution": {"PRACTICAL": 2, "HYBRID": 1},
            "level_distribution": {"APPLY": 2, "ASSIST": 1},
            "assertions": [
                {"assertion_id": "SA-000013", "unit_code": "CPCCCA2002", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "read and interpret plans and specifications for carpentry work", "keywords": ["carpentry", "plans"], "confidence": 0.94},
                {"assertion_id": "SA-000014", "unit_code": "CPCCCM2012", "teaching_context": "HYBRID", "level_of_engagement": "ASSIST", "evidence": "interpret basic construction drawings", "keywords": ["drawings", "construction"], "confidence": 0.89},
                {"assertion_id": "SA-000015", "unit_code": "CPCCWHS2001", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "use site plans to identify WHS requirements", "keywords": ["site plans", "WHS"], "confidence": 0.85},
            ],
        },
        {
            "skill_id": "SKL-00005-m3n4o5",
            "preferred_label": "Customer Service",
            "alternative_labels": ["Client Service", "Customer Relations"],
            "definition": "Deliver quality service to customers and clients in diverse contexts.",
            "category": "interpersonal",
            "facets": {
                "NAT": {"code": "NAT.SOC", "name": "Social/Interpersonal", "confidence": 0.96},
                "TRF": {"code": "TRF.UNI", "name": "Universal", "confidence": 0.94},
                "COG": {"code": "COG.APP", "name": "Apply", "confidence": 0.78},
            },
            "assertion_count": 3,
            "unit_codes": ["SIRXCEG001", "SITXCOM010", "BSBCMM211"],
            "qualifications": [{"code": "SIR30216", "title": "Certificate III in Retail"}, {"code": "SIT40521", "title": "Certificate IV in Kitchen Management"}, {"code": "BSB40520", "title": "Certificate IV in Leadership and Management"}],
            "occupations": [{"code": "621111", "title": "Sales Assistant (General)"}, {"code": "351311", "title": "Chef"}, {"code": "149999", "title": "Hospitality, Retail and Service Managers nec"}, {"code": "512111", "title": "Office Manager"}],
            "context_distribution": {"PRACTICAL": 3},
            "level_distribution": {"APPLY": 2, "ASSIST": 1},
            "assertions": [
                {"assertion_id": "SA-000016", "unit_code": "SIRXCEG001", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "engage customers and deliver quality service", "keywords": ["retail", "customer"], "confidence": 0.95},
                {"assertion_id": "SA-000017", "unit_code": "SITXCOM010", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "manage customer service interactions in hospitality", "keywords": ["hospitality", "service"], "confidence": 0.91},
                {"assertion_id": "SA-000018", "unit_code": "BSBCMM211", "teaching_context": "PRACTICAL", "level_of_engagement": "ASSIST", "evidence": "apply customer service skills in business context", "keywords": ["business", "client"], "confidence": 0.87},
            ],
        },
        {
            "skill_id": "SKL-00006-p6q7r8",
            "preferred_label": "Project Planning",
            "alternative_labels": ["Project Scheduling", "Work Planning"],
            "definition": "Plan, schedule and organise project activities and resources.",
            "category": "cognitive",
            "facets": {
                "NAT": {"code": "NAT.COG", "name": "Cognitive/Analytical", "confidence": 0.89},
                "TRF": {"code": "TRF.BRD", "name": "Broad/Cross-Sector", "confidence": 0.87},
                "COG": {"code": "COG.ANA", "name": "Analyse", "confidence": 0.83},
                "ASCED": {"code": "0803", "name": "Business and Management", "confidence": 0.79},
            },
            "assertion_count": 2,
            "unit_codes": ["BSBPMG430", "CPCCBC4001"],
            "qualifications": [{"code": "BSB50420", "title": "Diploma of Leadership and Management"}, {"code": "CPC40120", "title": "Certificate IV in Building and Construction"}],
            "occupations": [{"code": "149999", "title": "Hospitality, Retail and Service Managers nec"}, {"code": "133111", "title": "Construction Project Manager"}],
            "context_distribution": {"THEORETICAL": 1, "HYBRID": 1},
            "level_distribution": {"ENABLE": 2},
            "assertions": [
                {"assertion_id": "SA-000019", "unit_code": "BSBPMG430", "teaching_context": "THEORETICAL", "level_of_engagement": "ENABLE", "evidence": "apply project scope management techniques", "keywords": ["scope", "schedule", "budget"], "confidence": 0.88},
                {"assertion_id": "SA-000020", "unit_code": "CPCCBC4001", "teaching_context": "HYBRID", "level_of_engagement": "ENABLE", "evidence": "plan construction projects including resources and timelines", "keywords": ["construction", "timeline", "resources"], "confidence": 0.85},
            ],
        },
        {
            "skill_id": "SKL-00007-s9t0u1",
            "preferred_label": "First Aid Response",
            "alternative_labels": ["Emergency First Aid"],
            "definition": "Provide initial emergency care and first aid response in workplace settings.",
            "category": "technical",
            "facets": {
                "NAT": {"code": "NAT.TEC", "name": "Technical/Procedural", "confidence": 0.93},
                "TRF": {"code": "TRF.BRD", "name": "Broad/Cross-Sector", "confidence": 0.90},
                "COG": {"code": "COG.APP", "name": "Apply", "confidence": 0.88},
                "ASCED": {"code": "0613", "name": "Public Health", "confidence": 0.82},
            },
            "assertion_count": 1,
            "unit_codes": ["HLTAID011"],
            "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CHC43015", "title": "Certificate IV in Ageing Support"}],
            "occupations": [{"code": "331212", "title": "Carpenter"}, {"code": "423111", "title": "Aged or Disabled Carer"}],
            "context_distribution": {"PRACTICAL": 1},
            "level_distribution": {"APPLY": 1},
            "assertions": [
                {"assertion_id": "SA-000021", "unit_code": "HLTAID011", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "provide first aid response including CPR", "keywords": ["CPR", "emergency", "first aid"], "confidence": 0.95},
            ],
        },
        {
            "skill_id": "SKL-00008-v2w3x4",
            "preferred_label": "Measurement And Calculation",
            "alternative_labels": ["Construction Measurement", "Trade Calculations"],
            "definition": "Perform measurements and calculations for trade and construction work.",
            "category": "technical",
            "facets": {
                "NAT": {"code": "NAT.TEC", "name": "Technical/Procedural", "confidence": 0.91},
                "TRF": {"code": "TRF.SEC", "name": "Sector-Specific", "confidence": 0.85},
                "COG": {"code": "COG.APP", "name": "Apply", "confidence": 0.90},
                "ASCED": {"code": "0403", "name": "Building", "confidence": 0.88},
            },
            "assertion_count": 1,
            "unit_codes": ["CPCCCM2012"],
            "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CPC40120", "title": "Certificate IV in Building and Construction"}],
            "occupations": [{"code": "331212", "title": "Carpenter"}, {"code": "133111", "title": "Construction Project Manager"}],
            "context_distribution": {"PRACTICAL": 1},
            "level_distribution": {"APPLY": 1},
            "assertions": [
                {"assertion_id": "SA-000022", "unit_code": "CPCCCM2012", "teaching_context": "PRACTICAL", "level_of_engagement": "APPLY", "evidence": "carry out measurements and calculations for construction", "keywords": ["measurement", "calculation", "tools"], "confidence": 0.92},
            ],
        },
    ],
    "units": [
        {"unit_code": "BSBWHS411", "unit_title": "Implement and monitor WHS policies, procedures and programs", "skill_count": 2, "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9"], "qualification_codes": ["BSB40520", "BSB50420"], "qualifications": [{"code": "BSB40520", "title": "Certificate IV in Leadership and Management"}, {"code": "BSB50420", "title": "Diploma of Leadership and Management"}]},
        {"unit_code": "BSBOPS504", "unit_title": "Manage business risk", "skill_count": 1, "skill_ids": ["SKL-00001-a1b2c3"], "qualification_codes": ["BSB50420"], "qualifications": [{"code": "BSB50420", "title": "Diploma of Leadership and Management"}]},
        {"unit_code": "CHCCOM003", "unit_title": "Develop workplace communication strategies", "skill_count": 2, "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6"], "qualification_codes": ["CHC43015"], "qualifications": [{"code": "CHC43015", "title": "Certificate IV in Ageing Support"}]},
        {"unit_code": "CPCCWHS2001", "unit_title": "Apply WHS requirements, policies and procedures in the construction industry", "skill_count": 3, "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00004-j0k1l2"], "qualification_codes": ["CPC30220", "CPC40120"], "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CPC40120", "title": "Certificate IV in Building and Construction"}]},
        {"unit_code": "BSBCMM211", "unit_title": "Apply communication skills", "skill_count": 2, "skill_ids": ["SKL-00002-d4e5f6", "SKL-00005-m3n4o5"], "qualification_codes": ["BSB40520"], "qualifications": [{"code": "BSB40520", "title": "Certificate IV in Leadership and Management"}]},
        {"unit_code": "SITXCOM010", "unit_title": "Manage conflict", "skill_count": 2, "skill_ids": ["SKL-00002-d4e5f6", "SKL-00005-m3n4o5"], "qualification_codes": ["SIT40521"], "qualifications": [{"code": "SIT40521", "title": "Certificate IV in Kitchen Management"}]},
        {"unit_code": "HLTAID011", "unit_title": "Provide First Aid", "skill_count": 2, "skill_ids": ["SKL-00003-g7h8i9", "SKL-00007-s9t0u1"], "qualification_codes": ["CPC30220", "CHC43015"], "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CHC43015", "title": "Certificate IV in Ageing Support"}]},
        {"unit_code": "RIIWHS201E", "unit_title": "Work safely and follow WHS policies and procedures", "skill_count": 1, "skill_ids": ["SKL-00003-g7h8i9"], "qualification_codes": ["RII30920"], "qualifications": [{"code": "RII30920", "title": "Certificate III in Civil Construction"}]},
        {"unit_code": "TLILIC0003", "unit_title": "Licence to operate a forklift truck", "skill_count": 1, "skill_ids": ["SKL-00003-g7h8i9"], "qualification_codes": ["TLI30321"], "qualifications": [{"code": "TLI30321", "title": "Certificate III in Supply Chain Operations"}]},
        {"unit_code": "CPCCCA2002", "unit_title": "Use carpentry tools and equipment", "skill_count": 1, "skill_ids": ["SKL-00004-j0k1l2"], "qualification_codes": ["CPC30220"], "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}]},
        {"unit_code": "CPCCCM2012", "unit_title": "Work safely at heights", "skill_count": 2, "skill_ids": ["SKL-00004-j0k1l2", "SKL-00008-v2w3x4"], "qualification_codes": ["CPC30220", "CPC40120"], "qualifications": [{"code": "CPC30220", "title": "Certificate III in Carpentry"}, {"code": "CPC40120", "title": "Certificate IV in Building and Construction"}]},
        {"unit_code": "SIRXCEG001", "unit_title": "Engage the customer", "skill_count": 1, "skill_ids": ["SKL-00005-m3n4o5"], "qualification_codes": ["SIR30216"], "qualifications": [{"code": "SIR30216", "title": "Certificate III in Retail"}]},
        {"unit_code": "BSBPMG430", "unit_title": "Apply project scope management techniques", "skill_count": 1, "skill_ids": ["SKL-00006-p6q7r8"], "qualification_codes": ["BSB50420"], "qualifications": [{"code": "BSB50420", "title": "Diploma of Leadership and Management"}]},
        {"unit_code": "CPCCBC4001", "unit_title": "Apply building codes and standards to the construction process", "skill_count": 1, "skill_ids": ["SKL-00006-p6q7r8"], "qualification_codes": ["CPC40120"], "qualifications": [{"code": "CPC40120", "title": "Certificate IV in Building and Construction"}]},
    ],
    "qualifications": [
        {"qualification_code": "BSB40520", "qualification_title": "Certificate IV in Leadership and Management", "unit_codes": ["BSBWHS411", "BSBCMM211"], "occupation_codes": ["149999", "512111"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6", "SKL-00003-g7h8i9", "SKL-00005-m3n4o5"], "skill_count": 4},
        {"qualification_code": "BSB50420", "qualification_title": "Diploma of Leadership and Management", "unit_codes": ["BSBWHS411", "BSBOPS504", "BSBPMG430"], "occupation_codes": ["149999"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00006-p6q7r8"], "skill_count": 3},
        {"qualification_code": "CPC30220", "qualification_title": "Certificate III in Carpentry", "unit_codes": ["CPCCWHS2001", "HLTAID011", "CPCCCA2002", "CPCCCM2012"], "occupation_codes": ["331212"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00004-j0k1l2", "SKL-00007-s9t0u1", "SKL-00008-v2w3x4"], "skill_count": 5},
        {"qualification_code": "CPC40120", "qualification_title": "Certificate IV in Building and Construction", "unit_codes": ["CPCCWHS2001", "CPCCCM2012", "CPCCBC4001"], "occupation_codes": ["133111"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00004-j0k1l2", "SKL-00006-p6q7r8", "SKL-00008-v2w3x4"], "skill_count": 5},
        {"qualification_code": "CHC43015", "qualification_title": "Certificate IV in Ageing Support", "unit_codes": ["CHCCOM003", "HLTAID011"], "occupation_codes": ["423111"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6", "SKL-00003-g7h8i9", "SKL-00007-s9t0u1"], "skill_count": 4},
        {"qualification_code": "SIT40521", "qualification_title": "Certificate IV in Kitchen Management", "unit_codes": ["SITXCOM010"], "occupation_codes": ["351311"], "skill_ids": ["SKL-00002-d4e5f6", "SKL-00005-m3n4o5"], "skill_count": 2},
        {"qualification_code": "RII30920", "qualification_title": "Certificate III in Civil Construction", "unit_codes": ["RIIWHS201E"], "occupation_codes": ["821211"], "skill_ids": ["SKL-00003-g7h8i9"], "skill_count": 1},
        {"qualification_code": "TLI30321", "qualification_title": "Certificate III in Supply Chain Operations", "unit_codes": ["TLILIC0003"], "occupation_codes": ["741111"], "skill_ids": ["SKL-00003-g7h8i9"], "skill_count": 1},
        {"qualification_code": "SIR30216", "qualification_title": "Certificate III in Retail", "unit_codes": ["SIRXCEG001"], "occupation_codes": ["621111"], "skill_ids": ["SKL-00005-m3n4o5"], "skill_count": 1},
    ],
    "occupations": [
        {"anzsco_code": "149999", "anzsco_title": "Hospitality, Retail and Service Managers nec", "qualification_codes": ["BSB40520", "BSB50420"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6", "SKL-00003-g7h8i9", "SKL-00005-m3n4o5", "SKL-00006-p6q7r8"], "skill_count": 5},
        {"anzsco_code": "331212", "anzsco_title": "Carpenter", "qualification_codes": ["CPC30220"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00004-j0k1l2", "SKL-00007-s9t0u1", "SKL-00008-v2w3x4"], "skill_count": 5},
        {"anzsco_code": "133111", "anzsco_title": "Construction Project Manager", "qualification_codes": ["CPC40120"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00003-g7h8i9", "SKL-00004-j0k1l2", "SKL-00006-p6q7r8", "SKL-00008-v2w3x4"], "skill_count": 5},
        {"anzsco_code": "423111", "anzsco_title": "Aged or Disabled Carer", "qualification_codes": ["CHC43015"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6", "SKL-00003-g7h8i9", "SKL-00007-s9t0u1"], "skill_count": 4},
        {"anzsco_code": "351311", "anzsco_title": "Chef", "qualification_codes": ["SIT40521"], "skill_ids": ["SKL-00002-d4e5f6", "SKL-00005-m3n4o5"], "skill_count": 2},
        {"anzsco_code": "512111", "anzsco_title": "Office Manager", "qualification_codes": ["BSB40520"], "skill_ids": ["SKL-00001-a1b2c3", "SKL-00002-d4e5f6", "SKL-00003-g7h8i9", "SKL-00005-m3n4o5"], "skill_count": 4},
        {"anzsco_code": "821211", "anzsco_title": "Earthmoving Plant Operator", "qualification_codes": ["RII30920"], "skill_ids": ["SKL-00003-g7h8i9"], "skill_count": 1},
        {"anzsco_code": "741111", "anzsco_title": "Storeperson", "qualification_codes": ["TLI30321"], "skill_ids": ["SKL-00003-g7h8i9"], "skill_count": 1},
        {"anzsco_code": "621111", "anzsco_title": "Sales Assistant (General)", "qualification_codes": ["SIR30216"], "skill_ids": ["SKL-00005-m3n4o5"], "skill_count": 1},
    ],
}


if __name__ == "__main__":
    out_dir = "output"
    os.makedirs(out_dir, exist_ok=True)

    # Enrich assertions with qualification_codes and occupation_codes from concordance
    unit_index = {u["unit_code"]: u for u in demo_data["units"]}
    qual_index = {q["qualification_code"]: q for q in demo_data["qualifications"]}

    for skill in demo_data["skills"]:
        for a in skill.get("assertions", []):
            u = unit_index.get(a["unit_code"], {})
            a_qual_codes = u.get("qualification_codes", [])
            a_occ_codes = []
            for qc in a_qual_codes:
                q = qual_index.get(qc, {})
                a_occ_codes.extend(q.get("occupation_codes", []))
            a["qualification_codes"] = a_qual_codes
            a["occupation_codes"] = sorted(set(a_occ_codes))

    html_path = os.path.join(out_dir, "skill_search.html")
    data_path = os.path.join(out_dir, "skill_search_data.js")

    with open(os.path.join(out_dir, "skill_assertion_data.json"), "w") as f:
        json.dump(demo_data, f, indent=2)

    generate_search_html(demo_data, html_path, data_path)
    print(f"✓ Demo generated:")
    print(f"  {html_path}")
    print(f"  {data_path}")
