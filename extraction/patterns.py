"""
Extraction patterns and rules for skill identification
"""
"""
Extraction patterns and rules for skill identification
"""

from typing import Dict, List, Set
import re


class ExtractionPatterns:
    """Collection of patterns for skill extraction"""
    
    # Action verb patterns mapped to Bloom's taxonomy levels
    ACTION_VERB_PATTERNS = {
        "remember": ["identify", "list", "name", "recognize", "recall", "define", "describe"],
        "understand": ["explain", "describe", "interpret", "summarize", "classify", "discuss"],
        "apply": ["apply", "demonstrate", "implement", "use", "execute", "solve", "operate"],
        "analyze": ["analyze", "compare", "examine", "investigate", "differentiate", "organize"],
        "evaluate": ["evaluate", "assess", "critique", "justify", "judge", "recommend", "validate"],
        "create": ["create", "design", "develop", "construct", "produce", "formulate", "invent"]
    }
    
    # Skill indicator patterns
    SKILL_PATTERNS = [
        # Explicit skill mentions
        (r"(?:ability|abilities) to (\w+[\w\s]+?)(?:[,\.]|$)", "ability"),
        (r"competenc(?:y|ies) in (\w+[\w\s]+?)(?:[,\.]|$)", "competency"),
        (r"skills? in (\w+[\w\s]+?)(?:[,\.]|$)", "skill"),
        (r"knowledge of (\w+[\w\s]+?)(?:[,\.]|$)", "knowledge"),
        (r"understanding of (\w+[\w\s]+?)(?:[,\.]|$)", "understanding"),
        (r"experience (?:with|in) (\w+[\w\s]+?)(?:[,\.]|$)", "experience"),
        (r"proficiency in (\w+[\w\s]+?)(?:[,\.]|$)", "proficiency"),
        (r"expertise in (\w+[\w\s]+?)(?:[,\.]|$)", "expertise"),
        
        # Learning outcome patterns
        (r"students will (?:be able to |)(\w+[\w\s]+?)(?:[,\.]|$)", "outcome"),
        (r"demonstrate (\w+[\w\s]+?)(?:[,\.]|$)", "demonstrate"),
        (r"develop (\w+[\w\s]+?) skills", "develop"),
        (r"apply (\w+[\w\s]+?) (?:to|in)", "apply"),
        (r"master (\w+[\w\s]+?)(?:[,\.]|$)", "master"),
        
        # Technical skill patterns
        (r"use of (\w+[\w\s]+?) (?:software|tools?|systems?)", "technical"),
        (r"working with (\w+[\w\s]+?)(?:[,\.]|$)", "working"),
        (r"(?:programming|coding) in (\w+)", "programming"),
        (r"(\w+) programming", "programming"),
    ]
    
    # Context indicators
    CONTEXT_INDICATORS = {
        "practical": [
            "hands-on", "laboratory", "workshop", "practical", "project",
            "real-world", "industry", "workplace", "applied", "fieldwork",
            "experiential", "practicum", "internship", "placement"
        ],
        "theoretical": [
            "theory", "concept", "principle", "framework", "model",
            "academic", "research", "analysis", "study", "examination",
            "foundation", "fundamental", "abstract", "scholarly"
        ]
    }
    
    # Technology version patterns
    TECH_VERSION_PATTERNS = {
        "python": r"python\s*(\d+(?:\.\d+)?)",
        "java": r"java\s*(?:se\s*)?(\d+)",
        "javascript": r"(?:javascript|js)\s*(?:es)?(\d+)?",
        "react": r"react(?:\.?js)?\s*(?:v)?(\d+(?:\.\d+)?)",
        "angular": r"angular(?:js)?\s*(?:v)?(\d+)?",
        "node": r"node(?:\.?js)?\s*(?:v)?(\d+(?:\.\d+)?)",
        ".net": r"\.net\s*(?:core\s*)?(?:framework\s*)?(\d+(?:\.\d+)?)",
        "php": r"php\s*(\d+(?:\.\d+)?)",
    }
    
    # Skill categories based on keywords
    CATEGORY_KEYWORDS = {
        "technical": [
            "programming", "software", "hardware", "database", "network",
            "system", "development", "engineering", "technical", "technology",
            "coding", "algorithm", "data structure", "framework", "platform",
            "tool", "language", "stack", "architecture", "infrastructure"
        ],
        "cognitive": [
            "analysis", "problem-solving", "critical thinking", "reasoning",
            "decision-making", "evaluation", "synthesis", "comprehension",
            "interpretation", "assessment", "judgment", "logic", "strategy"
        ],
        "practical": [
            "hands-on", "implementation", "operation", "maintenance",
            "troubleshooting", "repair", "assembly", "installation",
            "configuration", "testing", "debugging", "deployment"
        ],
        "foundational": [
            "fundamental", "basic", "core", "essential", "prerequisite",
            "foundation", "principle", "theory", "concept", "methodology"
        ],
        "professional": [
            "communication", "teamwork", "leadership", "management",
            "presentation", "collaboration", "negotiation", "customer service",
            "project management", "time management", "organization", "ethics"
        ]
    }
    
    # Assessment type indicators
    ASSESSMENT_INDICATORS = {
        "exam": ["exam", "test", "quiz", "examination", "assessment"],
        "project": ["project", "portfolio", "case study", "capstone"],
        "practical": ["practical", "laboratory", "workshop", "demonstration"],
        "presentation": ["presentation", "oral", "viva", "defense"],
        "assignment": ["assignment", "homework", "coursework", "paper", "essay"],
        "group": ["group", "team", "collaborative", "peer"]
    }


