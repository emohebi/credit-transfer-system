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
        "IND.CON": {
            "code": "IND.CON",
            "name": "Construction & Infrastructure",
            "keywords": ["construction", "building", "infrastructure", "civil", "plumbing", "electrical",
                        "carpentry", "masonry", "engineering", "architecture"],
            "training_packages": ["CPC", "CPP"]
        },
        "IND.MFG": {
            "code": "IND.MFG",
            "name": "Manufacturing & Engineering",
            "keywords": ["manufacturing", "engineering", "fabrication", "production", "assembly",
                        "machining", "welding", "CNC", "industrial"],
            "training_packages": ["MEM", "MSM", "PMB", "PMC"]
        },
        "IND.HLT": {
            "code": "IND.HLT",
            "name": "Health & Community Services",
            "keywords": ["health", "healthcare", "medical", "nursing", "aged care", "disability",
                        "community", "social", "welfare", "mental health", "allied health"],
            "training_packages": ["HLT", "CHC"]
        },
        "IND.ICT": {
            "code": "IND.ICT",
            "name": "Information & Communications Technology",
            "keywords": ["IT", "ICT", "technology", "software", "computer", "network", "cyber",
                        "data", "digital", "programming", "web"],
            "training_packages": ["ICT"]
        },
        "IND.BUS": {
            "code": "IND.BUS",
            "name": "Business & Administration",
            "keywords": ["business", "administration", "management", "office", "clerical", "HR",
                        "human resources", "finance", "accounting", "marketing"],
            "training_packages": ["BSB", "FNS"]
        },
        "IND.HOS": {
            "code": "IND.HOS",
            "name": "Hospitality & Tourism",
            "keywords": ["hospitality", "tourism", "hotel", "restaurant", "food", "beverage",
                        "catering", "events", "travel", "accommodation"],
            "training_packages": ["SIT"]
        },
        "IND.RET": {
            "code": "IND.RET",
            "name": "Retail & Consumer Services",
            "keywords": ["retail", "sales", "customer service", "merchandising", "store",
                        "consumer", "shopping"],
            "training_packages": ["SIR"]
        },
        "IND.AUT": {
            "code": "IND.AUT",
            "name": "Automotive",
            "keywords": ["automotive", "motor", "vehicle", "car", "truck", "mechanic", "auto",
                        "diesel", "collision", "panel"],
            "training_packages": ["AUM", "AUR"]
        },
        "IND.AGR": {
            "code": "IND.AGR",
            "name": "Agriculture & Environment",
            "keywords": ["agriculture", "farming", "horticulture", "livestock", "environment",
                        "conservation", "forestry", "aquaculture", "rural"],
            "training_packages": ["AHC", "ACM", "FWP", "SFI"]
        },
        "IND.MIN": {
            "code": "IND.MIN",
            "name": "Mining & Resources",
            "keywords": ["mining", "resources", "oil", "gas", "drilling", "extraction",
                        "minerals", "quarry"],
            "training_packages": ["RII", "DRG"]
        },
        "IND.TRN": {
            "code": "IND.TRN",
            "name": "Transport & Logistics",
            "keywords": ["transport", "logistics", "warehousing", "freight", "shipping",
                        "supply chain", "distribution", "driving"],
            "training_packages": ["TLI", "MAR", "AVI"]
        },
        "IND.EDU": {
            "code": "IND.EDU",
            "name": "Education & Training",
            "keywords": ["education", "training", "teaching", "learning", "instruction",
                        "assessment", "curriculum", "facilitation"],
            "training_packages": ["TAE"]
        },
        "IND.CRE": {
            "code": "IND.CRE",
            "name": "Creative & Design",
            "keywords": ["creative", "design", "arts", "media", "film", "music", "visual",
                        "graphic", "photography", "fashion"],
            "training_packages": ["CUA", "CUF", "CUV", "SHB"]
        },
        "IND.GOV": {
            "code": "IND.GOV",
            "name": "Government & Public Safety",
            "keywords": ["government", "public sector", "defence", "police", "emergency",
                        "fire", "corrections", "security"],
            "training_packages": ["PSP", "PUA", "DEF", "POL", "CSC"]
        },
        "IND.UTL": {
            "code": "IND.UTL",
            "name": "Utilities & Energy",
            "keywords": ["electricity", "gas", "water", "utilities", "energy", "power",
                        "renewable", "solar", "wind"],
            "training_packages": ["UEE", "UEG", "UEP", "UET", "NWP"]
        },
        "IND.SCI": {
            "code": "IND.SCI",
            "name": "Science & Laboratory",
            "keywords": ["science", "laboratory", "research", "testing", "analysis",
                        "pharmaceutical", "biotech"],
            "training_packages": ["MSL", "FBP"]
        },
        "IND.SPT": {
            "code": "IND.SPT",
            "name": "Sport & Recreation",
            "keywords": ["sport", "fitness", "recreation", "gym", "coaching", "outdoor",
                        "aquatics", "personal training"],
            "training_packages": ["SIS"]
        },
        "IND.ALL": {
            "code": "IND.ALL",
            "name": "Cross-Industry",
            "keywords": ["all industries", "cross-industry", "universal", "general",
                        "transferable", "core"],
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
            "name": "Foundation",
            "level": 1,
            "description": "Basic awareness, performs routine tasks under close supervision",
            "aqf_level": "Certificate I",
            "sfia_level": "Follow",
            "keywords": ["basic", "introductory", "awareness", "fundamental", "entry"]
        },
        "LVL.2": {
            "code": "LVL.2",
            "name": "Developing",
            "level": 2,
            "description": "Applies skills in routine contexts with guidance",
            "aqf_level": "Certificate II",
            "sfia_level": "Assist",
            "keywords": ["developing", "routine", "guided", "supervised"]
        },
        "LVL.3": {
            "code": "LVL.3",
            "name": "Competent",
            "level": 3,
            "description": "Works independently in standard situations",
            "aqf_level": "Certificate III",
            "sfia_level": "Apply",
            "keywords": ["competent", "independent", "skilled", "trade"]
        },
        "LVL.4": {
            "code": "LVL.4",
            "name": "Proficient",
            "level": 4,
            "description": "Handles complex situations, may supervise others",
            "aqf_level": "Certificate IV",
            "sfia_level": "Enable",
            "keywords": ["proficient", "complex", "supervisor", "coordinator"]
        },
        "LVL.5": {
            "code": "LVL.5",
            "name": "Advanced",
            "level": 5,
            "description": "Expert in specialised areas, provides guidance",
            "aqf_level": "Diploma",
            "sfia_level": "Ensure/Advise",
            "keywords": ["advanced", "specialist", "expert", "advisor"]
        },
        "LVL.6": {
            "code": "LVL.6",
            "name": "Expert",
            "level": 6,
            "description": "Leads and influences, strategic capability",
            "aqf_level": "Advanced Diploma/Associate Degree",
            "sfia_level": "Initiate/Influence",
            "keywords": ["expert", "leader", "strategic", "senior"]
        },
        "LVL.7": {
            "code": "LVL.7",
            "name": "Master",
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
    
    keywords = value.get("keywords", [])
    if keywords:
        text_parts.append(" ".join(keywords[:15]))
    
    return ". ".join([p for p in text_parts if p])


def get_all_facet_embeddings_texts() -> dict:
    """Get all facet values as texts for embedding precomputation"""
    result = {}
    for facet_id, facet in ALL_FACETS.items():
        result[facet_id] = {}
        for value_code in facet.get("values", {}).keys():
            result[facet_id][value_code] = get_facet_text_for_embedding(facet_id, value_code)
    return result
