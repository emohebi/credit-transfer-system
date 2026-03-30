"""
Transferable Human Ability (THA) Facet Definition

Each value includes typical_skills for embedding similarity matching.
"""

TRANSFERABLE_HUMAN_ABILITY_FACET = {
    "facet_id": "THA",
    "facet_name": "Transferable Human Ability",
    "description": "Functional human capability that can be applied across contexts.",
    "multi_value": True,
    "parent_facet": "TRF",
    "values": {
        "THA.UNI.ORC": {
                "code": "THA.UNI.ORC",
                "name": "Oral Communication",
                "parent_trf": "TRF.UNI",
                "description": "Listening to and understanding spoken information, and communicating ideas and information clearly through speech.",
                "keywords": [
                        "speaking",
                        "listening",
                        "verbal",
                        "conversation",
                        "presentation"
                ],
                "typical_skills": [
                        "communicate effectively in the workplace",
                        "use verbal communication skills",
                        "participate in workplace conversations",
                        "deliver verbal briefings and instructions",
                        "listen actively and respond appropriately",
                        "provide clear spoken directions",
                        "present information to small groups",
                        "confirm understanding through questioning",
                        "use effective telephone communication",
                        "participate in workplace meetings"
                ]
        },
        "THA.UNI.WRC": {
                "code": "THA.UNI.WRC",
                "name": "Written Communication",
                "parent_trf": "TRF.UNI",
                "description": "Reading, understanding, and producing written information. Includes report writing, documentation, form completion, and interpreting written instructions.",
                "keywords": [
                        "writing",
                        "reading",
                        "documentation",
                        "report",
                        "correspondence",
                        "forms"
                ],
                "typical_skills": [
                        "write workplace correspondence",
                        "read and interpret workplace documents",
                        "complete workplace forms and records",
                        "draft emails and written communications",
                        "interpret written instructions and procedures",
                        "prepare written notes and summaries",
                        "use workplace vocabulary and terminology",
                        "proofread documents for accuracy",
                        "write simple technical reports",
                        "maintain written workplace logs"
                ]
        },
        "THA.UNI.NUM": {
                "code": "THA.UNI.NUM",
                "name": "Numeracy & Calculation",
                "parent_trf": "TRF.UNI",
                "description": "Applying mathematical concepts including arithmetic, measurement, estimation, and basic statistical reasoning to workplace tasks.",
                "keywords": [
                        "mathematics",
                        "calculation",
                        "measurement",
                        "estimation",
                        "counting",
                        "arithmetic"
                ],
                "typical_skills": [
                        "perform basic workplace calculations",
                        "use and apply workplace numeracy",
                        "estimate and calculate quantities",
                        "take measurements and record dimensions",
                        "calculate percentages and ratios",
                        "apply units of measurement",
                        "interpret graphs tables and charts",
                        "calculate areas volumes and weights",
                        "perform financial calculations",
                        "use measuring instruments accurately"
                ]
        },
        "THA.UNI.DIG": {
                "code": "THA.UNI.DIG",
                "name": "Digital Literacy",
                "parent_trf": "TRF.UNI",
                "description": "Using digital devices, software applications, and online platforms effectively.",
                "keywords": [
                        "computer",
                        "digital",
                        "software",
                        "internet",
                        "technology",
                        "ICT"
                ],
                "typical_skills": [
                        "use digital technology in the workplace",
                        "operate basic computer applications",
                        "use business software applications",
                        "manage digital files and records",
                        "use internet and email effectively",
                        "apply digital literacy skills in the workplace",
                        "use word processing software",
                        "create and use spreadsheets",
                        "operate digital communication tools",
                        "navigate online platforms and systems"
                ]
        },
        "THA.UNI.LRN": {
                "code": "THA.UNI.LRN",
                "name": "Learning & Self-Development",
                "parent_trf": "TRF.UNI",
                "description": "Acquiring new knowledge and skills, reflecting on performance, seeking feedback, and adapting to new methods.",
                "keywords": [
                        "learning",
                        "training",
                        "development",
                        "study",
                        "upskilling",
                        "reflection"
                ],
                "typical_skills": [
                        "develop and maintain professional competence",
                        "participate in professional development activities",
                        "identify personal learning needs",
                        "apply learning to workplace tasks",
                        "seek and respond to workplace feedback",
                        "reflect on own professional practice",
                        "maintain currency of industry knowledge",
                        "develop a learning plan",
                        "adapt to new workplace procedures",
                        "engage in self-directed learning"
                ]
        },
        "THA.UNI.PSL": {
                "code": "THA.UNI.PSL",
                "name": "Problem Solving",
                "parent_trf": "TRF.UNI",
                "description": "Identifying problems, gathering relevant information, generating possible solutions, evaluating options, and implementing effective solutions.",
                "keywords": [
                        "problem solving",
                        "troubleshooting",
                        "solutions",
                        "resolving",
                        "identifying issues"
                ],
                "typical_skills": [
                        "solve problems in the workplace",
                        "apply problem-solving techniques",
                        "identify and resolve workplace issues",
                        "troubleshoot equipment and process faults",
                        "analyse problems and develop solutions",
                        "apply systematic problem-solving processes",
                        "use initiative to address workplace challenges",
                        "evaluate options and recommend solutions",
                        "investigate and resolve complaints",
                        "identify root causes of problems"
                ]
        },
        "THA.UNI.CRT": {
                "code": "THA.UNI.CRT",
                "name": "Critical Thinking & Judgement",
                "parent_trf": "TRF.UNI",
                "description": "Analysing information objectively, evaluating evidence, recognising assumptions, and forming reasoned conclusions.",
                "keywords": [
                        "critical thinking",
                        "analysis",
                        "judgement",
                        "reasoning",
                        "evaluation",
                        "decision making"
                ],
                "typical_skills": [
                        "apply critical thinking skills",
                        "make informed decisions in the workplace",
                        "analyse and evaluate information",
                        "exercise professional judgement",
                        "assess situations and determine actions",
                        "evaluate alternatives and make recommendations",
                        "apply logical reasoning to workplace tasks",
                        "interpret and assess workplace data",
                        "make decisions within scope of authority"
                ]
        },
        "THA.UNI.TMG": {
                "code": "THA.UNI.TMG",
                "name": "Time Management & Organisation",
                "parent_trf": "TRF.UNI",
                "description": "Planning, prioritising, and managing ones own time and workload effectively.",
                "keywords": [
                        "time management",
                        "planning",
                        "prioritising",
                        "scheduling",
                        "organising",
                        "deadlines"
                ],
                "typical_skills": [
                        "organise personal work priorities and development",
                        "manage own time and priorities",
                        "plan and organise work schedules",
                        "prioritise tasks and manage workload",
                        "meet workplace deadlines and timeframes",
                        "maintain an organised work environment",
                        "schedule work activities and appointments",
                        "manage competing work demands",
                        "plan daily and weekly work activities"
                ]
        },
        "THA.UNI.TWK": {
                "code": "THA.UNI.TWK",
                "name": "Teamwork & Collaboration",
                "parent_trf": "TRF.UNI",
                "description": "Working cooperatively with others toward shared goals.",
                "keywords": [
                        "teamwork",
                        "collaboration",
                        "cooperation",
                        "group work",
                        "team",
                        "working together"
                ],
                "typical_skills": [
                        "work effectively with others",
                        "work in a team environment",
                        "contribute to team effectiveness",
                        "participate in team planning and activities",
                        "support team members to achieve goals",
                        "share information with colleagues",
                        "collaborate across work areas",
                        "build and maintain cooperative relationships",
                        "participate in group decision-making"
                ]
        },
        "THA.UNI.ETH": {
                "code": "THA.UNI.ETH",
                "name": "Workplace Ethics & Professionalism",
                "parent_trf": "TRF.UNI",
                "description": "Demonstrating integrity, responsibility, reliability, and professional conduct.",
                "keywords": [
                        "ethics",
                        "professionalism",
                        "integrity",
                        "responsibility",
                        "conduct",
                        "confidentiality"
                ],
                "typical_skills": [
                        "apply ethical principles in the workplace",
                        "maintain professional conduct and appearance",
                        "follow workplace codes of conduct",
                        "demonstrate workplace values and ethics",
                        "maintain confidentiality of information",
                        "apply workplace privacy requirements",
                        "exercise duty of care",
                        "demonstrate accountability for own work",
                        "recognise and address ethical dilemmas"
                ]
        },
        "THA.UNI.CUL": {
                "code": "THA.UNI.CUL",
                "name": "Cultural Awareness & Inclusion",
                "parent_trf": "TRF.UNI",
                "description": "Recognising and respecting cultural diversity, working effectively with people from different backgrounds.",
                "keywords": [
                        "cultural awareness",
                        "diversity",
                        "inclusion",
                        "respect",
                        "cross-cultural",
                        "indigenous"
                ],
                "typical_skills": [
                        "work with diverse people",
                        "develop cultural competence",
                        "communicate with people from diverse backgrounds",
                        "support Aboriginal and Torres Strait Islander cultural safety",
                        "work respectfully with culturally diverse clients",
                        "apply principles of cultural safety",
                        "address cross-cultural communication challenges",
                        "promote inclusive workplace practices",
                        "recognise and respect cultural differences"
                ]
        },
        "THA.UNI.SLF": {
                "code": "THA.UNI.SLF",
                "name": "Self-Management & Resilience",
                "parent_trf": "TRF.UNI",
                "description": "Managing ones own emotions, stress, and motivation. Includes adaptability and persistence.",
                "keywords": [
                        "self-management",
                        "resilience",
                        "adaptability",
                        "stress management",
                        "motivation",
                        "composure"
                ],
                "typical_skills": [
                        "manage personal stress in the workplace",
                        "demonstrate resilience and adaptability",
                        "maintain personal wellbeing at work",
                        "adapt to changing workplace situations",
                        "manage emotional responses at work",
                        "work effectively under pressure",
                        "demonstrate initiative and enterprise",
                        "develop personal resilience strategies",
                        "maintain motivation and engagement"
                ]
        },
        "THA.UNI.SAF": {
                "code": "THA.UNI.SAF",
                "name": "Personal Safety Awareness",
                "parent_trf": "TRF.UNI",
                "description": "Recognising personal safety risks, following basic safety procedures, using PPE.",
                "keywords": [
                        "safety",
                        "PPE",
                        "hazard",
                        "safe work",
                        "personal protection",
                        "safety awareness"
                ],
                "typical_skills": [
                        "follow safe work practices",
                        "use personal protective equipment",
                        "identify and report hazards",
                        "follow workplace safety procedures",
                        "apply basic safety rules and regulations",
                        "maintain a safe and clean work area",
                        "participate in safety inductions",
                        "respond to workplace safety signs and signals",
                        "apply manual handling techniques",
                        "follow infection control procedures"
                ]
        },
        "THA.BRD.RSK": {
                "code": "THA.BRD.RSK",
                "name": "Risk Assessment & Mitigation",
                "parent_trf": "TRF.BRD",
                "description": "Systematically identifying, evaluating, and controlling risks.",
                "keywords": [
                        "risk assessment",
                        "risk management",
                        "hazard identification",
                        "risk mitigation",
                        "risk matrix",
                        "controls"
                ],
                "typical_skills": [
                        "conduct risk assessments",
                        "identify hazards and assess risks",
                        "apply risk management processes",
                        "develop risk treatment plans",
                        "apply the hierarchy of controls",
                        "complete risk assessment documentation",
                        "monitor and review risk controls",
                        "facilitate risk identification workshops",
                        "evaluate and prioritise risks",
                        "implement risk mitigation strategies"
                ]
        },
        "THA.BRD.LDR": {
                "code": "THA.BRD.LDR",
                "name": "Leadership & People Management",
                "parent_trf": "TRF.BRD",
                "description": "Guiding, motivating, and directing people.",
                "keywords": [
                        "leadership",
                        "management",
                        "supervision",
                        "delegation",
                        "mentoring",
                        "coaching",
                        "performance management"
                ],
                "typical_skills": [
                        "lead and manage team effectiveness",
                        "manage people performance",
                        "provide leadership across the organisation",
                        "supervise and coordinate work activities",
                        "delegate and monitor work tasks",
                        "manage staff performance and development",
                        "mentor and coach individuals",
                        "provide constructive feedback to staff",
                        "manage workforce planning",
                        "develop and implement leadership strategies",
                        "build high-performing teams"
                ]
        },
        "THA.BRD.PRJ": {
                "code": "THA.BRD.PRJ",
                "name": "Project Planning & Coordination",
                "parent_trf": "TRF.BRD",
                "description": "Planning, organising, and coordinating projects or work activities.",
                "keywords": [
                        "project management",
                        "planning",
                        "coordination",
                        "scheduling",
                        "milestones",
                        "deliverables"
                ],
                "typical_skills": [
                        "manage projects",
                        "plan and coordinate project activities",
                        "develop project plans and schedules",
                        "manage project scope and deliverables",
                        "allocate and manage project resources",
                        "monitor project progress and milestones",
                        "coordinate project stakeholders",
                        "manage project risks and issues",
                        "apply project management methodologies",
                        "manage project budgets and timelines"
                ]
        },
        "THA.BRD.QMS": {
                "code": "THA.BRD.QMS",
                "name": "Quality Assurance & Improvement",
                "parent_trf": "TRF.BRD",
                "description": "Monitoring, evaluating, and improving quality of products, services, or processes.",
                "keywords": [
                        "quality",
                        "quality assurance",
                        "quality control",
                        "continuous improvement",
                        "audit",
                        "standards"
                ],
                "typical_skills": [
                        "implement quality assurance processes",
                        "manage quality systems and standards",
                        "conduct quality audits and inspections",
                        "implement continuous improvement programs",
                        "monitor product or service quality",
                        "apply quality management tools and techniques",
                        "identify and correct non-conformances",
                        "facilitate continuous improvement initiatives",
                        "develop quality control procedures",
                        "evaluate quality performance data"
                ]
        },
        "THA.BRD.TRN": {
                "code": "THA.BRD.TRN",
                "name": "Training & Knowledge Transfer",
                "parent_trf": "TRF.BRD",
                "description": "Teaching, instructing, and transferring knowledge or skills to others.",
                "keywords": [
                        "training",
                        "teaching",
                        "instruction",
                        "coaching",
                        "knowledge transfer",
                        "facilitation"
                ],
                "typical_skills": [
                        "deliver training and instruction",
                        "plan and conduct training sessions",
                        "assess competence and performance",
                        "facilitate learning in the workplace",
                        "design training programs and materials",
                        "demonstrate work skills to others",
                        "conduct workplace inductions",
                        "transfer knowledge and skills to team members",
                        "assess and validate learner competence",
                        "develop and deliver presentations for training"
                ]
        },
        "THA.BRD.REG": {
                "code": "THA.BRD.REG",
                "name": "Regulatory Compliance & Governance",
                "parent_trf": "TRF.BRD",
                "description": "Ensuring adherence to laws, regulations, standards, and organisational policies.",
                "keywords": [
                        "compliance",
                        "regulation",
                        "legislation",
                        "governance",
                        "policy",
                        "standards",
                        "legal"
                ],
                "typical_skills": [
                        "ensure compliance with legislation and regulations",
                        "interpret and apply workplace legislation",
                        "manage regulatory compliance requirements",
                        "develop and implement policies and procedures",
                        "conduct compliance audits and reviews",
                        "maintain compliance documentation and records",
                        "advise on legal and regulatory obligations",
                        "apply industry codes of practice",
                        "manage licensing and permit requirements",
                        "implement governance frameworks"
                ]
        },
        "THA.BRD.DAT": {
                "code": "THA.BRD.DAT",
                "name": "Data Analysis & Interpretation",
                "parent_trf": "TRF.BRD",
                "description": "Collecting, organising, analysing, and interpreting data to extract meaningful insights.",
                "keywords": [
                        "data analysis",
                        "statistics",
                        "interpretation",
                        "data collection",
                        "trends",
                        "reporting",
                        "metrics"
                ],
                "typical_skills": [
                        "analyse and present research data",
                        "collect and organise workplace data",
                        "interpret statistical information",
                        "identify trends and patterns in data",
                        "prepare data reports and summaries",
                        "use data analysis tools and software",
                        "apply evidence-based decision making",
                        "develop performance metrics and KPIs",
                        "create data visualisations and dashboards",
                        "evaluate data quality and reliability"
                ]
        },
        "THA.BRD.NEG": {
                "code": "THA.BRD.NEG",
                "name": "Negotiation & Conflict Resolution",
                "parent_trf": "TRF.BRD",
                "description": "Reaching agreements, resolving disputes, and managing conflicting interests.",
                "keywords": [
                        "negotiation",
                        "conflict resolution",
                        "mediation",
                        "dispute",
                        "compromise",
                        "persuasion"
                ],
                "typical_skills": [
                        "manage conflict in the workplace",
                        "negotiate agreements and contracts",
                        "resolve workplace disputes and grievances",
                        "mediate between conflicting parties",
                        "apply negotiation techniques",
                        "manage difficult conversations",
                        "facilitate consensus and agreement",
                        "address and resolve complaints",
                        "manage industrial relations issues"
                ]
        },
        "THA.BRD.CUS": {
                "code": "THA.BRD.CUS",
                "name": "Client & Stakeholder Engagement",
                "parent_trf": "TRF.BRD",
                "description": "Building and maintaining relationships with clients, customers, and stakeholders.",
                "keywords": [
                        "customer service",
                        "client relations",
                        "stakeholder",
                        "engagement",
                        "complaints",
                        "service delivery"
                ],
                "typical_skills": [
                        "deliver and monitor a service to customers",
                        "manage client relationships",
                        "identify and respond to customer needs",
                        "handle customer complaints and feedback",
                        "manage stakeholder engagement",
                        "build and maintain business relationships",
                        "provide quality customer service",
                        "consult with clients and stakeholders",
                        "manage service level agreements",
                        "develop customer engagement strategies"
                ]
        },
        "THA.BRD.RPT": {
                "code": "THA.BRD.RPT",
                "name": "Technical Reporting & Documentation",
                "parent_trf": "TRF.BRD",
                "description": "Preparing accurate technical documentation including reports, specifications, and procedures.",
                "keywords": [
                        "technical writing",
                        "documentation",
                        "reporting",
                        "records",
                        "specifications",
                        "procedures"
                ],
                "typical_skills": [
                        "prepare technical reports and documentation",
                        "write standard operating procedures",
                        "maintain workplace records and registers",
                        "document work activities and outcomes",
                        "prepare specifications and work instructions",
                        "write incident and investigation reports",
                        "develop technical manuals and guides",
                        "maintain asset and maintenance records",
                        "prepare compliance and audit reports",
                        "create process documentation"
                ]
        },
        "THA.BRD.FIN": {
                "code": "THA.BRD.FIN",
                "name": "Financial Management & Budgeting",
                "parent_trf": "TRF.BRD",
                "description": "Managing financial resources including budgeting, cost estimation, and financial reporting.",
                "keywords": [
                        "budget",
                        "finance",
                        "costing",
                        "invoicing",
                        "financial management",
                        "accounting"
                ],
                "typical_skills": [
                        "manage budgets and financial plans",
                        "prepare and monitor budgets",
                        "process financial transactions",
                        "manage accounts payable and receivable",
                        "prepare financial reports and statements",
                        "manage payroll and employee payments",
                        "forecast and monitor expenditure",
                        "develop and manage operational budgets",
                        "apply financial management principles",
                        "maintain financial records and documentation"
                ]
        },
        "THA.BRD.WHS": {
                "code": "THA.BRD.WHS",
                "name": "Workplace Health & Safety Management",
                "parent_trf": "TRF.BRD",
                "description": "Implementing and managing workplace health and safety systems.",
                "keywords": [
                        "WHS",
                        "OHS",
                        "safety management",
                        "incident investigation",
                        "safety audit",
                        "emergency response"
                ],
                "typical_skills": [
                        "manage work health and safety processes",
                        "implement and monitor WHS policies",
                        "investigate workplace incidents and accidents",
                        "conduct workplace safety audits",
                        "develop emergency response procedures",
                        "manage WHS consultation and communication",
                        "monitor and maintain WHS management systems",
                        "coordinate return-to-work programs",
                        "develop and implement safety improvement plans",
                        "manage hazardous substance procedures",
                        "conduct WHS risk management"
                ]
        },
        "THA.BRD.ENV": {
                "code": "THA.BRD.ENV",
                "name": "Environmental & Sustainability Management",
                "parent_trf": "TRF.BRD",
                "description": "Managing environmental impacts and promoting sustainable practices.",
                "keywords": [
                        "environmental",
                        "sustainability",
                        "waste management",
                        "conservation",
                        "recycling",
                        "emissions"
                ],
                "typical_skills": [
                        "implement and monitor environmental policies",
                        "manage waste and recycling systems",
                        "conduct environmental impact assessments",
                        "implement sustainability initiatives",
                        "monitor environmental conditions and compliance",
                        "develop environmental management plans",
                        "manage resource conservation programs",
                        "implement energy efficiency measures",
                        "manage emissions and pollution controls",
                        "promote sustainable work practices"
                ]
        },
        "THA.BRD.PRC": {
                "code": "THA.BRD.PRC",
                "name": "Process Design & Optimisation",
                "parent_trf": "TRF.BRD",
                "description": "Designing, mapping, and improving work processes and workflows.",
                "keywords": [
                        "process improvement",
                        "workflow",
                        "optimisation",
                        "efficiency",
                        "lean",
                        "standardisation"
                ],
                "typical_skills": [
                        "analyse and improve work processes",
                        "develop and implement standard operating procedures",
                        "map and optimise business workflows",
                        "apply lean and continuous improvement methods",
                        "review and streamline operational processes",
                        "design efficient work systems",
                        "implement process standardisation",
                        "evaluate and improve operational efficiency",
                        "develop workflow diagrams and procedures",
                        "manage organisational change for process improvement"
                ]
        },
        "THA.BRD.SCM": {
                "code": "THA.BRD.SCM",
                "name": "Supply Chain & Logistics Coordination",
                "parent_trf": "TRF.BRD",
                "description": "Coordinating the flow of materials, products, and information through supply chains.",
                "keywords": [
                        "supply chain",
                        "logistics",
                        "procurement",
                        "inventory",
                        "warehousing",
                        "distribution"
                ],
                "typical_skills": [
                        "manage procurement and purchasing",
                        "coordinate supply chain operations",
                        "manage inventory and stock levels",
                        "plan and coordinate logistics activities",
                        "manage warehouse and storage operations",
                        "process and track purchase orders",
                        "coordinate goods receipt and dispatch",
                        "manage supplier relationships and contracts",
                        "forecast demand and plan replenishment",
                        "optimise distribution and delivery schedules"
                ]
        },
        "THA.BRD.INN": {
                "code": "THA.BRD.INN",
                "name": "Innovation & Creative Problem Solving",
                "parent_trf": "TRF.BRD",
                "description": "Generating novel ideas, developing creative solutions, and driving innovation.",
                "keywords": [
                        "innovation",
                        "creativity",
                        "design thinking",
                        "ideation",
                        "novel solutions"
                ],
                "typical_skills": [
                        "foster innovation in the workplace",
                        "apply creative problem-solving techniques",
                        "generate and evaluate new ideas",
                        "develop innovative solutions to workplace challenges",
                        "apply design thinking methodology",
                        "prototype and test new concepts",
                        "manage innovation programs and initiatives",
                        "facilitate brainstorming and ideation sessions",
                        "implement new workplace methods and technologies"
                ]
        },
        "THA.BRD.STP": {
                "code": "THA.BRD.STP",
                "name": "Strategic Planning & Decision Making",
                "parent_trf": "TRF.BRD",
                "description": "Developing long-term plans, setting objectives, and making complex decisions.",
                "keywords": [
                        "strategic planning",
                        "strategy",
                        "decision making",
                        "objectives",
                        "policy"
                ],
                "typical_skills": [
                        "develop and implement strategic plans",
                        "make complex business decisions",
                        "set organisational objectives and priorities",
                        "develop and implement business plans",
                        "conduct strategic analysis and planning",
                        "develop organisational policies and strategies",
                        "manage strategic risk and opportunity",
                        "lead strategic change initiatives",
                        "align operational plans with strategic goals"
                ]
        },
        "THA.BRD.CHG": {
                "code": "THA.BRD.CHG",
                "name": "Change Management & Adaptation",
                "parent_trf": "TRF.BRD",
                "description": "Managing and facilitating organisational or procedural change.",
                "keywords": [
                        "change management",
                        "transition",
                        "transformation",
                        "adaptation",
                        "implementation"
                ],
                "typical_skills": [
                        "lead and manage organisational change",
                        "develop and implement change management plans",
                        "manage stakeholder engagement during change",
                        "facilitate organisational transitions",
                        "manage resistance to change",
                        "communicate change initiatives effectively",
                        "implement new systems and processes",
                        "evaluate and sustain change outcomes",
                        "manage organisational restructures"
                ]
        },
        "THA.BRD.INF": {
                "code": "THA.BRD.INF",
                "name": "Information Management & Research",
                "parent_trf": "TRF.BRD",
                "description": "Sourcing, organising, evaluating, and managing information.",
                "keywords": [
                        "research",
                        "information management",
                        "knowledge management",
                        "evidence",
                        "sourcing"
                ],
                "typical_skills": [
                        "manage information and knowledge",
                        "conduct workplace research and investigation",
                        "manage records and information systems",
                        "source and evaluate information",
                        "apply research methodology and techniques",
                        "manage business knowledge and intellectual property",
                        "maintain document control systems",
                        "develop information management procedures",
                        "apply evidence-based practice"
                ]
        },
        "THA.BRD.PRS": {
                "code": "THA.BRD.PRS",
                "name": "Presentation & Public Communication",
                "parent_trf": "TRF.BRD",
                "description": "Delivering information to groups through presentations and public speaking.",
                "keywords": [
                        "presentation",
                        "public speaking",
                        "demonstration",
                        "visual aids",
                        "audience"
                ],
                "typical_skills": [
                        "deliver workplace presentations",
                        "present information to groups and audiences",
                        "prepare and use visual aids and slides",
                        "facilitate workshops and seminars",
                        "deliver public speaking engagements",
                        "communicate persuasively to stakeholders",
                        "conduct product or service demonstrations",
                        "present reports and recommendations to management",
                        "facilitate conference sessions"
                ]
        },
        "THA.SEC.DGN": {
                "code": "THA.SEC.DGN",
                "name": "Design & Drafting",
                "parent_trf": "TRF.SEC",
                "description": "Creating designs, plans, drawings, and specifications.",
                "keywords": [
                        "design",
                        "drafting",
                        "CAD",
                        "drawing",
                        "blueprint",
                        "schematic",
                        "specifications"
                ],
                "typical_skills": [
                        "create technical drawings and plans",
                        "use computer-aided design software",
                        "produce architectural and engineering drawings",
                        "interpret and produce design specifications",
                        "develop construction and manufacturing drawings",
                        "create 3D models and visualisations",
                        "read and interpret technical blueprints",
                        "prepare schematic and wiring diagrams",
                        "develop landscape and site plans",
                        "validate designs against standards"
                ]
        },
        "THA.SEC.INS": {
                "code": "THA.SEC.INS",
                "name": "Inspection & Testing",
                "parent_trf": "TRF.SEC",
                "description": "Examining products, systems, or structures to verify conformance to standards.",
                "keywords": [
                        "inspection",
                        "testing",
                        "examination",
                        "verification",
                        "quality check",
                        "measurement"
                ],
                "typical_skills": [
                        "inspect and test products and components",
                        "conduct visual and dimensional inspections",
                        "perform non-destructive testing",
                        "test electrical installations and circuits",
                        "inspect structures for defects and compliance",
                        "conduct pressure and leak testing",
                        "perform materials testing and analysis",
                        "verify compliance with standards and specifications",
                        "conduct pre-start and pre-use equipment checks",
                        "inspect and test fire protection systems"
                ]
        },
        "THA.SEC.CAL": {
                "code": "THA.SEC.CAL",
                "name": "Calibration & Precision Measurement",
                "parent_trf": "TRF.SEC",
                "description": "Calibrating instruments and making precise measurements.",
                "keywords": [
                        "calibration",
                        "measurement",
                        "precision",
                        "metrology",
                        "tolerance",
                        "instruments"
                ],
                "typical_skills": [
                        "calibrate and maintain measuring instruments",
                        "perform precision measurements",
                        "use micrometers verniers and gauges",
                        "check tolerances and dimensional accuracy",
                        "calibrate process control instruments",
                        "operate coordinate measuring machines",
                        "perform instrument verification and adjustment",
                        "apply measurement uncertainty principles",
                        "maintain calibration records and schedules"
                ]
        },
        "THA.SEC.DIA": {
                "code": "THA.SEC.DIA",
                "name": "Diagnostic Reasoning & Fault Finding",
                "parent_trf": "TRF.SEC",
                "description": "Systematically diagnosing faults, malfunctions, or conditions.",
                "keywords": [
                        "diagnosis",
                        "fault finding",
                        "troubleshooting",
                        "root cause",
                        "symptoms",
                        "diagnostic"
                ],
                "typical_skills": [
                        "diagnose faults in mechanical systems",
                        "troubleshoot electrical and electronic circuits",
                        "conduct systematic fault-finding procedures",
                        "diagnose engine and vehicle malfunctions",
                        "use diagnostic equipment and scan tools",
                        "perform root cause analysis of failures",
                        "diagnose patient or client conditions",
                        "troubleshoot hydraulic and pneumatic systems",
                        "analyse failure modes and effects",
                        "diagnose IT network and system faults"
                ]
        },
        "THA.SEC.PAT": {
                "code": "THA.SEC.PAT",
                "name": "Client & Patient Assessment",
                "parent_trf": "TRF.SEC",
                "description": "Assessing the needs, conditions, or capabilities of clients or patients.",
                "keywords": [
                        "assessment",
                        "patient assessment",
                        "client assessment",
                        "screening",
                        "triage",
                        "needs analysis"
                ],
                "typical_skills": [
                        "assess client needs and circumstances",
                        "conduct patient health assessments",
                        "perform initial intake and screening",
                        "triage patients and prioritise care",
                        "assess client functional capacity",
                        "conduct mental health assessments",
                        "assess learning needs and abilities",
                        "perform skin and condition assessments",
                        "evaluate client eligibility for services",
                        "conduct nutritional and dietary assessments"
                ]
        },
        "THA.SEC.CPL": {
                "code": "THA.SEC.CPL",
                "name": "Care Planning & Case Management",
                "parent_trf": "TRF.SEC",
                "description": "Developing and managing individualised care, treatment, or service plans.",
                "keywords": [
                        "care plan",
                        "case management",
                        "treatment plan",
                        "individual plan",
                        "service plan",
                        "care coordination"
                ],
                "typical_skills": [
                        "develop individualised care plans",
                        "manage case loads and client records",
                        "coordinate client services and referrals",
                        "develop and implement treatment plans",
                        "monitor client progress and outcomes",
                        "review and update care plans",
                        "develop individual support plans",
                        "coordinate multidisciplinary care teams",
                        "manage discharge and transition planning",
                        "set and review client goals"
                ]
        },
        "THA.SEC.MON": {
                "code": "THA.SEC.MON",
                "name": "Monitoring & Surveillance",
                "parent_trf": "TRF.SEC",
                "description": "Continuously observing and monitoring systems, conditions, processes, or environments.",
                "keywords": [
                        "monitoring",
                        "surveillance",
                        "observation",
                        "watch",
                        "tracking",
                        "vital signs",
                        "alarms"
                ],
                "typical_skills": [
                        "monitor patient vital signs and conditions",
                        "operate security and surveillance systems",
                        "monitor process parameters and controls",
                        "conduct security patrols and inspections",
                        "monitor environmental conditions and alarms",
                        "track and monitor equipment performance",
                        "operate SCADA and control room systems",
                        "monitor water quality and treatment processes",
                        "observe and report on client behaviour",
                        "monitor and respond to alarm systems"
                ]
        },
        "THA.SEC.SMP": {
                "code": "THA.SEC.SMP",
                "name": "Sampling & Laboratory Technique",
                "parent_trf": "TRF.SEC",
                "description": "Collecting, preparing, and processing samples using laboratory or field techniques.",
                "keywords": [
                        "sampling",
                        "laboratory",
                        "specimen",
                        "sample preparation",
                        "testing",
                        "analysis"
                ],
                "typical_skills": [
                        "collect and prepare samples for analysis",
                        "perform laboratory tests and analyses",
                        "handle and process biological specimens",
                        "maintain laboratory equipment and supplies",
                        "apply aseptic and contamination control techniques",
                        "conduct soil water and air sampling",
                        "prepare chemical solutions and reagents",
                        "record and report laboratory results",
                        "perform microbiological testing",
                        "calibrate and maintain laboratory instruments"
                ]
        },
        "THA.SEC.SRV": {
                "code": "THA.SEC.SRV",
                "name": "Surveying & Spatial Measurement",
                "parent_trf": "TRF.SEC",
                "description": "Measuring and mapping physical spaces, land, or structures.",
                "keywords": [
                        "surveying",
                        "measurement",
                        "spatial",
                        "GPS",
                        "GIS",
                        "mapping",
                        "site measurement"
                ],
                "typical_skills": [
                        "conduct land and site surveys",
                        "use GPS and total station equipment",
                        "establish survey control and set out works",
                        "collect and process spatial data",
                        "use geographic information systems",
                        "perform levelling and height measurements",
                        "create site maps and boundary plans",
                        "interpret survey data and coordinates",
                        "set out building and construction works"
                ]
        },
        "THA.SEC.EST": {
                "code": "THA.SEC.EST",
                "name": "Estimation & Costing",
                "parent_trf": "TRF.SEC",
                "description": "Estimating quantities, costs, timeframes, and resource requirements.",
                "keywords": [
                        "estimation",
                        "costing",
                        "quantities",
                        "bill of quantities",
                        "material takeoff",
                        "pricing"
                ],
                "typical_skills": [
                        "estimate materials and quantities for projects",
                        "prepare cost estimates and quotations",
                        "calculate material takeoff from plans",
                        "prepare bills of quantities",
                        "estimate project labour and resource costs",
                        "prepare tender documentation and pricing",
                        "calculate job costing and profitability",
                        "estimate timeframes for work activities",
                        "develop project cost forecasts"
                ]
        },
        "THA.SEC.MKT": {
                "code": "THA.SEC.MKT",
                "name": "Marketing & Promotion",
                "parent_trf": "TRF.SEC",
                "description": "Promoting products, services, or ideas to target audiences.",
                "keywords": [
                        "marketing",
                        "promotion",
                        "advertising",
                        "branding",
                        "sales",
                        "market research"
                ],
                "typical_skills": [
                        "develop and implement marketing plans",
                        "conduct market research and analysis",
                        "manage advertising and promotional campaigns",
                        "develop and manage brand identity",
                        "create digital marketing content",
                        "manage social media marketing",
                        "develop sales strategies and targets",
                        "coordinate promotional events and launches",
                        "analyse marketing performance metrics",
                        "develop customer acquisition strategies"
                ]
        },
        "THA.SEC.FDP": {
                "code": "THA.SEC.FDP",
                "name": "Food Preparation & Hygiene",
                "parent_trf": "TRF.SEC",
                "description": "Preparing, cooking, and handling food safely and hygienically.",
                "keywords": [
                        "food preparation",
                        "cooking",
                        "food safety",
                        "hygiene",
                        "HACCP",
                        "kitchen"
                ],
                "typical_skills": [
                        "prepare and cook food items",
                        "apply food safety and hygiene practices",
                        "implement food safety programs and HACCP",
                        "prepare menus and food production plans",
                        "manage kitchen operations and workflow",
                        "prepare food for special dietary requirements",
                        "handle and store food safely",
                        "maintain clean and hygienic food areas",
                        "produce cakes pastries and bakery products",
                        "prepare and present food for service"
                ]
        },
        "THA.SEC.HOS": {
                "code": "THA.SEC.HOS",
                "name": "Hospitality & Service Operations",
                "parent_trf": "TRF.SEC",
                "description": "Managing hospitality service operations.",
                "keywords": [
                        "hospitality",
                        "service",
                        "accommodation",
                        "food service",
                        "beverage",
                        "events"
                ],
                "typical_skills": [
                        "provide food and beverage service",
                        "manage front office and reception operations",
                        "manage accommodation services",
                        "coordinate and manage events",
                        "serve alcoholic and non-alcoholic beverages",
                        "manage gaming operations",
                        "provide concierge and guest services",
                        "manage housekeeping operations",
                        "plan and coordinate functions and events",
                        "operate bar and cellar operations"
                ]
        },
        "THA.SEC.CRE": {
                "code": "THA.SEC.CRE",
                "name": "Creative & Artistic Expression",
                "parent_trf": "TRF.SEC",
                "description": "Applying creative and artistic skills to produce visual, auditory, or performative works.",
                "keywords": [
                        "creative",
                        "artistic",
                        "design",
                        "visual arts",
                        "graphic design",
                        "photography"
                ],
                "typical_skills": [
                        "create visual arts and design works",
                        "produce graphic design and digital media",
                        "capture and edit photographs and video",
                        "perform music and manage audio production",
                        "develop creative concepts and designs",
                        "apply colour theory and composition",
                        "produce illustrations and artwork",
                        "create and manage multimedia content",
                        "develop costume and set designs"
                ]
        },
        "THA.SEC.AGR": {
                "code": "THA.SEC.AGR",
                "name": "Agricultural & Horticultural Practice",
                "parent_trf": "TRF.SEC",
                "description": "Applying knowledge and techniques for growing crops, managing livestock, and maintaining landscapes.",
                "keywords": [
                        "agriculture",
                        "horticulture",
                        "farming",
                        "crops",
                        "livestock",
                        "soil",
                        "planting"
                ],
                "typical_skills": [
                        "plant and maintain crops and pastures",
                        "operate and maintain irrigation systems",
                        "apply fertilisers and soil amendments",
                        "manage pest weed and disease control",
                        "harvest and handle agricultural produce",
                        "maintain turf and landscape areas",
                        "operate farm machinery and equipment",
                        "manage soil health and conservation",
                        "propagate and cultivate plants",
                        "plan and implement crop rotations"
                ]
        },
        "THA.SEC.ANM": {
                "code": "THA.SEC.ANM",
                "name": "Animal Care & Handling",
                "parent_trf": "TRF.SEC",
                "description": "Caring for, handling, and managing animals safely and humanely.",
                "keywords": [
                        "animal care",
                        "animal handling",
                        "animal welfare",
                        "livestock",
                        "veterinary",
                        "feeding"
                ],
                "typical_skills": [
                        "handle and restrain animals safely",
                        "provide basic animal care and husbandry",
                        "monitor animal health and behaviour",
                        "feed and water animals according to requirements",
                        "administer animal health treatments",
                        "manage animal breeding programs",
                        "transport and move livestock safely",
                        "maintain animal housing and enclosures",
                        "provide grooming and hygiene care for animals",
                        "implement animal welfare standards"
                ]
        },
        "THA.SEC.SFT": {
                "code": "THA.SEC.SFT",
                "name": "Software & Systems Development",
                "parent_trf": "TRF.SEC",
                "description": "Developing, configuring, and maintaining software applications and information systems.",
                "keywords": [
                        "software",
                        "programming",
                        "coding",
                        "systems",
                        "database",
                        "IT",
                        "development"
                ],
                "typical_skills": [
                        "develop and maintain software applications",
                        "write and test program code",
                        "configure and manage ICT systems",
                        "administer databases and data storage",
                        "install and support ICT hardware and software",
                        "manage network infrastructure and security",
                        "develop and maintain websites",
                        "manage cloud computing services",
                        "implement cybersecurity measures",
                        "apply software development methodologies"
                ]
        },
        "THA.SEC.SEC": {
                "code": "THA.SEC.SEC",
                "name": "Security & Protective Services",
                "parent_trf": "TRF.SEC",
                "description": "Providing security and protection for people, property, and assets.",
                "keywords": [
                        "security",
                        "protection",
                        "access control",
                        "surveillance",
                        "crowd management"
                ],
                "typical_skills": [
                        "manage security operations and personnel",
                        "conduct security risk assessments",
                        "operate access control and surveillance systems",
                        "manage crowd control and event security",
                        "respond to security incidents and breaches",
                        "conduct security patrols and screening",
                        "coordinate emergency evacuations",
                        "manage protective security arrangements",
                        "investigate security incidents"
                ]
        },
        "THA.OCC.FAB": {
                "code": "THA.OCC.FAB",
                "name": "Material Fabrication & Joining",
                "parent_trf": "TRF.OCC",
                "description": "Cutting, shaping, joining, and finishing materials.",
                "keywords": [
                        "welding",
                        "fabrication",
                        "cutting",
                        "joining",
                        "soldering",
                        "brazing",
                        "metalwork"
                ],
                "typical_skills": [
                        "perform manual metal arc welding",
                        "oxy-fuel cut ferrous metals",
                        "perform MIG MAG welding",
                        "perform TIG welding",
                        "fabricate structural steel components",
                        "cut and shape materials using hand and power tools",
                        "join plastics using thermal techniques",
                        "assemble fabricated components",
                        "apply soldering and brazing techniques",
                        "operate guillotine press brake and rolls"
                ]
        },
        "THA.OCC.ELC": {
                "code": "THA.OCC.ELC",
                "name": "Electrical & Electronic Systems",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, and repairing electrical and electronic systems.",
                "keywords": [
                        "electrical",
                        "electronics",
                        "wiring",
                        "circuits",
                        "control systems",
                        "installation"
                ],
                "typical_skills": [
                        "install and maintain electrical wiring systems",
                        "terminate cables and wiring",
                        "install and test switchboard and control panels",
                        "diagnose and repair electrical circuits",
                        "install and commission programmable controllers",
                        "test and verify electrical installations",
                        "install and maintain lighting systems",
                        "connect and configure control systems",
                        "install and maintain power distribution systems",
                        "repair and maintain electronic equipment"
                ]
        },
        "THA.OCC.MEC": {
                "code": "THA.OCC.MEC",
                "name": "Mechanical Systems & Machinery",
                "parent_trf": "TRF.OCC",
                "description": "Operating, maintaining, and repairing mechanical systems and machinery.",
                "keywords": [
                        "mechanical",
                        "machinery",
                        "engines",
                        "hydraulics",
                        "pneumatics",
                        "maintenance",
                        "repair"
                ],
                "typical_skills": [
                        "service and repair mechanical equipment",
                        "maintain and overhaul engines and motors",
                        "service hydraulic and pneumatic systems",
                        "replace and align mechanical seals and bearings",
                        "perform preventive maintenance on plant equipment",
                        "disassemble inspect and reassemble mechanical components",
                        "maintain pumps and compressors",
                        "operate and maintain conveyor systems",
                        "perform condition monitoring of machinery",
                        "service and repair gearboxes and drive systems"
                ]
        },
        "THA.OCC.PLB": {
                "code": "THA.OCC.PLB",
                "name": "Plumbing & Fluid Systems",
                "parent_trf": "TRF.OCC",
                "description": "Installing, maintaining, and repairing plumbing, gas, and fluid systems.",
                "keywords": [
                        "plumbing",
                        "piping",
                        "drainage",
                        "water supply",
                        "gas fitting",
                        "pipe fitting"
                ],
                "typical_skills": [
                        "install and maintain hot and cold water systems",
                        "install drainage and sanitary plumbing",
                        "install and commission gas appliances",
                        "fabricate and install piping systems",
                        "install and test backflow prevention devices",
                        "lay and connect stormwater drainage",
                        "install and maintain water heating systems",
                        "braze and solder copper piping",
                        "install and maintain irrigation systems",
                        "test and commission plumbing installations"
                ]
        },
        "THA.OCC.BLD": {
                "code": "THA.OCC.BLD",
                "name": "Building & Structural Construction",
                "parent_trf": "TRF.OCC",
                "description": "Constructing, assembling, and erecting building structures.",
                "keywords": [
                        "construction",
                        "building",
                        "carpentry",
                        "bricklaying",
                        "concreting",
                        "formwork",
                        "scaffolding"
                ],
                "typical_skills": [
                        "construct wall and floor frames",
                        "install roof framing and trusses",
                        "lay bricks and blocks to line and level",
                        "erect and dismantle scaffolding",
                        "construct and strip formwork",
                        "pour and finish concrete slabs and footings",
                        "install windows doors and fixtures",
                        "construct timber and steel structures",
                        "install external and internal cladding",
                        "carry out levelling and setting out"
                ]
        },
        "THA.OCC.HVR": {
                "code": "THA.OCC.HVR",
                "name": "HVAC & Refrigeration Systems",
                "parent_trf": "TRF.OCC",
                "description": "Installing, servicing, and repairing HVAC and refrigeration systems.",
                "keywords": [
                        "HVAC",
                        "refrigeration",
                        "air conditioning",
                        "heating",
                        "ventilation",
                        "ductwork"
                ],
                "typical_skills": [
                        "install and commission split system air conditioners",
                        "recover and reclaim refrigerant gases",
                        "service and maintain commercial refrigeration systems",
                        "install ductwork and ventilation systems",
                        "diagnose faults in HVAC systems",
                        "install and service heat pump systems",
                        "perform refrigerant leak testing",
                        "commission and balance air conditioning systems",
                        "service and maintain cooling towers",
                        "install and test controls for HVAC systems"
                ]
        },
        "THA.OCC.VHC": {
                "code": "THA.OCC.VHC",
                "name": "Vehicle Operation & Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Operating, maintaining, and repairing vehicles and mobile equipment.",
                "keywords": [
                        "vehicle",
                        "automotive",
                        "driving",
                        "mechanics",
                        "fleet",
                        "heavy vehicle"
                ],
                "typical_skills": [
                        "service and repair automotive engines",
                        "diagnose and repair vehicle braking systems",
                        "overhaul manual and automatic transmissions",
                        "carry out vehicle inspections and roadworthiness checks",
                        "operate light and heavy vehicles safely",
                        "service and repair vehicle electrical systems",
                        "maintain and repair vehicle steering and suspension",
                        "carry out vehicle body repairs",
                        "manage fleet maintenance schedules",
                        "perform wheel alignment and tyre services"
                ]
        },
        "THA.OCC.CLN": {
                "code": "THA.OCC.CLN",
                "name": "Clinical & Therapeutic Procedures",
                "parent_trf": "TRF.OCC",
                "description": "Performing clinical assessments, therapeutic interventions, and medical procedures.",
                "keywords": [
                        "clinical",
                        "therapeutic",
                        "medical procedures",
                        "wound care",
                        "medication",
                        "physiotherapy",
                        "nursing"
                ],
                "typical_skills": [
                        "administer medications safely",
                        "perform wound care and dressing changes",
                        "provide intravenous therapy and cannulation",
                        "conduct physiotherapy treatment sessions",
                        "perform cardiopulmonary resuscitation",
                        "assist with surgical procedures",
                        "apply occupational therapy interventions",
                        "manage catheter and drainage care",
                        "administer injections and immunisations",
                        "perform clinical observations and vital signs"
                ]
        },
        "THA.OCC.PHA": {
                "code": "THA.OCC.PHA",
                "name": "Pharmaceutical & Chemical Handling",
                "parent_trf": "TRF.OCC",
                "description": "Handling, preparing, dispensing, and managing pharmaceutical products and chemical substances.",
                "keywords": [
                        "pharmaceutical",
                        "chemical",
                        "medication",
                        "dispensing",
                        "hazardous substances",
                        "MSDS"
                ],
                "typical_skills": [
                        "dispense pharmaceutical products",
                        "handle and store hazardous chemicals safely",
                        "prepare and compound medications",
                        "calculate medication dosages",
                        "manage controlled substances and drug registers",
                        "interpret safety data sheets and chemical labels",
                        "manage chemical spill response and cleanup",
                        "store and transport dangerous goods",
                        "apply chemical application techniques",
                        "manage pharmaceutical stock and inventory"
                ]
        },
        "THA.OCC.FIR": {
                "code": "THA.OCC.FIR",
                "name": "Emergency & First Response",
                "parent_trf": "TRF.OCC",
                "description": "Responding to emergencies including fire, medical, rescue, and hazardous situations.",
                "keywords": [
                        "emergency response",
                        "first aid",
                        "CPR",
                        "rescue",
                        "firefighting",
                        "paramedic"
                ],
                "typical_skills": [
                        "provide first aid and emergency response",
                        "perform cardiopulmonary resuscitation CPR",
                        "operate firefighting equipment and extinguishers",
                        "manage emergency evacuations and drills",
                        "respond to hazardous material incidents",
                        "coordinate emergency services and response teams",
                        "perform rescue operations",
                        "provide pre-hospital emergency care",
                        "manage mass casualty and disaster response",
                        "administer emergency oxygen therapy"
                ]
        },
        "THA.OCC.MAC": {
                "code": "THA.OCC.MAC",
                "name": "Machining & Precision Manufacturing",
                "parent_trf": "TRF.OCC",
                "description": "Operating machine tools to shape materials to precise specifications.",
                "keywords": [
                        "machining",
                        "CNC",
                        "turning",
                        "milling",
                        "grinding",
                        "lathe",
                        "toolmaking"
                ],
                "typical_skills": [
                        "operate CNC machining centres",
                        "perform lathe turning operations",
                        "set up and operate milling machines",
                        "perform precision grinding operations",
                        "program CNC machines using G-code",
                        "manufacture tooling jigs and fixtures",
                        "perform thread cutting and boring operations",
                        "operate wire EDM and spark erosion machines",
                        "produce components to engineering specifications",
                        "inspect machined parts using precision instruments"
                ]
        },
        "THA.OCC.SFC": {
                "code": "THA.OCC.SFC",
                "name": "Surface Finishing & Coating",
                "parent_trf": "TRF.OCC",
                "description": "Applying surface treatments, coatings, and finishes to materials.",
                "keywords": [
                        "painting",
                        "coating",
                        "finishing",
                        "polishing",
                        "plating",
                        "powder coating"
                ],
                "typical_skills": [
                        "apply protective coatings and paints",
                        "prepare surfaces for coating and finishing",
                        "apply powder coat and electrostatic finishes",
                        "perform spray painting and colour matching",
                        "apply anti-corrosion treatments",
                        "polish and buff metal surfaces",
                        "perform electroplating and anodising",
                        "apply industrial and decorative floor coatings",
                        "apply timber stains and lacquers",
                        "perform vehicle refinishing and detailing"
                ]
        },
        "THA.OCC.TXL": {
                "code": "THA.OCC.TXL",
                "name": "Textile & Garment Production",
                "parent_trf": "TRF.OCC",
                "description": "Working with textiles and fabrics to produce garments and textile products.",
                "keywords": [
                        "sewing",
                        "textiles",
                        "garment",
                        "pattern making",
                        "fabric",
                        "tailoring"
                ],
                "typical_skills": [
                        "cut and sew garments from patterns",
                        "draft and modify garment patterns",
                        "operate industrial sewing machines",
                        "perform alterations and repairs to garments",
                        "select and prepare fabrics and materials",
                        "produce soft furnishings and curtains",
                        "perform upholstery and re-upholstery",
                        "apply textile printing and dyeing techniques",
                        "construct prototype garments"
                ]
        },
        "THA.OCC.BIO": {
                "code": "THA.OCC.BIO",
                "name": "Biological & Specimen Processing",
                "parent_trf": "TRF.OCC",
                "description": "Handling, processing, and managing biological materials and specimens.",
                "keywords": [
                        "biological",
                        "specimen",
                        "tissue",
                        "sample processing",
                        "cryogenics",
                        "pathology"
                ],
                "typical_skills": [
                        "collect and process biological specimens",
                        "perform histology and tissue processing",
                        "handle and store biological materials safely",
                        "prepare specimens for microscopic examination",
                        "manage cryogenic storage and thawing procedures",
                        "process blood and body fluid samples",
                        "apply biocontainment and biosafety protocols",
                        "perform microbiological culture and identification",
                        "manage specimen tracking and chain of custody",
                        "process semen and reproductive biological materials"
                ]
        },
        "THA.OCC.EQM": {
                "code": "THA.OCC.EQM",
                "name": "Specialist Equipment Maintenance",
                "parent_trf": "TRF.OCC",
                "description": "Maintaining, cleaning, and servicing specialised equipment and instruments.",
                "keywords": [
                        "equipment maintenance",
                        "servicing",
                        "cleaning",
                        "sterilisation",
                        "preventive maintenance"
                ],
                "typical_skills": [
                        "clean and sterilise medical instruments",
                        "perform preventive maintenance on equipment",
                        "maintain and service specialised tools and equipment",
                        "manage equipment maintenance schedules and logs",
                        "perform functional testing of equipment",
                        "clean and maintain firearms and weapons",
                        "service and maintain dental equipment",
                        "manage equipment hygiene and decontamination",
                        "maintain and service laboratory equipment",
                        "service and maintain kitchen and food equipment"
                ]
        },
        "THA.OCC.HVY": {
                "code": "THA.OCC.HVY",
                "name": "Heavy Equipment & Plant Operation",
                "parent_trf": "TRF.OCC",
                "description": "Operating heavy plant and equipment including cranes, excavators, forklifts.",
                "keywords": [
                        "crane",
                        "excavator",
                        "forklift",
                        "earthmoving",
                        "plant operation",
                        "heavy equipment",
                        "rigging"
                ],
                "typical_skills": [
                        "operate forklifts and order pickers",
                        "operate excavators and backhoes",
                        "conduct crane operations and lifting",
                        "perform rigging and slinging of loads",
                        "operate earthmoving and grading equipment",
                        "operate elevated work platforms",
                        "perform dogging and crane signalling",
                        "operate concrete pumps and placing booms",
                        "drive and operate front-end loaders",
                        "operate drilling and piling equipment"
                ]
        },
        "THA.OCC.MAR": {
                "code": "THA.OCC.MAR",
                "name": "Maritime & Vessel Operations",
                "parent_trf": "TRF.OCC",
                "description": "Operating, navigating, and maintaining marine vessels and watercraft.",
                "keywords": [
                        "maritime",
                        "vessel",
                        "navigation",
                        "seamanship",
                        "marine",
                        "boat",
                        "ship"
                ],
                "typical_skills": [
                        "navigate and operate commercial vessels",
                        "perform seamanship and vessel handling",
                        "manage marine cargo loading and discharge",
                        "maintain marine engines and systems",
                        "apply maritime safety and survival procedures",
                        "operate radar and electronic navigation aids",
                        "manage vessel stability and trim",
                        "conduct marine radio communications",
                        "perform anchoring mooring and berthing operations",
                        "maintain vessel hull and deck equipment"
                ]
        },
        "THA.OCC.AVN": {
                "code": "THA.OCC.AVN",
                "name": "Aviation & Aircraft Systems",
                "parent_trf": "TRF.OCC",
                "description": "Operating, maintaining, and managing aircraft and aviation systems.",
                "keywords": [
                        "aviation",
                        "aircraft",
                        "flight",
                        "air traffic",
                        "aircraft maintenance",
                        "avionics"
                ],
                "typical_skills": [
                        "perform aircraft maintenance and inspections",
                        "service aircraft engines and propulsion systems",
                        "maintain avionics and aircraft electrical systems",
                        "conduct pre-flight and post-flight checks",
                        "apply aviation safety and regulatory procedures",
                        "perform aircraft structural repairs",
                        "manage aircraft maintenance documentation",
                        "operate air traffic management systems",
                        "service aircraft landing gear and hydraulics",
                        "manage aviation fuel and ground handling"
                ]
        },
        "THA.OCC.MNG": {
                "code": "THA.OCC.MNG",
                "name": "Mining & Extraction Operations",
                "parent_trf": "TRF.OCC",
                "description": "Performing mining, quarrying, and resource extraction operations.",
                "keywords": [
                        "mining",
                        "extraction",
                        "drilling",
                        "blasting",
                        "ore",
                        "quarrying",
                        "underground"
                ],
                "typical_skills": [
                        "conduct underground mining operations",
                        "perform drilling and blasting operations",
                        "operate ore processing and crushing equipment",
                        "install ground support in underground mines",
                        "conduct open cut mining operations",
                        "manage mine ventilation systems",
                        "operate continuous mining equipment",
                        "manage tailings and waste disposal",
                        "perform geological sampling and logging",
                        "apply mine safety and emergency procedures"
                ]
        },
        "THA.OCC.PCS": {
                "code": "THA.OCC.PCS",
                "name": "Personal Care & Beauty Services",
                "parent_trf": "TRF.OCC",
                "description": "Providing personal care and beauty treatments.",
                "keywords": [
                        "hairdressing",
                        "beauty",
                        "massage",
                        "nail",
                        "skin care",
                        "grooming",
                        "personal care"
                ],
                "typical_skills": [
                        "cut and style hair using various techniques",
                        "apply hair colouring and chemical treatments",
                        "perform facial and skin care treatments",
                        "provide body massage and relaxation therapies",
                        "apply and maintain nail enhancements",
                        "perform waxing and hair removal services",
                        "provide makeup application services",
                        "assess skin conditions and recommend treatments",
                        "manage client consultations and service records",
                        "apply eyelash and brow treatments"
                ]
        },
        "THA.OCC.SPR": {
                "code": "THA.OCC.SPR",
                "name": "Sport & Fitness Instruction",
                "parent_trf": "TRF.OCC",
                "description": "Coaching, instructing, and facilitating sport, fitness, and recreational activities.",
                "keywords": [
                        "sport",
                        "fitness",
                        "coaching",
                        "exercise",
                        "recreation",
                        "training programs"
                ],
                "typical_skills": [
                        "plan and deliver exercise programs",
                        "instruct and coach sport activities",
                        "conduct fitness assessments and testing",
                        "plan and deliver group fitness sessions",
                        "develop athlete training programs",
                        "provide gym floor instruction and supervision",
                        "plan and deliver aquatic programs",
                        "manage sport and recreation facilities",
                        "apply exercise science principles",
                        "coordinate community sport and recreation programs"
                ]
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
