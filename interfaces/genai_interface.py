"""
Interface for Azure OpenAI integration
"""

import json
import logging
import re
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class GenAIInterface:
    """Interface for Azure OpenAI integration"""
    
    def __init__(self, 
                 endpoint: Optional[str] = None,
                 deployment: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_version: str = "2025-01-01-preview",
                 timeout: int = 60,
                 max_tokens: int = 4000,
                 temperature: float = 0.0):
        """
        Initialize Azure OpenAI interface
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment: Deployment name (model)
            api_key: Azure OpenAI API key
            api_version: API version
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature
        """
        # Use environment variables as fallback
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "https://ehsaninstance1.openai.azure.com/")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        
        if not self.api_key or self.api_key == "REPLACE_WITH_YOUR_KEY_VALUE_HERE":
            raise ValueError("Azure OpenAI API key is required. Set AZURE_OPENAI_API_KEY environment variable.")
        
        self.api_version = api_version
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
                timeout=self.timeout
            )
            logger.info(f"Azure OpenAI client initialized with endpoint: {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def extract_skills_prompt(self, text: str, context: str = "course") -> List[Dict]:
        """
        Use Azure OpenAI to extract skills from text
        
        Args:
            text: Text to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills as dictionaries
        """
        system_prompt = self._build_skill_extraction_system_prompt()
        user_prompt = self._build_skill_extraction_user_prompt(text, context)
        
        try:
            response = self._call_openai_api(system_prompt, user_prompt)
            return self._parse_skill_extraction_response(response)
        except Exception as e:
            logger.warning(f"Azure OpenAI API call failed: {e}. Using fallback extraction.")
            return self._fallback_skill_extraction(text)
    
    def extract_skills_batch(self, texts: List[str], context: str = "course") -> List[List[Dict]]:
        """
        Extract skills from multiple texts (processes sequentially for now)
        
        Args:
            texts: List of texts to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills for each text
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Processing text {i+1}/{len(texts)}")
            try:
                skills = self.extract_skills_prompt(text, context)
                results.append(skills)
            except Exception as e:
                logger.warning(f"Failed to process text {i+1}: {e}")
                results.append([])
        
        return results
    
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Use Azure OpenAI to analyze similarity between two skills
        
        Args:
            skill1: First skill name
            skill2: Second skill name
            
        Returns:
            Similarity score between 0 and 1
        """
        system_prompt = """You are an expert in skill analysis. Analyze the similarity between two skills and return a score between 0 and 1.

Consider:
1. Semantic similarity
2. Required knowledge overlap
3. Application context similarity

Return ONLY a number between 0 and 1, nothing else."""
        
        user_prompt = f"Skill 1: {skill1}\nSkill 2: {skill2}\n\nSimilarity score:"
        
        try:
            response = self._call_openai_api(system_prompt, user_prompt)
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
        Use Azure OpenAI to identify implicit skills not explicitly mentioned
        
        Args:
            text: Course/unit description text
            explicit_skills: Already identified explicit skills
            
        Returns:
            List of implicit skills with confidence scores
        """
        system_prompt = """You are an expert in skill analysis. Given a course description and explicitly mentioned skills, identify implicit skills that would be required but aren't explicitly stated.

For each implicit skill, provide:
1. Skill name
2. Reason for inference
3. Confidence level (0-1)

Return as JSON list:
[
  {
    "name": "skill name",
    "reason": "why this skill is implied",
    "confidence": 0.6
  }
]"""
        
        user_prompt = f"""Course description: {text[:1000]}

Explicit skills already identified: {', '.join(explicit_skills[:20])}

Identify implicit skills:"""
        
        try:
            response = self._call_openai_api(system_prompt, user_prompt)
            return self._parse_implicit_skills_response(response)
        except Exception as e:
            logger.warning(f"Implicit skill identification failed: {e}")
            return []
    
    def _build_skill_extraction_system_prompt(self) -> str:
        """Build system prompt for skill extraction"""
        return """You are an expert in educational course analysis and skill extraction. Given a course or unit description, extract individual skills, making sure they are generalizable capabilities - not task descriptions.

IMPORTANT: Focus on the underlying skill or ability. If a tool/technology is mentioned, extract the human ability implied by its use (e.g., "Excel" → "spreadsheet data analysis", "Python" → "Python programming").

For each skill, identify:
1. Skill name (concise, specific)
2. Category (technical/cognitive/practical/foundational/professional)
3. Required proficiency level (novice/beginner/competent/proficient/expert)
4. Cognitive depth using Bloom's taxonomy (remember/understand/apply/analyze/evaluate/create)
5. Context (theoretical/practical/hybrid)
6. Related keywords
7. Confidence score (0-1)

Return your answer in strict JSON format:
[
  {
    "name": "skill name",
    "category": "category",
    "level": "proficiency level",
    "depth": "cognitive depth",
    "context": "context type",
    "keywords": ["keyword1", "keyword2"],
    "confidence": 0.8
  }
]

Note: Only output the JSON, do not generate any extra sentences."""
    
    def _build_skill_extraction_user_prompt(self, text: str, context: str) -> str:
        """Build user prompt for skill extraction"""
        return f"Now analyze the following {context}: {text[:2000]}"  # Limit text length
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str) -> str:
        """
        Make API call to Azure OpenAI
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Model response as string
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API request failed: {e}")
            raise
    
    def _parse_skill_extraction_response(self, response: str) -> List[Dict]:
        """Parse skill extraction response from Azure OpenAI"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                skills_json = json.loads(json_match.group())
                return self._validate_extracted_skills(skills_json)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse Azure OpenAI response as JSON: {e}")
        
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