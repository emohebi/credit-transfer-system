"""
Interface for Azure OpenAI integration
Modified to use Gen AI for all pattern matching and extraction tasks
"""

import json
import logging
import re
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from utils.converters import JSONExtraction

logger = logging.getLogger(__name__)


class GenAIInterface:
    """Interface for Azure OpenAI integration - Full Gen AI approach"""
    
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
            temperature: Sampling temperature (0.0 for deterministic)
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
        
        # Import prompts
        from extraction.genai_prompts import GenAIPrompts
        self.prompts = GenAIPrompts()
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None) -> str:
        """
        Make API call to Azure OpenAI
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Override max tokens for this call
            
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
                # max_tokens=max_tokens or self.max_tokens,
                temperature=0.0,  # Always use 0 for consistency
                top_p=1.0,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API request failed: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        try:
            # Try to extract JSON from response
            json_match = JSONExtraction.extract_json_from_text(response)
            if json_match:
                return json.loads(json_match)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        return {}
    
    # Main extraction methods
    
    def extract_skills_prompt(self, text: str, context: str = "course") -> List[Dict]:
        """
        Extract skills from text using Gen AI
        
        Args:
            text: Text to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills as dictionaries
        """
        system_prompt = self.prompts.skill_extraction_prompt()
        user_prompt = f"Context: {context}\n\nText to analyze:\n{text[:3000]}"
        
        response = self._call_openai_api(system_prompt, user_prompt)
        result = self._parse_json_response(response)
        
        return result.get("skills", [])
    
    def identify_study_level(self, course_text: str) -> Dict:
        """Identify study level from course description"""
        system_prompt = self.prompts.study_level_identification_prompt()
        user_prompt = f"Course description:\n{course_text[:2000]}"
        
        response = self._call_openai_api(system_prompt, user_prompt, max_tokens=512)
        return self._parse_json_response(response)
    
    def deduplicate_skills(self, skills: List[Dict]) -> Dict:
        """Deduplicate and merge similar skills"""
        system_prompt = self.prompts.skill_deduplication_prompt()
        skills_json = json.dumps(skills[:50], indent=2)
        user_prompt = f"Skills to analyze:\n{skills_json}"
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def identify_implicit_skills(self, text: str, explicit_skills: List[str]) -> List[Dict]:
        """Identify implicit skills not explicitly mentioned"""
        system_prompt = self.prompts.implicit_skill_identification_prompt()
        user_prompt = f"""Course content: {text[:1500]}

Explicit skills already identified: {', '.join(explicit_skills[:20])}"""
        
        response = self._call_openai_api(system_prompt, user_prompt)
        result = self._parse_json_response(response)
        return result.get("implicit_skills", [])
    
    def decompose_composite_skills(self, skills: List[str]) -> Dict:
        """Decompose composite skills into components"""
        system_prompt = self.prompts.composite_skill_decomposition_prompt()
        user_prompt = f"Skills to analyze:\n{json.dumps(skills[:30], indent=2)}"
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def adjust_skill_levels(self, skills: List[Dict], study_level: str, course_text: str) -> Dict:
        """Adjust skill levels based on context"""
        system_prompt = self.prompts.skill_level_adjustment_prompt()
        user_prompt = f"""Study level: {study_level}
Course context: {course_text[:1000]}
Skills to adjust: {json.dumps(skills[:30], indent=2)}"""
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def determine_context(self, text: str) -> Dict:
        """Determine theoretical vs practical context"""
        system_prompt = self.prompts.context_determination_prompt()
        user_prompt = f"Text to analyze:\n{text[:2000]}"
        
        response = self._call_openai_api(system_prompt, user_prompt, max_tokens=512)
        return self._parse_json_response(response)
    
    def extract_technology_versions(self, text: str) -> Dict:
        """Extract technology versions and assess currency"""
        system_prompt = self.prompts.technology_version_extraction_prompt()
        user_prompt = f"Text to analyze:\n{text[:2000]}"
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def analyze_prerequisites(self, prerequisites: List[str], course_text: str) -> Dict:
        """Analyze prerequisites and dependencies"""
        system_prompt = self.prompts.prerequisite_analysis_prompt()
        user_prompt = f"""Prerequisites: {', '.join(prerequisites)}
