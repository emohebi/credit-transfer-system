#!/usr/bin/env python3
"""
Comprehensive Taxonomy Structure Fix Script

This script applies ALL fixes identified from:
1. My initial analysis (duplicate keys, overlapping families)
2. The uploaded taxonomy_fixes_summary.md file
3. Additional merge requests for cleaner taxonomy

SUMMARY OF ALL CHANGES:
=======================

DELETIONS (8):
- technical_documentation (duplicate of technical_writing)
- data_visualisation (merged into business_intelligence_reporting)
- aws, azure, gcp (merged into cloud_platforms)
- interior_painting, exterior_painting (merged into building_painting)
- wall_tiling, floor_tiling (merged into tiling)

RENAMES (4):
- electrical_maintenance → industrial_electrical_maintenance (in manufacturing)
- electrical_maintenance_building → building_electrical_maintenance (in electrical)
- graphic_design_digital → digital_marketing_design
- butchery_hotel → institutional_butchery

MERGES (4):
- data_visualisation + business_intelligence → business_intelligence_reporting
- aws + azure + gcp → cloud_platforms
- interior_painting + exterior_painting → building_painting
- wall_tiling + floor_tiling → tiling

ADDITIONS (4):
- business_intelligence_reporting (merged family)
- cloud_platforms (merged family)
- building_painting (merged family)
- tiling (merged family)

DESCRIPTION UPDATES (15+):
- computer_vision, deep_learning, nlp, machine_learning (AI/ML clarifications)
- software_testing (vs industrial QC)
- surgical_nursing, perioperative_nursing (ward vs theatre)
- massage_therapy, sports_massage (general vs athletic)
- solar_pv_installation, solar_pv_systems (building vs utility scale)
- optometry (human eye care)
- technical_writing (merged keywords)
- graphic_design (kept as-is for print/brand focus)

Usage:
    python comprehensive_taxonomy_fix.py input.py output.py
"""

import re
import sys


def load_file(filepath):
    """Load file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(filepath, content):
    """Save content to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def remove_entry(content, key):
    """Remove a SKILL_FAMILIES entry by key name."""
    pattern = rf'    "{key}":\s*\{{[^{{}}]*\}},?\n'
    return re.sub(pattern, '', content, flags=re.DOTALL)


def insert_after_entry(content, after_key, new_entry):
    """Insert a new entry after an existing one."""
    pattern = rf'(    "{after_key}":\s*\{{[^{{}}]*\}},?\n)'
    return re.sub(pattern, rf'\1{new_entry}', content, flags=re.DOTALL)


