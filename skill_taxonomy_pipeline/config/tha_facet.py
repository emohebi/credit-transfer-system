"""
Transferable Human Ability (THA) Facet Definition

Defines ~90 human abilities organized hierarchically under TRF
(Transferability) categories. Each ability describes WHAT a human can do
(a functional capability), not WHERE they do it (domain/industry).

Sources:
  - O*NET Content Model: 52 abilities (cognitive, psychomotor, physical, sensory)
  - ESCO v1.2: Transversal skills hierarchy (thinking, social, self-management)
  - Australian CSfW: Core Skills for Work (navigating, interacting, getting work done)
  - Australian ACSF: Foundation skills (learning, reading, writing, oral, numeracy)
  - VET training package analysis: occupation-specific functional abilities

Design:
  - THA codes are prefixed by their parent TRF code: THA.UNI.xxx, THA.BRD.xxx, etc.
  - Multi-value: a skill can map to 1-3 THAs
  - Assignment uses the same embedding + LLM re-ranking as other facets
  - During assignment, only THA values matching the skill's TRF are considered

Integration:
  - Added to FACETS_TO_ASSIGN in settings.py
  - Added to MULTI_VALUE_FACETS in facets.py
  - FacetAssigner assigns THA using TRF-scoped candidate filtering
  - Replaces archetype sub-clustering as the sub-grouping mechanism
"""

