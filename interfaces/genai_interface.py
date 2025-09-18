"""
Interface for local GenAI model integration
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class GenAIInterface:
    """Interface for local GenAI model integration"""
    
    def __init__(self, model_endpoint: str = "http://localhost:8080", 
                 api_key: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize GenAI interface
        
        Args:
            model_endpoint: URL of the local GenAI model
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.endpoint = model_endpoint
        self.api_key = api_key
        self.timeout = timeout
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def extract_skills_prompt(self, text: str, context: str = "course") -> List[Dict]:
        """
        Use GenAI to extract skills from text
        
        Args:
            text: Text to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills as dictionaries
        """
        prompt = self._build_skill_extraction_prompt(text, context)
        
        try:
            response = self._call_genai_api(prompt)
            return self._parse_skill_extraction_response(response)
        except Exception as e:
            logger.warning(f"GenAI API call failed: {e}. Using fallback extraction.")
            return self._fallback_skill_extraction(text)
    
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Use GenAI to analyze similarity between two skills
        
        Args:
            skill1: First skill name
            skill2: Second skill name
            
        Returns:
            Similarity score between 0 and 1
        """
        prompt = f"""
        Analyze the similarity between these two skills:
        Skill 1: {skill1}
        Skill 2: {skill2}
        
        Consider:
        1. Semantic similarity
        2. Required knowledge overlap
        3. Application context similarity
        
        Return a similarity score between 0 and 1.
        """
        
        try:
            response = self._call_genai_api(prompt)
            # Parse similarity score from response
            score_match = re.search(r"(\d+\.?\d*)", response)
            if score_match:
                return min(1.0, max(0.0, float(score_match.group(1))))
            return 0.5  # Default if parsing fails
        except Exception as e:
            logger.warning(f"Similarity analysis failed: {e}")
            return self._fallback_similarity(skill1, skill2)
    
    def identify_implicit_skills(self, text: str, explicit_skills: List[str]) -> List[Dict]:
        """
        Use GenAI to identify implicit skills not explicitly mentioned
        
        Args:
            text: Course/unit description text
            explicit_skills: Already identified explicit skills
            
        Returns:
            List of implicit skills with confidence scores
        """
        prompt = f"""
        Given this course/unit description:
        {text[:1000]}  # Limit text length
        
        And these explicitly mentioned skills:
        {', '.join(explicit_skills[:20])}  # Limit list length
        
        Identify implicit skills that would be required or developed but aren't explicitly mentioned.
        For each implicit skill, provide:
        1. Skill name
        2. Reason for inference
        3. Confidence level (0-1)
        
        Return as JSON list.
        """
        
        try:
            response = self._call_genai_api(prompt)
            return self._parse_implicit_skills_response(response)
        except Exception as e:
            logger.warning(f"Implicit skill identification failed: {e}")
            return []
    
    def _build_skill_extraction_prompt(self, text: str, context: str) -> str:
        """Build prompt for skill extraction"""
        return f"""
        Extract all skills from the following {context} description. 
        For each skill, identify:
        1. Skill name (concise, specific)
        2. Category (technical/cognitive/practical/foundational/professional)
        3. Required proficiency level (novice/beginner/competent/proficient/expert)
        4. Cognitive depth using Bloom's taxonomy (remember/understand/apply/analyze/evaluate/create)
        5. Context (theoretical/practical/hybrid)
        6. Related keywords (list of related terms)
        7. Confidence score (0-1)
        
        Text to analyze:
        {text[:2000]}  # Limit text length for API
        
        Return as JSON list with the following structure:
        [
            {{
                "name": "skill name",
                "category": "category",
                "level": "proficiency level",
                "depth": "cognitive depth",
                "context": "context type",
                "keywords": ["keyword1", "keyword2"],
                "confidence": 0.8
            }}
        ]
        """
    
    def _call_genai_api(self, prompt: str) -> str:
        """
        Make API call to GenAI model
        
        Args:
            prompt: Prompt to send to the model
            
        Returns:
            Model response as string
        """
        try:
            response = self.session.post(
                f"{self.endpoint}/generate",
                json={"prompt": prompt, "max_tokens": 1000},
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response based on your GenAI model's format
            result = response.json()
            return result.get("text", "") or result.get("response", "")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GenAI API request failed: {e}")
            raise
    
    def _parse_skill_extraction_response(self, response: str) -> List[Dict]:
        """Parse skill extraction response from GenAI"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                skills_json = json.loads(json_match.group())
                return self._validate_extracted_skills(skills_json)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse GenAI response as JSON: {e}")
        
        # Fallback to text parsing
        return self._parse_text_response(response)
    
    def _parse_text_response(self, response: str) -> List[Dict]:
        """Parse non-JSON text response"""
        skills = []
        
        # Simple pattern matching for skill extraction
        skill_pattern = r"(?:skill|competency|ability):\s*([^\n,]+)"
        matches = re.findall(skill_pattern, response, re.IGNORECASE)
        
        for match in matches:
            skills.append({
                "name": match.strip(),
                "category": "technical",  # Default
                "level": "competent",     # Default
                "depth": "apply",         # Default
                "context": "hybrid",      # Default
                "keywords": [],
                "confidence": 0.6        # Lower confidence for parsed
            })
        
        return skills
    
    def _validate_extracted_skills(self, skills: List[Dict]) -> List[Dict]:
        """Validate and clean extracted skills"""
        valid_skills = []
        
        valid_categories = ["technical", "cognitive", "practical", "foundational", "professional"]
        valid_levels = ["novice", "beginner", "competent", "proficient", "expert"]
        valid_depths = ["remember", "understand", "apply", "analyze", "evaluate", "create"]
        valid_contexts = ["theoretical", "practical", "hybrid"]
        
        for skill in skills:
            # Validate and set defaults
            if "name" in skill and skill["name"]:
                clean_skill = {
                    "name": skill["name"][:100],  # Limit length
                    "category": skill.get("category", "technical").lower(),
                    "level": skill.get("level", "competent").lower(),
                    "depth": skill.get("depth", "apply").lower(),
                    "context": skill.get("context", "hybrid").lower(),
                    "keywords": skill.get("keywords", [])[:10],  # Limit keywords
                    "confidence": min(1.0, max(0.0, float(skill.get("confidence", 0.8))))
                }
                
                # Validate against allowed values
                if clean_skill["category"] not in valid_categories:
                    clean_skill["category"] = "technical"
                if clean_skill["level"] not in valid_levels:
                    clean_skill["level"] = "competent"
                if clean_skill["depth"] not in valid_depths:
                    clean_skill["depth"] = "apply"
                if clean_skill["context"] not in valid_contexts:
                    clean_skill["context"] = "hybrid"
                
                valid_skills.append(clean_skill)
        
        return valid_skills
    
    def _parse_implicit_skills_response(self, response: str) -> List[Dict]:
        """Parse implicit skills response"""
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return []
    
    def _fallback_skill_extraction(self, text: str) -> List[Dict]:
        """Fallback skill extraction using pattern matching"""
        skills = []
        text_lower = text.lower()
        
        # Pattern-based extraction
        skill_patterns = [
            (r"ability to (\w+[\w\s]+?)(?:[,\.]|$)", "cognitive"),
            (r"competency in (\w+[\w\s]+?)(?:[,\.]|$)", "technical"),
            (r"skills? in (\w+[\w\s]+?)(?:[,\.]|$)", "practical"),
            (r"knowledge of (\w+[\w\s]+?)(?:[,\.]|$)", "foundational"),
            (r"understanding of (\w+[\w\s]+?)(?:[,\.]|$)", "cognitive"),
            (r"experience with (\w+[\w\s]+?)(?:[,\.]|$)", "practical"),
            (r"proficiency in (\w+[\w\s]+?)(?:[,\.]|$)", "technical"),
        ]
        
        for pattern, category in skill_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                skill_name = match.strip()
                if len(skill_name) > 3 and len(skill_name) < 50:  # Basic validation
                    skills.append({
                        "name": skill_name,
                        "category": category,
                        "level": "competent",
                        "depth": "apply",
                        "context": "hybrid",
                        "keywords": [],
                        "confidence": 0.6
                    })
        
        # Remove duplicates
        seen = set()
        unique_skills = []
        for skill in skills:
            if skill["name"] not in seen:
                seen.add(skill["name"])
                unique_skills.append(skill)
        
        return unique_skills[:50]  # Limit to prevent too many false positives
    
    def _fallback_similarity(self, skill1: str, skill2: str) -> float:
        """Fallback similarity calculation using simple string matching"""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        # Exact match
        if skill1_lower == skill2_lower:
            return 1.0
        
        # One contains the other
        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            return 0.8
        
        # Word overlap
        words1 = set(skill1_lower.split())
        words2 = set(skill2_lower.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        jaccard = len(intersection) / len(union) if union else 0.0
        return jaccard
