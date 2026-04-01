"""
Transferable Human Ability (THA) Facet Definition

260 functional human abilities organized under TRF categories.
Each describes WHAT a human can do, not WHERE they do it.
Each THA passes the transferability test: a person who masters
one skill in a THA group can perform other skills in that group.
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
        "THA.BRD.SPV": {
                "code": "THA.BRD.SPV",
                "name": "Supervision & Work Coordination",
                "parent_trf": "TRF.BRD",
                "description": "Directing daily work activities, allocating tasks, monitoring progress, and ensuring team output meets requirements."
        },
        "THA.BRD.PFM": {
                "code": "THA.BRD.PFM",
                "name": "Performance Management & Coaching",
                "parent_trf": "TRF.BRD",
                "description": "Evaluating individual performance, providing feedback, setting development goals, mentoring, and building capability."
        },
        "THA.BRD.SLD": {
                "code": "THA.BRD.SLD",
                "name": "Strategic Leadership & Direction",
                "parent_trf": "TRF.BRD",
                "description": "Setting vision, aligning organisational strategy, making high-level decisions, and driving long-term objectives."
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
        "THA.BRD.TRD": {
                "code": "THA.BRD.TRD",
                "name": "Training Design & Delivery",
                "parent_trf": "TRF.BRD",
                "description": "Designing training programs, preparing materials, delivering structured instruction, and assessing learner competence."
        },
        "THA.BRD.MNT": {
                "code": "THA.BRD.MNT",
                "name": "Mentoring & Knowledge Transfer",
                "parent_trf": "TRF.BRD",
                "description": "Guiding less experienced individuals, sharing tacit knowledge, demonstrating techniques, and supporting skill development on the job."
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
        "THA.BRD.CSR": {
                "code": "THA.BRD.CSR",
                "name": "Customer Service & Support",
                "parent_trf": "TRF.BRD",
                "description": "Responding to customer needs, handling enquiries, resolving complaints, and delivering consistent service quality."
        },
        "THA.BRD.STK": {
                "code": "THA.BRD.STK",
                "name": "Stakeholder & Relationship Management",
                "parent_trf": "TRF.BRD",
                "description": "Building and maintaining professional relationships with external partners, clients, and stakeholders through consultation and engagement."
        },
        "THA.BRD.RPT": {
                "code": "THA.BRD.RPT",
                "name": "Technical Reporting & Documentation",
                "parent_trf": "TRF.BRD",
                "description": "Preparing accurate technical reports, specifications, procedures, work instructions, incident reports, and compliance records."
        },
        "THA.BRD.BDG": {
                "code": "THA.BRD.BDG",
                "name": "Budgeting & Cost Control",
                "parent_trf": "TRF.BRD",
                "description": "Preparing budgets, monitoring expenditure, forecasting costs, and managing financial resources within defined parameters."
        },
        "THA.BRD.BKP": {
                "code": "THA.BRD.BKP",
                "name": "Bookkeeping & Financial Processing",
                "parent_trf": "TRF.BRD",
                "description": "Recording financial transactions, processing invoices, managing accounts payable and receivable, and reconciling ledgers."
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
        "THA.BRD.INF": {
                "code": "THA.BRD.INF",
                "name": "Information Management & Research",
                "parent_trf": "TRF.BRD",
                "description": "Sourcing, organising, evaluating, and managing information through research methods, records management, and knowledge systems."
        },
        "THA.BRD.RCM": {
                "code": "THA.BRD.RCM",
                "name": "Recruitment & Workforce Planning",
                "parent_trf": "TRF.BRD",
                "description": "Identifying workforce needs, recruiting and selecting candidates, conducting interviews, and managing onboarding processes."
        },
        "THA.SEC.DGN": {
                "code": "THA.SEC.DGN",
                "name": "Technical Drawing & Drafting",
                "parent_trf": "TRF.SEC",
                "description": "Creating technical drawings, plans, and specifications using manual and computer-aided drafting tools."
        },
        "THA.SEC.3DM": {
                "code": "THA.SEC.3DM",
                "name": "3D Modelling & Visualisation",
                "parent_trf": "TRF.SEC",
                "description": "Creating three-dimensional digital models, renders, and visualisations for design, planning, or presentation."
        },
        "THA.SEC.INS": {
                "code": "THA.SEC.INS",
                "name": "Visual & Dimensional Inspection",
                "parent_trf": "TRF.SEC",
                "description": "Examining products, components, or structures visually and dimensionally to verify conformance to specifications."
        },
        "THA.SEC.NDT": {
                "code": "THA.SEC.NDT",
                "name": "Non-Destructive Testing",
                "parent_trf": "TRF.SEC",
                "description": "Testing materials and components for defects without damage using ultrasonic, radiographic, magnetic particle, or dye penetrant methods."
        },
        "THA.SEC.CAL": {
                "code": "THA.SEC.CAL",
                "name": "Instrument Calibration & Metrology",
                "parent_trf": "TRF.SEC",
                "description": "Calibrating measuring instruments, verifying accuracy, applying measurement uncertainty, and maintaining calibration records."
        },
        "THA.SEC.DIA": {
                "code": "THA.SEC.DIA",
                "name": "Systematic Fault Diagnosis",
                "parent_trf": "TRF.SEC",
                "description": "Isolating faults through structured elimination, symptom analysis, schematic interpretation, and diagnostic instrument use."
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
        "THA.SEC.PRM": {
                "code": "THA.SEC.PRM",
                "name": "Process Monitoring & Control",
                "parent_trf": "TRF.SEC",
                "description": "Continuously monitoring process parameters, adjusting controls, responding to alarms, and maintaining stable operating conditions."
        },
        "THA.SEC.VTL": {
                "code": "THA.SEC.VTL",
                "name": "Vital Signs & Clinical Monitoring",
                "parent_trf": "TRF.SEC",
                "description": "Measuring, recording, and interpreting patient vital signs and physiological parameters using clinical monitoring equipment."
        },
        "THA.SEC.SMP": {
                "code": "THA.SEC.SMP",
                "name": "Sample Collection & Laboratory Technique",
                "parent_trf": "TRF.SEC",
                "description": "Collecting, preparing, and processing samples using aseptic technique, contamination control, and laboratory protocols."
        },
        "THA.SEC.SRV": {
                "code": "THA.SEC.SRV",
                "name": "Site Measurement & Setting Out",
                "parent_trf": "TRF.SEC",
                "description": "Establishing reference points, taking measurements, and setting out work using optical, laser, and GPS instruments."
        },
        "THA.SEC.EST": {
                "code": "THA.SEC.EST",
                "name": "Quantity Estimation & Takeoff",
                "parent_trf": "TRF.SEC",
                "description": "Calculating material quantities, labour requirements, and costs from plans, drawings, and specifications."
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
                "name": "Digital Media Editing & Production",
                "parent_trf": "TRF.SEC",
                "description": "Editing and producing digital media content including video, audio, and graphics using post-production software."
        },
        "THA.SEC.CLN": {
                "code": "THA.SEC.CLN",
                "name": "Cleaning & Sanitisation",
                "parent_trf": "TRF.SEC",
                "description": "Applying systematic cleaning, sanitisation, and hygiene procedures for facilities, surfaces, and equipment."
        },
        "THA.SEC.STE": {
                "code": "THA.SEC.STE",
                "name": "Sterilisation & Decontamination",
                "parent_trf": "TRF.SEC",
                "description": "Sterilising instruments and equipment using autoclaves, chemical disinfection, and validated decontamination processes."
        },
        "THA.SEC.WTR": {
                "code": "THA.SEC.WTR",
                "name": "Water & Waste Treatment",
                "parent_trf": "TRF.SEC",
                "description": "Operating and maintaining water treatment, wastewater processing, and solid waste management systems."
        },
        "THA.SEC.NET": {
                "code": "THA.SEC.NET",
                "name": "Network & Systems Administration",
                "parent_trf": "TRF.SEC",
                "description": "Configuring, managing, and maintaining ICT networks, servers, cloud infrastructure, and telecommunications systems."
        },
        "THA.SEC.CYB": {
                "code": "THA.SEC.CYB",
                "name": "Cybersecurity & Information Protection",
                "parent_trf": "TRF.SEC",
                "description": "Implementing security measures, threat detection, incident response, and data protection for information systems."
        },
        "THA.SEC.DSP": {
                "code": "THA.SEC.DSP",
                "name": "Dispensing & Formulation",
                "parent_trf": "TRF.SEC",
                "description": "Measuring, preparing, compounding, and dispensing medications, chemical formulations, or specialised mixtures accurately."
        },
        "THA.SEC.IMG": {
                "code": "THA.SEC.IMG",
                "name": "Imaging & Diagnostic Visualisation",
                "parent_trf": "TRF.SEC",
                "description": "Operating imaging equipment and interpreting visual outputs including radiography, ultrasound, photography, and microscopy."
        },
        "THA.SEC.PRS": {
                "code": "THA.SEC.PRS",
                "name": "Sales & Persuasion Technique",
                "parent_trf": "TRF.SEC",
                "description": "Applying persuasion, rapport-building, and closing techniques to sell products, services, or ideas to customers."
        },
        "THA.SEC.EVT": {
                "code": "THA.SEC.EVT",
                "name": "Event & Function Coordination",
                "parent_trf": "TRF.SEC",
                "description": "Planning, organising, and managing events, functions, exhibitions, and conferences including logistics and attendee management."
        },
        "THA.SEC.AUT": {
                "code": "THA.SEC.AUT",
                "name": "Automation & Control Programming",
                "parent_trf": "TRF.SEC",
                "description": "Programming, configuring, and troubleshooting automated systems including PLCs, SCADA, robotics, and industrial control networks."
        },
        "THA.SEC.FOR": {
                "code": "THA.SEC.FOR",
                "name": "Forensic & Evidence Analysis",
                "parent_trf": "TRF.SEC",
                "description": "Collecting, preserving, and analysing physical, digital, or documentary evidence using forensic methods and chain of custody."
        },
        "THA.SEC.LGL": {
                "code": "THA.SEC.LGL",
                "name": "Legal Research & Advocacy",
                "parent_trf": "TRF.SEC",
                "description": "Researching legislation, preparing legal documents, presenting arguments, and advising on rights and obligations."
        },
        "THA.SEC.CHL": {
                "code": "THA.SEC.CHL",
                "name": "Cultural Heritage & Land Management",
                "parent_trf": "TRF.SEC",
                "description": "Documenting, preserving, and managing cultural heritage sites, indigenous landscapes, and sacred materials with appropriate protocols."
        },
        "THA.SEC.DSC": {
                "code": "THA.SEC.DSC",
                "name": "Disability Support Coordination",
                "parent_trf": "TRF.SEC",
                "description": "Coordinating support services, developing individual plans, and facilitating community participation for people with disabilities."
        },
        "THA.SEC.INT": {
                "code": "THA.SEC.INT",
                "name": "Interpreting & Translation",
                "parent_trf": "TRF.SEC",
                "description": "Converting spoken or written content between languages or communication modes including sign language and assistive communication."
        },
        "THA.SEC.PRV": {
                "code": "THA.SEC.PRV",
                "name": "Property Valuation & Assessment",
                "parent_trf": "TRF.SEC",
                "description": "Assessing market value, condition, and characteristics of property and assets using valuation methodologies and market analysis."
        },
        "THA.SEC.INR": {
                "code": "THA.SEC.INR",
                "name": "Insurance Assessment & Claims",
                "parent_trf": "TRF.SEC",
                "description": "Assessing insurance claims, evaluating damage or loss, determining liability, and processing settlement documentation."
        },
        "THA.SEC.COR": {
                "code": "THA.SEC.COR",
                "name": "Correctional & Custodial Operations",
                "parent_trf": "TRF.SEC",
                "description": "Managing detainees, maintaining security in custodial environments, conducting searches, and supporting rehabilitation programs."
        },
        "THA.OCC.MMA": {
                "code": "THA.OCC.MMA",
                "name": "Manual Metal Arc Welding",
                "parent_trf": "TRF.OCC",
                "description": "Joining metals using shielded manual metal arc (stick) welding processes on various joint configurations and positions."
        },
        "THA.OCC.MIG": {
                "code": "THA.OCC.MIG",
                "name": "MIG & MAG Welding",
                "parent_trf": "TRF.OCC",
                "description": "Joining metals using gas metal arc welding (MIG/MAG) processes with solid and flux-cored wires."
        },
        "THA.OCC.TIG": {
                "code": "THA.OCC.TIG",
                "name": "TIG Welding",
                "parent_trf": "TRF.OCC",
                "description": "Joining metals using gas tungsten arc welding (TIG/GTAW) processes for precision and thin-gauge applications."
        },
        "THA.OCC.OXY": {
                "code": "THA.OCC.OXY",
                "name": "Oxy-Fuel Cutting & Heating",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, heating, and gouging metals using oxy-acetylene and oxy-fuel gas equipment."
        },
        "THA.OCC.PLZ": {
                "code": "THA.OCC.PLZ",
                "name": "Plasma & Laser Cutting",
                "parent_trf": "TRF.OCC",
                "description": "Cutting metals and materials using plasma arc, laser, and waterjet cutting equipment."
        },
        "THA.OCC.SHM": {
                "code": "THA.OCC.SHM",
                "name": "Sheet Metal Forming",
                "parent_trf": "TRF.OCC",
                "description": "Forming sheet metal using guillotines, press brakes, rolls, folders, and hand forming techniques."
        },
        "THA.OCC.STF": {
                "code": "THA.OCC.STF",
                "name": "Structural Steel Fabrication",
                "parent_trf": "TRF.OCC",
                "description": "Marking out, cutting, drilling, and assembling structural steel sections and plate for frameworks and structures."
        },
        "THA.OCC.BRZ": {
                "code": "THA.OCC.BRZ",
                "name": "Soldering & Brazing",
                "parent_trf": "TRF.OCC",
                "description": "Joining metals, pipes, and components using soft soldering, silver brazing, and capillary brazing techniques."
        },
        "THA.OCC.FRG": {
                "code": "THA.OCC.FRG",
                "name": "Forging & Hot Working",
                "parent_trf": "TRF.OCC",
                "description": "Shaping metals through heating, hammering, pressing, and hot forming processes including blacksmithing."
        },
        "THA.OCC.LTH": {
                "code": "THA.OCC.LTH",
                "name": "Lathe Turning",
                "parent_trf": "TRF.OCC",
                "description": "Producing cylindrical components using manual and CNC lathes including facing, boring, threading, and taper turning."
        },
        "THA.OCC.MLG": {
                "code": "THA.OCC.MLG",
                "name": "Milling & Drilling",
                "parent_trf": "TRF.OCC",
                "description": "Producing flat, angled, and contoured surfaces using manual and CNC milling machines and precision drilling equipment."
        },
        "THA.OCC.GRN": {
                "code": "THA.OCC.GRN",
                "name": "Precision Grinding",
                "parent_trf": "TRF.OCC",
                "description": "Finishing components to tight tolerances using surface, cylindrical, centreless, and tool and cutter grinders."
        },
        "THA.OCC.CNC": {
                "code": "THA.OCC.CNC",
                "name": "CNC Programming & Operation",
                "parent_trf": "TRF.OCC",
                "description": "Programming, setting up, and operating CNC machining centres using G-code, CAM software, and tool management."
        },
        "THA.OCC.TLM": {
                "code": "THA.OCC.TLM",
                "name": "Toolmaking & Die Fitting",
                "parent_trf": "TRF.OCC",
                "description": "Manufacturing precision tools, dies, jigs, fixtures, and moulds using a combination of machining and fitting skills."
        },
        "THA.OCC.EDM": {
                "code": "THA.OCC.EDM",
                "name": "EDM & Advanced Machining",
                "parent_trf": "TRF.OCC",
                "description": "Producing components using electrical discharge machining, wire EDM, and non-traditional material removal processes."
        },
        "THA.OCC.SPP": {
                "code": "THA.OCC.SPP",
                "name": "Spray Painting & Colour Matching",
                "parent_trf": "TRF.OCC",
                "description": "Applying paint and coatings using spray equipment, matching colours, and achieving specified finish quality."
        },
        "THA.OCC.PWC": {
                "code": "THA.OCC.PWC",
                "name": "Powder Coating & Electroplating",
                "parent_trf": "TRF.OCC",
                "description": "Applying protective and decorative finishes through powder coating, electroplating, anodising, and galvanising processes."
        },
        "THA.OCC.SBL": {
                "code": "THA.OCC.SBL",
                "name": "Abrasive Blasting & Surface Preparation",
                "parent_trf": "TRF.OCC",
                "description": "Preparing surfaces using abrasive blasting, chemical cleaning, and mechanical preparation for coating application."
        },
        "THA.OCC.CST": {
                "code": "THA.OCC.CST",
                "name": "Casting & Moulding",
                "parent_trf": "TRF.OCC",
                "description": "Producing components through sand casting, die casting, injection moulding, and resin infusion processes."
        },
        "THA.OCC.3DP": {
                "code": "THA.OCC.3DP",
                "name": "Additive Manufacturing & 3D Printing",
                "parent_trf": "TRF.OCC",
                "description": "Producing components using additive manufacturing processes including FDM, SLA, SLS, and metal sintering."
        },
        "THA.OCC.DWR": {
                "code": "THA.OCC.DWR",
                "name": "Domestic Electrical Wiring",
                "parent_trf": "TRF.OCC",
                "description": "Installing, terminating, and connecting electrical wiring, switches, outlets, and distribution boards in residential buildings."
        },
        "THA.OCC.IWR": {
                "code": "THA.OCC.IWR",
                "name": "Industrial Electrical Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing electrical systems in commercial and industrial environments including switchboards, motor circuits, and power distribution."
        },
        "THA.OCC.ELT": {
                "code": "THA.OCC.ELT",
                "name": "Electrical Testing & Commissioning",
                "parent_trf": "TRF.OCC",
                "description": "Testing, verifying, and commissioning electrical installations for compliance with AS/NZS standards and safety requirements."
        },
        "THA.OCC.LTG": {
                "code": "THA.OCC.LTG",
                "name": "Lighting Installation & Design",
                "parent_trf": "TRF.OCC",
                "description": "Installing, configuring, and commissioning lighting systems including LED, emergency, and architectural lighting."
        },
        "THA.OCC.PCB": {
                "code": "THA.OCC.PCB",
                "name": "Circuit Board Assembly & Repair",
                "parent_trf": "TRF.OCC",
                "description": "Assembling, soldering, testing, and repairing printed circuit boards and electronic components."
        },
        "THA.OCC.SNR": {
                "code": "THA.OCC.SNR",
                "name": "Sensor & Instrumentation Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, calibrating, and maintaining sensors, transducers, transmitters, and process control instrumentation."
        },
        "THA.OCC.PLC": {
                "code": "THA.OCC.PLC",
                "name": "PLC Programming & Commissioning",
                "parent_trf": "TRF.OCC",
                "description": "Programming, configuring, testing, and commissioning programmable logic controllers for industrial automation."
        },
        "THA.OCC.PWR": {
                "code": "THA.OCC.PWR",
                "name": "Power Line & Distribution Work",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, and repairing overhead and underground power lines, transformers, and distribution equipment."
        },
        "THA.OCC.SOL": {
                "code": "THA.OCC.SOL",
                "name": "Solar & Renewable Energy Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, connecting, and commissioning solar photovoltaic systems, inverters, and battery storage systems."
        },
        "THA.OCC.TEL": {
                "code": "THA.OCC.TEL",
                "name": "Telecommunications & Fibre Cabling",
                "parent_trf": "TRF.OCC",
                "description": "Installing, terminating, splicing, and testing copper and fibre optic telecommunications cables and infrastructure."
        },
        "THA.OCC.PEM": {
                "code": "THA.OCC.PEM",
                "name": "Petrol Engine Servicing",
                "parent_trf": "TRF.OCC",
                "description": "Servicing, tuning, diagnosing, and repairing spark-ignition petrol engines and their fuel and ignition systems."
        },
        "THA.OCC.DSE": {
                "code": "THA.OCC.DSE",
                "name": "Diesel Engine Servicing",
                "parent_trf": "TRF.OCC",
                "description": "Servicing, diagnosing, and repairing compression-ignition diesel engines and their fuel injection systems."
        },
        "THA.OCC.GBX": {
                "code": "THA.OCC.GBX",
                "name": "Gearbox & Transmission Repair",
                "parent_trf": "TRF.OCC",
                "description": "Disassembling, inspecting, repairing, and reassembling manual and automatic transmissions, gearboxes, and final drives."
        },
        "THA.OCC.HYD": {
                "code": "THA.OCC.HYD",
                "name": "Hydraulic System Repair",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, diagnosing, and repairing hydraulic circuits, cylinders, valves, pumps, and power packs."
        },
        "THA.OCC.PNE": {
                "code": "THA.OCC.PNE",
                "name": "Pneumatic System Repair",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, and repairing pneumatic circuits, actuators, valves, compressors, and air treatment equipment."
        },
        "THA.OCC.BRG": {
                "code": "THA.OCC.BRG",
                "name": "Bearing, Seal & Coupling Fitting",
                "parent_trf": "TRF.OCC",
                "description": "Removing, fitting, and aligning bearings, seals, couplings, belts, chains, and mechanical drive components."
        },
        "THA.OCC.PMP": {
                "code": "THA.OCC.PMP",
                "name": "Pump & Compressor Servicing",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, overhauling, and troubleshooting centrifugal, positive displacement, and reciprocating pumps and compressors."
        },
        "THA.OCC.VIB": {
                "code": "THA.OCC.VIB",
                "name": "Condition Monitoring & Vibration Analysis",
                "parent_trf": "TRF.OCC",
                "description": "Performing vibration analysis, thermography, oil analysis, and ultrasonic testing for predictive maintenance."
        },
        "THA.OCC.PMT": {
                "code": "THA.OCC.PMT",
                "name": "Preventive Maintenance Scheduling",
                "parent_trf": "TRF.OCC",
                "description": "Planning, scheduling, and executing planned maintenance activities using maintenance management systems and procedures."
        },
        "THA.OCC.COP": {
                "code": "THA.OCC.COP",
                "name": "Copper & Plastic Pipe Joining",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, deburring, and joining copper, PEX, and plastic pipes using soldering, brazing, compression, and push-fit methods."
        },
        "THA.OCC.DRN": {
                "code": "THA.OCC.DRN",
                "name": "Drainage & Sewer Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, testing, and maintaining below-ground drainage, sewerage, and stormwater systems including grading and venting."
        },
        "THA.OCC.GAS": {
                "code": "THA.OCC.GAS",
                "name": "Gas Fitting & Appliance Commissioning",
                "parent_trf": "TRF.OCC",
                "description": "Installing, purging, testing, and commissioning gas piping, meters, regulators, and gas-fired appliances."
        },
        "THA.OCC.HWS": {
                "code": "THA.OCC.HWS",
                "name": "Hot Water System Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing, connecting, and commissioning storage, instantaneous, heat pump, and solar hot water systems."
        },
        "THA.OCC.BFP": {
                "code": "THA.OCC.BFP",
                "name": "Backflow Prevention & Testing",
                "parent_trf": "TRF.OCC",
                "description": "Installing, testing, and maintaining backflow prevention devices and cross-connection control systems."
        },
        "THA.OCC.RFG": {
                "code": "THA.OCC.RFG",
                "name": "Roof Covering & Flashing",
                "parent_trf": "TRF.OCC",
                "description": "Installing and repairing metal, tile, and membrane roof coverings, flashings, gutters, and downpipes."
        },
        "THA.OCC.WPF": {
                "code": "THA.OCC.WPF",
                "name": "Waterproofing & Membrane Application",
                "parent_trf": "TRF.OCC",
                "description": "Applying waterproofing membranes, sealants, and damp-proofing systems to wet areas, balconies, and below-grade structures."
        },
        "THA.OCC.WLF": {
                "code": "THA.OCC.WLF",
                "name": "Wall Framing & Assembly",
                "parent_trf": "TRF.OCC",
                "description": "Constructing timber and steel wall frames including layout, cutting, assembly, bracing, and tie-down."
        },
        "THA.OCC.RFR": {
                "code": "THA.OCC.RFR",
                "name": "Roof Framing & Truss Installation",
                "parent_trf": "TRF.OCC",
                "description": "Constructing roof frames, installing prefabricated trusses, and fitting ridge, hip, and valley members."
        },
        "THA.OCC.FLR": {
                "code": "THA.OCC.FLR",
                "name": "Floristry & Floral Design",
                "parent_trf": "TRF.OCC",
                "description": "Creating floral arrangements, bouquets, and installations using design principles, flower conditioning, and wiring techniques."
        },
        "THA.OCC.MSN": {
                "code": "THA.OCC.MSN",
                "name": "Bricklaying & Blockwork",
                "parent_trf": "TRF.OCC",
                "description": "Laying bricks, blocks, and stone to line and level for walls, arches, piers, and decorative features."
        },
        "THA.OCC.CPR": {
                "code": "THA.OCC.CPR",
                "name": "Concrete Placing & Finishing",
                "parent_trf": "TRF.OCC",
                "description": "Placing, compacting, screeding, floating, and finishing concrete for slabs, footings, paths, and structural elements."
        },
        "THA.OCC.FWK": {
                "code": "THA.OCC.FWK",
                "name": "Formwork Construction & Stripping",
                "parent_trf": "TRF.OCC",
                "description": "Constructing, erecting, and stripping timber and steel formwork for concrete pours."
        },
        "THA.OCC.SCF": {
                "code": "THA.OCC.SCF",
                "name": "Scaffolding Erection & Dismantling",
                "parent_trf": "TRF.OCC",
                "description": "Erecting, altering, and dismantling scaffolding and temporary access structures in compliance with safety standards."
        },
        "THA.OCC.TIL": {
                "code": "THA.OCC.TIL",
                "name": "Tiling & Waterproofing",
                "parent_trf": "TRF.OCC",
                "description": "Laying ceramic tiles, porcelain, and natural stone on walls and floors including substrate preparation and grouting."
        },
        "THA.OCC.PLT": {
                "code": "THA.OCC.PLT",
                "name": "Plastering & Rendering",
                "parent_trf": "TRF.OCC",
                "description": "Applying plaster, render, texture coats, and decorative finishes to internal and external wall and ceiling surfaces."
        },
        "THA.OCC.GYP": {
                "code": "THA.OCC.GYP",
                "name": "Plasterboard Installation & Finishing",
                "parent_trf": "TRF.OCC",
                "description": "Installing plasterboard sheets, jointing, sanding, and finishing to create smooth wall and ceiling linings."
        },
        "THA.OCC.CLD": {
                "code": "THA.OCC.CLD",
                "name": "External Cladding & Facade Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing external cladding systems, weatherboards, composite panels, and facade elements."
        },
        "THA.OCC.GLZ": {
                "code": "THA.OCC.GLZ",
                "name": "Glazing & Window Installation",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, fitting, and installing glass, mirrors, curtain walls, and window assemblies."
        },
        "THA.OCC.FLC": {
                "code": "THA.OCC.FLC",
                "name": "Floor Covering Installation",
                "parent_trf": "TRF.OCC",
                "description": "Installing vinyl, carpet, laminate, and timber flooring including measuring, cutting, and adhesive application."
        },
        "THA.OCC.CAB": {
                "code": "THA.OCC.CAB",
                "name": "Cabinet Construction & Installation",
                "parent_trf": "TRF.OCC",
                "description": "Manufacturing and installing cabinets, built-in furniture, benchtops, and architectural joinery components."
        },
        "THA.OCC.STO": {
                "code": "THA.OCC.STO",
                "name": "Setting Out & Levelling",
                "parent_trf": "TRF.OCC",
                "description": "Establishing building lines, levels, setout points, and datum references using optical and laser instruments."
        },
        "THA.OCC.DML": {
                "code": "THA.OCC.DML",
                "name": "Demolition & Asbestos Removal",
                "parent_trf": "TRF.OCC",
                "description": "Safely demolishing structures, removing hazardous materials including asbestos, and managing demolition waste."
        },
        "THA.OCC.IRR": {
                "code": "THA.OCC.IRR",
                "name": "Irrigation System Installation",
                "parent_trf": "TRF.OCC",
                "description": "Designing, installing, and maintaining irrigation systems including sprinklers, drip lines, controllers, and pumps."
        },
        "THA.OCC.SPL": {
                "code": "THA.OCC.SPL",
                "name": "Split System Installation & Service",
                "parent_trf": "TRF.OCC",
                "description": "Installing, commissioning, diagnosing, and servicing split and multi-split air conditioning systems."
        },
        "THA.OCC.CRF": {
                "code": "THA.OCC.CRF",
                "name": "Commercial Refrigeration Service",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, and repairing commercial refrigeration display cases, cool rooms, and refrigerated transport."
        },
        "THA.OCC.DCT": {
                "code": "THA.OCC.DCT",
                "name": "Ductwork Fabrication & Installation",
                "parent_trf": "TRF.OCC",
                "description": "Fabricating, installing, insulating, and balancing sheet metal and flexible ductwork for ventilation and air conditioning."
        },
        "THA.OCC.RFH": {
                "code": "THA.OCC.RFH",
                "name": "Refrigerant Handling & Recovery",
                "parent_trf": "TRF.OCC",
                "description": "Recovering, recycling, charging, and leak-testing refrigerant gases in compliance with environmental regulations."
        },
        "THA.OCC.PEM2": {
                "code": "THA.OCC.PEM2",
                "name": "Vehicle Petrol Engine Repair",
                "parent_trf": "TRF.OCC",
                "description": "Diagnosing and repairing automotive petrol engine faults including fuel injection, ignition, and emission systems."
        },
        "THA.OCC.DSE2": {
                "code": "THA.OCC.DSE2",
                "name": "Vehicle Diesel Engine Repair",
                "parent_trf": "TRF.OCC",
                "description": "Diagnosing and repairing automotive diesel engine faults including common rail, turbocharger, and exhaust systems."
        },
        "THA.OCC.ABR": {
                "code": "THA.OCC.ABR",
                "name": "Vehicle Brake & Suspension Repair",
                "parent_trf": "TRF.OCC",
                "description": "Servicing and repairing disc and drum brakes, ABS, suspension, steering, and wheel alignment systems."
        },
        "THA.OCC.AEL": {
                "code": "THA.OCC.AEL",
                "name": "Vehicle Electrical & Electronic Repair",
                "parent_trf": "TRF.OCC",
                "description": "Diagnosing and repairing vehicle electrical systems, CAN bus networks, engine management, and onboard electronics."
        },
        "THA.OCC.EVS": {
                "code": "THA.OCC.EVS",
                "name": "Electric Vehicle Systems",
                "parent_trf": "TRF.OCC",
                "description": "Servicing, diagnosing, and repairing electric and hybrid vehicle drive systems, batteries, and charging infrastructure."
        },
        "THA.OCC.PNL": {
                "code": "THA.OCC.PNL",
                "name": "Panel Beating & Body Repair",
                "parent_trf": "TRF.OCC",
                "description": "Repairing vehicle body panels, performing structural alignment, MIG welding, filling, and preparing for refinishing."
        },
        "THA.OCC.VRF": {
                "code": "THA.OCC.VRF",
                "name": "Vehicle Refinishing & Detailing",
                "parent_trf": "TRF.OCC",
                "description": "Spray painting vehicles, matching colours, applying clear coat, polishing, and detailing to factory finish standards."
        },
        "THA.OCC.VOP": {
                "code": "THA.OCC.VOP",
                "name": "Heavy Vehicle & Plant Driving",
                "parent_trf": "TRF.OCC",
                "description": "Safely operating heavy rigid vehicles, articulated trucks, buses, and mobile plant on roads and worksites."
        },
        "THA.OCC.CRN": {
                "code": "THA.OCC.CRN",
                "name": "Crane Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating mobile, tower, and overhead cranes including load chart interpretation, lift planning, and safe operation."
        },
        "THA.OCC.RIG": {
                "code": "THA.OCC.RIG",
                "name": "Rigging & Load Slinging",
                "parent_trf": "TRF.OCC",
                "description": "Selecting and attaching slings, chains, and shackles; calculating loads; and directing crane movements as a dogger or rigger."
        },
        "THA.OCC.FLT": {
                "code": "THA.OCC.FLT",
                "name": "Forklift & Warehouse Equipment Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating counterbalance forklifts, reach trucks, order pickers, and pallet jacks for material handling."
        },
        "THA.OCC.ETH": {
                "code": "THA.OCC.ETH",
                "name": "Excavation & Earthmoving",
                "parent_trf": "TRF.OCC",
                "description": "Operating excavators, backhoes, bulldozers, graders, and compaction equipment for earthworks and civil works."
        },
        "THA.OCC.EWP": {
                "code": "THA.OCC.EWP",
                "name": "Elevated Work Platform Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating boom lifts, scissor lifts, and other elevated work platforms for working safely at heights."
        },
        "THA.OCC.DRL": {
                "code": "THA.OCC.DRL",
                "name": "Drilling & Piling",
                "parent_trf": "TRF.OCC",
                "description": "Operating drilling rigs, boring equipment, and piling machines for construction, exploration, and resource extraction."
        },
        "THA.OCC.ORM": {
                "code": "THA.OCC.ORM",
                "name": "Oral Medication Administration",
                "parent_trf": "TRF.OCC",
                "description": "Preparing, checking, and administering oral, sublingual, and topical medications following the rights of medication administration."
        },
        "THA.OCC.INJ": {
                "code": "THA.OCC.INJ",
                "name": "Injection & Immunisation",
                "parent_trf": "TRF.OCC",
                "description": "Preparing and administering subcutaneous, intramuscular, and intradermal injections including immunisation procedures."
        },
        "THA.OCC.IVT": {
                "code": "THA.OCC.IVT",
                "name": "Intravenous Therapy & Cannulation",
                "parent_trf": "TRF.OCC",
                "description": "Inserting cannulae, managing IV lines, administering IV fluids and medications, and monitoring infusion therapy."
        },
        "THA.OCC.WND": {
                "code": "THA.OCC.WND",
                "name": "Wound Assessment & Dressing",
                "parent_trf": "TRF.OCC",
                "description": "Assessing, cleaning, debriding, and dressing wounds including surgical wounds, pressure injuries, and burns."
        },
        "THA.OCC.RSP": {
                "code": "THA.OCC.RSP",
                "name": "Airway & Respiratory Management",
                "parent_trf": "TRF.OCC",
                "description": "Managing airways, administering oxygen therapy, operating ventilators, performing suctioning, and monitoring respiratory function."
        },
        "THA.OCC.PHY": {
                "code": "THA.OCC.PHY",
                "name": "Manual Therapy & Mobilisation",
                "parent_trf": "TRF.OCC",
                "description": "Applying hands-on therapeutic techniques including joint mobilisation, soft tissue manipulation, and manual lymphatic drainage."
        },
        "THA.OCC.EXT": {
                "code": "THA.OCC.EXT",
                "name": "Therapeutic Exercise Prescription",
                "parent_trf": "TRF.OCC",
                "description": "Designing and supervising exercise programs for rehabilitation, strengthening, and functional restoration."
        },
        "THA.OCC.OTH": {
                "code": "THA.OCC.OTH",
                "name": "Functional Rehabilitation & Adaptation",
                "parent_trf": "TRF.OCC",
                "description": "Applying occupational therapy techniques for daily living skills, cognitive rehabilitation, and workplace modification."
        },
        "THA.OCC.DNT": {
                "code": "THA.OCC.DNT",
                "name": "Dental Chairside Assistance",
                "parent_trf": "TRF.OCC",
                "description": "Assisting with dental procedures, managing instruments, taking impressions, processing radiographs, and maintaining dental equipment."
        },
        "THA.OCC.SRG": {
                "code": "THA.OCC.SRG",
                "name": "Surgical Assistance & Perioperative Care",
                "parent_trf": "TRF.OCC",
                "description": "Preparing surgical environments, assisting during operations, managing instruments, and supporting pre and post-operative care."
        },
        "THA.OCC.BLS": {
                "code": "THA.OCC.BLS",
                "name": "Basic & Advanced Life Support",
                "parent_trf": "TRF.OCC",
                "description": "Performing CPR, using defibrillators, managing cardiac arrest, and providing basic and advanced life support interventions."
        },
        "THA.OCC.PAL": {
                "code": "THA.OCC.PAL",
                "name": "Palliative & End-of-Life Care",
                "parent_trf": "TRF.OCC",
                "description": "Providing comfort care, pain and symptom management, emotional support, and dignity for individuals at end of life."
        },
        "THA.OCC.MHC": {
                "code": "THA.OCC.MHC",
                "name": "Mental Health Crisis Intervention",
                "parent_trf": "TRF.OCC",
                "description": "Providing mental health first aid, de-escalation, suicide prevention, and recovery-oriented crisis support."
        },
        "THA.OCC.CTH": {
                "code": "THA.OCC.CTH",
                "name": "Catheter & Continence Care",
                "parent_trf": "TRF.OCC",
                "description": "Managing urinary catheters, continence aids, stoma care, and related elimination support procedures."
        },
        "THA.OCC.ADL": {
                "code": "THA.OCC.ADL",
                "name": "Personal Care & Daily Living Support",
                "parent_trf": "TRF.OCC",
                "description": "Assisting individuals with personal hygiene, bathing, dressing, eating, mobility, and routine daily tasks."
        },
        "THA.OCC.MAN": {
                "code": "THA.OCC.MAN",
                "name": "Patient Handling & Transfer",
                "parent_trf": "TRF.OCC",
                "description": "Safely lifting, transferring, and repositioning patients using hoists, slide sheets, and ergonomic handling techniques."
        },
        "THA.OCC.HPC": {
                "code": "THA.OCC.HPC",
                "name": "Health Promotion & Community Education",
                "parent_trf": "TRF.OCC",
                "description": "Delivering health education, screening programs, and preventive health messages to individuals and community groups."
        },
        "THA.OCC.FAD": {
                "code": "THA.OCC.FAD",
                "name": "First Aid & Trauma Response",
                "parent_trf": "TRF.OCC",
                "description": "Providing first aid, managing trauma, controlling bleeding, treating shock, and stabilising patients at emergency scenes."
        },
        "THA.OCC.FFS": {
                "code": "THA.OCC.FFS",
                "name": "Firefighting & Suppression",
                "parent_trf": "TRF.OCC",
                "description": "Operating firefighting equipment, applying suppression techniques, and conducting search and rescue in fire environments."
        },
        "THA.OCC.HAZ": {
                "code": "THA.OCC.HAZ",
                "name": "Hazardous Materials Response",
                "parent_trf": "TRF.OCC",
                "description": "Responding to chemical, biological, and radiological incidents including containment, decontamination, and safe handling."
        },
        "THA.OCC.CSR": {
                "code": "THA.OCC.CSR",
                "name": "Confined Space & Vertical Rescue",
                "parent_trf": "TRF.OCC",
                "description": "Performing rescue operations in confined spaces, at heights, and in environments with restricted access."
        },
        "THA.OCC.EVC": {
                "code": "THA.OCC.EVC",
                "name": "Emergency Evacuation & Warden Duties",
                "parent_trf": "TRF.OCC",
                "description": "Planning, coordinating, and conducting emergency evacuations, fire drills, and floor warden responsibilities."
        },
        "THA.OCC.CHM": {
                "code": "THA.OCC.CHM",
                "name": "Chemical Mixing & Application",
                "parent_trf": "TRF.OCC",
                "description": "Measuring, mixing, and applying chemical products safely including pesticides, herbicides, cleaning agents, and industrial chemicals."
        },
        "THA.OCC.DGH": {
                "code": "THA.OCC.DGH",
                "name": "Dangerous Goods Handling & Transport",
                "parent_trf": "TRF.OCC",
                "description": "Packing, labelling, storing, and transporting dangerous goods in compliance with ADG code and safety regulations."
        },
        "THA.OCC.BIO": {
                "code": "THA.OCC.BIO",
                "name": "Biological Specimen Processing",
                "parent_trf": "TRF.OCC",
                "description": "Collecting, processing, and managing biological specimens including tissue processing, cryogenic storage, and biosafety protocols."
        },
        "THA.OCC.MCB": {
                "code": "THA.OCC.MCB",
                "name": "Microbiology & Culture Technique",
                "parent_trf": "TRF.OCC",
                "description": "Performing microbiological culture, identification, staining, and antimicrobial susceptibility testing in laboratory settings."
        },
        "THA.OCC.HCK": {
                "code": "THA.OCC.HCK",
                "name": "Hot Cooking Methods",
                "parent_trf": "TRF.OCC",
                "description": "Preparing and cooking food using grilling, roasting, frying, saut\u00e9ing, braising, steaming, and poaching techniques."
        },
        "THA.OCC.CCK": {
                "code": "THA.OCC.CCK",
                "name": "Cold Food Preparation",
                "parent_trf": "TRF.OCC",
                "description": "Preparing cold dishes, salads, sandwiches, appetisers, and garde manger items using knife skills and plating techniques."
        },
        "THA.OCC.PTY": {
                "code": "THA.OCC.PTY",
                "name": "Pastry, Baking & Dessert Production",
                "parent_trf": "TRF.OCC",
                "description": "Producing cakes, pastries, breads, and desserts using baking, laminating, tempering, fermenting, and decorating techniques."
        },
        "THA.OCC.FHS": {
                "code": "THA.OCC.FHS",
                "name": "Food Safety & HACCP Implementation",
                "parent_trf": "TRF.OCC",
                "description": "Implementing food safety systems, HACCP plans, temperature monitoring, allergen management, and food handling compliance."
        },
        "THA.OCC.BAR": {
                "code": "THA.OCC.BAR",
                "name": "Beverage Preparation & Service",
                "parent_trf": "TRF.OCC",
                "description": "Preparing and serving espresso coffee, cocktails, wines, and beverages using bar equipment and service protocols."
        },
        "THA.OCC.FBS": {
                "code": "THA.OCC.FBS",
                "name": "Table & Restaurant Service",
                "parent_trf": "TRF.OCC",
                "description": "Providing table service, managing dining rooms, serving courses, and delivering front-of-house hospitality."
        },
        "THA.OCC.ACC": {
                "code": "THA.OCC.ACC",
                "name": "Reception & Guest Services",
                "parent_trf": "TRF.OCC",
                "description": "Managing front desk, reservations, check-in/check-out, room allocation, concierge services, and guest relations."
        },
        "THA.OCC.HSK": {
                "code": "THA.OCC.HSK",
                "name": "Housekeeping & Room Servicing",
                "parent_trf": "TRF.OCC",
                "description": "Cleaning and servicing guest rooms, public areas, and laundry to accommodation standards."
        },
        "THA.OCC.CRP": {
                "code": "THA.OCC.CRP",
                "name": "Broadacre Crop Production",
                "parent_trf": "TRF.OCC",
                "description": "Planting, cultivating, irrigating, fertilising, and harvesting field crops and pastures using farm machinery."
        },
        "THA.OCC.HRT": {
                "code": "THA.OCC.HRT",
                "name": "Horticultural Propagation & Growing",
                "parent_trf": "TRF.OCC",
                "description": "Propagating plants from seed, cutting, and graft; managing nursery production; and cultivating horticultural crops."
        },
        "THA.OCC.VIT": {
                "code": "THA.OCC.VIT",
                "name": "Viticulture & Winemaking",
                "parent_trf": "TRF.OCC",
                "description": "Managing grapevine cultivation, harvest timing, grape processing, fermentation, and winemaking operations."
        },
        "THA.OCC.BRW": {
                "code": "THA.OCC.BRW",
                "name": "Brewing, Distilling & Fermentation",
                "parent_trf": "TRF.OCC",
                "description": "Managing fermentation processes for beer, spirits, and fermented products including quality monitoring and packaging."
        },
        "THA.OCC.TRF": {
                "code": "THA.OCC.TRF",
                "name": "Turf Establishment & Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Establishing, mowing, fertilising, aerating, and maintaining turf surfaces for sports fields, parks, and landscapes."
        },
        "THA.OCC.ARB": {
                "code": "THA.OCC.ARB",
                "name": "Arboriculture & Tree Surgery",
                "parent_trf": "TRF.OCC",
                "description": "Pruning, removing, and managing trees using climbing, rigging, and chainsaw techniques with arboricultural knowledge."
        },
        "THA.OCC.LDS": {
                "code": "THA.OCC.LDS",
                "name": "Landscape Design & Installation",
                "parent_trf": "TRF.OCC",
                "description": "Designing, constructing, and installing landscape features including gardens, paths, retaining walls, and softscape areas."
        },
        "THA.OCC.SOI": {
                "code": "THA.OCC.SOI",
                "name": "Soil Assessment & Remediation",
                "parent_trf": "TRF.OCC",
                "description": "Testing soil properties, recommending amendments, managing erosion, and implementing soil conservation and rehabilitation."
        },
        "THA.OCC.PST": {
                "code": "THA.OCC.PST",
                "name": "Pest & Weed Management",
                "parent_trf": "TRF.OCC",
                "description": "Identifying and controlling pests, weeds, and diseases using chemical, biological, and integrated management methods."
        },
        "THA.OCC.FUM": {
                "code": "THA.OCC.FUM",
                "name": "Fumigation & Termite Treatment",
                "parent_trf": "TRF.OCC",
                "description": "Conducting structural fumigation, termite barrier installation, baiting systems, and timber pest inspections."
        },
        "THA.OCC.LSH": {
                "code": "THA.OCC.LSH",
                "name": "Livestock Handling & Mustering",
                "parent_trf": "TRF.OCC",
                "description": "Handling, restraining, mustering, drafting, and transporting cattle, sheep, and other livestock safely."
        },
        "THA.OCC.LSF": {
                "code": "THA.OCC.LSF",
                "name": "Livestock Feeding & Nutrition",
                "parent_trf": "TRF.OCC",
                "description": "Formulating rations, managing feed programs, operating feeding systems, and monitoring nutritional intake for livestock."
        },
        "THA.OCC.ANB": {
                "code": "THA.OCC.ANB",
                "name": "Animal Breeding & Reproduction",
                "parent_trf": "TRF.OCC",
                "description": "Managing breeding programs, artificial insemination, pregnancy testing, birthing assistance, and genetic selection."
        },
        "THA.OCC.AVT": {
                "code": "THA.OCC.AVT",
                "name": "Veterinary Clinical Assistance",
                "parent_trf": "TRF.OCC",
                "description": "Assisting with veterinary examinations, administering treatments, preparing animals for surgery, and managing clinical records."
        },
        "THA.OCC.SHR": {
                "code": "THA.OCC.SHR",
                "name": "Shearing & Wool Handling",
                "parent_trf": "TRF.OCC",
                "description": "Shearing sheep using mechanical handpieces, classing wool, pressing bales, and preparing clips for sale."
        },
        "THA.OCC.EQN": {
                "code": "THA.OCC.EQN",
                "name": "Equine Handling & Care",
                "parent_trf": "TRF.OCC",
                "description": "Handling, grooming, exercising, feeding, and providing daily care for horses including hoof care and tack management."
        },
        "THA.OCC.FAR": {
                "code": "THA.OCC.FAR",
                "name": "Farriery & Hoof Care",
                "parent_trf": "TRF.OCC",
                "description": "Trimming hooves, fitting horseshoes, corrective shoeing, and maintaining equine hoof health."
        },
        "THA.OCC.KNL": {
                "code": "THA.OCC.KNL",
                "name": "Companion Animal Care & Grooming",
                "parent_trf": "TRF.OCC",
                "description": "Providing daily care, grooming, bathing, and basic health monitoring for dogs, cats, and companion animals."
        },
        "THA.OCC.DTR": {
                "code": "THA.OCC.DTR",
                "name": "Animal Behaviour & Training",
                "parent_trf": "TRF.OCC",
                "description": "Assessing animal behaviour, applying positive reinforcement training techniques, and modifying unwanted behaviours."
        },
        "THA.OCC.AQU": {
                "code": "THA.OCC.AQU",
                "name": "Aquaculture & Fish Farming",
                "parent_trf": "TRF.OCC",
                "description": "Managing aquatic species production, hatchery operations, pond/cage management, water quality, and harvesting."
        },
        "THA.OCC.UGM": {
                "code": "THA.OCC.UGM",
                "name": "Underground Mining Development",
                "parent_trf": "TRF.OCC",
                "description": "Operating underground equipment, installing ground support, managing ventilation, and conducting development drives."
        },
        "THA.OCC.OCM": {
                "code": "THA.OCC.OCM",
                "name": "Open Cut Mining Operations",
                "parent_trf": "TRF.OCC",
                "description": "Operating equipment for bench operations, overburden removal, loading, and hauling in open cut environments."
        },
        "THA.OCC.BLT": {
                "code": "THA.OCC.BLT",
                "name": "Blasting & Shot Firing",
                "parent_trf": "TRF.OCC",
                "description": "Preparing, loading, wiring, and firing explosive charges for mining, quarrying, and construction blasting."
        },
        "THA.OCC.OPR": {
                "code": "THA.OCC.OPR",
                "name": "Mineral Processing & Separation",
                "parent_trf": "TRF.OCC",
                "description": "Operating crushing, grinding, flotation, gravity separation, and leaching circuits for mineral extraction."
        },
        "THA.OCC.NAV": {
                "code": "THA.OCC.NAV",
                "name": "Vessel Navigation & Piloting",
                "parent_trf": "TRF.OCC",
                "description": "Navigating vessels using charts, radar, GPS, and electronic aids; managing bridge watch; and plotting courses."
        },
        "THA.OCC.MCG": {
                "code": "THA.OCC.MCG",
                "name": "Deck Operations & Cargo Handling",
                "parent_trf": "TRF.OCC",
                "description": "Managing deck equipment, mooring, anchoring, cargo loading and discharge, and marine safety equipment."
        },
        "THA.OCC.MEN": {
                "code": "THA.OCC.MEN",
                "name": "Marine Engine Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating, monitoring, and maintaining marine propulsion engines, auxiliary systems, and engineering equipment."
        },
        "THA.OCC.DIV": {
                "code": "THA.OCC.DIV",
                "name": "Commercial Diving & Underwater Work",
                "parent_trf": "TRF.OCC",
                "description": "Performing underwater inspection, welding, cutting, construction, and salvage using surface-supplied and SCUBA diving."
        },
        "THA.OCC.ACM": {
                "code": "THA.OCC.ACM",
                "name": "Aircraft Airframe Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Inspecting, repairing, and maintaining aircraft structures, control surfaces, landing gear, and airframe systems."
        },
        "THA.OCC.AVI": {
                "code": "THA.OCC.AVI",
                "name": "Avionics Installation & Repair",
                "parent_trf": "TRF.OCC",
                "description": "Installing, testing, and maintaining avionics, flight instruments, navigation systems, and aircraft communication equipment."
        },
        "THA.OCC.UAV": {
                "code": "THA.OCC.UAV",
                "name": "Drone & UAV Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating remotely piloted aircraft for survey, inspection, photography, and agricultural applications."
        },
        "THA.OCC.SEW": {
                "code": "THA.OCC.SEW",
                "name": "Machine Sewing & Garment Assembly",
                "parent_trf": "TRF.OCC",
                "description": "Operating industrial sewing machines to cut, stitch, and assemble garments and textile products."
        },
        "THA.OCC.PAT": {
                "code": "THA.OCC.PAT",
                "name": "Pattern Drafting & Grading",
                "parent_trf": "TRF.OCC",
                "description": "Drafting, modifying, and grading garment patterns for production using manual and digital methods."
        },
        "THA.OCC.UPH": {
                "code": "THA.OCC.UPH",
                "name": "Upholstery & Soft Furnishing",
                "parent_trf": "TRF.OCC",
                "description": "Producing and repairing upholstered furniture, curtains, blinds, and soft furnishings."
        },
        "THA.OCC.ALT": {
                "code": "THA.OCC.ALT",
                "name": "Garment Alteration & Repair",
                "parent_trf": "TRF.OCC",
                "description": "Performing alterations, repairs, and adjustments to garments including hemming, resizing, and mending."
        },
        "THA.OCC.HCT": {
                "code": "THA.OCC.HCT",
                "name": "Hair Cutting & Styling",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, blow-drying, setting, and styling hair using professional techniques, tools, and products."
        },
        "THA.OCC.HCL": {
                "code": "THA.OCC.HCL",
                "name": "Hair Colouring & Chemical Treatment",
                "parent_trf": "TRF.OCC",
                "description": "Applying hair colour, highlights, tints, perming, and chemical straightening treatments."
        },
        "THA.OCC.SKN": {
                "code": "THA.OCC.SKN",
                "name": "Facial & Skin Treatment",
                "parent_trf": "TRF.OCC",
                "description": "Performing facial treatments, skin analysis, microdermabrasion, peels, and recommending skincare programs."
        },
        "THA.OCC.WAX": {
                "code": "THA.OCC.WAX",
                "name": "Body Waxing & Hair Removal",
                "parent_trf": "TRF.OCC",
                "description": "Performing waxing, sugaring, threading, and other hair removal techniques on face and body."
        },
        "THA.OCC.MSG": {
                "code": "THA.OCC.MSG",
                "name": "Remedial & Relaxation Massage",
                "parent_trf": "TRF.OCC",
                "description": "Performing remedial, relaxation, sports, and therapeutic massage techniques for pain relief and wellbeing."
        },
        "THA.OCC.NLT": {
                "code": "THA.OCC.NLT",
                "name": "Nail Enhancement & Art",
                "parent_trf": "TRF.OCC",
                "description": "Applying, maintaining, and removing nail enhancements including acrylics, gels, and nail art techniques."
        },
        "THA.OCC.MKP": {
                "code": "THA.OCC.MKP",
                "name": "Makeup Application & Design",
                "parent_trf": "TRF.OCC",
                "description": "Applying makeup for fashion, bridal, theatre, film, and special effects using professional techniques and products."
        },
        "THA.OCC.GFI": {
                "code": "THA.OCC.GFI",
                "name": "Gym & Personal Training",
                "parent_trf": "TRF.OCC",
                "description": "Instructing gym floor exercises, designing personal training programs, and conducting fitness assessments."
        },
        "THA.OCC.GRP": {
                "code": "THA.OCC.GRP",
                "name": "Group Exercise Instruction",
                "parent_trf": "TRF.OCC",
                "description": "Planning and leading group fitness classes including aerobics, spin, yoga, and circuit-based sessions."
        },
        "THA.OCC.COA": {
                "code": "THA.OCC.COA",
                "name": "Sports Coaching & Athlete Development",
                "parent_trf": "TRF.OCC",
                "description": "Coaching sport-specific skills, managing training loads, developing competitive programs, and athlete preparation."
        },
        "THA.OCC.AQP": {
                "code": "THA.OCC.AQP",
                "name": "Aquatic Instruction & Lifeguarding",
                "parent_trf": "TRF.OCC",
                "description": "Teaching swimming, supervising pool safety, performing aquatic rescues, and managing pool water quality."
        },
        "THA.OCC.BKE": {
                "code": "THA.OCC.BKE",
                "name": "Back-End Development",
                "parent_trf": "TRF.OCC",
                "description": "Writing server-side application code, building APIs, managing data persistence, and implementing business logic."
        },
        "THA.OCC.FRE": {
                "code": "THA.OCC.FRE",
                "name": "Front-End & UI Development",
                "parent_trf": "TRF.OCC",
                "description": "Building user interfaces using HTML, CSS, JavaScript frameworks, and responsive design principles."
        },
        "THA.OCC.DBA": {
                "code": "THA.OCC.DBA",
                "name": "Database Design & Administration",
                "parent_trf": "TRF.OCC",
                "description": "Designing schemas, writing queries, optimising performance, managing backups, and maintaining relational and NoSQL databases."
        },
        "THA.OCC.MOB": {
                "code": "THA.OCC.MOB",
                "name": "Mobile Application Development",
                "parent_trf": "TRF.OCC",
                "description": "Developing, testing, and deploying native and cross-platform mobile applications for iOS and Android."
        },
        "THA.OCC.TST": {
                "code": "THA.OCC.TST",
                "name": "Software Testing & Quality Assurance",
                "parent_trf": "TRF.OCC",
                "description": "Designing test cases, executing manual and automated tests, reporting defects, and verifying software quality."
        },
        "THA.OCC.GRD": {
                "code": "THA.OCC.GRD",
                "name": "Security Patrol & Access Control",
                "parent_trf": "TRF.OCC",
                "description": "Conducting security patrols, managing access points, screening persons, and responding to security incidents."
        },
        "THA.OCC.CWD": {
                "code": "THA.OCC.CWD",
                "name": "Crowd Management & Event Security",
                "parent_trf": "TRF.OCC",
                "description": "Managing crowds, controlling access at events, de-escalating situations, and coordinating security teams."
        },
        "THA.OCC.DRW": {
                "code": "THA.OCC.DRW",
                "name": "Drawing & Fine Art",
                "parent_trf": "TRF.OCC",
                "description": "Creating original artworks using drawing, painting, sculpture, printmaking, and mixed media techniques."
        },
        "THA.OCC.GFX": {
                "code": "THA.OCC.GFX",
                "name": "Graphic Design & Visual Communication",
                "parent_trf": "TRF.OCC",
                "description": "Designing logos, marketing materials, publications, and digital graphics using layout and design software."
        },
        "THA.OCC.PHO": {
                "code": "THA.OCC.PHO",
                "name": "Photography & Image Editing",
                "parent_trf": "TRF.OCC",
                "description": "Capturing, composing, lighting, and editing photographic images for commercial, editorial, and artistic purposes."
        },
        "THA.OCC.VID": {
                "code": "THA.OCC.VID",
                "name": "Video Production & Editing",
                "parent_trf": "TRF.OCC",
                "description": "Shooting, editing, colour grading, and producing video content for broadcast, web, and commercial applications."
        },
        "THA.OCC.SND": {
                "code": "THA.OCC.SND",
                "name": "Sound Recording & Mixing",
                "parent_trf": "TRF.OCC",
                "description": "Recording, mixing, editing, and mastering audio content including music, voiceover, and live sound reinforcement."
        },
        "THA.OCC.JWL": {
                "code": "THA.OCC.JWL",
                "name": "Jewellery Making & Stone Setting",
                "parent_trf": "TRF.OCC",
                "description": "Fabricating, soldering, setting stones, polishing, and finishing jewellery using precious and semi-precious materials."
        },
        "THA.OCC.CHD": {
                "code": "THA.OCC.CHD",
                "name": "Early Childhood Education & Care",
                "parent_trf": "TRF.OCC",
                "description": "Supporting childrens learning and development through play-based programs, observation, and age-appropriate activities."
        },
        "THA.OCC.YTH": {
                "code": "THA.OCC.YTH",
                "name": "Youth Work & Outreach",
                "parent_trf": "TRF.OCC",
                "description": "Engaging with young people through outreach, group programs, advocacy, mentoring, and support services."
        },
        "THA.OCC.AGC": {
                "code": "THA.OCC.AGC",
                "name": "Aged Care & Dementia Support",
                "parent_trf": "TRF.OCC",
                "description": "Providing specialised care for older people including dementia-specific approaches, reminiscence, and aged care standards."
        },
        "THA.OCC.AOD": {
                "code": "THA.OCC.AOD",
                "name": "Alcohol & Drug Intervention",
                "parent_trf": "TRF.OCC",
                "description": "Providing assessment, counselling, harm reduction, and support for individuals with substance use issues."
        },
        "THA.OCC.LCK": {
                "code": "THA.OCC.LCK",
                "name": "Locksmithing & Security Hardware",
                "parent_trf": "TRF.OCC",
                "description": "Installing, rekeying, repairing, and opening locks, safes, and access control hardware."
        },
        "THA.OCC.RLY": {
                "code": "THA.OCC.RLY",
                "name": "Railway Track & Signalling",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, and inspecting railway tracks, points, signals, and rail infrastructure systems."
        },
        "THA.OCC.BOA": {
                "code": "THA.OCC.BOA",
                "name": "Boatbuilding & Marine Construction",
                "parent_trf": "TRF.OCC",
                "description": "Constructing, repairing, and maintaining boat hulls, decks, and marine structures using timber, fibreglass, and composites."
        },
        "THA.OCC.MTP": {
                "code": "THA.OCC.MTP",
                "name": "Meat Processing & Butchery",
                "parent_trf": "TRF.OCC",
                "description": "Slaughtering, boning, cutting, trimming, and preparing meat products to specification and food safety standards."
        },
        "THA.OCC.BKY": {
                "code": "THA.OCC.BKY",
                "name": "Bread & Bakery Production",
                "parent_trf": "TRF.OCC",
                "description": "Producing bread, rolls, and yeast-raised products through mixing, proving, baking, and finishing at commercial scale."
        },
        "THA.OCC.FNR": {
                "code": "THA.OCC.FNR",
                "name": "Funeral & Mortuary Services",
                "parent_trf": "TRF.OCC",
                "description": "Preparing deceased persons, managing mortuary procedures, coordinating funeral services, and supporting bereaved families."
        },
        "THA.OCC.REP": {
                "code": "THA.OCC.REP",
                "name": "Real Estate & Property Management",
                "parent_trf": "TRF.OCC",
                "description": "Managing property sales, rentals, inspections, tenant relations, and trust accounting for residential and commercial property."
        },
        "THA.OCC.TAX": {
                "code": "THA.OCC.TAX",
                "name": "Taxidermy & Specimen Preservation",
                "parent_trf": "TRF.OCC",
                "description": "Preserving and mounting animal specimens using skinning, tanning, moulding, and posing techniques."
        },
        "THA.OCC.ENG": {
                "code": "THA.OCC.ENG",
                "name": "Engraving & Precision Marking",
                "parent_trf": "TRF.OCC",
                "description": "Engraving, etching, and precision marking on metals, glass, and other materials using hand and machine tools."
        },
        "THA.OCC.OPT": {
                "code": "THA.OCC.OPT",
                "name": "Optical Dispensing & Lens Fitting",
                "parent_trf": "TRF.OCC",
                "description": "Measuring, fitting, adjusting, and dispensing corrective lenses, frames, and optical appliances."
        },
        "THA.OCC.PRO": {
                "code": "THA.OCC.PRO",
                "name": "Prosthetics & Orthotics Fabrication",
                "parent_trf": "TRF.OCC",
                "description": "Fabricating, fitting, and adjusting prosthetic limbs and orthotic devices from measurements and prescriptions."
        },
        "THA.OCC.SGN": {
                "code": "THA.OCC.SGN",
                "name": "Sign Language & Assistive Communication",
                "parent_trf": "TRF.OCC",
                "description": "Communicating using Auslan or other sign languages and assistive communication methods for deaf and hearing-impaired individuals."
        },
        "THA.OCC.RPA": {
                "code": "THA.OCC.RPA",
                "name": "Rope Access & Height Safety",
                "parent_trf": "TRF.OCC",
                "description": "Performing work tasks at height using industrial rope access techniques, harnesses, and fall arrest systems."
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