TRANSFERABLE_HUMAN_ABILITY_FACET = {
    "facet_id": "THA",
    "facet_name": "Transferable Human Ability",
    "description": "Functional human capability that can be applied across contexts. Describes WHAT a person can do, independent of industry or domain.",
    "multi_value": True,
    "parent_facet": "TRF",
    "values": {

        # ═══════════════════════════════════════════════════════════
        #  TRF.UNI — UNIVERSAL ABILITIES
        #  Foundational capabilities needed in virtually all occupations
        # ═══════════════════════════════════════════════════════════

        "THA.UNI.ORC": {
            "code": "THA.UNI.ORC",
            "name": "Oral Communication",
            "parent_trf": "TRF.UNI",
            "description": "Listening to and understanding spoken information, and communicating ideas and information clearly through speech. Includes active listening, verbal instruction, and conversation.",
            "keywords": ["speaking", "listening", "verbal", "conversation", "presentation", "discussion", "briefing", "explaining"],
        },
        "THA.UNI.WRC": {
            "code": "THA.UNI.WRC",
            "name": "Written Communication",
            "parent_trf": "TRF.UNI",
            "description": "Reading, understanding, and producing written information. Includes report writing, documentation, form completion, email correspondence, and interpreting written instructions.",
            "keywords": ["writing", "reading", "documentation", "report", "correspondence", "forms", "notes", "literacy"],
        },
        "THA.UNI.NUM": {
            "code": "THA.UNI.NUM",
            "name": "Numeracy & Calculation",
            "parent_trf": "TRF.UNI",
            "description": "Applying mathematical concepts including arithmetic, measurement, estimation, and basic statistical reasoning to workplace tasks.",
            "keywords": ["mathematics", "calculation", "measurement", "estimation", "counting", "arithmetic", "percentages", "ratios"],
        },
        "THA.UNI.DIG": {
            "code": "THA.UNI.DIG",
            "name": "Digital Literacy",
            "parent_trf": "TRF.UNI",
            "description": "Using digital devices, software applications, and online platforms effectively. Includes basic computer operation, internet use, digital file management, and common workplace software.",
            "keywords": ["computer", "digital", "software", "internet", "technology", "online", "ICT", "applications", "email"],
        },
        "THA.UNI.LRN": {
            "code": "THA.UNI.LRN",
            "name": "Learning & Self-Development",
            "parent_trf": "TRF.UNI",
            "description": "Acquiring new knowledge and skills, reflecting on performance, seeking feedback, and adapting to new information or methods. Includes continuous professional development.",
            "keywords": ["learning", "training", "development", "study", "upskilling", "reflection", "feedback", "improvement", "adaptation"],
        },
        "THA.UNI.PSL": {
            "code": "THA.UNI.PSL",
            "name": "Problem Solving",
            "parent_trf": "TRF.UNI",
            "description": "Identifying problems, gathering relevant information, generating possible solutions, evaluating options, and implementing effective solutions.",
            "keywords": ["problem solving", "troubleshooting", "solutions", "resolving", "identifying issues", "fixing", "debugging"],
        },
        "THA.UNI.CRT": {
            "code": "THA.UNI.CRT",
            "name": "Critical Thinking & Judgement",
            "parent_trf": "TRF.UNI",
            "description": "Analysing information objectively, evaluating evidence, recognising assumptions, and forming reasoned conclusions. Includes logical reasoning and sound decision-making.",
            "keywords": ["critical thinking", "analysis", "judgement", "reasoning", "evaluation", "decision making", "logic", "assessment"],
        },
        "THA.UNI.TMG": {
            "code": "THA.UNI.TMG",
            "name": "Time Management & Organisation",
            "parent_trf": "TRF.UNI",
            "description": "Planning, prioritising, and managing one's own time and workload effectively. Includes scheduling, meeting deadlines, and organising resources.",
            "keywords": ["time management", "planning", "prioritising", "scheduling", "organising", "deadlines", "workload", "efficiency"],
        },
        "THA.UNI.TWK": {
            "code": "THA.UNI.TWK",
            "name": "Teamwork & Collaboration",
            "parent_trf": "TRF.UNI",
            "description": "Working cooperatively with others toward shared goals. Includes contributing to group tasks, supporting colleagues, sharing information, and participating in team processes.",
            "keywords": ["teamwork", "collaboration", "cooperation", "group work", "team", "working together", "colleagues", "supporting"],
        },
        "THA.UNI.ETH": {
            "code": "THA.UNI.ETH",
            "name": "Workplace Ethics & Professionalism",
            "parent_trf": "TRF.UNI",
            "description": "Demonstrating integrity, responsibility, reliability, and professional conduct. Includes following codes of conduct, respecting confidentiality, and maintaining ethical standards.",
            "keywords": ["ethics", "professionalism", "integrity", "responsibility", "conduct", "confidentiality", "accountability", "reliability"],
        },
        "THA.UNI.CUL": {
            "code": "THA.UNI.CUL",
            "name": "Cultural Awareness & Inclusion",
            "parent_trf": "TRF.UNI",
            "description": "Recognising and respecting cultural diversity, working effectively with people from different backgrounds, and contributing to inclusive environments.",
            "keywords": ["cultural awareness", "diversity", "inclusion", "respect", "cross-cultural", "indigenous", "multicultural", "sensitivity"],
        },
        "THA.UNI.SLF": {
            "code": "THA.UNI.SLF",
            "name": "Self-Management & Resilience",
            "parent_trf": "TRF.UNI",
            "description": "Managing one's own emotions, stress, and motivation. Includes adaptability, persistence, maintaining composure under pressure, and self-regulation.",
            "keywords": ["self-management", "resilience", "adaptability", "stress management", "motivation", "composure", "persistence", "flexibility"],
        },
        "THA.UNI.SAF": {
            "code": "THA.UNI.SAF",
            "name": "Personal Safety Awareness",
            "parent_trf": "TRF.UNI",
            "description": "Recognising personal safety risks, following basic safety procedures, using personal protective equipment, and maintaining safe work habits.",
            "keywords": ["safety", "PPE", "hazard", "safe work", "personal protection", "safety awareness", "safe practices"],
        },

        # ═══════════════════════════════════════════════════════════
        #  TRF.BRD — CROSS-SECTOR ABILITIES
        #  Specialist capabilities transferable across multiple industries
        # ═══════════════════════════════════════════════════════════

        "THA.BRD.RSK": {
            "code": "THA.BRD.RSK",
            "name": "Risk Assessment & Mitigation",
            "parent_trf": "TRF.BRD",
            "description": "Systematically identifying, evaluating, and controlling risks. Includes hazard identification, risk matrices, hierarchy of controls, and risk treatment plans.",
            "keywords": ["risk assessment", "risk management", "hazard identification", "risk mitigation", "risk matrix", "controls", "risk analysis"],
        },
        "THA.BRD.LDR": {
            "code": "THA.BRD.LDR",
            "name": "Leadership & People Management",
            "parent_trf": "TRF.BRD",
            "description": "Guiding, motivating, and directing people. Includes delegating tasks, providing feedback, performance management, mentoring, and building team capability.",
            "keywords": ["leadership", "management", "supervision", "delegation", "mentoring", "coaching", "directing", "performance management"],
        },
        "THA.BRD.PRJ": {
            "code": "THA.BRD.PRJ",
            "name": "Project Planning & Coordination",
            "parent_trf": "TRF.BRD",
            "description": "Planning, organising, and coordinating projects or work activities. Includes scope definition, resource allocation, scheduling, monitoring progress, and managing deliverables.",
            "keywords": ["project management", "planning", "coordination", "scheduling", "milestones", "deliverables", "project plan", "resource allocation"],
        },
        "THA.BRD.QMS": {
            "code": "THA.BRD.QMS",
            "name": "Quality Assurance & Improvement",
            "parent_trf": "TRF.BRD",
            "description": "Monitoring, evaluating, and improving the quality of products, services, or processes. Includes quality standards, auditing, continuous improvement, and defect analysis.",
            "keywords": ["quality", "quality assurance", "quality control", "continuous improvement", "audit", "standards", "inspection", "compliance"],
        },
        "THA.BRD.TRN": {
            "code": "THA.BRD.TRN",
            "name": "Training & Knowledge Transfer",
            "parent_trf": "TRF.BRD",
            "description": "Teaching, instructing, and transferring knowledge or skills to others. Includes designing training, delivering instruction, assessing competency, and facilitating learning.",
            "keywords": ["training", "teaching", "instruction", "coaching", "knowledge transfer", "facilitation", "assessment", "mentoring", "demonstration"],
        },
        "THA.BRD.REG": {
            "code": "THA.BRD.REG",
            "name": "Regulatory Compliance & Governance",
            "parent_trf": "TRF.BRD",
            "description": "Ensuring adherence to laws, regulations, standards, and organisational policies. Includes interpreting legislation, maintaining compliance records, and conducting compliance audits.",
            "keywords": ["compliance", "regulation", "legislation", "governance", "policy", "standards", "legal", "regulatory", "audit"],
        },
        "THA.BRD.DAT": {
            "code": "THA.BRD.DAT",
            "name": "Data Analysis & Interpretation",
            "parent_trf": "TRF.BRD",
            "description": "Collecting, organising, analysing, and interpreting data to extract meaningful insights. Includes statistical analysis, data visualisation, trend identification, and evidence-based reasoning.",
            "keywords": ["data analysis", "statistics", "interpretation", "data collection", "trends", "reporting", "metrics", "evidence", "analytics"],
        },
        "THA.BRD.NEG": {
            "code": "THA.BRD.NEG",
            "name": "Negotiation & Conflict Resolution",
            "parent_trf": "TRF.BRD",
            "description": "Reaching agreements, resolving disputes, and managing conflicting interests. Includes mediation, persuasion, compromise, and constructive confrontation.",
            "keywords": ["negotiation", "conflict resolution", "mediation", "dispute", "compromise", "persuasion", "agreement", "facilitation"],
        },
        "THA.BRD.CUS": {
            "code": "THA.BRD.CUS",
            "name": "Client & Stakeholder Engagement",
            "parent_trf": "TRF.BRD",
            "description": "Building and maintaining relationships with clients, customers, and stakeholders. Includes needs assessment, service delivery, complaint handling, and relationship management.",
            "keywords": ["customer service", "client relations", "stakeholder", "engagement", "complaints", "service delivery", "relationship management"],
        },
        "THA.BRD.RPT": {
            "code": "THA.BRD.RPT",
            "name": "Technical Reporting & Documentation",
            "parent_trf": "TRF.BRD",
            "description": "Preparing accurate technical documentation including reports, specifications, procedures, and records. Includes technical writing, record keeping, and documentation standards.",
            "keywords": ["technical writing", "documentation", "reporting", "records", "specifications", "procedures", "logs", "technical reports"],
        },
        "THA.BRD.FIN": {
            "code": "THA.BRD.FIN",
            "name": "Financial Management & Budgeting",
            "parent_trf": "TRF.BRD",
            "description": "Managing financial resources including budgeting, cost estimation, financial reporting, invoicing, and financial decision-making.",
            "keywords": ["budget", "finance", "costing", "invoicing", "financial management", "accounting", "expenditure", "revenue", "profit"],
        },
        "THA.BRD.WHS": {
            "code": "THA.BRD.WHS",
            "name": "Workplace Health & Safety Management",
            "parent_trf": "TRF.BRD",
            "description": "Implementing and managing workplace health and safety systems. Includes WHS policy development, incident investigation, safety auditing, and emergency response coordination.",
            "keywords": ["WHS", "OHS", "safety management", "incident investigation", "safety audit", "emergency response", "safety system", "safety policy"],
        },
        "THA.BRD.ENV": {
            "code": "THA.BRD.ENV",
            "name": "Environmental & Sustainability Management",
            "parent_trf": "TRF.BRD",
            "description": "Managing environmental impacts and promoting sustainable practices. Includes waste management, resource conservation, environmental monitoring, and sustainability planning.",
            "keywords": ["environmental", "sustainability", "waste management", "conservation", "recycling", "emissions", "environmental impact", "green"],
        },
        "THA.BRD.PRC": {
            "code": "THA.BRD.PRC",
            "name": "Process Design & Optimisation",
            "parent_trf": "TRF.BRD",
            "description": "Designing, mapping, and improving work processes and workflows. Includes process analysis, efficiency improvement, standardisation, and lean methodology.",
            "keywords": ["process improvement", "workflow", "optimisation", "efficiency", "lean", "standardisation", "procedures", "process design"],
        },
        "THA.BRD.SCM": {
            "code": "THA.BRD.SCM",
            "name": "Supply Chain & Logistics Coordination",
            "parent_trf": "TRF.BRD",
            "description": "Coordinating the flow of materials, products, and information through supply chains. Includes procurement, inventory management, distribution, and logistics planning.",
            "keywords": ["supply chain", "logistics", "procurement", "inventory", "warehousing", "distribution", "ordering", "stock management"],
        },
        "THA.BRD.INN": {
            "code": "THA.BRD.INN",
            "name": "Innovation & Creative Problem Solving",
            "parent_trf": "TRF.BRD",
            "description": "Generating novel ideas, developing creative solutions, and driving innovation. Includes design thinking, ideation, prototyping, and implementing new approaches.",
            "keywords": ["innovation", "creativity", "design thinking", "ideation", "novel solutions", "invention", "creative", "new approaches"],
        },
        "THA.BRD.STP": {
            "code": "THA.BRD.STP",
            "name": "Strategic Planning & Decision Making",
            "parent_trf": "TRF.BRD",
            "description": "Developing long-term plans, setting objectives, and making complex decisions with incomplete information. Includes scenario analysis, strategic thinking, and policy development.",
            "keywords": ["strategic planning", "strategy", "decision making", "objectives", "policy", "long-term planning", "vision", "direction"],
        },
        "THA.BRD.CHG": {
            "code": "THA.BRD.CHG",
            "name": "Change Management & Adaptation",
            "parent_trf": "TRF.BRD",
            "description": "Managing and facilitating organisational or procedural change. Includes stakeholder communication during transitions, resistance management, and implementation planning.",
            "keywords": ["change management", "transition", "transformation", "adaptation", "implementation", "restructure", "reform"],
        },
        "THA.BRD.INF": {
            "code": "THA.BRD.INF",
            "name": "Information Management & Research",
            "parent_trf": "TRF.BRD",
            "description": "Sourcing, organising, evaluating, and managing information. Includes research methods, information systems, knowledge management, and evidence-based practice.",
            "keywords": ["research", "information management", "knowledge management", "evidence", "sourcing", "information systems", "records management"],
        },
        "THA.BRD.PRS": {
            "code": "THA.BRD.PRS",
            "name": "Presentation & Public Communication",
            "parent_trf": "TRF.BRD",
            "description": "Delivering information to groups through presentations, demonstrations, and public speaking. Includes visual aids, audience engagement, and persuasive communication.",
            "keywords": ["presentation", "public speaking", "demonstration", "visual aids", "audience", "briefing", "seminar", "workshop delivery"],
        },

        # ═══════════════════════════════════════════════════════════
        #  TRF.SEC — SECTOR-SPECIFIC ABILITIES
        #  Capabilities relevant within a sector or related sectors
        # ═══════════════════════════════════════════════════════════

        "THA.SEC.DGN": {
            "code": "THA.SEC.DGN",
            "name": "Design & Drafting",
            "parent_trf": "TRF.SEC",
            "description": "Creating designs, plans, drawings, and specifications. Includes CAD, technical drawing, schematic design, and design validation.",
            "keywords": ["design", "drafting", "CAD", "drawing", "blueprint", "schematic", "specifications", "plans", "modelling"],
        },
        "THA.SEC.INS": {
            "code": "THA.SEC.INS",
            "name": "Inspection & Testing",
            "parent_trf": "TRF.SEC",
            "description": "Examining products, systems, or structures to verify conformance to standards. Includes testing procedures, measurement, non-destructive testing, and quality checks.",
            "keywords": ["inspection", "testing", "examination", "verification", "quality check", "measurement", "compliance check", "assessment"],
        },
        "THA.SEC.CAL": {
            "code": "THA.SEC.CAL",
            "name": "Calibration & Precision Measurement",
            "parent_trf": "TRF.SEC",
            "description": "Calibrating instruments and making precise measurements. Includes metrology, instrument calibration, tolerance checking, and measurement uncertainty.",
            "keywords": ["calibration", "measurement", "precision", "metrology", "tolerance", "instruments", "gauges", "accuracy"],
        },
        "THA.SEC.DIA": {
            "code": "THA.SEC.DIA",
            "name": "Diagnostic Reasoning & Fault Finding",
            "parent_trf": "TRF.SEC",
            "description": "Systematically diagnosing faults, malfunctions, or conditions. Includes symptom analysis, root cause identification, diagnostic tools, and systematic elimination.",
            "keywords": ["diagnosis", "fault finding", "troubleshooting", "root cause", "symptoms", "diagnostic", "malfunction", "failure analysis"],
        },
        "THA.SEC.PAT": {
            "code": "THA.SEC.PAT",
            "name": "Client & Patient Assessment",
            "parent_trf": "TRF.SEC",
            "description": "Assessing the needs, conditions, or capabilities of clients, patients, or service users. Includes intake assessment, needs analysis, screening, and triage.",
            "keywords": ["assessment", "patient assessment", "client assessment", "screening", "triage", "needs analysis", "intake", "evaluation"],
        },
        "THA.SEC.CPL": {
            "code": "THA.SEC.CPL",
            "name": "Care Planning & Case Management",
            "parent_trf": "TRF.SEC",
            "description": "Developing and managing individualised care, treatment, or service plans. Includes goal setting, intervention planning, progress monitoring, and case coordination.",
            "keywords": ["care plan", "case management", "treatment plan", "individual plan", "service plan", "care coordination", "intervention", "goals"],
        },
        "THA.SEC.MON": {
            "code": "THA.SEC.MON",
            "name": "Monitoring & Surveillance",
            "parent_trf": "TRF.SEC",
            "description": "Continuously observing and monitoring systems, conditions, processes, or environments. Includes vital signs monitoring, process monitoring, CCTV, and alarm response.",
            "keywords": ["monitoring", "surveillance", "observation", "watch", "tracking", "vital signs", "alarms", "sensors", "patrol"],
        },
        "THA.SEC.SMP": {
            "code": "THA.SEC.SMP",
            "name": "Sampling & Laboratory Technique",
            "parent_trf": "TRF.SEC",
            "description": "Collecting, preparing, and processing samples using laboratory or field techniques. Includes specimen handling, sample preparation, contamination control, and laboratory protocols.",
            "keywords": ["sampling", "laboratory", "specimen", "sample preparation", "testing", "analysis", "contamination control", "protocols"],
        },
        "THA.SEC.SRV": {
            "code": "THA.SEC.SRV",
            "name": "Surveying & Spatial Measurement",
            "parent_trf": "TRF.SEC",
            "description": "Measuring and mapping physical spaces, land, or structures. Includes land surveying, site measurement, GPS, GIS, and spatial data collection.",
            "keywords": ["surveying", "measurement", "spatial", "GPS", "GIS", "mapping", "site measurement", "levels", "boundaries"],
        },
        "THA.SEC.EST": {
            "code": "THA.SEC.EST",
            "name": "Estimation & Costing",
            "parent_trf": "TRF.SEC",
            "description": "Estimating quantities, costs, timeframes, and resource requirements for projects or tasks. Includes bill of quantities, material takeoff, and cost estimation.",
            "keywords": ["estimation", "costing", "quantities", "bill of quantities", "material takeoff", "pricing", "quotes", "tender"],
        },
        "THA.SEC.MKT": {
            "code": "THA.SEC.MKT",
            "name": "Marketing & Promotion",
            "parent_trf": "TRF.SEC",
            "description": "Promoting products, services, or ideas to target audiences. Includes market research, advertising, branding, digital marketing, and sales strategy.",
            "keywords": ["marketing", "promotion", "advertising", "branding", "sales", "market research", "digital marketing", "campaign"],
        },
        "THA.SEC.FDP": {
            "code": "THA.SEC.FDP",
            "name": "Food Preparation & Hygiene",
            "parent_trf": "TRF.SEC",
            "description": "Preparing, cooking, and handling food safely and hygienically. Includes food safety standards, HACCP, kitchen operations, and dietary requirements.",
            "keywords": ["food preparation", "cooking", "food safety", "hygiene", "HACCP", "kitchen", "dietary", "food handling", "catering"],
        },
        "THA.SEC.HOS": {
            "code": "THA.SEC.HOS",
            "name": "Hospitality & Service Operations",
            "parent_trf": "TRF.SEC",
            "description": "Managing hospitality service operations including accommodation, food and beverage service, event coordination, and guest services.",
            "keywords": ["hospitality", "service", "accommodation", "food service", "beverage", "events", "guest services", "front desk"],
        },
        "THA.SEC.CRE": {
            "code": "THA.SEC.CRE",
            "name": "Creative & Artistic Expression",
            "parent_trf": "TRF.SEC",
            "description": "Applying creative and artistic skills to produce visual, auditory, or performative works. Includes visual arts, graphic design, photography, music, and performance.",
            "keywords": ["creative", "artistic", "design", "visual arts", "graphic design", "photography", "music", "performance", "crafts"],
        },
        "THA.SEC.AGR": {
            "code": "THA.SEC.AGR",
            "name": "Agricultural & Horticultural Practice",
            "parent_trf": "TRF.SEC",
            "description": "Applying knowledge and techniques for growing crops, managing livestock, and maintaining landscapes. Includes planting, harvesting, soil management, and pest control.",
            "keywords": ["agriculture", "horticulture", "farming", "crops", "livestock", "soil", "planting", "harvesting", "pest control", "irrigation"],
        },
        "THA.SEC.ANM": {
            "code": "THA.SEC.ANM",
            "name": "Animal Care & Handling",
            "parent_trf": "TRF.SEC",
            "description": "Caring for, handling, and managing animals safely and humanely. Includes feeding, health monitoring, behaviour management, and welfare compliance.",
            "keywords": ["animal care", "animal handling", "animal welfare", "livestock", "veterinary", "feeding", "breeding", "husbandry"],
        },
        "THA.SEC.SFT": {
            "code": "THA.SEC.SFT",
            "name": "Software & Systems Development",
            "parent_trf": "TRF.SEC",
            "description": "Developing, configuring, and maintaining software applications and information systems. Includes programming, system administration, database management, and IT support.",
            "keywords": ["software", "programming", "coding", "systems", "database", "IT", "development", "applications", "networking"],
        },
        "THA.SEC.SEC": {
            "code": "THA.SEC.SEC",
            "name": "Security & Protective Services",
            "parent_trf": "TRF.SEC",
            "description": "Providing security and protection for people, property, and assets. Includes access control, threat assessment, crowd management, and emergency evacuation.",
            "keywords": ["security", "protection", "access control", "surveillance", "crowd management", "threat assessment", "guarding"],
        },

        # ═══════════════════════════════════════════════════════════
        #  TRF.OCC — OCCUPATION-SPECIFIC ABILITIES
        #  Deep specialist capabilities unique to specific occupations
        # ═══════════════════════════════════════════════════════════

        "THA.OCC.FAB": {
            "code": "THA.OCC.FAB",
            "name": "Material Fabrication & Joining",
            "parent_trf": "TRF.OCC",
            "description": "Cutting, shaping, joining, and finishing materials including metal, wood, plastics, and composites. Includes welding, soldering, brazing, adhesive bonding, and mechanical fastening.",
            "keywords": ["welding", "fabrication", "cutting", "joining", "soldering", "brazing", "metalwork", "woodwork", "assembly"],
        },
        "THA.OCC.ELC": {
            "code": "THA.OCC.ELC",
            "name": "Electrical & Electronic Systems",
            "parent_trf": "TRF.OCC",
            "description": "Installing, maintaining, and repairing electrical and electronic systems. Includes wiring, circuit testing, control systems, and electrical safety.",
            "keywords": ["electrical", "electronics", "wiring", "circuits", "control systems", "installation", "electrical testing", "power"],
        },
        "THA.OCC.MEC": {
            "code": "THA.OCC.MEC",
            "name": "Mechanical Systems & Machinery",
            "parent_trf": "TRF.OCC",
            "description": "Operating, maintaining, and repairing mechanical systems and machinery. Includes engines, pumps, hydraulics, pneumatics, and mechanical components.",
            "keywords": ["mechanical", "machinery", "engines", "hydraulics", "pneumatics", "maintenance", "repair", "servicing", "operation"],
        },
        "THA.OCC.PLB": {
            "code": "THA.OCC.PLB",
            "name": "Plumbing & Fluid Systems",
            "parent_trf": "TRF.OCC",
            "description": "Installing, maintaining, and repairing plumbing, gas, and fluid systems. Includes pipe fitting, drainage, water supply, gas systems, and backflow prevention.",
            "keywords": ["plumbing", "piping", "drainage", "water supply", "gas fitting", "pipe fitting", "fluid systems", "sanitation"],
        },
        "THA.OCC.BLD": {
            "code": "THA.OCC.BLD",
            "name": "Building & Structural Construction",
            "parent_trf": "TRF.OCC",
            "description": "Constructing, assembling, and erecting building structures. Includes carpentry, bricklaying, concreting, formwork, scaffolding, and structural assembly.",
            "keywords": ["construction", "building", "carpentry", "bricklaying", "concreting", "formwork", "scaffolding", "framing", "roofing"],
        },
        "THA.OCC.HVR": {
            "code": "THA.OCC.HVR",
            "name": "HVAC & Refrigeration Systems",
            "parent_trf": "TRF.OCC",
            "description": "Installing, servicing, and repairing heating, ventilation, air conditioning, and refrigeration systems. Includes refrigerant handling, ductwork, and climate control.",
            "keywords": ["HVAC", "refrigeration", "air conditioning", "heating", "ventilation", "ductwork", "refrigerant", "climate control"],
        },
        "THA.OCC.VHC": {
            "code": "THA.OCC.VHC",
            "name": "Vehicle Operation & Maintenance",
            "parent_trf": "TRF.OCC",
            "description": "Operating, maintaining, and repairing vehicles and mobile equipment. Includes automotive mechanics, heavy vehicle operation, fleet management, and vehicle inspection.",
            "keywords": ["vehicle", "automotive", "driving", "mechanics", "fleet", "heavy vehicle", "maintenance", "engine", "transmission"],
        },
        "THA.OCC.CLN": {
            "code": "THA.OCC.CLN",
            "name": "Clinical & Therapeutic Procedures",
            "parent_trf": "TRF.OCC",
            "description": "Performing clinical assessments, therapeutic interventions, and medical procedures. Includes wound care, medication administration, physiotherapy, and clinical observations.",
            "keywords": ["clinical", "therapeutic", "medical procedures", "wound care", "medication", "physiotherapy", "nursing", "treatment"],
        },
        "THA.OCC.PHA": {
            "code": "THA.OCC.PHA",
            "name": "Pharmaceutical & Chemical Handling",
            "parent_trf": "TRF.OCC",
            "description": "Handling, preparing, dispensing, and managing pharmaceutical products and chemical substances. Includes dosage calculation, chemical safety, and MSDS compliance.",
            "keywords": ["pharmaceutical", "chemical", "medication", "dispensing", "hazardous substances", "MSDS", "dosage", "compounds"],
        },
        "THA.OCC.FIR": {
            "code": "THA.OCC.FIR",
            "name": "Emergency & First Response",
            "parent_trf": "TRF.OCC",
            "description": "Responding to emergencies including fire, medical, rescue, and hazardous situations. Includes first aid, CPR, firefighting, and emergency coordination.",
            "keywords": ["emergency response", "first aid", "CPR", "rescue", "firefighting", "paramedic", "emergency management", "triage"],
        },
        "THA.OCC.MAC": {
            "code": "THA.OCC.MAC",
            "name": "Machining & Precision Manufacturing",
            "parent_trf": "TRF.OCC",
            "description": "Operating machine tools to shape materials to precise specifications. Includes CNC operation, turning, milling, grinding, and toolmaking.",
            "keywords": ["machining", "CNC", "turning", "milling", "grinding", "lathe", "toolmaking", "precision", "manufacturing"],
        },
        "THA.OCC.SFC": {
            "code": "THA.OCC.SFC",
            "name": "Surface Finishing & Coating",
            "parent_trf": "TRF.OCC",
            "description": "Applying surface treatments, coatings, and finishes to materials and products. Includes painting, powder coating, anodising, plating, and polishing.",
            "keywords": ["painting", "coating", "finishing", "polishing", "plating", "powder coating", "surface treatment", "refinishing"],
        },
        "THA.OCC.TXL": {
            "code": "THA.OCC.TXL",
            "name": "Textile & Garment Production",
            "parent_trf": "TRF.OCC",
            "description": "Working with textiles and fabrics to produce garments, furnishings, and textile products. Includes cutting, sewing, pattern making, and textile processing.",
            "keywords": ["sewing", "textiles", "garment", "pattern making", "fabric", "tailoring", "upholstery", "fashion"],
        },
        "THA.OCC.BIO": {
            "code": "THA.OCC.BIO",
            "name": "Biological & Specimen Processing",
            "parent_trf": "TRF.OCC",
            "description": "Handling, processing, and managing biological materials and specimens. Includes tissue processing, specimen collection, cryogenics, and biocontainment procedures.",
            "keywords": ["biological", "specimen", "tissue", "sample processing", "cryogenics", "pathology", "microbiology", "biocontainment"],
        },
        "THA.OCC.EQM": {
            "code": "THA.OCC.EQM",
            "name": "Specialist Equipment Maintenance",
            "parent_trf": "TRF.OCC",
            "description": "Maintaining, cleaning, and servicing specialised equipment and instruments. Includes preventive maintenance schedules, equipment hygiene, sterilisation, and functional testing.",
            "keywords": ["equipment maintenance", "servicing", "cleaning", "sterilisation", "calibration", "preventive maintenance", "instrument care"],
        },
        "THA.OCC.HVY": {
            "code": "THA.OCC.HVY",
            "name": "Heavy Equipment & Plant Operation",
            "parent_trf": "TRF.OCC",
            "description": "Operating heavy plant and equipment including cranes, excavators, forklifts, and earthmoving machinery. Includes load management and operator safety.",
            "keywords": ["crane", "excavator", "forklift", "earthmoving", "plant operation", "heavy equipment", "rigging", "lifting"],
        },
        "THA.OCC.MAR": {
            "code": "THA.OCC.MAR",
            "name": "Maritime & Vessel Operations",
            "parent_trf": "TRF.OCC",
            "description": "Operating, navigating, and maintaining marine vessels and watercraft. Includes seamanship, navigation, marine safety, and cargo handling.",
            "keywords": ["maritime", "vessel", "navigation", "seamanship", "marine", "boat", "ship", "cargo", "watercraft"],
        },
        "THA.OCC.AVN": {
            "code": "THA.OCC.AVN",
            "name": "Aviation & Aircraft Systems",
            "parent_trf": "TRF.OCC",
            "description": "Operating, maintaining, and managing aircraft and aviation systems. Includes aircraft maintenance, flight operations, air traffic procedures, and aviation safety.",
            "keywords": ["aviation", "aircraft", "flight", "air traffic", "aircraft maintenance", "avionics", "pilot", "aerospace"],
        },
        "THA.OCC.MNG": {
            "code": "THA.OCC.MNG",
            "name": "Mining & Extraction Operations",
            "parent_trf": "TRF.OCC",
            "description": "Performing mining, quarrying, and resource extraction operations. Includes drilling, blasting, ore processing, mine safety, and ground support.",
            "keywords": ["mining", "extraction", "drilling", "blasting", "ore", "quarrying", "underground", "open cut", "mineral"],
        },
        "THA.OCC.PCS": {
            "code": "THA.OCC.PCS",
            "name": "Personal Care & Beauty Services",
            "parent_trf": "TRF.OCC",
            "description": "Providing personal care and beauty treatments. Includes hairdressing, beauty therapy, massage, nail technology, and skin care.",
            "keywords": ["hairdressing", "beauty", "massage", "nail", "skin care", "grooming", "personal care", "therapy", "cosmetics"],
        },
        "THA.OCC.SPR": {
            "code": "THA.OCC.SPR",
            "name": "Sport & Fitness Instruction",
            "parent_trf": "TRF.OCC",
            "description": "Coaching, instructing, and facilitating sport, fitness, and recreational activities. Includes exercise programming, coaching techniques, and fitness assessment.",
            "keywords": ["sport", "fitness", "coaching", "exercise", "recreation", "training programs", "physical activity", "athletics"],
        },
    },
}

# Helper: map TRF code → list of THA codes in that group
TRF_TO_THA = {}
for code, val in TRANSFERABLE_HUMAN_ABILITY_FACET["values"].items():
    parent = val["parent_trf"]
    TRF_TO_THA.setdefault(parent, []).append(code)

# Validate completeness
_TRF_COVERAGE = {
    "TRF.UNI": len(TRF_TO_THA.get("TRF.UNI", [])),
    "TRF.BRD": len(TRF_TO_THA.get("TRF.BRD", [])),
    "TRF.SEC": len(TRF_TO_THA.get("TRF.SEC", [])),
    "TRF.OCC": len(TRF_TO_THA.get("TRF.OCC", [])),
}

# Expected: UNI ~13, BRD ~20, SEC ~18, OCC ~22 = ~73 total
TOTAL_THA_VALUES = sum(_TRF_COVERAGE.values())
