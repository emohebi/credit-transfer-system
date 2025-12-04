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
    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTHCARE & COMMUNITY (Split from original combined domain)
    # ═══════════════════════════════════════════════════════════════════════════
    "healthcare_clinical": {
        "name": "Healthcare & Allied Health",
        "description": "Clinical healthcare, nursing specialties, allied health professions, dental, pharmacy, and medical support services",
        "training_package": "HLT - Health"
    },
    "community_services": {
        "name": "Community, Disability & Social Services",
        "description": "Disability support, aged care support, community services, child protection, youth work, and mental health support",
        "training_package": "CHC - Community Services"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTION & ELECTRICAL (Split from original combined domain)
    # ═══════════════════════════════════════════════════════════════════════════
    "construction_building": {
        "name": "Construction & Building Trades",
        "description": "Carpentry, bricklaying, plastering, painting, tiling, roofing, plumbing, glazing, and general construction",
        "training_package": "CPC - Construction, Plumbing and Services"
    },
    "electrical_communications": {
        "name": "Electrical & Communications Trades",
        "description": "Electrical installation, data cabling, solar PV, air conditioning, refrigeration, and communications infrastructure",
        "training_package": "UEE - Electrotechnology"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BUSINESS & FINANCE (Split from original combined domain)
    # ═══════════════════════════════════════════════════════════════════════════
    "finance_accounting": {
        "name": "Finance, Accounting & Banking",
        "description": "Accounting, bookkeeping, payroll, taxation, financial planning, banking, insurance, and lending",
        "training_package": "FNS - Financial Services"
    },
    "business_administration": {
        "name": "Business Services & Administration",
        "description": "Office administration, HR, marketing, project management, legal support, and business operations",
        "training_package": "BSB - Business Services"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTOMOTIVE & TRANSPORT (Split from original combined domain)
    # ═══════════════════════════════════════════════════════════════════════════
    "automotive_repair": {
        "name": "Automotive Service & Repair",
        "description": "Light vehicle, heavy vehicle, motorcycle, and marine mechanical repair, auto electrical, and body repair",
        "training_package": "AUR - Automotive"
    },
    "transport_logistics": {
        "name": "Transport, Logistics & Warehousing",
        "description": "Driving, warehousing, freight forwarding, supply chain, maritime, rail, and aviation ground operations",
        "training_package": "TLI - Transport and Logistics"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PRIMARY INDUSTRIES
    # ═══════════════════════════════════════════════════════════════════════════
    "agriculture_primary": {
        "name": "Agriculture, Horticulture & Primary Industries",
        "description": "Farming, livestock, horticulture, aquaculture, forestry, conservation, and meat processing",
        "training_package": "AHC - Agriculture, Horticulture and Conservation"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CREATIVE & DIGITAL
    # ═══════════════════════════════════════════════════════════════════════════
    "creative_arts": {
        "name": "Creative Arts, Culture & Entertainment",
        "description": "Visual arts, design, performing arts, music, film/TV production, and media",
        "training_package": "CUA - Creative Arts and Culture"
    },
    "digital_technology": {
        "name": "Digital Technology & ICT",
        "description": "Software development, IT operations, data analytics, cybersecurity, cloud, and digital design",
        "training_package": "ICT - Information and Communications Technology"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EDUCATION & TRAINING
    # ═══════════════════════════════════════════════════════════════════════════
    "education_training": {
        "name": "Education, Training & Development",
        "description": "Early childhood, school education, VET, training, and educational support",
        "training_package": "TAE - Training and Education"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HOSPITALITY & TOURISM
    # ═══════════════════════════════════════════════════════════════════════════
    "hospitality_tourism": {
        "name": "Hospitality, Tourism & Events",
        "description": "Commercial cookery, food service, accommodation, tourism, and events",
        "training_package": "SIT - Tourism, Travel and Hospitality"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MANUFACTURING & ENGINEERING
    # ═══════════════════════════════════════════════════════════════════════════
    "manufacturing_engineering": {
        "name": "Manufacturing, Engineering & Production",
        "description": "Machining, welding, fitting, maintenance, production, and food/beverage manufacturing",
        "training_package": "MEM - Manufacturing and Engineering"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC SAFETY & SECURITY
    # ═══════════════════════════════════════════════════════════════════════════
    "public_safety": {
        "name": "Public Safety, Security & Defence",
        "description": "Security, emergency services, firefighting, corrections, and defence",
        "training_package": "CPP - Property Services / DEF - Defence"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RETAIL & PERSONAL SERVICES
    # ═══════════════════════════════════════════════════════════════════════════
    "retail_services": {
        "name": "Retail, Sales & Personal Services",
        "description": "Retail sales, hairdressing, beauty therapy, and personal services",
        "training_package": "SIR - Retail Services / SHB - Hairdressing and Beauty"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SCIENCE & LABORATORY
    # ═══════════════════════════════════════════════════════════════════════════
    "science_technical": {
        "name": "Science, Laboratory & Technical Services",
        "description": "Laboratory analysis, research, pharmaceutical, environmental, and forensic services",
        "training_package": "MSL - Laboratory Operations"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SPORT & RECREATION
    # ═══════════════════════════════════════════════════════════════════════════
    "sport_recreation": {
        "name": "Sport, Fitness & Recreation",
        "description": "Personal training, group fitness, sports coaching, aquatics, and outdoor recreation",
        "training_package": "SIS - Sport, Fitness and Recreation"
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITIES & RESOURCES
    # ═══════════════════════════════════════════════════════════════════════════
    "utilities_resources": {
        "name": "Utilities, Resources & Infrastructure",
        "description": "Electricity, gas, water, telecommunications, mining, civil construction, and renewable energy",
        "training_package": "UET - Transmission, Distribution and Rail / RII - Resources and Infrastructure"
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  SKILL FAMILIES - 90+ Detailed Classifications with Full Descriptions
# ═══════════════════════════════════════════════════════════════════════════



# ============================================================================
# GRANULAR SKILL FAMILIES (551 families for precise embedding matching)
# ============================================================================
SKILL_FAMILIES = {
    # ═══════════════════════════════════════════════════════════════════════════
    # AGRICULTURE, HORTICULTURE & PRIMARY INDUSTRIES (45 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Crop & Broadacre Farming
    "grain_cropping": {
        "name": "Broadacre Cropping",
        "domain": "agriculture_primary",
        "description": "Growing and harvesting grain crops including wheat, barley, oats, and canola",
        "keywords": ["grain", "wheat", "barley", "oats", "canola", "cropping", "broadacre", "harvest", "header", "grain storage", "silo"]
    },
    "cotton_farming": {
        "name": "Cotton Cropping",
        "domain": "agriculture_primary",
        "description": "Cotton cultivation, irrigation, and harvesting operations",
        "keywords": ["cotton", "cotton picking", "cotton ginning", "cotton farming", "cotton irrigation", "cotton harvest"]
    },
    "sugar_cane": {
        "name": "Sugar Cane Production",
        "domain": "agriculture_primary",
        "description": "Sugar cane cultivation, harvesting, and milling operations",
        "keywords": ["sugar cane", "cane harvesting", "cane farming", "sugar milling", "cane planting", "bagasse"]
    },
    "vegetable_production": {
        "name": "Vegetable Production",
        "domain": "agriculture_primary",
        "description": "Commercial vegetable growing, harvesting, and packing",
        "keywords": ["vegetable", "vegetables", "market garden", "vegetable growing", "vegetable harvest", "tomato", "lettuce", "capsicum", "brassica"]
    },
    "fruit_orchard": {
        "name": "Orchard Production",
        "domain": "agriculture_primary",
        "description": "Fruit tree cultivation, pruning, and fruit harvesting",
        "keywords": ["orchard", "fruit", "fruit picking", "apple", "citrus", "stone fruit", "pruning", "thinning", "fruit packing", "avocado", "mango"]
    },
    "nut_production": {
        "name": "Nut Production",
        "domain": "agriculture_primary",
        "description": "Nut tree cultivation and nut harvesting operations",
        "keywords": ["nut", "almond", "macadamia", "walnut", "nut harvesting", "nut processing", "nut orchard"]
    },
    
    # Viticulture & Wine
    "vineyard_management": {
        "name": "Viticulture Management",
        "domain": "agriculture_primary",
        "description": "Grape vine cultivation, pruning, and vineyard operations",
        "keywords": ["vineyard", "viticulture", "grape", "vine pruning", "vine training", "grape harvest", "vintage", "canopy management"]
    },
    "winemaking": {
        "name": "Winemaking Cellar Operations",
        "domain": "agriculture_primary",
        "description": "Wine production, fermentation, and cellar management",
        "keywords": ["winemaking", "wine", "cellar", "fermentation", "wine barrel", "wine bottling", "oenology", "wine tasting", "wine blending"]
    },
    
    # Livestock
    "cattle_beef": {
        "name": "Beef Cattle Production",
        "domain": "agriculture_primary",
        "description": "Managing beef cattle including breeding, calving, calf marking, weaning, mustering, and feedlot operations on pastoral properties.",
        "keywords": ['beef cattle', 'cattle', 'beef', 'mustering', 'cattle yard', 'feedlot', 'calving', 'calf', 'weaning', 'cattle breeding', 'branding', 'cow-calf']
    },
    "dairy_farming": {
        "name": "Dairy Farming",
        "domain": "agriculture_primary",
        "description": "Managing dairy cattle including breeding, calving, calf rearing, milking, herd health, and dairy operations.",
        "keywords": ['dairy', 'dairy farming', 'milking', 'dairy cattle', 'dairy herd', 'calving', 'calf rearing', 'heifer', 'lactation', 'dairy breeding']
    },
    "sheep_wool": {
        "name": "Sheep Wool Production",
        "domain": "agriculture_primary",
        "description": "Managing sheep flocks including breeding, lambing, lamb marking, weaning, shearing, and wool production on pastoral properties.",
        "keywords": ['sheep', 'wool', 'shearing', 'lamb', 'lambing', 'flock', 'ewe', 'ram', 'sheep breeding', 'lamb marking', 'weaning lambs', 'crutching']
    },
    "pig_farming": {
        "name": "Pig Production",
        "domain": "agriculture_primary",
        "description": "Managing pig production including breeding programs, farrowing, sow and piglet care, piglet fostering, sow-piglet bonding, weaning, growing, and finishing pigs in production systems.",
        "keywords": ['pig', 'pork', 'piggery', 'farrowing', 'pig farming', 'swine', 'sow', 'piglet', 'piglet fostering', 'sow bonding', 'pig breeding', 'weaning pigs', 'litter management']
    },
    "poultry_eggs": {
        "name": "Poultry Production",
        "domain": "agriculture_primary",
        "description": "Managing poultry production including breeding, hatching, chick rearing, broiler growing, layer management, and egg production.",
        "keywords": ['poultry', 'chicken', 'eggs', 'egg production', 'broiler', 'layer', 'hatchery', 'chick', 'hatching', 'poultry breeding', 'pullet', 'hen']
    },
    "goat_farming": {
        "name": "Goat Production",
        "domain": "agriculture_primary",
        "description": "Managing goat herds including breeding, kidding, kid rearing, meat production, dairy goats, or fibre production.",
        "keywords": ['goat', 'goat farming', 'kidding', 'goat breeding', 'dairy goat', 'meat goat', 'fibre goat', 'kid rearing', 'doe', 'buck', 'goat husbandry']
    },
    
    # Horticulture
    "nursery_propagation": {
        "name": "Plant Propagation",
        "domain": "agriculture_primary",
        "description": "Plant propagation, nursery production, and seedling growing",
        "keywords": ["nursery", "propagation", "seedling", "cutting", "grafting", "potting", "plant nursery", "tissue culture", "germination"]
    },
    "turf_management": {
        "name": "Turf Management",
        "domain": "agriculture_primary",
        "description": "Turf installation, sports turf maintenance, and lawn care",
        "keywords": ["turf", "turf management", "lawn", "sports turf", "green keeping", "turf installation", "mowing", "aeration", "golf course", "oval"]
    },
    "landscape_construction": {
        "name": "Landscape Construction",
        "domain": "agriculture_primary",
        "description": "Constructing landscape elements including retaining walls, paths, and garden structures.",
        "keywords": ["landscape construction", "landscaping", "paving", "retaining wall", "garden construction", "landscape installation", "hardscape"]
    },
    "garden_maintenance": {
        "name": "Grounds Maintenance",
        "domain": "agriculture_primary",
        "description": "Maintaining gardens and grounds including mowing, pruning, weeding, planting, and general horticultural upkeep",
        "keywords": ["garden maintenance", "grounds maintenance", "pruning", "hedge trimming", "weeding", "mulching", "garden care", "groundskeeper"]
    },
    "arboriculture": {
        "name": "Arboriculture Tree Care",
        "domain": "agriculture_primary",
        "description": "Caring for trees including pruning, tree removal, climbing, stump grinding, and arboricultural assessment",
        "keywords": ["arboriculture", "tree surgery", "tree climbing", "tree removal", "tree pruning", "arborist", "chainsaw", "tree felling", "stump grinding"]
    },
    "irrigation_systems": {
        "name": "Irrigation Installation",
        "domain": "agriculture_primary",
        "description": "Designing and installing irrigation systems including drip, sprinkler, and pivot systems for agriculture and landscapes",
        "keywords": ["irrigation", "irrigation system", "drip irrigation", "sprinkler", "irrigation installation", "fertigation", "irrigation controller", "reticulation"]
    },
    
    # Animal Care
    "veterinary_nursing": {
        "name": "Veterinary Nursing",
        "domain": "agriculture_primary",
        "description": "Providing veterinary nursing care for animals in veterinary clinics including clinical procedures, animal anaesthesia, post-operative animal care, and animal hospital support.",
        "keywords": ['veterinary nursing', 'vet nurse', 'animal nursing', 'veterinary assistant', 'animal clinic', 'animal anaesthesia', 'animal hospital', 'veterinary care', 'animal recovery']
    },
    "dog_grooming": {
        "name": "Pet Grooming",
        "domain": "agriculture_primary",
        "description": "Grooming dogs and pets including washing, clipping, styling, nail trimming, coat care, and breed-specific grooming in salons or mobile services.",
        "keywords": ['dog grooming', 'pet grooming', 'dog washing', 'dog clipping', 'breed styling', 'dog bathing', 'coat care', 'dog salon', 'pet styling']
    },
    "kennel_cattery": {
        "name": "Animal Care Facilities",
        "domain": "agriculture_primary",
        "description": "Operating animal boarding, breeding, and training facilities including kennels, catteries, dog breeding, puppy care, whelping, fostering pups, operant conditioning, positive reinforcement, mother-pup bonding, obedience training, and animal socialization.",
        "keywords": ['kennel', 'cattery', 'animal boarding', 'dog breeding', 'puppy care', 'whelping', 'pup fostering', 'operant conditioning', 'positive reinforcement', 'dog training', 'obedience training', 'litter care', 'puppy socialization', 'pup monitoring', 'animal fostering', 'species behavior', 'behavior selection']
    },
    "horse_care": {
        "name": "Equine Husbandry",
        "domain": "agriculture_primary",
        "description": "Managing horses including stable management, feeding, health care, breeding, foaling, mare and foal care, and stud operations.",
        "keywords": ['horse', 'equine', 'stable', 'horse care', 'horse husbandry', 'stud', 'mare', 'stallion', 'foaling', 'foal care', 'horse breeding', 'yearling']
    },
    "horse_riding": {
        "name": "Horse Training",
        "domain": "agriculture_primary",
        "description": "Teaching horse riding and equestrian skills to human riders including dressage, jumping, western riding, and horsemanship instruction. Training horses and riders.",
        "keywords": ['horse riding', 'equestrian', 'riding instruction', 'horse training', 'dressage', 'jumping', 'riding lessons', 'horsemanship', 'horse schooling', 'breaking horses']
    },
    "farrier": {
        "name": "Farriery Horseshoeing",
        "domain": "agriculture_primary",
        "description": "Shoeing horses and caring for hooves including trimming, balancing, and therapeutic shoeing",
        "keywords": ["farrier", "horseshoeing", "hoof care", "horseshoe", "hoof trimming", "blacksmith", "hoof health"]
    },
    "racing_industry": {
        "name": "Racing Industry Operations",
        "domain": "agriculture_primary",
        "description": "Working in horse racing or greyhound racing including stable hands, track work, animal conditioning, breeding operations, and race day operations.",
        "keywords": ['horse racing', 'greyhound racing', 'racehorse', 'stable hand', 'track work', 'racing greyhound', 'thoroughbred', 'racing industry', 'racing breeding']
    },
    
    # Aquaculture & Fishing
    "fish_farming": {
        "name": "Aquaculture Fish Farming",
        "domain": "agriculture_primary",
        "description": "Fish farming, hatchery operations, and aquaculture production",
        "keywords": ["fish farming", "aquaculture", "hatchery", "fish stock", "aquaculture production", "fish husbandry", "barramundi", "salmon", "trout"]
    },
    "oyster_shellfish": {
        "name": "Shellfish Aquaculture",
        "domain": "agriculture_primary",
        "description": "Cultivating oysters and shellfish including spat collection, growing, grading, and shellfish aquaculture operations.",
        "keywords": ['oyster', 'shellfish', 'oyster farming', 'oyster cultivation', 'spat', 'shellfish aquaculture', 'mussel', 'oyster lease']
    },
    "prawn_farming": {
        "name": "Prawn Aquaculture",
        "domain": "agriculture_primary",
        "description": "Farming prawns and crustaceans including breeding, hatchery operations, larval rearing, pond management, and harvest.",
        "keywords": ['prawn', 'prawn farming', 'crustacean', 'prawn breeding', 'prawn hatchery', 'larval rearing', 'aquaculture', 'shrimp']
    },
    "commercial_fishing": {
        "name": "Commercial Fishing",
        "domain": "agriculture_primary",
        "description": "Commercial fishing, net fishing, and trawling operations",
        "keywords": ["commercial fishing", "fishing", "trawling", "net fishing", "fishing vessel", "catch", "fish handling", "deck hand", "fishing boat"]
    },
    
    # Forestry
    "tree_felling": {
        "name": "Tree Felling Harvesting",
        "domain": "agriculture_primary",
        "description": "Tree felling, log extraction, and forest harvesting",
        "keywords": ["tree felling", "logging", "forest harvesting", "log extraction", "chainsaw", "tree harvesting", "skidder", "feller buncher"]
    },
    "sawmilling": {
        "name": "Sawmilling Timber Processing",
        "domain": "agriculture_primary",
        "description": "Operating sawmills to process logs into timber including milling, drying, and grading lumber",
        "keywords": ["sawmill", "sawmilling", "timber processing", "log sawing", "timber grading", "kiln drying", "timber drying", "lumber"]
    },
    "plantation_forestry": {
        "name": "Plantation Forestry",
        "domain": "agriculture_primary",
        "description": "Establishing and managing tree plantations for timber production including planting, thinning, and harvesting",
        "keywords": ["plantation", "plantation forestry", "tree planting", "forest establishment", "silviculture", "forest management", "pine plantation", "eucalyptus"]
    },
    
    # Conservation
    "bushland_restoration": {
        "name": "Bushland Revegetation",
        "domain": "agriculture_primary",
        "description": "Restoring native bushland including weed removal, revegetation, and ecological restoration techniques",
        "keywords": ["bushland restoration", "revegetation", "native vegetation", "habitat restoration", "bush regeneration", "native planting", "ecosystem restoration"]
    },
    "weed_control": {
        "name": "Weed Management",
        "domain": "agriculture_primary",
        "description": "Weed identification, control, and herbicide application",
        "keywords": ["weed control", "weed management", "herbicide", "weed spraying", "weed identification", "noxious weeds", "weed eradication"]
    },
    "pest_animal_control": {
        "name": "Pest Animal Control",
        "domain": "agriculture_primary",
        "description": "Controlling pest animals including feral pigs, foxes, rabbits, and wild dogs using trapping and baiting",
        "keywords": ["pest animal", "feral animal", "pest control", "rabbit control", "fox control", "feral pig", "trapping", "baiting", "culling"]
    },
    "fire_management": {
        "name": "Prescribed Fire Management",
        "domain": "agriculture_primary",
        "description": "Managing fire in landscapes including prescribed burning, fire breaks, and bushfire risk reduction",
        "keywords": ["fire management", "prescribed burning", "hazard reduction", "controlled burn", "fire break", "bushfire management", "burn off"]
    },
    "park_ranger": {
        "name": "Park Management",
        "domain": "agriculture_primary",
        "description": "Managing national parks and reserves including conservation, visitor management, and natural resource management",
        "keywords": ["park ranger", "ranger", "national park", "reserve management", "park management", "conservation area", "wildlife management"]
    },
    
    # Beekeeping
    "beekeeping": {
        "name": "Beekeeping Apiculture",
        "domain": "agriculture_primary",
        "description": "Beehive management, honey extraction, and pollination services",
        "keywords": ["beekeeping", "apiculture", "honey", "beehive", "bees", "queen rearing", "honey extraction", "pollination", "apiary"]
    },
    
    # Meat Processing
    "slaughtering": {
        "name": "Slaughtering Operations",
        "domain": "agriculture_primary",
        "description": "Processing livestock in abattoirs including slaughtering, dressing, and carcass handling operations",
        "keywords": ["slaughtering", "abattoir", "slaughter", "stunning", "bleeding", "livestock processing", "kill floor"]
    },
    "boning_slicing": {
        "name": "Meat Boning Slicing",
        "domain": "agriculture_primary",
        "description": "Breaking down meat carcasses including boning, slicing, trimming, and preparing primal cuts",
        "keywords": ["boning", "slicing", "meat cutting", "carcase", "primal cuts", "boner", "slicer", "meat breakdown"]
    },
    "retail_butchery": {
        "name": "Retail Butchery",
        "domain": "agriculture_primary",
        "description": "Retail meat cutting, display, and customer service",
        "keywords": ["butcher", "retail butchery", "meat retail", "butcher shop", "meat display", "meat preparation", "smallgoods"]
    },
    "meat_inspection": {
        "name": "Meat Inspection",
        "domain": "agriculture_primary",
        "description": "Inspecting meat and livestock for quality and safety compliance in abattoirs and processing facilities",
        "keywords": ["meat inspection", "meat inspector", "meat quality", "carcase grading", "meat standards", "ante-mortem", "post-mortem"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTION, BUILDING & TRADES (65 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Carpentry
    "wall_framing": {
        "name": "Wall Framing",
        "domain": "construction_building",
        "description": "Constructing timber wall frames for residential and commercial buildings including load-bearing walls.",
        "keywords": ["wall framing", "wall frame", "stud wall", "timber framing", "wall construction", "noggin", "top plate", "bottom plate"]
    },
    "roof_framing": {
        "name": "Roof Framing",
        "domain": "construction_building",
        "description": "Constructing timber roof structures including trusses, rafters, and roof framing systems.",
        "keywords": ["roof framing", "roof truss", "rafter", "ridge beam", "roof construction", "hip roof", "gable", "ceiling joist", "purlin"]
    },
    "floor_framing": {
        "name": "Floor Framing",
        "domain": "construction_building",
        "description": "Constructing timber floor frames and subfloor structures including bearers and joists.",
        "keywords": ["floor framing", "floor joist", "bearer", "subfloor", "floor construction", "stumps", "piers", "floor system"]
    },
    "formwork": {
        "name": "Formwork Construction",
        "domain": "construction_building",
        "description": "Constructing concrete formwork for slabs, walls, and structural concrete including traditional and system formwork.",
        "keywords": ["formwork", "concrete formwork", "shuttering", "form construction", "formwork installation", "stripping formwork", "boxing"]
    },
    "timber_flooring": {
        "name": "Timber Flooring Installation",
        "domain": "construction_building",
        "description": "Installing timber flooring including solid timber, parquetry, and timber floor finishing.",
        "keywords": ["timber flooring", "floor sanding", "hardwood floor", "floor laying", "floor finishing", "timber floor", "floor polishing", "parquetry"]
    },
    "stair_construction": {
        "name": "Stair Construction",
        "domain": "construction_building",
        "description": "Constructing stairs including timber stairs, balustrades, and stair installation.",
        "keywords": ["stair construction", "staircase", "balustrade", "handrail", "stringer", "tread", "riser", "newel post"]
    },
    "door_window_install": {
        "name": "Door Window Installation",
        "domain": "construction_building",
        "description": "Installing doors and windows in buildings including frames, hardware, flashing, and weathersealing",
        "keywords": ["door installation", "window installation", "door fitting", "window fitting", "door frame", "window frame", "door hanging", "glazing bead"]
    },
    "kitchen_cabinets": {
        "name": "Kitchen Installation",
        "domain": "construction_building",
        "description": "Installing kitchen cabinetry and benchtops including flat-pack assembly, custom kitchens, and joinery fitout",
        "keywords": ["kitchen installation", "cabinet installation", "kitchen cabinets", "benchtop", "kitchen fitting", "splashback", "pantry"]
    },
    "decking_pergola": {
        "name": "Decking Pergola Construction",
        "domain": "construction_building",
        "description": "Constructing timber decks and pergolas including composite decking and outdoor structures.",
        "keywords": ["decking", "deck construction", "pergola", "outdoor structure", "deck building", "verandah", "gazebo", "outdoor living"]
    },
    "cabinetmaking": {
        "name": "Cabinetmaking Joinery",
        "domain": "construction_building",
        "description": "Manufacturing and installing custom cabinetry, furniture, and joinery using timber and board products.",
        "keywords": ["cabinetmaking", "cabinet maker", "furniture making", "joinery", "custom cabinets", "built-in", "wardrobe", "vanity"]
    },
    
    # Bricklaying & Masonry
    "bricklaying": {
        "name": "Bricklaying Masonry",
        "domain": "construction_building",
        "description": "Laying bricks and blocks for walls, fences, and structures including brick bonds and mortar work.",
        "keywords": ["bricklaying", "brick", "bricklayer", "brick wall", "mortar", "brick course", "pointing", "brick veneer"]
    },
    "blocklaying": {
        "name": "Block Laying",
        "domain": "construction_building",
        "description": "Laying concrete blocks and masonry units for structural and retaining walls.",
        "keywords": ["blocklaying", "concrete block", "block wall", "masonry block", "block laying", "besser block", "core filling"]
    },
    "stone_masonry": {
        "name": "Stone Masonry",
        "domain": "construction_building",
        "description": "Working with natural and manufactured stone including stone walls, cladding, and masonry restoration.",
        "keywords": ["stone masonry", "stone wall", "stonework", "natural stone", "stone laying", "sandstone", "bluestone", "limestone"]
    },
    "paving": {
        "name": "Paving Installation",
        "domain": "construction_building",
        "description": "Laying pavers and segmental paving for driveways, paths, and outdoor areas.",
        "keywords": ["paving", "pavers", "brick paving", "segmental paving", "paver installation", "driveway paving", "pathway", "paver laying"]
    },
    
    # Plumbing
    "water_supply_plumbing": {
        "name": "Water Supply Plumbing",
        "domain": "construction_building",
        "description": "Installing water supply pipework and fixtures in buildings including copper, PEX, and water services.",
        "keywords": ["water supply", "water pipe", "copper pipe", "water plumbing", "pipe installation", "water main", "water connection", "pipe fitting"]
    },
    "drainage_plumbing": {
        "name": "Drainage Plumbing",
        "domain": "construction_building",
        "description": "Installing drainage and sewer connections for buildings including PVC drainage and sewer compliance.",
        "keywords": ["drainage", "sewerage", "drain pipe", "sewer", "drainage installation", "stormwater", "septic", "waste pipe", "drain laying"]
    },
    "sanitary_fixtures": {
        "name": "Sanitary Plumbing",
        "domain": "construction_building",
        "description": "Installing bathroom fixtures including toilets, basins, showers, baths, and tapware in residential and commercial buildings",
        "keywords": ["sanitary", "toilet installation", "basin", "bathroom fixtures", "plumbing fixtures", "tapware", "bath", "shower"]
    },
    "hot_water_systems": {
        "name": "Hot Water Installation",
        "domain": "construction_building",
        "description": "Installing and repairing hot water systems including gas, electric, solar, and heat pump water heaters",
        "keywords": ["hot water", "hot water system", "water heater", "tempering valve", "solar hot water", "heat pump", "gas hot water", "electric hot water"]
    },
    "roof_plumbing": {
        "name": "Roof Plumbing Guttering",
        "domain": "construction_building",
        "description": "Installing roof plumbing including gutters, downpipes, flashings, and roof drainage.",
        "keywords": ["roof plumbing", "guttering", "gutter", "downpipe", "roof drainage", "flashing", "box gutter", "rainwater"]
    },
    "gas_fitting": {
        "name": "Gas Fitting",
        "domain": "construction_building",
        "description": "Installing gas appliances and gas piping in buildings including cooktops, heaters, and gas compliance.",
        "keywords": ["gas fitting", "gas pipe", "gas installation", "gas appliance", "gas connection", "gas meter", "natural gas", "LPG"]
    },
    
    # Electrical
    "domestic_wiring": {
        "name": "Domestic Electrical",
        "domain": "electrical_communications",
        "description": "Installing electrical wiring in residential homes including circuits, switchboards, power points, and lighting",
        "keywords": ["domestic wiring", "electrical wiring", "house wiring", "residential electrical", "power points", "light switches", "electrical installation"]
    },
    "commercial_electrical": {
        "name": "Commercial Electrical",
        "domain": "electrical_communications",
        "description": "Installing electrical systems in commercial and industrial buildings including power distribution and lighting.",
        "keywords": ["commercial electrical", "industrial electrical", "3 phase", "distribution board", "switchboard", "power distribution", "electrical contractor"]
    },
    "electrical_maintenance": {
        "name": "Industrial Electrical Maintenance",
        "domain": "construction_building",
        "description": "Maintaining industrial electrical systems including motors, switchboards, control panels, and factory electrical equipment. Not IT/computer systems.",
        "keywords": ["electrical maintenance", "electrical repair", "fault finding", "electrical testing", "repair electrical", "electrical service"]
    },
    "lighting_installation": {
        "name": "Lighting Installation",
        "domain": "electrical_communications",
        "description": "Installing lighting systems in buildings including LED lighting, controls, and emergency lighting.",
        "keywords": ["lighting installation", "light fitting", "LED lighting", "light installation", "downlight", "pendant light", "lighting design"]
    },
    "data_cabling": {
        "name": "Data Cabling",
        "domain": "electrical_communications",
        "description": "Installing structured data cabling in buildings including Cat6, fibre optic, and network infrastructure.",
        "keywords": ["data cabling", "structured cabling", "network cable", "cat6", "data points", "patch panel", "communications cabling", "fibre optic"]
    },
    "solar_pv_installation": {
        "name": "Solar PV Installation",
        "domain": "electrical_communications",
        "description": "Installing rooftop solar PV systems on buildings including panels, inverters, and grid connections.",
        "keywords": ["solar installation", "solar panel", "solar PV", "inverter", "solar system", "photovoltaic", "grid connect", "solar mounting"]
    },
    "air_conditioning_install": {
        "name": "HVAC Installation",
        "domain": "electrical_communications",
        "description": "Split system and ducted air conditioning installation",
        "keywords": ["air conditioning", "air con installation", "split system", "ducted air conditioning", "HVAC installation", "AC installation", "refrigerant"]
    },
    "refrigeration": {
        "name": "Refrigeration Systems",
        "domain": "electrical_communications",
        "description": "Installing and servicing commercial refrigeration systems including cool rooms, display units, and refrigeration equipment.",
        "keywords": ["refrigeration", "commercial refrigeration", "coolroom", "freezer", "refrigeration service", "refrigerant handling", "cold storage"]
    },
    
    # Painting & Decorating
    "interior_painting": {
        "name": "Interior Painting",
        "domain": "construction_building",
        "description": "Painting interior surfaces including walls, ceilings, and trim in residential and commercial buildings.",
        "keywords": ["interior painting", "wall painting", "ceiling painting", "indoor painting", "brush painting", "roller painting", "cutting in"]
    },
    "exterior_painting": {
        "name": "Exterior Painting",
        "domain": "construction_building",
        "description": "Painting exterior building surfaces including weatherboards, render, and exterior trim.",
        "keywords": ["exterior painting", "house painting", "outdoor painting", "weatherboard", "render painting", "exterior surfaces"]
    },
    "spray_painting_building": {
        "name": "Building Spray Painting",
        "domain": "construction_building",
        "description": "Spray painting building components including doors, cabinets, steelwork, and architectural elements",
        "keywords": ["spray painting", "airless spraying", "spray application", "spray gun", "paint spraying", "industrial painting"]
    },
    "wallpapering": {
        "name": "Wallpapering Installation",
        "domain": "construction_building",
        "description": "Hanging wallpaper and wall coverings including preparation, adhesive application, and pattern matching.",
        "keywords": ["wallpaper", "wallpapering", "wall covering", "wallpaper hanging", "wallpaper installation", "vinyl wallpaper", "paper hanging"]
    },
    "decorative_finishes": {
        "name": "Decorative Painting",
        "domain": "construction_building",
        "description": "Applying decorative paint finishes including faux finishes, venetian plaster, texture coats, and specialty coatings",
        "keywords": ["decorative finish", "faux finish", "texture coating", "venetian plaster", "specialty finish", "marbling", "colour washing"]
    },
    
    # Plastering
    "solid_plastering": {
        "name": "Solid Plastering Rendering",
        "domain": "construction_building",
        "description": "Applying cement render and solid plaster finishes to walls including sand and cement rendering.",
        "keywords": ["solid plastering", "rendering", "cement render", "sand and cement", "plaster rendering", "scratch coat", "float finish"]
    },
    "plasterboard_installation": {
        "name": "Plasterboard Installation",
        "domain": "construction_building",
        "description": "Installing plasterboard wall and ceiling linings including framing, fixing, and cornices.",
        "keywords": ["plasterboard", "gyprock", "drywall", "plasterboard installation", "wall lining", "ceiling lining", "plaster sheeting"]
    },
    "plasterboard_stopping": {
        "name": "Plasterboard Finishing",
        "domain": "construction_building",
        "description": "Finishing plasterboard joints including taping, setting compound, sanding, and preparing walls for painting",
        "keywords": ["stopping", "plasterboard finishing", "jointing", "plaster finishing", "tape and stop", "cornice", "sanding"]
    },
    "cornice_installation": {
        "name": "Cornice Installation",
        "domain": "construction_building",
        "description": "Installing decorative cornices and ceiling mouldings including plaster and polystyrene cornices.",
        "keywords": ["cornice", "moulding", "decorative cornice", "ceiling rose", "architrave", "skirting", "dado rail", "picture rail"]
    },
    
    # Tiling
    "wall_tiling": {
        "name": "Wall Tiling",
        "domain": "construction_building",
        "description": "Installing ceramic, porcelain, and natural stone tiles on walls in bathrooms and wet areas.",
        "keywords": ["wall tiling", "wall tiles", "bathroom tiles", "kitchen tiles", "ceramic tiles", "tile installation", "splashback tiles"]
    },
    "floor_tiling": {
        "name": "Floor Tiling",
        "domain": "construction_building",
        "description": "Installing floor tiles including large format tiles, preparation, and tile layout.",
        "keywords": ["floor tiling", "floor tiles", "porcelain tiles", "tile laying", "large format tiles", "floor tile installation", "grout"]
    },
    "waterproofing": {
        "name": "Waterproofing Application",
        "domain": "construction_building",
        "description": "Applying waterproofing membranes to wet areas, balconies, and below-ground structures.",
        "keywords": ["waterproofing", "waterproof membrane", "wet area", "shower waterproofing", "bathroom waterproofing", "tanking", "sealing"]
    },
    
    # Roofing
    "roof_tiling": {
        "name": "Roof Tiling",
        "domain": "construction_building",
        "description": "Installing concrete and terracotta roof tiles including battens, bedding, and pointing.",
        "keywords": ["roof tiling", "roof tiles", "tile roofing", "terracotta tiles", "concrete tiles", "roof tile installation", "ridge capping"]
    },
    "metal_roofing": {
        "name": "Metal Roofing",
        "domain": "construction_building",
        "description": "Installing metal roof sheeting including Colorbond, flashings, and metal roof systems.",
        "keywords": ["metal roofing", "colorbond", "roof sheeting", "metal roof", "corrugated iron", "zincalume", "roof installation"]
    },
    "roof_restoration": {
        "name": "Roof Restoration",
        "domain": "construction_building",
        "description": "Restoring and recoating roofs including cleaning, repairs, and protective coatings.",
        "keywords": ["roof restoration", "roof repair", "roof cleaning", "roof painting", "tile repair", "roof maintenance", "repointing"]
    },
    
    # Glazing
    "window_glazing": {
        "name": "Window Glazing",
        "domain": "construction_building",
        "description": "Installing glass in windows and doors including double glazing and glazing systems.",
        "keywords": ["glazing", "window glass", "glass installation", "glass replacement", "double glazing", "glazier", "window repair"]
    },
    "shopfront_glazing": {
        "name": "Commercial Glazing",
        "domain": "construction_building",
        "description": "Installing commercial glazing including shopfronts, curtain walls, automatic doors, and commercial glass systems",
        "keywords": ["shopfront", "commercial glazing", "curtain wall", "structural glazing", "frameless glass", "glass doors", "automatic doors"]
    },
    "mirror_installation": {
        "name": "Mirror Splashback Installation",
        "domain": "construction_building",
        "description": "Installing mirrors and glass splashbacks including measuring, cutting, polishing, and adhesive or mechanical fixing",
        "keywords": ["mirror installation", "mirror", "glass splashback", "bathroom mirror", "mirror fixing", "splashback"]
    },
    
    # Flooring
    "carpet_laying": {
        "name": "Carpet Laying",
        "domain": "construction_building",
        "description": "Installing carpet flooring including underlay, stretching, and seaming.",
        "keywords": ["carpet laying", "carpet installation", "carpet fitting", "carpet stretching", "underlay", "carpet gripper", "carpet seaming"]
    },
    "vinyl_flooring": {
        "name": "Vinyl Flooring Installation",
        "domain": "construction_building",
        "description": "Installing vinyl and resilient flooring including sheet vinyl, LVT, and vinyl planks.",
        "keywords": ["vinyl flooring", "vinyl installation", "linoleum", "resilient flooring", "sheet vinyl", "vinyl tiles", "LVT"]
    },
    "laminate_flooring": {
        "name": "Floating Floor Installation",
        "domain": "construction_building",
        "description": "Installing laminate and floating floors including underlay, click-lock installation, and transition strips",
        "keywords": ["laminate flooring", "floating floor", "laminate installation", "click lock", "laminate floor", "engineered flooring"]
    },
    
    # Concrete & Civil
    "concrete_placement": {
        "name": "Concrete Finishing",
        "domain": "construction_building",
        "description": "Placing and finishing concrete including pouring, screeding, floating, trowelling, and curing concrete slabs",
        "keywords": ["concrete", "concrete placement", "concrete finishing", "concrete pour", "screeding", "trowelling", "concrete slab"]
    },
    "exposed_aggregate": {
        "name": "Decorative Concrete",
        "domain": "construction_building",
        "description": "Creating decorative concrete finishes including exposed aggregate, stamped concrete, and polished concrete floors",
        "keywords": ["exposed aggregate", "decorative concrete", "polished concrete", "stamped concrete", "stencilled concrete", "coloured concrete"]
    },
    "concreting_civil": {
        "name": "Civil Concreting",
        "domain": "construction_building",
        "description": "Placing concrete for civil works including kerbs, gutters, footpaths, driveways, and infrastructure concreting",
        "keywords": ["civil concrete", "kerb", "kerbing", "footpath", "drainage pit", "civil works", "concrete channel"]
    },
    
    # Scaffolding
    "scaffold_erection": {
        "name": "Scaffolding Erection",
        "domain": "construction_building",
        "description": "Erecting scaffolding for construction access including tube and coupler, modular scaffolding, and scaffold safety",
        "keywords": ["scaffold", "scaffolding", "scaffold erection", "scaffold assembly", "modular scaffold", "tube and fitting", "working platform"]
    },
    "rigging": {
        "name": "Rigging Dogging",
        "domain": "construction_building",
        "description": "Performing rigging operations including slinging loads, crane signalling, dogging, and load shifting safely",
        "keywords": ["rigging", "dogging", "dogman", "rigger", "crane signalling", "sling", "lifting", "load calculation"]
    },
    
    # Other Building
    "demolition": {
        "name": "Demolition Work",
        "domain": "construction_building",
        "description": "Demolishing buildings and structures including asbestos awareness and demolition safety.",
        "keywords": ["demolition", "building demolition", "strip out", "site clearance", "demolition work", "deconstruction"]
    },
    "asbestos_removal": {
        "name": "Asbestos Removal",
        "domain": "construction_building",
        "description": "Removing asbestos-containing materials safely including Class A and Class B asbestos removal.",
        "keywords": ["asbestos", "asbestos removal", "asbestos abatement", "friable asbestos", "non-friable", "ACM", "asbestos disposal"]
    },
    "fencing": {
        "name": "Fencing Installation",
        "domain": "construction_building",
        "description": "Installing fences including timber, Colorbond, pool fencing, and security fencing.",
        "keywords": ["fencing", "fence installation", "fence construction", "timber fence", "colorbond fence", "pool fence", "gate", "post hole"]
    },
    "swimming_pool_building": {
        "name": "Pool Construction",
        "domain": "construction_building",
        "description": "Constructing swimming pools including concrete pools, fibreglass installation, tiling, and pool surrounds",
        "keywords": ["swimming pool", "pool construction", "pool building", "pool shell", "pool tiling", "pool coping", "fibreglass pool", "concrete pool"]
    },
    "building_inspection": {
        "name": "Building Inspection",
        "domain": "construction_building",
        "description": "Inspecting buildings for compliance including building certifiers and inspection reporting.",
        "keywords": ["building inspection", "building inspector", "construction inspection", "compliance inspection", "defect inspection", "pre-purchase inspection"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AUTOMOTIVE, TRANSPORT & LOGISTICS (45 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Mechanical
    "engine_repair": {
        "name": "Engine Repair",
        "domain": "automotive_repair",
        "description": "Repairing and overhauling internal combustion engines including diagnosis, component replacement, and engine rebuilding for vehicles.",
        "keywords": ["engine repair", "engine overhaul", "engine rebuild", "engine diagnostics", "cylinder head", "engine block", "timing", "valve"]
    },
    "brake_systems": {
        "name": "Brake System Repair",
        "domain": "automotive_repair",
        "description": "Servicing and repairing vehicle brake systems including disc brakes, drum brakes, ABS, and brake component replacement.",
        "keywords": ["brake", "brake repair", "brake pads", "brake rotors", "disc brakes", "drum brakes", "brake service", "ABS", "brake fluid"]
    },
    "suspension_steering": {
        "name": "Suspension Steering Repair",
        "domain": "automotive_repair",
        "description": "Repairing vehicle suspension and steering systems including shocks, springs, ball joints, and steering components.",
        "keywords": ["suspension", "steering", "shock absorber", "strut", "control arm", "wheel alignment", "power steering", "rack and pinion"]
    },
    "transmission_service": {
        "name": "Transmission Drivetrain Service",
        "domain": "automotive_repair",
        "description": "Servicing and repairing vehicle transmissions and drivetrains including manual, automatic, and CVT transmissions.",
        "keywords": ["transmission", "gearbox", "clutch", "differential", "drivetrain", "CV joint", "driveshaft", "automatic transmission", "manual transmission"]
    },
    "vehicle_servicing": {
        "name": "Vehicle Servicing",
        "domain": "automotive_repair",
        "description": "Performing scheduled vehicle servicing including oil changes, filters, fluids, and routine maintenance.",
        "keywords": ["vehicle service", "car service", "oil change", "log book service", "routine maintenance", "filter replacement", "service schedule"]
    },
    "exhaust_systems": {
        "name": "Exhaust System Repair",
        "domain": "automotive_repair",
        "description": "Repairing exhaust systems including mufflers, catalytic converters, and exhaust component replacement.",
        "keywords": ["exhaust", "exhaust system", "muffler", "catalytic converter", "exhaust manifold", "exhaust repair", "DPF"]
    },
    "tyre_fitting": {
        "name": "Tyre Wheel Service",
        "domain": "automotive_repair",
        "description": "Fitting and balancing tyres including wheel alignment, puncture repairs, and tyre rotation.",
        "keywords": ["tyre fitting", "tyre", "wheel balancing", "tyre change", "wheel alignment", "tyre repair", "puncture repair", "tyre rotation"]
    },
    
    # Electrical
    "auto_electrical": {
        "name": "Auto Electrical Systems",
        "domain": "automotive_repair",
        "description": "Diagnosing and repairing automotive electrical systems including starters, alternators, wiring, and electrical faults.",
        "keywords": ["auto electrical", "automotive electrical", "car electrical", "wiring", "alternator", "starter motor", "battery", "electrical fault"]
    },
    "vehicle_electronics": {
        "name": "Vehicle Diagnostics",
        "domain": "automotive_repair",
        "description": "Diagnosing vehicle electronic systems using scan tools including ECU faults, sensors, and electronic components",
        "keywords": ["vehicle electronics", "ECU", "diagnostic", "scan tool", "engine management", "OBD", "vehicle computer", "electronic control"]
    },
    "air_conditioning_auto": {
        "name": "Automotive Air Conditioning",
        "domain": "automotive_repair",
        "description": "Servicing automotive air conditioning systems including refrigerant recovery, regas, and A/C repairs.",
        "keywords": ["automotive air conditioning", "car AC", "vehicle air con", "refrigerant", "AC regas", "compressor", "car climate control"]
    },
    
    # Body Repair
    "panel_beating": {
        "name": "Panel Beating",
        "domain": "automotive_repair",
        "description": "Repairing vehicle body panels including collision repair, panel replacement, and body restoration.",
        "keywords": ["panel beating", "body repair", "panel repair", "dent repair", "collision repair", "panel beater", "body work", "structural repair"]
    },
    "spray_painting_auto": {
        "name": "Automotive Spray Painting",
        "domain": "automotive_repair",
        "description": "Spray painting vehicles including preparation, colour matching, clear coat application, and automotive refinishing.",
        "keywords": ["spray painting", "automotive painting", "car painting", "vehicle refinishing", "clear coat", "base coat", "paint booth", "colour matching"]
    },
    "paint_preparation": {
        "name": "Paint Preparation",
        "domain": "automotive_repair",
        "description": "Preparing vehicle surfaces for painting including sanding, priming, and masking.",
        "keywords": ["paint preparation", "sanding", "primer", "filler", "surface prep", "block sanding", "masking", "prep work"]
    },
    "paintless_dent_repair": {
        "name": "Paintless Dent Repair",
        "domain": "automotive_repair",
        "description": "Removing dents from vehicle panels without repainting using PDR techniques.",
        "keywords": ["paintless dent repair", "PDR", "dent removal", "hail damage", "dent puller", "dent tools"]
    },
    "windscreen_repair": {
        "name": "Windscreen Replacement",
        "domain": "automotive_repair",
        "description": "Repairing and replacing automotive windscreens and vehicle glass including chip repairs and installations",
        "keywords": ["windscreen", "windscreen repair", "windscreen replacement", "auto glass", "chip repair", "glass replacement"]
    },
    "vehicle_detailing": {
        "name": "Vehicle Detailing",
        "domain": "automotive_repair",
        "description": "Detailing vehicles including interior and exterior cleaning, polishing, and paint protection.",
        "keywords": ["vehicle detailing", "car detailing", "car wash", "polishing", "waxing", "interior cleaning", "paint correction", "ceramic coating"]
    },
    
    # Heavy Vehicle
    "heavy_vehicle_mechanic": {
        "name": "Heavy Vehicle Mechanical",
        "domain": "automotive_repair",
        "description": "Maintaining and repairing heavy vehicles including trucks, buses, and heavy commercial vehicles.",
        "keywords": ["heavy vehicle", "truck mechanic", "bus mechanic", "diesel mechanic", "heavy duty", "truck repair", "commercial vehicle"]
    },
    "diesel_systems": {
        "name": "Diesel Fuel Systems",
        "domain": "automotive_repair",
        "description": "Servicing diesel fuel systems including injectors, fuel pumps, turbochargers, and diesel engine components.",
        "keywords": ["diesel", "diesel fuel system", "fuel injection", "common rail", "diesel pump", "injector", "diesel engine"]
    },
    "trailer_repair": {
        "name": "Trailer Servicing",
        "domain": "automotive_repair",
        "description": "Servicing and repairing trailers including brakes, bearings, axles, electrical systems, and structural repairs",
        "keywords": ["trailer", "trailer repair", "trailer maintenance", "trailer brakes", "trailer coupling", "trailer service"]
    },
    
    # Motorcycle & Small Engine
    "motorcycle_mechanic": {
        "name": "Motorcycle Mechanical",
        "domain": "automotive_repair",
        "description": "Maintaining and repairing motorcycles including engines, brakes, and electrical systems.",
        "keywords": ["motorcycle", "motorbike", "motorcycle mechanic", "motorcycle service", "motorcycle repair", "two-wheeler"]
    },
    "outdoor_power_equipment": {
        "name": "Outdoor Power Equipment",
        "domain": "automotive_repair",
        "description": "Servicing outdoor power equipment including mowers, chainsaws, and small engines.",
        "keywords": ["outdoor power equipment", "small engine", "lawn mower", "chainsaw", "brush cutter", "blower", "garden equipment"]
    },
    "marine_mechanic": {
        "name": "Marine Mechanical",
        "domain": "automotive_repair",
        "description": "Maintaining and repairing marine engines and boat systems including outboards, inboards, and marine equipment.",
        "keywords": ["marine mechanic", "boat engine", "outboard motor", "marine engine", "boat repair", "inboard engine"]
    },
    
    # Electric Vehicles
    "ev_service": {
        "name": "Electric Vehicle Service",
        "domain": "automotive_repair",
        "description": "Servicing electric vehicles including EV battery systems, charging systems, and high-voltage safety.",
        "keywords": ["electric vehicle", "EV", "hybrid vehicle", "EV service", "electric car", "battery electric", "high voltage", "EV charging"]
    },
    
    # Driving
    "car_driving": {
        "name": "Motor Vehicle Driving",
        "domain": "transport_logistics",
        "description": "Driving motor vehicles including car licence, defensive driving, and road safety.",
        "keywords": ["car driving", "driving", "driver", "light vehicle", "motor vehicle", "driving licence", "road rules"]
    },
    "heavy_rigid_driving": {
        "name": "Heavy Rigid Driving",
        "domain": "transport_logistics",
        "description": "Driving heavy rigid vehicles including HR licence trucks and rigid vehicle operation.",
        "keywords": ["heavy rigid", "HR licence", "truck driving", "rigid truck", "HR driving", "heavy vehicle driving"]
    },
    "heavy_combination_driving": {
        "name": "Heavy Combination Driving",
        "domain": "transport_logistics",
        "description": "Driving heavy combination vehicles including HC licence trucks and B-double operation.",
        "keywords": ["heavy combination", "HC licence", "articulated truck", "semi trailer", "B-double", "HC driving"]
    },
    "multi_combination_driving": {
        "name": "Multi-Combination Driving",
        "domain": "transport_logistics",
        "description": "Driving multi-combination vehicles including MC licence road trains and multi-trailers.",
        "keywords": ["multi-combination", "MC licence", "road train", "MC driving", "B-triple", "super B-double"]
    },
    "bus_driving": {
        "name": "Bus Driving",
        "domain": "transport_logistics",
        "description": "Driving passenger buses including route services, charter, and bus passenger safety.",
        "keywords": ["bus driving", "bus driver", "coach driving", "passenger vehicle", "bus licence", "public transport"]
    },
    "forklift_operation": {
        "name": "Forklift Operation",
        "domain": "transport_logistics",
        "description": "Operating forklifts including counterbalance, reach, and warehouse forklift operation with LF licence.",
        "keywords": ["forklift", "forklift operation", "forklift driving", "forklift licence", "forklift operator", "pallet", "high reach"]
    },
    "crane_operation": {
        "name": "Crane Operation",
        "domain": "transport_logistics",
        "description": "Operating cranes including mobile cranes, tower cranes, and crane licence classifications.",
        "keywords": ["crane", "crane operation", "crane driver", "mobile crane", "tower crane", "slewing crane", "crane licence"]
    },
    "ewp_operation": {
        "name": "EWP Operation",
        "domain": "transport_logistics",
        "description": "Operating elevated work platforms including scissor lifts, boom lifts, and EWP licence.",
        "keywords": ["EWP", "elevated work platform", "boom lift", "scissor lift", "cherry picker", "MEWP", "working at heights"]
    },
    
    # Warehousing
    "warehouse_operations": {
        "name": "Warehouse Operations",
        "domain": "transport_logistics",
        "description": "Working in warehouses including receiving, storage, inventory management, and dispatch operations.",
        "keywords": ["warehouse", "warehouse operations", "warehousing", "receival", "dispatch", "inventory", "stock control", "warehouse management"]
    },
    "order_picking": {
        "name": "Order Picking Fulfilment",
        "domain": "transport_logistics",
        "description": "Picking and packing orders in warehouses including RF scanning, pick accuracy, and order fulfilment.",
        "keywords": ["order picking", "picking", "packing", "order fulfilment", "pick and pack", "order processing", "RF scanner"]
    },
    "goods_receival": {
        "name": "Goods Receival Dispatch",
        "domain": "transport_logistics",
        "description": "Receiving and dispatching goods including checking deliveries, documentation, and loading vehicles.",
        "keywords": ["receival", "dispatch", "goods receival", "shipping", "receiving goods", "consignment", "delivery docket"]
    },
    
    # Transport & Logistics
    "freight_forwarding": {
        "name": "Freight Forwarding",
        "domain": "transport_logistics",
        "description": "Coordinating freight movements including customs, shipping documentation, and logistics coordination.",
        "keywords": ["freight forwarding", "freight", "logistics", "shipping", "customs clearance", "import", "export", "freight broker"]
    },
    "transport_scheduling": {
        "name": "Transport Scheduling",
        "domain": "transport_logistics",
        "description": "Scheduling transport and deliveries including route planning, dispatch, and fleet coordination.",
        "keywords": ["transport scheduling", "dispatch", "fleet management", "route planning", "transport coordination", "logistics planning"]
    },
    "supply_chain_operations": {
        "name": "Supply Chain Operations",
        "domain": "transport_logistics",
        "description": "Managing supply chain operations including inventory, logistics, demand planning, and distribution",
        "keywords": ["supply chain", "logistics management", "inventory management", "demand planning", "supply planning", "3PL"]
    },
    
    # Maritime
    "deck_operations": {
        "name": "Maritime Deck Operations",
        "domain": "transport_logistics",
        "description": "Working on ship decks including seamanship, mooring, cargo handling, and deck maintenance",
        "keywords": ["deck operations", "seamanship", "deckhand", "mooring", "anchoring", "deck work", "maritime"]
    },
    "coxswain": {
        "name": "Coxswain Operations",
        "domain": "transport_logistics",
        "description": "Operating small commercial vessels including boat handling, navigation, and vessel safety management",
        "keywords": ["coxswain", "small vessel", "boat operation", "vessel master", "commercial vessel", "boat licence"]
    },
    
    # Rail
    "train_driving": {
        "name": "Train Driving",
        "domain": "transport_logistics",
        "description": "Driving trains and locomotives including passenger and freight train operation.",
        "keywords": ["train driving", "train driver", "locomotive", "rail operations", "train operation", "rail driver"]
    },
    "rail_shunting": {
        "name": "Rail Shunting",
        "domain": "transport_logistics",
        "description": "Shunting rail wagons and carriages including yard operations and rail coupling.",
        "keywords": ["shunting", "rail shunting", "rail yard", "shunter", "coupling", "marshalling", "rail operations"]
    },
    
    # Aviation
    "aircraft_ground_handling": {
        "name": "Aircraft Ground Handling",
        "domain": "transport_logistics",
        "description": "Handling aircraft on the ground including baggage, pushback, marshalling, and ramp services",
        "keywords": ["ground handling", "ramp operations", "aircraft handling", "baggage handling", "aircraft loading", "airport operations"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DIGITAL TECHNOLOGY & ICT (55 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Programming Languages
    "python_programming": {
        "name": "Python Programming",
        "domain": "digital_technology",
        "description": "Developing applications and scripts using Python programming language including libraries like NumPy, Pandas, Django, and Flask.",
        "keywords": ["Python", "Python programming", "Python development", "Python script", "Python code", "Django", "Flask", "pandas"]
    },
    "javascript_programming": {
        "name": "JavaScript Development",
        "domain": "digital_technology",
        "description": "Developing web applications using JavaScript and TypeScript including Node.js, npm packages, and modern ES6+ features.",
        "keywords": ["JavaScript", "JS", "TypeScript", "ES6", "Node.js", "npm", "JavaScript programming", "frontend JavaScript"]
    },
    "java_programming": {
        "name": "Java Programming",
        "domain": "digital_technology",
        "description": "Developing enterprise applications using Java programming language including Spring Boot, Maven, and JVM ecosystem tools.",
        "keywords": ["Java", "Java programming", "Java development", "Spring", "JVM", "Java application", "Maven", "Gradle"]
    },
    "csharp_dotnet": {
        "name": ".NET Development",
        "domain": "digital_technology",
        "description": "Developing applications using C# and .NET framework including ASP.NET, Entity Framework, and Visual Studio tooling.",
        "keywords": ["C#", "CSharp", ".NET", "dotnet", "ASP.NET", ".NET Core", "Visual Studio", "C# programming"]
    },
    "sql_database": {
        "name": "Database Development",
        "domain": "digital_technology",
        "description": "Developing databases using SQL including schema design, queries, stored procedures, and database administration",
        "keywords": ["SQL", "database", "SQL Server", "MySQL", "PostgreSQL", "Oracle", "database development", "query", "stored procedure"]
    },
    "php_programming": {
        "name": "PHP Development",
        "domain": "digital_technology",
        "description": "Developing web applications using PHP including Laravel, WordPress plugins, and server-side scripting",
        "keywords": ["PHP", "PHP programming", "Laravel", "WordPress development", "PHP development", "Symfony"]
    },
    
    # Web Development
    "frontend_web": {
        "name": "Frontend Development",
        "domain": "digital_technology",
        "description": "Building website front-ends using HTML, CSS, JavaScript, and responsive design techniques for browser-based user interfaces.",
        "keywords": ["frontend", "front-end", "HTML", "CSS", "web design", "responsive design", "Bootstrap", "Tailwind", "web layout"]
    },
    "react_development": {
        "name": "React Development",
        "domain": "digital_technology",
        "description": "Building user interfaces using React JavaScript library including hooks, state management, and component-based architecture.",
        "keywords": ["React", "ReactJS", "React.js", "React development", "Redux", "React hooks", "React components", "Next.js"]
    },
    "angular_development": {
        "name": "Angular Development",
        "domain": "digital_technology",
        "description": "Building single-page applications using Angular framework including TypeScript, RxJS, and Angular CLI.",
        "keywords": ["Angular", "AngularJS", "Angular development", "Angular components", "RxJS", "Angular CLI"]
    },
    "vue_development": {
        "name": "Vue.js Development",
        "domain": "digital_technology",
        "description": "Building web interfaces using Vue.js framework including Vuex state management, Vue Router, and component composition.",
        "keywords": ["Vue", "Vue.js", "Vuex", "Nuxt.js", "Vue development", "Vue components"]
    },
    "backend_web": {
        "name": "Backend Development",
        "domain": "digital_technology",
        "description": "Developing server-side web applications including APIs, databases, authentication, and business logic using various frameworks.",
        "keywords": ["backend", "back-end", "server-side", "API development", "REST API", "web server", "backend development"]
    },
    "wordpress_cms": {
        "name": "CMS Development",
        "domain": "digital_technology",
        "description": "Developing WordPress websites including themes, plugins, customisation, and content management",
        "keywords": ["WordPress", "CMS", "content management", "WordPress development", "WordPress theme", "WordPress plugin", "Drupal", "Joomla"]
    },
    
    # Mobile Development
    "ios_development": {
        "name": "iOS Development",
        "domain": "digital_technology",
        "description": "Developing native iOS mobile applications using Swift or Objective-C, Xcode, and Apple development frameworks.",
        "keywords": ["iOS", "iOS development", "Swift", "iPhone app", "iPad app", "Xcode", "iOS app", "Apple development"]
    },
    "android_development": {
        "name": "Android Development",
        "domain": "digital_technology",
        "description": "Developing native Android mobile applications using Kotlin or Java, Android Studio, and Android SDK.",
        "keywords": ["Android", "Android development", "Kotlin", "Android app", "Android Studio", "mobile app", "Android SDK"]
    },
    "react_native": {
        "name": "React Native Development",
        "domain": "digital_technology",
        "description": "Developing cross-platform mobile apps using React Native framework for iOS and Android deployment from single codebase.",
        "keywords": ["React Native", "cross-platform mobile", "mobile development", "React Native app", "Expo"]
    },
    
    # Data & Analytics
    "data_analysis": {
        "name": "Data Analysis",
        "domain": "digital_technology",
        "description": "Analysing datasets using statistical methods and tools like Excel, Python, or R to identify patterns, trends, and business insights.",
        "keywords": ["data analysis", "data analyst", "data interpretation", "Excel analysis", "statistical analysis", "data insights"]
    },
    "data_visualisation": {
        "name": "Data Visualisation",
        "domain": "digital_technology",
        "description": "Creating charts, dashboards, and visual reports using tools like Tableau, Power BI, or D3.js to communicate data insights.",
        "keywords": ["data visualisation", "data visualization", "dashboard", "Power BI", "Tableau", "charts", "graphs", "visual analytics"]
    },
    "business_intelligence": {
        "name": "Business Intelligence",
        "domain": "digital_technology",
        "description": "Creating BI reports and dashboards using tools like Power BI, Tableau, or Looker for business data analysis and visualisation.",
        "keywords": ["business intelligence", "BI", "reporting", "SSRS", "Crystal Reports", "business reporting", "BI tools"]
    },
    "data_engineering": {
        "name": "Data Engineering",
        "domain": "digital_technology",
        "description": "Building and maintaining data pipelines, ETL processes, data warehouses, and data infrastructure using tools like Spark, Airflow, or dbt.",
        "keywords": ["data engineering", "ETL", "data pipeline", "data warehouse", "data lake", "Apache Spark", "Airflow", "data integration"]
    },
    
    # AI & Machine Learning
    "machine_learning": {
        "name": "Machine Learning",
        "domain": "digital_technology",
        "description": "Developing machine learning and AI models using Python, TensorFlow, or scikit-learn for prediction, classification, and pattern recognition. Computer algorithms, not human learning.",
        "keywords": ['machine learning', 'ML', 'AI models', 'TensorFlow', 'scikit-learn', 'neural network', 'predictive modeling', 'classification', 'computer learning', 'algorithm training']
    },
    "deep_learning": {
        "name": "Deep Learning",
        "domain": "digital_technology",
        "description": "Building neural networks and deep learning models using TensorFlow, PyTorch, or Keras for image recognition, NLP, and complex pattern recognition.",
        "keywords": ["deep learning", "neural network", "TensorFlow", "PyTorch", "CNN", "RNN", "LSTM", "transformer"]
    },
    "nlp": {
        "name": "Natural Language Processing",
        "domain": "digital_technology",
        "description": "Building natural language processing systems for text analysis, sentiment analysis, chatbots, and language understanding using NLP libraries.",
        "keywords": ["NLP", "natural language processing", "text analysis", "sentiment analysis", "chatbot", "language model", "BERT", "GPT"]
    },
    "computer_vision": {
        "name": "Computer Vision",
        "domain": "digital_technology",
        "description": "Developing image and video analysis systems using OpenCV, convolutional neural networks, and object detection algorithms.",
        "keywords": ["computer vision", "image recognition", "object detection", "OpenCV", "image processing", "facial recognition", "YOLO"]
    },
    
    # Cloud & Infrastructure
    "aws": {
        "name": "AWS Cloud Services",
        "domain": "digital_technology",
        "description": "Deploying and managing IT cloud infrastructure on Amazon Web Services including EC2 servers, S3 storage, Lambda functions, RDS databases, and AWS cloud services.",
        "keywords": ['AWS', 'Amazon Web Services', 'EC2', 'S3', 'Lambda', 'RDS', 'cloud computing', 'AWS cloud', 'Amazon cloud', 'AWS infrastructure']
    },
    "azure": {
        "name": "Azure Cloud Services",
        "domain": "digital_technology",
        "description": "Deploying and managing IT cloud infrastructure on Microsoft Azure including Azure VMs, Azure Functions, Azure Storage, and Microsoft cloud services.",
        "keywords": ['Azure', 'Microsoft Azure', 'Azure cloud', 'Azure VMs', 'Azure Functions', 'Microsoft cloud', 'Azure infrastructure', 'Azure services']
    },
    "gcp": {
        "name": "Google Cloud Platform",
        "domain": "digital_technology",
        "description": "Deploying and managing cloud infrastructure on Google Cloud Platform including Compute Engine, Cloud Functions, and GCP services.",
        "keywords": ["GCP", "Google Cloud", "Google Cloud Platform", "BigQuery", "Google Kubernetes Engine", "GCP services"]
    },
    "docker_containers": {
        "name": "Container Technology",
        "domain": "digital_technology",
        "description": "Working with containerisation technologies including Docker, container images, container orchestration, and microservices deployment.",
        "keywords": ["Docker", "container", "containerisation", "Docker image", "Docker compose", "container orchestration"]
    },
    "kubernetes": {
        "name": "Kubernetes Orchestration",
        "domain": "digital_technology",
        "description": "Orchestrating containerised applications using Kubernetes including pods, deployments, services, and cluster management.",
        "keywords": ["Kubernetes", "K8s", "container orchestration", "pods", "kubectl", "Helm", "Kubernetes cluster"]
    },
    
    # DevOps
    "cicd": {
        "name": "CI/CD DevOps",
        "domain": "digital_technology",
        "description": "Building CI/CD pipelines for automated software deployment using Jenkins, GitHub Actions, GitLab CI, or Azure DevOps.",
        "keywords": ["CI/CD", "continuous integration", "continuous deployment", "pipeline", "Jenkins", "GitLab CI", "GitHub Actions"]
    },
    "infrastructure_code": {
        "name": "Infrastructure as Code",
        "domain": "digital_technology",
        "description": "Managing infrastructure as code using Terraform, CloudFormation, Ansible, or Pulumi for automated infrastructure provisioning.",
        "keywords": ["infrastructure as code", "IaC", "Terraform", "Ansible", "Puppet", "Chef", "CloudFormation"]
    },
    "git_version_control": {
        "name": "Version Control",
        "domain": "digital_technology",
        "description": "Using Git for source code version control including branching strategies, merging, pull requests, and repository management.",
        "keywords": ["Git", "version control", "GitHub", "GitLab", "Bitbucket", "branching", "merge", "pull request", "repository"]
    },
    
    # Networking
    "network_administration": {
        "name": "Network Administration",
        "domain": "digital_technology",
        "description": "Managing computer networks including routers, switches, firewalls, VLANs, and network infrastructure configuration.",
        "keywords": ["network administration", "networking", "router", "switch", "LAN", "WAN", "network configuration", "TCP/IP", "VLAN"]
    },
    "network_security": {
        "name": "Network Security",
        "domain": "digital_technology",
        "description": "Securing IT networks using firewalls, intrusion detection systems, VPNs, and network security protocols and monitoring.",
        "keywords": ["network security", "firewall", "VPN", "intrusion detection", "network protection", "security appliance"]
    },
    "wireless_networking": {
        "name": "Wireless Networking",
        "domain": "digital_technology",
        "description": "Configuring and managing wireless networks including WiFi access points, controllers, and wireless security protocols.",
        "keywords": ["wireless", "WiFi", "wireless network", "access point", "wireless security", "802.11", "wireless configuration"]
    },
    
    # Systems Administration
    "windows_server": {
        "name": "Windows Server Administration",
        "domain": "digital_technology",
        "description": "Administering Windows Server environments including Active Directory, Group Policy, IIS, and Windows system management.",
        "keywords": ["Windows Server", "Active Directory", "AD", "Group Policy", "Windows administration", "WSUS", "DNS", "DHCP"]
    },
    "linux_administration": {
        "name": "Linux Administration",
        "domain": "digital_technology",
        "description": "Managing Linux servers including installation, configuration, shell scripting, package management, and system maintenance.",
        "keywords": ["Linux", "Linux administration", "Ubuntu", "CentOS", "RHEL", "bash", "shell", "Linux server"]
    },
    "virtualisation": {
        "name": "Virtualisation Technology",
        "domain": "digital_technology",
        "description": "Managing virtual machines and hypervisors using VMware, Hyper-V, or similar platforms for server consolidation and virtualisation.",
        "keywords": ["virtualisation", "virtualization", "VMware", "Hyper-V", "virtual machine", "VM", "ESXi", "vSphere"]
    },
    
    # Cybersecurity
    "security_operations": {
        "name": "Security Operations",
        "domain": "digital_technology",
        "description": "Monitoring and responding to security incidents in a Security Operations Centre including SIEM, threat detection, and incident response.",
        "keywords": ["security operations", "SOC", "SIEM", "security monitoring", "incident response", "threat detection", "security analyst"]
    },
    "penetration_testing": {
        "name": "Penetration Testing",
        "domain": "digital_technology",
        "description": "Ethical hacking and security vulnerability assessment of IT systems, networks, and web applications using Kali Linux and similar tools.",
        "keywords": ["penetration testing", "pen testing", "ethical hacking", "vulnerability assessment", "security testing", "Kali Linux"]
    },
    "security_compliance": {
        "name": "Security Compliance",
        "domain": "digital_technology",
        "description": "Ensuring IT systems comply with security standards and regulations including ISO 27001, SOC 2, PCI-DSS, and security audits.",
        "keywords": ["security compliance", "ISO 27001", "security audit", "compliance", "security framework", "NIST", "security policy"]
    },
    
    # IT Support
    "desktop_support": {
        "name": "Desktop Support",
        "domain": "digital_technology",
        "description": "Supporting end-user computing devices including PCs, laptops, printers, and desktop software installation and configuration.",
        "keywords": ["desktop support", "end user support", "PC support", "computer support", "workstation", "Windows support", "Mac support"]
    },
    "helpdesk": {
        "name": "IT Service Desk",
        "domain": "digital_technology",
        "description": "Providing first-line IT support to end users including troubleshooting hardware, software, and network connectivity issues.",
        "keywords": ["helpdesk", "help desk", "service desk", "IT support", "ticketing", "IT helpdesk", "user support", "ITIL"]
    },
    "hardware_support": {
        "name": "Hardware Support",
        "domain": "digital_technology",
        "description": "Repairing and maintaining computer hardware including desktops, laptops, servers, and peripheral device troubleshooting.",
        "keywords": ["hardware support", "hardware repair", "PC repair", "laptop repair", "computer repair", "hardware troubleshooting"]
    },
    "software_installation": {
        "name": "Software Configuration",
        "domain": "digital_technology",
        "description": "Installing and configuring software applications including deployment, licensing, updates, and troubleshooting",
        "keywords": ["software installation", "software deployment", "software configuration", "application installation", "software setup"]
    },
    
    # Design
    "ui_design": {
        "name": "UI Design",
        "domain": "digital_technology",
        "description": "Designing visual user interfaces for websites and applications including layouts, typography, icons, and interactive elements.",
        "keywords": ["UI design", "user interface", "interface design", "Figma", "Sketch", "Adobe XD", "UI", "visual design"]
    },
    "ux_design": {
        "name": "UX Design Research",
        "domain": "digital_technology",
        "description": "Designing user experiences for digital products including user research, wireframing, prototyping, and usability testing of websites and apps.",
        "keywords": ["UX design", "user experience", "UX research", "usability", "wireframing", "prototyping", "user testing"]
    },
    "graphic_design_digital": {
        "name": "Digital Design",
        "domain": "digital_technology",
        "description": "Creating digital graphics including web graphics, social media visuals, and digital marketing assets",
        "keywords": ["graphic design", "digital design", "Photoshop", "Illustrator", "visual design", "digital graphics", "banner design"]
    },
    
    # Other
    "software_testing": {
        "name": "Software Testing QA",
        "domain": "digital_technology",
        "description": "Testing software applications including functional, regression, and automated testing using tools like Selenium. Excludes industrial equipment testing.",
        "keywords": ["software testing", "QA", "quality assurance", "test automation", "Selenium", "test cases", "bug testing", "regression testing"]
    },
    "technical_documentation": {
        "name": "Technical Writing",
        "domain": "digital_technology",
        "description": "Writing technical documentation including user guides, API documentation, system specifications, and technical manuals for software products.",
        "keywords": ["technical documentation", "technical writing", "documentation", "user manual", "API documentation", "knowledge base"]
    },
    "game_development": {
        "name": "Game Development",
        "domain": "digital_technology",
        "description": "Creating video games using game engines like Unity or Unreal Engine including game mechanics, graphics, and gameplay programming.",
        "keywords": ["game development", "Unity", "Unreal Engine", "game programming", "game design", "game engine", "C# game"]
    },
    "blockchain_development": {
        "name": "Blockchain Development",
        "domain": "digital_technology",
        "description": "Developing blockchain applications and smart contracts using Solidity, Ethereum, or other distributed ledger technologies.",
        "keywords": ["blockchain", "smart contract", "Solidity", "Ethereum", "Web3", "cryptocurrency", "DeFi", "NFT"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HEALTHCARE & COMMUNITY SERVICES (75 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Nursing - Acute Care
    "emergency_nursing": {
        "name": "Emergency Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care in emergency departments including triage, trauma, and acute patient assessment.",
        "keywords": ["emergency nursing", "ED nursing", "emergency department", "triage", "trauma nursing", "emergency care", "resuscitation"]
    },
    "intensive_care_nursing": {
        "name": "Intensive Care Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care in intensive care units including ventilated patients, haemodynamic monitoring, and critical care.",
        "keywords": ["intensive care", "ICU nursing", "critical care", "ICU", "ventilator", "critical care nursing", "high dependency"]
    },
    "surgical_nursing": {
        "name": "Surgical Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for surgical patients including perioperative care, wound management, and post-operative recovery.",
        "keywords": ["surgical nursing", "perioperative", "post-operative", "surgical ward", "pre-operative", "surgical care"]
    },
    "medical_nursing": {
        "name": "Medical Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care on medical wards including medication administration, patient observations, and care planning.",
        "keywords": ["medical nursing", "medical ward", "general nursing", "ward nursing", "medical care", "inpatient nursing"]
    },
    "oncology_nursing": {
        "name": "Oncology Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for cancer patients including chemotherapy administration, symptom management, and palliative care.",
        "keywords": ["oncology nursing", "cancer care", "chemotherapy", "oncology", "cancer nursing", "palliative", "radiation therapy"]
    },
    "cardiac_nursing": {
        "name": "Cardiac Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for cardiac patients including ECG monitoring, cardiac rehabilitation, and coronary care.",
        "keywords": ["cardiac nursing", "cardiology", "CCU", "cardiac care", "heart failure", "ECG", "cardiac monitoring"]
    },
    "renal_nursing": {
        "name": "Renal Dialysis Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for patients with kidney disease including haemodialysis, peritoneal dialysis, and renal patient education.",
        "keywords": ["renal nursing", "dialysis", "haemodialysis", "peritoneal dialysis", "kidney", "nephrology", "renal care"]
    },
    "paediatric_nursing": {
        "name": "Paediatric Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for human children in hospitals including sick children, paediatric procedures, and family-centred care.",
        "keywords": ['paediatric', 'pediatric', "children's hospital", 'sick children', 'child nursing', 'human children', 'paeds', "children's ward"]
    },
    "neonatal_nursing": {
        "name": "Neonatal Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for human newborns and premature babies in neonatal intensive care and special care nurseries.",
        "keywords": ['neonatal', 'NICU', 'newborn', 'premature', 'special care nursery', 'human babies', 'neonate', 'premmie']
    },
    
    # Nursing - Community & Specialty
    "community_nursing": {
        "name": "Community Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care in community settings including home visits, wound care, and chronic disease management.",
        "keywords": ["community nursing", "district nursing", "home nursing", "community health", "visiting nurse", "outreach nursing"]
    },
    "mental_health_nursing": {
        "name": "Mental Health Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for mental health patients including psychiatric assessment, therapeutic interventions, and mental health care.",
        "keywords": ["mental health nursing", "psychiatric nursing", "psych nursing", "mental health care", "psychiatric care", "inpatient psych"]
    },
    "aged_care_nursing": {
        "name": "Aged Care Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for elderly human residents in aged care facilities including medications, clinical care, and end-of-life support.",
        "keywords": ['aged care', 'nursing home', 'elderly', 'geriatric', 'residential aged care', 'human elderly', 'aged care nursing', 'dementia nursing']
    },
    "wound_care": {
        "name": "Wound Care Management",
        "domain": "healthcare_clinical",
        "description": "Assessing and treating patient wounds in clinical settings including wound dressings, pressure injury assessment, wound healing management, and clinical wound care.",
        "keywords": ['wound care', 'wound dressing', 'wound assessment', 'pressure injury', 'wound healing', 'clinical wound care', 'wound management', 'patient wounds']
    },
    "medication_administration": {
        "name": "Medication Administration",
        "domain": "healthcare_clinical",
        "description": "Administering medications to human patients safely including oral, injection, IV medications, drug calculations, and medication safety protocols in healthcare settings.",
        "keywords": ['medication', 'drug administration', 'IV', 'injection', 'oral medication', 'drug calculation', 'medication safety', 'human patient', 'nursing medication']
    },
    "infection_control": {
        "name": "Infection Control",
        "domain": "healthcare_clinical",
        "description": "Implementing infection prevention and control measures including hand hygiene, PPE, and infection surveillance.",
        "keywords": ["infection control", "infection prevention", "hand hygiene", "PPE", "isolation", "sterilisation", "aseptic technique"]
    },
    "clinical_observations": {
        "name": "Clinical Observations",
        "domain": "healthcare_clinical",
        "description": "Taking and recording patient vital signs in hospitals and clinics including blood pressure, temperature, pulse, respiration, and oxygen saturation for human patients.",
        "keywords": ['vital signs', 'observations', 'blood pressure', 'temperature', 'pulse', 'respiration', 'SpO2', 'clinical obs', 'patient monitoring', 'nursing observations', 'human patient']
    },
    
    # Allied Health
    "physiotherapy": {
        "name": "Physiotherapy Services",
        "domain": "healthcare_clinical",
        "description": "Providing physiotherapy treatment including exercise prescription, manual therapy, and rehabilitation programs.",
        "keywords": ["physiotherapy", "physical therapy", "physio", "rehabilitation", "exercise therapy", "manual therapy", "mobility"]
    },
    "occupational_therapy": {
        "name": "Occupational Therapy",
        "domain": "healthcare_clinical",
        "description": "Providing occupational therapy including activities of daily living assessment, equipment prescription, and rehabilitation.",
        "keywords": ["occupational therapy", "OT", "ADL", "activities of daily living", "functional assessment", "home modifications"]
    },
    "speech_pathology": {
        "name": "Speech Pathology",
        "domain": "healthcare_clinical",
        "description": "Providing speech pathology services including communication disorders, swallowing assessment, and speech therapy.",
        "keywords": ["speech pathology", "speech therapy", "speech language", "swallowing", "dysphagia", "communication disorder", "stuttering"]
    },
    "dietetics": {
        "name": "Dietetics Clinical Nutrition",
        "domain": "healthcare_clinical",
        "description": "Providing dietetic services for human patients including nutritional assessment, therapeutic diets, enteral feeding, tube feeding, and clinical nutrition counselling.",
        "keywords": ['dietetics', 'dietitian', 'clinical nutrition', 'therapeutic diet', 'enteral feeding', 'tube feeding', 'nutritional assessment', 'human nutrition', 'patient diet']
    },
    "podiatry": {
        "name": "Podiatry Services",
        "domain": "healthcare_clinical",
        "description": "Providing podiatry services including foot assessment, nail care, orthotics, and diabetic foot care.",
        "keywords": ["podiatry", "podiatrist", "foot care", "diabetic foot", "orthotic", "nail care", "foot assessment"]
    },
    "audiology": {
        "name": "Audiology Services",
        "domain": "healthcare_clinical",
        "description": "Providing audiology services including hearing assessment, hearing aids, and audiological rehabilitation.",
        "keywords": ["audiology", "hearing", "audiologist", "hearing test", "hearing aid", "audiometry", "cochlear implant"]
    },
    "optometry": {
        "name": "Optometry Services",
        "domain": "healthcare_clinical",
        "description": "Providing optometry services including eye examinations, vision testing, and optical prescriptions.",
        "keywords": ["optometry", "optometrist", "eye test", "vision", "glasses", "contact lenses", "eye examination"]
    },
    "exercise_physiology": {
        "name": "Exercise Physiology",
        "domain": "healthcare_clinical",
        "description": "Providing exercise physiology services including exercise prescription for chronic conditions and rehabilitation.",
        "keywords": ["exercise physiology", "exercise physiologist", "clinical exercise", "exercise prescription", "cardiac rehab", "exercise therapy"]
    },
    
    # Medical Support
    "medical_reception": {
        "name": "Medical Reception",
        "domain": "healthcare_clinical",
        "description": "Providing reception services in medical practices including appointments, billing, and patient administration.",
        "keywords": ["medical reception", "medical receptionist", "practice reception", "patient booking", "medical admin", "appointment scheduling"]
    },
    "medical_records": {
        "name": "Health Information Management",
        "domain": "healthcare_clinical",
        "description": "Managing health information and medical records including clinical coding, documentation, and health data",
        "keywords": ["medical records", "health records", "patient records", "medical documentation", "health information", "medical filing"]
    },
    "medical_billing": {
        "name": "Medical Billing Coding",
        "domain": "healthcare_clinical",
        "description": "Processing medical billing including Medicare, health fund claims, and medical accounts.",
        "keywords": ["medical billing", "medical coding", "ICD-10", "Medicare billing", "health insurance claims", "coding", "billing"]
    },
    "pathology_collection": {
        "name": "Pathology Collection",
        "domain": "healthcare_clinical",
        "description": "Collecting pathology specimens including venepuncture, blood collection, and specimen handling.",
        "keywords": ["pathology collection", "blood collection", "phlebotomy", "venepuncture", "specimen collection", "blood draw"]
    },
    "medical_imaging_assistance": {
        "name": "Medical Imaging Assistance",
        "domain": "healthcare_clinical",
        "description": "Assisting with medical imaging procedures including patient positioning, radiography, and imaging support",
        "keywords": ["medical imaging", "radiology", "X-ray", "imaging assistant", "radiography", "CT scan", "MRI"]
    },
    "sterilisation_services": {
        "name": "Sterilisation Services",
        "domain": "healthcare_clinical",
        "description": "Sterilising medical instruments and equipment in hospitals including CSSD operations, autoclave operation, instrument processing, and infection control sterilisation.",
        "keywords": ['sterilisation', 'CSSD', 'sterile processing', 'autoclave', 'instrument sterilisation', 'medical sterilisation', 'infection control', 'sterile supplies', 'hospital sterilisation']
    },
    
    # Pharmacy
    "pharmacy_dispensing": {
        "name": "Pharmacy Dispensing",
        "domain": "healthcare_clinical",
        "description": "Dispensing medications in pharmacies including prescription processing, patient counselling, and medication management.",
        "keywords": ["pharmacy dispensing", "dispensary", "prescription", "medication dispensing", "pharmacy", "dispensing technician"]
    },
    "pharmacy_retail": {
        "name": "Community Pharmacy",
        "domain": "healthcare_clinical",
        "description": "Working in community pharmacies including dispensing, OTC sales, health advice, and retail operations",
        "keywords": ["pharmacy retail", "community pharmacy", "chemist", "OTC", "pharmacy sales", "front shop", "pharmacy customer service"]
    },
    "hospital_pharmacy": {
        "name": "Hospital Pharmacy",
        "domain": "healthcare_clinical",
        "description": "Working in hospital pharmacies including clinical pharmacy, drug distribution, and pharmacy services.",
        "keywords": ["hospital pharmacy", "clinical pharmacy", "ward pharmacy", "medication review", "hospital dispensary"]
    },
    
    # Dental
    "dental_assisting": {
        "name": "Dental Assisting",
        "domain": "healthcare_clinical",
        "description": "Assisting dentists during procedures including chairside assistance, instrument preparation, and patient care.",
        "keywords": ["dental assistant", "dental assisting", "chairside", "dental nurse", "dental surgery", "dental instruments"]
    },
    "dental_radiography": {
        "name": "Dental Radiography",
        "domain": "healthcare_clinical",
        "description": "Taking dental x-rays including intraoral and extraoral radiography and radiation safety.",
        "keywords": ["dental radiography", "dental X-ray", "dental imaging", "OPG", "periapical", "bitewing"]
    },
    "dental_hygiene": {
        "name": "Dental Hygiene",
        "domain": "healthcare_clinical",
        "description": "Providing dental hygiene services for human patients including scaling, prophylaxis, professional teeth cleaning, preventive care, and oral health education.",
        "keywords": ['dental hygiene', 'dental hygienist', 'scaling', 'prophylaxis', 'teeth cleaning', 'oral hygiene', 'preventive dental', 'dental cleaning', 'human dental care']
    },
    "dental_prosthetics": {
        "name": "Dental Prosthetics",
        "domain": "healthcare_clinical",
        "description": "Manufacturing dental prosthetics including dentures, crowns, and dental laboratory work.",
        "keywords": ["dental prosthetics", "dentures", "dental technician", "dental lab", "crown", "bridge", "dental prosthesis"]
    },
    
    # Mental Health
    "mental_health_support": {
        "name": "Mental Health Support",
        "domain": "community_services",
        "description": "Providing mental health support work including recovery support, psychosocial support, and mental health programs.",
        "keywords": ["mental health support", "mental health worker", "recovery support", "psychosocial support", "mental health care"]
    },
    "counselling": {
        "name": "Counselling Services",
        "domain": "community_services",
        "description": "Providing counselling services including individual counselling, therapy, and mental health support.",
        "keywords": ["counselling", "counselor", "therapy", "talk therapy", "psychotherapy", "therapeutic counselling"]
    },
    "drug_alcohol_support": {
        "name": "AOD Support",
        "domain": "community_services",
        "description": "Supporting people with alcohol and drug issues including AOD counselling, harm reduction, and recovery programs",
        "keywords": ["drug and alcohol", "AOD", "substance abuse", "addiction", "detox", "rehabilitation", "drug counselling"]
    },
    "crisis_intervention": {
        "name": "Crisis Intervention",
        "domain": "community_services",
        "description": "Providing crisis support for people in mental health or personal crisis including crisis counselling, suicide prevention, safety planning, and emergency mental health response.",
        "keywords": ['crisis intervention', 'crisis support', 'crisis counselling', 'suicide prevention', 'mental health crisis', 'safety planning', 'crisis response', 'emergency support']
    },
    
    # Aged Care
    "personal_care": {
        "name": "Personal Care Support",
        "domain": "community_services",
        "description": "Providing personal care support for human clients including bathing, dressing, toileting, grooming, and daily living assistance.",
        "keywords": ['personal care', 'ADL', 'bathing', 'showering', 'dressing', 'toileting', 'human personal care', 'daily living', 'personal support']
    },
    "mobility_assistance": {
        "name": "Mobility Assistance",
        "domain": "community_services",
        "description": "Assisting with mobility including transfers, walking support, wheelchair assistance, and mobility aids.",
        "keywords": ["mobility assistance", "transfer", "hoisting", "mobility aid", "walking frame", "wheelchair", "mobility support"]
    },
    "dementia_care": {
        "name": "Dementia Care",
        "domain": "community_services",
        "description": "Providing care for human clients with dementia including memory support, behavior management, and specialized dementia care techniques.",
        "keywords": ['dementia', 'dementia care', 'memory support', "Alzheimer's", 'dementia support', 'human dementia', 'cognitive impairment', 'dementia behaviour']
    },
    "palliative_care": {
        "name": "Palliative Care",
        "domain": "community_services",
        "description": "Providing palliative and end-of-life care for terminally ill patients including comfort care, pain management, and family support in hospice or aged care settings.",
        "keywords": ['palliative care', 'end of life', 'hospice', 'terminal care', 'comfort care', 'dying patient', 'palliative nursing', 'hospice care']
    },
    "meal_assistance": {
        "name": "Meal Assistance",
        "domain": "community_services",
        "description": "Assisting human clients with meals including food preparation, feeding assistance, and nutrition support for aged care or disability clients. Not animal feeding.",
        "keywords": ['meal assistance', 'feeding assistance', 'food preparation', 'nutrition support', 'human clients', 'aged care meals', 'disability meals', 'mealtime support']
    },
    "lifestyle_activities": {
        "name": "Lifestyle Recreation Support",
        "domain": "community_services",
        "description": "Facilitating recreational activities for aged care or disability clients including social programs and leisure activities",
        "keywords": ["lifestyle", "activities", "recreation", "diversional therapy", "aged care activities", "leisure", "social activities"]
    },
    
    # Disability
    "disability_support": {
        "name": "Disability Support",
        "domain": "community_services",
        "description": "Supporting people with disability in daily activities including personal care, community access, skill development, and NDIS support work. Human clients only.",
        "keywords": ['disability', 'disability support', 'NDIS', 'disability worker', 'support worker', 'human disability', 'disability care', 'DSW', 'community access']
    },
    "community_participation": {
        "name": "Community Participation Support",
        "domain": "community_services",
        "description": "Supporting community participation including social activities, outings, and community access.",
        "keywords": ["community participation", "community access", "social participation", "community inclusion", "outings", "day program"]
    },
    "supported_independent_living": {
        "name": "Supported Independent Living",
        "domain": "community_services",
        "description": "Supporting people with disability to live independently in their own homes including daily living skills, household tasks, and NDIS SIL support.",
        "keywords": ['SIL', 'supported independent living', 'disability housing', 'independent living', 'NDIS housing', 'daily living support', 'disability support']
    },
    "behaviour_support": {
        "name": "Behaviour Support",
        "domain": "community_services",
        "description": "Implementing positive behaviour support for human clients with disability including behaviour plans, strategies, and PBS approaches.",
        "keywords": ['behaviour support', 'PBS', 'positive behaviour', 'behaviour plan', 'human behaviour', 'behaviour management', 'restrictive practices', 'behaviour intervention']
    },
    "assistive_technology": {
        "name": "Assistive Technology",
        "domain": "community_services",
        "description": "Supporting use of assistive technology including mobility aids, communication devices, and adaptive equipment.",
        "keywords": ["assistive technology", "AT", "adaptive equipment", "mobility equipment", "communication device", "AAC"]
    },
    
    # Community Services
    "case_management": {
        "name": "Case Management",
        "domain": "community_services",
        "description": "Coordinating human services for clients with complex needs including social work case coordination, client needs assessment, service referrals, and welfare case management.",
        "keywords": ['case management', 'case manager', 'care coordination', 'social work', 'client services', 'service coordination', 'welfare', 'case work', 'human services', 'client needs']
    },
    "child_protection": {
        "name": "Child Protection",
        "domain": "community_services",
        "description": "Working in child protection services for human children including child safety assessment, case work, and family intervention.",
        "keywords": ['child protection', 'child safety', 'human children', 'child welfare', 'child abuse', 'protective services', 'mandatory reporting']
    },
    "youth_work": {
        "name": "Youth Work",
        "domain": "community_services",
        "description": "Working with young people (human adolescents) including youth programs, engagement, support services, and youth development.",
        "keywords": ['youth work', 'youth services', 'young people', 'human youth', 'adolescent', 'youth worker', 'youth program', 'teen']
    },
    "family_support": {
        "name": "Family Support Services",
        "domain": "community_services",
        "description": "Providing support services for human families including parenting support, family intervention, and family counselling services.",
        "keywords": ['family support', 'parenting', 'family services', 'human families', 'family intervention', 'parent support', 'family counselling']
    },
    "housing_support": {
        "name": "Housing Support",
        "domain": "community_services",
        "description": "Providing housing support for homeless or at-risk people including crisis accommodation, tenancy support, social housing, and homelessness services.",
        "keywords": ['housing support', 'homelessness', 'crisis accommodation', 'social housing', 'tenancy support', 'housing assistance', 'homeless services']
    },
    "domestic_violence_support": {
        "name": "Family Violence Support",
        "domain": "community_services",
        "description": "Supporting victims of domestic and family violence including crisis intervention, safety planning, and advocacy",
        "keywords": ["domestic violence", "DV support", "family violence", "DFV", "women's refuge", "domestic abuse", "safety planning"]
    },
    "community_development": {
        "name": "Community Development",
        "domain": "community_services",
        "description": "Facilitating community development including community programs, engagement, and capacity building.",
        "keywords": ["community development", "community engagement", "capacity building", "community program", "community worker", "grassroots"]
    },
    "volunteer_management": {
        "name": "Volunteer Management",
        "domain": "community_services",
        "description": "Coordinating volunteers including recruitment, training, and volunteer program management.",
        "keywords": ["volunteer management", "volunteer coordinator", "volunteer program", "volunteer recruitment", "volunteering"]
    },
    
    # First Aid & Emergency
    "first_aid": {
        "name": "First Aid",
        "domain": "healthcare_clinical",
        "description": "Providing first aid and basic life support for human emergencies including CPR, bleeding control, burns, fractures, and emergency first response in workplace or community settings.",
        "keywords": ['first aid', 'CPR', 'basic life support', 'emergency response', 'first responder', 'HLTAID', 'human first aid', 'workplace first aid', 'bleeding control']
    },
    "advanced_life_support": {
        "name": "Advanced Life Support",
        "domain": "healthcare_clinical",
        "description": "Providing advanced resuscitation including ACLS, ALS, airway management, and emergency cardiac care.",
        "keywords": ["advanced life support", "ALS", "ACLS", "advanced resuscitation", "defibrillation", "intubation", "cardiac arrest"]
    },
    
    # Indigenous Health
    "aboriginal_health": {
        "name": "Aboriginal Health",
        "domain": "healthcare_clinical",
        "description": "Working in Aboriginal and Torres Strait Islander health services including cultural safety and Indigenous health programs.",
        "keywords": ["Aboriginal health", "Indigenous health", "Aboriginal health worker", "First Nations health", "cultural safety", "ATSI health"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # BUSINESS, FINANCE & ADMINISTRATION (65 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Accounting
    "accounts_payable": {
        "name": "Accounts Payable",
        "domain": "finance_accounting",
        "description": "Processing accounts payable including supplier invoices, payment runs, reconciliations, and creditor management",
        "keywords": ["accounts payable", "AP", "creditors", "supplier payments", "invoice processing", "payment run", "vendor payments"]
    },
    "accounts_receivable": {
        "name": "Accounts Receivable",
        "domain": "finance_accounting",
        "description": "Managing accounts receivable including customer invoicing, payment collection, and debtor follow-up",
        "keywords": ["accounts receivable", "AR", "debtors", "invoicing", "collections", "customer billing", "receivables"]
    },
    "bookkeeping": {
        "name": "Bookkeeping Services",
        "domain": "finance_accounting",
        "description": "Maintaining financial records including transaction entry, bank reconciliation, and general ledger management",
        "keywords": ["bookkeeping", "bookkeeper", "ledger", "journal entries", "bank reconciliation", "financial records", "Xero", "MYOB", "QuickBooks"]
    },
    "payroll_processing": {
        "name": "Payroll Processing",
        "domain": "finance_accounting",
        "description": "Processing payroll including wages, superannuation, tax, and payroll compliance.",
        "keywords": ["payroll", "payroll processing", "wages", "salary", "payslip", "superannuation", "PAYG", "STP", "payroll officer"]
    },
    "bas_gst": {
        "name": "BAS GST Lodgement",
        "domain": "finance_accounting",
        "description": "Preparing and lodging Business Activity Statements including GST calculations, PAYG, and ATO compliance",
        "keywords": ["BAS", "GST", "Business Activity Statement", "tax lodgement", "GST return", "BAS agent", "quarterly BAS"]
    },
    "financial_reporting": {
        "name": "Financial Reporting",
        "domain": "finance_accounting",
        "description": "Preparing financial reports and statements including balance sheets, profit and loss, and management reports",
        "keywords": ["financial reporting", "financial statements", "profit and loss", "balance sheet", "cash flow", "management accounts"]
    },
    "budget_management": {
        "name": "Budget Management",
        "domain": "finance_accounting",
        "description": "Managing budgets including budget preparation, forecasting, variance analysis, and financial planning",
        "keywords": ["budget", "budgeting", "budget management", "forecasting", "financial planning", "variance analysis", "budget preparation"]
    },
    "taxation": {
        "name": "Taxation Compliance",
        "domain": "finance_accounting",
        "description": "Preparing income tax returns and ensuring tax compliance including individual tax, company tax, FBT, GST obligations, and ATO lodgements. Taxation and tax accounting only.",
        "keywords": ['taxation', 'tax return', 'income tax', 'company tax', 'FBT', 'GST', 'ATO', 'tax compliance', 'tax accountant', 'tax lodgement']
    },
    "audit": {
        "name": "Financial Auditing",
        "domain": "finance_accounting",
        "description": "Conducting financial audits of company accounts including statutory audits, compliance audits, internal financial audits, and accounting standards verification. Financial auditing only.",
        "keywords": ['financial audit', 'statutory audit', 'internal audit', 'compliance audit', 'audit procedures', 'auditor', 'accounting audit', 'financial statements audit']
    },
    "management_accounting": {
        "name": "Management Accounting",
        "domain": "finance_accounting",
        "description": "Providing management accounting including cost accounting, budgeting, and financial decision support",
        "keywords": ["management accounting", "cost accounting", "costing", "cost analysis", "management reporting", "cost centre"]
    },
    
    # Banking & Finance
    "bank_teller": {
        "name": "Bank Teller Operations",
        "domain": "finance_accounting",
        "description": "Processing bank transactions at the counter including deposits, withdrawals, and customer service",
        "keywords": ["bank teller", "teller", "banking", "cash handling", "bank transactions", "customer banking", "bank deposits"]
    },
    "lending": {
        "name": "Lending Credit",
        "domain": "finance_accounting",
        "description": "Processing bank loans and mortgages including borrower creditworthiness assessment, home loan applications, personal loan documentation, and banking lending compliance. Financial lending only.",
        "keywords": ['lending', 'loans', 'credit', 'loan processing', 'mortgage', 'home loan', 'personal loan', 'borrower assessment', 'bank lending', 'financial lending', 'loan application', 'creditworthiness']
    },
    "financial_planning": {
        "name": "Financial Planning",
        "domain": "finance_accounting",
        "description": "Advising clients on personal finances and wealth including investment portfolios, superannuation strategies, retirement planning, and financial wealth management. Personal finance advisory.",
        "keywords": ['financial planning', 'financial advice', 'wealth management', 'investment advice', 'retirement planning', 'superannuation', 'financial planner', 'wealth advisory', 'portfolio management']
    },
    "insurance_broking": {
        "name": "Insurance Broking",
        "domain": "finance_accounting",
        "description": "Selling and advising on insurance policies including policy comparison, premium quotes, insurance placement, and insurance broker services. Insurance sales only.",
        "keywords": ['insurance broking', 'insurance sales', 'insurance broker', 'policy placement', 'premium quotes', 'insurance advice', 'insurance products', 'policy comparison']
    },
    "claims_processing": {
        "name": "Insurance Claims Processing",
        "domain": "finance_accounting",
        "description": "Processing insurance claims in insurance companies including policyholder claim lodgement, loss assessment, claim investigation, and insurance claim settlement. Insurance industry only.",
        "keywords": ['insurance claims', 'claims processing', 'claims handler', 'claim lodgement', 'insurance assessment', 'policy claim', 'loss adjuster', 'claim settlement', 'insurance payout']
    },
    "superannuation": {
        "name": "Superannuation Administration",
        "domain": "finance_accounting",
        "description": "Administering superannuation funds including contributions, member services, and super compliance",
        "keywords": ["superannuation", "super", "SMSF", "super fund", "superannuation administration", "member services", "super contributions"]
    },
    
    # Administration
    "reception": {
        "name": "Front Desk Reception",
        "domain": "business_administration",
        "description": "Providing front desk reception services including greeting visitors, answering phones, and administrative support",
        "keywords": ["reception", "receptionist", "front desk", "greeting visitors", "switchboard", "front of house", "visitor management"]
    },
    "data_entry": {
        "name": "Data Entry",
        "domain": "business_administration",
        "description": "Entering data into systems including data input, data verification, and database entry.",
        "keywords": ["data entry", "data input", "keyboarding", "typing", "data processing", "data capture", "alpha-numeric entry"]
    },
    "word_processing": {
        "name": "Document Processing",
        "domain": "business_administration",
        "description": "Creating and formatting documents using word processing software including reports, letters, and correspondence",
        "keywords": ["word processing", "Microsoft Word", "document formatting", "typing", "correspondence", "document preparation", "letter writing"]
    },
    "spreadsheets": {
        "name": "Spreadsheet Analysis",
        "domain": "business_administration",
        "description": "Working with spreadsheets including data entry, formulas, pivot tables, and data analysis using Excel",
        "keywords": ["spreadsheet", "Excel", "Microsoft Excel", "formulas", "pivot table", "VLOOKUP", "spreadsheet analysis", "Excel functions"]
    },
    "diary_calendar": {
        "name": "Calendar Management",
        "domain": "business_administration",
        "description": "Managing executive schedules and office calendars including appointment booking, meeting scheduling, and corporate diary management for business executives.",
        "keywords": ['diary management', 'calendar management', 'scheduling', 'appointments', 'executive diary', 'meeting scheduling', 'office calendar', 'corporate calendar']
    },
    "travel_booking": {
        "name": "Travel Coordination",
        "domain": "business_administration",
        "description": "Arranging business travel including flights, accommodation, car hire, and travel itinerary coordination",
        "keywords": ["travel booking", "travel coordination", "flights", "accommodation booking", "itinerary", "business travel", "travel arrangements"]
    },
    "meeting_coordination": {
        "name": "Meeting Coordination",
        "domain": "business_administration",
        "description": "Coordinating corporate meetings and boardroom bookings including agenda preparation, room booking, minute taking, and business meeting logistics.",
        "keywords": ['meeting coordination', 'boardroom booking', 'agenda', 'meeting minutes', 'corporate meetings', 'business meetings', 'meeting logistics']
    },
    "filing_records": {
        "name": "Records Management",
        "domain": "business_administration",
        "description": "Managing office files and corporate records including paper filing, electronic document management, archiving, and records retention compliance.",
        "keywords": ['records management', 'filing', 'document management', 'archiving', 'record keeping', 'document control', 'office files', 'corporate records']
    },
    "executive_assistant": {
        "name": "Executive Assistance",
        "domain": "business_administration",
        "description": "Supporting C-suite executives and senior managers in corporations including executive diary management, board papers, correspondence, and high-level corporate administration.",
        "keywords": ['executive assistant', 'EA', 'PA', 'executive support', 'C-suite support', 'board papers', 'executive administration', 'senior management support']
    },
    "mail_handling": {
        "name": "Mail Handling",
        "domain": "business_administration",
        "description": "Handling mail and courier services including incoming mail, outgoing mail, and deliveries.",
        "keywords": ["mail handling", "mail room", "courier", "mail distribution", "post", "mail processing", "incoming mail"]
    },
    "office_equipment": {
        "name": "Office Equipment Operation",
        "domain": "business_administration",
        "description": "Operating office equipment including photocopiers, printers, and office machines.",
        "keywords": ["office equipment", "photocopying", "printing", "scanner", "fax", "laminating", "binding", "office machines"]
    },
    
    # HR & Recruitment
    "recruitment": {
        "name": "Recruitment Talent Acquisition",
        "domain": "business_administration",
        "description": "Recruiting staff including job advertising, screening, interviewing, and candidate selection.",
        "keywords": ["recruitment", "recruiting", "hiring", "candidate sourcing", "job advertising", "interviewing", "talent acquisition"]
    },
    "onboarding": {
        "name": "Employee Onboarding",
        "domain": "business_administration",
        "description": "Inducting new employees including orientation programs, paperwork, system access, and initial training",
        "keywords": ["onboarding", "induction", "new employee", "orientation", "employee induction", "new starter", "onboarding process"]
    },
    "hr_administration": {
        "name": "HR Administration",
        "domain": "business_administration",
        "description": "Administering HR functions including employee records, HR systems, and HR documentation.",
        "keywords": ["HR administration", "HR admin", "personnel", "employee records", "HR systems", "HRIS", "HR documentation"]
    },
    "performance_management": {
        "name": "Performance Management",
        "domain": "business_administration",
        "description": "Managing employee workplace performance including staff appraisals, KPI setting, performance reviews, and HR performance management in organisations.",
        "keywords": ['performance management', 'performance review', 'staff appraisal', 'KPIs', 'employee performance', 'HR performance', 'goal setting', 'performance appraisal', 'workplace performance']
    },
    "employee_relations": {
        "name": "Employee Relations",
        "domain": "business_administration",
        "description": "Managing employee relations including workplace issues, grievances, and industrial relations.",
        "keywords": ["employee relations", "workplace relations", "grievance", "disciplinary", "industrial relations", "ER", "workplace dispute"]
    },
    "whs_compliance": {
        "name": "WHS Compliance",
        "domain": "business_administration",
        "description": "Ensuring workplace health and safety compliance including risk assessment, safety procedures, and WHS systems.",
        "keywords": ["WHS", "work health safety", "OHS", "safety compliance", "workplace safety", "safety officer", "hazard management"]
    },
    "workers_compensation": {
        "name": "Workers Compensation",
        "domain": "business_administration",
        "description": "Managing workers compensation insurance claims including workplace injury claims, return to work programs, WorkCover, and injury management for employees.",
        "keywords": ['workers compensation', 'WorkCover', 'injury management', 'return to work', 'workplace injury', 'workers comp claims', 'RTW', 'injury claims']
    },
    
    # Legal
    "legal_secretary": {
        "name": "Legal Secretarial",
        "domain": "business_administration",
        "description": "Providing secretarial support in legal environments including legal documents, court filings, and law firm administration",
        "keywords": ["legal secretary", "law firm", "legal admin", "legal correspondence", "legal documents", "legal typing"]
    },
    "conveyancing": {
        "name": "Property Conveyancing",
        "domain": "business_administration",
        "description": "Processing property transfers including searches, contracts, settlements, and property law documentation",
        "keywords": ["conveyancing", "property settlement", "conveyancer", "property transfer", "title search", "settlement", "PEXA"]
    },
    "litigation_support": {
        "name": "Litigation Support",
        "domain": "business_administration",
        "description": "Supporting litigation including document management, discovery, and legal research.",
        "keywords": ["litigation", "court", "litigation support", "court documents", "discovery", "legal research", "trial preparation"]
    },
    "contract_administration": {
        "name": "Contract Administration",
        "domain": "business_administration",
        "description": "Administering contracts including contract documentation, compliance, and contract management.",
        "keywords": ["contract administration", "contracts", "contract management", "agreement", "contract review", "contract compliance"]
    },
    
    # Project & Business
    "project_coordination": {
        "name": "Project Coordination",
        "domain": "business_administration",
        "description": "Coordinating corporate project activities including project scheduling, documentation, stakeholder coordination, and project administration support for business projects.",
        "keywords": ['project coordination', 'project support', 'project administration', 'project scheduling', 'project documentation', 'business projects', 'corporate projects']
    },
    "project_management": {
        "name": "Project Management",
        "domain": "business_administration",
        "description": "Managing corporate and IT projects including project planning, schedule management, resource coordination, milestone tracking, and project delivery using methodologies like PRINCE2 or Agile.",
        "keywords": ['project management', 'project manager', 'project planning', 'PRINCE2', 'Agile', 'project delivery', 'milestone', 'Gantt chart', 'project schedule', 'PMO', 'project lifecycle']
    },
    "business_analysis": {
        "name": "Business Analysis",
        "domain": "business_administration",
        "description": "Analysing corporate business requirements and processes including business process mapping, stakeholder requirements gathering, gap analysis, and IT solution design for organisations.",
        "keywords": ['business analysis', 'business analyst', 'requirements gathering', 'process mapping', 'gap analysis', 'BA', 'business requirements', 'stakeholder analysis', 'corporate analysis', 'organisational requirements']
    },
    "change_management": {
        "name": "Change Management",
        "domain": "business_administration",
        "description": "Managing organisational transformation and change programs including change impact assessment, staff communication, adoption planning, and business transformation initiatives.",
        "keywords": ['change management', 'organisational change', 'transformation', 'change program', 'change adoption', 'business transformation', 'change impact', 'transition management']
    },
    "process_improvement": {
        "name": "Process Improvement",
        "domain": "business_administration",
        "description": "Improving corporate business processes using Lean, Six Sigma, or continuous improvement methodologies including workflow optimisation and operational efficiency programs.",
        "keywords": ['process improvement', 'continuous improvement', 'Lean', 'Six Sigma', 'workflow optimisation', 'operational efficiency', 'business process', 'kaizen', 'process reengineering']
    },
    
    # Sales & Marketing
    "sales": {
        "name": "Sales Development",
        "domain": "business_administration",
        "description": "Selling products or services in B2B or B2C environments including prospecting, negotiating, and closing deals",
        "keywords": ["sales", "selling", "sales representative", "account management", "sales targets", "pipeline", "closing", "prospecting"]
    },
    "account_management": {
        "name": "Account Management",
        "domain": "business_administration",
        "description": "Managing client accounts including relationship management, account growth, and client retention.",
        "keywords": ["account management", "account manager", "client management", "customer relationship", "key accounts", "client retention"]
    },
    "marketing": {
        "name": "Marketing Strategy",
        "domain": "business_administration",
        "description": "Developing marketing strategies including campaigns, brand management, market positioning, and marketing planning",
        "keywords": ["marketing", "marketing strategy", "campaign", "brand", "marketing plan", "go-to-market", "marketing manager"]
    },
    "digital_marketing": {
        "name": "Digital Marketing",
        "domain": "business_administration",
        "description": "Executing digital marketing including SEO, SEM, email marketing, and online advertising.",
        "keywords": ["digital marketing", "online marketing", "SEO", "SEM", "Google Ads", "PPC", "content marketing", "email marketing"]
    },
    "social_media_marketing": {
        "name": "Social Media Marketing",
        "domain": "business_administration",
        "description": "Managing social media marketing including content creation, community management, and social campaigns.",
        "keywords": ["social media marketing", "social media", "Facebook", "Instagram", "LinkedIn", "social media management", "content creation"]
    },
    "market_research": {
        "name": "Market Research",
        "domain": "business_administration",
        "description": "Conducting market research including surveys, focus groups, and consumer insights.",
        "keywords": ["market research", "research", "survey", "consumer research", "market analysis", "focus group", "competitor analysis"]
    },
    "public_relations": {
        "name": "Public Relations",
        "domain": "business_administration",
        "description": "Managing corporate public relations and media including press releases, media relations, crisis communications, and corporate reputation management.",
        "keywords": ['public relations', 'PR', 'media relations', 'press release', 'reputation management', 'corporate communications', 'media management', 'crisis communications']
    },
    "events_management": {
        "name": "Event Management",
        "domain": "business_administration",
        "description": "Managing corporate events including conferences, seminars, product launches, and business functions",
        "keywords": ["events management", "event planning", "conference", "corporate events", "event coordination", "exhibition", "seminar"]
    },
    
    # Real Estate
    "property_sales": {
        "name": "Real Estate Sales",
        "domain": "business_administration",
        "description": "Selling real estate including property marketing, open homes, auctions, and sales negotiation",
        "keywords": ["property sales", "real estate", "real estate agent", "property listing", "open home", "auction", "property selling"]
    },
    "property_management": {
        "name": "Property Management",
        "domain": "business_administration",
        "description": "Managing rental investment properties including tenant management, rent collection, lease administration, and property maintenance coordination for landlords.",
        "keywords": ['property management', 'rental property', 'tenant management', 'rent collection', 'lease management', 'landlord services', 'rental management', 'investment property']
    },
    
    # Customer Service
    "customer_service": {
        "name": "Customer Service",
        "domain": "business_administration",
        "description": "Providing customer service including enquiry handling, problem resolution, and service delivery.",
        "keywords": ["customer service", "customer support", "customer care", "client service", "enquiries", "customer enquiry", "service desk"]
    },
    "call_centre": {
        "name": "Call Centre Operations",
        "domain": "business_administration",
        "description": "Working in call centres including inbound calls, outbound calls, and telephone customer service.",
        "keywords": ["call centre", "call center", "inbound calls", "outbound calls", "phone support", "contact centre", "telephony"]
    },
    "complaints_handling": {
        "name": "Complaints Resolution",
        "domain": "business_administration",
        "description": "Resolving customer complaints including investigation, resolution, escalation, and complaint management",
        "keywords": ["complaints handling", "complaints", "complaint resolution", "dispute resolution", "customer complaints", "escalation"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MANUFACTURING, ENGINEERING & PRODUCTION (55 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Machining
    "lathe_operation": {
        "name": "Lathe Operation",
        "domain": "manufacturing_engineering",
        "description": "Operating manual and CNC lathes to produce cylindrical metal components through turning, boring, and threading operations.",
        "keywords": ["lathe", "turning", "lathe operation", "CNC lathe", "manual lathe", "lathe machining", "facing", "boring"]
    },
    "milling": {
        "name": "Milling Machine Operation",
        "domain": "manufacturing_engineering",
        "description": "Operating milling machines to produce metal components through cutting, drilling, and surface finishing operations.",
        "keywords": ["milling", "milling machine", "CNC milling", "mill", "end mill", "milling operation", "vertical mill", "horizontal mill"]
    },
    "cnc_programming": {
        "name": "CNC Programming",
        "domain": "manufacturing_engineering",
        "description": "Creating CNC programs using G-code and CAM software for automated machining of metal and plastic components.",
        "keywords": ["CNC programming", "G-code", "CNC code", "CAM", "CNC setup", "program editing", "CNC programming"]
    },
    "cnc_operation": {
        "name": "CNC Machining",
        "domain": "manufacturing_engineering",
        "description": "Operating CNC machine tools including lathes, mills, and machining centres to produce precision metal components.",
        "keywords": ["CNC operation", "CNC operator", "CNC machining", "CNC machine", "machine operation", "CNC setter"]
    },
    "grinding": {
        "name": "Grinding Surface Finishing",
        "domain": "manufacturing_engineering",
        "description": "Operating grinding machines for precision surface finishing including cylindrical, surface, and tool grinding.",
        "keywords": ["grinding", "surface grinding", "cylindrical grinding", "grinder", "precision grinding", "grinding machine"]
    },
    "tool_making": {
        "name": "Tool Die Making",
        "domain": "manufacturing_engineering",
        "description": "Manufacturing precision tools, dies, and moulds for production including machining, EDM, and tool fitting.",
        "keywords": ["tool making", "toolmaker", "die making", "jig", "fixture", "precision tooling", "mould making", "EDM"]
    },
    
    # Welding & Fabrication
    "mig_welding": {
        "name": "MIG Welding",
        "domain": "manufacturing_engineering",
        "description": "Welding metals using MIG/GMAW process with wire-fed welding machines for fabrication and manufacturing applications.",
        "keywords": ["MIG welding", "GMAW", "MIG", "wire welding", "gas metal arc", "MIG welder", "steel welding"]
    },
    "tig_welding": {
        "name": "TIG Welding",
        "domain": "manufacturing_engineering",
        "description": "Welding metals using TIG/GTAW process for precision welding of stainless steel, aluminium, and thin materials.",
        "keywords": ["TIG welding", "GTAW", "TIG", "tungsten", "TIG welder", "argon welding", "stainless welding", "aluminium welding"]
    },
    "stick_welding": {
        "name": "MMA Welding",
        "domain": "manufacturing_engineering",
        "description": "Welding metals using stick/MMA welding process with consumable electrodes for structural and maintenance welding.",
        "keywords": ["stick welding", "MMA", "MMAW", "arc welding", "manual metal arc", "electrode", "stick welder"]
    },
    "pipe_welding": {
        "name": "Pipe Welding",
        "domain": "manufacturing_engineering",
        "description": "Welding pipe and tube for pipelines, pressure vessels, and piping systems using various welding processes.",
        "keywords": ["pipe welding", "pipe welder", "tube welding", "pipeline", "pipe fabrication", "pressure welding"]
    },
    "structural_welding": {
        "name": "Structural Welding",
        "domain": "manufacturing_engineering",
        "description": "Welding structural steel for buildings, bridges, and heavy fabrication including certified structural welding.",
        "keywords": ["structural welding", "structural steel", "steel fabrication", "structural fabrication", "steel welding"]
    },
    "metal_fabrication": {
        "name": "Metal Fabrication",
        "domain": "manufacturing_engineering",
        "description": "Fabricating metal structures and components including cutting, forming, welding, and assembly of steel and aluminium.",
        "keywords": ["metal fabrication", "fabrication", "sheet metal", "plate work", "fabricator", "metal work", "steel fabrication"]
    },
    "sheet_metal": {
        "name": "Sheet Metal Work",
        "domain": "manufacturing_engineering",
        "description": "Forming sheet metal into components using folding, rolling, pressing, and fabrication techniques.",
        "keywords": ["sheet metal", "sheet metal work", "folding", "bending", "guillotine", "press brake", "sheet metal forming"]
    },
    "plasma_cutting": {
        "name": "Plasma Laser Cutting",
        "domain": "manufacturing_engineering",
        "description": "Operating plasma and laser cutting machines including CNC profiling, metal cutting, and plate processing",
        "keywords": ["plasma cutting", "laser cutting", "CNC cutting", "plasma", "profile cutting", "oxy cutting", "waterjet"]
    },
    
    # Fitting & Assembly
    "mechanical_fitting": {
        "name": "Mechanical Fitting",
        "domain": "manufacturing_engineering",
        "description": "Assembling, installing, and maintaining mechanical equipment including pumps, gearboxes, bearings, and mechanical drive systems.",
        "keywords": ["mechanical fitting", "fitter", "fitting", "assembly", "mechanical assembly", "machine assembly", "fitter and turner"]
    },
    "hydraulics": {
        "name": "Hydraulic Systems",
        "domain": "manufacturing_engineering",
        "description": "Installing and maintaining hydraulic systems including pumps, cylinders, valves, and hydraulic power units in industrial equipment.",
        "keywords": ["hydraulics", "hydraulic", "hydraulic system", "hydraulic cylinder", "hydraulic pump", "hydraulic repair", "fluid power"]
    },
    "pneumatics": {
        "name": "Pneumatic Systems",
        "domain": "manufacturing_engineering",
        "description": "Installing and maintaining pneumatic systems including compressors, air cylinders, valves, and pneumatic control circuits.",
        "keywords": ["pneumatics", "pneumatic", "pneumatic system", "air system", "compressed air", "pneumatic cylinder", "pneumatic valves"]
    },
    "bearing_installation": {
        "name": "Bearing Seal Installation",
        "domain": "manufacturing_engineering",
        "description": "Installing and maintaining bearings, seals, and rotating equipment components in industrial machinery.",
        "keywords": ["bearing", "bearing installation", "seal", "bearing replacement", "bearing fitting", "shaft seal", "bearing maintenance"]
    },
    "precision_measurement": {
        "name": "Precision Measurement",
        "domain": "manufacturing_engineering",
        "description": "Using precision measuring instruments including micrometers, calipers, CMMs, and gauges for quality control.",
        "keywords": ["precision measurement", "measuring", "micrometer", "vernier", "caliper", "gauge", "inspection", "CMM"]
    },
    
    # Maintenance
    "preventive_maintenance": {
        "name": "Preventive Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Performing scheduled preventive maintenance on industrial equipment including lubrication, inspections, and component replacement.",
        "keywords": ["preventive maintenance", "PM", "scheduled maintenance", "maintenance schedule", "routine maintenance", "planned maintenance"]
    },
    "breakdown_maintenance": {
        "name": "Breakdown Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Responding to emergency equipment breakdowns in manufacturing facilities, diagnosing faults and restoring production machinery.",
        "keywords": ["breakdown maintenance", "breakdown repair", "emergency repair", "fault repair", "unplanned maintenance", "breakdown"]
    },
    "machine_maintenance": {
        "name": "Machine Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining and repairing industrial manufacturing machinery including CNC machines, conveyors, and production equipment.",
        "keywords": ["machine maintenance", "machinery maintenance", "equipment maintenance", "machine repair", "industrial maintenance"]
    },
    "conveyor_maintenance": {
        "name": "Conveyor Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining conveyor belt systems including belt tracking, roller replacement, drive systems, and conveyor safety equipment.",
        "keywords": ["conveyor", "conveyor maintenance", "belt conveyor", "conveyor system", "conveyor belt", "materials handling"]
    },
    "pump_maintenance": {
        "name": "Pump Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining industrial pumps including centrifugal pumps, positive displacement pumps, seals, and pump alignment.",
        "keywords": ["pump maintenance", "pump repair", "pump service", "centrifugal pump", "pump overhaul", "pump rebuild"]
    },
    "compressor_maintenance": {
        "name": "Compressor Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining air compressors and compressed air systems including reciprocating, screw, and centrifugal compressors.",
        "keywords": ["compressor", "compressor maintenance", "air compressor", "compressor service", "compressor repair", "compressed air system"]
    },
    
    # Electrical/Electronic
    "electrical_maintenance": {
        "name": "Industrial Electrical Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining industrial electrical systems including motors, switchboards, control panels, and factory electrical equipment. Not IT/computer systems.",
        "keywords": ["electrical maintenance", "industrial electrical", "electrical repair", "motor maintenance", "electrical fault", "electrical service"]
    },
    "motor_control": {
        "name": "Motor Control Systems",
        "domain": "manufacturing_engineering",
        "description": "Installing and maintaining electric motor control systems including variable speed drives, soft starters, and motor control centres.",
        "keywords": ["motor control", "electric motor", "VSD", "variable speed drive", "motor starter", "soft starter", "motor control centre"]
    },
    "plc_programming": {
        "name": "PLC Programming",
        "domain": "manufacturing_engineering",
        "description": "Programming industrial Programmable Logic Controllers for factory automation, machine control, and process control using ladder logic and structured text.",
        "keywords": ["PLC", "PLC programming", "programmable logic controller", "ladder logic", "Siemens", "Allen Bradley", "automation"]
    },
    "instrumentation": {
        "name": "Industrial Instrumentation",
        "domain": "manufacturing_engineering",
        "description": "Installing and maintaining industrial measurement instruments including sensors, transmitters, gauges, and process control instrumentation.",
        "keywords": ["instrumentation", "instruments", "process control", "sensors", "transmitters", "calibration", "control systems"]
    },
    
    # Production
    "production_operation": {
        "name": "Production Operations",
        "domain": "manufacturing_engineering",
        "description": "Operating production lines and manufacturing processes including machine operation, assembly, and production monitoring.",
        "keywords": ["production", "production operation", "production line", "manufacturing", "production worker", "assembly line", "process operator"]
    },
    "machine_operation": {
        "name": "Machine Operation",
        "domain": "manufacturing_engineering",
        "description": "Operating industrial machinery in manufacturing facilities including setup, operation, and basic maintenance.",
        "keywords": ["machine operation", "machine operator", "operating machinery", "production machine", "factory machine"]
    },
    "packaging_operation": {
        "name": "Packaging Operations",
        "domain": "manufacturing_engineering",
        "description": "Operating packaging machinery and performing manual packaging including labelling, sealing, and palletising.",
        "keywords": ["packaging", "packing", "labelling", "packaging machine", "shrink wrap", "carton", "palletising"]
    },
    "quality_inspection": {
        "name": "Quality Inspection",
        "domain": "manufacturing_engineering",
        "description": "Inspecting manufactured products for quality conformance including dimensional inspection, visual inspection, and testing.",
        "keywords": ["quality inspection", "QC", "quality control", "inspection", "quality check", "product inspection", "incoming inspection"]
    },
    "quality_assurance": {
        "name": "Quality Assurance",
        "domain": "manufacturing_engineering",
        "description": "Implementing quality management systems including ISO 9001, quality procedures, audits, and continuous improvement in manufacturing.",
        "keywords": ["quality assurance", "QA", "ISO 9001", "quality system", "quality management", "audit", "quality procedures"]
    },
    
    # Food & Beverage Manufacturing
    "food_processing": {
        "name": "Food Processing",
        "domain": "manufacturing_engineering",
        "description": "Operating food processing equipment and performing food manufacturing operations including HACCP compliance.",
        "keywords": ["food processing", "food production", "food manufacturing", "food factory", "food processing equipment"]
    },
    "meat_processing": {
        "name": "Meat Processing",
        "domain": "manufacturing_engineering",
        "description": "Processing meat products including boning, slicing, mincing, and smallgoods manufacturing.",
        "keywords": ["meat processing", "smallgoods", "sausage making", "meat production", "ham", "bacon", "meat plant"]
    },
    "dairy_processing": {
        "name": "Dairy Processing",
        "domain": "manufacturing_engineering",
        "description": "Processing dairy products including milk, cheese, yogurt, and dairy product manufacturing.",
        "keywords": ["dairy processing", "milk processing", "cheese making", "yogurt", "dairy plant", "pasteurisation"]
    },
    "bakery_production": {
        "name": "Bakery Production",
        "domain": "manufacturing_engineering",
        "description": "Operating commercial bakery equipment for bread, pastry, and baked goods production.",
        "keywords": ["bakery production", "commercial baking", "bread production", "bakery", "dough", "oven operation", "baking production"]
    },
    "beverage_production": {
        "name": "Beverage Production",
        "domain": "manufacturing_engineering",
        "description": "Operating beverage production equipment for drinks manufacturing including filling, bottling, and packaging.",
        "keywords": ["beverage production", "drink production", "bottling", "beverage manufacturing", "soft drink", "juice production"]
    },
    "brewing": {
        "name": "Beer Brewing",
        "domain": "manufacturing_engineering",
        "description": "Operating brewery equipment for beer production including mashing, fermentation, and packaging.",
        "keywords": ["brewing", "beer production", "brewery", "craft beer", "fermentation", "brewhouse", "kegging", "beer"]
    },
    
    # Plastics & Composites
    "injection_moulding": {
        "name": "Injection Moulding",
        "domain": "manufacturing_engineering",
        "description": "Operating plastic injection moulding machines to produce plastic components including setup, operation, and quality control.",
        "keywords": ["injection moulding", "injection molding", "plastic moulding", "moulding machine", "mould setting", "plastic injection"]
    },
    "extrusion": {
        "name": "Extrusion Processing",
        "domain": "manufacturing_engineering",
        "description": "Operating extrusion machines to produce plastic or metal profiles through continuous extrusion processes.",
        "keywords": ["extrusion", "extruder", "plastic extrusion", "pipe extrusion", "profile extrusion", "extrusion line"]
    },
    "composite_fabrication": {
        "name": "Composite Fabrication",
        "domain": "manufacturing_engineering",
        "description": "Manufacturing composite and fibreglass products including layup, moulding, and finishing of composite materials.",
        "keywords": ["composite", "fibreglass", "carbon fibre", "composite fabrication", "laminating", "GRP", "composite manufacture"]
    },
    
    # Surface Treatment
    "powder_coating": {
        "name": "Powder Coating",
        "domain": "manufacturing_engineering",
        "description": "Applying powder coat finishes to metal products using electrostatic application and curing processes.",
        "keywords": ["powder coating", "powder coat", "electrostatic coating", "powder paint", "curing oven", "coating line"]
    },
    "electroplating": {
        "name": "Electroplating Finishing",
        "domain": "manufacturing_engineering",
        "description": "Applying metal plating and surface finishes using electroplating processes including chrome, zinc, and nickel plating.",
        "keywords": ["electroplating", "plating", "chrome plating", "zinc plating", "metal finishing", "anodising", "galvanising"]
    },
    "sandblasting": {
        "name": "Abrasive Blasting",
        "domain": "manufacturing_engineering",
        "description": "Preparing metal surfaces using abrasive blasting techniques including sandblasting, shot blasting, and surface preparation.",
        "keywords": ["sandblasting", "abrasive blasting", "surface preparation", "blast cleaning", "grit blasting", "shot blasting"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EDUCATION, TRAINING & DEVELOPMENT (25 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Early Childhood
    "early_childhood_education": {
        "name": "Early Childhood Education",
        "domain": "education_training",
        "description": "Educating human children in early childhood settings including kindergarten, preschool, and developmental programs for children aged 0-5 years. Not animal-related.",
        "keywords": ['early childhood', 'kindergarten', 'preschool', 'early learning', 'EYLF', 'NQS', 'child development', 'human children', 'pre-prep', 'early years']
    },
    "childcare": {
        "name": "Childcare Services",
        "domain": "education_training",
        "description": "Caring for human children in childcare centres including supervision, activities, and developmental support for infants and toddlers. Does not include animal care.",
        "keywords": ['childcare', 'child care', 'daycare', 'long day care', 'childcare centre', 'childcare worker', 'child minding', 'human children', 'infant care', 'toddler care', 'early childhood']
    },
    "outside_school_hours": {
        "name": "OSHC Care",
        "domain": "education_training",
        "description": "Providing before and after school care for school-aged human children including vacation care, homework help, and recreational activities.",
        "keywords": ['OSHC', 'outside school hours', 'before school', 'after school', 'vacation care', 'school age care', 'holiday program', 'human children']
    },
    
    # School Education
    "primary_teaching": {
        "name": "Primary Teaching",
        "domain": "education_training",
        "description": "Teaching primary school students including curriculum delivery and classroom management.",
        "keywords": ["primary teaching", "primary school", "primary teacher", "primary education", "elementary", "classroom teaching"]
    },
    "secondary_teaching": {
        "name": "Secondary Teaching",
        "domain": "education_training",
        "description": "Teaching secondary school students including subject specialisation and student engagement.",
        "keywords": ["secondary teaching", "high school", "secondary teacher", "secondary education", "subject teaching", "high school teacher"]
    },
    "special_education": {
        "name": "Special Education",
        "domain": "education_training",
        "description": "Teaching students with special needs including learning support and adapted curriculum.",
        "keywords": ["special education", "special needs", "learning support", "special ed", "disability education", "inclusion"]
    },
    "teacher_aide": {
        "name": "Teacher Aide",
        "domain": "education_training",
        "description": "Supporting teachers in school classrooms with human students including learning support, supervision, and educational assistance.",
        "keywords": ['teacher aide', 'education assistant', 'classroom support', 'teacher assistant', 'learning support', 'school assistant', 'human students']
    },
    
    # Tertiary & VET
    "vet_training": {
        "name": "VET Training Delivery",
        "domain": "education_training",
        "description": "Delivering vocational education and training including competency-based training and assessment.",
        "keywords": ["VET", "vocational training", "TAE", "trainer", "assessor", "RTO", "competency", "training delivery"]
    },
    "assessment": {
        "name": "Competency Assessment",
        "domain": "education_training",
        "description": "Assessing vocational training competencies including practical skills assessment, Recognition of Prior Learning (RPL), workplace assessment, and VET assessment.",
        "keywords": ['competency assessment', 'VET assessment', 'RPL', 'skills assessment', 'training assessment', 'practical assessment', 'workplace assessment', 'vocational assessment']
    },
    "learning_design": {
        "name": "Learning Design",
        "domain": "education_training",
        "description": "Designing learning programs including curriculum development and instructional design.",
        "keywords": ["learning design", "curriculum development", "instructional design", "course development", "training materials", "learning resources"]
    },
    "elearning": {
        "name": "E-Learning Development",
        "domain": "education_training",
        "description": "Developing e-learning content including online courses, learning management systems, and digital learning.",
        "keywords": ["e-learning", "elearning", "online learning", "LMS", "SCORM", "Articulate", "online course", "virtual learning"]
    },
    
    # Training Support
    "training_coordination": {
        "name": "Training Coordination",
        "domain": "education_training",
        "description": "Coordinating corporate training programs including training calendar scheduling, venue booking, trainer coordination, and training administration.",
        "keywords": ['training coordination', 'training administration', 'training scheduling', 'training logistics', 'course coordination', 'trainer booking', 'training programs']
    },
    "student_support": {
        "name": "Student Support Services",
        "domain": "education_training",
        "description": "Supporting students with wellbeing, learning, and engagement including student services.",
        "keywords": ["student support", "student services", "student welfare", "student counselling", "learning support", "student assistance"]
    },
    "library_services": {
        "name": "Library Services",
        "domain": "education_training",
        "description": "Providing library and information services including cataloguing, reference services, collection management, and library program delivery in libraries.",
        "keywords": ['library services', 'librarian', 'cataloguing', 'reference services', 'collection management', 'library programs', 'information services']
    },
    
    # Coaching & Development
    "workplace_coaching": {
        "name": "Workplace Coaching",
        "domain": "education_training",
        "description": "Coaching and mentoring in workplaces including performance coaching and professional development.",
        "keywords": ["workplace coaching", "coaching", "mentoring", "on-the-job training", "buddy", "workplace mentor", "skills coaching"]
    },
    "facilitation": {
        "name": "Training Facilitation",
        "domain": "education_training",
        "description": "Facilitating training workshops and group sessions including adult learning, group dynamics, and participatory methods",
        "keywords": ["facilitation", "facilitator", "workshop", "group facilitation", "training facilitation", "session facilitation"]
    },
    "presentation_skills": {
        "name": "Presentation Skills",
        "domain": "education_training",
        "description": "Delivering presentations including public speaking, facilitation, and presentation techniques.",
        "keywords": ["presentation", "presenting", "public speaking", "presentation skills", "PowerPoint", "speaker", "keynote"]
    },
    
    # Languages
    "english_teaching": {
        "name": "English Language Teaching",
        "domain": "education_training",
        "description": "Teaching English as a second language including TESOL, ESL, and English language instruction.",
        "keywords": ["English teaching", "ESL", "TESOL", "EAL", "English language", "ELICOS", "English teacher"]
    },
    "auslan": {
        "name": "Sign Language Interpreting",
        "domain": "education_training",
        "description": "Interpreting Australian Sign Language (Auslan) for deaf and hard-of-hearing people in various settings",
        "keywords": ["Auslan", "sign language", "deaf", "signing", "Auslan interpreter", "deaf community"]
    },
    "interpreting": {
        "name": "Language Interpreting",
        "domain": "education_training",
        "description": "Interpreting between spoken languages including consecutive and simultaneous interpreting services",
        "keywords": ["interpreting", "interpreter", "translation", "NAATI", "community interpreting", "language services"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # HOSPITALITY, TOURISM & EVENTS (45 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Kitchen
    "commercial_cookery": {
        "name": "Commercial Cookery",
        "domain": "hospitality_tourism",
        "description": "Preparing food in commercial kitchens including cooking techniques, menu planning, and kitchen operations.",
        "keywords": ["commercial cookery", "chef", "cook", "commercial kitchen", "cooking", "professional cooking", "kitchen"]
    },
    "pastry_baking": {
        "name": "Patisserie Baking",
        "domain": "hospitality_tourism",
        "description": "Preparing pastries and baked goods including cakes, breads, desserts, and patisserie techniques.",
        "keywords": ["pastry", "baking", "patisserie", "pastry chef", "dessert", "cake", "bread baking", "pastry making"]
    },
    "asian_cookery": {
        "name": "Asian Cuisine Cookery",
        "domain": "hospitality_tourism",
        "description": "Preparing Asian cuisine including Chinese, Thai, Japanese, Vietnamese, and Asian cooking techniques.",
        "keywords": ["Asian cookery", "Asian cuisine", "wok", "Chinese cooking", "Japanese", "Thai", "Vietnamese", "Asian food"]
    },
    "short_order_cooking": {
        "name": "Short Order Cooking",
        "domain": "hospitality_tourism",
        "description": "Preparing short order and fast food including grilling, frying, and quick service cooking.",
        "keywords": ["short order", "fast food", "grill cook", "line cook", "fast food cooking", "quick service"]
    },
    "kitchen_operations": {
        "name": "Kitchen Operations",
        "domain": "hospitality_tourism",
        "description": "Working in commercial kitchens including kitchen hand duties, cleaning, and kitchen support.",
        "keywords": ["kitchen hand", "kitchen assistant", "kitchen operations", "dishwashing", "food prep", "kitchen duties", "kitchen steward"]
    },
    "food_preparation": {
        "name": "Food Preparation",
        "domain": "hospitality_tourism",
        "description": "Preparing ingredients for cooking including mise en place, food handling, and basic food preparation.",
        "keywords": ["food preparation", "food prep", "mise en place", "prep cook", "vegetable prep", "ingredient preparation"]
    },
    "catering": {
        "name": "Catering Services",
        "domain": "hospitality_tourism",
        "description": "Providing catering services including event catering, off-site catering, and catering operations.",
        "keywords": ["catering", "catering services", "event catering", "function catering", "catering kitchen", "off-site catering"]
    },
    
    # Front of House
    "food_beverage_service": {
        "name": "Food Beverage Service",
        "domain": "hospitality_tourism",
        "description": "Providing food and beverage service in restaurants including table service, order taking, and customer care",
        "keywords": ["food service", "beverage service", "waiter", "waitress", "table service", "restaurant service", "F&B service"]
    },
    "barista": {
        "name": "Barista Skills",
        "domain": "hospitality_tourism",
        "description": "Preparing coffee and espresso drinks including espresso extraction, milk texturing, and coffee service.",
        "keywords": ["barista", "coffee", "espresso", "latte art", "coffee making", "cafe", "milk texturing", "coffee machine"]
    },
    "bar_service": {
        "name": "Bar Service",
        "domain": "hospitality_tourism",
        "description": "Providing bar service including cocktails, beer, wine, and responsible service of alcohol.",
        "keywords": ["bar service", "bartender", "bartending", "cocktails", "bar operations", "mixology", "bar work", "RSA"]
    },
    "sommelier": {
        "name": "Sommelier Wine Service",
        "domain": "hospitality_tourism",
        "description": "Providing sommelier and wine service including wine selection, tasting, and wine service.",
        "keywords": ["sommelier", "wine service", "wine", "beverage service", "wine list", "wine pairing", "wine knowledge"]
    },
    "rsl_gaming": {
        "name": "Gaming Operations",
        "domain": "hospitality_tourism",
        "description": "Operating gaming facilities in clubs including poker machines, keno, TAB, and gaming compliance",
        "keywords": ["RSL", "gaming", "club", "poker machines", "gaming attendant", "club operations", "gaming venue", "RCG"]
    },
    
    # Accommodation
    "hotel_reception": {
        "name": "Hotel Reception",
        "domain": "hospitality_tourism",
        "description": "Providing hotel reception services including check-in, reservations, and front desk operations.",
        "keywords": ["hotel reception", "front desk", "check-in", "check-out", "hotel reservations", "front office", "guest services"]
    },
    "concierge": {
        "name": "Concierge Services",
        "domain": "hospitality_tourism",
        "description": "Providing concierge services including guest assistance, recommendations, and VIP services.",
        "keywords": ["concierge", "guest assistance", "guest services", "hotel concierge", "porter", "bell desk"]
    },
    "housekeeping": {
        "name": "Hotel Housekeeping",
        "domain": "hospitality_tourism",
        "description": "Providing hotel housekeeping services including room cleaning, bed making, and housekeeping standards",
        "keywords": ["housekeeping", "room cleaning", "hotel cleaning", "room attendant", "housekeeping attendant", "bed making", "room servicing"]
    },
    "hotel_operations": {
        "name": "Hotel Operations Management",
        "domain": "hospitality_tourism",
        "description": "Managing hotel operations including rooms division, guest services, and hotel management.",
        "keywords": ["hotel operations", "hotel management", "rooms division", "hotel duty manager", "night audit", "revenue management"]
    },
    
    # Tourism
    "tour_guiding": {
        "name": "Tour Guiding",
        "domain": "hospitality_tourism",
        "description": "Guiding tours including tour commentary, group management, and tourism interpretation.",
        "keywords": ["tour guide", "tour guiding", "guided tour", "interpretation", "tourist guide", "tour leader", "sightseeing"]
    },
    "travel_consulting": {
        "name": "Travel Consulting",
        "domain": "hospitality_tourism",
        "description": "Providing travel consulting services including bookings, itineraries, and travel advice.",
        "keywords": ["travel consultant", "travel agent", "travel booking", "holiday booking", "travel agency", "reservations", "itinerary"]
    },
    "tourism_information": {
        "name": "Tourism Information Services",
        "domain": "hospitality_tourism",
        "description": "Providing tourism information services including visitor centres and travel advice.",
        "keywords": ["tourism information", "visitor information", "tourist information", "information centre", "visitor services"]
    },
    "eco_tourism": {
        "name": "Eco Tourism",
        "domain": "hospitality_tourism",
        "description": "Providing eco tourism and nature-based tourism services including environmental interpretation.",
        "keywords": ["eco tourism", "ecotourism", "nature tourism", "sustainable tourism", "wildlife tourism", "adventure tourism"]
    },
    
    # Events
    "event_coordination": {
        "name": "Event Coordination",
        "domain": "hospitality_tourism",
        "description": "Coordinating functions and special events including venue booking, catering coordination, event logistics, and event day management for corporate and social events.",
        "keywords": ['event coordination', 'function coordination', 'event planning', 'venue booking', 'event logistics', 'event management', 'function management', 'special events']
    },
    "wedding_planning": {
        "name": "Wedding Event Planning",
        "domain": "hospitality_tourism",
        "description": "Planning weddings including wedding coordination, vendors, and event management.",
        "keywords": ["wedding planning", "wedding coordinator", "wedding", "bridal", "wedding venue", "wedding day coordination"]
    },
    "conference_operations": {
        "name": "Conference Operations",
        "domain": "hospitality_tourism",
        "description": "Operating conference and exhibition facilities including AV, room setup, and conference services.",
        "keywords": ["conference", "exhibition", "convention", "conference operations", "exhibition stand", "trade show", "venue management"]
    },
    "audio_visual_events": {
        "name": "Event Audio Visual",
        "domain": "hospitality_tourism",
        "description": "Operating audio visual equipment for events including projectors, screens, microphones, and AV systems",
        "keywords": ["audio visual", "AV", "event AV", "sound", "lighting", "projection", "event technology", "staging"]
    },
    
    # Food Safety
    "food_safety": {
        "name": "Food Safety",
        "domain": "hospitality_tourism",
        "description": "Implementing food safety practices including HACCP, food handling, and hygiene compliance.",
        "keywords": ["food safety", "food hygiene", "food handling", "HACCP", "food safety supervisor", "temperature control", "food handler"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # CREATIVE ARTS, CULTURE & ENTERTAINMENT (45 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Visual Arts
    "painting_drawing": {
        "name": "Fine Art Painting",
        "domain": "creative_arts",
        "description": "Creating fine art through painting and drawing including oils, acrylics, watercolours, and mixed media",
        "keywords": ["painting", "drawing", "fine art", "artist", "canvas", "oil painting", "watercolour", "sketching", "illustration"]
    },
    "sculpture": {
        "name": "Sculpture Art",
        "domain": "creative_arts",
        "description": "Creating three-dimensional art including carving, modelling, casting, and sculptural installation",
        "keywords": ["sculpture", "sculptor", "3D art", "clay", "bronze casting", "carving", "sculptural", "installation art"]
    },
    "printmaking": {
        "name": "Printmaking Art",
        "domain": "creative_arts",
        "description": "Creating fine art prints including etching, lithography, screen printing, and relief printing techniques",
        "keywords": ["printmaking", "print", "etching", "lithography", "screen printing", "woodcut", "linocut", "monotype"]
    },
    "ceramics": {
        "name": "Ceramics Pottery",
        "domain": "creative_arts",
        "description": "Creating pottery and ceramic art including wheel throwing, hand building, glazing, and kiln firing",
        "keywords": ["ceramics", "pottery", "ceramic", "kiln", "glazing", "wheel throwing", "hand building", "ceramic artist"]
    },
    "glass_art": {
        "name": "Glass Art",
        "domain": "creative_arts",
        "description": "Creating glass art including glassblowing, kiln forming, stained glass, and glass casting",
        "keywords": ["glass art", "glass blowing", "stained glass", "fused glass", "glass artist", "kiln formed glass"]
    },
    "textile_art": {
        "name": "Textile Art",
        "domain": "creative_arts",
        "description": "Creating textile art including weaving, embroidery, felting, fabric dyeing, and fibre sculpture",
        "keywords": ["textile art", "fibre art", "weaving", "tapestry", "textile", "embroidery", "fabric art", "quilting"]
    },
    
    # Design
    "graphic_design": {
        "name": "Graphic Design",
        "domain": "creative_arts",
        "description": "Designing visual communications for print including logos, brochures, packaging, and publication design",
        "keywords": ["graphic design", "graphic designer", "visual design", "layout", "branding", "logo design", "InDesign", "print design"]
    },
    "fashion_design": {
        "name": "Fashion Design",
        "domain": "creative_arts",
        "description": "Designing clothing and fashion including garment design, pattern making, and fashion illustration",
        "keywords": ["fashion design", "fashion designer", "garment design", "fashion illustration", "pattern making", "couture", "apparel design"]
    },
    "interior_design": {
        "name": "Interior Design",
        "domain": "creative_arts",
        "description": "Designing interior spaces including space planning, colour schemes, materials selection, and furnishing",
        "keywords": ["interior design", "interior designer", "space planning", "interior decoration", "interior styling", "fit-out design"]
    },
    "industrial_design": {
        "name": "Industrial Product Design",
        "domain": "creative_arts",
        "description": "Designing products and industrial objects including form, function, materials, and manufacturing considerations",
        "keywords": ["industrial design", "product design", "3D design", "product designer", "CAD design", "prototype", "consumer products"]
    },
    "jewellery_design": {
        "name": "Jewellery Making",
        "domain": "creative_arts",
        "description": "Designing and making jewellery including metalsmithing, stone setting, and precious metal work",
        "keywords": ["jewellery design", "jewellery making", "goldsmith", "silversmith", "stone setting", "metalsmith", "jeweller"]
    },
    
    # Photography & Video
    "photography": {
        "name": "Photography Services",
        "domain": "creative_arts",
        "description": "Capturing photographs including camera operation, lighting, composition, and photographic techniques",
        "keywords": ["photography", "photographer", "camera", "photo shoot", "portrait photography", "wedding photography", "commercial photography"]
    },
    "photo_editing": {
        "name": "Photo Editing Retouching",
        "domain": "creative_arts",
        "description": "Editing photographs digitally including retouching, colour correction, compositing, and image manipulation",
        "keywords": ["photo editing", "retouching", "Photoshop", "Lightroom", "image editing", "colour correction", "photo manipulation"]
    },
    "videography": {
        "name": "Videography Production",
        "domain": "creative_arts",
        "description": "Filming video content including camera operation, lighting, shot composition, and video production",
        "keywords": ["videography", "video production", "filming", "videographer", "camera operator", "video shoot", "cinematography"]
    },
    "video_editing": {
        "name": "Video Editing",
        "domain": "creative_arts",
        "description": "Editing video content including cutting, transitions, colour grading, effects, and post-production",
        "keywords": ["video editing", "editing", "Premiere Pro", "Final Cut", "post-production", "video editor", "DaVinci Resolve"]
    },
    
    # Animation & VFX
    "2d_animation": {
        "name": "2D Animation",
        "domain": "creative_arts",
        "description": "Creating two-dimensional animation including traditional animation, motion graphics, and digital 2D techniques",
        "keywords": ["2D animation", "animation", "animator", "character animation", "After Effects", "frame by frame", "motion graphics"]
    },
    "3d_animation": {
        "name": "3D Animation Modelling",
        "domain": "creative_arts",
        "description": "Creating 3D animation and models including modelling, rigging, texturing, and rendering in 3D software",
        "keywords": ["3D animation", "3D modelling", "Maya", "Blender", "Cinema 4D", "3D artist", "rigging", "rendering"]
    },
    "visual_effects": {
        "name": "Visual Effects Compositing",
        "domain": "creative_arts",
        "description": "Creating visual effects for film and video including compositing, CGI, green screen, and VFX pipelines",
        "keywords": ["visual effects", "VFX", "compositing", "Nuke", "green screen", "CGI", "special effects", "motion tracking"]
    },
    
    # Performing Arts
    "acting": {
        "name": "Acting Performance",
        "domain": "creative_arts",
        "description": "Performing dramatic roles for stage or screen including character development, script interpretation, and performance",
        "keywords": ["acting", "actor", "theatre", "drama", "performance", "stage", "screen acting", "audition"]
    },
    "dance": {
        "name": "Dance Performance",
        "domain": "creative_arts",
        "description": "Performing dance including ballet, contemporary, jazz, hip-hop, or cultural dance styles and choreography",
        "keywords": ["dance", "dancer", "choreography", "ballet", "contemporary dance", "dance performance", "choreographer"]
    },
    "music_performance": {
        "name": "Music Performance",
        "domain": "creative_arts",
        "description": "Performing music on instruments including instrumental technique, ensemble playing, and live performance",
        "keywords": ["music performance", "musician", "instrument", "singer", "vocalist", "band", "orchestra", "live music"]
    },
    "singing": {
        "name": "Vocal Performance",
        "domain": "creative_arts",
        "description": "Performing vocals including singing technique, breath control, vocal styles, and live vocal performance",
        "keywords": ["singing", "vocal", "singer", "vocalist", "voice", "choir", "backing vocals", "vocal training"]
    },
    
    # Music Production
    "music_production": {
        "name": "Music Production Recording",
        "domain": "creative_arts",
        "description": "Producing and recording music including tracking, mixing, sound design, and digital audio workstations",
        "keywords": ["music production", "producer", "recording", "studio", "DAW", "Logic Pro", "Ableton", "beat making"]
    },
    "sound_engineering": {
        "name": "Sound Engineering Mixing",
        "domain": "creative_arts",
        "description": "Engineering audio including recording, mixing, mastering, and audio production in studios",
        "keywords": ["sound engineering", "audio engineering", "mixing", "mastering", "sound engineer", "Pro Tools", "audio recording"]
    },
    "live_sound": {
        "name": "Live Sound Engineering",
        "domain": "creative_arts",
        "description": "Operating live sound systems including PA setup, mixing, monitor engineering, and live event audio",
        "keywords": ["live sound", "PA", "sound operator", "FOH", "monitor engineer", "live mixing", "concert sound"]
    },
    
    # Stage & Production
    "stage_management": {
        "name": "Stage Management",
        "domain": "creative_arts",
        "description": "Managing theatrical productions including rehearsals, cues, backstage coordination, and show calling",
        "keywords": ["stage management", "stage manager", "backstage", "cues", "production management", "call sheet", "theatre production"]
    },
    "lighting_design": {
        "name": "Lighting Design",
        "domain": "creative_arts",
        "description": "Designing lighting for stage and events including lighting plots, programming, and theatrical lighting",
        "keywords": ["lighting design", "lighting operator", "stage lighting", "lighting rig", "LX", "lighting programming", "moving lights"]
    },
    "set_design": {
        "name": "Set Design Construction",
        "domain": "creative_arts",
        "description": "Designing and building sets for theatre and film including scenic design, construction, and installation",
        "keywords": ["set design", "scenic", "set construction", "set builder", "scenic artist", "props", "stage design"]
    },
    "costume_design": {
        "name": "Costume Wardrobe",
        "domain": "creative_arts",
        "description": "Designing costumes for performance including period costumes, wardrobe management, and costume construction",
        "keywords": ["costume design", "wardrobe", "costume", "costume maker", "dresser", "costume construction", "theatrical costume"]
    },
    "makeup_effects": {
        "name": "Makeup Special Effects",
        "domain": "creative_arts",
        "description": "Applying makeup for stage and film including theatrical makeup, prosthetics, and special effects makeup",
        "keywords": ["makeup", "special effects makeup", "SFX makeup", "prosthetics", "theatrical makeup", "film makeup", "makeup artist"]
    },
    
    # Media & Broadcast
    "broadcasting": {
        "name": "Media Broadcasting",
        "domain": "creative_arts",
        "description": "Working in radio and television broadcasting including presenting, production, and broadcast operations",
        "keywords": ["broadcasting", "broadcast", "radio", "TV", "on-air", "presenter", "announcer", "broadcast journalist"]
    },
    "podcasting": {
        "name": "Podcasting Production",
        "domain": "creative_arts",
        "description": "Producing podcasts including recording, editing, publishing, and podcast content creation",
        "keywords": ["podcasting", "podcast", "podcast production", "audio content", "podcast editing", "podcast host"]
    },
    "streaming": {
        "name": "Live Streaming",
        "domain": "creative_arts",
        "description": "Creating live streaming content including setup, broadcasting, audience engagement, and streaming platforms",
        "keywords": ["streaming", "live streaming", "Twitch", "YouTube live", "streamer", "OBS", "content creator"]
    },
    "content_creation": {
        "name": "Digital Content Creation",
        "domain": "creative_arts",
        "description": "Creating digital content for social media including video, graphics, writing, and online content",
        "keywords": ["content creation", "content creator", "social media content", "YouTube", "TikTok", "influencer", "vlogging"]
    },
    
    # Writing
    "creative_writing": {
        "name": "Creative Writing",
        "domain": "creative_arts",
        "description": "Writing creative fiction and prose including novels, short stories, scripts, and creative non-fiction",
        "keywords": ["creative writing", "writing", "fiction", "novelist", "short story", "screenplay", "script writing", "author"]
    },
    "copywriting": {
        "name": "Copywriting Content",
        "domain": "creative_arts",
        "description": "Writing marketing and advertising copy including headlines, body copy, taglines, and persuasive content",
        "keywords": ["copywriting", "copywriter", "advertising copy", "marketing copy", "content writing", "web copy", "ad copy"]
    },
    "journalism": {
        "name": "Journalism Reporting",
        "domain": "creative_arts",
        "description": "Writing news and journalism including news gathering, interviewing, reporting, and journalistic writing",
        "keywords": ["journalism", "journalist", "news writing", "reporting", "news", "press", "media", "investigative journalism"]
    },
    "editing_proofreading": {
        "name": "Editing Proofreading",
        "domain": "creative_arts",
        "description": "Editing and proofreading text including grammar, spelling, style, and substantive editing",
        "keywords": ["editing", "proofreading", "editor", "copy editing", "manuscript", "publishing", "sub-editing"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RETAIL, SALES & PERSONAL SERVICES (35 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Retail
    "retail_sales": {
        "name": "Retail Sales",
        "domain": "retail_services",
        "description": "Selling products in retail environments including customer service, product knowledge, and sales techniques",
        "keywords": ["retail", "retail sales", "shop assistant", "sales assistant", "customer service", "retail store", "selling"]
    },
    "visual_merchandising": {
        "name": "Visual Merchandising",
        "domain": "retail_services",
        "description": "Creating retail displays and store merchandising including window displays and visual presentation",
        "keywords": ["visual merchandising", "merchandising", "display", "store layout", "window display", "retail display", "VM"]
    },
    "stock_management": {
        "name": "Stock Inventory Management",
        "domain": "retail_services",
        "description": "Managing retail stock including inventory control, stocktakes, ordering, and stock replenishment",
        "keywords": ["stock management", "inventory", "stock control", "stocktake", "replenishment", "stock rotation", "ordering"]
    },
    "point_of_sale": {
        "name": "Point of Sale Operations",
        "domain": "retail_services",
        "description": "Operating point of sale systems including cash handling, EFTPOS, and checkout procedures",
        "keywords": ["point of sale", "POS", "cash register", "checkout", "till", "EFTPOS", "cashier", "sales processing"]
    },
    "loss_prevention": {
        "name": "Loss Prevention",
        "domain": "retail_services",
        "description": "Preventing retail loss including theft prevention, surveillance, and retail security measures",
        "keywords": ["loss prevention", "retail security", "shrinkage", "theft prevention", "shoplifting", "stock loss"]
    },
    
    # Personal Services
    "hairdressing": {
        "name": "Hairdressing Styling",
        "domain": "retail_services",
        "description": "Cutting and styling hair including haircuts, blow-drying, styling techniques, and hair treatments",
        "keywords": ["hairdressing", "hairdresser", "hair cutting", "hair styling", "hair colour", "salon", "haircut", "balayage"]
    },
    "barbering": {
        "name": "Barbering Services",
        "domain": "retail_services",
        "description": "Providing barbering services including men's haircuts, shaving, beard trimming, and grooming",
        "keywords": ["barbering", "barber", "men's haircut", "fade", "beard trim", "barber shop", "clipper cut", "shave"]
    },
    "hair_colouring": {
        "name": "Hair Colouring",
        "domain": "retail_services",
        "description": "Applying hair colour including permanent colour, highlights, balayage, and colour correction",
        "keywords": ["hair colour", "hair colouring", "highlights", "foils", "colour correction", "tint", "bleach", "balayage"]
    },
    "beauty_therapy": {
        "name": "Beauty Therapy",
        "domain": "retail_services",
        "description": "Providing beauty treatments including facials, skin treatments, body treatments, and beauty therapy",
        "keywords": ["beauty therapy", "beauty therapist", "facial", "skincare", "beauty treatment", "beauty salon", "spa treatment"]
    },
    "nail_services": {
        "name": "Nail Services",
        "domain": "retail_services",
        "description": "Providing nail services including manicures, pedicures, gel nails, acrylics, and nail art",
        "keywords": ["nail services", "manicure", "pedicure", "nail technician", "nail art", "gel nails", "acrylic nails", "nail salon"]
    },
    "waxing": {
        "name": "Waxing Hair Removal",
        "domain": "retail_services",
        "description": "Removing body hair using waxing techniques including strip wax, hot wax, and Brazilian waxing",
        "keywords": ["waxing", "hair removal", "body waxing", "Brazilian", "wax treatment", "IPL", "laser hair removal"]
    },
    "lash_brow": {
        "name": "Lash Brow Services",
        "domain": "retail_services",
        "description": "Providing lash and brow services including lash extensions, tinting, brow shaping, and lamination",
        "keywords": ["lash extensions", "brow", "eyebrow", "lash lift", "brow lamination", "eyelash", "brow shaping", "lash technician"]
    },
    "massage_therapy": {
        "name": "Massage Therapy",
        "domain": "retail_services",
        "description": "Providing massage therapy including remedial massage, relaxation massage, and therapeutic bodywork",
        "keywords": ["massage", "massage therapy", "remedial massage", "relaxation massage", "massage therapist", "deep tissue", "sports massage"]
    },
    "makeup_artistry": {
        "name": "Makeup Artistry",
        "domain": "retail_services",
        "description": "Applying professional makeup including bridal, editorial, special occasion, and makeup techniques",
        "keywords": ["makeup artist", "makeup", "cosmetics", "bridal makeup", "makeup application", "MUA", "beauty makeup"]
    },
    "tattooing": {
        "name": "Tattooing Art",
        "domain": "retail_services",
        "description": "Creating tattoos including tattoo design, machine operation, hygiene, and tattoo artistry",
        "keywords": ["tattooing", "tattoo", "tattoo artist", "tattoo studio", "ink", "body art", "tattoo design"]
    },
    "body_piercing": {
        "name": "Body Piercing",
        "domain": "retail_services",
        "description": "Performing body piercings including ear, nose, and body piercings with sterile techniques",
        "keywords": ["body piercing", "piercing", "piercer", "ear piercing", "body modification", "piercing studio"]
    },
    
    # Optical
    "optical_dispensing": {
        "name": "Optical Dispensing",
        "domain": "retail_services",
        "description": "Dispensing spectacles and optical products including frame selection, lens fitting, and adjustments",
        "keywords": ["optical dispensing", "optical", "spectacles", "glasses", "frame fitting", "lens dispensing", "optician"]
    },
    
    # Funeral
    "funeral_services": {
        "name": "Funeral Services",
        "domain": "retail_services",
        "description": "Providing funeral services including funeral directing, mortuary work, and bereavement support",
        "keywords": ["funeral", "funeral director", "funeral services", "mortuary", "embalming", "burial", "cremation", "bereavement"]
    },
    
    # Locksmith
    "locksmithing": {
        "name": "Locksmithing Services",
        "domain": "retail_services",
        "description": "Providing locksmith services including lock installation, key cutting, and security hardware",
        "keywords": ["locksmith", "locksmithing", "locks", "key cutting", "lock installation", "security locks", "safe opening"]
    },
    
    # Dry Cleaning & Laundry
    "dry_cleaning": {
        "name": "Dry Cleaning",
        "domain": "retail_services",
        "description": "Providing dry cleaning services including garment care, stain removal, and laundry processing",
        "keywords": ["dry cleaning", "laundry", "pressing", "ironing", "garment care", "commercial laundry", "laundromat"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PUBLIC SAFETY, SECURITY & DEFENCE (30 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Security
    "security_guarding": {
        "name": "Security Guarding",
        "domain": "public_safety",
        "description": "Providing security guard services including static guarding, patrols, and security officer duties",
        "keywords": ["security guard", "security officer", "guarding", "security patrol", "static security", "mobile patrol", "security licence"]
    },
    "crowd_control": {
        "name": "Crowd Control",
        "domain": "public_safety",
        "description": "Managing crowds at events and venues including crowd safety, barrier control, and event security",
        "keywords": ["crowd control", "crowd management", "bouncer", "door security", "event security", "venue security"]
    },
    "cctv_monitoring": {
        "name": "CCTV Surveillance",
        "domain": "public_safety",
        "description": "Monitoring CCTV and surveillance systems including camera operation, incident detection, and control rooms",
        "keywords": ["CCTV", "surveillance", "monitoring", "control room", "security cameras", "video surveillance", "security monitoring"]
    },
    "access_control_security": {
        "name": "Security Access Control",
        "domain": "public_safety",
        "description": "Managing security access control including screening, ID checks, and entry point security",
        "keywords": ["access control", "screening", "ID checking", "entry control", "security screening", "visitor management"]
    },
    "security_systems": {
        "name": "Security Systems Installation",
        "domain": "public_safety",
        "description": "Installing security systems including alarms, access control, CCTV cameras, and electronic security",
        "keywords": ["security systems", "alarm system", "security installation", "intruder alarm", "security alarm", "access control system"]
    },
    "cash_transit": {
        "name": "Cash in Transit",
        "domain": "public_safety",
        "description": "Transporting cash and valuables in armoured vehicles including cash collection and secure transport",
        "keywords": ["cash-in-transit", "CIT", "armoured vehicle", "cash transport", "security transport", "cash collection"]
    },
    "investigation": {
        "name": "Private Investigation",
        "domain": "public_safety",
        "description": "Conducting private investigations including surveillance, background checks, and evidence gathering",
        "keywords": ["investigation", "investigator", "private investigator", "surveillance", "inquiry agent", "evidence gathering"]
    },
    
    # Emergency Services
    "firefighting": {
        "name": "Firefighting Operations",
        "domain": "public_safety",
        "description": "Fighting fires and performing rescues including structural firefighting, bushfire, and emergency response",
        "keywords": ["firefighting", "firefighter", "fire brigade", "fire rescue", "fire suppression", "fire service", "firefighting operations"]
    },
    "fire_prevention": {
        "name": "Fire Investigation Prevention",
        "domain": "public_safety",
        "description": "Preventing fires through inspection, investigation, and fire safety compliance enforcement",
        "keywords": ["fire prevention", "fire safety", "fire investigation", "fire inspection", "fire cause", "fire compliance"]
    },
    "ambulance_paramedic": {
        "name": "Paramedic Services",
        "domain": "public_safety",
        "description": "Providing paramedic and ambulance services including emergency medical care and patient transport",
        "keywords": ["paramedic", "ambulance", "emergency medical", "pre-hospital", "EMT", "ambulance officer", "patient transport"]
    },
    "rescue_operations": {
        "name": "Rescue Operations",
        "domain": "public_safety",
        "description": "Performing technical rescue operations including vertical rescue, confined space, and emergency rescue",
        "keywords": ["rescue", "rescue operations", "technical rescue", "urban rescue", "rope rescue", "confined space rescue", "SES"]
    },
    "lifesaving": {
        "name": "Lifeguarding Services",
        "domain": "public_safety",
        "description": "Providing lifeguard services at pools and beaches including water rescue, CPR, and aquatic safety",
        "keywords": ["lifesaving", "lifeguard", "pool lifeguard", "surf lifesaving", "beach patrol", "water rescue", "aquatic safety"]
    },
    
    # Defence
    "military_operations": {
        "name": "Military Operations",
        "domain": "public_safety",
        "description": "Serving in military and defence operations including combat, peacekeeping, and defence force duties",
        "keywords": ["military", "defence", "army", "navy", "air force", "ADF", "military operations", "combat"]
    },
    "military_logistics": {
        "name": "Defence Logistics",
        "domain": "public_safety",
        "description": "Managing defence logistics including supply chain, procurement, and military equipment support",
        "keywords": ["military logistics", "defence logistics", "military supply", "quartermaster", "defence supply chain"]
    },
    
    # Corrections
    "corrections": {
        "name": "Corrections Custodial",
        "domain": "public_safety",
        "description": "Working in correctional facilities including prisoner supervision, security, and rehabilitation programs",
        "keywords": ["corrections", "correctional officer", "prison", "custodial", "correctional services", "jail", "detention"]
    },
    
    # Traffic & Road Safety
    "traffic_control": {
        "name": "Traffic Control",
        "domain": "public_safety",
        "description": "Controlling traffic at worksites and events using stop-slow procedures and traffic management plans",
        "keywords": ["traffic control", "traffic controller", "stop slow", "road traffic", "traffic management", "TC", "traffic marshal"]
    },
    "parking_enforcement": {
        "name": "Parking Enforcement",
        "domain": "public_safety",
        "description": "Enforcing parking regulations including issuing infringements, patrols, and parking compliance",
        "keywords": ["parking", "parking officer", "parking enforcement", "parking inspector", "infringement", "parking patrol"]
    },
    
    # Emergency Management
    "emergency_management": {
        "name": "Emergency Management",
        "domain": "public_safety",
        "description": "Managing emergency response to disasters and major incidents including emergency operations centres, disaster coordination, evacuation planning, and disaster recovery.",
        "keywords": ['emergency management', 'disaster management', 'emergency operations', 'disaster response', 'EOC', 'evacuation', 'disaster recovery', 'emergency coordination', 'major incident']
    },
    "emergency_dispatch": {
        "name": "Emergency Dispatch",
        "domain": "public_safety",
        "description": "Dispatching emergency services including 000 call taking, CAD systems, and emergency coordination",
        "keywords": ["emergency dispatch", "000", "triple zero", "dispatch", "emergency call", "call taker", "emergency communications"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # UTILITIES, RESOURCES & INFRASTRUCTURE (40 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Electrical Infrastructure
    "powerline_work": {
        "name": "Powerline Work",
        "domain": "utilities_resources",
        "description": "Working on overhead powerlines including construction, maintenance, and repair of electrical transmission and distribution lines.",
        "keywords": ["powerline", "overhead power", "lineworker", "power pole", "transmission", "distribution lines", "powerline maintenance"]
    },
    "underground_cables": {
        "name": "Underground Cabling",
        "domain": "utilities_resources",
        "description": "Installing underground electrical cables including trenching, jointing, and cable termination",
        "keywords": ["underground cable", "cable jointing", "cable installation", "HV cable", "underground power", "cable laying"]
    },
    "substation_work": {
        "name": "Substation Operations",
        "domain": "utilities_resources",
        "description": "Operating electrical substations including high voltage switching, maintenance, and substation equipment",
        "keywords": ["substation", "electrical substation", "transformer", "switchyard", "high voltage", "substation maintenance"]
    },
    
    # Telecommunications
    "nbn_installation": {
        "name": "Fibre Network Installation",
        "domain": "utilities_resources",
        "description": "Installing National Broadband Network connections including fibre, fixed wireless, and HFC installations.",
        "keywords": ["NBN", "fibre installation", "NBN installation", "FTTP", "FTTN", "fibre optic", "NBN technician"]
    },
    "telecommunications_cabling": {
        "name": "Telecommunications Cabling",
        "domain": "utilities_resources",
        "description": "Installing telecommunications cables including copper and fibre optic cables for phone and data networks.",
        "keywords": ["telecommunications", "telco", "cabling", "phone line", "telecom", "communications cabling", "pit and pipe"]
    },
    "tower_climbing": {
        "name": "Tower Climbing",
        "domain": "utilities_resources",
        "description": "Climbing telecommunications and transmission towers for installation and maintenance of antennas and equipment.",
        "keywords": ["tower climbing", "tower technician", "telecommunications tower", "antenna", "tower installation", "rigging"]
    },
    
    # Water & Wastewater
    "water_treatment": {
        "name": "Water Treatment",
        "domain": "utilities_resources",
        "description": "Operating water treatment plants and systems including filtration, disinfection, and potable water production.",
        "keywords": ["water treatment", "water plant", "potable water", "water quality", "filtration", "chlorination", "water treatment operator"]
    },
    "wastewater_treatment": {
        "name": "Wastewater Treatment",
        "domain": "utilities_resources",
        "description": "Operating wastewater treatment plants including sewage processing, biological treatment, and effluent management.",
        "keywords": ["wastewater", "sewage treatment", "wastewater plant", "effluent", "sludge", "wastewater operator", "STP"]
    },
    "water_network": {
        "name": "Water Network Operations",
        "domain": "utilities_resources",
        "description": "Operating and maintaining water distribution networks including pipes, valves, pumps, and reticulation systems.",
        "keywords": ["water network", "water main", "water pipe", "water reticulation", "water infrastructure", "water distribution"]
    },
    "sewer_network": {
        "name": "Sewer Network Operations",
        "domain": "utilities_resources",
        "description": "Operating and maintaining sewer collection networks including pipes, manholes, pump stations, and sewer infrastructure.",
        "keywords": ["sewer", "sewer main", "sewer network", "sewerage", "sewer maintenance", "sewer cleaning", "CCTV inspection"]
    },
    
    # Gas
    "gas_distribution": {
        "name": "Gas Distribution",
        "domain": "utilities_resources",
        "description": "Operating and maintaining gas distribution networks including pipelines, regulators, and gas infrastructure.",
        "keywords": ["gas distribution", "gas network", "gas main", "natural gas", "gas pipeline", "gas infrastructure"]
    },
    "gas_metering": {
        "name": "Gas Metering Installation",
        "domain": "utilities_resources",
        "description": "Installing and maintaining gas meters and metering equipment for residential and commercial gas supply.",
        "keywords": ["gas meter", "gas metering", "meter reading", "meter installation", "gas measurement", "gas connection"]
    },
    
    # Renewable Energy
    "solar_pv_systems": {
        "name": "Solar PV Systems",
        "domain": "utilities_resources",
        "description": "Installing and maintaining solar photovoltaic systems including panels, inverters, and grid-connected solar installations.",
        "keywords": ["solar PV", "solar panel", "photovoltaic", "solar installation", "solar system", "rooftop solar", "solar inverter"]
    },
    "wind_turbine": {
        "name": "Wind Turbine Maintenance",
        "domain": "utilities_resources",
        "description": "Operating and maintaining wind turbines including mechanical, electrical, and blade maintenance at wind farms.",
        "keywords": ["wind turbine", "wind farm", "wind energy", "turbine maintenance", "wind power", "wind technician"]
    },
    "battery_storage": {
        "name": "Battery Storage Systems",
        "domain": "utilities_resources",
        "description": "Installing and maintaining battery energy storage systems including lithium-ion batteries and grid storage solutions.",
        "keywords": ["battery storage", "energy storage", "battery system", "BESS", "lithium battery", "grid storage"]
    },
    
    # Mining
    "underground_mining": {
        "name": "Underground Mining",
        "domain": "utilities_resources",
        "description": "Working in underground mining operations including development, production, and underground mine services.",
        "keywords": ["underground mining", "underground mine", "mining", "miner", "stoping", "development", "long wall", "coal mining"]
    },
    "surface_mining": {
        "name": "Surface Mining",
        "domain": "utilities_resources",
        "description": "Working in surface mining operations including open cut mining, quarrying, and overburden removal.",
        "keywords": ["surface mining", "open cut", "open pit", "strip mining", "quarry", "surface mine", "overburden"]
    },
    "drilling_blasting": {
        "name": "Drilling Blasting",
        "domain": "utilities_resources",
        "description": "Performing drilling and blasting operations for mining, quarrying, and civil construction.",
        "keywords": ["drilling", "blasting", "blast", "drill rig", "explosives", "shotfirer", "blast hole", "detonation"]
    },
    "mining_equipment": {
        "name": "Mining Equipment Operation",
        "domain": "utilities_resources",
        "description": "Operating heavy mining equipment including haul trucks, excavators, loaders, and draglines in mining operations.",
        "keywords": ["mining equipment", "haul truck", "excavator", "loader", "dozer", "mining machinery", "dump truck"]
    },
    "mineral_processing": {
        "name": "Mineral Processing",
        "domain": "utilities_resources",
        "description": "Operating mineral processing plants including crushing, grinding, flotation, and ore beneficiation.",
        "keywords": ["mineral processing", "processing plant", "crushing", "grinding", "flotation", "ore processing", "concentrator"]
    },
    
    # Oil & Gas
    "drilling_rigs": {
        "name": "Drilling Rig Operations",
        "domain": "utilities_resources",
        "description": "Operating drilling rigs for oil and gas exploration, water bores, or mineral exploration.",
        "keywords": ["drilling rig", "oil drilling", "gas drilling", "derrick", "roughneck", "driller", "rig operations"]
    },
    "pipeline_operations": {
        "name": "Pipeline Operations",
        "domain": "utilities_resources",
        "description": "Operating oil and gas pipelines including pipeline monitoring, pigging, and pipeline integrity management.",
        "keywords": ["pipeline", "pipeline operations", "oil pipeline", "gas pipeline", "pipeline maintenance", "pigging"]
    },
    
    # Civil Infrastructure
    "road_construction": {
        "name": "Road Construction",
        "domain": "utilities_resources",
        "description": "Constructing roads including pavement laying, road base preparation, and road surfacing.",
        "keywords": ["road construction", "road building", "asphalt", "bitumen", "pavement", "road works", "road maintenance"]
    },
    "earthmoving": {
        "name": "Earthmoving Operations",
        "domain": "utilities_resources",
        "description": "Operating earthmoving equipment including excavators, bulldozers, graders, and loaders for civil construction.",
        "keywords": ["earthmoving", "excavation", "excavator", "bulldozer", "grader", "backhoe", "earthworks", "cut and fill"]
    },
    "bridge_construction": {
        "name": "Bridge Construction",
        "domain": "utilities_resources",
        "description": "Constructing bridges and bridge structures including formwork, reinforcement, and bridge deck construction.",
        "keywords": ["bridge construction", "bridge", "bridge building", "bridge maintenance", "structural bridge", "bridge deck"]
    },
    "tunnel_construction": {
        "name": "Tunnel Construction",
        "domain": "utilities_resources",
        "description": "Constructing tunnels using boring machines, drill and blast, or cut and cover methods.",
        "keywords": ["tunnel", "tunnelling", "TBM", "tunnel construction", "underground construction", "tunnel boring"]
    },
    "civil_surveying": {
        "name": "Civil Surveying",
        "domain": "utilities_resources",
        "description": "Conducting civil engineering surveys including set out, levelling, and survey data collection for construction projects.",
        "keywords": ["surveying", "survey", "surveyor", "civil survey", "set out", "GPS survey", "total station", "levels"]
    },
    
    # Environment
    "environmental_monitoring": {
        "name": "Environmental Monitoring",
        "domain": "utilities_resources",
        "description": "Monitoring environmental conditions in the field including water sampling, air quality monitoring, wildlife monitoring, ecological surveys, and environmental data collection.",
        "keywords": ['environmental monitoring', 'environmental sampling', 'water sampling', 'air quality', 'wildlife monitoring', 'ecological survey', 'environmental testing', 'habitat monitoring', 'population monitoring']
    },
    "contamination_assessment": {
        "name": "Contamination Assessment",
        "domain": "utilities_resources",
        "description": "Assessing contaminated sites including soil sampling, groundwater investigation, and contamination remediation planning.",
        "keywords": ["contamination", "contaminated site", "soil testing", "groundwater", "remediation", "site assessment"]
    },
    "waste_management": {
        "name": "Waste Management",
        "domain": "utilities_resources",
        "description": "Managing waste collection and disposal including landfill operations, waste transfer, and waste services.",
        "keywords": ["waste management", "waste collection", "garbage", "landfill", "waste disposal", "refuse", "rubbish collection"]
    },
    "recycling": {
        "name": "Recycling Operations",
        "domain": "utilities_resources",
        "description": "Operating recycling facilities including material sorting, processing, and resource recovery operations",
        "keywords": ["recycling", "recycling plant", "sorting", "materials recovery", "MRF", "recyclables", "resource recovery"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SCIENCE, LABORATORY & TECHNICAL SERVICES (30 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Laboratory
    "laboratory_techniques": {
        "name": "Laboratory Techniques",
        "domain": "science_technical",
        "description": "Performing general laboratory procedures including sample preparation, documentation, and laboratory safety.",
        "keywords": ["laboratory", "lab techniques", "laboratory skills", "lab work", "laboratory procedures", "lab assistant"]
    },
    "chemical_analysis": {
        "name": "Chemical Analysis",
        "domain": "science_technical",
        "description": "Performing chemical laboratory analysis including wet chemistry, titrations, and analytical testing in a laboratory environment.",
        "keywords": ["chemical analysis", "chemistry", "chemical testing", "analytical chemistry", "titration", "spectroscopy", "chromatography"]
    },
    "microbiological_testing": {
        "name": "Microbiological Testing",
        "domain": "science_technical",
        "description": "Performing microbiological laboratory testing including culture techniques, sterile procedures, and microbial identification.",
        "keywords": ["microbiology", "microbiological", "bacteria", "culture", "microbial testing", "sterile technique", "incubation"]
    },
    "pathology_testing": {
        "name": "Pathology Testing",
        "domain": "science_technical",
        "description": "Performing medical pathology tests in clinical laboratories including haematology, biochemistry, and diagnostic testing.",
        "keywords": ["pathology", "medical laboratory", "blood testing", "haematology", "biochemistry", "pathology lab", "diagnostic testing"]
    },
    "histology": {
        "name": "Histology Processing",
        "domain": "science_technical",
        "description": "Preparing and examining tissue samples for microscopic analysis including sectioning, staining, and histological techniques.",
        "keywords": ["histology", "histopathology", "tissue processing", "embedding", "microtome", "staining", "tissue sections"]
    },
    "molecular_biology": {
        "name": "Molecular Biology",
        "domain": "science_technical",
        "description": "Performing molecular biology techniques including PCR, DNA extraction, gel electrophoresis, and genetic analysis.",
        "keywords": ["molecular biology", "PCR", "DNA", "RNA", "gene", "sequencing", "molecular techniques", "gel electrophoresis"]
    },
    "sample_preparation": {
        "name": "Sample Preparation",
        "domain": "science_technical",
        "description": "Preparing samples for laboratory analysis including extraction, digestion, filtration, and sample handling.",
        "keywords": ["sample preparation", "sample collection", "specimen", "sample handling", "sample processing", "specimen preparation"]
    },
    
    # Environmental Science
    "water_testing": {
        "name": "Water Quality Testing",
        "domain": "science_technical",
        "description": "Testing water samples in laboratories for quality, contamination, and compliance including chemical and microbiological analysis.",
        "keywords": ["water testing", "water analysis", "water quality", "water sampling", "pH testing", "water chemistry"]
    },
    "soil_testing": {
        "name": "Soil Testing",
        "domain": "science_technical",
        "description": "Analysing soil samples in laboratories for agricultural, environmental, or construction purposes including chemical and physical testing.",
        "keywords": ["soil testing", "soil analysis", "soil sampling", "soil chemistry", "soil science", "agronomy"]
    },
    "air_quality_testing": {
        "name": "Air Quality Testing",
        "domain": "science_technical",
        "description": "Monitoring and testing air quality including emissions testing, particulate analysis, and atmospheric sampling.",
        "keywords": ["air quality", "air testing", "emissions", "air monitoring", "air sampling", "particulate", "gas analysis"]
    },
    
    # Food Science
    "food_testing": {
        "name": "Food Testing",
        "domain": "science_technical",
        "description": "Testing food products in laboratories for safety, quality, and nutritional analysis including microbiological and chemical testing.",
        "keywords": ["food testing", "food analysis", "food safety testing", "food quality", "nutritional analysis", "food laboratory"]
    },
    "sensory_evaluation": {
        "name": "Sensory Evaluation",
        "domain": "science_technical",
        "description": "Conducting sensory testing and evaluation of food and beverage products including taste panels and sensory analysis.",
        "keywords": ["sensory evaluation", "sensory testing", "taste testing", "sensory panel", "flavour", "food sensory"]
    },
    
    # Research
    "research_methods": {
        "name": "Research Methodology",
        "domain": "science_technical",
        "description": "Applying scientific research methodology including experimental design, literature review, and research protocols.",
        "keywords": ["research methods", "research", "scientific research", "methodology", "research design", "data collection"]
    },
    "statistical_analysis": {
        "name": "Statistical Analysis",
        "domain": "science_technical",
        "description": "Performing statistical analysis of research and laboratory data using SPSS, R, or similar statistical software.",
        "keywords": ["statistical analysis", "statistics", "SPSS", "data analysis", "statistical methods", "hypothesis testing"]
    },
    
    # Geology
    "geological_sampling": {
        "name": "Geological Sampling",
        "domain": "science_technical",
        "description": "Collecting and analysing geological samples including core logging, rock sampling, and geological field work.",
        "keywords": ["geological sampling", "core logging", "rock sampling", "geology", "mineral sampling", "drill core", "geological survey"]
    },
    
    # Animal Science
    "animal_research": {
        "name": "Animal Research",
        "domain": "science_technical",
        "description": "Working with laboratory animals in research facilities including animal husbandry, breeding colonies, behavior monitoring, species behavior, behavioral assessment, pup fostering, mother-pup interactions, bonding assessment, weaning, and animal ethics compliance.",
        "keywords": ['animal research', 'laboratory animals', 'animal technician', 'vivarium', 'animal breeding', 'animal behavior', 'animal behaviour', 'species behavior', 'behavioral assessment', 'pup fostering', 'mother pup bonding', 'bonding monitoring', 'pup interactions', 'litter management', 'animal husbandry', 'foster mother', 'pup care']
    },
    
    # Forensics
    "forensic_analysis": {
        "name": "Forensic Analysis",
        "domain": "science_technical",
        "description": "Analysing forensic evidence in laboratories including fingerprints, DNA, trace evidence, and crime scene analysis.",
        "keywords": ["forensic", "forensic analysis", "forensic science", "evidence", "crime scene", "DNA forensics", "fingerprint"]
    },
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SPORT, FITNESS & RECREATION (30 families)
    # ═══════════════════════════════════════════════════════════════════════════
    
    # Fitness
    "personal_training": {
        "name": "Personal Training",
        "domain": "sport_recreation",
        "description": "Providing personal fitness training including exercise prescription, motivation, and one-on-one coaching",
        "keywords": ["personal training", "personal trainer", "PT", "fitness training", "one-on-one training", "fitness coach"]
    },
    "group_fitness": {
        "name": "Group Fitness Instruction",
        "domain": "sport_recreation",
        "description": "Instructing group fitness classes including aerobics, HIIT, spin, and group exercise programming",
        "keywords": ["group fitness", "group exercise", "fitness class", "aerobics", "spin class", "HIIT", "circuit class"]
    },
    "gym_instruction": {
        "name": "Gym Instruction",
        "domain": "sport_recreation",
        "description": "Providing gym floor instruction including equipment induction, exercise technique, and member support",
        "keywords": ["gym instruction", "gym instructor", "gym floor", "fitness instruction", "weights", "resistance training"]
    },
    "strength_conditioning": {
        "name": "Strength Conditioning",
        "domain": "sport_recreation",
        "description": "Training athletes in strength and conditioning including periodisation, power, and athletic performance",
        "keywords": ["strength and conditioning", "S&C", "athletic training", "power training", "sports conditioning"]
    },
    "yoga_instruction": {
        "name": "Yoga Instruction",
        "domain": "sport_recreation",
        "description": "Teaching yoga classes including asanas, breathing, meditation, and various yoga styles",
        "keywords": ["yoga", "yoga instructor", "yoga teacher", "Hatha", "Vinyasa", "yoga class", "asana"]
    },
    "pilates_instruction": {
        "name": "Pilates Instruction",
        "domain": "sport_recreation",
        "description": "Teaching Pilates including mat work, reformer, and clinical Pilates instruction",
        "keywords": ["Pilates", "Pilates instructor", "reformer", "mat Pilates", "clinical Pilates", "Pilates class"]
    },
    
    # Aquatics
    "swimming_instruction": {
        "name": "Swimming Instruction",
        "domain": "sport_recreation",
        "description": "Teaching swimming including learn-to-swim, stroke correction, and water safety education",
        "keywords": ["swimming instruction", "swim teacher", "learn to swim", "swimming lessons", "swim coach", "swim school"]
    },
    "pool_operations": {
        "name": "Aquatic Facility Operations",
        "domain": "sport_recreation",
        "description": "Operating swimming pool facilities including water quality, plant room, and aquatic facility management",
        "keywords": ["pool operations", "pool plant", "pool maintenance", "pool chemistry", "aquatic facility", "pool technician"]
    },
    "aquatic_programming": {
        "name": "Aquatic Programs",
        "domain": "sport_recreation",
        "description": "Developing aquatic programs including water aerobics, squad training, and aquatic activities",
        "keywords": ["aquatic programs", "aqua aerobics", "aquatic fitness", "water exercise", "hydrotherapy", "aquatic therapy"]
    },
    
    # Sport
    "sports_coaching": {
        "name": "Sports Coaching",
        "domain": "sport_recreation",
        "description": "Coaching sports including skill development, team coaching, and athletic development",
        "keywords": ["sports coaching", "coach", "sports coach", "team coaching", "athletic coaching", "sports development"]
    },
    "sports_officiating": {
        "name": "Sports Officiating",
        "domain": "sport_recreation",
        "description": "Officiating sports as referee or umpire including rules application and match officiating",
        "keywords": ["officiating", "referee", "umpire", "sports official", "refereeing", "match official", "rules"]
    },
    "sports_administration": {
        "name": "Sports Administration",
        "domain": "sport_recreation",
        "description": "Administering sports organisations including club management, events, and sports governance",
        "keywords": ["sports administration", "sports management", "club administration", "sports club", "sport governance"]
    },
    "athlete_management": {
        "name": "Athlete Management",
        "domain": "sport_recreation",
        "description": "Managing athletes including performance support, career management, and elite sport coordination",
        "keywords": ["athlete management", "athlete", "sports performance", "high performance", "elite sport", "athlete development"]
    },
    
    # Outdoor
    "outdoor_recreation": {
        "name": "Outdoor Recreation",
        "domain": "sport_recreation",
        "description": "Leading outdoor recreation activities including bushwalking, camping, and adventure activities",
        "keywords": ["outdoor recreation", "outdoor activities", "adventure", "outdoor education", "bushwalking", "camping"]
    },
    "rock_climbing": {
        "name": "Climbing Abseiling Instruction",
        "domain": "sport_recreation",
        "description": "Instructing climbing and abseiling including indoor climbing, outdoor guiding, and rope techniques",
        "keywords": ["rock climbing", "climbing", "abseiling", "bouldering", "climbing instruction", "belay", "climbing wall"]
    },
    "kayaking_canoeing": {
        "name": "Paddle Sports Instruction",
        "domain": "sport_recreation",
        "description": "Instructing paddle sports including kayaking, canoeing, SUP, and water safety",
        "keywords": ["kayaking", "canoeing", "paddling", "kayak", "canoe", "white water", "sea kayaking"]
    },
    "scuba_diving": {
        "name": "Scuba Diving Instruction",
        "domain": "sport_recreation",
        "description": "Instructing scuba diving including certification courses, dive guiding, and dive operations",
        "keywords": ["scuba diving", "diving", "dive instructor", "PADI", "scuba", "dive master", "underwater"]
    },
    "skiing_snowboarding": {
        "name": "Snow Sports Instruction",
        "domain": "sport_recreation",
        "description": "Instructing snow sports including skiing, snowboarding, and snow sport techniques",
        "keywords": ["skiing", "snowboarding", "ski instructor", "snow sports", "ski school", "snowboard instructor"]
    },
    "golf_instruction": {
        "name": "Golf Coaching",
        "domain": "sport_recreation",
        "description": "Coaching golf including swing technique, course management, and golf instruction",
        "keywords": ["golf", "golf instruction", "golf coach", "golf pro", "golf lesson", "golf swing", "golf teaching"]
    },
    "tennis_coaching": {
        "name": "Tennis Coaching",
        "domain": "sport_recreation",
        "description": "Coaching tennis including stroke technique, tactics, and tennis player development",
        "keywords": ["tennis", "tennis coaching", "tennis coach", "tennis instruction", "tennis lesson", "racquet sports"]
    },
    "martial_arts": {
        "name": "Martial Arts Instruction",
        "domain": "sport_recreation",
        "description": "Teaching martial arts including technique, self-defence, and martial arts discipline",
        "keywords": ["martial arts", "karate", "taekwondo", "judo", "jiu-jitsu", "martial arts instructor", "self-defence"]
    },
    "greenhouse_hydroponics": {
        "name": "Controlled Environment Horticulture",
        "domain": "agriculture_primary",
        "description": "Controlled environment agriculture and soilless growing",
        "keywords": ['greenhouse', 'hydroponics', 'glasshouse', 'controlled environment', 'NFT', 'aquaponics', 'vertical farming', 'grow lights']
    },
    "agricultural_machinery": {
        "name": "Agricultural Machinery Operation",
        "domain": "agriculture_primary",
        "description": "Operating farm machinery including tractors, harvesters, headers, and agricultural implements",
        "keywords": ['tractor', 'harvester', 'combine', 'farm machinery', 'agricultural equipment', 'seeder', 'sprayer', 'GPS guidance']
    },
    "seed_production": {
        "name": "Seed Production",
        "domain": "agriculture_primary",
        "description": "Producing certified seed including growing, harvesting, processing, cleaning, and seed quality testing",
        "keywords": ['seed production', 'seed certification', 'seed processing', 'seed cleaning', 'seed testing', 'germination', 'seed saving']
    },
    "organic_farming": {
        "name": "Organic Farming",
        "domain": "agriculture_primary",
        "description": "Organic certification and regenerative agriculture practices",
        "keywords": ['organic farming', 'organic certification', 'regenerative', 'biodynamic', 'permaculture', 'no-till', 'cover cropping', 'composting']
    },
    "alpaca_llama": {
        "name": "Alpaca Llama Husbandry",
        "domain": "agriculture_primary",
        "description": "Managing alpacas or llamas including breeding, birthing (unpacking), cria care, fibre production, and camelid husbandry.",
        "keywords": ['alpaca', 'llama', 'alpaca husbandry', 'alpaca breeding', 'cria', 'unpacking', 'camelid', 'fleece', 'alpaca shearing', 'fibre animal']
    },
    "mushroom_production": {
        "name": "Mushroom Cultivation",
        "domain": "agriculture_primary",
        "description": "Growing mushrooms commercially in controlled environments including composting, spawning, and harvesting",
        "keywords": ['mushroom', 'mushroom growing', 'mushroom production', 'spawn', 'substrate', 'fungi', 'oyster mushroom', 'shiitake']
    },
    "olive_production": {
        "name": "Olive Production",
        "domain": "agriculture_primary",
        "description": "Growing olives and producing olive oil including orchard management, harvesting, and oil pressing",
        "keywords": ['olive', 'olive growing', 'olive oil', 'olive grove', 'olive harvest', 'olive press', 'extra virgin']
    },
    "wheel_alignment": {
        "name": "Wheel Alignment",
        "domain": "automotive_repair",
        "description": "Performing wheel alignment including camber, caster, toe adjustment, and steering geometry.",
        "keywords": ['wheel alignment', 'alignment', 'camber', 'caster', 'toe', 'thrust angle', 'alignment machine', 'steering geometry']
    },
    "battery_service": {
        "name": "Battery Service",
        "domain": "automotive_repair",
        "description": "Testing and replacing vehicle batteries including battery diagnostics, charging systems, and jump starting.",
        "keywords": ['battery service', 'battery testing', 'battery replacement', 'car battery', 'battery charging', 'jump start', 'battery diagnostics']
    },
    "fuel_systems": {
        "name": "Fuel System Service",
        "domain": "automotive_repair",
        "description": "Servicing petrol fuel systems including fuel pumps, injectors, and fuel system diagnostics.",
        "keywords": ['fuel system', 'fuel pump', 'fuel injector', 'fuel filter', 'fuel tank', 'petrol system', 'fuel line', 'fuel pressure']
    },
    "window_tinting": {
        "name": "Window Tinting",
        "domain": "automotive_repair",
        "description": "Applying window tint film to vehicles including UV protection and privacy film installation.",
        "keywords": ['window tinting', 'tint', 'window film', 'car tinting', 'tint film', 'UV protection', 'privacy film']
    },
    "caravan_rv_repair": {
        "name": "Caravan RV Repair",
        "domain": "automotive_repair",
        "description": "Repairing caravans and motorhomes including appliances, plumbing, and RV-specific systems.",
        "keywords": ['caravan', 'RV', 'motorhome', 'caravan repair', 'camper', 'caravan service', 'RV maintenance', 'camper trailer']
    },
    "procurement": {
        "name": "Procurement Purchasing",
        "domain": "business_administration",
        "description": "Procuring corporate goods and services including strategic sourcing, supplier contract negotiation, vendor management, and organisational purchasing processes.",
        "keywords": ['procurement', 'purchasing', 'strategic sourcing', 'supplier management', 'vendor management', 'purchase order', 'contract negotiation', 'corporate purchasing', 'supply procurement']
    },
    "tender_writing": {
        "name": "Tender Writing",
        "domain": "business_administration",
        "description": "Writing tenders and bids including proposals, RFT responses, and bid management.",
        "keywords": ['tender writing', 'bid writing', 'tender', 'RFT', 'proposal writing', 'tender response', 'bid management', 'EOI']
    },
    "grant_writing": {
        "name": "Grant Writing",
        "domain": "business_administration",
        "description": "Writing grant applications including funding proposals, acquittals, and grant management.",
        "keywords": ['grant writing', 'grant application', 'funding', 'grant management', 'acquittal', 'grant submission', 'funding proposal']
    },
    "governance_compliance": {
        "name": "Corporate Governance",
        "domain": "business_administration",
        "description": "Managing corporate governance including board meetings, regulatory compliance, and company secretarial duties",
        "keywords": ['governance', 'compliance', 'board governance', 'regulatory compliance', 'company secretary', 'corporate governance', 'board papers', 'AGM']
    },
    "credit_control": {
        "name": "Credit Control",
        "domain": "finance_accounting",
        "description": "Managing financial credit and debt collection including debtor follow-up, overdue account recovery, payment terms negotiation, and accounts receivable debt management. Financial debt only.",
        "keywords": ['credit control', 'debt collection', 'debt recovery', 'overdue accounts', 'debtor management', 'financial debt', 'accounts receivable', 'payment collection', 'bad debt']
    },
    "risk_management": {
        "name": "Risk Management",
        "domain": "business_administration",
        "description": "Managing corporate enterprise risk including business risk assessment, risk registers, risk mitigation strategies, and organisational risk frameworks. Corporate risk management.",
        "keywords": ['enterprise risk', 'risk management', 'risk assessment', 'risk register', 'risk mitigation', 'corporate risk', 'business risk', 'risk framework', 'risk appetite']
    },
    "insulation_installation": {
        "name": "Insulation Installation",
        "domain": "construction_building",
        "description": "Installing thermal and acoustic insulation in walls, ceilings, and floors.",
        "keywords": ['insulation', 'insulation installation', 'thermal insulation', 'batts', 'wall insulation', 'ceiling insulation', 'acoustic insulation', 'R-value']
    },
    "steel_framing": {
        "name": "Steel Framing",
        "domain": "construction_building",
        "description": "Constructing light steel wall and roof frames using cold-formed steel framing systems.",
        "keywords": ['steel framing', 'steel frame', 'light gauge steel', 'metal framing', 'steel stud', 'steel truss', 'cold formed steel']
    },
    "external_cladding": {
        "name": "External Cladding",
        "domain": "construction_building",
        "description": "Installing external wall cladding including weatherboards, fibre cement, and facade systems.",
        "keywords": ['cladding', 'external cladding', 'weatherboard', 'wall cladding', 'facade', 'James Hardie', 'fibre cement', 'timber cladding']
    },
    "structural_steel_erection": {
        "name": "Structural Steel Erection",
        "domain": "construction_building",
        "description": "Erecting structural steel for buildings and structures including beams, columns, and steel connections.",
        "keywords": ['structural steel', 'steel erection', 'steel structure', 'steel beam', 'steel column', 'bolting', 'steel frame erection']
    },
    "suspended_ceilings": {
        "name": "Suspended Ceiling Installation",
        "domain": "construction_building",
        "description": "Installing suspended ceiling systems including grid ceilings, acoustic tiles, and access panel ceilings",
        "keywords": ['suspended ceiling', 'drop ceiling', 'ceiling grid', 'ceiling tiles', 'T-bar ceiling', 'acoustic ceiling', 'ceiling installation']
    },
    "fire_stopping": {
        "name": "Passive Fire Protection",
        "domain": "construction_building",
        "description": "Fire stopping and passive fire protection installation",
        "keywords": ['fire stopping', 'passive fire', 'fire collar', 'fire seal', 'intumescent', 'fire barrier', 'fire protection', 'fire rating']
    },
    "access_flooring": {
        "name": "Access Flooring Installation",
        "domain": "construction_building",
        "description": "Installing raised access flooring systems for commercial buildings and data centres.",
        "keywords": ['access flooring', 'raised floor', 'raised access floor', 'computer floor', 'access floor tiles', 'pedestal floor']
    },
    "electrical_maintenance_building": {
        "name": "Building Electrical Maintenance",
        "domain": "electrical_communications",
        "description": "Maintaining electrical systems in buildings including fault finding, repairs, and electrical safety testing.",
        "keywords": ['electrical maintenance', 'building electrical', 'electrical service', 'light replacement', 'electrical fault', 'power maintenance']
    },
    "music_composition": {
        "name": "Music Composition",
        "domain": "creative_arts",
        "description": "Composing original music including songwriting, scoring, arranging, and music theory application",
        "keywords": ['music composition', 'composing', 'songwriting', 'composer', 'arrangement', 'orchestration', 'score', 'music theory']
    },
    "voice_acting": {
        "name": "Voice Acting",
        "domain": "creative_arts",
        "description": "Performing voice work including character voices, narration, voice-over, and audio drama",
        "keywords": ['voice acting', 'voice over', 'voiceover', 'VO', 'narration', 'dubbing', 'voice artist', 'ADR']
    },
    "dj_turntablism": {
        "name": "DJ Performance",
        "domain": "creative_arts",
        "description": "Performing as a DJ including mixing, beatmatching, scratching, and live DJ performance",
        "keywords": ['DJ', 'DJing', 'turntable', 'mixing', 'beatmatching', 'scratching', 'club DJ', 'Serato', 'CDJ']
    },
    "foley_sound_design": {
        "name": "Sound Design Foley",
        "domain": "creative_arts",
        "description": "Creating sound effects for film and media including foley recording, sound design, and audio post-production",
        "keywords": ['foley', 'sound design', 'sound effects', 'SFX', 'foley artist', 'film sound', 'audio post', 'sound design']
    },
    "art_restoration": {
        "name": "Art Conservation",
        "domain": "creative_arts",
        "description": "Conserving and restoring fine art including painting restoration, conservation techniques, and art preservation",
        "keywords": ['art restoration', 'conservation', 'art conservation', 'restoration', 'preserving', 'artwork repair', 'painting restoration']
    },
    "calligraphy_lettering": {
        "name": "Calligraphy Lettering",
        "domain": "creative_arts",
        "description": "Creating decorative lettering including calligraphy, hand lettering, sign writing, and typographic art",
        "keywords": ['calligraphy', 'lettering', 'hand lettering', 'brush lettering', 'typography', 'signwriting', 'illumination']
    },
    "framing_mounting": {
        "name": "Picture Framing",
        "domain": "creative_arts",
        "description": "Framing artwork and pictures including mat cutting, frame making, mounting, and conservation framing",
        "keywords": ['picture framing', 'framing', 'mounting', 'matting', 'frame making', 'conservation framing', 'art framing']
    },
    "salesforce_crm": {
        "name": "CRM Development",
        "domain": "digital_technology",
        "description": "Developing and customising Salesforce CRM including Apex programming, Lightning components, and Salesforce administration.",
        "keywords": ['Salesforce', 'CRM', 'Salesforce development', 'Apex', 'Salesforce admin', 'customer relationship management', 'HubSpot', 'Dynamics 365']
    },
    "sap_erp": {
        "name": "ERP Implementation",
        "domain": "digital_technology",
        "description": "Implementing and customising SAP ERP systems including SAP ABAP development, SAP HANA, and SAP modules configuration.",
        "keywords": ['SAP', 'ERP', 'enterprise resource planning', 'SAP ABAP', 'SAP HANA', 'Oracle ERP', 'SAP Fiori', 'SAP S/4HANA']
    },
    "rpa_automation": {
        "name": "Robotic Process Automation",
        "domain": "digital_technology",
        "description": "Automating business processes using robotic process automation tools like UiPath, Blue Prism, or Automation Anywhere.",
        "keywords": ['RPA', 'robotic process automation', 'UiPath', 'Blue Prism', 'Automation Anywhere', 'process automation', 'bot development']
    },
    "low_code_development": {
        "name": "Low-Code Development",
        "domain": "digital_technology",
        "description": "Building applications using low-code platforms like Power Apps, Mendix, OutSystems, or similar visual development tools.",
        "keywords": ['low-code', 'no-code', 'Power Platform', 'Power Apps', 'Mendix', 'OutSystems', 'citizen developer', 'AppSheet']
    },
    "api_management": {
        "name": "API Development",
        "domain": "digital_technology",
        "description": "Designing, developing, and managing RESTful APIs and GraphQL endpoints including documentation, versioning, and gateway configuration.",
        "keywords": ['API', 'API design', 'API management', 'API gateway', 'REST', 'GraphQL', 'OpenAPI', 'Swagger', 'Postman']
    },
    "mainframe_legacy": {
        "name": "Mainframe Systems",
        "domain": "digital_technology",
        "description": "Mainframe programming and legacy system maintenance",
        "keywords": ['mainframe', 'COBOL', 'legacy systems', 'AS/400', 'JCL', 'CICS', 'mainframe programming', 'IBM mainframe']
    },
    "accessibility_testing": {
        "name": "Accessibility Testing",
        "domain": "digital_technology",
        "description": "Testing websites and applications for WCAG compliance, screen reader compatibility, and accessibility for users with disabilities.",
        "keywords": ['accessibility', 'accessibility testing', 'WCAG', 'a11y', 'screen reader', 'accessible design', 'Section 508', 'ARIA']
    },
    "mobile_testing": {
        "name": "Mobile Testing",
        "domain": "digital_technology",
        "description": "Testing mobile applications on iOS and Android devices, including functional testing, UI testing, and mobile test automation with Appium.",
        "keywords": ['mobile testing', 'app testing', 'iOS testing', 'Android testing', 'mobile QA', 'device testing', 'Appium', 'mobile automation']
    },
    "performance_testing": {
        "name": "Performance Testing",
        "domain": "digital_technology",
        "description": "Load testing, stress testing, and performance benchmarking of software applications using JMeter, Gatling, or k6.",
        "keywords": ['performance testing', 'load testing', 'stress testing', 'JMeter', 'performance', 'scalability testing', 'Gatling', 'k6']
    },
    "music_education": {
        "name": "Music Education",
        "domain": "education_training",
        "description": "Teaching music including instrumental lessons, music theory, and music education.",
        "keywords": ['music education', 'music teaching', 'music teacher', 'instrumental teaching', 'piano teacher', 'guitar teacher', 'music lesson']
    },
    "physical_education": {
        "name": "Physical Education",
        "domain": "education_training",
        "description": "Teaching physical education including school sport, HPE, and fitness programs.",
        "keywords": ['physical education', 'PE teacher', 'PE', 'school sport', 'HPE', 'health and physical education', 'sports teacher']
    },
    "tutoring": {
        "name": "Tutoring Services",
        "domain": "education_training",
        "description": "Providing private tutoring for school students including homework help, exam preparation, academic coaching, and subject-specific tutoring.",
        "keywords": ['tutoring', 'private tutor', 'academic coaching', 'homework help', 'exam preparation', 'student tutoring', 'school tutoring']
    },
    "stem_education": {
        "name": "STEM Education",
        "domain": "education_training",
        "description": "Teaching STEM subjects including science, technology, engineering, and mathematics education.",
        "keywords": ['STEM', 'STEM education', 'science teaching', 'coding education', 'robotics education', 'STEAM', 'maker education']
    },
    "art_education": {
        "name": "Visual Arts Teaching",
        "domain": "education_training",
        "description": "Teaching visual arts in schools or community settings including art techniques, creativity, and art appreciation",
        "keywords": ['art education', 'art teacher', 'visual arts teaching', 'art class', 'art workshop', 'creative arts education']
    },
    "drama_education": {
        "name": "Drama Education",
        "domain": "education_training",
        "description": "Teaching drama and theatre including performance, theatre studies, and drama programs.",
        "keywords": ['drama education', 'drama teacher', 'theatre education', 'acting class', 'drama workshop', 'performing arts education']
    },
    "perioperative_nursing": {
        "name": "Perioperative Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care in operating theatres including scrub, scout, anaesthetic, and PACU nursing.",
        "keywords": ['perioperative', 'operating theatre', 'theatre nurse', 'scrub nurse', 'scout nurse', 'anaesthetic nurse', 'recovery', 'PACU']
    },
    "midwifery": {
        "name": "Midwifery Services",
        "domain": "healthcare_clinical",
        "description": "Providing midwifery care for human mothers and babies including antenatal, labour, birth, and postnatal care.",
        "keywords": ['midwifery', 'midwife', 'childbirth', 'antenatal', 'postnatal', 'labour', 'birth', 'human mothers', 'human babies', 'pregnancy']
    },
    "continence_care": {
        "name": "Continence Care",
        "domain": "healthcare_clinical",
        "description": "Providing continence care for patients including bladder and bowel assessment, continence aids, incontinence management, and clinical continence nursing.",
        "keywords": ['continence care', 'incontinence', 'bladder care', 'bowel care', 'continence nursing', 'continence aids', 'patient continence', 'clinical continence']
    },
    "stomal_therapy": {
        "name": "Stomal Therapy",
        "domain": "healthcare_clinical",
        "description": "Providing stomal therapy including ostomy care, stoma management, and patient education.",
        "keywords": ['stomal therapy', 'stoma', 'ostomy', 'stoma care', 'colostomy', 'ileostomy', 'stoma nurse', 'ostomy bag']
    },
    "diabetes_education": {
        "name": "Diabetes Education",
        "domain": "healthcare_clinical",
        "description": "Providing diabetes education including blood glucose management, insulin education, and diabetes self-management.",
        "keywords": ['diabetes education', 'diabetes educator', 'diabetes management', 'blood glucose', 'insulin', 'HbA1c', 'diabetes care']
    },
    "practice_nursing": {
        "name": "Practice Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care in general practice clinics including immunisations, wound care, and chronic disease management.",
        "keywords": ['practice nurse', 'practice nursing', 'GP nursing', 'clinic nurse', 'immunisation', 'health assessment', 'chronic disease management']
    },
    "telehealth": {
        "name": "Telehealth Services",
        "domain": "healthcare_clinical",
        "description": "Delivering healthcare services via telehealth including virtual consultations and remote patient monitoring.",
        "keywords": ['telehealth', 'telemedicine', 'virtual consultation', 'remote health', 'video consultation', 'telehealth nursing']
    },
    "respiratory_care": {
        "name": "Respiratory Care",
        "domain": "healthcare_clinical",
        "description": "Providing respiratory care including oxygen therapy, CPAP, nebulisers, and respiratory assessment.",
        "keywords": ['respiratory care', 'oxygen therapy', 'nebuliser', 'CPAP', 'BiPAP', 'respiratory', 'spirometry', 'peak flow']
    },
    "lymphoedema": {
        "name": "Lymphoedema Therapy",
        "domain": "healthcare_clinical",
        "description": "Providing lymphoedema therapy including compression therapy, manual lymphatic drainage, and lymphoedema management.",
        "keywords": ['lymphoedema', 'lymphedema', 'compression therapy', 'manual lymphatic drainage', 'MLD', 'compression garment', 'swelling']
    },
    "room_service": {
        "name": "Room Service",
        "domain": "hospitality_tourism",
        "description": "Providing hotel room service including order taking, tray service, and in-room dining.",
        "keywords": ['room service', 'in-room dining', 'IRD', 'room service order', 'tray service', 'room delivery']
    },
    "banquet_service": {
        "name": "Banquet Service",
        "domain": "hospitality_tourism",
        "description": "Providing banquet and function service including plated service, buffet, and event catering.",
        "keywords": ['banquet', 'banquet service', 'function service', 'banquet operations', 'event service', 'plated service', 'buffet service']
    },
    "fine_dining": {
        "name": "Fine Dining Service",
        "domain": "hospitality_tourism",
        "description": "Providing fine dining service including silver service, gueridon, and premium restaurant service.",
        "keywords": ['fine dining', 'silver service', 'gueridon', 'fine dining service', 'tableside service', 'wine service', 'degustation']
    },
    "quick_service": {
        "name": "Quick Service Operations",
        "domain": "hospitality_tourism",
        "description": "Working in quick service restaurants including counter service, drive-through, and fast food operations.",
        "keywords": ['quick service', 'QSR', 'fast food', 'drive-through', 'counter service', 'fast casual', 'takeaway']
    },
    "food_truck": {
        "name": "Mobile Food Service",
        "domain": "hospitality_tourism",
        "description": "Operating food trucks and mobile food services including mobile catering, markets, and event food service",
        "keywords": ['food truck', 'mobile catering', 'food van', 'street food', 'mobile kitchen', 'pop-up', 'food stall']
    },
    "butchery_hotel": {
        "name": "Institutional Butchery",
        "domain": "hospitality_tourism",
        "description": "Large-scale meat preparation for hotels and institutions",
        "keywords": ['hotel butchery', 'institutional butchery', 'meat preparation', 'portion control', 'carcass breakdown', 'meat fabrication']
    },
    "cad_cam": {
        "name": "CAD CAM Design",
        "domain": "manufacturing_engineering",
        "description": "Using CAD/CAM software for design and manufacturing including AutoCAD, SolidWorks, and CAM programming for CNC machines.",
        "keywords": ['CAD', 'CAM', 'AutoCAD', 'SolidWorks', 'CAD/CAM', 'computer-aided design', '3D modelling', 'engineering drawing']
    },
    "heat_treatment": {
        "name": "Heat Treatment",
        "domain": "manufacturing_engineering",
        "description": "Performing metal heat treatment processes including hardening, tempering, annealing, and case hardening.",
        "keywords": ['heat treatment', 'hardening', 'tempering', 'annealing', 'quenching', 'case hardening', 'heat treating', 'induction hardening']
    },
    "robotic_welding": {
        "name": "Robotic Welding",
        "domain": "manufacturing_engineering",
        "description": "Operating and programming robotic welding systems for automated welding in manufacturing production lines.",
        "keywords": ['robotic welding', 'welding robot', 'robot programming', 'automated welding', 'robotic cell', 'welding automation']
    },
    "lean_manufacturing": {
        "name": "Lean Manufacturing",
        "domain": "manufacturing_engineering",
        "description": "Implementing lean manufacturing principles including 5S, kaizen, value stream mapping, and waste reduction.",
        "keywords": ['lean manufacturing', 'lean', '5S', 'kaizen', 'value stream', 'waste reduction', 'continuous improvement', 'kanban']
    },
    "statistical_process_control": {
        "name": "Statistical Process Control",
        "domain": "manufacturing_engineering",
        "description": "Applying statistical methods to monitor and control manufacturing processes including control charts, Cp, Cpk, and Six Sigma.",
        "keywords": ['statistical process control', 'SPC', 'control chart', 'Cp', 'Cpk', 'process capability', 'variation', 'six sigma']
    },
    "press_operation": {
        "name": "Press Operation",
        "domain": "manufacturing_engineering",
        "description": "Operating mechanical and hydraulic presses for metal forming, stamping, and pressing operations.",
        "keywords": ['press operation', 'press', 'mechanical press', 'hydraulic press', 'stamping', 'pressing', 'press brake', 'punch press']
    },
    "textile_manufacturing": {
        "name": "Textile Manufacturing",
        "domain": "manufacturing_engineering",
        "description": "Operating textile production equipment including weaving, knitting, and fabric manufacturing machinery.",
        "keywords": ['textile manufacturing', 'weaving', 'knitting', 'textile', 'fabric production', 'textile machine', 'loom', 'spinning']
    },
    "woodworking_machinery": {
        "name": "Woodworking Machinery",
        "domain": "manufacturing_engineering",
        "description": "Operating woodworking machinery including CNC routers, panel saws, edge banders, and timber processing equipment.",
        "keywords": ['woodworking machinery', 'CNC router', 'panel saw', 'edge bander', 'thicknesser', 'wood CNC', 'jointer', 'spindle moulder']
    },
    "k9_handling": {
        "name": "Security Dog Handling",
        "domain": "public_safety",
        "description": "Handling security or detection dogs including patrol dogs, explosive detection, and drug detection canines",
        "keywords": ['K9', 'dog handling', 'security dog', 'detection dog', 'guard dog', 'dog handler', 'canine', 'patrol dog']
    },
    "close_protection": {
        "name": "Close Protection",
        "domain": "public_safety",
        "description": "Providing close personal protection including bodyguard services, executive protection, and VIP security",
        "keywords": ['close protection', 'bodyguard', 'VIP security', 'executive protection', 'personal protection', 'CPO', 'protective services']
    },
    "maritime_security": {
        "name": "Maritime Security",
        "domain": "public_safety",
        "description": "Providing security at ports and maritime facilities including vessel security and port access control",
        "keywords": ['maritime security', 'port security', 'ship security', 'ISPS', 'maritime patrol', 'vessel security', 'port facility security']
    },
    "aviation_security": {
        "name": "Aviation Security",
        "domain": "public_safety",
        "description": "Screening passengers and baggage at airports including x-ray operation and aviation security procedures",
        "keywords": ['aviation security', 'airport security', 'baggage screening', 'passenger screening', 'ASO', 'X-ray screening', 'airport screening']
    },
    "cybercrime_investigation": {
        "name": "Digital Forensics",
        "domain": "public_safety",
        "description": "Investigating cybercrime and digital evidence including computer forensics and electronic evidence recovery",
        "keywords": ['cybercrime', 'digital forensics', 'computer forensics', 'cybercrime investigation', 'digital evidence', 'e-crime']
    },
    "spray_tanning": {
        "name": "Spray Tanning",
        "domain": "retail_services",
        "description": "Applying spray tan including airbrush application, solution selection, and tan preparation",
        "keywords": ['spray tan', 'spray tanning', 'fake tan', 'sunless tan', 'tanning', 'tan application', 'bronzing']
    },
    "teeth_whitening": {
        "name": "Teeth Whitening",
        "domain": "retail_services",
        "description": "Providing cosmetic teeth whitening services in beauty or retail settings using non-clinical whitening systems. Not clinical dental procedures.",
        "keywords": ['teeth whitening', 'cosmetic whitening', 'tooth whitening', 'bleaching', 'beauty teeth', 'non-clinical whitening', 'retail whitening']
    },
    "cosmetic_tattooing": {
        "name": "Cosmetic Tattooing",
        "domain": "retail_services",
        "description": "Applying semi-permanent makeup including microblading, lip blush, and cosmetic tattoo procedures",
        "keywords": ['cosmetic tattooing', 'microblading', 'semi-permanent makeup', 'eyebrow tattooing', 'lip tattooing', 'PMU', 'micropigmentation']
    },
    "hair_extensions": {
        "name": "Hair Extensions",
        "domain": "retail_services",
        "description": "Applying hair extensions including tape-ins, micro-links, fusion, and extension maintenance",
        "keywords": ['hair extensions', 'extensions', 'tape extensions', 'keratin bonds', 'micro rings', 'weave', 'hair extension application']
    },
    "skin_consultation": {
        "name": "Skin Analysis",
        "domain": "retail_services",
        "description": "Analysing skin conditions and providing skincare consultations including product recommendations",
        "keywords": ['skin consultation', 'skin analysis', 'skin assessment', 'skincare consultation', 'skin type', 'skin condition', 'dermascope']
    },
    "florist": {
        "name": "Floristry Design",
        "domain": "retail_services",
        "description": "Creating floral arrangements including bouquets, installations, event floristry, and flower care",
        "keywords": ['floristry', 'florist', 'floral design', 'flower arrangement', 'bouquet', 'floral', 'wedding flowers', 'flower shop']
    },
    "shoe_repair": {
        "name": "Shoe Repair",
        "domain": "retail_services",
        "description": "Repairing footwear including sole replacement, heel repairs, and leather goods restoration",
        "keywords": ['shoe repair', 'cobbler', 'shoe restoration', 'heel replacement', 'sole replacement', 'leather repair', 'shoe care']
    },
    "watch_repair": {
        "name": "Watch Repair Horology",
        "domain": "retail_services",
        "description": "Repairing watches and clocks including movement servicing, battery replacement, and horology",
        "keywords": ['watch repair', 'watchmaker', 'horology', 'watch service', 'watch movement', 'clock repair', 'watch restoration']
    },
    "calibration": {
        "name": "Instrument Calibration",
        "domain": "science_technical",
        "description": "Calibrating laboratory and industrial instruments to traceable standards ensuring measurement accuracy and compliance.",
        "keywords": ['calibration', 'instrument calibration', 'calibration certificate', 'measurement', 'traceability', 'verification', 'calibration lab']
    },
    "spectroscopy": {
        "name": "Spectroscopy Analysis",
        "domain": "science_technical",
        "description": "Operating spectroscopy instruments including UV-Vis, IR, and atomic absorption for chemical compound identification and quantification.",
        "keywords": ['spectroscopy', 'spectrometry', 'UV-Vis', 'IR spectroscopy', 'NMR', 'atomic absorption', 'spectrophotometer', 'spectrum']
    },
    "mass_spectrometry": {
        "name": "Mass Spectrometry",
        "domain": "science_technical",
        "description": "Operating mass spectrometry instruments including LC-MS and GC-MS for molecular identification and analysis.",
        "keywords": ['mass spectrometry', 'MS', 'LC-MS', 'GC-MS', 'mass spec', 'ion', 'mass spectrometer', 'chromatography']
    },
    "pharmaceutical_testing": {
        "name": "Pharmaceutical Testing",
        "domain": "science_technical",
        "description": "Testing pharmaceutical products for quality control including assay, dissolution, stability, and drug testing in pharmaceutical labs.",
        "keywords": ['pharmaceutical testing', 'drug testing', 'pharmaceutical QC', 'stability testing', 'dissolution', 'assay', 'pharmaceutical analysis']
    },
    "clinical_trials": {
        "name": "Clinical Trials Coordination",
        "domain": "science_technical",
        "description": "Coordinating clinical research trials including patient recruitment, protocol compliance, GCP, and clinical data management.",
        "keywords": ['clinical trials', 'clinical research', 'CRA', 'clinical trial coordinator', 'GCP', 'protocol', 'patient recruitment', 'regulatory']
    },
    "cytology": {
        "name": "Cytology Cell Analysis",
        "domain": "science_technical",
        "description": "Analysing cell samples including Pap smears and cytological specimens for diagnostic pathology.",
        "keywords": ['cytology', 'cytological', 'cell analysis', 'Pap smear', 'cervical cytology', 'cytopathology', 'cell staining']
    },
    "immunology_testing": {
        "name": "Immunology Testing",
        "domain": "science_technical",
        "description": "Performing immunological laboratory assays including ELISA, antibody testing, and serology in diagnostic laboratories.",
        "keywords": ['immunology', 'immunoassay', 'ELISA', 'antibody', 'serology', 'immunological testing', 'antigen', 'immunology lab']
    },
    "chromatography": {
        "name": "Chromatography Analysis",
        "domain": "science_technical",
        "description": "Operating chromatography equipment including HPLC and gas chromatography for separation and analysis of chemical compounds.",
        "keywords": ['chromatography', 'HPLC', 'gas chromatography', 'GC', 'LC', 'column', 'separation', 'chromatograph']
    },
    "dance_instruction": {
        "name": "Dance Instruction",
        "domain": "sport_recreation",
        "description": "Teaching dance including ballet, contemporary, ballroom, and dance technique across styles",
        "keywords": ['dance instruction', 'dance teacher', 'dance class', 'ballet teacher', 'hip hop', 'contemporary', 'ballroom', 'dance studio']
    },
    "boxing_instruction": {
        "name": "Boxing Coaching",
        "domain": "sport_recreation",
        "description": "Coaching boxing and combat sports including technique, fitness, and fight preparation",
        "keywords": ['boxing', 'boxing coach', 'combat sports', 'MMA', 'kickboxing', 'Muay Thai', 'boxing training', 'fight training']
    },
    "triathlon_coaching": {
        "name": "Endurance Coaching",
        "domain": "sport_recreation",
        "description": "Coaching triathlon and endurance sports including swim, bike, run, and endurance training",
        "keywords": ['triathlon', 'triathlon coaching', 'endurance', 'marathon', 'Ironman', 'running coach', 'cycling coach', 'multisport']
    },
    "surf_instruction": {
        "name": "Surf Instruction",
        "domain": "sport_recreation",
        "description": "Teaching surfing including wave selection, paddling, standing, and surf safety",
        "keywords": ['surf instruction', 'surfing', 'surf lesson', 'surf coach', 'surf school', 'learn to surf', 'stand up paddle', 'SUP']
    },
    "gymnastics_coaching": {
        "name": "Gymnastics Coaching",
        "domain": "sport_recreation",
        "description": "Coaching gymnastics including apparatus, floor, and gymnastics skill development",
        "keywords": ['gymnastics', 'gymnastics coaching', 'gym coach', 'tumbling', 'apparatus', 'gymnastics class', 'acrobatics']
    },
    "sports_massage": {
        "name": "Sports Massage",
        "domain": "sport_recreation",
        "description": "Providing sports massage including pre-event, post-event, and athletic soft tissue therapy",
        "keywords": ['sports massage', 'athletic massage', 'sports therapy', 'pre-event massage', 'post-event', 'muscle recovery', 'sports therapist']
    },
    "horse_riding_instruction": {
        "name": "Equestrian Instruction",
        "domain": "sport_recreation",
        "description": "Teaching horse riding including dressage, jumping, and equestrian skill development",
        "keywords": ['horse riding instruction', 'riding lesson', 'equestrian coaching', 'riding school', 'pony club', 'dressage coaching', 'jumping coach']
    },
    "smart_metering": {
        "name": "Smart Metering",
        "domain": "utilities_resources",
        "description": "Installing smart meters and advanced metering infrastructure for electricity, gas, and water utilities.",
        "keywords": ['smart meter', 'smart metering', 'AMI', 'advanced metering', 'meter data', 'smart grid', 'remote reading']
    },
    "stormwater_management": {
        "name": "Stormwater Management",
        "domain": "utilities_resources",
        "description": "Managing stormwater systems including drainage infrastructure, detention basins, and stormwater quality treatment.",
        "keywords": ['stormwater', 'stormwater management', 'drainage', 'stormwater drain', 'detention basin', 'WSUD', 'stormwater harvesting']
    },
    "meter_reading": {
        "name": "Meter Reading",
        "domain": "utilities_resources",
        "description": "Reading utility meters for electricity, gas, and water including manual and automated meter data collection.",
        "keywords": ['meter reading', 'meter reader', 'utility meter', 'water meter', 'electricity meter', 'meter route', 'AMR']
    },
    "line_marking": {
        "name": "Line Marking",
        "domain": "utilities_resources",
        "description": "Applying line markings to roads, car parks, and facilities including thermoplastic and paint line marking.",
        "keywords": ['line marking', 'road marking', 'car park marking', 'pavement marking', 'thermoplastic', 'road lines', 'line painting']
    },
    "street_lighting": {
        "name": "Street Lighting",
        "domain": "utilities_resources",
        "description": "Installing and maintaining street lights and public lighting including LED upgrades and lighting controls.",
        "keywords": ['street lighting', 'street light', 'public lighting', 'LED street light', 'light pole', 'outdoor lighting', 'luminaire']
    },
    "geotechnical_testing": {
        "name": "Geotechnical Testing",
        "domain": "utilities_resources",
        "description": "Conducting geotechnical field investigations including soil testing, bore holes, and foundation assessment for construction projects.",
        "keywords": ['geotechnical', 'geotechnical testing', 'soil testing', 'bore hole', 'penetration test', 'geotechnical investigation', 'foundation']
    },
    "commissioning_testing": {
        "name": "Commissioning Testing",
        "domain": "manufacturing_engineering",
        "description": "Testing and commissioning industrial plant, equipment, and systems including pre-commissioning checks, functional testing, and handover documentation.",
        "keywords": ['commissioning', 'plant commissioning', 'equipment commissioning', 'system commissioning', 'pre-commissioning', 'functional testing', 'handover', 'commissioning testing']
    },
    "control_systems_testing": {
        "name": "Control Systems Testing",
        "domain": "manufacturing_engineering",
        "description": "Testing industrial control systems including SCADA, DCS, and PLC systems for process control applications. Excludes software application testing.",
        "keywords": ['control systems', 'SCADA testing', 'DCS testing', 'process control testing', 'PLC testing', 'control system commissioning', 'loop testing', 'I/O testing']
    },
    "electrical_testing": {
        "name": "Electrical Testing",
        "domain": "electrical_communications",
        "description": "Testing electrical installations and equipment including insulation resistance, earth continuity, RCD testing, and electrical safety compliance testing.",
        "keywords": ['electrical testing', 'insulation testing', 'megger', 'RCD testing', 'earth testing', 'electrical compliance', 'test and tag', 'PAT testing', 'electrical safety testing']
    },
    "operational_readiness": {
        "name": "Operational Readiness",
        "domain": "utilities_resources",
        "description": "Preparing operational systems for handover including operational testing, procedure development, operator training, and readiness assessment for utilities and infrastructure.",
        "keywords": ['operational readiness', 'operational testing', 'system testing', 'operational procedures', 'handover', 'readiness review', 'operational acceptance']
    },

    "animal_control": {
        "name": "Animal Control",
        "domain": "agriculture_primary",
        "description": "Managing animal control and wildlife response including animal seizures, wildlife incidents, dangerous animal management, stray animals, and compliance enforcement.",
        "keywords": ["animal control", "wildlife control", "animal management", "ranger", "animal seizure", "dangerous animal", "stray animal", "animal compliance", "wildlife officer", "animal incident"]
    },
    "wildlife_rescue": {
        "name": "Wildlife Rescue",
        "domain": "agriculture_primary",
        "description": "Rescuing and rehabilitating wildlife including injured animals, marine mammals, whale disentanglement, whale behaviour assessment, wildlife capture, chemical restraint, and animal release.",
        "keywords": ['wildlife rescue', 'animal rescue', 'wildlife rehabilitation', 'whale rescue', 'whale behaviour', 'whale assessment', 'marine mammal', 'wildlife capture', 'chemical restraint', 'wildlife release', 'injured wildlife', 'fauna rescue', 'entanglement', 'whale disentanglement']
    },
    "indigenous_land_management": {
        "name": "Indigenous Land Management",
        "domain": "utilities_resources",
        "description": "Managing land using Indigenous knowledge and practices including traditional burning, cultural site management, country management, and Indigenous ranger work.",
        "keywords": ["indigenous land management", "traditional burning", "cultural burning", "country management", "indigenous ranger", "traditional owner", "aboriginal land", "cultural landscape", "caring for country", "indigenous practices"]
    },
    "cultural_heritage": {
        "name": "Cultural Heritage Management",
        "domain": "creative_arts",
        "description": "Managing and protecting cultural heritage including heritage assessment, cultural site surveys, archaeological sites, heritage conservation, and cultural protocols.",
        "keywords": ["cultural heritage", "heritage management", "heritage assessment", "cultural site", "archaeological", "heritage conservation", "cultural protocol", "heritage survey", "indigenous heritage", "cultural values"]
    },
    "agricultural_extension": {
        "name": "Agricultural Extension",
        "domain": "agriculture_primary",
        "description": "Providing on-farm agricultural advice and extension services to farmers including agronomic consulting, farm best practices, crop recommendations, and farmer education.",
        "keywords": ['agricultural extension', 'farm advice', 'agronomist', 'farm consultant', 'extension officer', 'farmer education', 'on-farm advice', 'agricultural consulting', 'farming advice']
    },
    "crop_agronomy": {
        "name": "Crop Agronomy",
        "domain": "agriculture_primary",
        "description": "Managing crop production including crop planning, soil management, fertiliser application, crop protection, irrigation scheduling, and harvest planning.",
        "keywords": ["crop agronomy", "crop production", "agronomy", "crop management", "fertiliser", "crop protection", "irrigation", "soil management", "cropping", "harvest planning"]
    },
    "integrated_pest_management": {
        "name": "Integrated Pest Management",
        "domain": "agriculture_primary",
        "description": "Implementing integrated pest management including pest identification, biological control, chemical control, pest monitoring, and IPM strategies.",
        "keywords": ["integrated pest management", "IPM", "pest control", "biological control", "pest identification", "pest monitoring", "crop protection", "pest management", "weed control", "disease management"]
    },
    "stakeholder_engagement": {
        "name": "Stakeholder Engagement",
        "domain": "business_administration",
        "description": "Engaging corporate and community stakeholders including stakeholder consultation, relationship management, community engagement planning, and stakeholder communication strategies.",
        "keywords": ['stakeholder engagement', 'stakeholder management', 'consultation', 'community engagement', 'stakeholder communication', 'relationship management', 'stakeholder analysis', 'engagement planning']
    },
    "interpersonal_communication": {
        "name": "Interpersonal Communication",
        "domain": "business_administration",
        "description": "Communicating effectively including active listening, verbal communication, non-verbal communication, negotiation, conflict resolution, and empathetic communication.",
        "keywords": ["interpersonal communication", "active listening", "verbal communication", "non-verbal communication", "negotiation", "conflict resolution", "empathetic communication", "communication skills", "listening skills", "de-escalation"]
    },
    "genetics_breeding": {
        "name": "Genetics Breeding",
        "domain": "science_technical",
        "description": "Working with genetics and breeding including genetic analysis, breeding programs, genetic diversity, embryo transfer, artificial insemination, and genetic selection.",
        "keywords": ["genetics", "breeding", "genetic analysis", "genetic diversity", "embryo transfer", "artificial insemination", "genetic selection", "breeding program", "animal genetics", "plant genetics"]
    },
    "research_ethics": {
        "name": "Research Ethics",
        "domain": "science_technical",
        "description": "Managing research ethics including animal ethics, human ethics, ethics applications, 3Rs principles, ethics compliance, and research integrity.",
        "keywords": ["research ethics", "animal ethics", "human ethics", "ethics application", "3Rs", "replacement reduction refinement", "ethics compliance", "research integrity", "ethics committee", "ethics approval"]
    },
    "assistance_dog_training": {
        "name": "Assistance Dog Training",
        "domain": "agriculture_primary",
        "description": "Training assistance dogs and handlers including guide dogs, service dogs, therapy dogs, operant conditioning, positive reinforcement, handler training, dog behaviour assessment, and assistance animal placement.",
        "keywords": ['assistance dog', 'guide dog', 'service dog', 'therapy dog', 'handler training', 'dog training', 'operant conditioning', 'positive reinforcement', 'classical conditioning', 'dog behaviour', 'behavior selection', 'species behavior', 'assistance animal', 'dog placement', 'working dog']
    },

    "solution_architecture": {
        "name": "Solution Architecture",
        "domain": "digital_technology",
        "description": "Designing IT solution architectures including software system design, technology stack selection, integration patterns, and enterprise IT architecture for software projects.",
        "keywords": ["solution architecture", "IT architecture", "software architecture", "system design", "technology stack", "integration architecture", "enterprise architecture", "technical design", "solution design"]
    },
    "systems_analysis": {
        "name": "Systems Analysis",
        "domain": "digital_technology",
        "description": "Analysing IT systems and software requirements including system specifications, technical requirements, software analysis, and IT system documentation.",
        "keywords": ["systems analysis", "systems analyst", "IT analysis", "software requirements", "system specifications", "technical analysis", "IT requirements", "system documentation"]
    },
    "it_service_management": {
        "name": "IT Service Management",
        "domain": "digital_technology",
        "description": "Managing IT services using ITIL or similar frameworks including service desk operations, incident management, problem management, and IT service delivery.",
        "keywords": ["IT service management", "ITIL", "service desk", "incident management", "problem management", "IT helpdesk", "service delivery", "ITSM", "IT support"]
    },
    "it_asset_management": {
        "name": "IT Asset Management",
        "domain": "digital_technology",
        "description": "Managing IT assets and technology inventory including hardware tracking, software licensing, IT asset lifecycle, technology availability assessment, and asset registers.",
        "keywords": ["IT asset management", "asset tracking", "software licensing", "hardware inventory", "IT assets", "technology inventory", "asset register", "IT lifecycle", "technology availability"]
    },
    "technical_writing": {
        "name": "Technical Writing",
        "domain": "digital_technology",
        "description": "Writing technical documentation for IT and software including user manuals, API documentation, system specifications, and technical guides.",
        "keywords": ["technical writing", "documentation", "user manual", "API documentation", "technical documentation", "system documentation", "technical writer", "software documentation"]
    },
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
    
    # Construction and Building
    "CPC": "Construction, Plumbing and Services",
    "CPP": "Property Services",
    "MSF": "Furnishing",
    
    # Automotive and Transport
    "AUM": "Automotive Manufacturing",
    "AUR": "Automotive Retail, Service and Repair",
    "AVI": "Aviation",
    "MAR": "Maritime",
    "TLI": "Transport and Logistics",
    
    # Manufacturing and Engineering
    "MEA": "Aeroskills",
    "MEM": "Manufacturing and Engineering",
    "MSM": "Manufacturing (Manufactured Mineral Products)",
    "MST": "Textiles, Clothing and Footwear",
    "PMA": "Pulp and Paper Manufacturing Industries",
    "PMB": "Polymer Manufacturing",
    "PMC": "Competitive Manufacturing",
    "FBP": "Food, Beverage and Pharmaceutical",
    
    # Technology and ICT
    "ICT": "Information and Communications Technology",
    "ICP": "Printing and Graphic Arts",
    
    # Health and Community
    "CHC": "Community Services",
    "HLT": "Health",
    
    # Business and Finance
    "BSB": "Business Services",
    "FNS": "Financial Services",
    "LGA": "Local Government",
    "PSP": "Public Sector",
    
    # Education and Training
    "TAE": "Training and Education",
    
    # Hospitality and Tourism
    "SIT": "Tourism, Travel and Hospitality",
    "SFL": "Floristry",
    
    # Creative Arts
    "CUA": "Creative Arts and Culture",
    "CUF": "Screen and Media",
    "CUS": "Sustainability",
    "CUV": "Visual Arts",
    "SHB": "Hairdressing and Beauty Services",
    
    # Public Safety and Security
    "CSC": "Correctional Services",
    "DEF": "Defence",
    "POL": "Police",
    "PUA": "Public Safety",
    
    # Resources and Utilities
    "DRG": "Drilling",
    "NWP": "Water",
    "RII": "Resources and Infrastructure Industry",
    "UEE": "Electrotechnology",
    "UEG": "Gas Industry",
    "UEP": "Electricity Supply Industry - Generation Sector",
    "UET": "Transmission, Distribution and Rail Sector",
    
    # Science and Laboratory
    "MSL": "Laboratory Operations",
    "MSS": "Sustainability",
    
    # Sport and Recreation
    "SIS": "Sport, Fitness and Recreation",
    
    # Retail and Personal Services
    "SIR": "Retail Services",
    "SIF": "Funeral Services"
}


# ═══════════════════════════════════════════════════════════════════════════
#  COMPLEXITY LEVELS (5 levels - Enhanced with AQF and Bloom's Taxonomy)
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
#  TRANSFERABILITY TYPES (4 categories - O*NET and ASC aligned)
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
#  SKILL NATURE TYPES (5 types - O*NET and BLS aligned)
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

MULTI_FACTOR_WEIGHTS = {
    "semantic_weight": float(os.environ.get("SEMANTIC_WEIGHT", "0.60")),
    "level_weight": float(os.environ.get("LEVEL_WEIGHT", "0.25")),
    "context_weight": float(os.environ.get("CONTEXT_WEIGHT", "0.15")),
}

MATCH_THRESHOLDS = {
    "direct_match_threshold": float(os.environ.get("DIRECT_MATCH_THRESHOLD", "0.90")),
    "partial_threshold": float(os.environ.get("PARTIAL_THRESHOLD", "0.80")),
    "minimum_threshold": float(os.environ.get("MINIMUM_THRESHOLD", "0.65")),
}

LEVEL_COMPATIBILITY = {
    "max_level_difference_for_dedup": 1,
    "level_penalty_factor": 0.2,
    "prefer_higher_levels": True,
}

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
    "confidence_threshold": 0.7,
    "min_skill_length": 3,
    "max_skill_length": 200,
    "batch_size": 1000,
    "n_jobs": -1,
}

# ============================================================================
# EMBEDDING SETTINGS
# ============================================================================

EMBEDDING_CONFIG = {
    # "model_name": "sentence-transformers--all-mpnet-base-v2",
    "model_name": "jinaai--jina-embeddings-v4",
    # "model_name": "Qwen--Qwen3-Embedding-0.6B",
    # "model_name": "sentence-transformers--all-MiniLM-L6-v2",
    "batch_size": 64,
    "cache_embeddings": True,
    "normalize_embeddings": False,
    "device": "cuda" if os.environ.get("CUDA_AVAILABLE") else "cuda:1",
    "external_model_dir": os.getenv("EXTERNAL_MODEL_DIR", "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"),
    "model_cache_dir": os.getenv("MODEL_CACHE_DIR", "/root/.cache/huggingface/hub"),
    "similarity_method": os.environ.get("SIMILARITY_METHOD", "matrix"),
    "matrix_memory_threshold": 500000,
    "faiss_exact_search_threshold": 5000,
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# DEDUPLICATION SETTINGS
# ============================================================================

DEDUP_CONFIG = {
    "similarity_threshold": MATCH_THRESHOLDS["partial_threshold"],
    **MATCH_THRESHOLDS,
    "use_faiss": False,
    "faiss_index_type": "IVF1024,Flat",
    "nprobe": 64,
    "fuzzy_ratio_threshold": 90,
    **LEVEL_COMPATIBILITY,
    **MULTI_FACTOR_WEIGHTS
}

# ============================================================================
# FAMILY ASSIGNMENT SETTINGS (Replaces Clustering)
# ============================================================================

FAMILY_ASSIGNMENT_CONFIG = {
    "use_genai": True,
    "genai_batch_size": 50,
    "fallback_to_keyword_matching": True,
    "keyword_match_threshold": 3,
    "use_embedding_similarity": True,
    "embedding_similarity_threshold": 0.7,
    "max_retries": 3,
    # LLM Re-ranking settings (Top-K + LLM selection for better accuracy)
    "use_llm_reranking": True,  # Enable LLM re-ranking of top-K embedding candidates
    "rerank_top_k": 5,          # Number of top candidates to consider for re-ranking
    "rerank_similarity_threshold": 0.5,  # Min similarity for candidates to be re-ranked
}

# ============================================================================
# HIERARCHY SETTINGS
# ============================================================================

HIERARCHY_CONFIG = {
    "max_children": 25,
    "min_children": 2,
    "max_depth": 4,  # Domain → Family → Group → Skills
    "balance_threshold": 0.3,
    "max_level_span_per_node": 2,
    "enable_cross_cutting_dimensions": True,
    "enable_transferability_scoring": True,
    "enable_digital_intensity_scoring": True,
    "enable_future_readiness_scoring": True,
    "enable_skill_nature_classification": True,
    "enable_context_classification": True,
    "build_skill_relationships": True,
    "max_related_skills": 20,
    "relationship_similarity_threshold": 0.85,
    "include_training_package_alignment": True,
    "include_qualification_mapping": True,
    "include_unit_of_competency_links": True,
    "include_industry_sector_codes": True,
    "include_occupation_codes": True,
    "enable_skill_pathways": True,
    "enable_prerequisite_mapping": True,
    "enable_licensing_requirements": True,
    "use_llm_refinement": False
}

# ============================================================================
# VALIDATION CONFIGURATION
# ============================================================================

VALIDATION_CONFIG = {
    "min_coverage": 0.85,
    "target_coverage": 0.95,
    "min_cluster_coherence": 0.65,
    "target_cluster_coherence": 0.80,
    "expected_depth_range": (3, 4),
    "min_balance_score": 0.45,
    "expected_domains": 15,
    "expected_families_range": (85, 110),
    "require_all_dimensions": True,
    "validate_complexity_distribution": True,
    "validate_transferability_variety": True,
    "validate_digital_intensity_range": True,
    "validate_future_readiness_distribution": True,
    "validate_training_package_coverage": True,
    "validate_aqf_alignment": True,
    "min_skills_per_family": 5,
    "max_skills_per_family": 5000,
    "min_avg_relationships": 1.5,
    "max_isolated_skills_percent": 10,
    "coverage_threshold": 0.95,
    "coherence_threshold": 0.7,
    "distinctiveness_threshold": 0.5,
    "max_orphan_skills": 100,
    "validate_with_llm": True,
    "check_level_consistency": True,
    "check_context_alignment": True,
    "minimum_cluster_coherence": 0.6,
    "validate_domain_assignment": True,
    "validate_transferability_scores": True,
    "validate_skill_relationships": True,
}

# ============================================================================
# LLM SETTINGS
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

# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

EMBEDDING_MODELS = {
    "jinaai--jina-embeddings-v4": {
        "model_id": "jinaai/jina-embeddings-v4",
        "revision": "737fa5c46f0262ceba4a462ffa1c5bcf01da416f",
        "trust_remote_code": True,
        "embedding_dim": 2048
    },
    "Qwen--Qwen3-Embedding-0.6B": {
        "model_id": "Qwen/Qwen3-Embedding-0.6B",
        "revision": None,
        "trust_remote_code": True,
        "embedding_dim": 1024
    },
    "sentence-transformers--all-mpnet-base-v2": {
        "model_id": "sentence-transformers/all-mpnet-base-v2",
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
}

MODELS = {
    "meta-llama--Llama-3.1-8B-Instruct": {
        "model_id": "meta-llama/Llama-3.1-8B-Instruct",
        "revision": "0e9e39f249a16976918f6564b8830bc894c89659",
        "template": "Llama"
    },
    "gpt-oss-120b": {
        "model_id": "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models/gpt-oss-120b",
        "revision": None,
        "template": "GPT"
    },
}

# ============================================================================
# EXPORT CONFIGURATION
# ============================================================================

CONFIG: Dict[str, Any] = {
    "backed_type": "vllm",
    "data": DATA_CONFIG,
    "embedding": EMBEDDING_CONFIG,
    "dedup": DEDUP_CONFIG,
    "family_assignment": FAMILY_ASSIGNMENT_CONFIG,
    "hierarchy": HIERARCHY_CONFIG,
    "validation": VALIDATION_CONFIG,
    "llm": LLM_CONFIG,
    "multi_factor": {
        "weights": MULTI_FACTOR_WEIGHTS,
        "thresholds": MATCH_THRESHOLDS,
        "level_compatibility": LEVEL_COMPATIBILITY,
        "context_compatibility": CONTEXT_COMPATIBILITY,
    },
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


def get_config_profile(profile: str = "balanced") -> Dict[str, Any]:
    """Get a pre-configured profile with different weight balances"""
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
            "direct_match_threshold": 0.95,
            "partial_threshold": 0.90,
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
        for key in ["embedding", "dedup"]:
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
logger.info("SKILL TAXONOMY CONFIGURATION")
logger.info("=" * 60)
logger.info(f"Skill Domains: {len(SKILL_DOMAINS)}")
logger.info(f"Skill Families: {len(SKILL_FAMILIES)}")
logger.info(f"Training Packages: {len(TRAINING_PACKAGES)}")
logger.info("=" * 60)