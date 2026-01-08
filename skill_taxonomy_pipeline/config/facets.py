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
#  FACET 8: INDUSTRY DOMAIN (IND) - Industry sectors (multi-value allowed)
# ═══════════════════════════════════════════════════════════════════════════

INDUSTRY_DOMAIN_FACET = {
    "facet_id": "IND",
    "facet_name": "Industry Domain",
    "description": "Industry sectors where this skill is applicable (multiple allowed)",
    "multi_value": True,
    "values": {
        "0101": {
        "code": "0101",
        "name": "Mathematical Sciences",
        "description": "Mathematical Sciences disciplines covering key subfields such as Mathematics, and Statistics.",
        "keywords": [
            "Mathematical Sciences, n.e.c.",
            "Mathematics",
            "Statistics"
        ],
        "training_packages": []
        },
        "0103": {
        "code": "0103",
        "name": "Physics and Astronomy",
        "description": "Physics and Astronomy disciplines covering key subfields such as Astronomy, and Physics.",
        "keywords": [
            "Astronomy",
            "Physics"
        ],
        "training_packages": []
        },
        "0105": {
        "code": "0105",
        "name": "Chemical Sciences",
        "description": "Chemical Sciences disciplines covering key subfields such as Inorganic Chemistry, and Organic Chemistry.",
        "keywords": [
            "Chemical Sciences, n.e.c.",
            "Inorganic Chemistry",
            "Organic Chemistry"
        ],
        "training_packages": []
        },
        "0107": {
        "code": "0107",
        "name": "Earth Sciences",
        "description": "Earth Sciences disciplines covering key subfields such as Atmospheric Sciences, Geochemistry, and Geology.",
        "keywords": [
            "Atmospheric Sciences",
            "Earth Sciences, n.e.c.",
            "Geochemistry",
            "Geology",
            "Geophysics",
            "Hydrology",
            "Oceanography",
            "Soil Science"
        ],
        "training_packages": []
        },
        "0109": {
        "code": "0109",
        "name": "Biological Sciences",
        "description": "Biological Sciences disciplines covering key subfields such as Biochemistry and Cell Biology, Botany, and Ecology and Evolution.",
        "keywords": [
            "Biochemistry and Cell Biology",
            "Biological Sciences, n.e.c.",
            "Botany",
            "Ecology and Evolution",
            "Genetics",
            "Human Biology",
            "Marine Science",
            "Microbiology",
            "Zoology"
        ],
        "training_packages": []
        },
        "0199": {
        "code": "0199",
        "name": "Other Natural and Physical Sciences",
        "description": "Other Natural and Physical Sciences disciplines covering key subfields such as Food Science and Biotechnology, Forensic Science, and Laboratory Technology.",
        "keywords": [
            "Food Science and Biotechnology",
            "Forensic Science",
            "Laboratory Technology",
            "Medical Science",
            "Natural and Physical Sciences, n.e.c.",
            "Pharmacology"
        ],
        "training_packages": []
        },
        "0201": {
        "code": "0201",
        "name": "Computer Science",
        "description": "Computer Science disciplines covering key subfields such as Algorithms, Artificial Intelligence, and Compiler Construction.",
        "keywords": [
            "Algorithms",
            "Artificial Intelligence",
            "Compiler Construction",
            "Computational Theory",
            "Computer Graphics",
            "Computer Science, n.e.c.",
            "Data Structures",
            "Formal Language Theory",
            "Networks and Communications",
            "Operating Systems",
            "Programming"
        ],
        "training_packages": []
        },
        "0203": {
        "code": "0203",
        "name": "Information Systems",
        "description": "Information Systems disciplines covering key subfields such as Conceptual Modelling, Database Management, and Decision Support Systems.",
        "keywords": [
            "Conceptual Modelling",
            "Database Management",
            "Decision Support Systems",
            "Information Systems, n.e.c.",
            "Systems Analysis and Design"
        ],
        "training_packages": []
        },
        "0299": {
        "code": "0299",
        "name": "Other Information Technology",
        "description": "Other Information Technology disciplines covering key subfields such as .",
        "keywords": [
            "Information Technology, n.e.c.",
            "Security Science"
        ],
        "training_packages": []
        },
        "0301": {
        "code": "0301",
        "name": "Manufacturing Engineering and Technology",
        "description": "Manufacturing Engineering and Technology disciplines covering key subfields such as Cabinet Making, Footwear Making, and Furniture Polishing.",
        "keywords": [
            "Cabinet Making",
            "Footwear Making",
            "Furniture Polishing",
            "Furniture Upholstery and Renovation",
            "Garment Making",
            "Manufacturing Engineering",
            "Manufacturing Engineering and Technology, n.e.c.",
            "Printing",
            "Textile Making",
            "Wood Machining and Turning"
        ],
        "training_packages": []
        },
        "0303": {
        "code": "0303",
        "name": "Process and Resources Engineering",
        "description": "Process and Resources Engineering disciplines covering key subfields such as Chemical Engineering, Food Processing Technology, and Materials Engineering.",
        "keywords": [
            "Chemical Engineering",
            "Food Processing Technology",
            "Materials Engineering",
            "Mining Engineering",
            "Process and Resources Engineering, n.e.c."
        ],
        "training_packages": []
        },
        "0305": {
        "code": "0305",
        "name": "Automotive Engineering and Technology",
        "description": "Automotive Engineering and Technology disciplines covering key subfields such as Automotive Body Construction, Automotive Electrics and Electronics, and Automotive Engineering.",
        "keywords": [
            "Automotive Body Construction",
            "Automotive Electrics and Electronics",
            "Automotive Engineering",
            "Automotive Engineering and Technology, n.e.c.",
            "Automotive Vehicle Operations",
            "Automotive Vehicle Refinishing",
            "Panel Beating",
            "Upholstery and Vehicle Trimming",
            "Vehicle Mechanics"
        ],
        "training_packages": []
        },
        "0307": {
        "code": "0307",
        "name": "Mechanical and Industrial Engineering and Technology",
        "description": "Mechanical and Industrial Engineering and Technology disciplines covering key subfields such as Boilermaking and Welding, Industrial Engineering, and Mechanical Engineering.",
        "keywords": [
            "Boilermaking and Welding",
            "Industrial Engineering",
            "Mechanical Engineering",
            "Mechanical and Industrial Engineering and Technology, n.e.c.",
            "Metal Casting and Patternmaking",
            "Metal Fitting, Turning and Machining",
            "Plant and Machine Operations",
            "Precision Metalworking",
            "Sheetmetal Working",
            "Toolmaking"
        ],
        "training_packages": []
        },
        "0309": {
        "code": "0309",
        "name": "Civil Engineering",
        "description": "Civil Engineering disciplines covering key subfields such as Building Services Engineering, Construction Engineering, and Geotechnical Engineering.",
        "keywords": [
            "Building Services Engineering",
            "Civil Engineering, n.e.c.",
            "Construction Engineering",
            "Geotechnical Engineering",
            "Ocean Engineering",
            "Structural Engineering",
            "Transport Engineering",
            "Water and Sanitary Engineering"
        ],
        "training_packages": []
        },
        "0311": {
        "code": "0311",
        "name": "Geomatic Engineering",
        "description": "Geomatic Engineering disciplines covering key subfields such as Mapping Science, and Surveying.",
        "keywords": [
            "Geomatic Engineering, n.e.c.",
            "Mapping Science",
            "Surveying"
        ],
        "training_packages": []
        },
        "0313": {
        "code": "0313",
        "name": "Electrical and Electronic Engineering and Technology",
        "description": "Electrical and Electronic Engineering and Technology disciplines covering key subfields such as Communications Equipment Installation and Maintenance and Communications Technologies.",
        "keywords": [
            "Communications Equipment Installation and Maintenance",
            "Communications Technologies",
            "Computer Engineering",
            "Electrical Engineering",
            "Electrical Fitting, Electrical Mechanics",
            "Electrical and Electronic Engineering and Technology, n.e.c.",
            "Electronic Engineering",
            "Electronic Equipment Servicing",
            "Powerline Installation and Maintenance",
            "Refrigeration and Air Conditioning Mechanics"
        ],
        "training_packages": []
        },
        "0315": {
        "code": "0315",
        "name": "Aerospace Engineering and Technology",
        "description": "Aerospace Engineering and Technology disciplines covering key subfields such as Aerospace Engineering, Air Traffic Control, and Aircraft Maintenance Engineering.",
        "keywords": [
            "Aerospace Engineering",
            "Aerospace Engineering and Technology, n.e.c.",
            "Air Traffic Control",
            "Aircraft Maintenance Engineering",
            "Aircraft Operation"
        ],
        "training_packages": []
        },
        "0317": {
        "code": "0317",
        "name": "Maritime Engineering and Technology",
        "description": "Maritime Engineering and Technology disciplines covering key subfields such as Marine Construction, Marine Craft Operation, and Maritime Engineering.",
        "keywords": [
            "Marine Construction",
            "Marine Craft Operation",
            "Maritime Engineering",
            "Maritime Engineering and Technology, n.e.c."
        ],
        "training_packages": []
        },
        "0399": {
        "code": "0399",
        "name": "Other Engineering and Related Technologies",
        "description": "Other Engineering and Related Technologies disciplines covering key subfields such as Biomedical Engineering, Cleaning, and Environmental Engineering.",
        "keywords": [
            "Biomedical Engineering",
            "Cleaning",
            "Engineering and Related Technologies, n.e.c.",
            "Environmental Engineering",
            "Fire Technology",
            "Rail Operations"
        ],
        "training_packages": []
        },
        "0401": {
        "code": "0401",
        "name": "Architecture and Urban Environment",
        "description": "Architecture and Urban Environment disciplines covering key subfields such as Architecture, Interior and Environmental Design, and Landscape Architecture.",
        "keywords": [
            "Architecture",
            "Architecture and Urban Environment, n.e.c.",
            "Interior and Environmental Design",
            "Landscape Architecture",
            "Urban Design and Regional Planning"
        ],
        "training_packages": []
        },
        "0403": {
        "code": "0403",
        "name": "Building",
        "description": "Building disciplines covering key subfields such as Bricklaying and Stonemasonry, Building Construction Economics, and Building Construction Management.",
        "keywords": [
            "Bricklaying and Stonemasonry",
            "Building Construction Economics",
            "Building Construction Management",
            "Building Science and Technology",
            "Building Surveying",
            "Building, n.e.c.",
            "Carpentry and Joinery",
            "Ceiling, Wall and Floor Fixing",
            "Floor Coverings",
            "Furnishing Installation",
            "Glazing",
            "Painting, Decorating and Sign Writing",
            "Plastering",
            "Plumbing",
            "Roof Fixing",
            "Scaffolding and Rigging"
        ],
        "training_packages": []
        },
        "0501": {
        "code": "0501",
        "name": "Agriculture",
        "description": "Agriculture disciplines covering key subfields such as Agricultural Science, Animal Husbandry, and Wool Science.",
        "keywords": [
            "Agricultural Science",
            "Agriculture, n.e.c.",
            "Animal Husbandry",
            "Wool Science"
        ],
        "training_packages": []
        },
        "0503": {
        "code": "0503",
        "name": "Horticulture and Viticulture",
        "description": "Horticulture and Viticulture disciplines covering key subfields such as Horticulture, and Viticulture.",
        "keywords": [
            "Horticulture",
            "Viticulture"
        ],
        "training_packages": []
        },
        "0505": {
        "code": "0505",
        "name": "Forestry Studies",
        "description": "Forestry Studies disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Forestry Studies"
        ],
        "training_packages": []
        },
        "0507": {
        "code": "0507",
        "name": "Fisheries Studies",
        "description": "Fisheries Studies disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Aquaculture",
            "Fisheries Studies, n.e.c."
        ],
        "training_packages": []
        },
        "0509": {
        "code": "0509",
        "name": "Environmental Studies",
        "description": "Environmental Studies disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Environmental Studies, n.e.c.",
            "Land, Parks and Wildlife Management"
        ],
        "training_packages": []
        },
        "0599": {
        "code": "0599",
        "name": "Other Agriculture, Environmental and Related Studies",
        "description": "Other Agriculture, Environmental and Related Studies disciplines covering key subfields such as .",
        "keywords": [
            "Agriculture, Environmental and Related Studies, n.e.c.",
            "Pest and Weed Control"
        ],
        "training_packages": []
        },
        "0601": {
        "code": "0601",
        "name": "Medical Studies",
        "description": "Medical Studies disciplines covering key subfields such as Anaesthesiology, General Medicine, and General Practice.",
        "keywords": [
            "Anaesthesiology",
            "General Medicine",
            "General Practice",
            "Internal Medicine",
            "Medical Studies, n.e.c.",
            "Obstetrics and Gynaecology",
            "Paediatrics",
            "Pathology",
            "Psychiatry",
            "Radiology",
            "Surgery"
        ],
        "training_packages": []
        },
        "0603": {
        "code": "0603",
        "name": "Nursing",
        "description": "Nursing disciplines covering key subfields such as Aged Care Nursing, Community Nursing, and Critical Care Nursing.",
        "keywords": [
            "Aged Care Nursing",
            "Community Nursing",
            "Critical Care Nursing",
            "General Nursing",
            "Mental Health Nursing",
            "Midwifery",
            "Mothercraft Nursing and Family and Child Health Nursing",
            "Nursing, n.e.c.",
            "Palliative Care Nursing"
        ],
        "training_packages": []
        },
        "0605": {
        "code": "0605",
        "name": "Pharmacy",
        "description": "Pharmacy disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Pharmacy"
        ],
        "training_packages": []
        },
        "0607": {
        "code": "0607",
        "name": "Dental Studies",
        "description": "Dental Studies disciplines covering key subfields such as Dental Assisting, Dental Technology, and Dentistry.",
        "keywords": [
            "Dental Assisting",
            "Dental Studies, n.e.c.",
            "Dental Technology",
            "Dentistry"
        ],
        "training_packages": []
        },
        "0609": {
        "code": "0609",
        "name": "Optical Science",
        "description": "Optical Science disciplines covering key subfields such as Optical Technology, and Optometry.",
        "keywords": [
            "Optical Science, n.e.c.",
            "Optical Technology",
            "Optometry"
        ],
        "training_packages": []
        },
        "0611": {
        "code": "0611",
        "name": "Veterinary Studies",
        "description": "Veterinary Studies disciplines covering key subfields such as Veterinary Assisting, and Veterinary Science.",
        "keywords": [
            "Veterinary Assisting",
            "Veterinary Science",
            "Veterinary Studies, n.e.c."
        ],
        "training_packages": []
        },
        "0613": {
        "code": "0613",
        "name": "Public Health",
        "description": "Public Health disciplines covering key subfields such as Community Health, Environmental Health, and Epidemiology.",
        "keywords": [
            "Community Health",
            "Environmental Health",
            "Epidemiology",
            "Health Promotion",
            "Indigenous Health",
            "Occupational Health and Safety",
            "Public Health, n.e.c."
        ],
        "training_packages": []
        },
        "0615": {
        "code": "0615",
        "name": "Radiography",
        "description": "Radiography disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Radiography"
        ],
        "training_packages": []
        },
        "0617": {
        "code": "0617",
        "name": "Rehabilitation Therapies",
        "description": "Rehabilitation Therapies disciplines covering key subfields such as Audiology, Chiropractic and Osteopathy, and Massage Therapy.",
        "keywords": [
            "Audiology",
            "Chiropractic and Osteopathy",
            "Massage Therapy",
            "Occupational Therapy",
            "Physiotherapy",
            "Podiatry",
            "Rehabilitation Therapies, n.e.c.",
            "Speech Pathology"
        ],
        "training_packages": []
        },
        "0619": {
        "code": "0619",
        "name": "Complementary Therapies",
        "description": "Complementary Therapies disciplines covering key subfields such as Acupuncture, Naturopathy, and Traditional Chinese Medicine.",
        "keywords": [
            "Acupuncture",
            "Complementary Therapies, n.e.c.",
            "Naturopathy",
            "Traditional Chinese Medicine"
        ],
        "training_packages": []
        },
        "0699": {
        "code": "0699",
        "name": "Other Health",
        "description": "Other Health disciplines covering key subfields such as First Aid, Human Movement, and Nutrition and Dietetics.",
        "keywords": [
            "First Aid",
            "Health, n.e.c.",
            "Human Movement",
            "Nutrition and Dietetics",
            "Paramedical Studies"
        ],
        "training_packages": []
        },
        "0701": {
        "code": "0701",
        "name": "Teacher Education",
        "description": "Teacher Education disciplines covering key subfields such as English as a Second Language Teaching and Nursing Education Teacher Training.",
        "keywords": [
            "English as a Second Language Teaching",
            "Nursing Education Teacher Training",
            "Teacher Education, n.e.c.",
            "Teacher Education: Early Childhood",
            "Teacher Education: Higher Education",
            "Teacher Education: Primary",
            "Teacher Education: Secondary",
            "Teacher Education: Special Education",
            "Teacher Education: Vocational Education and Training",
            "Teacher-Librarianship"
        ],
        "training_packages": []
        },
        "0703": {
        "code": "0703",
        "name": "Curriculum and Education Studies",
        "description": "Curriculum and Education Studies disciplines covering key subfields such as Curriculum Studies, and Education Studies.",
        "keywords": [
            "Curriculum Studies",
            "Education Studies"
        ],
        "training_packages": []
        },
        "0799": {
        "code": "0799",
        "name": "Other Education",
        "description": "Other Education disciplines spanning core studies and related applied fields.",
        "keywords": [
            "Education, n.e.c."
        ],
        "training_packages": []
        },
        "0801": {
        "code": "0801",
        "name": "Accounting",
        "description": "Accounting disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Accounting"
        ],
        "training_packages": []
        },
        "0803": {
        "code": "0803",
        "name": "Business and Management",
        "description": "Business and Management disciplines covering key subfields such as Business Management, Farm Management and Agribusiness, and Hospitality Management.",
        "keywords": [
            "Business Management",
            "Business and Management, n.e.c.",
            "Farm Management and Agribusiness",
            "Hospitality Management",
            "Human Resource Management",
            "Industrial Relations",
            "International Business",
            "Organisation Management",
            "Personal Management Training",
            "Project Management",
            "Public and Health Care Administration",
            "Quality Management",
            "Tourism Management"
        ],
        "training_packages": []
        },
        "0805": {
        "code": "0805",
        "name": "Sales and Marketing",
        "description": "Sales and Marketing disciplines covering key subfields such as Advertising, Marketing, and Public Relations.",
        "keywords": [
            "Advertising",
            "Marketing",
            "Public Relations",
            "Real Estate",
            "Sales",
            "Sales and Marketing, n.e.c."
        ],
        "training_packages": []
        },
        "0807": {
        "code": "0807",
        "name": "Tourism",
        "description": "Tourism disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Tourism"
        ],
        "training_packages": []
        },
        "0809": {
        "code": "0809",
        "name": "Office Studies",
        "description": "Office Studies disciplines covering key subfields such as Keyboard Skills, Practical Computing Skills, and Secretarial and Clerical Studies.",
        "keywords": [
            "Keyboard Skills",
            "Office Studies, n.e.c.",
            "Practical Computing Skills",
            "Secretarial and Clerical Studies"
        ],
        "training_packages": []
        },
        "0811": {
        "code": "0811",
        "name": "Banking, Finance and Related Fields",
        "description": "Banking, Finance and Related Fields disciplines covering key subfields such as Banking and Finance and Insurance and Actuarial Studies.",
        "keywords": [
            "Banking and Finance",
            "Banking, Finance and Related Fields, n.e.c.",
            "Insurance and Actuarial Studies",
            "Investment and Securities"
        ],
        "training_packages": []
        },
        "0899": {
        "code": "0899",
        "name": "Other Management and Commerce",
        "description": "Other Management and Commerce disciplines covering key subfields such as Purchasing, Warehousing and Distribution, and Valuation.",
        "keywords": [
            "Management and Commerce, n.e.c.",
            "Purchasing, Warehousing and Distribution",
            "Valuation"
        ],
        "training_packages": []
        },
        "0901": {
        "code": "0901",
        "name": "Political Science and Policy Studies",
        "description": "Political Science and Policy Studies disciplines covering key subfields such as Policy Studies, and Political Science.",
        "keywords": [
            "Policy Studies",
            "Political Science"
        ],
        "training_packages": []
        },
        "0903": {
        "code": "0903",
        "name": "Studies in Human Society",
        "description": "Studies in Human Society disciplines covering key subfields such as Anthropology, Archaeology, and Gender Specific Studies.",
        "keywords": [
            "Anthropology",
            "Archaeology",
            "Gender Specific Studies",
            "History",
            "Human Geography",
            "Indigenous Studies",
            "Sociology",
            "Studies in Human Society, n.e.c."
        ],
        "training_packages": []
        },
        "0905": {
        "code": "0905",
        "name": "Human Welfare Studies and Services",
        "description": "Human Welfare Studies and Services disciplines covering key subfields such as Care for the Aged and Care for the Disabled.",
        "keywords": [
            "Care for the Aged",
            "Care for the Disabled",
            "Children's Services",
            "Counselling",
            "Human Welfare Studies and Services, n.e.c.",
            "Residential Client Care",
            "Social Work",
            "Welfare Studies",
            "Youth Work"
        ],
        "training_packages": []
        },
        "0907": {
        "code": "0907",
        "name": "Behavioural Science",
        "description": "Behavioural Science disciplines covering key subfields such as . Emphasises theory, practice, and industry-relevant applications.",
        "keywords": [
            "Behavioural Science, n.e.c.",
            "Psychology"
        ],
        "training_packages": []
        },
        "0909": {
        "code": "0909",
        "name": "Law",
        "description": "Law disciplines covering key subfields such as Business and Commercial Law, Constitutional Law, and Criminal Law.",
        "keywords": [
            "Business and Commercial Law",
            "Constitutional Law",
            "Criminal Law",
            "Family Law",
            "International Law",
            "Law, n.e.c.",
            "Legal Practice",
            "Taxation Law"
        ],
        "training_packages": []
        },
        "0911": {
        "code": "0911",
        "name": "Justice and Law Enforcement",
        "description": "Justice and Law Enforcement disciplines covering key subfields such as Justice Administration, Legal Studies, and Police Studies.",
        "keywords": [
            "Justice Administration",
            "Justice and Law Enforcement, n.e.c.",
            "Legal Studies",
            "Police Studies"
        ],
        "training_packages": []
        },
        "0913": {
        "code": "0913",
        "name": "Librarianship, Information Management and Curatorial Studies",
        "description": "Librarianship, Information Management and Curatorial Studies disciplines covering key subfields such as Curatorial Studies, and Librarianship and Information Management.",
        "keywords": [
            "Curatorial Studies",
            "Librarianship and Information Management"
        ],
        "training_packages": []
        },
        "0915": {
        "code": "0915",
        "name": "Language and Literature",
        "description": "Language and Literature disciplines covering key subfields such as Australian Indigenous Languages, Eastern Asian Languages, and Eastern European Languages.",
        "keywords": [
            "Australian Indigenous Languages",
            "Eastern Asian Languages",
            "Eastern European Languages",
            "English Language",
            "Language and Literature, n.e.c.",
            "Linguistics",
            "Literature",
            "Northern European Languages",
            "Southeast Asian Languages",
            "Southern Asian Languages",
            "Southern European Languages",
            "Southwest Asian and North African Languages",
            "Translating and Interpreting"
        ],
        "training_packages": []
        },
        "0917": {
        "code": "0917",
        "name": "Philosophy and Religious Studies",
        "description": "Philosophy and Religious Studies disciplines covering key subfields such as Philosophy, and Religious Studies.",
        "keywords": [
            "Philosophy",
            "Religious Studies"
        ],
        "training_packages": []
        },
        "0919": {
        "code": "0919",
        "name": "Economics and Econometrics",
        "description": "Economics and Econometrics disciplines covering key subfields such as Econometrics, and Economics.",
        "keywords": [
            "Econometrics",
            "Economics"
        ],
        "training_packages": []
        },
        "0921": {
        "code": "0921",
        "name": "Sport and Recreation",
        "description": "Sport and Recreation disciplines covering key subfields such as Sport and Recreation Activities, and Sports Coaching, Officiating and Instruction.",
        "keywords": [
            "Sport and Recreation Activities",
            "Sport and Recreation, n.e.c.",
            "Sports Coaching, Officiating and Instruction"
        ],
        "training_packages": []
        },
        "0999": {
        "code": "0999",
        "name": "Other Society and Culture",
        "description": "Other Society and Culture disciplines covering key subfields such as Criminology, Family and Consumer Studies, and Security Services.",
        "keywords": [
            "Criminology",
            "Family and Consumer Studies",
            "Security Services",
            "Society and Culture, n.e.c."
        ],
        "training_packages": []
        },
        "1001": {
        "code": "1001",
        "name": "Performing Arts",
        "description": "Performing Arts disciplines covering key subfields such as Dance, Drama and Theatre Studies, and Music.",
        "keywords": [
            "Dance",
            "Drama and Theatre Studies",
            "Music",
            "Performing Arts, n.e.c."
        ],
        "training_packages": []
        },
        "1003": {
        "code": "1003",
        "name": "Visual Arts and Crafts",
        "description": "Visual Arts and Crafts disciplines covering key subfields such as Crafts, Fine Arts, and Floristry.",
        "keywords": [
            "Crafts",
            "Fine Arts",
            "Floristry",
            "Jewellery Making",
            "Photography",
            "Visual Arts and Crafts, n.e.c."
        ],
        "training_packages": []
        },
        "1005": {
        "code": "1005",
        "name": "Graphic and Design Studies",
        "description": "Graphic and Design Studies disciplines covering key subfields such as Fashion Design, Graphic Arts and Design Studies, and Textile Design.",
        "keywords": [
            "Fashion Design",
            "Graphic Arts and Design Studies",
            "Graphic and Design Studies, n.e.c.",
            "Textile Design"
        ],
        "training_packages": []
        },
        "1007": {
        "code": "1007",
        "name": "Communication and Media Studies",
        "description": "Communication and Media Studies disciplines covering key subfields such as Audio Visual Studies, Journalism, and Verbal Communication.",
        "keywords": [
            "Audio Visual Studies",
            "Communication and Media Studies, n.e.c.",
            "Journalism",
            "Verbal Communication",
            "Written Communication"
        ],
        "training_packages": []
        },
        "1099": {
        "code": "1099",
        "name": "Other Creative Arts",
        "description": "Other Creative Arts disciplines spanning core studies and related applied fields.",
        "keywords": [
            "Creative Arts, n.e.c."
        ],
        "training_packages": []
        },
        "1101": {
        "code": "1101",
        "name": "Food and Hospitality",
        "description": "Food and Hospitality disciplines covering key subfields such as Baking and Pastrymaking, Butchery, and Cookery.",
        "keywords": [
            "Baking and Pastrymaking",
            "Butchery",
            "Cookery",
            "Food Hygiene",
            "Food and Beverage Service",
            "Food and Hospitality, n.e.c.",
            "Hospitality"
        ],
        "training_packages": []
        },
        "1103": {
        "code": "1103",
        "name": "Personal Services",
        "description": "Personal Services disciplines covering key subfields such as Beauty Therapy, and Hairdressing.",
        "keywords": [
            "Beauty Therapy",
            "Hairdressing",
            "Personal Services, n.e.c."
        ],
        "training_packages": []
        },
        "1201": {
        "code": "1201",
        "name": "General Education Programmes",
        "description": "General Education Programmes disciplines covering key subfields such as General Primary and Secondary Education Programmes and Learning Skills Programmes.",
        "keywords": [
            "General Education Programmes, n.e.c.",
            "General Primary and Secondary Education Programmes",
            "Learning Skills Programmes",
            "Literacy and Numeracy Programmes"
        ],
        "training_packages": []
        },
        "1203": {
        "code": "1203",
        "name": "Social Skills Programmes",
        "description": "Social Skills Programmes disciplines covering key subfields such as Parental Education Programmes and Social and Interpersonal Skills Programmes.",
        "keywords": [
            "Parental Education Programmes",
            "Social Skills Programmes, n.e.c.",
            "Social and Interpersonal Skills Programmes",
            "Survival Skills Programmes"
        ],
        "training_packages": []
        },
        "1205": {
        "code": "1205",
        "name": "Employment Skills Programmes",
        "description": "Employment Skills Programmes disciplines covering key subfields such as Career Development Programmes, Job Search Skills Programmes, and Work Practices Programmes.",
        "keywords": [
            "Career Development Programmes",
            "Employment Skills Programmes, n.e.c.",
            "Job Search Skills Programmes",
            "Work Practices Programmes"
        ],
        "training_packages": []
        },
        "1299": {
        "code": "1299",
        "name": "Other Mixed Field Programmes",
        "description": "Other Mixed Field Programmes disciplines spanning core studies and related applied fields.",
        "keywords": [
            "Mixed Field Programmes, n.e.c."
        ],
        "training_packages": []
        }
    }
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
    "IND": INDUSTRY_DOMAIN_FACET,
    "LVL": PROFICIENCY_LEVEL_FACET,
}

# Facets that allow multiple values
MULTI_VALUE_FACETS = ["IND"]

# Facets with ordered/hierarchical values
ORDERED_FACETS = ["COG", "DIG", "LVL"]

# Priority order for assignment (most important first)
FACET_PRIORITY = ["NAT", "TRF", "COG", "CTX", "FUT", "LRN", "DIG", "IND", "LVL"]


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
    
    # keywords = value.get("keywords", [])
    # if keywords:
    #     text_parts.append(" ".join(keywords[:15]))
    
    return ". ".join([p for p in text_parts if p])


def get_all_facet_embeddings_texts() -> dict:
    """Get all facet values as texts for embedding precomputation"""
    result = {}
    for facet_id, facet in ALL_FACETS.items():
        result[facet_id] = {}
        for value_code in facet.get("values", {}).keys():
            result[facet_id][value_code] = get_facet_text_for_embedding(facet_id, value_code)
    return result