class SkillOntology:
    """Domain-specific skill ontology"""
    
    def __init__(self):
        self.ontology = self._build_default_ontology()
        self.inference_rules = self._build_inference_rules()
    
    def _build_default_ontology(self) -> Dict:
        """Build default skill ontology"""
        return {
            "software_development": {
                "programming": {
                    "languages": ["python", "java", "javascript", "c++", "c#", "ruby", "go"],
                    "paradigms": ["oop", "functional", "procedural", "reactive"],
                    "practices": ["testing", "debugging", "version control", "code review"]
                },
                "web_development": {
                    "frontend": ["html", "css", "javascript", "react", "angular", "vue"],
                    "backend": ["node.js", "django", "flask", "spring", "express"],
                    "fullstack": ["mean", "mern", "lamp", "jamstack"]
                },
                "databases": {
                    "relational": ["sql", "mysql", "postgresql", "oracle"],
                    "nosql": ["mongodb", "cassandra", "redis", "elasticsearch"],
                    "concepts": ["normalization", "indexing", "transactions", "replication"]
                }
            },
            "data_science": {
                "analysis": ["statistics", "hypothesis testing", "regression", "clustering"],
                "tools": ["python", "r", "matlab", "sas", "spss"],
                "visualization": ["matplotlib", "seaborn", "tableau", "powerbi", "d3.js"],
                "machine_learning": ["supervised", "unsupervised", "deep learning", "nlp"]
            },
            "engineering": {
                "electrical": ["circuits", "electronics", "power systems", "control systems"],
                "mechanical": ["cad", "thermodynamics", "fluid mechanics", "materials"],
                "civil": ["structural", "geotechnical", "transportation", "hydraulics"],
                "software": ["architecture", "design patterns", "algorithms", "data structures"]
            }
        }
    
    def _build_inference_rules(self) -> Dict:
        """Build skill inference rules"""
        return {
            # If skill A is present, skills B, C, D are likely implied
            "database design": ["sql", "normalization", "er modeling", "data modeling"],
            "web development": ["html", "css", "javascript", "responsive design"],
            "full stack development": ["frontend", "backend", "database", "api design"],
            "project management": ["planning", "risk assessment", "stakeholder communication", "scheduling"],
            "machine learning": ["python", "statistics", "data preprocessing", "model evaluation"],
            "data analysis": ["statistics", "data visualization", "data cleaning", "interpretation"],
            "software testing": ["unit testing", "integration testing", "debugging", "test planning"],
            "system administration": ["linux", "networking", "security", "troubleshooting"],
            "cloud computing": ["aws/azure/gcp", "containerization", "microservices", "devops"],
            "mobile development": ["ios/android", "ui/ux", "api integration", "responsive design"]
        }
    
    def get_implied_skills(self, skill: str) -> List[str]:
        """Get implied skills based on inference rules"""
        skill_lower = skill.lower()
        
        # Direct match
        if skill_lower in self.inference_rules:
            return self.inference_rules[skill_lower]
        
        # Partial match
        for key, implied in self.inference_rules.items():
            if key in skill_lower or skill_lower in key:
                return implied
        
        return []
    
    def categorize_skill(self, skill: str) -> str:
        """Categorize skill based on ontology"""
        skill_lower = skill.lower()
        
        for domain, categories in self.ontology.items():
            for category, items in categories.items():
                if isinstance(items, dict):
                    for subcat, skills in items.items():
                        if any(s in skill_lower for s in skills):
                            return f"{domain}.{category}.{subcat}"
                elif isinstance(items, list):
                    if any(s in skill_lower for s in items):
                        return f"{domain}.{category}"
        
        return "general"


class CompositeSkillDecomposer:
    """Decompose composite skills into component skills"""
    
    DECOMPOSITION_RULES = {
        "project management": [
            "project planning",
            "resource allocation",
            "risk management",
            "stakeholder communication",
            "progress monitoring",
            "project delivery"
        ],
        "software development": [
            "requirements analysis",
            "system design",
            "coding/implementation",
            "testing",
            "debugging",
            "documentation"
        ],
        "data analysis": [
            "data collection",
            "data cleaning",
            "statistical analysis",
            "data visualization",
            "interpretation",
            "reporting"
        ],
        "system maintenance": [
            "system monitoring",
            "troubleshooting",
            "updating/patching",
            "backup management",
            "documentation",
            "user support"
        ],
        "web design": [
            "ui design",
            "ux design",
            "responsive design",
            "accessibility",
            "prototyping",
            "user testing"
        ],
        "network administration": [
            "network configuration",
            "security management",
            "performance monitoring",
            "troubleshooting",
            "documentation",
            "user management"
        ],
        "business analysis": [
            "requirements gathering",
            "process mapping",
            "gap analysis",
            "solution design",
            "stakeholder management",
            "documentation"
        ],
        "quality assurance": [
            "test planning",
            "test case design",
            "test execution",
            "defect tracking",
            "regression testing",
            "test reporting"
        ]
    }
    
    @classmethod
    def decompose(cls, skill_name: str) -> List[str]:
        """
        Decompose a composite skill into components
        
        Args:
            skill_name: Name of the composite skill
            
        Returns:
            List of component skills
        """
        skill_lower = skill_name.lower()
        
        # Direct match
        for composite, components in cls.DECOMPOSITION_RULES.items():
            if composite in skill_lower:
                # Add context from original skill name
                context = skill_lower.replace(composite, "").strip()
                if context:
                    return [f"{comp} ({context})" for comp in components]
                return components
        
        # No decomposition available
        return [skill_name]
    
    @classmethod
    def is_composite(cls, skill_name: str) -> bool:
        """Check if a skill is composite"""
        skill_lower = skill_name.lower()
        return any(composite in skill_lower for composite in cls.DECOMPOSITION_RULES.keys())