def apply_all_fixes(content):
    """Apply ALL taxonomy fixes from both analysis sources."""
    
    print("Applying comprehensive fixes...")
    
    # =========================================================================
    # FIX 1: Handle duplicate "electrical_maintenance" key
    # The first occurrence (construction_building domain) is a bug - wrong domain
    # We need to remove the first one, then rename the second to industrial_electrical_maintenance
    # =========================================================================
    elec_maint_pattern = r'    "electrical_maintenance":\s*\{[^{}]*\},?\n'
    matches = list(re.finditer(elec_maint_pattern, content, flags=re.DOTALL))
    
    if len(matches) >= 2:
        print(f"  Found {len(matches)} 'electrical_maintenance' entries - removing first (duplicate key)")
        first_match = matches[0]
        content = content[:first_match.start()] + content[first_match.end():]
    
    # =========================================================================
    # FIX 2: Rename electrical_maintenance → industrial_electrical_maintenance
    # =========================================================================
    old_elec_maint = r'    "electrical_maintenance":\s*\{[^{}]*\},?\n'
    new_elec_maint = '''    "industrial_electrical_maintenance": {
        "name": "Industrial Electrical Maintenance",
        "domain": "manufacturing_engineering",
        "description": "Maintaining industrial electrical systems in manufacturing facilities including motors, switchboards, control panels, and factory electrical equipment. Industrial/factory context, not building maintenance.",
        "keywords": ["industrial electrical", "electrical maintenance", "motor maintenance", "electrical fault", "factory electrical", "electrical service", "control panel", "industrial wiring"]
    },
'''
    content = re.sub(old_elec_maint, new_elec_maint, content)
    print("  Renamed electrical_maintenance → industrial_electrical_maintenance")
    
    # =========================================================================
    # FIX 3: Rename electrical_maintenance_building → building_electrical_maintenance
    # =========================================================================
    content = content.replace('"electrical_maintenance_building":', '"building_electrical_maintenance":')
    
    # Also update the entry content
    old_building_elec = r'    "building_electrical_maintenance":\s*\{[^{}]*\},?\n'
    new_building_elec = '''    "building_electrical_maintenance": {
        "name": "Building Electrical Maintenance",
        "domain": "electrical_communications",
        "description": "Maintaining electrical systems in commercial and residential buildings including fault finding, repairs, and electrical safety testing. Building maintenance context, not industrial/factory.",
        "keywords": ["building electrical", "electrical maintenance", "electrical service", "light replacement", "electrical fault", "power maintenance", "commercial electrical maintenance"]
    },
'''
    content = re.sub(old_building_elec, new_building_elec, content)
    print("  Renamed/updated electrical_maintenance_building → building_electrical_maintenance")
    
    # =========================================================================
    # FIX 4: Delete technical_documentation (duplicate of technical_writing)
    # =========================================================================
    if '"technical_documentation"' in content:
        print("  Removing 'technical_documentation' (duplicate of technical_writing)")
        content = remove_entry(content, 'technical_documentation')
    
    # =========================================================================
    # FIX 5: Update technical_writing with merged keywords
    # =========================================================================
    old_tw = r'    "technical_writing":\s*\{[^{}]*\}'
    new_tw = '''    "technical_writing": {
        "name": "Technical Writing",
        "domain": "digital_technology",
        "description": "Writing technical documentation for IT and software including user guides, API documentation, system specifications, technical manuals, and knowledge bases",
        "keywords": ["technical writing", "technical documentation", "documentation", "user manual", "API documentation", "knowledge base", "technical writer", "system documentation", "software documentation"]
    }'''
    content = re.sub(old_tw, new_tw, content)
    print("  Updated technical_writing with merged keywords")
    
    # =========================================================================
    # FIX 6: Rename graphic_design_digital → digital_marketing_design
    # =========================================================================
    old_gdd = r'    "graphic_design_digital":\s*\{[^{}]*\},?\n'
    new_gdd = '''    "digital_marketing_design": {
        "name": "Digital Marketing Design",
        "domain": "digital_technology",
        "description": "Creating digital marketing assets including web graphics, social media visuals, email templates, online advertising creatives, and digital campaign materials",
        "keywords": ["digital design", "web graphics", "social media design", "digital marketing assets", "banner design", "email design", "ad creatives", "digital campaign", "online graphics"]
    },
'''
    content = re.sub(old_gdd, new_gdd, content)
    print("  Renamed graphic_design_digital → digital_marketing_design")
    
    # =========================================================================
    # FIX 7: Rename butchery_hotel → institutional_butchery
    # =========================================================================
    content = content.replace('"butchery_hotel":', '"institutional_butchery":')
    
    old_butchery = r'    "institutional_butchery":\s*\{[^{}]*\},?\n'
    new_butchery = '''    "institutional_butchery": {
        "name": "Institutional Butchery",
        "domain": "hospitality_tourism",
        "description": "Large-scale meat preparation for hotels, hospitals, and institutions including bulk meat cutting, portion control, and volume meat production",
        "keywords": ["institutional butchery", "volume butchery", "hotel butchery", "bulk meat", "portion control", "large-scale meat", "institutional catering", "hospital kitchen"]
    },
'''
    content = re.sub(old_butchery, new_butchery, content)
    print("  Renamed butchery_hotel → institutional_butchery")
    
    # =========================================================================
    # FIX 8: Merge data_visualisation + business_intelligence → business_intelligence_reporting
    # =========================================================================
    # Remove data_visualisation
    if '"data_visualisation"' in content:
        print("  Removing 'data_visualisation' (merging into business_intelligence_reporting)")
        content = remove_entry(content, 'data_visualisation')
    
    # Replace business_intelligence with merged business_intelligence_reporting
    old_bi = r'    "business_intelligence":\s*\{[^{}]*\},?\n'
    new_bi = '''    "business_intelligence_reporting": {
        "name": "Business Intelligence Reporting",
        "domain": "digital_technology",
        "description": "Creating business intelligence dashboards, reports, and data visualisations using tools like Power BI, Tableau, or Looker for business analysis and decision support",
        "keywords": ["business intelligence", "BI", "data visualisation", "data visualization", "dashboard", "Power BI", "Tableau", "reporting", "charts", "graphs", "visual analytics", "SSRS", "Crystal Reports", "Looker", "business reporting"]
    },
'''
    content = re.sub(old_bi, new_bi, content)
    print("  Merged data_visualisation + business_intelligence → business_intelligence_reporting")
    
    # =========================================================================
    # FIX 9: Merge aws + azure + gcp → cloud_platforms
    # =========================================================================
    if '"aws"' in content:
        print("  Removing 'aws' (merging into cloud_platforms)")
        content = remove_entry(content, 'aws')
    
    if '"azure"' in content:
        print("  Removing 'azure' (merging into cloud_platforms)")
        content = remove_entry(content, 'azure')
    
    if '"gcp"' in content:
        print("  Removing 'gcp' (merging into cloud_platforms)")
        content = remove_entry(content, 'gcp')
    
    # Add cloud_platforms after docker_containers
    cloud_entry = '''    "cloud_platforms": {
        "name": "Cloud Platform Services",
        "domain": "digital_technology",
        "description": "Deploying and managing IT cloud infrastructure on major cloud platforms including AWS (EC2, S3, Lambda, RDS), Microsoft Azure (VMs, Functions, Storage), and Google Cloud Platform (Compute Engine, BigQuery, GKE).",
        "keywords": ["cloud", "AWS", "Azure", "GCP", "Amazon Web Services", "Microsoft Azure", "Google Cloud", "EC2", "S3", "Lambda", "cloud computing", "cloud infrastructure", "cloud services", "cloud deployment", "IaaS", "PaaS"]
    },
'''
    content = insert_after_entry(content, 'docker_containers', cloud_entry)
    print("  Added cloud_platforms (merged aws + azure + gcp)")
    
    # =========================================================================
    # FIX 25: Merge interior_painting + exterior_painting → building_painting
    # =========================================================================
    if '"interior_painting"' in content:
        print("  Removing 'interior_painting' (merging into building_painting)")
        content = remove_entry(content, 'interior_painting')
    
    if '"exterior_painting"' in content:
        print("  Removing 'exterior_painting' (merging into building_painting)")
        content = remove_entry(content, 'exterior_painting')
    
    # Add building_painting - try multiple insertion points
    building_painting_entry = '''    "building_painting": {
        "name": "Building Painting",
        "domain": "construction_building",
        "description": "Painting interior and exterior building surfaces including walls, ceilings, trim, weatherboards, and render in residential and commercial buildings.",
        "keywords": ["painting", "interior painting", "exterior painting", "wall painting", "ceiling painting", "house painting", "brush painting", "roller painting", "cutting in", "weatherboard", "render painting", "commercial painting"]
    },
'''
    # Try multiple insertion points in order of preference
    inserted = False
    for target in ['decorative_finishes', 'spray_painting_building', 'wallpapering', 'cornice_installation', 'plasterboard_stopping']:
        if f'"{target}"' in content and not inserted:
            content = insert_after_entry(content, target, building_painting_entry)
            inserted = True
            break
    
    if not inserted:
        # Last resort: add after SKILL_FAMILIES = {
        content = content.replace('SKILL_FAMILIES = {', 'SKILL_FAMILIES = {\n' + building_painting_entry, 1)
    
    print("  Added building_painting (merged interior + exterior painting)")
    
    # =========================================================================
    # FIX 26: Merge wall_tiling + floor_tiling → tiling
    # =========================================================================
    if '"wall_tiling"' in content:
        print("  Removing 'wall_tiling' (merging into tiling)")
        content = remove_entry(content, 'wall_tiling')
    
    if '"floor_tiling"' in content:
        print("  Removing 'floor_tiling' (merging into tiling)")
        content = remove_entry(content, 'floor_tiling')
    
    # Add tiling before waterproofing
    tiling_entry = '''    "tiling": {
        "name": "Wall Floor Tiling",
        "domain": "construction_building",
        "description": "Installing ceramic, porcelain, and natural stone tiles on walls and floors including bathrooms, kitchens, wet areas, splashbacks, and large format floor tiles.",
        "keywords": ["tiling", "wall tiling", "floor tiling", "wall tiles", "floor tiles", "ceramic tiles", "porcelain tiles", "tile installation", "bathroom tiles", "kitchen tiles", "splashback tiles", "tile laying", "grout", "tile cutting"]
    },
'''
    if '"waterproofing"' in content:
        # Insert before waterproofing by finding it and inserting before
        waterproof_pattern = r'(    "waterproofing":\s*\{)'
        content = re.sub(waterproof_pattern, tiling_entry + r'\1', content)
    else:
        # Fallback: insert after cornice_installation
        content = insert_after_entry(content, 'cornice_installation', tiling_entry)
    print("  Added tiling (merged wall + floor tiling)")
    
    # =========================================================================
    # FIX 27: Update computer_vision description
    # =========================================================================
    old_cv = r'    "computer_vision":\s*\{[^{}]*\},?\n'
    new_cv = '''    "computer_vision": {
        "name": "Computer Vision",
        "domain": "digital_technology",
        "description": "Developing AI/computer image and video analysis systems using OpenCV, CNNs, and object detection algorithms. Computer/AI visual processing systems only - not human optometry, ophthalmology, or visual assessment.",
        "keywords": ["computer vision", "image recognition", "object detection", "OpenCV", "image processing", "YOLO", "CNN", "video analysis", "AI vision", "machine vision"]
    },
'''
    content = re.sub(old_cv, new_cv, content)
    print("  Updated computer_vision description")
    
    # =========================================================================
    # FIX 25: Update deep_learning description
    # =========================================================================
    old_dl = r'    "deep_learning":\s*\{[^{}]*\},?\n'
    new_dl = '''    "deep_learning": {
        "name": "Deep Learning",
        "domain": "digital_technology",
        "description": "Building deep neural networks using TensorFlow, PyTorch, or Keras for AI applications. Computer neural network systems only - not human learning, neuroscience, or education.",
        "keywords": ["deep learning", "neural network", "TensorFlow", "PyTorch", "CNN", "RNN", "LSTM", "transformer", "AI neural network", "Keras"]
    },
'''
    content = re.sub(old_dl, new_dl, content)
    print("  Updated deep_learning description")
    
    # =========================================================================
    # FIX 26: Update nlp description
    # =========================================================================
    old_nlp = r'    "nlp":\s*\{[^{}]*\},?\n'
    new_nlp = '''    "nlp": {
        "name": "Natural Language Processing",
        "domain": "digital_technology",
        "description": "Building computer NLP systems for text analysis, sentiment analysis, chatbots, and language understanding using AI/ML. Computer language processing only - not human linguistics, translation services, or language teaching.",
        "keywords": ["NLP", "natural language processing", "text analysis", "sentiment analysis", "chatbot", "language model", "BERT", "GPT", "AI text", "text mining"]
    },
'''
    content = re.sub(old_nlp, new_nlp, content)
    print("  Updated nlp description")
    
    # =========================================================================
    # FIX 27: Update machine_learning description
    # =========================================================================
    old_ml = r'    "machine_learning":\s*\{[^{}]*\},?\n'
    new_ml = '''    "machine_learning": {
        "name": "Machine Learning",
        "domain": "digital_technology",
        "description": "Developing machine learning models using Python, TensorFlow, or scikit-learn for prediction, classification, and pattern recognition. Computer/AI algorithms only - not human learning or training delivery.",
        "keywords": ["machine learning", "ML", "AI models", "TensorFlow", "scikit-learn", "predictive modeling", "classification", "computer learning", "algorithm training", "model training"]
    },
'''
    content = re.sub(old_ml, new_ml, content)
    print("  Updated machine_learning description")
    
    # =========================================================================
    # FIX 25: Update software_testing description
    # =========================================================================
    old_testing = r'    "software_testing":\s*\{[^{}]*\},?\n'
    new_testing = '''    "software_testing": {
        "name": "Software Testing QA",
        "domain": "digital_technology",
        "description": "Testing software applications including functional, regression, and automated testing using tools like Selenium. Software/application testing only - not industrial equipment testing, calibration, or manufacturing quality control.",
        "keywords": ["software testing", "QA", "quality assurance", "test automation", "Selenium", "test cases", "bug testing", "regression testing", "application testing", "software QA"]
    },
'''
    content = re.sub(old_testing, new_testing, content)
    print("  Updated software_testing description")
    
    # =========================================================================
    # FIX 26: Update surgical_nursing (ward-based focus)
    # =========================================================================
    old_surgical = r'    "surgical_nursing":\s*\{[^{}]*\},?\n'
    new_surgical = '''    "surgical_nursing": {
        "name": "Surgical Ward Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for human surgical patients on hospital wards including pre-admission assessment, post-operative recovery care, wound management, and surgical ward nursing. Ward-based care - not operating theatre roles.",
        "keywords": ["surgical nursing", "surgical ward", "post-operative", "pre-admission", "surgical care", "wound management", "surgical patient", "ward nursing", "post-op care"]
    },
'''
    content = re.sub(old_surgical, new_surgical, content)
    print("  Updated surgical_nursing (ward-based focus)")
    
    # =========================================================================
    # FIX 27: Update perioperative_nursing (theatre-based focus)
    # =========================================================================
    old_periop = r'    "perioperative_nursing":\s*\{[^{}]*\},?\n'
    new_periop = '''    "perioperative_nursing": {
        "name": "Perioperative Theatre Nursing",
        "domain": "healthcare_clinical",
        "description": "Providing nursing care for human patients in operating theatres including scrub nursing, scout nursing, anaesthetic nursing, and PACU recovery nursing. Operating theatre roles only - not ward-based surgical care.",
        "keywords": ["perioperative nursing", "operating theatre", "scrub nurse", "scout nurse", "anaesthetic nursing", "PACU", "theatre nursing", "surgical instruments", "OR nursing", "circulating nurse"]
    },
'''
    content = re.sub(old_periop, new_periop, content)
    print("  Updated perioperative_nursing (theatre-based focus)")
    
    # =========================================================================
    # FIX 25: Update massage_therapy (general therapeutic)
    # =========================================================================
    old_massage = r'    "massage_therapy":\s*\{[^{}]*\},?\n'
    new_massage = '''    "massage_therapy": {
        "name": "Massage Therapy",
        "domain": "retail_services",
        "description": "Providing general massage therapy for human clients in salons and clinics including remedial massage, relaxation massage, and therapeutic bodywork. General therapeutic massage - sports massage is covered separately under sport_recreation.",
        "keywords": ["massage therapy", "remedial massage", "relaxation massage", "therapeutic massage", "bodywork", "soft tissue therapy", "massage therapist", "clinic massage", "spa massage"]
    },
'''
    content = re.sub(old_massage, new_massage, content)
    print("  Updated massage_therapy (general therapeutic)")
    
    # =========================================================================
    # FIX 26: Update sports_massage (athletic context)
    # =========================================================================
    old_sports_massage = r'    "sports_massage":\s*\{[^{}]*\},?\n'
    new_sports_massage = '''    "sports_massage": {
        "name": "Sports Massage",
        "domain": "sport_recreation",
        "description": "Providing sports massage for human athletes including pre-event preparation, post-event recovery, and athletic soft tissue therapy in sports performance contexts. Athletic/sports context - general massage therapy is covered separately under retail_services.",
        "keywords": ["sports massage", "athletic massage", "pre-event massage", "post-event recovery", "sports injury massage", "athletic soft tissue", "sports therapist", "athlete massage"]
    },
'''
    content = re.sub(old_sports_massage, new_sports_massage, content)
    print("  Updated sports_massage (athletic context)")
    
    # =========================================================================
    # FIX 27: Update solar_pv_installation (rooftop/building-scale)
    # =========================================================================
    old_solar_install = r'    "solar_pv_installation":\s*\{[^{}]*\},?\n'
    new_solar_install = '''    "solar_pv_installation": {
        "name": "Rooftop Solar Installation",
        "domain": "electrical_communications",
        "description": "Installing rooftop solar PV systems on residential and commercial buildings including panels, inverters, and grid connections. Building-scale installations by licensed electricians - not utility-scale solar farms.",
        "keywords": ["solar installation", "rooftop solar", "residential solar", "commercial solar", "solar panel installation", "inverter installation", "grid connect solar", "solar mounting", "PV installation"]
    },
'''
    content = re.sub(old_solar_install, new_solar_install, content)
    print("  Updated solar_pv_installation (rooftop/building-scale)")
    
    # =========================================================================
    # FIX 25: Update solar_pv_systems (utility-scale)
    # =========================================================================
    old_solar_systems = r'    "solar_pv_systems":\s*\{[^{}]*\},?\n'
    new_solar_systems = '''    "solar_pv_systems": {
        "name": "Utility-Scale Solar Systems",
        "domain": "utilities_resources",
        "description": "Operating and maintaining utility-scale solar PV systems including large solar farms, solar tracking systems, and grid-scale solar infrastructure. Utility-scale installations - not residential/commercial rooftop solar.",
        "keywords": ["solar farm", "utility solar", "large-scale solar", "solar tracking", "grid-scale solar", "solar power station", "solar array", "photovoltaic farm", "solar O&M"]
    },
'''
    content = re.sub(old_solar_systems, new_solar_systems, content)
    print("  Updated solar_pv_systems (utility-scale)")
    
    # =========================================================================
    # FIX 26: Update optometry (human eye care clarification)
    # =========================================================================
    old_optometry = r'    "optometry":\s*\{[^{}]*\},?\n'
    new_optometry = '''    "optometry": {
        "name": "Optometry Services",
        "domain": "healthcare_clinical",
        "description": "Providing optometry services for human patients including eye examinations, human vision testing, optical prescriptions, and spectacle dispensing. Human eye care only - not computer vision or machine vision systems.",
        "keywords": ["optometry", "optometrist", "eye examination", "human vision", "optical prescription", "spectacles", "eye care", "vision correction", "eye test", "human eyesight"]
    },
'''
    content = re.sub(old_optometry, new_optometry, content)
    print("  Updated optometry (human eye care clarification)")
    
    # =========================================================================
    # FIX 27: Update quality_assurance (manufacturing context)
    # =========================================================================
    old_qa = r'    "quality_assurance":\s*\{[^{}]*\},?\n'
    new_qa = '''    "quality_assurance": {
        "name": "Manufacturing Quality Assurance",
        "domain": "manufacturing_engineering",
        "description": "Implementing quality management systems in manufacturing including ISO 9001, quality procedures, quality audits, and continuous improvement. Manufacturing and production quality only - not software QA/testing.",
        "keywords": ["manufacturing QA", "quality assurance", "ISO 9001", "quality system", "quality management", "quality audit", "quality procedures", "manufacturing quality", "production quality"]
    },
'''
    content = re.sub(old_qa, new_qa, content)
    print("  Updated quality_assurance (manufacturing context)")
    
    # =========================================================================
    # FIX 25: Update graphic_design (print/brand focus - keep distinct from digital)
    # =========================================================================
    old_graphic = r'    "graphic_design":\s*\{[^{}]*\},?\n'
    new_graphic = '''    "graphic_design": {
        "name": "Graphic Design",
        "domain": "creative_arts",
        "description": "Designing visual communications for print and brand including logos, brochures, packaging, publication design, and corporate identity",
        "keywords": ["graphic design", "graphic designer", "visual design", "layout", "branding", "logo design", "InDesign", "print design", "publication design", "corporate identity"]
    },
'''
    content = re.sub(old_graphic, new_graphic, content)
    print("  Updated graphic_design (print/brand focus)")
    
    # =========================================================================
    # FIX 26: Update makeup_effects (theatrical/SFX context)
    # =========================================================================
    old_makeup_fx = r'    "makeup_effects":\s*\{[^{}]*\},?\n'
    new_makeup_fx = '''    "makeup_effects": {
        "name": "Theatrical SFX Makeup",
        "domain": "creative_arts",
        "description": "Applying makeup for stage, film, and television productions including theatrical makeup, prosthetics, special effects makeup, ageing effects, and character transformation. Entertainment industry makeup only - not beauty/cosmetic makeup.",
        "keywords": ["special effects makeup", "SFX makeup", "prosthetics", "theatrical makeup", "film makeup", "stage makeup", "character makeup", "ageing makeup", "wound effects", "creature makeup"]
    },
'''
    content = re.sub(old_makeup_fx, new_makeup_fx, content)
    print("  Updated makeup_effects (theatrical/SFX context)")
    
    # =========================================================================
    # FIX 27: Update makeup_artistry (beauty/cosmetic context)
    # =========================================================================
    old_makeup_art = r'    "makeup_artistry":\s*\{[^{}]*\},?\n'
    new_makeup_art = '''    "makeup_artistry": {
        "name": "Beauty Makeup Artistry",
        "domain": "retail_services",
        "description": "Applying professional cosmetic makeup for human clients including bridal makeup, editorial, special occasion makeup, and everyday beauty techniques in salons and freelance settings. Beauty/cosmetic makeup only - not theatrical SFX.",
        "keywords": ["makeup artist", "MUA", "bridal makeup", "cosmetics", "beauty makeup", "makeup application", "wedding makeup", "editorial makeup", "special occasion makeup", "glamour makeup"]
    },
'''
    content = re.sub(old_makeup_art, new_makeup_art, content)
    print("  Updated makeup_artistry (beauty/cosmetic context)")
    
    return content


