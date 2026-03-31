"""
Transferable Human Ability (THA) Facet Definition

~160 functional human abilities organized under TRF categories.
Each describes WHAT a human can do, not WHERE they do it.
Domain/industry is captured by the ASCED facet.
"""

TRANSFERABLE_HUMAN_ABILITY_FACET = {
    "facet_id": "THA",
    "facet_name": "Transferable Human Ability",
    "description": "Functional human capability applied across contexts. Describes WHAT a person can do, independent of industry.",
    "multi_value": False,
    "parent_facet": "TRF",
    "values": {
        "THA.UNI.ORC": {
                "code": "THA.UNI.ORC",
                "name": "Oral Communication",
                "parent_trf": "TRF.UNI",
                "description": "Listening to and understanding spoken information, and communicating ideas clearly through speech, presentations, and conversations."
        },
        "THA.UNI.WRC": {
                "code": "THA.UNI.WRC",
                "name": "Written Communication",
                "parent_trf": "TRF.UNI",
                "description": "Reading, understanding, and producing written information including reports, emails, forms, and workplace documentation."
        },
        "THA.UNI.NUM": {
                "code": "THA.UNI.NUM",
                "name": "Numeracy & Calculation",
                "parent_trf": "TRF.UNI",
                "description": "Applying mathematical concepts including arithmetic, measurement, estimation, ratios, and basic statistical reasoning."
        },
        "THA.UNI.DIG": {
                "code": "THA.UNI.DIG",
                "name": "Digital Literacy",
                "parent_trf": "TRF.UNI",
                "description": "Using digital devices, software applications, online platforms, and workplace information systems effectively."
        },
        "THA.UNI.LRN": {
                "code": "THA.UNI.LRN",
                "name": "Learning & Self-Development",
                "parent_trf": "TRF.UNI",
                "description": "Acquiring new knowledge and skills, reflecting on performance, seeking feedback, maintaining professional currency."
        },
        "THA.UNI.PSL": {
                "code": "THA.UNI.PSL",
                "name": "Problem Solving & Critical Thinking",
                "parent_trf": "TRF.UNI",
                "description": "Identifying problems, analysing information, evaluating evidence, generating solutions, and making reasoned decisions."
        },
        "THA.UNI.TMG": {
                "code": "THA.UNI.TMG",
                "name": "Time Management & Organisation",
                "parent_trf": "TRF.UNI",
                "description": "Planning, prioritising, and managing workload, schedules, deadlines, and workplace resources effectively."
        },
        "THA.UNI.TWK": {
                "code": "THA.UNI.TWK",
                "name": "Teamwork & Collaboration",
                "parent_trf": "TRF.UNI",
                "description": "Working cooperatively with others, contributing to group tasks, supporting colleagues, and participating in team processes."
        },
        "THA.UNI.ETH": {
                "code": "THA.UNI.ETH",
                "name": "Workplace Ethics & Professionalism",
                "parent_trf": "TRF.UNI",
                "description": "Demonstrating integrity, responsibility, reliability, following codes of conduct, and maintaining confidentiality."
        },
        "THA.UNI.CUL": {
                "code": "THA.UNI.CUL",
                "name": "Cultural Awareness & Inclusion",
                "parent_trf": "TRF.UNI",
                "description": "Respecting cultural diversity, working with people from different backgrounds, and contributing to inclusive environments."
        },
        "THA.UNI.SLF": {
                "code": "THA.UNI.SLF",
                "name": "Self-Management & Resilience",
                "parent_trf": "TRF.UNI",
                "description": "Managing emotions, stress, and motivation; adapting to change; maintaining composure and persistence under pressure."
        },
        "THA.UNI.SAF": {
                "code": "THA.UNI.SAF",
                "name": "Personal Safety Awareness",
                "parent_trf": "TRF.UNI",
                "description": "Recognising safety risks, following safety procedures, using PPE, applying manual handling techniques, and maintaining safe work habits."
        },
        "THA.BRD.RSK": {
                "code": "THA.BRD.RSK",
                "name": "Risk Assessment & Mitigation",
                "parent_trf": "TRF.BRD",
                "description": "Systematically identifying, evaluating, and controlling risks using hazard identification, risk matrices, and hierarchy of controls."
        },
        "THA.BRD.LDR": {
                "code": "THA.BRD.LDR",
                "name": "Leadership & People Management",
                "parent_trf": "TRF.BRD",
                "description": "Guiding, motivating, and directing people including delegation, performance management, mentoring, and building team capability."
        },
        "THA.BRD.PRJ": {
                "code": "THA.BRD.PRJ",
                "name": "Project Planning & Coordination",
                "parent_trf": "TRF.BRD",
                "description": "Planning, organising, and coordinating projects including scope, resources, scheduling, and monitoring deliverables."
        },
        "THA.BRD.QMS": {
                "code": "THA.BRD.QMS",
                "name": "Quality Assurance & Improvement",
                "parent_trf": "TRF.BRD",
                "description": "Monitoring, evaluating, and improving quality through standards, auditing, continuous improvement, and defect analysis."
        },
        "THA.BRD.TRN": {
                "code": "THA.BRD.TRN",
                "name": "Training & Knowledge Transfer",
                "parent_trf": "TRF.BRD",
                "description": "Teaching, instructing, and transferring knowledge to others including training design, delivery, facilitation, and competency assessment."
        },
        "THA.BRD.REG": {
                "code": "THA.BRD.REG",
                "name": "Regulatory Compliance & Governance",
                "parent_trf": "TRF.BRD",
                "description": "Ensuring adherence to laws, regulations, standards, and organisational policies through interpretation, documentation, and auditing."
        },
        "THA.BRD.DAT": {
                "code": "THA.BRD.DAT",
                "name": "Data Analysis & Interpretation",
                "parent_trf": "TRF.BRD",
                "description": "Collecting, organising, analysing, and interpreting data to extract insights, identify trends, and support evidence-based decisions."
        },
        "THA.BRD.NEG": {
                "code": "THA.BRD.NEG",
                "name": "Negotiation & Conflict Resolution",
                "parent_trf": "TRF.BRD",
                "description": "Reaching agreements, resolving disputes, mediating between parties, and managing conflicting interests constructively."
        },
        "THA.BRD.CUS": {
                "code": "THA.BRD.CUS",
                "name": "Client & Stakeholder Engagement",
                "parent_trf": "TRF.BRD",
                "description": "Building and maintaining relationships with clients, customers, and stakeholders through needs assessment, service delivery, and complaint handling."
        },
        "THA.BRD.RPT": {
                "code": "THA.BRD.RPT",
                "name": "Technical Reporting & Documentation",
                "parent_trf": "TRF.BRD",
                "description": "Preparing accurate technical reports, specifications, procedures, work instructions, incident reports, and compliance records."
        },
        "THA.BRD.FIN": {
                "code": "THA.BRD.FIN",
                "name": "Financial Management & Budgeting",
                "parent_trf": "TRF.BRD",
                "description": "Managing financial resources including budgeting, cost estimation, financial reporting, invoicing, and expenditure monitoring."
        },
        "THA.BRD.WHS": {
                "code": "THA.BRD.WHS",
                "name": "Workplace Health & Safety Management",
                "parent_trf": "TRF.BRD",
                "description": "Implementing and managing WHS systems including policy development, incident investigation, safety auditing, and emergency coordination."
        },
        "THA.BRD.ENV": {
                "code": "THA.BRD.ENV",
                "name": "Environmental & Sustainability Management",
                "parent_trf": "TRF.BRD",
                "description": "Managing environmental impacts through waste management, resource conservation, environmental monitoring, and sustainability planning."
        },
        "THA.BRD.PRC": {
                "code": "THA.BRD.PRC",
                "name": "Process Design & Optimisation",
                "parent_trf": "TRF.BRD",
                "description": "Designing, mapping, and improving work processes and workflows using process analysis, standardisation, and lean methodology."
        },
        "THA.BRD.SCM": {
                "code": "THA.BRD.SCM",
                "name": "Supply Chain & Logistics Coordination",
                "parent_trf": "TRF.BRD",
                "description": "Coordinating material, product, and information flow through procurement, inventory management, warehousing, and distribution."
        },
        "THA.BRD.STP": {
                "code": "THA.BRD.STP",
                "name": "Strategic Planning & Decision Making",
                "parent_trf": "TRF.BRD",
                "description": "Developing long-term plans, setting objectives, conducting scenario analysis, and making complex decisions with incomplete information."
        },
        "THA.BRD.INF": {
                "code": "THA.BRD.INF",
                "name": "Information Management & Research",
                "parent_trf": "TRF.BRD",
                "description": "Sourcing, organising, evaluating, and managing information through research methods, records management, and knowledge systems."
        },
        "THA.SEC.DGN": {
                "code": "THA.SEC.DGN",
                "name": "Design & Drafting",
                "parent_trf": "TRF.SEC",
                "description": "Creating designs, plans, drawings, specifications, CAD models, schematics, and 3D visualisations for construction, manufacturing, or engineering."
        },
        "THA.SEC.INS": {
                "code": "THA.SEC.INS",
                "name": "Inspection & Testing",
                "parent_trf": "TRF.SEC",
                "description": "Examining products, systems, or structures to verify conformance through visual inspection, dimensional checks, pressure testing, and compliance verification."
        },
        "THA.SEC.CAL": {
                "code": "THA.SEC.CAL",
                "name": "Calibration & Precision Measurement",
                "parent_trf": "TRF.SEC",
                "description": "Calibrating instruments, making precise measurements, checking tolerances, and applying metrology principles with gauges and measuring devices."
        },
        "THA.SEC.DIA": {
                "code": "THA.SEC.DIA",
                "name": "Diagnostic Reasoning & Fault Finding",
                "parent_trf": "TRF.SEC",
                "description": "Systematically diagnosing faults and malfunctions through symptom analysis, root cause identification, and use of diagnostic tools."
        },
        "THA.SEC.PAT": {
                "code": "THA.SEC.PAT",
                "name": "Client & Patient Assessment",
                "parent_trf": "TRF.SEC",
                "description": "Assessing needs, conditions, or capabilities of clients, patients, or service users through intake, screening, triage, and needs analysis."
        },
        "THA.SEC.CPL": {
                "code": "THA.SEC.CPL",
                "name": "Care Planning & Case Management",
                "parent_trf": "TRF.SEC",
                "description": "Developing and managing individualised care, treatment, or service plans including goal setting, progress monitoring, and case coordination."
        },
        "THA.SEC.MON": {
                "code": "THA.SEC.MON",
                "name": "Monitoring & Surveillance",
                "parent_trf": "TRF.SEC",
                "description": "Continuously observing systems, conditions, or environments including vital signs monitoring, process monitoring, SCADA, and alarm response."
        },
        "THA.SEC.SMP": {
                "code": "THA.SEC.SMP",
                "name": "Sampling & Laboratory Technique",
                "parent_trf": "TRF.SEC",
                "description": "Collecting, preparing, and processing samples using laboratory or field techniques including specimen handling and contamination control."
        },
        "THA.SEC.SRV": {
                "code": "THA.SEC.SRV",
                "name": "Surveying & Spatial Measurement",
                "parent_trf": "TRF.SEC",
                "description": "Measuring and mapping physical spaces using surveying equipment, GPS, GIS, levelling instruments, and spatial data processing."
        },
        "THA.SEC.EST": {
                "code": "THA.SEC.EST",
                "name": "Estimation & Costing",
                "parent_trf": "TRF.SEC",
                "description": "Estimating quantities, costs, timeframes, and resource requirements through material takeoff, bills of quantities, and tender preparation."
        },
        "THA.SEC.MKT": {
                "code": "THA.SEC.MKT",
                "name": "Marketing & Promotion",
                "parent_trf": "TRF.SEC",
                "description": "Promoting products, services, or ideas through market research, advertising, branding, digital marketing, and campaign management."
        },
        "THA.SEC.CPN": {
                "code": "THA.SEC.CPN",
                "name": "Counselling & Psychosocial Support",
                "parent_trf": "TRF.SEC",
                "description": "Providing emotional support, counselling, crisis intervention, and therapeutic communication to individuals in distress or need."
        },
        "THA.SEC.RHB": {
                "code": "THA.SEC.RHB",
                "name": "Rehabilitation & Recovery Support",
                "parent_trf": "TRF.SEC",
                "description": "Supporting individuals in physical, mental, or social recovery through structured programs, exercise therapy, and community reintegration."
        },
        "THA.SEC.MDA": {
                "code": "THA.SEC.MDA",
                "name": "Media Production & Content Creation",
                "parent_trf": "TRF.SEC",
                "description": "Creating, editing, and producing multimedia content including video, audio, photography, graphic design, and digital publishing."
        },
        "THA.SEC.PFM": {
                "code": "THA.SEC.PFM",
                "name": "Performance & Presentation Arts",
                "parent_trf": "TRF.SEC",
                "description": "Performing, directing, and producing live and recorded performances in music, dance, drama, and public events."
        },
        "THA.SEC.CLN": {
                "code": "THA.SEC.CLN",
                "name": "Cleaning & Decontamination",
                "parent_trf": "TRF.SEC",
                "description": "Applying systematic cleaning, sanitisation, sterilisation, and decontamination procedures for facilities, equipment, and environments."
        },
        "THA.SEC.WTR": {
                "code": "THA.SEC.WTR",
                "name": "Water & Waste Treatment",
                "parent_trf": "TRF.SEC",
                "description": "Operating and maintaining water treatment, wastewater processing, and solid waste management systems and infrastructure."
        },
        "THA.SEC.NET": {
                "code": "THA.SEC.NET",
                "name": "Network & Infrastructure Management",
                "parent_trf": "TRF.SEC",
                "description": "Configuring, managing, and maintaining ICT networks, servers, cloud infrastructure, and telecommunications systems."
        },
        "THA.SEC.CYB": {
                "code": "THA.SEC.CYB",
                "name": "Cybersecurity & Information Protection",
                "parent_trf": "TRF.SEC",
                "description": "Implementing security measures, threat detection, incident response, and data protection for information systems and networks."
        },
        "THA.SEC.TUT": {
                "code": "THA.SEC.TUT",
                "name": "Tutoring & Learner Support",
                "parent_trf": "TRF.SEC",
                "description": "Providing individualised learning support, academic assistance, and guided instruction to students with varying needs."
        },
        "THA.SEC.DSP": {
                "code": "THA.SEC.DSP",
                "name": "Dispensing & Dosage Preparation",
                "parent_trf": "TRF.SEC",
                "description": "Measuring, preparing, compounding, and dispensing medications, chemical formulations, or specialised mixtures accurately."
        },
        "THA.SEC.IMG": {
                "code": "THA.SEC.IMG",
                "name": "Imaging & Visualisation",
                "parent_trf": "TRF.SEC",
                "description": "Operating imaging equipment and interpreting visual outputs including radiography, ultrasound, photography, and microscopy."
        },
        "THA.SEC.ERG": {
                "code": "THA.SEC.ERG",
                "name": "Ergonomic & Workplace Assessment",
                "parent_trf": "TRF.SEC",
                "description": "Evaluating workplace design, posture, equipment setup, and environmental conditions to optimise human performance and safety."
        },
        "THA.SEC.PRS": {
                "code": "THA.SEC.PRS",
                "name": "Persuasion & Sales Technique",
                "parent_trf": "TRF.SEC",
                "description": "Applying persuasion, negotiation, and closing techniques to sell products, services, or ideas to customers and clients."
        },
        "THA.SEC.EVT": {
                "code": "THA.SEC.EVT",
                "name": "Event Planning & Coordination",
                "parent_trf": "TRF.SEC",
                "description": "Planning, organising, and managing events, functions, exhibitions, and conferences including logistics, vendors, and attendee management."
        },
        "THA.SEC.GIS": {
                "code": "THA.SEC.GIS",
                "name": "Geospatial Analysis & Mapping",
                "parent_trf": "TRF.SEC",
                "description": "Analysing spatial data using GIS software, remote sensing, terrain modelling, and geographic information systems."
        },
        "THA.SEC.BIM": {
                "code": "THA.SEC.BIM",
                "name": "Building Information Modelling",
                "parent_trf": "TRF.SEC",
                "description": "Creating and managing building information models for design coordination, clash detection, and construction planning."
        },
        "THA.SEC.AUT": {
                "code": "THA.SEC.AUT",
                "name": "Automation & Control Systems",
                "parent_trf": "TRF.SEC",
                "description": "Programming, configuring, and maintaining automated systems including PLCs, SCADA, robotics, and industrial control networks."
        },
        "THA.SEC.SIM": {
                "code": "THA.SEC.SIM",
                "name": "Simulation & Modelling",
                "parent_trf": "TRF.SEC",
                "description": "Creating and running simulations and computational models for training, analysis, prediction, or design validation."
        },
        "THA.SEC.FOR": {
                "code": "THA.SEC.FOR",
                "name": "Forensic Analysis & Investigation",
                "parent_trf": "TRF.SEC",
                "description": "Collecting, preserving, and analysing physical, digital, or documentary evidence using forensic methods and chain of custody protocols."
        },
        "THA.OCC.WLD": {
                "code": "THA.OCC.WLD",
                "name": "Arc & Gas Welding",
                "parent_trf": "TRF.OCC",
                "description": "Performing manual metal arc, MIG/MAG, TIG, oxy-fuel welding and cutting on ferrous and non-ferrous metals."
        },
        "THA.OCC.MTF": {
                "code": "THA.OCC.MTF",
                "name": "Metal Fabrication & Forming",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, shaping, and forming metal using guillotines, press brakes, rolls, plasma cutters, and hand tools."
        },
        "THA.OCC.BRZ": {
                "code": "THA.OCC.BRZ",
                "name": "Soldering, Brazing & Thermal Joining",
                "parent_trf": "TRF.OCC",
                "description": "Joining materials using soldering, brazing, silver brazing, and thermal bonding techniques for pipes, electronics, and components."
        },
        "THA.OCC.MAC": {
                "code": "THA.OCC.MAC",
                "name": "Machining & CNC Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating lathes, milling machines, grinders, and CNC machining centres to produce precision components."
        },
        "THA.OCC.TLM": {
                "code": "THA.OCC.TLM",
                "name": "Toolmaking & Jig Fabrication",
                "parent_trf": "TRF.OCC",
                "description": "Manufacturing precision tooling, jigs, fixtures, dies, and moulds for production and assembly processes."
        },
        "THA.OCC.SFC": {
                "code": "THA.OCC.SFC",
                "name": "Surface Finishing & Coating",
                "parent_trf": "TRF.OCC",
                "description": "Applying paint, powder coat, plating, polishing, anti-corrosion treatments, and decorative finishes to surfaces."
        },
        "THA.OCC.CST": {
                "code": "THA.OCC.CST",
                "name": "Casting & Moulding",
                "parent_trf": "TRF.OCC",
                "description": "Producing components through sand casting, die casting, injection moulding, and other forming processes."
        },
        "THA.OCC.ELW": {
                "code": "THA.OCC.ELW",
                "name": "Electrical Wiring & Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, terminating, and connecting electrical wiring, cables, conduits, and distribution systems in buildings and structures."
        },
        "THA.OCC.ELT": {
                "code": "THA.OCC.ELT",
                "name": "Electrical Testing & Verification",
                "parent_trf": "TRF.OCC",
                "description": "Testing, verifying, and commissioning electrical installations, circuits, and equipment for compliance and safety."
        },
        "THA.OCC.ELR": {
                "code": "THA.OCC.ELR",
                "name": "Electronic Repair & Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Diagnosing, repairing, and maintaining electronic equipment, circuit boards, sensors, and control devices."
        },
        "THA.OCC.PLC": {
                "code": "THA.OCC.PLC",
                "name": "PLC & Industrial Control Programming",
                "parent_trf": "TRF.OCC",
                "description": "Programming, configuring, and troubleshooting programmable logic controllers and industrial automation systems."
        },
        "THA.OCC.PWR": {
                "code": "THA.OCC.PWR",
                "name": "Power Generation & Distribution",
                "parent_trf": "TRF.OCC",
                "description": "Installing, operating, and maintaining power generation, transmission, and distribution systems and equipment."
        },
        "THA.OCC.TEL": {
                "code": "THA.OCC.TEL",
                "name": "Telecommunications & Cabling",
                "parent_trf": "TRF.OCC",
                "description": "Installing, terminating, and testing telecommunications cables, fibre optics, and communication infrastructure."
        },
        "THA.OCC.MER": {
                "code": "THA.OCC.MER",
                "name": "Mechanical Repair & Overhaul",
                "parent_trf": "TRF.OCC",
                "description": "Disassembling, inspecting, repairing, and reassembling mechanical components, engines, motors, and rotating equipment."
        },
        "THA.OCC.HYD": {
                "code": "THA.OCC.HYD",
                "name": "Hydraulic & Pneumatic Systems",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, diagnosing, and repairing hydraulic and pneumatic circuits, cylinders, valves, and pumps."
        },
        "THA.OCC.BRG": {
                "code": "THA.OCC.BRG",
                "name": "Bearing & Seal Replacement",
                "parent_trf": "TRF.OCC",
                "description": "Removing, fitting, and aligning bearings, seals, couplings, and mechanical drive components to specified tolerances."
        },
        "THA.OCC.PMT": {
                "code": "THA.OCC.PMT",
                "name": "Preventive & Predictive Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Performing scheduled maintenance, condition monitoring, vibration analysis, and oil analysis on plant and equipment."
        },
        "THA.OCC.PMP": {
                "code": "THA.OCC.PMP",
                "name": "Pump & Compressor Servicing",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, overhauling, and troubleshooting pumps, compressors, fans, and fluid handling equipment."
        },
        "THA.OCC.PPF": {
                "code": "THA.OCC.PPF",
                "name": "Pipe Fitting & Joining",
                "parent_trf": "TRF.OCC",
                "description": "Fabricating, fitting, and joining pipes using threading, welding, brazing, soldering, and mechanical coupling techniques."
        },
        "THA.OCC.DRN": {
                "code": "THA.OCC.DRN",
                "name": "Drainage & Sanitary Plumbing",
                "parent_trf": "TRF.OCC",
                "description": "Installing, testing, and maintaining drainage, sewerage, and sanitary plumbing systems including venting and grading."
        },
        "THA.OCC.GAS": {
                "code": "THA.OCC.GAS",
                "name": "Gas Fitting & Appliance Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, commissioning, testing, and servicing gas piping, meters, regulators, and gas-fired appliances."
        },
        "THA.OCC.RFG": {
                "code": "THA.OCC.RFG",
                "name": "Roofing & Waterproofing",
                "parent_trf": "TRF.OCC",
                "description": "Installing and repairing roof coverings, flashings, gutters, downpipes, and waterproofing membranes."
        },
        "THA.OCC.IRR": {
                "code": "THA.OCC.IRR",
                "name": "Irrigation & Water Reticulation",
                "parent_trf": "TRF.OCC",
                "description": "Designing, installing, and maintaining irrigation systems, water reticulation, sprinklers, and drip systems."
        },
        "THA.OCC.FRM": {
                "code": "THA.OCC.FRM",
                "name": "Structural Framing & Assembly",
                "parent_trf": "TRF.OCC",
                "description": "Constructing wall frames, floor frames, roof trusses, and structural assemblies in timber and steel."
        },
        "THA.OCC.MSN": {
                "code": "THA.OCC.MSN",
                "name": "Masonry & Blockwork",
                "parent_trf": "TRF.OCC",
                "description": "Laying bricks, blocks, and stone to line and level for walls, arches, piers, and decorative features."
        },
        "THA.OCC.CNC": {
                "code": "THA.OCC.CNC",
                "name": "Concrete Placement & Finishing",
                "parent_trf": "TRF.OCC",
                "description": "Placing, compacting, levelling, and finishing concrete for slabs, footings, paths, and structural elements."
        },
        "THA.OCC.FWK": {
                "code": "THA.OCC.FWK",
                "name": "Formwork Construction",
                "parent_trf": "TRF.OCC",
                "description": "Constructing, erecting, and stripping timber and steel formwork for concrete pours and structural elements."
        },
        "THA.OCC.SCF": {
                "code": "THA.OCC.SCF",
                "name": "Scaffolding & Temporary Structures",
                "parent_trf": "TRF.OCC",
                "description": "Erecting, altering, and dismantling scaffolding, temporary access structures, and edge protection systems."
        },
        "THA.OCC.CLD": {
                "code": "THA.OCC.CLD",
                "name": "Cladding & Glazing Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing external cladding, wall linings, window glazing, curtain walls, and facade systems."
        },
        "THA.OCC.TIL": {
                "code": "THA.OCC.TIL",
                "name": "Tiling & Floor Covering",
                "parent_trf": "TRF.OCC",
                "description": "Laying ceramic tiles, natural stone, vinyl, carpet, and timber flooring including substrate preparation."
        },
        "THA.OCC.PLT": {
                "code": "THA.OCC.PLT",
                "name": "Plastering & Rendering",
                "parent_trf": "TRF.OCC",
                "description": "Applying plaster, render, texture coats, and decorative finishes to internal and external surfaces."
        },
        "THA.OCC.CAB": {
                "code": "THA.OCC.CAB",
                "name": "Cabinetmaking & Joinery",
                "parent_trf": "TRF.OCC",
                "description": "Manufacturing and installing cabinets, built-in furniture, bench tops, doors, and architectural joinery."
        },
        "THA.OCC.STO": {
                "code": "THA.OCC.STO",
                "name": "Setting Out & Levelling",
                "parent_trf": "TRF.OCC",
                "description": "Establishing building lines, levels, setout points, and datum references using optical and laser instruments."
        },
        "THA.OCC.DML": {
                "code": "THA.OCC.DML",
                "name": "Demolition & Deconstruction",
                "parent_trf": "TRF.OCC",
                "description": "Safely demolishing structures, removing materials, managing asbestos, and salvaging reusable components."
        },
        "THA.OCC.RAC": {
                "code": "THA.OCC.RAC",
                "name": "Refrigeration & Air Conditioning",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, and repairing split systems, commercial refrigeration, chillers, and heat pump systems."
        },
        "THA.OCC.DCT": {
                "code": "THA.OCC.DCT",
                "name": "Ductwork & Ventilation",
                "parent_trf": "TRF.OCC",
                "description": "Fabricating, installing, and balancing ductwork, ventilation systems, exhaust systems, and air distribution networks."
        },
        "THA.OCC.RFH": {
                "code": "THA.OCC.RFH",
                "name": "Refrigerant Handling & Recovery",
                "parent_trf": "TRF.OCC",
                "description": "Recovering, recycling, and handling refrigerant gases safely in compliance with environmental regulations."
        },
        "THA.OCC.AEM": {
                "code": "THA.OCC.AEM",
                "name": "Automotive Engine & Drivetrain",
                "parent_trf": "TRF.OCC",
                "description": "Servicing, diagnosing, and repairing petrol and diesel engines, transmissions, differentials, and driveline components."
        },
        "THA.OCC.ABR": {
                "code": "THA.OCC.ABR",
                "name": "Automotive Braking & Suspension",
                "parent_trf": "TRF.OCC",
                "description": "Servicing and repairing vehicle braking systems, steering, suspension, wheel alignment, and tyre management."
        },
        "THA.OCC.AEL": {
                "code": "THA.OCC.AEL",
                "name": "Automotive Electrical & Electronics",
                "parent_trf": "TRF.OCC",
                "description": "Diagnosing and repairing vehicle electrical systems, engine management, sensors, wiring harnesses, and onboard electronics."
        },
        "THA.OCC.PNL": {
                "code": "THA.OCC.PNL",
                "name": "Panel Beating & Body Repair",
                "parent_trf": "TRF.OCC",
                "description": "Repairing vehicle body panels, performing structural alignment, rust repair, and preparing surfaces for refinishing."
        },
        "THA.OCC.VOP": {
                "code": "THA.OCC.VOP",
                "name": "Vehicle & Heavy Plant Operation",
                "parent_trf": "TRF.OCC",
                "description": "Safely operating light vehicles, heavy rigid vehicles, articulated vehicles, buses, and mobile plant on roads and worksites."
        },
        "THA.OCC.CRN": {
                "code": "THA.OCC.CRN",
                "name": "Crane Operation & Lifting",
                "parent_trf": "TRF.OCC",
                "description": "Operating mobile and tower cranes, performing crane lifts, managing load charts, and coordinating with doggers and riggers."
        },
        "THA.OCC.RIG": {
                "code": "THA.OCC.RIG",
                "name": "Rigging & Dogging",
                "parent_trf": "TRF.OCC",
                "description": "Selecting and applying slings, chains, shackles, and lifting gear; performing dogging; directing crane movements."
        },
        "THA.OCC.FLT": {
                "code": "THA.OCC.FLT",
                "name": "Forklift & Order Picker Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating counterbalance forklifts, reach trucks, order pickers, and pallet jacks in warehouse and worksite environments."
        },
        "THA.OCC.ETH": {
                "code": "THA.OCC.ETH",
                "name": "Earthmoving & Grading",
                "parent_trf": "TRF.OCC",
                "description": "Operating excavators, backhoes, bulldozers, graders, scrapers, and compaction equipment for earthworks and civil construction."
        },
        "THA.OCC.EWP": {
                "code": "THA.OCC.EWP",
                "name": "Elevated Work Platform Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating boom lifts, scissor lifts, and other elevated work platforms for working at heights safely."
        },
        "THA.OCC.DRL": {
                "code": "THA.OCC.DRL",
                "name": "Drilling & Boring Operations",
                "parent_trf": "TRF.OCC",
                "description": "Operating drilling rigs, boring equipment, and piling machines for resource extraction, construction, and exploration."
        },
        "THA.OCC.MED": {
                "code": "THA.OCC.MED",
                "name": "Medication Administration",
                "parent_trf": "TRF.OCC",
                "description": "Preparing, calculating dosages, and administering medications via oral, injection, intravenous, and topical routes."
        },
        "THA.OCC.WND": {
                "code": "THA.OCC.WND",
                "name": "Wound Care & Dressing",
                "parent_trf": "TRF.OCC",
                "description": "Assessing, cleaning, debriding, and dressing wounds including surgical wounds, ulcers, and burns."
        },
        "THA.OCC.IVT": {
                "code": "THA.OCC.IVT",
                "name": "Intravenous Therapy & Cannulation",
                "parent_trf": "TRF.OCC",
                "description": "Inserting cannulae, managing IV lines, administering IV fluids and medications, and monitoring infusion therapy."
        },
        "THA.OCC.RSP": {
                "code": "THA.OCC.RSP",
                "name": "Respiratory & Airway Management",
                "parent_trf": "TRF.OCC",
                "description": "Managing airways, administering oxygen therapy, operating ventilators, and performing suctioning procedures."
        },
        "THA.OCC.OBS": {
                "code": "THA.OCC.OBS",
                "name": "Clinical Observations & Vital Signs",
                "parent_trf": "TRF.OCC",
                "description": "Measuring and recording blood pressure, pulse, temperature, respiration, oxygen saturation, and neurological observations."
        },
        "THA.OCC.PHY": {
                "code": "THA.OCC.PHY",
                "name": "Physiotherapy & Exercise Therapy",
                "parent_trf": "TRF.OCC",
                "description": "Applying therapeutic exercise, manual therapy, electrotherapy, and movement rehabilitation techniques."
        },
        "THA.OCC.OTH": {
                "code": "THA.OCC.OTH",
                "name": "Occupational Therapy Interventions",
                "parent_trf": "TRF.OCC",
                "description": "Applying occupational therapy techniques for daily living skills, cognitive rehabilitation, and workplace modification."
        },
        "THA.OCC.DNT": {
                "code": "THA.OCC.DNT",
                "name": "Dental Procedures & Assistance",
                "parent_trf": "TRF.OCC",
                "description": "Assisting with or performing dental examinations, scaling, polishing, radiography, and chairside procedures."
        },
        "THA.OCC.SRG": {
                "code": "THA.OCC.SRG",
                "name": "Surgical Assistance & Procedures",
                "parent_trf": "TRF.OCC",
                "description": "Preparing surgical environments, assisting during operations, managing instruments, and supporting perioperative care."
        },
        "THA.OCC.CPR": {
                "code": "THA.OCC.CPR",
                "name": "Resuscitation & Emergency Life Support",
                "parent_trf": "TRF.OCC",
                "description": "Performing CPR, using defibrillators, providing basic and advanced life support in emergency situations."
        },
        "THA.OCC.PAL": {
                "code": "THA.OCC.PAL",
                "name": "Palliative & End-of-Life Care",
                "parent_trf": "TRF.OCC",
                "description": "Providing comfort care, symptom management, emotional support, and dignity for individuals at end of life."
        },
        "THA.OCC.MHC": {
                "code": "THA.OCC.MHC",
                "name": "Mental Health Support & Intervention",
                "parent_trf": "TRF.OCC",
                "description": "Providing mental health first aid, de-escalation, crisis support, and recovery-oriented interventions."
        },
        "THA.OCC.ADL": {
                "code": "THA.OCC.ADL",
                "name": "Activities of Daily Living Support",
                "parent_trf": "TRF.OCC",
                "description": "Assisting individuals with personal hygiene, mobility, eating, dressing, and daily routine tasks."
        },
        "THA.OCC.MAN": {
                "code": "THA.OCC.MAN",
                "name": "Manual Handling & Patient Transfer",
                "parent_trf": "TRF.OCC",
                "description": "Safely lifting, transferring, and repositioning patients and clients using hoists, slide sheets, and ergonomic techniques."
        },
        "THA.OCC.CTH": {
                "code": "THA.OCC.CTH",
                "name": "Catheter & Continence Management",
                "parent_trf": "TRF.OCC",
                "description": "Managing urinary catheters, continence aids, stoma care, and related elimination support procedures."
        },
        "THA.OCC.FAD": {
                "code": "THA.OCC.FAD",
                "name": "First Aid & Pre-Hospital Care",
                "parent_trf": "TRF.OCC",
                "description": "Providing first aid, managing trauma, controlling bleeding, treating shock, and stabilising patients before hospital care."
        },
        "THA.OCC.FFS": {
                "code": "THA.OCC.FFS",
                "name": "Firefighting & Suppression",
                "parent_trf": "TRF.OCC",
                "description": "Operating firefighting equipment, applying suppression techniques, conducting search and rescue in fire environments."
        },
        "THA.OCC.HAZ": {
                "code": "THA.OCC.HAZ",
                "name": "Hazardous Materials Response",
                "parent_trf": "TRF.OCC",
                "description": "Responding to chemical, biological, and radiological incidents including containment, decontamination, and safe handling."
        },
        "THA.OCC.RES": {
                "code": "THA.OCC.RES",
                "name": "Rescue & Confined Space Operations",
                "parent_trf": "TRF.OCC",
                "description": "Performing technical rescue operations in confined spaces, at heights, in water, and in collapsed structures."
        },
        "THA.OCC.CHM": {
                "code": "THA.OCC.CHM",
                "name": "Chemical Handling & Application",
                "parent_trf": "TRF.OCC",
                "description": "Handling, storing, mixing, and applying chemicals safely including interpreting SDS, managing spills, and applying pesticides."
        },
        "THA.OCC.BIO": {
                "code": "THA.OCC.BIO",
                "name": "Biological Specimen Processing",
                "parent_trf": "TRF.OCC",
                "description": "Collecting, processing, and managing biological specimens including tissue processing, cryogenics, and biosafety protocols."
        },
        "THA.OCC.STR": {
                "code": "THA.OCC.STR",
                "name": "Sterilisation & Decontamination",
                "parent_trf": "TRF.OCC",
                "description": "Sterilising instruments and equipment using autoclaves, chemical disinfection, and validated decontamination processes."
        },
        "THA.OCC.CKG": {
                "code": "THA.OCC.CKG",
                "name": "Cooking & Culinary Technique",
                "parent_trf": "TRF.OCC",
                "description": "Preparing, cooking, and presenting food using various methods including grilling, baking, saut\u00e9ing, and sous vide."
        },
        "THA.OCC.PTY": {
                "code": "THA.OCC.PTY",
                "name": "Patisserie & Baking",
                "parent_trf": "TRF.OCC",
                "description": "Producing cakes, pastries, breads, and desserts using baking, laminating, tempering, and decorating techniques."
        },
        "THA.OCC.FHS": {
                "code": "THA.OCC.FHS",
                "name": "Food Safety & Hygiene Management",
                "parent_trf": "TRF.OCC",
                "description": "Implementing food safety systems, HACCP, temperature monitoring, allergen management, and food handling compliance."
        },
        "THA.OCC.BAR": {
                "code": "THA.OCC.BAR",
                "name": "Beverage Service & Mixology",
                "parent_trf": "TRF.OCC",
                "description": "Preparing and serving alcoholic and non-alcoholic beverages, operating bar equipment, and managing cellar operations."
        },
        "THA.OCC.FBS": {
                "code": "THA.OCC.FBS",
                "name": "Food & Table Service",
                "parent_trf": "TRF.OCC",
                "description": "Providing table service, managing dining rooms, serving meals, and delivering front-of-house hospitality service."
        },
        "THA.OCC.ACC": {
                "code": "THA.OCC.ACC",
                "name": "Accommodation & Front Office",
                "parent_trf": "TRF.OCC",
                "description": "Managing front desk, reservations, room allocation, housekeeping coordination, and guest services operations."
        },
        "THA.OCC.CRP": {
                "code": "THA.OCC.CRP",
                "name": "Crop Production & Harvesting",
                "parent_trf": "TRF.OCC",
                "description": "Planting, cultivating, irrigating, fertilising, and harvesting crops and pastures using manual and mechanised methods."
        },
        "THA.OCC.SOL": {
                "code": "THA.OCC.SOL",
                "name": "Soil & Land Management",
                "parent_trf": "TRF.OCC",
                "description": "Assessing soil health, applying amendments, managing erosion, implementing conservation practices, and land rehabilitation."
        },
        "THA.OCC.PST": {
                "code": "THA.OCC.PST",
                "name": "Pest, Weed & Disease Control",
                "parent_trf": "TRF.OCC",
                "description": "Identifying and managing pests, weeds, and plant/animal diseases using chemical, biological, and integrated methods."
        },
        "THA.OCC.LDM": {
                "code": "THA.OCC.LDM",
                "name": "Landscape & Turf Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Establishing and maintaining gardens, lawns, turf, trees, and landscape features including pruning and propagation."
        },
        "THA.OCC.ANH": {
                "code": "THA.OCC.ANH",
                "name": "Animal Handling & Husbandry",
                "parent_trf": "TRF.OCC",
                "description": "Handling, restraining, feeding, breeding, and providing daily care for livestock, companion, and native animals."
        },
        "THA.OCC.AVT": {
                "code": "THA.OCC.AVT",
                "name": "Animal Health & Veterinary Support",
                "parent_trf": "TRF.OCC",
                "description": "Administering animal health treatments, assisting with veterinary procedures, managing medications, and monitoring animal conditions."
        },
        "THA.OCC.AQU": {
                "code": "THA.OCC.AQU",
                "name": "Aquaculture & Fisheries",
                "parent_trf": "TRF.OCC",
                "description": "Managing aquatic species production, fish farming, hatchery operations, water quality management, and marine harvesting."
        },
        "THA.OCC.UGM": {
                "code": "THA.OCC.UGM",
                "name": "Underground Mining Operations",
                "parent_trf": "TRF.OCC",
                "description": "Operating underground mining equipment, managing ground support, ventilation, and conducting underground development."
        },
        "THA.OCC.OCM": {
                "code": "THA.OCC.OCM",
                "name": "Open Cut & Surface Mining",
                "parent_trf": "TRF.OCC",
                "description": "Operating open cut mining equipment, managing bench operations, overburden removal, and pit development."
        },
        "THA.OCC.BLS": {
                "code": "THA.OCC.BLS",
                "name": "Blasting & Explosives Handling",
                "parent_trf": "TRF.OCC",
                "description": "Preparing, loading, and firing explosive charges for mining, quarrying, and construction blasting operations."
        },
        "THA.OCC.OPR": {
                "code": "THA.OCC.OPR",
                "name": "Ore Processing & Mineral Separation",
                "parent_trf": "TRF.OCC",
                "description": "Operating crushing, grinding, flotation, gravity separation, and other mineral processing equipment and circuits."
        },
        "THA.OCC.NAV": {
                "code": "THA.OCC.NAV",
                "name": "Navigation & Vessel Handling",
                "parent_trf": "TRF.OCC",
                "description": "Navigating marine vessels, performing seamanship duties, operating radar, managing vessel stability, and berthing operations."
        },
        "THA.OCC.MCG": {
                "code": "THA.OCC.MCG",
                "name": "Marine Cargo & Deck Operations",
                "parent_trf": "TRF.OCC",
                "description": "Managing cargo loading and discharge, deck equipment operation, mooring, anchoring, and marine maintenance."
        },
        "THA.OCC.ACM": {
                "code": "THA.OCC.ACM",
                "name": "Aircraft Maintenance & Inspection",
                "parent_trf": "TRF.OCC",
                "description": "Performing scheduled and unscheduled aircraft maintenance, structural repairs, and airworthiness inspections."
        },
        "THA.OCC.AVI": {
                "code": "THA.OCC.AVI",
                "name": "Avionics & Aircraft Electronics",
                "parent_trf": "TRF.OCC",
                "description": "Installing, testing, and maintaining avionics systems, flight instruments, navigation electronics, and aircraft communication systems."
        },
        "THA.OCC.SEW": {
                "code": "THA.OCC.SEW",
                "name": "Sewing & Garment Construction",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, sewing, and assembling garments from patterns using industrial and domestic sewing machines."
        },
        "THA.OCC.PAT": {
                "code": "THA.OCC.PAT",
                "name": "Pattern Making & Textile Design",
                "parent_trf": "TRF.OCC",
                "description": "Drafting, modifying, and grading garment patterns; designing textile prints; and developing fashion prototypes."
        },
        "THA.OCC.UPH": {
                "code": "THA.OCC.UPH",
                "name": "Upholstery & Soft Furnishing",
                "parent_trf": "TRF.OCC",
                "description": "Producing and repairing upholstered furniture, curtains, blinds, and soft furnishings using fabrics and padding materials."
        },
        "THA.OCC.HAR": {
                "code": "THA.OCC.HAR",
                "name": "Hairdressing & Colour Technique",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, styling, colouring, perming, and chemically treating hair using professional techniques and products."
        },
        "THA.OCC.BTY": {
                "code": "THA.OCC.BTY",
                "name": "Beauty Therapy & Skin Treatment",
                "parent_trf": "TRF.OCC",
                "description": "Performing facial treatments, skin analysis, waxing, makeup application, eyelash and brow treatments."
        },
        "THA.OCC.MSG": {
                "code": "THA.OCC.MSG",
                "name": "Massage & Body Therapy",
                "parent_trf": "TRF.OCC",
                "description": "Performing remedial, relaxation, sports, and therapeutic massage techniques for pain relief and wellbeing."
        },
        "THA.OCC.NLT": {
                "code": "THA.OCC.NLT",
                "name": "Nail Technology & Enhancement",
                "parent_trf": "TRF.OCC",
                "description": "Applying, maintaining, and removing nail enhancements including acrylics, gels, and nail art techniques."
        },
        "THA.OCC.FIT": {
                "code": "THA.OCC.FIT",
                "name": "Fitness Instruction & Programming",
                "parent_trf": "TRF.OCC",
                "description": "Planning and delivering exercise programs, group fitness sessions, gym floor instruction, and fitness assessments."
        },
        "THA.OCC.COA": {
                "code": "THA.OCC.COA",
                "name": "Sports Coaching & Development",
                "parent_trf": "TRF.OCC",
                "description": "Coaching sport-specific skills, developing athlete training programs, and coordinating competitive sport activities."
        },
        "THA.OCC.AQP": {
                "code": "THA.OCC.AQP",
                "name": "Aquatic & Pool Operations",
                "parent_trf": "TRF.OCC",
                "description": "Managing swimming pool operations, water quality, lifeguarding, and aquatic program delivery."
        },
        "THA.OCC.COD": {
                "code": "THA.OCC.COD",
                "name": "Software Development & Programming",
                "parent_trf": "TRF.OCC",
                "description": "Writing, testing, debugging, and maintaining program code in various languages and development frameworks."
        },
        "THA.OCC.DBA": {
                "code": "THA.OCC.DBA",
                "name": "Database Administration & Management",
                "parent_trf": "TRF.OCC",
                "description": "Designing, administering, optimising, and securing databases and data storage systems."
        },
        "THA.OCC.WEB": {
                "code": "THA.OCC.WEB",
                "name": "Web Development & Design",
                "parent_trf": "TRF.OCC",
                "description": "Creating, developing, and maintaining websites, web applications, and user interfaces using web technologies."
        },
        "THA.OCC.GRD": {
                "code": "THA.OCC.GRD",
                "name": "Security Guarding & Patrol",
                "parent_trf": "TRF.OCC",
                "description": "Conducting security patrols, access control, crowd management, incident response, and security screening operations."
        },
        "THA.OCC.EVC": {
                "code": "THA.OCC.EVC",
                "name": "Emergency Evacuation Coordination",
                "parent_trf": "TRF.OCC",
                "description": "Planning, coordinating, and conducting emergency evacuations, drills, and warden duties for buildings and events."
        },
        "THA.OCC.EQH": {
                "code": "THA.OCC.EQH",
                "name": "Equipment Hygiene & Sterilisation",
                "parent_trf": "TRF.OCC",
                "description": "Cleaning, disinfecting, and sterilising specialised equipment including medical instruments, firearms, and food processing equipment."
        },
        "THA.OCC.EQS": {
                "code": "THA.OCC.EQS",
                "name": "Equipment Servicing & Functional Testing",
                "parent_trf": "TRF.OCC",
                "description": "Performing preventive maintenance, functional testing, and servicing of specialised tools, instruments, and apparatus."
        },
        "THA.OCC.VIA": {
                "code": "THA.OCC.VIA",
                "name": "Visual Arts & Illustration",
                "parent_trf": "TRF.OCC",
                "description": "Creating visual artworks, illustrations, paintings, sculptures, and artistic pieces using various media and techniques."
        },
        "THA.OCC.GFX": {
                "code": "THA.OCC.GFX",
                "name": "Graphic Design & Layout",
                "parent_trf": "TRF.OCC",
                "description": "Designing visual communications including logos, marketing materials, publications, and digital graphics using design software."
        },
        "THA.OCC.PHO": {
                "code": "THA.OCC.PHO",
                "name": "Photography & Videography",
                "parent_trf": "TRF.OCC",
                "description": "Capturing, editing, and producing photographic and video content for commercial, editorial, and artistic purposes."
        },
        "THA.OCC.SND": {
                "code": "THA.OCC.SND",
                "name": "Sound & Audio Production",
                "parent_trf": "TRF.OCC",
                "description": "Recording, mixing, editing, and producing audio content including music, voiceover, podcasts, and live sound reinforcement."
        },
        "THA.OCC.CHD": {
                "code": "THA.OCC.CHD",
                "name": "Child Development & Early Education",
                "parent_trf": "TRF.OCC",
                "description": "Supporting childrens learning, development, and wellbeing through play-based programs, observation, and age-appropriate activities."
        },
        "THA.OCC.YTH": {
                "code": "THA.OCC.YTH",
                "name": "Youth Work & Community Engagement",
                "parent_trf": "TRF.OCC",
                "description": "Engaging with young people and communities through outreach, group programs, advocacy, and support services."
        }
},
}

# Helper: map TRF code -> list of THA codes
TRF_TO_THA = {}
for code, val in TRANSFERABLE_HUMAN_ABILITY_FACET["values"].items():
    parent = val["parent_trf"]
    TRF_TO_THA.setdefault(parent, []).append(code)

_TRF_COVERAGE = {trf: len(codes) for trf, codes in TRF_TO_THA.items()}
TOTAL_THA_VALUES = sum(_TRF_COVERAGE.values())