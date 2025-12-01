"""
Enhanced Configuration settings for multi-dimensional skill taxonomy pipeline
Implements state-of-the-art taxonomy structure with 5-level hierarchy and cross-cutting dimensions
"""
import os
from pathlib import Path
from typing import Dict, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = PROJECT_ROOT / "cache"

# Create directories if they don't exist
for dir_path in [DATA_DIR, OUTPUT_DIR, CACHE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# MULTI-DIMENSIONAL TAXONOMY STRUCTURE CONFIGURATION
# ============================================================================
SKILL_DOMAINS = {
    "agriculture_primary": {
        "name": "Agriculture, Horticulture & Primary Industries",
        "description": "Farming, horticulture, conservation, land management, animal care, aquaculture, and primary production",
        "training_packages": ["AHC", "ACM", "AMP", "SFI", "FWP"],
        "keywords": ["agriculture", "farming", "horticulture", "gardening", "livestock", "crops", "animal", "conservation", "land management", "forestry", "aquaculture", "fishing", "meat processing"]
    },
    
    "construction_building": {
        "name": "Construction, Building & Trades",
        "description": "Building, construction, plumbing, electrical, carpentry, and related trade skills",
        "training_packages": ["CPC", "CPP", "MSF"],
        "keywords": ["construction", "building", "carpentry", "plumbing", "electrical", "bricklaying", "tiling", "painting", "plastering", "roofing", "concreting", "scaffolding", "demolition"]
    },
    
    "automotive_transport": {
        "name": "Automotive, Transport & Logistics",
        "description": "Automotive services, transport operations, logistics, warehousing, and supply chain",
        "training_packages": ["AUR", "AUM", "TLI", "MAR"],
        "keywords": ["automotive", "vehicle", "car", "truck", "transport", "logistics", "supply chain", "warehousing", "distribution", "freight", "driving", "maritime", "shipping"]
    },
    
    "manufacturing_engineering": {
        "name": "Manufacturing, Engineering & Production",
        "description": "Manufacturing processes, engineering, production, quality control, and industrial operations",
        "training_packages": ["MEM", "MSM", "MST", "PMA", "PMB", "PMC"],
        "keywords": ["manufacturing", "engineering", "production", "fabrication", "machining", "assembly", "quality control", "industrial", "maintenance", "mechanical", "processing"]
    },
    
    "digital_technology": {
        "name": "Digital Technology & ICT",
        "description": "Information technology, software development, cybersecurity, telecommunications, and digital media",
        "training_packages": ["ICT", "ICP"],
        "keywords": ["IT", "technology", "software", "programming", "computer", "digital", "cyber", "network", "telecommunications", "data", "web", "app", "systems", "cloud"]
    },
    
    "healthcare_community": {
        "name": "Healthcare & Community Services",
        "description": "Health services, nursing, allied health, aged care, disability support, and community services",
        "training_packages": ["HLT", "CHC"],
        "keywords": ["health", "medical", "nursing", "clinical", "patient care", "aged care", "disability", "community services", "social work", "mental health", "rehabilitation", "therapy"]
    },
    
    "business_finance": {
        "name": "Business, Finance & Administration",
        "description": "Business operations, finance, accounting, administration, management, and professional services",
        "training_packages": ["BSB", "FNS", "LGA", "PSP"],
        "keywords": ["business", "finance", "accounting", "administration", "management", "office", "marketing", "sales", "HR", "payroll", "bookkeeping", "governance", "policy"]
    },
    
    "education_training": {
        "name": "Education, Training & Development",
        "description": "Teaching, training, education support, childcare, and learning development",
        "training_packages": ["CHC", "TAE"],
        "keywords": ["education", "teaching", "training", "childcare", "early childhood", "learning", "instruction", "tutoring", "education support", "curriculum", "assessment"]
    },
    
    "hospitality_tourism": {
        "name": "Hospitality, Tourism & Events",
        "description": "Hospitality services, tourism, travel, events, food service, and accommodation",
        "training_packages": ["SIT", "SFL"],
        "keywords": ["hospitality", "tourism", "hotel", "restaurant", "catering", "cooking", "chef", "food service", "events", "travel", "accommodation", "bar", "cafe"]
    },
    
    "creative_arts": {
        "name": "Creative Arts, Culture & Entertainment",
        "description": "Visual arts, performing arts, design, media, entertainment, and cultural industries",
        "training_packages": ["CUA", "CUF", "CUS", "CUV", "ICP"],
        "keywords": ["arts", "creative", "design", "media", "entertainment", "music", "dance", "theatre", "film", "photography", "graphic design", "fashion", "cultural"]
    },
    
    "public_safety": {
        "name": "Public Safety, Security & Defence",
        "description": "Emergency services, law enforcement, security, firefighting, corrections, and defence",
        "training_packages": ["PUA", "POL", "CSC", "DEF"],
        "keywords": ["safety", "security", "emergency", "fire", "police", "law enforcement", "defence", "military", "corrections", "rescue", "investigation", "protective services"]
    },
    
    "utilities_resources": {
        "name": "Utilities, Resources & Infrastructure",
        "description": "Mining, resources, utilities, water, energy, electrotechnology, and infrastructure",
        "training_packages": ["RII", "UEE", "UEP", "UET", "NWP", "DRG"],
        "keywords": ["mining", "resources", "utilities", "water", "electricity", "energy", "infrastructure", "gas", "oil", "drilling", "extraction", "power", "electrical"]
    },
    
    "science_technical": {
        "name": "Science, Laboratory & Technical Services",
        "description": "Scientific research, laboratory work, technical services, and applied sciences",
        "training_packages": ["MSL", "PMA"],
        "keywords": ["science", "laboratory", "research", "testing", "analysis", "chemistry", "biology", "technical", "scientific", "lab", "pathology", "measurement"]
    },
    
    "sport_recreation": {
        "name": "Sport, Fitness & Recreation",
        "description": "Sport coaching, fitness instruction, recreation, outdoor education, and racing",
        "training_packages": ["SIS", "RGR"],
        "keywords": ["sport", "fitness", "recreation", "outdoor", "coaching", "trainer", "exercise", "gym", "aquatic", "racing", "outdoor education", "adventure"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL FAMILIES - 85+ Detailed Classifications Mapped to Training Packages
# ═══════════════════════════════════════════════════════════════════════════

SKILL_FAMILIES = {
    # ───────────────────────────────────────────────────────────────────────
    # AGRICULTURE, HORTICULTURE & PRIMARY INDUSTRIES (11 families)
    # ───────────────────────────────────────────────────────────────────────
    "crop_production": {
        "name": "Crop Production & Farming",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["cropping", "farming", "grains", "cereals", "field crops", "planting", "harvesting", "irrigation", "pest control"]
    },
    
    "horticulture_landscaping": {
        "name": "Horticulture & Landscaping",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["horticulture", "landscaping", "gardens", "turf", "nursery", "plants", "flowers", "grounds maintenance", "arboriculture"]
    },
    
    "livestock_animal_production": {
        "name": "Livestock & Animal Production",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["livestock", "cattle", "sheep", "pigs", "poultry", "grazing", "animal husbandry", "breeding", "feedlot"]
    },
    
    "animal_care_management": {
        "name": "Animal Care & Management",
        "domain": "agriculture_primary",
        "training_package": "ACM",
        "keywords": ["animal care", "veterinary", "pet care", "dog grooming", "animal welfare", "kennels", "catteries", "wildlife"]
    },
    
    "meat_processing": {
        "name": "Meat Processing & Production",
        "domain": "agriculture_primary",
        "training_package": "AMP",
        "keywords": ["meat processing", "abattoir", "butchery", "meat inspection", "slaughtering", "meat retail", "carcass"]
    },
    
    "aquaculture_fishing": {
        "name": "Aquaculture & Fishing",
        "domain": "agriculture_primary",
        "training_package": "SFI",
        "keywords": ["aquaculture", "fishing", "seafood", "fish farming", "oyster", "prawn", "commercial fishing", "marine"]
    },
    
    "forestry_conservation": {
        "name": "Forestry & Conservation",
        "domain": "agriculture_primary",
        "training_package": "FWP",
        "keywords": ["forestry", "logging", "timber", "conservation", "forest management", "sawmilling", "tree care", "arboriculture"]
    },
    
    "conservation_land_management": {
        "name": "Conservation & Land Management",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["conservation", "land management", "parks", "natural resource management", "biodiversity", "environmental", "ecology"]
    },
    
    "equine_racing": {
        "name": "Equine & Racing Industry",
        "domain": "agriculture_primary",
        "training_package": "RGR",
        "keywords": ["horse", "equine", "racing", "thoroughbred", "harness racing", "greyhound", "jockey", "stable", "track"]
    },
    
    "viticulture_winemaking": {
        "name": "Viticulture & Winemaking",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["viticulture", "winemaking", "vineyard", "grapes", "wine production", "cellar", "oenology"]
    },
    
    "rural_operations": {
        "name": "Rural Operations & Farm Management",
        "domain": "agriculture_primary",
        "training_package": "AHC",
        "keywords": ["farm management", "rural operations", "agricultural", "farm machinery", "station management"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # CONSTRUCTION, BUILDING & TRADES (12 families)
    # ───────────────────────────────────────────────────────────────────────
    "building_construction": {
        "name": "Building & Construction",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["building", "construction", "residential", "commercial", "building surveying", "construction management"]
    },
    
    "carpentry_joinery": {
        "name": "Carpentry & Joinery",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["carpentry", "joinery", "formwork", "timber", "framing", "cabinetmaking", "carpenter"]
    },
    
    "plumbing_services": {
        "name": "Plumbing & Gasfitting",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["plumbing", "gasfitting", "drainage", "water services", "sanitary", "pipework", "plumber"]
    },
    
    "electrical_trades": {
        "name": "Electrical Trades",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["electrical", "electrician", "wiring", "electrical installation", "electrical fitting", "powerline"]
    },
    
    "bricklaying_blocklaying": {
        "name": "Bricklaying & Blocklaying",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["bricklaying", "blocklaying", "masonry", "brickwork", "stone masonry", "paving"]
    },
    
    "painting_decorating": {
        "name": "Painting & Decorating",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["painting", "decorating", "signwriting", "coating", "surface preparation", "spray painting"]
    },
    
    "plastering_wall_ceiling": {
        "name": "Plastering & Wall/Ceiling Lining",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["plastering", "wall lining", "ceiling", "solid plastering", "fibrous plastering", "rendering"]
    },
    
    "roof_wall_floor_tiling": {
        "name": "Roofing, Wall & Floor Tiling",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["roofing", "tiling", "wall tiling", "floor tiling", "roof plumbing", "metal roofing"]
    },
    
    "property_services": {
        "name": "Property Services & Facilities Management",
        "domain": "construction_building",
        "training_package": "CPP",
        "keywords": ["property services", "real estate", "facility management", "cleaning", "asset maintenance", "building surveying"]
    },
    
    "air_conditioning_refrigeration": {
        "name": "Air Conditioning & Refrigeration",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["air conditioning", "refrigeration", "HVAC", "mechanical services", "climate control"]
    },
    
    "civil_construction": {
        "name": "Civil Construction & Infrastructure",
        "domain": "construction_building",
        "training_package": "CPC",
        "keywords": ["civil construction", "roads", "bridges", "earthmoving", "concrete", "infrastructure", "highway"]
    },
    
    "furnishing_flooring": {
        "name": "Furnishing, Upholstery & Flooring",
        "domain": "construction_building",
        "training_package": "MSF",
        "keywords": ["furnishing", "upholstery", "flooring", "furniture", "floor covering", "blinds", "curtains"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # AUTOMOTIVE, TRANSPORT & LOGISTICS (8 families)
    # ───────────────────────────────────────────────────────────────────────
    "automotive_mechanical": {
        "name": "Automotive Mechanical Repair",
        "domain": "automotive_transport",
        "training_package": "AUR",
        "keywords": ["automotive", "mechanic", "vehicle repair", "engine", "automotive servicing", "light vehicle", "heavy vehicle"]
    },
    
    "automotive_electrical": {
        "name": "Automotive Electrical & Electronics",
        "domain": "automotive_transport",
        "training_package": "AUR",
        "keywords": ["automotive electrical", "auto electrical", "vehicle electronics", "automotive technology"]
    },
    
    "automotive_body_repair": {
        "name": "Automotive Body Repair & Painting",
        "domain": "automotive_transport",
        "training_package": "AUR",
        "keywords": ["panel beating", "spray painting", "automotive refinishing", "collision repair", "vehicle painting"]
    },
    
    "automotive_manufacturing": {
        "name": "Automotive Manufacturing",
        "domain": "automotive_transport",
        "training_package": "AUM",
        "keywords": ["automotive manufacturing", "vehicle assembly", "automotive components", "production"]
    },
    
    "transport_logistics": {
        "name": "Transport & Logistics Operations",
        "domain": "automotive_transport",
        "training_package": "TLI",
        "keywords": ["transport", "logistics", "warehousing", "supply chain", "freight", "distribution", "inventory"]
    },
    
    "driving_operations": {
        "name": "Driving & Vehicle Operations",
        "domain": "automotive_transport",
        "training_package": "TLI",
        "keywords": ["driving", "truck driving", "forklift", "bus driving", "mobile crane", "vehicle operations"]
    },
    
    "maritime_operations": {
        "name": "Maritime Operations",
        "domain": "automotive_transport",
        "training_package": "MAR",
        "keywords": ["maritime", "shipping", "marine", "vessel operations", "port operations", "maritime safety"]
    },
    
    "aviation_services": {
        "name": "Aviation Services & Operations",
        "domain": "automotive_transport",
        "training_package": "AVI",
        "keywords": ["aviation", "aircraft", "airport operations", "aviation services", "flight operations", "cabin crew"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # MANUFACTURING, ENGINEERING & PRODUCTION (7 families)
    # ───────────────────────────────────────────────────────────────────────
    "engineering_mechanical": {
        "name": "Mechanical & Manufacturing Engineering",
        "domain": "manufacturing_engineering",
        "training_package": "MEM",
        "keywords": ["engineering", "mechanical", "manufacturing", "fabrication", "machining", "fitting", "turning"]
    },
    
    "metal_fabrication": {
        "name": "Metal Fabrication & Welding",
        "domain": "manufacturing_engineering",
        "training_package": "MEM",
        "keywords": ["metal fabrication", "welding", "boilermaking", "sheetmetal", "structural steel", "metal trades"]
    },
    
    "production_manufacturing": {
        "name": "Production & Process Manufacturing",
        "domain": "manufacturing_engineering",
        "training_package": "PMA",
        "keywords": ["production", "process", "manufacturing operations", "production systems", "industrial"]
    },
    
    "textiles_clothing": {
        "name": "Textiles, Clothing & Footwear",
        "domain": "manufacturing_engineering",
        "training_package": "MST",
        "keywords": ["textiles", "clothing", "footwear", "garment", "textile production", "fashion production"]
    },
    
    "polymer_manufacturing": {
        "name": "Polymer & Chemical Manufacturing",
        "domain": "manufacturing_engineering",
        "training_package": "PMB",
        "keywords": ["polymer", "plastics", "chemical manufacturing", "process plant", "petrochemical"]
    },
    
    "process_plant_operations": {
        "name": "Process Plant Operations",
        "domain": "manufacturing_engineering",
        "training_package": "PMC",
        "keywords": ["process plant", "plant operations", "chemical plant", "processing", "industrial operations"]
    },
    
    "aerospace_manufacturing": {
        "name": "Aerospace & Aircraft Maintenance",
        "domain": "manufacturing_engineering",
        "training_package": "MEA",
        "keywords": ["aerospace", "aircraft maintenance", "avionics", "aeroskills", "aircraft engineering"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # DIGITAL TECHNOLOGY & ICT (6 families)
    # ───────────────────────────────────────────────────────────────────────
    "software_development": {
        "name": "Software Development & Programming",
        "domain": "digital_technology",
        "training_package": "ICT",
        "keywords": ["software development", "programming", "coding", "web development", "app development", "software engineering"]
    },
    
    "network_systems": {
        "name": "Network & Systems Administration",
        "domain": "digital_technology",
        "training_package": "ICT",
        "keywords": ["networking", "systems administration", "infrastructure", "network security", "server management"]
    },
    
    "cybersecurity": {
        "name": "Cybersecurity & Information Security",
        "domain": "digital_technology",
        "training_package": "ICT",
        "keywords": ["cybersecurity", "information security", "cyber", "security operations", "threat intelligence"]
    },
    
    "database_data": {
        "name": "Database & Data Management",
        "domain": "digital_technology",
        "training_package": "ICT",
        "keywords": ["database", "data management", "data analysis", "business intelligence", "SQL", "data warehousing"]
    },
    
    "it_support": {
        "name": "IT Support & Helpdesk",
        "domain": "digital_technology",
        "training_package": "ICT",
        "keywords": ["IT support", "technical support", "helpdesk", "user support", "desktop support"]
    },
    
    "printing_graphic_arts": {
        "name": "Printing & Graphic Arts",
        "domain": "digital_technology",
        "training_package": "ICP",
        "keywords": ["printing", "graphic arts", "print production", "digital printing", "prepress", "finishing"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # HEALTHCARE & COMMUNITY SERVICES (10 families)
    # ───────────────────────────────────────────────────────────────────────
    "nursing_clinical": {
        "name": "Nursing & Clinical Care",
        "domain": "healthcare_community",
        "training_package": "HLT",
        "keywords": ["nursing", "clinical", "patient care", "enrolled nurse", "registered nurse", "acute care"]
    },
    
    "allied_health": {
        "name": "Allied Health Services",
        "domain": "healthcare_community",
        "training_package": "HLT",
        "keywords": ["allied health", "physiotherapy", "occupational therapy", "podiatry", "dental", "optical"]
    },
    
    "aged_care": {
        "name": "Aged Care & Support",
        "domain": "healthcare_community",
        "training_package": "CHC",
        "keywords": ["aged care", "elderly care", "residential aged care", "home care", "dementia care"]
    },
    
    "disability_support": {
        "name": "Disability Support & Services",
        "domain": "healthcare_community",
        "training_package": "CHC",
        "keywords": ["disability support", "individual support", "NDIS", "disability services", "personal care"]
    },
    
    "mental_health": {
        "name": "Mental Health & AOD Services",
        "domain": "healthcare_community",
        "training_package": "CHC",
        "keywords": ["mental health", "alcohol and drugs", "AOD", "counseling", "mental health support"]
    },
    
    "community_services": {
        "name": "Community Services & Social Work",
        "domain": "healthcare_community",
        "training_package": "CHC",
        "keywords": ["community services", "social work", "welfare", "community development", "case management"]
    },
    
    "youth_work": {
        "name": "Youth Work & Family Services",
        "domain": "healthcare_community",
        "training_package": "CHC",
        "keywords": ["youth work", "family services", "child protection", "youth services", "family intervention"]
    },
    
    "health_assistance": {
        "name": "Health Service Assistance",
        "domain": "healthcare_community",
        "training_package": "HLT",
        "keywords": ["health services", "medical receptionist", "ward clerk", "health administration", "patient services"]
    },
    
    "ambulance_paramedic": {
        "name": "Ambulance & Paramedic Services",
        "domain": "healthcare_community",
        "training_package": "HLT",
        "keywords": ["ambulance", "paramedic", "emergency care", "patient transport", "first responder"]
    },
    
    "complementary_therapies": {
        "name": "Complementary & Alternative Therapies",
        "domain": "healthcare_community",
        "training_package": "HLT",
        "keywords": ["massage", "remedial therapy", "aromatherapy", "naturopathy", "complementary health"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # BUSINESS, FINANCE & ADMINISTRATION (8 families)
    # ───────────────────────────────────────────────────────────────────────
    "business_administration": {
        "name": "Business Administration & Management",
        "domain": "business_finance",
        "training_package": "BSB",
        "keywords": ["business", "administration", "management", "business operations", "office management"]
    },
    
    "finance_accounting": {
        "name": "Finance & Accounting",
        "domain": "business_finance",
        "training_package": "FNS",
        "keywords": ["finance", "accounting", "bookkeeping", "financial services", "banking", "payroll"]
    },
    
    "human_resources": {
        "name": "Human Resources & Recruitment",
        "domain": "business_finance",
        "training_package": "BSB",
        "keywords": ["human resources", "HR", "recruitment", "workforce planning", "employee relations"]
    },
    
    "marketing_communication": {
        "name": "Marketing & Communications",
        "domain": "business_finance",
        "training_package": "BSB",
        "keywords": ["marketing", "communications", "advertising", "public relations", "social media", "digital marketing"]
    },
    
    "project_management": {
        "name": "Project Management",
        "domain": "business_finance",
        "training_package": "BSB",
        "keywords": ["project management", "program management", "project coordination", "project administration"]
    },
    
    "procurement_contracting": {
        "name": "Procurement & Contracting",
        "domain": "business_finance",
        "training_package": "BSB",
        "keywords": ["procurement", "purchasing", "contract management", "tendering", "supply"]
    },
    
    "local_government": {
        "name": "Local Government Operations",
        "domain": "business_finance",
        "training_package": "LGA",
        "keywords": ["local government", "council", "municipal", "regulatory services", "community services"]
    },
    
    "public_sector": {
        "name": "Public Sector & Government Services",
        "domain": "business_finance",
        "training_package": "PSP",
        "keywords": ["public sector", "government", "public administration", "policy", "governance"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # EDUCATION, TRAINING & DEVELOPMENT (3 families)
    # ───────────────────────────────────────────────────────────────────────
    "childcare_early_education": {
        "name": "Childcare & Early Childhood Education",
        "domain": "education_training",
        "training_package": "CHC",
        "keywords": ["childcare", "early childhood", "ECEC", "kindergarten", "preschool", "child development"]
    },
    
    "training_assessment": {
        "name": "Training & Assessment",
        "domain": "education_training",
        "training_package": "TAE",
        "keywords": ["training", "assessment", "VET", "trainer", "assessor", "education", "teaching"]
    },
    
    "education_support": {
        "name": "Education Support & Assistance",
        "domain": "education_training",
        "training_package": "CHC",
        "keywords": ["education support", "teacher aide", "learning support", "student support", "classroom assistant"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # HOSPITALITY, TOURISM & EVENTS (5 families)
    # ───────────────────────────────────────────────────────────────────────
    "commercial_cookery": {
        "name": "Commercial Cookery & Culinary Arts",
        "domain": "hospitality_tourism",
        "training_package": "SIT",
        "keywords": ["cooking", "chef", "commercial cookery", "culinary", "kitchen operations", "patisserie"]
    },
    
    "hospitality_operations": {
        "name": "Hospitality Operations & Service",
        "domain": "hospitality_tourism",
        "training_package": "SIT",
        "keywords": ["hospitality", "food and beverage", "restaurant service", "bar operations", "gaming"]
    },
    
    "tourism_travel": {
        "name": "Tourism & Travel Services",
        "domain": "hospitality_tourism",
        "training_package": "SIT",
        "keywords": ["tourism", "travel", "tour guiding", "visitor services", "attractions", "travel agency"]
    },
    
    "events_management": {
        "name": "Events & Conference Management",
        "domain": "hospitality_tourism",
        "training_package": "SIT",
        "keywords": ["events", "event management", "conferences", "exhibitions", "event coordination"]
    },
    
    "floristry": {
        "name": "Floristry & Floral Design",
        "domain": "hospitality_tourism",
        "training_package": "SFL",
        "keywords": ["floristry", "florist", "floral design", "flower arranging", "floral decoration"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # CREATIVE ARTS, CULTURE & ENTERTAINMENT (6 families)
    # ───────────────────────────────────────────────────────────────────────
    "visual_arts": {
        "name": "Visual Arts & Design",
        "domain": "creative_arts",
        "training_package": "CUA",
        "keywords": ["visual arts", "fine arts", "painting", "sculpture", "drawing", "ceramics", "craft"]
    },
    
    "performing_arts": {
        "name": "Performing Arts & Music",
        "domain": "creative_arts",
        "training_package": "CUA",
        "keywords": ["performing arts", "music", "dance", "theatre", "acting", "performance", "drama"]
    },
    
    "screen_media": {
        "name": "Screen & Media Production",
        "domain": "creative_arts",
        "training_package": "CUA",
        "keywords": ["screen", "media", "film", "television", "video production", "broadcasting", "animation"]
    },
    
    "design_creative": {
        "name": "Design & Creative Industries",
        "domain": "creative_arts",
        "training_package": "CUA",
        "keywords": ["design", "graphic design", "interior design", "product design", "industrial design"]
    },
    
    "hairdressing_beauty": {
        "name": "Hairdressing & Beauty Services",
        "domain": "creative_arts",
        "training_package": "SHB",
        "keywords": ["hairdressing", "beauty therapy", "barbering", "makeup", "nail technology", "skin care"]
    },
    
    "live_production": {
        "name": "Live Production & Technical Services",
        "domain": "creative_arts",
        "training_package": "CUA",
        "keywords": ["live production", "technical production", "staging", "sound", "lighting", "entertainment technology"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # PUBLIC SAFETY, SECURITY & DEFENCE (5 families)
    # ───────────────────────────────────────────────────────────────────────
    "emergency_firefighting": {
        "name": "Emergency Services & Firefighting",
        "domain": "public_safety",
        "training_package": "PUA",
        "keywords": ["emergency", "fire", "firefighting", "emergency management", "disaster response", "rescue"]
    },
    
    "policing_investigation": {
        "name": "Policing & Investigation",
        "domain": "public_safety",
        "training_package": "POL",
        "keywords": ["police", "policing", "investigation", "law enforcement", "crime scene", "forensics"]
    },
    
    "security_operations": {
        "name": "Security Operations & Services",
        "domain": "public_safety",
        "training_package": "CPP",
        "keywords": ["security", "security operations", "crowd control", "loss prevention", "security guard"]
    },
    
    "correctional_services": {
        "name": "Correctional Services",
        "domain": "public_safety",
        "training_package": "CSC",
        "keywords": ["corrections", "correctional", "custodial", "prison", "detention", "offender management"]
    },
    
    "defence_military": {
        "name": "Defence & Military Services",
        "domain": "public_safety",
        "training_package": "DEF",
        "keywords": ["defence", "military", "armed forces", "navy", "army", "air force"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # UTILITIES, RESOURCES & INFRASTRUCTURE (7 families)
    # ───────────────────────────────────────────────────────────────────────
    "mining_resources": {
        "name": "Mining & Resources Extraction",
        "domain": "utilities_resources",
        "training_package": "RII",
        "keywords": ["mining", "resources", "extraction", "underground mining", "open cut", "drilling", "blasting"]
    },
    
    "civil_infrastructure": {
        "name": "Civil Infrastructure & Construction",
        "domain": "utilities_resources",
        "training_package": "RII",
        "keywords": ["civil construction", "infrastructure", "roads", "rail", "tunneling", "pipelaying"]
    },
    
    "electrotechnology": {
        "name": "Electrotechnology",
        "domain": "utilities_resources",
        "training_package": "UEE",
        "keywords": ["electrotechnology", "electrical", "electronics", "refrigeration", "air conditioning", "instrumentation"]
    },
    
    "electricity_generation": {
        "name": "Electricity Generation & Supply",
        "domain": "utilities_resources",
        "training_package": "UEP",
        "keywords": ["electricity generation", "power generation", "power station", "energy production"]
    },
    
    "transmission_distribution": {
        "name": "Transmission, Distribution & Rail",
        "domain": "utilities_resources",
        "training_package": "UET",
        "keywords": ["transmission", "distribution", "electricity supply", "rail", "powerlines", "substations"]
    },
    
    "water_utilities": {
        "name": "Water Utilities & Treatment",
        "domain": "utilities_resources",
        "training_package": "NWP",
        "keywords": ["water", "water treatment", "wastewater", "water supply", "sewerage", "utilities"]
    },
    
    "drilling_operations": {
        "name": "Drilling & Resource Operations",
        "domain": "utilities_resources",
        "training_package": "DRG",
        "keywords": ["drilling", "oil and gas", "mineral exploration", "drilling operations", "well operations"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # SCIENCE, LABORATORY & TECHNICAL SERVICES (3 families)
    # ───────────────────────────────────────────────────────────────────────
    "laboratory_operations": {
        "name": "Laboratory Operations & Testing",
        "domain": "science_technical",
        "training_package": "MSL",
        "keywords": ["laboratory", "testing", "analysis", "pathology", "chemistry", "microbiology", "sampling"]
    },
    
    "quality_measurement": {
        "name": "Quality & Measurement Sciences",
        "domain": "science_technical",
        "training_package": "MSL",
        "keywords": ["quality", "measurement", "calibration", "metrology", "testing", "inspection"]
    },
    
    "food_beverage_pharma": {
        "name": "Food, Beverage & Pharmaceutical",
        "domain": "science_technical",
        "training_package": "FBP",
        "keywords": ["food processing", "beverage", "pharmaceutical", "food safety", "food technology"]
    },
    
    # ───────────────────────────────────────────────────────────────────────
    # SPORT, FITNESS & RECREATION (4 families)
    # ───────────────────────────────────────────────────────────────────────
    "fitness_instruction": {
        "name": "Fitness Instruction & Personal Training",
        "domain": "sport_recreation",
        "training_package": "SIS",
        "keywords": ["fitness", "personal training", "gym", "exercise", "strength training", "group fitness"]
    },
    
    "sport_coaching": {
        "name": "Sport Coaching & Development",
        "domain": "sport_recreation",
        "training_package": "SIS",
        "keywords": ["coaching", "sport", "sports coaching", "athlete development", "sports development"]
    },
    
    "outdoor_recreation": {
        "name": "Outdoor Recreation & Education",
        "domain": "sport_recreation",
        "training_package": "SIS",
        "keywords": ["outdoor recreation", "outdoor education", "adventure", "camping", "bushwalking"]
    },
    
    "aquatic_operations": {
        "name": "Aquatic Operations & Lifeguarding",
        "domain": "sport_recreation",
        "training_package": "SIS",
        "keywords": ["aquatic", "swimming", "pool operations", "lifeguard", "aquatic programming"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  AUSTRALIAN TRAINING PACKAGE CODES - Complete Reference
# ═══════════════════════════════════════════════════════════════════════════

TRAINING_PACKAGES = {
    # Primary Industries
    "ACM": "Animal Care and Management",
    "AHC": "Agriculture, Horticulture and Conservation and Land Management",
    "AMP": "Australian Meat Processing",
    "FWP": "Forest and Wood Products",
    "RGR": "Racing Industry",
    "SFI": "Seafood Industry",
    
    # Construction & Building
    "CPC": "Construction, Plumbing and Services",
    "CPP": "Property Services",
    "MSF": "Furnishing",
    
    # Automotive & Transport
    "AUM": "Automotive Manufacturing",
    "AUR": "Automotive Retail, Service and Repair",
    "AVI": "Aviation",
    "MAR": "Maritime",
    "TLI": "Transport and Logistics",
    
    # Manufacturing & Engineering
    "MEA": "Aeroskills",
    "MEM": "Manufacturing and Engineering",
    "MSM": "Manufacturing (Manufactured Mineral Products)",
    "MST": "Textiles, Clothing and Footwear",
    "PMA": "Pulp and Paper Manufacturing Industries",
    "PMB": "Polymer Manufacturing",
    "PMC": "Competitive Manufacturing",
    
    # Technology & ICT
    "ICT": "Information and Communications Technology",
    "ICP": "Printing and Graphic Arts",
    
    # Health & Community
    "CHC": "Community Services",
    "HLT": "Health",
    
    # Business & Finance
    "BSB": "Business Services",
    "FNS": "Financial Services",
    "LGA": "Local Government",
    "PSP": "Public Sector",
    
    # Education & Training
    "TAE": "Training and Education",
    
    # Hospitality & Tourism
    "SIT": "Tourism, Travel and Hospitality",
    "SFL": "Floristry",
    
    # Creative Arts
    "CUA": "Creative Arts and Culture",
    "CUF": "Screen and Media",
    "CUS": "Sustainability",
    "CUV": "Visual Arts",
    "SHB": "Hairdressing and Beauty Services",
    
    # Public Safety & Security
    "CSC": "Correctional Services",
    "DEF": "Defence",
    "POL": "Police",
    "PUA": "Public Safety",
    
    # Resources & Utilities
    "DRG": "Drilling",
    "NWP": "Water",
    "RII": "Resources and Infrastructure Industry",
    "UEE": "Electrotechnology",
    "UEP": "Electricity Supply Industry - Generation Sector",
    "UET": "Transmission, Distribution and Rail Sector",
    
    # Science & Laboratory
    "MSL": "Laboratory Operations",
    "FBP": "Food, Beverage and Pharmaceutical",
    
    # Sport & Recreation
    "SIS": "Sport, Fitness and Recreation"
}


# ═══════════════════════════════════════════════════════════════════════════
#  COMPLEXITY LEVELS (5 levels - Enhanced with AQF & Bloom's Taxonomy)
# ═══════════════════════════════════════════════════════════════════════════

COMPLEXITY_LEVELS = {
    1: {
        "name": "Foundational",
        "description": "Basic awareness, recall of facts, fundamental tasks under close supervision",
        "bloom_taxonomy": "Remember/Understand",
        "dreyfus_model": "Novice",
        "aqf_level": "Certificate I",
        "vet_context": "Pre-vocational, basic orientation, introductory skills"
    },
    2: {
        "name": "Basic",
        "description": "Understanding and application of routine procedures with guidance",
        "bloom_taxonomy": "Understand/Apply",
        "dreyfus_model": "Advanced Beginner",
        "aqf_level": "Certificate II-III",
        "vet_context": "Routine work, supervised application, developing competence"
    },
    3: {
        "name": "Intermediate",
        "description": "Independent application, analysis, and adaptation of learned skills",
        "bloom_taxonomy": "Apply/Analyze",
        "dreyfus_model": "Competent",
        "aqf_level": "Certificate III-IV",
        "vet_context": "Skilled work, autonomous practice, trade qualification level"
    },
    4: {
        "name": "Advanced",
        "description": "Complex problem-solving, synthesis, evaluation in varied contexts",
        "bloom_taxonomy": "Analyze/Evaluate",
        "dreyfus_model": "Proficient",
        "aqf_level": "Diploma/Advanced Diploma",
        "vet_context": "Complex operations, supervision, para-professional work"
    },
    5: {
        "name": "Expert",
        "description": "Mastery, innovation, creation of new knowledge and strategic application",
        "bloom_taxonomy": "Evaluate/Create",
        "dreyfus_model": "Expert",
        "aqf_level": "Degree and above",
        "vet_context": "Specialist expertise, strategic thinking, innovation and leadership"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  TRANSFERABILITY TYPES (4 categories - O*NET & ASC aligned)
# ═══════════════════════════════════════════════════════════════════════════

TRANSFERABILITY_TYPES = {
    "universal": {
        "name": "Universal/Core Competencies",
        "score": 4,
        "description": "Foundational skills applicable across all occupations (ASC Core Competencies)",
        "examples": ["Communication", "Teamwork", "Problem Solving", "Learning Agility", "Digital Literacy", "Critical Thinking", "Time Management", "Adaptability", "Initiative", "Resilience"],
        "keywords": ["communication", "teamwork", "problem solving", "learning", "adaptability", "critical thinking", "time management", "ethics", "work ethic"]
    },
    "cross_sector": {
        "name": "Cross-Sector/Transferable",
        "score": 3,
        "description": "Specialist skills transferable across multiple industries and sectors",
        "examples": ["Project Management", "Customer Service", "Data Analysis", "Quality Assurance", "WHS", "Supervision", "Budgeting"],
        "keywords": ["project management", "customer service", "data analysis", "quality", "safety", "compliance", "budgeting", "supervision", "coordination"]
    },
    "sector_specific": {
        "name": "Sector-Specific",
        "score": 2,
        "description": "Skills relevant within a specific sector or closely related industries",
        "examples": ["Healthcare Protocols", "Construction Methods", "Manufacturing Processes", "Hospitality Standards", "Agricultural Techniques"],
        "keywords": ["industry practices", "sector standards", "domain methods", "sector protocols"]
    },
    "occupation_specific": {
        "name": "Occupation-Specific/Technical",
        "score": 1,
        "description": "Highly specialized skills unique to particular occupation or role",
        "examples": ["Welding Certification", "Dental Procedures", "Legal Drafting", "Aircraft Maintenance", "Specific Machinery Operation"],
        "keywords": ["technical", "specialized", "certification", "licensed", "regulated", "specific equipment"]
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  DIGITAL INTENSITY LEVELS (5 levels - 0-4 scale)
# ═══════════════════════════════════════════════════════════════════════════

DIGITAL_INTENSITY_LEVELS = {
    0: {
        "name": "No/Minimal Digital",
        "description": "Primarily manual/physical tasks with negligible digital tool usage",
        "examples": ["Manual labor", "Traditional crafts", "Physical caregiving", "Manual trades"],
        "percentage": "0-10% of work involves digital tools"
    },
    1: {
        "name": "Low Digital",
        "description": "Basic digital literacy, simple tool usage (email, basic software, POS)",
        "examples": ["Email communication", "Basic data entry", "POS systems", "Simple device operation"],
        "percentage": "11-30% of work involves digital tools"
    },
    2: {
        "name": "Medium Digital",
        "description": "Regular use of specialized software and digital platforms",
        "examples": ["Office productivity suites", "Industry-specific software", "Digital communication tools", "CAD"],
        "percentage": "31-60% of work involves digital tools"
    },
    3: {
        "name": "High Digital",
        "description": "Advanced digital skills, complex software, data manipulation, programming",
        "examples": ["Programming", "Data analytics", "Digital design", "System administration", "Database management"],
        "percentage": "61-85% of work involves digital tools"
    },
    4: {
        "name": "Advanced Digital/Tech-Native",
        "description": "Cutting-edge technology, AI/ML, automation, emerging tech, digital innovation",
        "examples": ["AI/ML development", "Cloud architecture", "Cybersecurity", "IoT", "Blockchain", "Quantum computing"],
        "percentage": "86-100% of work involves digital tools"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  FUTURE-READINESS CATEGORIES (4 categories - Labor Market aligned)
# ═══════════════════════════════════════════════════════════════════════════

FUTURE_READINESS = {
    "declining": {
        "name": "Declining Demand",
        "score": 1,
        "description": "Skills being automated, phased out, or experiencing decreased labor market demand",
        "drivers": ["Automation", "Technological displacement", "Industry decline", "Process optimization"],
        "keywords": ["manual data entry", "routine clerical", "basic bookkeeping", "repetitive tasks", "manual assembly"],
        "trend": "↓ Decreasing"
    },
    "stable": {
        "name": "Stable Demand",
        "score": 2,
        "description": "Consistent demand with minimal change expected in medium term",
        "drivers": ["Ongoing essential services", "Mature industries", "Regulated professions"],
        "keywords": ["core trades", "essential services", "foundational skills", "licensed trades"],
        "trend": "→ Steady"
    },
    "growing": {
        "name": "Growing Demand",
        "score": 3,
        "description": "Increasing importance and labor market demand driven by economic/social trends",
        "drivers": ["Population growth", "Demographic shifts", "Service economy expansion", "Technology adoption"],
        "keywords": ["digital skills", "healthcare", "data analysis", "sustainability", "aged care", "NDIS", "customer experience"],
        "trend": "↑ Increasing"
    },
    "transformative": {
        "name": "Transformative/Emerging",
        "score": 4,
        "description": "Critical for future economy, rapidly evolving, high-growth sectors",
        "drivers": ["Digital transformation", "Climate change", "Innovation economy", "Emerging technologies"],
        "keywords": ["AI", "machine learning", "renewable energy", "cybersecurity", "biotechnology", "quantum computing", "green skills", "circular economy"],
        "trend": "↑↑ Exponential"
    }
}


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL NATURE TYPES (5 types - O*NET & BLS aligned)
# ═══════════════════════════════════════════════════════════════════════════

SKILL_NATURE_TYPES = {
    "content": {
        "name": "Content/Knowledge Skills",
        "description": "Background knowledge, domain expertise, and specialized understanding",
        "o_net_category": "Content",
        "examples": ["Mathematics", "Science", "Language", "Domain knowledge", "Technical knowledge"],
        "characteristics": ["Learned", "Declarative", "Domain-specific"]
    },
    "process": {
        "name": "Process/Cognitive Skills",
        "description": "Information processing, cognitive operations, thinking skills",
        "o_net_category": "Process",
        "examples": ["Critical thinking", "Active learning", "Monitoring", "Active listening"],
        "characteristics": ["Thinking", "Processing", "Analyzing"]
    },
    "social": {
        "name": "Social/Interpersonal Skills",
        "description": "Interpersonal interaction, collaboration, and relationship management",
        "o_net_category": "Social",
        "examples": ["Service orientation", "Persuasion", "Coordination", "Negotiation", "Instructing"],
        "characteristics": ["Interactive", "Relational", "Collaborative"]
    },
    "technical": {
        "name": "Technical/Practical Skills",
        "description": "Equipment operation, tool usage, hands-on technical abilities",
        "o_net_category": "Technical",
        "examples": ["Equipment operation", "Technology design", "Programming", "Quality control"],
        "characteristics": ["Procedural", "Manual", "Applied"]
    },
    "resource": {
        "name": "Resource Management Skills",
        "description": "Allocation and management of time, finances, materials, and personnel",
        "o_net_category": "Resource Management",
        "examples": ["Time management", "Financial resources", "Material resources", "Personnel management"],
        "characteristics": ["Organizing", "Planning", "Allocating"]
    }
}

CONTEXT_TYPES = {
    "theoretical": {
        "name": "Theoretical/Academic",
        "description": "Primarily conceptual learning in classroom/academic settings",
        "learning_environment": "Classroom, lecture, online learning",
        "examples": ["Theory courses", "Academic study", "Conceptual frameworks"]
    },
    "practical": {
        "name": "Practical/Applied",
        "description": "Hands-on application in workshops, labs, or simulated environments",
        "learning_environment": "Workshop, laboratory, training facility",
        "examples": ["Trade skills", "Laboratory work", "Practical demonstrations"]
    },
    "workplace": {
        "name": "Workplace/On-the-Job",
        "description": "Skills applied directly in real workplace settings",
        "learning_environment": "Actual workplace, apprenticeship, traineeship",
        "examples": ["Apprenticeships", "Work placements", "On-the-job training"]
    },
    "hybrid": {
        "name": "Hybrid/Blended",
        "description": "Combination of theoretical knowledge and practical application",
        "learning_environment": "Mixed classroom and workshop/workplace",
        "examples": ["VET qualifications", "Dual-sector programs", "Work-integrated learning"]
    },
    "digital": {
        "name": "Digital/Virtual",
        "description": "Primarily delivered through digital platforms and virtual environments",
        "learning_environment": "Online, virtual reality, simulation software",
        "examples": ["E-learning", "Virtual simulations", "Remote collaboration"]
    }
}

# ============================================================================
# MULTI-FACTOR MATCHING CONFIGURATION
# ============================================================================
# These weights are used throughout the pipeline for skill similarity calculation
# They should sum to 1.0 when normalized

MULTI_FACTOR_WEIGHTS = {
    "semantic_weight": float(os.environ.get("SEMANTIC_WEIGHT", "0.60")),  # Weight for text similarity
    "level_weight": float(os.environ.get("LEVEL_WEIGHT", "0.25")),      # Weight for skill level compatibility
    "context_weight": float(os.environ.get("CONTEXT_WEIGHT", "0.15")),   # Weight for context (practical/theoretical)
}

# Thresholds for different match types
MATCH_THRESHOLDS = {
    "direct_match_threshold": float(os.environ.get("DIRECT_MATCH_THRESHOLD", "0.90")),  # Direct/exact match
    "partial_threshold": float(os.environ.get("PARTIAL_THRESHOLD", "0.80")),           # Partial match
    "minimum_threshold": float(os.environ.get("MINIMUM_THRESHOLD", "0.65")),          # Minimum for consideration
}

# Level compatibility configuration
LEVEL_COMPATIBILITY = {
    "max_level_difference_for_dedup": 1,     # Max level difference to consider skills as duplicates
    "level_penalty_factor": 0.2,             # Penalty per level difference
    "prefer_higher_levels": True,            # Prefer higher level skills as masters in deduplication
}

# Context compatibility configuration
CONTEXT_COMPATIBILITY = {
    "practical_practical": 1.0,
    "practical_hybrid": 0.7,
    "practical_theoretical": 0.3,
    "theoretical_theoretical": 1.0,
    "theoretical_hybrid": 0.7,
    "theoretical_practical": 0.3,
    "hybrid_practical": 0.7,
    "hybrid_theoretical": 0.7,
    "hybrid_hybrid": 1.0,
}

# ============================================================================
# DATA PROCESSING SETTINGS
# ============================================================================

DATA_CONFIG = {
    "confidence_threshold": 0.7,  # Minimum confidence for including skills
    "min_skill_length": 3,        # Minimum character length for skill names
    "max_skill_length": 200,      # Maximum character length for skill names
    "batch_size": 1000,           # Batch size for processing
    "n_jobs": -1,                 # Number of parallel jobs (-1 for all CPUs)
}

# ============================================================================
# EMBEDDING SETTINGS
# ============================================================================

EMBEDDING_CONFIG = {
    # "model_name": "sentence-transformers--all-mpnet-base-v2",
    # "model_name": "sentence-transformers--all-MiniLM-L6-v2",
    "model_name": "jinaai--jina-embeddings-v4",
    "batch_size": 8,
    "cache_embeddings": True,
    "normalize_embeddings": True,
    "device": "cuda" if os.environ.get("CUDA_AVAILABLE") else "cpu",
    "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
    "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
    # Similarity method selection
    "similarity_method": os.environ.get("SIMILARITY_METHOD", "faiss"),  # 'faiss' or 'matrix'
    
    # Matrix-specific settings
    "matrix_memory_threshold": 10000,  # Max samples for full matrix computation
    
    # FAISS-specific settings
    "faiss_exact_search_threshold": 5000,  # Use exact search if fewer samples
    
    # Multi-factor weights (reference to global config)
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# DEDUPLICATION SETTINGS
# ============================================================================

DEDUP_CONFIG = {
    "similarity_threshold": MATCH_THRESHOLDS["partial_threshold"],  # Base threshold
    
    # Match type thresholds
    **MATCH_THRESHOLDS,
    
    # FAISS settings
    "use_faiss": True,
    "faiss_index_type": "IVF1024,Flat",
    "nprobe": 64,
    
    # General settings
    "fuzzy_ratio_threshold": 90,
    
    # Level and context settings
    **LEVEL_COMPATIBILITY,
    
    # Multi-factor weights
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# CLUSTERING SETTINGS
# ============================================================================

CLUSTERING_CONFIG = {
    "algorithm": "hdbscan",
    "min_cluster_size": 10,
    "min_samples": 5,
    "metric": "euclidean",
    "cluster_selection_epsilon": 0.0,
    "alpha": 1.0,
    "use_umap_reduction": True,
    "umap_n_components": 50,
    "umap_n_neighbors": 30,
    "umap_min_dist": 0.0,
    
    # Multi-factor clustering
    "use_multi_factor_clustering": True,
    "cluster_coherence_threshold": 0.7,  # Minimum coherence for valid clusters
    "split_high_variance_clusters": True,  # Split clusters with high level variance
    "merge_small_clusters": True,         # Merge very small clusters
    
    # Multi-factor weights
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# HIERARCHY SETTINGS
# ============================================================================

HIERARCHY_CONFIG = {
    # Structure parameters
    "max_children": 25,  # Maximum direct children per node
    "min_children": 2,   # Minimum children to create a node
    "max_depth": 5,      # Maximum depth: Root=0, Domain=1, Family=2, Cluster=3, Group=4, Skills=5
    
    # Balancing and organization
    "balance_threshold": 0.3,
    "max_level_span_per_node": 2,  # Maximum complexity level range within group
    
    # Multi-dimensional classification
    "enable_cross_cutting_dimensions": True,
    "enable_transferability_scoring": True,
    "enable_digital_intensity_scoring": True,
    "enable_future_readiness_scoring": True,
    "enable_skill_nature_classification": True,
    "enable_context_classification": True,
    
    # Relationships & connections
    "build_skill_relationships": True,
    "max_related_skills": 10,
    "relationship_similarity_threshold": 0.75,
    
    # VET-specific enrichment
    "include_training_package_alignment": True,  # Align with Australian Training Packages
    "include_qualification_mapping": True,       # Map to AQF levels & qualifications
    "include_unit_of_competency_links": True,    # Link to units of competency
    "include_industry_sector_codes": True,       # Align with ANZSIC codes
    "include_occupation_codes": True,            # Align with ANZSCO/OSCA codes
    
    # Advanced features
    "enable_skill_pathways": True,               # Show progression pathways
    "enable_prerequisite_mapping": True,         # Map prerequisite relationships
    "enable_licensing_requirements": True        # Flag licensed/regulated skills
}


# ═══════════════════════════════════════════════════════════════════════════
#  VALIDATION CONFIGURATION (Enhanced quality thresholds)
# ═══════════════════════════════════════════════════════════════════════════

VALIDATION_CONFIG = {
    # Coverage thresholds
    "min_coverage": 0.85,  # Minimum 85% of skills in taxonomy
    "target_coverage": 0.95,  # Target 95%
    
    # Quality metrics
    "min_cluster_coherence": 0.65,
    "target_cluster_coherence": 0.80,
    
    # Structure validation
    "expected_depth_range": (4, 5),
    "min_balance_score": 0.45,
    "expected_domains": 14,
    "expected_families_range": (75, 95),
    
    # Dimension completeness
    "require_all_dimensions": True,
    "validate_complexity_distribution": True,
    "validate_transferability_variety": True,
    "validate_digital_intensity_range": True,
    "validate_future_readiness_distribution": True,
    
    # VET-specific validation
    "validate_training_package_coverage": True,
    "validate_aqf_alignment": True,
    "min_skills_per_family": 5,
    "max_skills_per_family": 5000,
    
    # Relationship validation
    "min_avg_relationships": 1.5,
    "max_isolated_skills_percent": 10,
    
    # to be deleted
    "coverage_threshold": 0.95,
    "coherence_threshold": 0.7,
    "distinctiveness_threshold": 0.5,
    "max_orphan_skills": 100,
    "validate_with_llm": True,
    "check_level_consistency": True,
    "check_context_alignment": True,
    "minimum_cluster_coherence": 0.6,
    
    # NEW: Multi-dimensional validation
    "validate_domain_assignment": True,
    "validate_transferability_scores": True,
    "validate_skill_relationships": True,
    "min_skills_per_family": 5,
}


# ============================================================================
# SKILL EXTRACTION SETTINGS (if using with models from attached code)
# ============================================================================

SKILL_EXTRACTION_CONFIG = {
    "use_multi_factor_extraction": True,
    "extract_skill_levels": True,
    "extract_skill_context": True,
    "confidence_threshold": 0.6,
    
    # Level detection keywords
    "level_keywords": {
        "follow": ["basic", "introductory", "fundamental", "beginning"],
        "assist": ["support", "help", "aid", "contribute"],
        "apply": ["implement", "use", "perform", "execute"],
        "enable": ["facilitate", "coordinate", "manage", "lead"],
        "ensure_advise": ["ensure", "advise", "consult", "recommend"],
        "initiate_influence": ["initiate", "influence", "drive", "champion"],
        "set_strategy": ["strategy", "vision", "direction", "transform"]
    },
    
    # Context detection keywords
    "context_keywords": {
        "practical": ["hands-on", "laboratory", "workshop", "applied", "project"],
        "theoretical": ["theory", "concept", "principle", "framework", "model"],
        "hybrid": ["combined", "integrated", "both", "mixed"]
    }
}

# ============================================================================
# LLM SETTINGS (if using Azure OpenAI)
# ============================================================================
LLM_CONFIG = {
    "openai": {
        "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
        "azure_endpoint": os.environ.get("ENDPOINT_URL"),
        "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
        "deployment_name": os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
        "timeout": 60,
        "max_tokens": 4000,
        "temperature": 0.0,
        "rate_limit_delay": 1.0
    },
    "vllm": {
        "model_name": os.getenv("VLLM_MODEL_NAME", "gpt-oss-120b"),
        "num_gpus": int(os.getenv("VLLM_NUM_GPUS", "1")),
        "max_model_len": int(os.getenv("VLLM_MAX_MODEL_LEN", "10240")),
        "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
        "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
        "tensor_parallel_size": 1,
        "gpu_memory_utilization": 0.9
    }
}
# LLM_CONFIG = {
#     "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
#     "azure_endpoint": os.environ.get("ENDPOINT_URL"),
#     "api_version": os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
#     "deployment_name": os.environ.get("DEPLOYMENT_NAME", "gpt-4"),
    

#     "temperature": 0.0,
#     "max_tokens": 500,
#     "retry_attempts": 3,
#     "batch_size": 20,
#     "cache_responses": True,
#     "backed_type": "azure_openai"  # 'azure_openai' or 'vllm'
# }

# ============================================================================
# CATEGORY HIERARCHY (with expected levels)
# ============================================================================

CATEGORY_HIERARCHY = {
    "technical": {
        "parent": "Hard Skills",
        "expected_level_range": (2, 5),  # SFIA levels 2-5
        "subcategories": [
            "Engineering & Technology",
            "Information Technology",
            "Manufacturing & Production",
            "Quality & Testing",
            "Research & Development"
        ]
    },
    "cognitive": {
        "parent": "Cognitive Skills",
        "expected_level_range": (3, 6),  # SFIA levels 3-6
        "subcategories": [
            "Problem Solving",
            "Critical Thinking",
            "Decision Making",
            "Analytical Skills",
            "Creative Thinking"
        ]
    },
    "interpersonal": {
        "parent": "Soft Skills",
        "expected_level_range": (2, 5),  # SFIA levels 2-5
        "subcategories": [
            "Communication",
            "Leadership",
            "Teamwork",
            "Customer Service",
            "Conflict Resolution"
        ]
    },
    "domain_knowledge": {
        "parent": "Domain Expertise",
        "expected_level_range": (3, 7),  # SFIA levels 3-7
        "subcategories": [
            "Industry Knowledge",
            "Regulatory Compliance",
            "Business Acumen",
            "Subject Matter Expertise",
            "Market Knowledge"
        ]
    }
}

# Model configurations
EMBEDDING_MODELS = {
    "jinaai--jina-embeddings-v4": {
        "model_id": "jinaai/jina-embeddings-v4",
        "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
        "trust_remote_code": True,
        "embedding_dim": 2048
    },
    "google--embeddinggemma-300m": {
        "model_id": "google/embeddinggemma-300m",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 768
    },
    "Qwen--Qwen3-Embedding-0.6B": {
        "model_id": "Qwen/Qwen3-Embedding-0.6B",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 1024
    },
    "BAAI--bge-base-en-v1.5": {
        "model_id": "BAAI/bge-base-en-v1.5",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 768
    },
    "sentence-transformers--all-MiniLM-L6-v2": {
        "model_id": "sentence-transformers/all-MiniLM-L6-v2",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 384
    },
    "sentence-transformers--all-mpnet-base-v2": {
        "model_id": "sentence-transformers/all-mpnet-base-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 768
    },
    "intfloat--e5-large-v2": {
        "model_id": "intfloat/e5-large-v2",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 1024
    },
    "WhereIsAI--UAE-Large-V1": {
        "model_id": "WhereIsAI/UAE-Large-V1",
        "revision": None,
        "trust_remote_code": False,
        "embedding_dim": 1024
    }
}

# Model configurations
MODELS = {
    "mistralai--Mistral-7B-Instruct-v0.2": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.2",
        "revision": "41b61a33a2483885c981aa79e0df6b32407ed873",
        "template": "Mistral"
    },
    "mistralai--Mistral-7B-Instruct-v0.3": {
        "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
        "revision": "e0bc86c23ce5aae1db576c8cca6f06f1f73af2db",
        "template": "Mistral"
    },
    "neuralmagic--Meta-Llama-3.1-70B-Instruct-quantized.w4a16": {
        "model_id": "neuralmagic/Meta-Llama-3.1-70B-Instruct-quantized.w4a16",
        "revision": "8c670bcdb23f58a977e1440354beb7c3e455961d",
        "template": "Llama"
    },
    "meta-llama--Llama-3.1-8B-Instruct": {
        "model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "revision": "0e9e39f249a16976918f6564b8830bc894c89659",
        "template": "Llama"
    },
    "neuralmagic--Meta-Llama-3.1-70B-Instruct-FP8": {
        "model_id": "neuralmagic/Meta-Llama-3.1-70B-Instruct-FP8",
        "revision": "08b31c0f951f2227f6cdbc088cdb6fd139aecf0f",
        "template": "Llama"
    },
    "microsoft--Phi-4-mini-instruct": {
        "model_id": "microsoft/Phi-4-mini-instruct",
        "revision": "c0fb9e74abda11b496b7907a9c6c9009a7a0488f",
        "template": "Phi"
    },
    "cortecs--Llama-3.3-70B-Instruct-FP8-Dynamic": {
        "model_id": "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic",
        "revision": "3722358cc2b990b22304489b2f87ef3bb876d6f6",
        "template": "Llama"
    },
    "gpt-oss-120b": {
        "model_id": "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models/gpt-oss-120b",
        "revision": None,
        "template": "GPT"
    },
    "gpt-oss-20b": {
        "model_id": "unsloth/gpt-oss-20b-unsloth-bnb-4bit",
        "revision": None,
        "template": "GPT"
    }
}

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

CONFIG: Dict[str, Any] = {
    "backed_type": "openai",
    "data": DATA_CONFIG,
    "embedding": EMBEDDING_CONFIG,
    "dedup": DEDUP_CONFIG,
    "clustering": CLUSTERING_CONFIG,
    "hierarchy": HIERARCHY_CONFIG,
    "validation": VALIDATION_CONFIG,
    "categories": CATEGORY_HIERARCHY,
    "extraction": SKILL_EXTRACTION_CONFIG,
    "llm": LLM_CONFIG,
    "multi_factor": {
        "weights": MULTI_FACTOR_WEIGHTS,
        "thresholds": MATCH_THRESHOLDS,
        "level_compatibility": LEVEL_COMPATIBILITY,
        "context_compatibility": CONTEXT_COMPATIBILITY,
    },
    # NEW: Multi-dimensional taxonomy config
    "taxonomy": {
        "domains": SKILL_DOMAINS,
        "families": SKILL_FAMILIES,
        "complexity_levels": COMPLEXITY_LEVELS,
        "transferability": TRANSFERABILITY_TYPES,
        "digital_intensity": DIGITAL_INTENSITY_LEVELS,
        "future_readiness": FUTURE_READINESS,
        "skill_nature": SKILL_NATURE_TYPES,
    },
    "paths": {
        "project_root": str(PROJECT_ROOT),
        "data_dir": str(DATA_DIR),
        "output_dir": str(OUTPUT_DIR),
        "cache_dir": str(CACHE_DIR),
    },
    "models": {
        "embedding_models": EMBEDDING_MODELS,
        "llm_models": MODELS,
    }
}

# ============================================================================
# CONFIGURATION PROFILES (Quick presets)
# ============================================================================

def get_config_profile(profile: str = "balanced") -> Dict[str, Any]:
    """
    Get a pre-configured profile with different weight balances
    
    Profiles:
    - semantic_focused: Emphasizes text similarity (0.8, 0.1, 0.1)
    - level_aware: Balances semantic and level (0.5, 0.35, 0.15)
    - balanced: Equal consideration (0.6, 0.25, 0.15)
    - context_sensitive: Includes context heavily (0.5, 0.2, 0.3)
    """
    profiles = {
        "semantic_focused": {
            "semantic_weight": 0.80,
            "level_weight": 0.10,
            "context_weight": 0.10,
            "direct_match_threshold": 0.85,
            "partial_threshold": 0.75,
        },
        "level_aware": {
            "semantic_weight": 0.50,
            "level_weight": 0.35,
            "context_weight": 0.15,
            "direct_match_threshold": 0.88,
            "partial_threshold": 0.78,
        },
        "balanced": {
            "semantic_weight": 0.80,
            "level_weight": 0.10,
            "context_weight": 0.10,
            "direct_match_threshold": 0.90,
            "partial_threshold": 0.80,
        },
        "context_sensitive": {
            "semantic_weight": 0.50,
            "level_weight": 0.20,
            "context_weight": 0.30,
            "direct_match_threshold": 0.92,
            "partial_threshold": 0.82,
        }
    }
    
    profile_config = CONFIG.copy()
    
    if profile in profiles:
        weights = profiles[profile]
        # Update all relevant sections
        for key in ["embedding", "dedup", "clustering"]:
            profile_config[key].update(weights)
        profile_config["multi_factor"]["weights"].update(weights)
        profile_config["multi_factor"]["thresholds"].update(weights)
    
    return profile_config

# ============================================================================
# LOGGING
# ============================================================================

import logging

logger = logging.getLogger(__name__)
logger.info("=" * 60)
logger.info("MULTI-FACTOR SKILL MATCHING CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Semantic Weight: {MULTI_FACTOR_WEIGHTS['semantic_weight']:.2f}")
logger.info(f"Level Weight: {MULTI_FACTOR_WEIGHTS['level_weight']:.2f}")
logger.info(f"Context Weight: {MULTI_FACTOR_WEIGHTS['context_weight']:.2f}")
logger.info(f"Direct Match Threshold: {MATCH_THRESHOLDS['direct_match_threshold']:.2f}")
logger.info(f"Partial Match Threshold: {MATCH_THRESHOLDS['partial_threshold']:.2f}")
logger.info(f"Taxonomy Structure: 5-Level Hierarchy")
logger.info(f"Skill Domains: {len(SKILL_DOMAINS)}")
logger.info(f"Skill Families: {len(SKILL_FAMILIES)}")
logger.info(f"Cross-Cutting Dimensions: 6 (Complexity, Transferability, Digital Intensity, etc.)")
logger.info("=" * 60)
logger.info(f"Config: {CONFIG}")
logger.info("=" * 60)