Course context: {course_text[:1000]}"""
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Analyze similarity between two skills
        
        Args:
            skill1: First skill name
            skill2: Second skill name
            
        Returns:
            Similarity score between 0 and 1
        """
        system_prompt = self.prompts.skill_similarity_prompt()
        user_prompt = f"Skill 1: {skill1}\nSkill 2: {skill2}"
        
        response = self._call_openai_api(system_prompt, user_prompt, max_tokens=256)
        result = self._parse_json_response(response)
        return result.get("similarity_score", 0.5)
    
    def detect_edge_cases(self, vet_text: str, uni_text: str, mapping_info: Dict) -> Dict:
        """Detect edge cases in credit mapping"""
        system_prompt = self.prompts.edge_case_detection_prompt()
        user_prompt = f"""VET content: {vet_text[:1000]}
University content: {uni_text[:1000]}
Mapping summary: {json.dumps(mapping_info, indent=2)}"""
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def extract_keywords(self, skill_name: str, context_text: str) -> List[str]:
        """Extract relevant keywords for a skill"""
        system_prompt = self.prompts.keyword_extraction_prompt()
        user_prompt = f"Skill: {skill_name}\nContext: {context_text[:500]}"
        
        response = self._call_openai_api(system_prompt, user_prompt, max_tokens=256)
        result = self._parse_json_response(response)
        return result.get("keywords", [])
    
    def analyze_assessment(self, assessment_text: str) -> Dict:
        """Analyze assessment methods"""
        system_prompt = self.prompts.assessment_type_analysis_prompt()
        user_prompt = f"Assessment description:\n{assessment_text[:1500]}"
        
        response = self._call_openai_api(system_prompt, user_prompt)
        return self._parse_json_response(response)
    
    def categorize_skill(self, skill_name: str, context: str = "") -> str:
        """Categorize a skill"""
        system_prompt = self.prompts.skill_categorization_prompt()
        user_prompt = f"Skill to categorize: {skill_name}\nContext: {context[:200]}"
        
        response = self._call_openai_api(system_prompt, user_prompt, max_tokens=256)
        result = self._parse_json_response(response)
        return result.get("category", "technical")
    
    def _validate_and_parse_json(self, response: str, schema_type: str = "skills") -> Dict:
        """Strictly validate JSON response against schema"""
        import jsonschema
        
        schemas = {
            "skills": {
                "type": "object",
                "properties": {
                    "skills": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "minLength": 3, "maxLength": 50},
                                "category": {"enum": ["technical", "cognitive", "practical", "foundational", "professional"]},
                                "level": {"enum": ["novice", "beginner", "competent", "proficient", "expert"]},
                                "context": {"enum": ["theoretical", "practical", "hybrid"]},
                                "keywords": {"type": "array", "items": {"type": "string"}, "minItems": 3, "maxItems": 10},
                                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                                "evidence": {"type": "string", "maxLength": 100}
                            },
                            "required": ["name", "category", "level", "context", "confidence"]
                        }
                    }
                },
                "required": ["skills"]
            }
        }
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                jsonschema.validate(instance=data, schema=schemas[schema_type])
                return data
        except (json.JSONDecodeError, jsonschema.ValidationError) as e:
            logger.warning(f"JSON validation failed: {e}")
            # Fallback to original parser
            return self._parse_json_response(response)

    def generate_response(self, system_prompt: str, user_prompt: str, max_tokens: int = None) -> str:
        """
        Unified method for generating responses
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Maximum tokens for response
            
        Returns:
            Generated text response
        """
        return self._call_openai_api(system_prompt, user_prompt, max_tokens)