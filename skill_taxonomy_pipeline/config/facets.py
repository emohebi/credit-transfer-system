"""
Multi-Dimensional Faceted Taxonomy Configuration
Defines all facets (dimensions) for skill classification

Each skill will be assigned values across multiple independent facets,
enabling flexible querying and multiple views of the same skill set.
"""

# ═══════════════════════════════════════════════════════════════════════════
#  FACET 1: SKILL NATURE (NAT) - What type of competency is this?
# ═══════════════════════════════════════════════════════════════════════════

SKILL_NATURE_FACET = {
    "facet_id": "NAT",
    "facet_name": "Skill Nature",
    "description": "Classifies the fundamental type of competency",
    "values": {
        "NAT.TEC": {
            "code": "NAT.TEC",
            "name": "Technical/Procedural",
            "description": "Industry-specific procedural and practical skills involving tools, equipment, or technical processes",
            "keywords": ["operate", "install", "maintain", "repair", "build", "construct", "configure", "calibrate", 
                        "assemble", "fabricate", "weld", "machine", "program", "code", "develop", "test",
                        "equipment", "machinery", "tools", "systems", "hardware", "software", "technical"],
            "subcategories": {
                "NAT.TEC.TRD": "Trade/Craft skills",
                "NAT.TEC.OPR": "Equipment/Machine operation",
                "NAT.TEC.DIG": "Digital/Software tools",
                "NAT.TEC.SCI": "Scientific/Technical procedures"
            }
        },
        "NAT.COG": {
            "code": "NAT.COG",
            "name": "Cognitive/Analytical",
            "description": "Thinking, reasoning, problem-solving and analytical capabilities",
            "keywords": ["analyse", "analyze", "evaluate", "assess", "interpret", "synthesise", "synthesize",
                        "problem-solving", "critical thinking", "decision", "judgement", "judgment", "reason",
                        "diagnose", "troubleshoot", "investigate", "research", "plan", "design", "strategise"],
            "subcategories": {
                "NAT.COG.ANA": "Analytical thinking",
                "NAT.COG.PRB": "Problem solving",
                "NAT.COG.DEC": "Decision making",
                "NAT.COG.CRE": "Creative/Innovative thinking"
            }
        },
        "NAT.SOC": {
            "code": "NAT.SOC",
            "name": "Social/Interpersonal",
            "description": "Working with others, communication, and relationship management",
            "keywords": ["communicate", "collaborate", "team", "lead", "mentor", "coach", "negotiate",
                        "customer", "client", "stakeholder", "present", "facilitate", "mediate",
                        "counsel", "support", "assist", "serve", "interact", "relationship"],
            "subcategories": {
                "NAT.SOC.COM": "Communication",
                "NAT.SOC.COL": "Collaboration/Teamwork",
                "NAT.SOC.LDR": "Leadership/Influence",
                "NAT.SOC.SRV": "Service/Customer orientation"
            }
        },
        "NAT.SLF": {
            "code": "NAT.SLF",
            "name": "Self-Management",
            "description": "Managing oneself, personal effectiveness, and professional conduct",
            "keywords": ["organise", "organize", "prioritise", "prioritize", "manage time", "adapt",
                        "initiative", "self-directed", "autonomous", "resilient", "flexible",
                        "learn", "develop", "improve", "reflect", "goal", "professional"],
            "subcategories": {
                "NAT.SLF.ORG": "Organisation/Planning",
                "NAT.SLF.ADP": "Adaptability/Flexibility",
                "NAT.SLF.INI": "Initiative/Enterprise",
                "NAT.SLF.LRN": "Learning agility"
            }
        },
        "NAT.FND": {
            "code": "NAT.FND",
            "name": "Foundational/Core",
            "description": "Basic foundational capabilities including literacy, numeracy, and digital basics",
            "keywords": ["read", "write", "calculate", "measure", "count", "literacy", "numeracy",
                        "digital", "computer", "basic", "fundamental", "core", "essential",
                        "comprehend", "interpret text", "document"],
            "subcategories": {
                "NAT.FND.LIT": "Literacy",
                "NAT.FND.NUM": "Numeracy",
                "NAT.FND.DFL": "Digital fluency"
            }
        },
        "NAT.REG": {
            "code": "NAT.REG",
            "name": "Regulatory/Compliance",
            "description": "Safety, ethics, quality, and regulatory compliance",
            "keywords": ["safety", "WHS", "OHS", "compliance", "regulation", "standard", "quality",
                        "audit", "inspect", "ethics", "legal", "policy", "procedure", "protocol",
                        "risk", "hazard", "environment", "sustainable"],
            "subcategories": {
                "NAT.REG.WHS": "Work health & safety",
                "NAT.REG.ETH": "Ethics & professional conduct",
                "NAT.REG.QUA": "Quality assurance",
                "NAT.REG.ENV": "Environmental compliance"
            }
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 2: TRANSFERABILITY (TRF) - How portable is this skill?
# ═══════════════════════════════════════════════════════════════════════════

TRANSFERABILITY_FACET = {
    "facet_id": "TRF",
    "facet_name": "Transferability",
    "description": "Indicates how portable/transferable the skill is across contexts",
    "values": {
        "TRF.UNI": {
            "code": "TRF.UNI",
            "name": "Universal",
            "score": 4,
            "description": "Foundational skills applicable across all occupations and industries",
            "keywords": ["communication", "teamwork", "problem solving", "learning", "adaptability",
                        "critical thinking", "time management", "ethics", "work ethic", "collaboration",
                        "initiative", "resilience", "numeracy", "literacy", "digital literacy"],
            "examples": ["Oral communication", "Written communication", "Teamwork", "Problem solving",
                        "Time management", "Adaptability", "Learning agility"]
        },
        "TRF.BRD": {
            "code": "TRF.BRD",
            "name": "Broad/Cross-Sector",
            "score": 3,
            "description": "Specialist skills transferable across multiple industries and sectors",
            "keywords": ["project management", "customer service", "data analysis", "quality assurance",
                        "WHS", "supervision", "budgeting", "reporting", "documentation", "training",
                        "coordination", "scheduling", "compliance", "risk management"],
            "examples": ["Project management", "Customer service", "Data analysis", "Quality assurance",
                        "Supervision", "Budget management", "Report writing"]
        },
        "TRF.SEC": {
            "code": "TRF.SEC",
            "name": "Sector-Specific",
            "score": 2,
            "description": "Skills relevant within a specific sector or closely related industries",
            "keywords": ["industry", "sector", "domain", "specialised", "specialized", "field-specific",
                        "trade", "profession", "discipline"],
            "examples": ["Healthcare protocols", "Construction methods", "Manufacturing processes",
                        "Hospitality standards", "Agricultural techniques"]
        },
        "TRF.OCC": {
            "code": "TRF.OCC",
            "name": "Occupation-Specific",
            "score": 1,
            "description": "Highly specialized skills unique to particular occupation or role",
            "keywords": ["certification", "licensed", "regulated", "specific equipment", "proprietary",
                        "unique", "specialised", "specialized", "technical", "expert"],
            "examples": ["Welding certification", "Dental procedures", "Legal drafting",
                        "Aircraft maintenance", "Specific machinery operation"]
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 3: COGNITIVE COMPLEXITY (COG) - Bloom's Taxonomy inspired
# ═══════════════════════════════════════════════════════════════════════════

COGNITIVE_COMPLEXITY_FACET = {
    "facet_id": "COG",
    "facet_name": "Cognitive Complexity",
    "description": "Level of cognitive processing required (based on Bloom's Taxonomy)",
    "values": {
        "COG.REM": {
            "code": "COG.REM",
            "name": "Remember",
            "level": 1,
            "description": "Recall facts, terms, basic concepts, and procedures",
            "keywords": ["recall", "recognise", "recognize", "identify", "list", "name", "define",
                        "describe", "state", "locate", "find", "memorise", "memorize"],
            "verbs": ["define", "duplicate", "list", "memorize", "recall", "repeat", "state"]
        },
        "COG.UND": {
            "code": "COG.UND",
            "name": "Understand",
            "level": 2,
            "description": "Explain ideas or concepts, interpret meaning",
            "keywords": ["explain", "interpret", "summarise", "summarize", "classify", "compare",
                        "contrast", "discuss", "distinguish", "paraphrase", "predict"],
            "verbs": ["classify", "describe", "discuss", "explain", "identify", "locate", "recognize",
                      "report", "select", "translate"]
        },
        "COG.APP": {
            "code": "COG.APP",
            "name": "Apply",
            "level": 3,
            "description": "Use information in standard situations, execute procedures",
            "keywords": ["apply", "use", "implement", "execute", "perform", "carry out", "demonstrate",
                        "operate", "practice", "schedule", "sketch", "solve"],
            "verbs": ["execute", "implement", "solve", "use", "demonstrate", "interpret", "operate",
                      "schedule", "sketch"]
        },
        "COG.ANA": {
            "code": "COG.ANA",
            "name": "Analyse",
            "level": 4,
            "description": "Break down information, diagnose, troubleshoot, draw connections",
            "keywords": ["analyse", "analyze", "diagnose", "troubleshoot", "examine", "investigate",
                        "differentiate", "organise", "organize", "attribute", "deconstruct", "outline"],
            "verbs": ["differentiate", "organize", "relate", "compare", "contrast", "distinguish",
                      "examine", "experiment", "question", "test"]
        },
        "COG.EVA": {
            "code": "COG.EVA",
            "name": "Evaluate",
            "level": 5,
            "description": "Assess, judge, audit, critique, make decisions based on criteria",
            "keywords": ["evaluate", "assess", "judge", "audit", "critique", "justify", "appraise",
                        "argue", "defend", "select", "support", "value", "review", "recommend"],
            "verbs": ["appraise", "argue", "defend", "judge", "select", "support", "value", "critique",
                      "weigh"]
        },
        "COG.CRE": {
            "code": "COG.CRE",
            "name": "Create",
            "level": 6,
            "description": "Design, innovate, develop new solutions, produce original work",
            "keywords": ["create", "design", "develop", "innovate", "produce", "construct", "generate",
                        "plan", "compose", "formulate", "invent", "devise", "assemble", "author"],
            "verbs": ["design", "assemble", "construct", "conjecture", "develop", "formulate",
                      "author", "investigate"]
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 4: WORK CONTEXT (CTX) - O*NET inspired work activity types
# ═══════════════════════════════════════════════════════════════════════════

WORK_CONTEXT_FACET = {
    "facet_id": "CTX",
    "facet_name": "Work Context",
    "description": "Primary type of work activity the skill involves",
    "values": {
        "CTX.INF": {
            "code": "CTX.INF",
            "name": "Information Activities",
            "description": "Working with data, information, and knowledge",
            "keywords": ["data", "information", "document", "record", "report", "research", "analyse",
                        "analyze", "process", "interpret", "compile", "database", "spreadsheet"],
            "subcategories": {
                "CTX.INF.GAT": "Gathering information",
                "CTX.INF.PRC": "Processing information",
                "CTX.INF.ANA": "Analysing information",
                "CTX.INF.DOC": "Documenting/Recording"
            }
        },
        "CTX.PEO": {
            "code": "CTX.PEO",
            "name": "People Activities",
            "description": "Working with and through people",
            "keywords": ["customer", "client", "patient", "student", "team", "staff", "supervise",
                        "train", "mentor", "coach", "counsel", "serve", "assist", "communicate"],
            "subcategories": {
                "CTX.PEO.SRV": "Serving/Assisting",
                "CTX.PEO.TEA": "Teaching/Training",
                "CTX.PEO.SUP": "Supervising/Managing",
                "CTX.PEO.NEG": "Negotiating/Influencing"
            }
        },
        "CTX.THG": {
            "code": "CTX.THG",
            "name": "Things/Physical Activities",
            "description": "Working with physical objects, equipment, and materials",
            "keywords": ["equipment", "machinery", "tool", "material", "build", "construct", "repair",
                        "maintain", "operate", "handle", "install", "assemble", "physical", "manual"],
            "subcategories": {
                "CTX.THG.OPR": "Operating equipment",
                "CTX.THG.BLD": "Building/Constructing",
                "CTX.THG.REP": "Repairing/Maintaining",
                "CTX.THG.HND": "Handling materials"
            }
        },
        "CTX.SYS": {
            "code": "CTX.SYS",
            "name": "Systems Activities",
            "description": "Working with processes, systems, and organizational elements",
            "keywords": ["system", "process", "plan", "schedule", "coordinate", "monitor", "control",
                        "optimise", "optimize", "improve", "manage", "organize", "organise", "workflow"],
            "subcategories": {
                "CTX.SYS.PLN": "Planning/Scheduling",
                "CTX.SYS.CRD": "Coordinating",
                "CTX.SYS.MON": "Monitoring/Controlling",
                "CTX.SYS.OPT": "Optimising/Improving"
            }
        },
        "CTX.IDE": {
            "code": "CTX.IDE",
            "name": "Ideas/Creative Activities",
            "description": "Working with concepts, designs, and creative outputs",
            "keywords": ["design", "create", "innovate", "concept", "idea", "creative", "artistic",
                        "develop", "invent", "compose", "write", "produce", "strategy"],
            "subcategories": {
                "CTX.IDE.DSN": "Designing",
                "CTX.IDE.INN": "Innovating",
                "CTX.IDE.STR": "Strategising"
            }
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 5: FUTURE READINESS (FUT) - Automation/AI relationship
# ═══════════════════════════════════════════════════════════════════════════

FUTURE_READINESS_FACET = {
    "facet_id": "FUT",
    "facet_name": "Future Readiness",
    "description": "Relationship with automation/AI and future labor market demand",
    "values": {
        "FUT.HUM": {
            "code": "FUT.HUM",
            "name": "Uniquely Human",
            "score": 4,
            "description": "Skills that are difficult to automate, requiring human judgment, empathy, or creativity",
            "keywords": ["empathy", "emotional intelligence", "creativity", "innovation", "leadership",
                        "negotiation", "complex problem", "ethical", "judgment", "intuition", "care",
                        "relationship", "trust", "mentoring", "coaching", "counselling"],
            "trend": "High demand, hard to automate"
        },
        "FUT.COL": {
            "code": "FUT.COL",
            "name": "Human-AI Collaborative",
            "score": 3,
            "description": "Skills enhanced by AI tools, requiring human oversight and collaboration",
            "keywords": ["AI-assisted", "data-driven", "augmented", "hybrid", "oversight", "validate",
                        "interpret results", "prompt", "supervise AI", "human-in-the-loop"],
            "trend": "Growing demand, AI-augmented"
        },
        "FUT.AUG": {
            "code": "FUT.AUG",
            "name": "AI-Augmentable",
            "score": 2,
            "description": "Skills where AI can significantly assist but human input remains valuable",
            "keywords": ["software", "analysis", "reporting", "documentation", "research", "translation",
                        "content", "design", "coding", "programming"],
            "trend": "Stable, AI-enhanced productivity"
        },
        "FUT.AUT": {
            "code": "FUT.AUT",
            "name": "Automatable",
            "score": 1,
            "description": "Routine procedural tasks susceptible to automation",
            "keywords": ["routine", "repetitive", "manual data", "basic entry", "standard procedure",
                        "simple calculation", "filing", "sorting", "copying", "transcription"],
            "trend": "Declining demand, automation risk"
        },
        "FUT.EMG": {
            "code": "FUT.EMG",
            "name": "Emerging",
            "score": 5,
            "description": "New skill areas driven by emerging technologies and trends",
            "keywords": ["AI", "machine learning", "cybersecurity", "blockchain", "quantum", "IoT",
                        "renewable", "sustainability", "circular economy", "green", "EV", "battery",
                        "cloud", "data science", "automation engineering"],
            "trend": "Rapid growth, emerging demand"
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 6: LEARNING CONTEXT (LRN) - How/where the skill is typically learned
# ═══════════════════════════════════════════════════════════════════════════

LEARNING_CONTEXT_FACET = {
    "facet_id": "LRN",
    "facet_name": "Learning Context",
    "description": "Primary context in which the skill is typically developed",
    "values": {
        "LRN.THE": {
            "code": "LRN.THE",
            "name": "Theoretical/Academic",
            "description": "Primarily conceptual learning in classroom/academic settings",
            "keywords": ["theory", "concept", "principle", "academic", "classroom", "lecture",
                        "study", "knowledge", "understand", "learn", "course"],
            "environment": "Classroom, lecture, online learning"
        },
        "LRN.PRA": {
            "code": "LRN.PRA",
            "name": "Practical/Hands-on",
            "description": "Hands-on application in workshops, labs, or simulated environments",
            "keywords": ["practical", "hands-on", "workshop", "lab", "laboratory", "demonstration",
                        "practice", "simulation", "exercise", "drill", "training"],
            "environment": "Workshop, laboratory, training facility"
        },
        "LRN.WRK": {
            "code": "LRN.WRK",
            "name": "Workplace/On-the-Job",
            "description": "Skills developed directly through workplace experience",
            "keywords": ["workplace", "on-the-job", "apprenticeship", "traineeship", "work placement",
                        "internship", "experience", "real-world", "industry", "actual"],
            "environment": "Actual workplace, apprenticeship"
        },
        "LRN.HYB": {
            "code": "LRN.HYB",
            "name": "Hybrid/Blended",
            "description": "Combination of theoretical knowledge and practical application",
            "keywords": ["blended", "hybrid", "integrated", "combined", "mixed", "work-integrated",
                        "dual", "theory and practice"],
            "environment": "Mixed classroom and workplace"
        },
        "LRN.DIG": {
            "code": "LRN.DIG",
            "name": "Digital/Self-Paced",
            "description": "Primarily developed through digital platforms and self-directed learning",
            "keywords": ["online", "e-learning", "digital", "self-paced", "virtual", "remote",
                        "distance", "MOOC", "tutorial", "video"],
            "environment": "Online, virtual platforms"
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 7: DIGITAL INTENSITY (DIG) - Level of digital tool usage
# ═══════════════════════════════════════════════════════════════════════════

DIGITAL_INTENSITY_FACET = {
    "facet_id": "DIG",
    "facet_name": "Digital Intensity",
    "description": "Level of digital tool and technology usage required",
    "values": {
        "DIG.MIN": {
            "code": "DIG.MIN",
            "name": "Minimal Digital",
            "level": 0,
            "description": "Primarily manual/physical tasks with negligible digital tool usage",
            "keywords": ["manual", "physical", "hands-on", "traditional", "non-digital"],
            "percentage": "0-10% digital"
        },
        "DIG.LOW": {
            "code": "DIG.LOW",
            "name": "Low Digital",
            "level": 1,
            "description": "Basic digital literacy, simple tool usage",
            "keywords": ["email", "basic computer", "POS", "simple software", "word processing"],
            "percentage": "11-30% digital"
        },
        "DIG.MED": {
            "code": "DIG.MED",
            "name": "Medium Digital",
            "level": 2,
            "description": "Regular use of specialized software and digital platforms",
            "keywords": ["software", "application", "system", "platform", "database", "spreadsheet",
                        "industry software", "CAD", "CRM", "ERP"],
            "percentage": "31-60% digital"
        },
        "DIG.HIG": {
            "code": "DIG.HIG",
            "name": "High Digital",
            "level": 3,
            "description": "Advanced digital skills, complex software, data manipulation",
            "keywords": ["programming", "coding", "data analytics", "digital design", "system admin",
                        "database management", "network", "development", "automation"],
            "percentage": "61-85% digital"
        },
        "DIG.ADV": {
            "code": "DIG.ADV",
            "name": "Advanced Digital",
            "level": 4,
            "description": "Cutting-edge technology, AI/ML, emerging tech",
            "keywords": ["AI", "machine learning", "cloud architecture", "cybersecurity", "IoT",
                        "blockchain", "data science", "DevOps", "full-stack"],
            "percentage": "86-100% digital"
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 8: ASCED FIELD OF EDUCATION (ASCED) - Australian Standard Classification of Education
#  Uses 4-digit narrow field codes as primary keys
# ═══════════════════════════════════════════════════════════════════════════

ASCED_FIELD_OF_EDUCATION_FACET = {
    "facet_id": "ASCED",
    "facet_name": "ASCED Field of Education",
    "description": "Australian Standard Classification of Education (ASCED) - Field of Education classification at the narrow field (4-digit) level",
    "standard": "Australian Standard Classification of Education (ASCED) 2001",
    "reference": "https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/latest-release",
    "multi_value": True,
    "values": {
        # ─────────────────────────────────────────────────────────────────────
        # 01 - Natural and Physical Sciences
        # ─────────────────────────────────────────────────────────────────────
        "0101": {
            "code": "0101",
            "name": "Mathematical Sciences",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Mathematics, statistics, operations research, and actuarial science. Includes algebra, calculus, geometry, probability, statistical analysis, and mathematical modeling.",
            "keywords": ["mathematics", "statistics", "algebra", "calculus", "geometry", "probability", "statistical analysis", 
                        "mathematical modeling", "operations research", "actuarial", "quantitative analysis", "numerical methods",
                        "data analysis", "mathematical computation", "applied mathematics"]
        },
        "0103": {
            "code": "0103",
            "name": "Physics and Astronomy",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Physics, astrophysics, and astronomy. Includes mechanics, thermodynamics, electromagnetism, optics, quantum physics, and astronomical observation.",
            "keywords": ["physics", "astronomy", "astrophysics", "mechanics", "thermodynamics", "electromagnetism", "optics",
                        "quantum", "nuclear", "particle physics", "cosmology", "spectroscopy", "radiation", "acoustics"]
        },
        "0105": {
            "code": "0105",
            "name": "Chemical Sciences",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Chemistry and chemical sciences. Includes organic, inorganic, analytical, physical chemistry, biochemistry, and materials chemistry.",
            "keywords": ["chemistry", "chemical", "organic chemistry", "inorganic chemistry", "analytical chemistry", "biochemistry",
                        "materials chemistry", "polymer", "pharmaceutical chemistry", "laboratory", "compounds", "reactions",
                        "synthesis", "chromatography", "spectroscopy"]
        },
        "0107": {
            "code": "0107",
            "name": "Earth Sciences",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Geology, geophysics, geochemistry, oceanography, and atmospheric sciences. Includes soil science, hydrology, and climate science.",
            "keywords": ["geology", "geophysics", "geochemistry", "oceanography", "atmospheric", "meteorology", "soil science",
                        "hydrology", "climate", "seismology", "mineralogy", "paleontology", "sedimentology", "earth science"]
        },
        "0109": {
            "code": "0109",
            "name": "Biological Sciences",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Biology, biochemistry, microbiology, genetics, ecology, and zoology. Includes botany, marine biology, biotechnology, and pharmacology.",
            "keywords": ["biology", "biochemistry", "microbiology", "genetics", "ecology", "zoology", "botany", "marine biology",
                        "biotechnology", "pharmacology", "molecular biology", "cell biology", "immunology", "virology",
                        "physiology", "bioinformatics", "laboratory", "specimen", "organism"]
        },
        "0199": {
            "code": "0199",
            "name": "Other Natural and Physical Sciences",
            "broad_field_code": "01",
            "broad_field_name": "Natural and Physical Sciences",
            "description": "Natural and physical sciences not elsewhere classified. Includes forensic science, laboratory technology, and interdisciplinary natural sciences.",
            "keywords": ["forensic science", "laboratory technology", "natural sciences", "scientific research", "laboratory skills",
                        "scientific methods", "experimental", "research methods", "science technology"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 02 - Information Technology
        # ─────────────────────────────────────────────────────────────────────
        "0201": {
            "code": "0201",
            "name": "Computer Science",
            "broad_field_code": "02",
            "broad_field_name": "Information Technology",
            "description": "Computer science, programming, software engineering, and computer systems. Includes algorithms, data structures, artificial intelligence, and computer architecture.",
            "keywords": ["computer science", "programming", "software engineering", "algorithms", "data structures", "coding",
                        "software development", "artificial intelligence", "machine learning", "computer architecture",
                        "operating systems", "compilers", "python", "java", "javascript", "C++", "developer"]
        },
        "0203": {
            "code": "0203",
            "name": "Information Systems",
            "broad_field_code": "02",
            "broad_field_name": "Information Technology",
            "description": "Information systems, database management, systems analysis, and IT management. Includes business systems, enterprise architecture, and data management.",
            "keywords": ["information systems", "database", "systems analysis", "IT management", "business systems", "SQL",
                        "enterprise architecture", "data management", "systems administration", "network administration",
                        "IT support", "helpdesk", "systems integration", "ERP", "CRM", "business intelligence"]
        },
        "0299": {
            "code": "0299",
            "name": "Other Information Technology",
            "broad_field_code": "02",
            "broad_field_name": "Information Technology",
            "description": "Information technology not elsewhere classified. Includes cybersecurity, networking, cloud computing, and emerging technologies.",
            "keywords": ["cybersecurity", "networking", "cloud computing", "IT security", "network security", "penetration testing",
                        "digital forensics", "IT infrastructure", "DevOps", "web development", "mobile development",
                        "blockchain", "IoT", "internet of things"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 03 - Engineering and Related Technologies
        # ─────────────────────────────────────────────────────────────────────
        "0301": {
            "code": "0301",
            "name": "Manufacturing Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Manufacturing engineering, industrial technology, and production systems. Includes CNC machining, fabrication, welding, and manufacturing processes.",
            "keywords": ["manufacturing", "CNC", "machining", "fabrication", "welding", "sheet metal", "tool making",
                        "die making", "production", "industrial technology", "CAD/CAM", "precision engineering",
                        "metalwork", "turning", "milling", "grinding", "casting", "forging"]
        },
        "0303": {
            "code": "0303",
            "name": "Process and Resources Engineering",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Chemical engineering, petroleum engineering, mining engineering, and materials engineering. Includes process control and resource extraction.",
            "keywords": ["chemical engineering", "petroleum", "mining engineering", "materials engineering", "process control",
                        "resource extraction", "oil and gas", "refinery", "metallurgy", "minerals processing",
                        "pipeline", "drilling", "extraction", "smelting"]
        },
        "0305": {
            "code": "0305",
            "name": "Automotive Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Automotive engineering, vehicle mechanics, and automotive technology. Includes light vehicle, heavy vehicle, motorcycle, and marine mechanics.",
            "keywords": ["automotive", "vehicle", "mechanic", "car", "truck", "motorcycle", "diesel", "engine",
                        "transmission", "brake", "suspension", "electrical systems", "diagnostic", "service technician",
                        "auto electrician", "panel beating", "spray painting", "heavy vehicle"]
        },
        "0307": {
            "code": "0307",
            "name": "Mechanical and Industrial Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Mechanical engineering, industrial engineering, and maintenance engineering. Includes HVAC, refrigeration, and plant maintenance.",
            "keywords": ["mechanical engineering", "industrial engineering", "maintenance", "HVAC", "refrigeration",
                        "air conditioning", "plant maintenance", "hydraulics", "pneumatics", "pumps", "compressors",
                        "industrial maintenance", "fitter", "machinist", "millwright", "mechanical systems"]
        },
        "0309": {
            "code": "0309",
            "name": "Civil Engineering",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Civil engineering, structural engineering, and construction engineering. Includes roads, bridges, dams, and infrastructure development.",
            "keywords": ["civil engineering", "structural engineering", "construction engineering", "roads", "bridges", "dams",
                        "infrastructure", "concrete", "steel structures", "geotechnical", "water resources",
                        "transportation engineering", "surveying", "construction management"]
        },
        "0311": {
            "code": "0311",
            "name": "Geomatic Engineering",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Surveying, mapping, cartography, and geographic information systems. Includes land surveying, cadastral surveying, and spatial science.",
            "keywords": ["surveying", "mapping", "cartography", "GIS", "geographic information systems", "land surveying",
                        "cadastral", "spatial science", "remote sensing", "photogrammetry", "GPS", "geodesy",
                        "topographic", "survey drafting"]
        },
        "0313": {
            "code": "0313",
            "name": "Electrical and Electronic Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Electrical engineering, electronics, telecommunications, and computer engineering. Includes power systems, instrumentation, and control systems.",
            "keywords": ["electrical engineering", "electronics", "telecommunications", "power systems", "instrumentation",
                        "control systems", "electrician", "electrical installation", "wiring", "switchboard",
                        "PLC", "automation", "robotics", "electronic repair", "circuit", "microcontroller"]
        },
        "0315": {
            "code": "0315",
            "name": "Aerospace Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Aerospace engineering, aircraft maintenance, and aviation technology. Includes avionics, aircraft structures, and propulsion systems.",
            "keywords": ["aerospace", "aircraft", "aviation", "avionics", "aircraft maintenance", "propulsion",
                        "aeronautics", "flight systems", "aircraft structures", "composites", "aerospace manufacturing",
                        "drone", "UAV", "helicopter", "jet engine"]
        },
        "0317": {
            "code": "0317",
            "name": "Maritime Engineering and Technology",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Marine engineering, naval architecture, and maritime technology. Includes ship operations, marine mechanics, and offshore systems.",
            "keywords": ["marine engineering", "naval architecture", "maritime", "ship", "vessel", "marine mechanics",
                        "offshore", "boat building", "marine systems", "deck operations", "marine diesel",
                        "port operations", "maritime logistics"]
        },
        "0399": {
            "code": "0399",
            "name": "Other Engineering and Related Technologies",
            "broad_field_code": "03",
            "broad_field_name": "Engineering and Related Technologies",
            "description": "Engineering and technology not elsewhere classified. Includes biomedical engineering, environmental engineering, and emerging engineering fields.",
            "keywords": ["biomedical engineering", "environmental engineering", "fire engineering", "safety engineering",
                        "systems engineering", "engineering management", "quality engineering", "renewable energy",
                        "sustainable engineering", "engineering technology"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 04 - Architecture and Building
        # ─────────────────────────────────────────────────────────────────────
        "0401": {
            "code": "0401",
            "name": "Architecture and Urban Environment",
            "broad_field_code": "04",
            "broad_field_name": "Architecture and Building",
            "description": "Architecture, landscape architecture, urban design, and interior architecture. Includes building design, environmental design, and town planning.",
            "keywords": ["architecture", "landscape architecture", "urban design", "interior architecture", "building design",
                        "environmental design", "town planning", "urban planning", "architectural drafting",
                        "sustainable design", "heritage conservation", "landscape design", "CAD"]
        },
        "0403": {
            "code": "0403",
            "name": "Building",
            "broad_field_code": "04",
            "broad_field_name": "Architecture and Building",
            "description": "Building and construction trades. Includes carpentry, plumbing, bricklaying, plastering, painting, tiling, and construction management.",
            "keywords": ["building", "construction", "carpentry", "joinery", "plumbing", "gasfitting", "bricklaying",
                        "plastering", "painting", "decorating", "tiling", "roofing", "glazing", "scaffolding",
                        "concreting", "formwork", "flooring", "ceiling fixing", "wall and floor tiling",
                        "building inspection", "site supervision", "construction management"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 05 - Agriculture, Environmental and Related Studies
        # ─────────────────────────────────────────────────────────────────────
        "0501": {
            "code": "0501",
            "name": "Agriculture",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Agriculture, farming, animal husbandry, and agricultural science. Includes crop production, livestock management, and agricultural technology.",
            "keywords": ["agriculture", "farming", "animal husbandry", "livestock", "crop production", "agronomy",
                        "dairy farming", "beef cattle", "sheep", "poultry", "pig farming", "grain",
                        "irrigation", "agricultural machinery", "farm management", "agricultural science"]
        },
        "0503": {
            "code": "0503",
            "name": "Horticulture and Viticulture",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Horticulture, viticulture, floristry, and turf management. Includes nursery, landscaping, parks and gardens, and wine production.",
            "keywords": ["horticulture", "viticulture", "floristry", "turf management", "nursery", "landscaping",
                        "parks and gardens", "wine production", "arboriculture", "greenkeeping", "garden design",
                        "plant propagation", "pest management", "permaculture", "pruning", "irrigation"]
        },
        "0505": {
            "code": "0505",
            "name": "Forestry Studies",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Forestry, forest management, and timber production. Includes silviculture, forest harvesting, and forest conservation.",
            "keywords": ["forestry", "forest management", "timber", "silviculture", "forest harvesting", "logging",
                        "sawmilling", "wood processing", "forest conservation", "plantation", "tree felling",
                        "chainsaw", "forest operations"]
        },
        "0507": {
            "code": "0507",
            "name": "Fisheries Studies",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Fisheries, aquaculture, and seafood industry. Includes fish farming, commercial fishing, and seafood processing.",
            "keywords": ["fisheries", "aquaculture", "seafood", "fish farming", "commercial fishing", "seafood processing",
                        "oyster farming", "prawn farming", "marine aquaculture", "hatchery", "fish health",
                        "fishing operations", "deck hand"]
        },
        "0509": {
            "code": "0509",
            "name": "Environmental Studies",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Environmental science, conservation, land management, and sustainability. Includes natural resource management and environmental protection.",
            "keywords": ["environmental", "conservation", "land management", "sustainability", "natural resource management",
                        "environmental protection", "ecology", "wildlife management", "park ranger", "land care",
                        "environmental monitoring", "waste management", "recycling", "renewable energy", "carbon"]
        },
        "0599": {
            "code": "0599",
            "name": "Other Agriculture, Environmental and Related Studies",
            "broad_field_code": "05",
            "broad_field_name": "Agriculture, Environmental and Related Studies",
            "description": "Agriculture and environmental studies not elsewhere classified. Includes pest control, animal control, and rural operations.",
            "keywords": ["pest control", "animal control", "rural operations", "agricultural support", "stock handling",
                        "woolclassing", "shearing", "fencing", "rural skills", "agricultural contracting"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 06 - Health
        # ─────────────────────────────────────────────────────────────────────
        "0601": {
            "code": "0601",
            "name": "Medical Studies",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Medicine, surgery, and medical sciences. Includes general medicine, pathology, medical imaging, and specialist medical fields.",
            "keywords": ["medicine", "medical", "surgery", "pathology", "medical imaging", "radiology", "anaesthesia",
                        "emergency medicine", "general practice", "pediatrics", "psychiatry", "cardiology",
                        "oncology", "clinical", "diagnosis", "treatment"]
        },
        "0603": {
            "code": "0603",
            "name": "Nursing",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Nursing, midwifery, and nursing practice. Includes registered nursing, enrolled nursing, and specialist nursing fields.",
            "keywords": ["nursing", "nurse", "midwifery", "enrolled nursing", "registered nurse", "patient care",
                        "clinical nursing", "aged care nursing", "mental health nursing", "community nursing",
                        "nursing assessment", "medication administration", "wound care"]
        },
        "0605": {
            "code": "0605",
            "name": "Pharmacy",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Pharmacy and pharmaceutical science. Includes community pharmacy, hospital pharmacy, and pharmaceutical manufacturing.",
            "keywords": ["pharmacy", "pharmaceutical", "pharmacist", "dispensing", "medication", "drug",
                        "pharmaceutical manufacturing", "compounding", "pharmacy assistant", "prescription"]
        },
        "0607": {
            "code": "0607",
            "name": "Dental Studies",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Dentistry, dental technology, and oral health. Includes dental assisting, dental hygiene, and dental prosthetics.",
            "keywords": ["dental", "dentistry", "oral health", "dental assistant", "dental hygienist", "dental technician",
                        "dental prosthetics", "orthodontics", "periodontics", "dental surgery", "teeth", "oral care"]
        },
        "0609": {
            "code": "0609",
            "name": "Optical Science",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Optometry, optical dispensing, and optical science. Includes eye care, vision testing, and spectacle making.",
            "keywords": ["optometry", "optical", "optician", "dispensing optician", "eye care", "vision",
                        "spectacles", "glasses", "contact lenses", "optical dispensing", "eye examination"]
        },
        "0611": {
            "code": "0611",
            "name": "Veterinary Studies",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Veterinary science and animal health. Includes veterinary nursing, animal care, and veterinary technology.",
            "keywords": ["veterinary", "vet", "animal health", "veterinary nursing", "animal care", "vet nurse",
                        "animal surgery", "animal medicine", "pet care", "livestock health", "animal handling",
                        "animal welfare", "dog", "cat", "horse", "equine"]
        },
        "0613": {
            "code": "0613",
            "name": "Public Health",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Public health, epidemiology, and health promotion. Includes occupational health, indigenous health, and community health.",
            "keywords": ["public health", "epidemiology", "health promotion", "occupational health", "indigenous health",
                        "community health", "health policy", "disease prevention", "health education",
                        "population health", "health services", "health administration"]
        },
        "0615": {
            "code": "0615",
            "name": "Radiography",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Radiography, medical imaging, and radiation therapy. Includes diagnostic imaging, ultrasound, and nuclear medicine.",
            "keywords": ["radiography", "medical imaging", "radiation therapy", "X-ray", "CT scan", "MRI",
                        "ultrasound", "nuclear medicine", "sonography", "diagnostic imaging", "radiographer"]
        },
        "0617": {
            "code": "0617",
            "name": "Rehabilitation Therapies",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Physiotherapy, occupational therapy, speech pathology, and rehabilitation. Includes exercise physiology and chiropractic.",
            "keywords": ["physiotherapy", "occupational therapy", "speech pathology", "rehabilitation", "exercise physiology",
                        "chiropractic", "podiatry", "orthotics", "prosthetics", "physical therapy", "therapy assistant",
                        "mobility", "functional assessment", "therapeutic exercise"]
        },
        "0619": {
            "code": "0619",
            "name": "Complementary Therapies",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Complementary and alternative medicine. Includes massage therapy, naturopathy, acupuncture, and traditional Chinese medicine.",
            "keywords": ["complementary therapy", "massage therapy", "naturopathy", "acupuncture", "traditional Chinese medicine",
                        "aromatherapy", "reflexology", "remedial massage", "herbal medicine", "homeopathy",
                        "myotherapy", "Bowen therapy", "kinesiology"]
        },
        "0699": {
            "code": "0699",
            "name": "Other Health",
            "broad_field_code": "06",
            "broad_field_name": "Health",
            "description": "Health fields not elsewhere classified. Includes nutrition, first aid, ambulance/paramedic, and health support services.",
            "keywords": ["nutrition", "dietetics", "first aid", "paramedic", "ambulance", "health support",
                        "patient transport", "sterilisation", "health assistant", "pathology collection",
                        "medical administration", "health information", "allied health assistant"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 07 - Education
        # ─────────────────────────────────────────────────────────────────────
        "0701": {
            "code": "0701",
            "name": "Teacher Education",
            "broad_field_code": "07",
            "broad_field_name": "Education",
            "description": "Teacher education and teacher training. Includes early childhood, primary, secondary, and vocational teacher education.",
            "keywords": ["teacher education", "teacher training", "early childhood teacher", "primary teacher",
                        "secondary teacher", "vocational teacher", "teacher aide", "education assistant",
                        "special education teacher", "TESOL", "teaching methods", "pedagogy"]
        },
        "0703": {
            "code": "0703",
            "name": "Curriculum and Education Studies",
            "broad_field_code": "07",
            "broad_field_name": "Education",
            "description": "Curriculum studies, educational theory, and education research. Includes instructional design and educational leadership.",
            "keywords": ["curriculum", "education studies", "educational theory", "education research", "instructional design",
                        "educational leadership", "assessment", "learning theory", "educational psychology",
                        "education policy", "curriculum development"]
        },
        "0799": {
            "code": "0799",
            "name": "Other Education",
            "broad_field_code": "07",
            "broad_field_name": "Education",
            "description": "Education not elsewhere classified. Includes training and assessment, education support, and education administration.",
            "keywords": ["training and assessment", "education support", "education administration", "trainer",
                        "assessor", "training delivery", "learning facilitation", "workplace training",
                        "education coordinator", "school administration"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 08 - Management and Commerce
        # ─────────────────────────────────────────────────────────────────────
        "0801": {
            "code": "0801",
            "name": "Accounting",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Accounting, auditing, and taxation. Includes financial accounting, management accounting, bookkeeping, and forensic accounting.",
            "keywords": ["accounting", "auditing", "taxation", "bookkeeping", "financial accounting", "management accounting",
                        "payroll", "accounts payable", "accounts receivable", "BAS", "GST", "tax return",
                        "financial reporting", "MYOB", "Xero", "QuickBooks"]
        },
        "0803": {
            "code": "0803",
            "name": "Business and Management",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Business administration, management, and human resource management. Includes project management, operations, and strategic management.",
            "keywords": ["business", "management", "business administration", "human resources", "project management",
                        "operations management", "strategic management", "leadership", "organisational development",
                        "change management", "business planning", "entrepreneurship", "small business"]
        },
        "0805": {
            "code": "0805",
            "name": "Sales and Marketing",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Sales, marketing, advertising, and public relations. Includes digital marketing, market research, and retail management.",
            "keywords": ["sales", "marketing", "advertising", "public relations", "digital marketing", "market research",
                        "retail management", "merchandising", "brand management", "customer service",
                        "social media marketing", "e-commerce", "telemarketing", "sales management"]
        },
        "0807": {
            "code": "0807",
            "name": "Tourism",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Tourism management, travel services, and hospitality management. Includes tour guiding, event management, and destination marketing.",
            "keywords": ["tourism", "travel", "hospitality management", "tour guiding", "event management",
                        "destination marketing", "travel agent", "tourism marketing", "hotel management",
                        "visitor services", "ecotourism", "adventure tourism"]
        },
        "0809": {
            "code": "0809",
            "name": "Office Studies",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Office administration, secretarial studies, and administrative support. Includes reception, data entry, and records management.",
            "keywords": ["office administration", "secretarial", "administrative", "reception", "data entry",
                        "records management", "executive assistant", "personal assistant", "word processing",
                        "office management", "filing", "scheduling", "correspondence"]
        },
        "0811": {
            "code": "0811",
            "name": "Banking, Finance and Related Fields",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Banking, finance, financial planning, and insurance. Includes investment, credit, and financial services.",
            "keywords": ["banking", "finance", "financial planning", "insurance", "investment", "credit",
                        "financial services", "mortgage broking", "superannuation", "wealth management",
                        "financial advice", "lending", "risk management", "compliance"]
        },
        "0899": {
            "code": "0899",
            "name": "Other Management and Commerce",
            "broad_field_code": "08",
            "broad_field_name": "Management and Commerce",
            "description": "Management and commerce not elsewhere classified. Includes purchasing, logistics, and quality management.",
            "keywords": ["purchasing", "logistics", "supply chain", "quality management", "warehousing",
                        "inventory management", "procurement", "contract management", "import/export",
                        "freight", "distribution", "materials handling"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 09 - Society and Culture
        # ─────────────────────────────────────────────────────────────────────
        "0901": {
            "code": "0901",
            "name": "Political Science and Policy Studies",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Political science, policy studies, and public administration. Includes government, international relations, and public policy.",
            "keywords": ["political science", "policy studies", "public administration", "government",
                        "international relations", "public policy", "governance", "policy analysis",
                        "political theory", "diplomacy"]
        },
        "0903": {
            "code": "0903",
            "name": "Studies in Human Society",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Sociology, anthropology, history, and human geography. Includes cultural studies, indigenous studies, and gender studies.",
            "keywords": ["sociology", "anthropology", "history", "human geography", "cultural studies",
                        "indigenous studies", "gender studies", "archaeology", "heritage", "social research",
                        "demography", "criminology"]
        },
        "0905": {
            "code": "0905",
            "name": "Human Welfare Studies and Services",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Social work, welfare, and community services. Includes aged care, disability services, child protection, and youth work.",
            "keywords": ["social work", "welfare", "community services", "aged care", "disability services",
                        "child protection", "youth work", "case management", "family services", "homelessness",
                        "mental health support", "counselling", "support worker", "carer"]
        },
        "0907": {
            "code": "0907",
            "name": "Behavioural Science",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Psychology, cognitive science, and behavioural studies. Includes counselling psychology, clinical psychology, and behavioural analysis.",
            "keywords": ["psychology", "behavioural science", "cognitive science", "counselling psychology",
                        "clinical psychology", "behavioural analysis", "psychotherapy", "mental health",
                        "neuropsychology", "developmental psychology"]
        },
        "0909": {
            "code": "0909",
            "name": "Law",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Legal studies, law, and legal practice. Includes commercial law, criminal law, family law, and legal support.",
            "keywords": ["law", "legal", "lawyer", "solicitor", "barrister", "legal practice", "commercial law",
                        "criminal law", "family law", "property law", "legal assistant", "paralegal",
                        "conveyancing", "litigation", "legal secretary"]
        },
        "0911": {
            "code": "0911",
            "name": "Justice and Law Enforcement",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Justice administration, law enforcement, and corrections. Includes policing, security, and criminology.",
            "keywords": ["justice", "law enforcement", "police", "corrections", "security", "criminology",
                        "protective services", "investigation", "border protection", "customs",
                        "court administration", "probation", "parole", "security officer", "crowd control"]
        },
        "0913": {
            "code": "0913",
            "name": "Librarianship, Information Management and Curatorial Studies",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Library and information science, records management, and museum studies. Includes archives, gallery curation, and information management.",
            "keywords": ["library", "librarianship", "information management", "records management", "museum",
                        "gallery", "archives", "curation", "cataloguing", "collection management",
                        "preservation", "digital preservation", "information services"]
        },
        "0915": {
            "code": "0915",
            "name": "Language and Literature",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Languages, linguistics, and literature. Includes English, foreign languages, translation, and interpreting.",
            "keywords": ["language", "linguistics", "literature", "English", "foreign language", "translation",
                        "interpreting", "TESOL", "LOTE", "creative writing", "editing", "publishing",
                        "Auslan", "sign language", "professional writing"]
        },
        "0917": {
            "code": "0917",
            "name": "Philosophy and Religious Studies",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Philosophy, religious studies, and theology. Includes ethics, comparative religion, and ministry studies.",
            "keywords": ["philosophy", "religious studies", "theology", "ethics", "comparative religion",
                        "ministry", "pastoral care", "chaplaincy", "divinity", "spiritual care"]
        },
        "0919": {
            "code": "0919",
            "name": "Economics and Econometrics",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Economics, econometrics, and economic analysis. Includes microeconomics, macroeconomics, and economic policy.",
            "keywords": ["economics", "econometrics", "economic analysis", "microeconomics", "macroeconomics",
                        "economic policy", "economic modelling", "economic research", "economic forecasting"]
        },
        "0921": {
            "code": "0921",
            "name": "Sport and Recreation",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Sport, recreation, and fitness. Includes coaching, sports management, fitness instruction, and outdoor recreation.",
            "keywords": ["sport", "recreation", "fitness", "coaching", "sports management", "personal training",
                        "fitness instruction", "outdoor recreation", "aquatics", "gym", "sports development",
                        "exercise", "athletics", "swimming", "sports officiating"]
        },
        "0999": {
            "code": "0999",
            "name": "Other Society and Culture",
            "broad_field_code": "09",
            "broad_field_name": "Society and Culture",
            "description": "Society and culture not elsewhere classified. Includes funeral services, celebrancy, and family history research.",
            "keywords": ["funeral services", "celebrant", "family history", "genealogy", "community development",
                        "volunteer management", "advocacy", "social enterprise"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 10 - Creative Arts
        # ─────────────────────────────────────────────────────────────────────
        "1001": {
            "code": "1001",
            "name": "Performing Arts",
            "broad_field_code": "10",
            "broad_field_name": "Creative Arts",
            "description": "Music, dance, drama, and performance. Includes theatre production, music production, and circus arts.",
            "keywords": ["performing arts", "music", "dance", "drama", "theatre", "acting", "singing",
                        "musical instrument", "stage", "performance", "circus", "choreography",
                        "music production", "sound production", "stage management"]
        },
        "1003": {
            "code": "1003",
            "name": "Visual Arts and Crafts",
            "broad_field_code": "10",
            "broad_field_name": "Creative Arts",
            "description": "Visual arts, fine arts, and crafts. Includes painting, sculpture, ceramics, photography, and textile arts.",
            "keywords": ["visual arts", "fine arts", "painting", "sculpture", "ceramics", "photography",
                        "textile arts", "printmaking", "jewellery", "glass", "woodwork", "leatherwork",
                        "illustration", "drawing", "art history"]
        },
        "1005": {
            "code": "1005",
            "name": "Graphic and Design Studies",
            "broad_field_code": "10",
            "broad_field_name": "Creative Arts",
            "description": "Graphic design, industrial design, fashion design, and interior design. Includes web design and multimedia.",
            "keywords": ["graphic design", "industrial design", "fashion design", "interior design", "web design",
                        "multimedia", "visual communication", "digital design", "UX design", "UI design",
                        "product design", "signage", "packaging design", "branding"]
        },
        "1007": {
            "code": "1007",
            "name": "Communication and Media Studies",
            "broad_field_code": "10",
            "broad_field_name": "Creative Arts",
            "description": "Media, journalism, film, and communication studies. Includes broadcasting, advertising, and digital media.",
            "keywords": ["media", "journalism", "film", "communication", "broadcasting", "television", "radio",
                        "advertising", "digital media", "video production", "screen production", "animation",
                        "audio production", "podcasting", "content creation"]
        },
        "1099": {
            "code": "1099",
            "name": "Other Creative Arts",
            "broad_field_code": "10",
            "broad_field_name": "Creative Arts",
            "description": "Creative arts not elsewhere classified. Includes games design, creative writing, and arts management.",
            "keywords": ["games design", "creative writing", "arts management", "curation", "cultural management",
                        "creative industries", "entertainment", "digital arts", "interactive media"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 11 - Food, Hospitality and Personal Services
        # ─────────────────────────────────────────────────────────────────────
        "1101": {
            "code": "1101",
            "name": "Food and Hospitality",
            "broad_field_code": "11",
            "broad_field_name": "Food, Hospitality and Personal Services",
            "description": "Food preparation, cookery, hospitality, and food service. Includes commercial cookery, patisserie, and bar service.",
            "keywords": ["food", "hospitality", "cookery", "chef", "commercial cookery", "patisserie", "baking",
                        "butchery", "food service", "bar service", "barista", "catering", "food safety",
                        "kitchen operations", "food preparation", "restaurant", "cafe", "events"]
        },
        "1103": {
            "code": "1103",
            "name": "Personal Services",
            "broad_field_code": "11",
            "broad_field_name": "Food, Hospitality and Personal Services",
            "description": "Personal services including hairdressing, beauty, and other personal care. Includes barbering, makeup, and beauty therapy.",
            "keywords": ["hairdressing", "beauty", "barbering", "makeup", "beauty therapy", "nail technology",
                        "skin care", "salon", "spa", "waxing", "tanning", "eyelash", "cosmetics",
                        "hair styling", "colour", "cut", "blow dry", "personal grooming"]
        },
        
        # ─────────────────────────────────────────────────────────────────────
        # 12 - Mixed Field Programmes
        # ─────────────────────────────────────────────────────────────────────
        "1201": {
            "code": "1201",
            "name": "General Education Programmes",
            "broad_field_code": "12",
            "broad_field_name": "Mixed Field Programmes",
            "description": "General education and preparatory programmes. Includes adult literacy, numeracy, and general studies.",
            "keywords": ["general education", "literacy", "numeracy", "adult education", "foundation skills",
                        "basic education", "preparatory", "bridging", "access programmes", "general studies"]
        },
        "1203": {
            "code": "1203",
            "name": "Social Skills Programmes",
            "broad_field_code": "12",
            "broad_field_name": "Mixed Field Programmes",
            "description": "Social skills development and life skills programmes. Includes communication skills and interpersonal development.",
            "keywords": ["social skills", "life skills", "communication skills", "interpersonal skills",
                        "personal development", "self-management", "teamwork", "conflict resolution",
                        "emotional intelligence", "cultural awareness"]
        },
        "1205": {
            "code": "1205",
            "name": "Employment Skills Programmes",
            "broad_field_code": "12",
            "broad_field_name": "Mixed Field Programmes",
            "description": "Employment preparation and career development. Includes work readiness, job seeking, and career planning.",
            "keywords": ["employment skills", "work readiness", "job seeking", "career development", "career planning",
                        "resume writing", "interview skills", "workplace skills", "employability",
                        "work experience", "transition to work"]
        },
        "1299": {
            "code": "1299",
            "name": "Other Mixed Field Programmes",
            "broad_field_code": "12",
            "broad_field_name": "Mixed Field Programmes",
            "description": "Mixed field programmes not elsewhere classified. Includes interdisciplinary studies and combined programmes.",
            "keywords": ["mixed field", "interdisciplinary", "combined programmes", "multi-disciplinary",
                        "integrated studies", "cross-disciplinary"]
        }
    }
}

# Legacy alias for backward compatibility
INDUSTRY_DOMAIN_FACET = ASCED_FIELD_OF_EDUCATION_FACET

# Broad field lookup for convenience
ASCED_BROAD_FIELDS = {
    "01": "Natural and Physical Sciences",
    "02": "Information Technology",
    "03": "Engineering and Related Technologies",
    "04": "Architecture and Building",
    "05": "Agriculture, Environmental and Related Studies",
    "06": "Health",
    "07": "Education",
    "08": "Management and Commerce",
    "09": "Society and Culture",
    "10": "Creative Arts",
    "11": "Food, Hospitality and Personal Services",
    "12": "Mixed Field Programmes"
}


# ═══════════════════════════════════════════════════════════════════════════
#  FACET 9: PROFICIENCY LEVEL (LVL) - AQF/SFIA aligned levels
# ═══════════════════════════════════════════════════════════════════════════

PROFICIENCY_LEVEL_FACET = {
    "facet_id": "LVL",
    "facet_name": "Proficiency Level",
    "description": "Level of proficiency/mastery required (AQF/SFIA aligned)",
    "values": {
        "LVL.1": {
            "code": "LVL.1",
            "name": "FOLLOW",
            "level": 1,
            "description": "Basic awareness, performs routine tasks under close supervision",
            "aqf_level": "Certificate I",
            "sfia_level": "Follow",
            "keywords": ["basic", "introductory", "awareness", "fundamental", "entry"]
        },
        "LVL.2": {
            "code": "LVL.2",
            "name": "ASSIST",
            "level": 2,
            "description": "Applies skills in routine contexts with guidance",
            "aqf_level": "Certificate II",
            "sfia_level": "Assist",
            "keywords": ["developing", "routine", "guided", "supervised"]
        },
        "LVL.3": {
            "code": "LVL.3",
            "name": "APPLY",
            "level": 3,
            "description": "Works independently in standard situations",
            "aqf_level": "Certificate III",
            "sfia_level": "Apply",
            "keywords": ["competent", "independent", "skilled", "trade"]
        },
        "LVL.4": {
            "code": "LVL.4",
            "name": "ENABLE",
            "level": 4,
            "description": "Handles complex situations, may supervise others",
            "aqf_level": "Certificate IV",
            "sfia_level": "Enable",
            "keywords": ["proficient", "complex", "supervisor", "coordinator"]
        },
        "LVL.5": {
            "code": "LVL.5",
            "name": "ENSURE ADVISE",
            "level": 5,
            "description": "Expert in specialised areas, provides guidance",
            "aqf_level": "Diploma",
            "sfia_level": "Ensure/Advise",
            "keywords": ["advanced", "specialist", "expert", "advisor"]
        },
        "LVL.6": {
            "code": "LVL.6",
            "name": "INITIATE INFLUENCE",
            "level": 6,
            "description": "Leads and influences, strategic capability",
            "aqf_level": "Advanced Diploma/Associate Degree",
            "sfia_level": "Initiate/Influence",
            "keywords": ["expert", "leader", "strategic", "senior"]
        },
        "LVL.7": {
            "code": "LVL.7",
            "name": "SET STRATEGY",
            "level": 7,
            "description": "Sets strategy, recognized authority in field",
            "aqf_level": "Bachelor/Graduate",
            "sfia_level": "Set Strategy",
            "keywords": ["master", "authority", "strategic leader", "principal"]
        }
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  AGGREGATE FACET CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

ALL_FACETS = {
    "NAT": SKILL_NATURE_FACET,
    "TRF": TRANSFERABILITY_FACET,
    "COG": COGNITIVE_COMPLEXITY_FACET,
    "CTX": WORK_CONTEXT_FACET,
    "FUT": FUTURE_READINESS_FACET,
    "LRN": LEARNING_CONTEXT_FACET,
    "DIG": DIGITAL_INTENSITY_FACET,
    "ASCED": ASCED_FIELD_OF_EDUCATION_FACET,
    "LVL": PROFICIENCY_LEVEL_FACET,
}

# Legacy alias - map IND to ASCED for backward compatibility
ALL_FACETS["IND"] = ASCED_FIELD_OF_EDUCATION_FACET

# Facets that allow multiple values
MULTI_VALUE_FACETS = ["ASCED", "IND"]

# Facets with ordered/hierarchical values
ORDERED_FACETS = ["COG", "DIG", "LVL"]

# Priority order for assignment (most important first)
FACET_PRIORITY = ["NAT", "TRF", "COG", "CTX", "FUT", "LRN", "DIG", "ASCED", "LVL"]


def get_facet_values_list(facet_id: str) -> list:
    """Get list of all values for a facet"""
    facet = ALL_FACETS.get(facet_id, {})
    return list(facet.get("values", {}).keys())


def get_facet_text_for_embedding(facet_id: str, value_code: str) -> str:
    """Generate text representation of a facet value for embedding"""
    facet = ALL_FACETS.get(facet_id, {})
    value = facet.get("values", {}).get(value_code, {})
    
    text_parts = [
        value.get("name", ""),
        value.get("description", "")
    ]
    
    # Add keywords for ASCED facet
    if facet_id in ["ASCED", "IND"]:
        keywords = value.get("keywords", [])
        if keywords:
            text_parts.append(" ".join(keywords[:15]))
    
    return ". ".join([p for p in text_parts if p])


def get_all_facet_embeddings_texts() -> dict:
    """Get all facet values as texts for embedding precomputation"""
    result = {}
    for facet_id, facet in ALL_FACETS.items():
        # Skip the legacy IND alias to avoid duplication
        if facet_id == "IND":
            continue
        result[facet_id] = {}
        for value_code in facet.get("values", {}).keys():
            result[facet_id][value_code] = get_facet_text_for_embedding(facet_id, value_code)
    return result


def get_asced_narrow_field_info(narrow_field_code: str) -> dict:
    """
    Get information about a specific ASCED narrow field code.
    
    Args:
        narrow_field_code: 4-digit ASCED narrow field code (e.g., "0101")
        
    Returns:
        Dictionary with narrow field information including parent broad field
    """
    # 4-digit codes are now primary keys in ASCED_FIELD_OF_EDUCATION_FACET
    if narrow_field_code in ASCED_FIELD_OF_EDUCATION_FACET["values"]:
        field = ASCED_FIELD_OF_EDUCATION_FACET["values"][narrow_field_code]
        return {
            "narrow_field_code": narrow_field_code,
            "narrow_field_name": field["name"],
            "broad_field_code": field.get("broad_field_code", narrow_field_code[:2]),
            "broad_field_name": field.get("broad_field_name", ""),
            "description": field.get("description", ""),
            "keywords": field.get("keywords", [])
        }
    
    return {}


def get_asced_broad_field_name(code: str) -> str:
    """
    Get the broad field name for an ASCED code (2-digit or 4-digit).
    
    Args:
        code: ASCED code (2-digit broad field or 4-digit narrow field)
        
    Returns:
        Broad field name
    """
    broad_code = code[:2] if len(code) >= 2 else code
    return ASCED_BROAD_FIELDS.get(broad_code, "Unknown")


def get_asced_codes_for_broad_field(broad_field_code: str) -> list:
    """
    Get all 4-digit narrow field codes under a broad field.
    
    Args:
        broad_field_code: 2-digit ASCED broad field code (e.g., "01")
        
    Returns:
        List of 4-digit narrow field codes
    """
    return [
        code for code in ASCED_FIELD_OF_EDUCATION_FACET["values"].keys()
        if code.startswith(broad_field_code)
    ]


def map_legacy_industry_code_to_asced(legacy_code: str) -> str:
    """
    Validate and return an ASCED narrow field code.
    
    Args:
        legacy_code: ASCED code (should be 4-digit narrow field code)
        
    Returns:
        The code if valid, or empty string if not found
    """
    if legacy_code in ASCED_FIELD_OF_EDUCATION_FACET["values"]:
        return legacy_code
    # Handle 2-digit codes by returning first narrow field
    if len(legacy_code) == 2:
        matching_codes = get_asced_codes_for_broad_field(legacy_code)
        return matching_codes[0] if matching_codes else ""
    return ""