def main():

    print("Usage: python comprehensive_taxonomy_fix.py input.py output.py")
    print("\nNo arguments provided - using test mode")
    input_file = './skill_taxonomy_pipeline/config/structure.py'
    output_file = './skill_taxonomy_pipeline/config/structure_fixed.py'

    
    print(f"\n{'='*70}")
    print("COMPREHENSIVE TAXONOMY FIX SCRIPT")
    print(f"{'='*70}")
    print(f"\nLoading: {input_file}")
    
    try:
        content = load_file(input_file)
    except FileNotFoundError:
        print(f"ERROR: File not found: {input_file}")
        sys.exit(1)
        
    print(f"  File size: {len(content):,} characters")
    
    print("\nAnalyzing structure...")
    family_count_before = content.count('"domain":')
    print(f"  Families before: ~{family_count_before}")
    
    fixed_content = apply_all_fixes(content)
    
    family_count_after = fixed_content.count('"domain":')
    print(f"\n  Families after: ~{family_count_after}")
    print(f"  Net change: {family_count_after - family_count_before}")
    
    print(f"\nSaving: {output_file}")
    save_file(output_file, fixed_content)
    
    print(f"\n{'='*70}")
    print("DONE! Summary of ALL changes applied:")
    print(f"{'='*70}")
    print("""
DELETIONS (8):
  - technical_documentation (duplicate of technical_writing)
  - data_visualisation (merged into business_intelligence_reporting)
  - aws, azure, gcp (merged into cloud_platforms)
  - interior_painting, exterior_painting (merged into building_painting)
  - wall_tiling, floor_tiling (merged into tiling)

RENAMES (4):
  - electrical_maintenance → industrial_electrical_maintenance
  - electrical_maintenance_building → building_electrical_maintenance  
  - graphic_design_digital → digital_marketing_design
  - butchery_hotel → institutional_butchery

MERGES (4 new families created):
  - data_visualisation + business_intelligence → business_intelligence_reporting
  - aws + azure + gcp → cloud_platforms
  - interior_painting + exterior_painting → building_painting
  - wall_tiling + floor_tiling → tiling

DESCRIPTION UPDATES (16):
  - technical_writing (merged keywords)
  - computer_vision (AI/computer only, not human optometry)
  - deep_learning (computer neural networks only, not human learning)
  - nlp (computer language processing only, not linguistics)
  - machine_learning (computer algorithms only, not human training)
  - software_testing (software only, not industrial QC)
  - surgical_nursing (ward-based focus)
  - perioperative_nursing (theatre-based focus)
  - massage_therapy (general therapeutic)
  - sports_massage (athletic context)
  - solar_pv_installation (rooftop/building-scale)
  - solar_pv_systems (utility-scale)
  - optometry (human eye care)
  - quality_assurance (manufacturing context)
  - graphic_design (print/brand focus)
  - makeup_effects (theatrical/SFX)
  - makeup_artistry (beauty/cosmetic)

NET FAMILY COUNT CHANGE: -4 (8 deleted, 4 added)
""")


if __name__ == "__main__":
    main()
