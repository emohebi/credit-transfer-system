"""
Skill granularity converter for VET-University alignment
"""

from collections import defaultdict
import logging
from typing import List, Dict, Set
from sklearn.cluster import AgglomerativeClustering
import numpy as np

logger = logging.getLogger(__name__)


class SkillGranularityConverter:
    """Converts between different skill granularity levels"""
    
    def __init__(self, genai=None, embeddings=None):
        self.genai = genai
        self.embeddings = embeddings
        
        # Skill hierarchy templates
        self.hierarchy_patterns = {
            "technical": {
                "broad": ["software development", "data analysis", "system administration"],
                "specific": ["Python programming", "SQL queries", "Linux commands"]
            },
            "cognitive": {
                "broad": ["problem solving", "critical thinking", "research"],
                "specific": ["debugging code", "hypothesis testing", "literature review"]
            }
        }
    
    def decompose_broad_skill(self, broad_skill: str, context: str = "") -> List[Dict[str, str]]:
        """Decompose broad academic skill into VET-level components"""
        
        if self.genai:
            prompt = f"""
            Decompose the broad skill '{broad_skill}' into 3-5 specific, measurable competencies.
            Context: {context}
            
            Each component should be:
            - Action-oriented (starts with a verb)
            - Observable and measurable
            - At appropriate granularity for hands-on training
            - Directly related to the parent skill
            
            Return as JSON:
            {{
                "components": [
                    {{"name": "specific skill", "relationship": "how it relates to parent"}}
                ]
            }}
            """
            
            result = self.genai.extract_skills_prompt(prompt, "decomposition")
            return result.get("components", [])
        else:
            # Fallback to rule-based decomposition
            return self._rule_based_decomposition(broad_skill)
    
    def aggregate_specific_skills(self, specific_skills: List[str]) -> List[Dict[str, any]]:
        """Aggregate multiple VET skills into broader academic categories"""
        
        if not specific_skills:
            return []
        
        if self.embeddings:
            # Use embeddings for clustering
            skill_embeddings = self.embeddings.encode(specific_skills)
            
            # Hierarchical clustering
            n_clusters = min(5, max(1, len(specific_skills) // 3))
            clustering = AgglomerativeClustering(
                n_clusters=n_clusters,
                metric='cosine',
                linkage='average'
            )
            clusters = clustering.fit_predict(skill_embeddings)
            
            # Group skills by cluster
            clustered_skills = {}
            for skill, cluster_id in zip(specific_skills, clusters):
                if cluster_id not in clustered_skills:
                    clustered_skills[cluster_id] = []
                clustered_skills[cluster_id].append(skill)
            
            # Generate broad categories for each cluster
            broad_categories = []
            for cluster_id, skills in clustered_skills.items():
                if self.genai:
                    category = self._generate_category_name(skills)
                else:
                    category = self._infer_category_name(skills)
                
                broad_categories.append({
                    "category": category,
                    "skills": skills,
                    "confidence": len(skills) / len(specific_skills)
                })
            
            return broad_categories
        else:
            # Fallback to keyword-based grouping
            return self._keyword_based_aggregation(specific_skills)
    
    def _generate_category_name(self, skills: List[str]) -> str:
        """Generate category name using GenAI"""
        if self.genai:
            prompt = f"""
            Generate a concise, broad category name for these skills:
            {', '.join(skills[:10])}
            
            The category should be:
            - 2-4 words maximum
            - Academic/professional level
            - Encompassing all listed skills
            
            Return only the category name.
            """
            response = self.genai.extract_skills_prompt(prompt, "category")
            return response.get("category", "General Skills")
        return "General Skills"
    
    def _rule_based_decomposition(self, broad_skill: str) -> List[Dict[str, str]]:
        """Rule-based fallback for skill decomposition"""
        broad_skill_lower = broad_skill.lower()
        components = []
        
        # Common decomposition patterns
        patterns = {
            "project management": [
                {"name": "project planning and scheduling", "relationship": "planning phase"},
                {"name": "resource allocation and budgeting", "relationship": "resource management"},
                {"name": "risk assessment and mitigation", "relationship": "risk management"},
                {"name": "stakeholder communication", "relationship": "communication aspect"}
            ],
            "data analysis": [
                {"name": "data collection and validation", "relationship": "data preparation"},
                {"name": "statistical analysis techniques", "relationship": "analysis methods"},
                {"name": "data visualization creation", "relationship": "presentation"},
                {"name": "insight interpretation", "relationship": "decision support"}
            ],
            "software development": [
                {"name": "code design and architecture", "relationship": "design phase"},
                {"name": "implementation and testing", "relationship": "development phase"},
                {"name": "debugging and optimization", "relationship": "quality assurance"},
                {"name": "version control and documentation", "relationship": "maintenance"}
            ]
        }
        
        # Find matching pattern
        for pattern_key, pattern_components in patterns.items():
            if pattern_key in broad_skill_lower:
                return pattern_components
        
        # Default decomposition
        return [
            {"name": f"understand {broad_skill} concepts", "relationship": "theoretical foundation"},
            {"name": f"apply {broad_skill} techniques", "relationship": "practical application"},
            {"name": f"evaluate {broad_skill} outcomes", "relationship": "assessment"}
        ]
    
    def _keyword_based_aggregation(self, skills: List[str]) -> List[Dict[str, any]]:
        """Keyword-based fallback for skill aggregation"""
        # Extract common keywords
        keyword_groups = defaultdict(list)
        
        for skill in skills:
            # Simple keyword extraction
            words = skill.lower().split()
            for word in words:
                if len(word) > 4:  # Skip short words
                    keyword_groups[word].append(skill)
        
        # Find most common keywords
        sorted_keywords = sorted(keyword_groups.items(), key=lambda x: len(x[1]), reverse=True)
        
        categories = []
        used_skills = set()
        
        for keyword, related_skills in sorted_keywords[:5]:
            unused_skills = [s for s in related_skills if s not in used_skills]
            if unused_skills:
                categories.append({
                    "category": keyword.capitalize() + " Skills",
                    "skills": unused_skills,
                    "confidence": len(unused_skills) / len(skills)
                })
                used_skills.update(unused_skills)
        
        return categories
    
    def map_granularity_level(self, skill: str) -> str:
        """Determine granularity level of a skill"""
        words = skill.split()
        
        # Heuristic rules
        if len(words) <= 2:
            return "broad"
        elif len(words) <= 4:
            return "intermediate"
        else:
            return "specific"
    
    def calculate_granularity_mismatch(self, vet_skills: List[str], uni_skills: List[str]) -> float:
        """Calculate granularity mismatch between skill sets"""
        vet_levels = [self.map_granularity_level(s) for s in vet_skills]
        uni_levels = [self.map_granularity_level(s) for s in uni_skills]
        
        # Count distribution
        vet_distribution = {
            "broad": vet_levels.count("broad") / len(vet_levels) if vet_levels else 0,
            "intermediate": vet_levels.count("intermediate") / len(vet_levels) if vet_levels else 0,
            "specific": vet_levels.count("specific") / len(vet_levels) if vet_levels else 0
        }
        
        uni_distribution = {
            "broad": uni_levels.count("broad") / len(uni_levels) if uni_levels else 0,
            "intermediate": uni_levels.count("intermediate") / len(uni_levels) if uni_levels else 0,
            "specific": uni_levels.count("specific") / len(uni_levels) if uni_levels else 0
        }
        
        # Calculate KL divergence as mismatch measure
        mismatch = 0
        for level in ["broad", "intermediate", "specific"]:
            if uni_distribution[level] > 0:
                if vet_distribution[level] > 0:
                    mismatch += uni_distribution[level] * np.log(
                        uni_distribution[level] / vet_distribution[level]
                    )
                else:
                    mismatch += 1.0  # Maximum penalty for missing level
        
        return min(1.0, mismatch)