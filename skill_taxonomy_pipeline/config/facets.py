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
        "TRF.UNI": {"code": "TRF.UNI", "name": "Universal", "description": "Foundational skills applicable across all occupations and industries."},
        "TRF.BRD": {"code": "TRF.BRD", "name": "Cross-Sector", "description": "Specialist skills transferable across multiple industries and sectors."},
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

ASCED_FIELD_OF_EDUCATION_FACET = {
    "facet_id": "ASCED",
    "facet_name": "ASCED Field of Education",
    "description": "Australian Standard Classification of Education (ASCED) - Field of Education classification at the narrow field (4-digit) level",
    "standard": "Australian Standard Classification of Education (ASCED) 2001",
    "reference": "https://www.abs.gov.au/statistics/classifications/australian-standard-classification-education-asced/latest-release",
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
        "description": "Medical Studies disciplines for human only, covering key subfields such as Anaesthesiology, General Medicine, and General Practice.",
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
        "description": "Nursing disciplines for human only, covering key subfields such as Aged Care Nursing, Community Nursing, and Critical Care Nursing.",
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
        "description": "Sport and Recreation for human only, disciplines covering key subfields such as Sport and Recreation Activities, and Sports Coaching, Officiating and Instruction.",
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
        "description": "Personal Services disciplines for human only, covering key subfields such as Beauty Therapy, and Hairdressing.",
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
        "description": "General Education Programmes disciplines for human only covering key subfields such as General Primary and Secondary Education Programmes and Learning Skills Programmes.",
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

# ═══════════════════════════════════════════════════════════════════
#  FACET 5: PROFICIENCY LEVEL (LVL) — SFIA-aligned
# ═══════════════════════════════════════════════════════════════════
# NOTE: LVL is assigned via direct mapping from the 'level' column
# (FacetAssigner._assign_level_facet), not via embedding similarity.
# It must still be in ALL_FACETS so the system recognises it as a facet.

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
#  AGGREGATE
# ═══════════════════════════════════════════════════════════════════

ALL_FACETS = {
    "NAT": SKILL_NATURE_FACET,
    "TRF": TRANSFERABILITY_FACET,
    "COG": COGNITIVE_COMPLEXITY_FACET,
    "ASCED": ASCED_FIELD_OF_EDUCATION_FACET,
    "LVL": PROFICIENCY_LEVEL_FACET,
}

MULTI_VALUE_FACETS = ["ASCED"]

# Ordered list of facets for processing priority
ORDERED_FACETS = ["NAT", "TRF", "COG", "ASCED", "LVL"]

# Default facet assignment priority (used by FacetAssigner when no config override)
FACET_PRIORITY = ["NAT", "TRF", "COG", "ASCED", "LVL"]


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