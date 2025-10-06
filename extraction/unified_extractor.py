"""
Unified skill extractor with backend-agnostic interface
"""

import hashlib
import json
import pickle
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
from utils.prompt_manager import PromptManager
from models.base_models import Skill, UnitOfCompetency, UniCourse
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel

logger = logging.getLogger(__name__)


class UnifiedSkillExtractor:
    """Unified skill extractor supporting both OpenAI and vLLM backends with study level"""
    
    def __init__(self, genai=None, config=None):
        self.genai = genai
        self.config = config or {}
        self.cache = {}
        self.cache_file = Path("cache/skill_extraction_cache.pkl")
        
        
        # Detect backend type
        self.backend_type = self._detect_backend_type()
        self.is_openai = self.backend_type == "openai"
        self.is_vllm = self.backend_type == "vllm"
        
        # Rate limiting for OpenAI
        self.last_request_time = 0
        self.rate_limit_delay = config.get("RATE_LIMIT_DELAY", 1.0) if self.is_openai else 0
        
        # Study level cache
        self.study_level_cache = {}
        
        self.prompt_manager = PromptManager()
        
        logger.info(f"Initialized UnifiedSkillExtractor with backend: {self.backend_type}")
    
    def _detect_backend_type(self) -> str:
        """Detect the backend type from genai interface"""
        if not self.genai:
            return "none"
        
        class_name = self.genai.__class__.__name__
        
        if "OpenAI" in class_name or hasattr(self.genai, 'client'):
            return "openai"
        elif "VLLM" in class_name or hasattr(self.genai, 'llm'):
            return "vllm"
        else:
            return "unknown"
        
    def _get_model_name(self) -> str:
        """Get the model name for cache key generation"""
        if self.is_openai and hasattr(self.genai, 'deployment'):
            return self.genai.deployment
        elif self.is_vllm and hasattr(self.genai, 'model_name'):
            return self.genai.model_name
        else:
            return "unknown"
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting for OpenAI API"""
        if not self.is_openai:
            return
        
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _call_genai(self, prompt: str, system_prompt: str = None) -> str:
        """Call GenAI with appropriate method for backend - DETERMINISTIC"""
        
        self._enforce_rate_limit()
        
        if not system_prompt:
            system_prompt = "You are an expert skill extractor and education level classifier."
        
        # Add deterministic instruction
        system_prompt += "\nIMPORTANT: Be comprehensive and consistent. Extract ALL identifiable skills. List skills in alphabetical order for consistency."
        
        try:
            # Force deterministic settings
            if self.is_openai:
                return self.genai.generate_response(system_prompt, prompt, 
                                                temperature=0.0, top_p=1.0)
            elif self.is_vllm:
                return self.genai.generate_response(system_prompt, prompt)
            else:
                logger.warning("No compatible GenAI method found")
                return "[]"
                
        except Exception as e:
            logger.error(f"GenAI call failed: {e}")
            return "[]"
    
    def extract_skills(self, 
                   items: Union[List, Any],
                   item_type: str = "auto") -> Union[List[Skill], Dict[str, List[Skill]]]:
        """
        Universal extraction method without caching
        """
        # Convert single item to list
        single_item = not isinstance(items, list)
        if single_item:
            items = [items]
        
        # Detect item type
        if item_type == "auto":
            item_type = self._detect_item_type(items[0])
        
        # Process items
        results = {}
        texts_to_process = []
        items_to_process = []
        study_levels_to_process = []
        
        for item in items:
            texts_to_process.append(self._get_item_text(item))
            items_to_process.append(item)
            
            # Get or infer study level
            study_level = self._get_or_infer_study_level(item, item_type)
            study_levels_to_process.append(study_level)
        
        # Process items
        if texts_to_process:
            # Individual processing with study levels
            extracted_skills = []
            for text, study_level, it in zip(texts_to_process, study_levels_to_process, items_to_process):
                skills = self._single_extract(text, item_type, study_level, item=it)
                extracted_skills.append(skills)
            
            # Store results
            for item, skills, study_level in zip(items_to_process, extracted_skills, study_levels_to_process):
                item_code = self._get_item_code(item)
                results[item_code] = skills
                
                # Update item's extracted_skills and study_level
                if hasattr(item, 'extracted_skills'):
                    item.extracted_skills = skills
                if hasattr(item, 'study_level'):
                    item.study_level = study_level
        
        # Return results
        if single_item:
            return results[self._get_item_code(items[0])]
        else:
            return results
    
    def _get_or_infer_study_level(self, item, item_type: str) -> str:
        """Get study level from item or infer it"""
        
        # For University courses, use existing study level or infer
        # if item_type == "University Course" and hasattr(item, 'study_level'):
        #     if item.study_level and item.study_level.lower() != "unknown":
        #         return item.study_level
        
        # For VET or missing study levels, infer from text
        text = self._get_item_text(item)
        
        # First try simple keyword-based inference
        inferred_level = StudyLevel.infer_from_text(text)
        
        # If we have AI available and need more precision, use it
        if self.genai:
            ai_level = self._infer_study_level_with_ai(text, item_type)
            if ai_level:
                inferred_level = ai_level
        
        # Convert enum to string if needed
        if hasattr(inferred_level, 'value'):
            inferred_level = inferred_level.value
        
        logger.info(f"Inferred study level for {self._get_item_code(item)}: {inferred_level}")
        
        return inferred_level
    
    # In the UnifiedSkillExtractor class, update the _single_extract method:

    def _single_extract(self, text: str, item_type: str, study_level: str = None, item = None) -> List[Skill]:
        """Extract skills from single text with deterministic ordering"""
        
        if not self.genai:
            logger.error("No GenAI interface available for extraction")
            return []
        
        # Get standardized extraction prompt
        system_prompt, user_prompt = self.prompt_manager.get_skill_extraction_prompt(
            text=text,
            item_type=item_type,
            study_level=study_level,
            backend_type=self.backend_type
        )
        
        try:
            response = self._call_genai(user_prompt, system_prompt)
            skills_data = self._parse_json_response(response)
            # logger.info(f"{skills_data}")
            # Convert to Skill objects
            skills = []
            seen_names = set()
            
            for skill_dict in skills_data:
                if isinstance(skill_dict, dict):
                    skill_name = skill_dict.get("name", "").lower().strip()
                    
                    # Skip duplicates
                    if skill_name in seen_names:
                        continue
                    
                    seen_names.add(skill_name)
                    skill_dict['code'] = self._get_item_code(item)
                    skill = self._dict_to_skill(skill_dict)
                    
                    # Ensure level is within expected range
                    if study_level:
                        study_enum = StudyLevel.from_string(study_level)
                        expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
                        
                        if skill.level.value < expected_min:
                            skill.level = SkillLevel(expected_min)
                        elif skill.level.value > expected_max:
                            skill.level = SkillLevel(expected_max)
                    
                    # Only include skills with sufficient confidence
                    if skill.confidence >= self.config.get("MIN_CONFIDENCE", 0.7):
                        skills.append(skill)
            
            # Sort skills by name for consistent ordering
            skills.sort(key=lambda s: (s.name.lower(), -s.confidence))
            # Generate descriptions for extracted skills if GenAI is available
            if self.genai and skills:
                try:
                    # Prepare skills with evidence for description generation
                    skills_for_description = []
                    for skill in skills:  # Limit to first 20 for efficiency
                        skill_dict = {
                            'name': skill.name,
                            'category': skill.category.value,
                            'level': skill.level.value,
                            'context': skill.context.value,
                            'evidence': skill.evidence
                        }
                        skills_for_description.append(skill_dict)
                    if self.is_openai:
                        # Get description generation prompt
                        system_prompt, user_prompt = self.prompt_manager.get_skill_description_prompt(
                            skills_with_evidence=skills_for_description,
                            context_type=item_type,
                            backend_type=self.backend_type
                        )
                        
                        # Generate descriptions
                        response = self._call_genai(user_prompt, system_prompt)
                        descriptions_data = self._parse_json_response(response)
                    else:
                        user_prompts = []
                        for skill_dict in skills_for_description:  # Limit to 20 for efficiency
                            system_prompt, user_prompt = self.prompt_manager.get_skill_description_prompt(
                                skills_with_evidence=[skill_dict],
                                context_type=item_type,
                                backend_type=self.backend_type
                            )
                            user_prompts.append(user_prompt)
                        responses = self.genai._generate_batch(system_prompt, user_prompts)
                        descriptions_data = self._parse_json_response(responses)
                    
                    # Map descriptions back to skills
                    if isinstance(descriptions_data, list):
                        description_map = {}
                        for desc_item in descriptions_data:
                            if isinstance(desc_item, dict):
                                skill_name = desc_item.get('name', '').lower().strip()
                                description = desc_item.get('description', '')
                                if skill_name and description:
                                    description_map[skill_name] = description
                        
                        # Update skill objects with descriptions
                        for skill in skills:
                            skill_name_lower = skill.name.lower().strip()
                            if skill_name_lower in description_map:
                                skill.description = description_map[skill_name_lower]
                                logger.debug(f"Added description for skill '{skill.name}': {skill.description[:50]}...")
                    
                    logger.info(f"Generated descriptions for {len([s for s in skills if s.description])} skills")
                    
                except Exception as e:
                    logger.warning(f"Failed to generate skill descriptions: {e}")
            
            # Limit to configured maximum
            max_skills = self.config.get("MAX_SKILLS_PER_UNIT", 100)
            if len(skills) > max_skills:
                skills = skills[:max_skills]
            
            return skills
            
        except Exception as e:
            logger.error(f"Error in skill extraction: {e}")
            return []
            # return self._fallback_extraction(text, study_level)
        
    def _final_deduplication(self, skills: List[Skill]) -> List[Skill]:
        """Final deduplication based on standardized names"""
        
        seen_names = {}
        final_skills = []
        
        for skill in skills:
            std_name = skill.name.lower().strip()
            
            if std_name not in seen_names:
                seen_names[std_name] = skill
                final_skills.append(skill)
            else:
                # Keep the one with higher confidence
                if skill.confidence > seen_names[std_name].confidence:
                    # Remove old one and add new one
                    final_skills = [s for s in final_skills if s.name.lower().strip() != std_name]
                    final_skills.append(skill)
                    seen_names[std_name] = skill
        
        return final_skills
    
    def _infer_study_level_with_ai(self, text: str, item_type: str) -> Optional[str]:
        """Use AI to infer study level from text"""
        
        if not self.genai:
            return None
        
        # Get standardized prompt from PromptManager
        system_prompt, user_prompt = self.prompt_manager.get_study_level_inference_prompt(
            text=text,
            item_type=item_type,
            backend_type=self.backend_type
        )
        
        try:
            response = self._call_genai(user_prompt, system_prompt)
            response = response.strip().lower()
            
            if 'intro' in response:
                return StudyLevel.INTRODUCTORY.value
            elif 'adv' in response:
                return StudyLevel.ADVANCED.value
            else:
                return StudyLevel.INTERMEDIATE.value
                
        except Exception as e:
            logger.warning(f"Failed to infer study level with AI: {e}")
            return None
    
    def _adjust_skill_level_for_study(self, skill_level: int, expected_min: int, expected_max: int) -> int:
        """Adjust SFIA skill level to fit within expected range"""
        
        # Ensure we stay within SFIA bounds (1-7)
        skill_level = max(1, min(7, skill_level))
        expected_min = max(1, min(7, expected_min))
        expected_max = max(1, min(7, expected_max))
        
        # Allow some flexibility (1 level outside range) but respect SFIA bounds
        if skill_level < expected_min - 1:
            return max(1, expected_min)
        elif skill_level > expected_max + 1:
            return min(7, expected_max)
        else:
            return skill_level
    
    def _fallback_extraction(self, text: str, study_level: str = None) -> List[Skill]:
        """Fallback extraction without AI, considering SFIA study level"""
        skills = []
        
        # Determine expected SFIA skill level based on study level
        if study_level:
            study_enum = StudyLevel.from_string(study_level)
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
            default_level = int((expected_min + expected_max) / 2)
        else:
            default_level = 3  # SFIA Level 3 (Apply) as default
        
        # Ensure default level is within SFIA bounds
        default_level = max(1, min(7, default_level))
        
        lines = text.split('\n')
        for line in lines[:20]:
            line = line.strip()
            if len(line) > 10 and len(line) < 200:
                if any(keyword in line.lower() for keyword in 
                    ['ability', 'understand', 'develop', 'apply', 'analyze']):
                    skill = Skill(
                        name=line[:100],
                        category=SkillCategory.TECHNICAL,
                        level=SkillLevel(default_level),
                        context=SkillContext.HYBRID,
                        confidence=0.5,
                        source=f"fallback_{study_level or 'unknown'}"
                    )
                    skills.append(skill)
        
        return skills[:10]
    
    def _parse_batch_response(self, response: str, expected_count: int) -> List[List[Dict]]:
        """Parse batch extraction response"""
        results = []
        
        try:
            data = self._parse_json_response(response)
            
            # Handle format: [{"text_index": 0, "skills": [...]}, ...]
            if isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict) and "skills" in data[0]:
                    # Sort by text_index to ensure correct order
                    sorted_data = sorted(data, key=lambda x: x.get("text_index", 0))
                    for item in sorted_data:
                        results.append(item.get("skills", []))
                else:
                    # Assume it's a list of skill lists
                    results = data
        except Exception as e:
            logger.error(f"Failed to parse batch response: {e}")
        
        # Ensure we have the right number of results
        while len(results) < expected_count:
            results.append([])
        
        return results[:expected_count]
    
    def _generate_keywords(self, skill_name: str, evidence: str = "", category: str = "") -> List[str]:
        """Generate keywords from skill name and evidence if not provided"""
        keywords = []
        
        # Extract words from skill name
        name_words = skill_name.lower().split()
        keywords.extend(name_words)
        
        # Add category as keyword
        if category:
            keywords.append(category.lower())
        
        # Extract key terms from evidence if available
        if evidence:
            # Common important words to look for in evidence
            important_terms = ['analysis', 'management', 'design', 'development', 'planning', 
                            'implementation', 'testing', 'optimization', 'communication',
                            'database', 'software', 'system', 'process', 'strategy',
                            'financial', 'technical', 'business', 'project', 'data']
            
            evidence_lower = evidence.lower()
            for term in important_terms:
                if term in evidence_lower and term not in keywords:
                    keywords.append(term)
        
        # Common skill-related keywords based on skill name patterns
        skill_lower = skill_name.lower()
        if 'data' in skill_lower:
            keywords.extend(['data', 'information', 'analytics'])
        if 'project' in skill_lower:
            keywords.extend(['project', 'planning', 'coordination'])
        if 'communication' in skill_lower:
            keywords.extend(['communication', 'collaboration', 'teamwork'])
        if 'analysis' in skill_lower or 'analytical' in skill_lower:
            keywords.extend(['analysis', 'evaluation', 'assessment'])
        if 'management' in skill_lower or 'manage' in skill_lower:
            keywords.extend(['management', 'leadership', 'coordination'])
        
        # Remove duplicates and limit to 10
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen and len(kw) > 2:  # Skip very short words
                seen.add(kw)
                unique_keywords.append(kw)
                if len(unique_keywords) >= 10:
                    break
        
        return unique_keywords
    
    def _dict_to_skill(self, skill_dict: Dict, study_level: str = None) -> Skill:
        """Convert dictionary to Skill object with description and keywords"""
        
        # Extract keywords - handle both list and string formats
        keywords = skill_dict.get("keywords", [])
        if isinstance(keywords, str):
            # If keywords came as a string, split it
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        elif not isinstance(keywords, list):
            keywords = []
            
        if not keywords:
            keywords = self._generate_keywords(
                skill_dict.get("name", ""),
                skill_dict.get("evidence", ""),
                skill_dict.get("category", "")
            )
        
        # Ensure keywords is a list of strings
        keywords = [str(k) for k in keywords[:10]]  # Limit to 10 keywords
        
        skill = Skill(
            code=skill_dict.get("code", "").strip()[:50],
            name=skill_dict.get("name", "Unknown").strip()[:100],
            description=skill_dict.get("description", "").strip()[:200],
            category=self._map_category(skill_dict.get("category", "technical")),
            level=self._map_level(skill_dict.get("level", 3)),
            context=self._map_context(skill_dict.get("context", "hybrid")),
            confidence=min(1.0, max(0.0, skill_dict.get("confidence", 0.7))),
            keywords=keywords,  # Now properly extracted
            # source=skill_dict.get("source", f"{self.backend_type}_extracted"),
            evidence=skill_dict.get("evidence", "")[:200],
            # translation_rationale=skill_dict.get("level_justification", skill_dict.get("reasoning", ""))[:200]
            # evidence_type=skill_dict.get("evidence_type", "")
        )
        return skill
    
    def _get_cache_key(self, item) -> str:
        """Generate cache key"""
        text = self._get_item_text(item)
        # Include backend type in cache key
        backend_suffix = self.backend_type
        return hashlib.md5(f"{text}_{backend_suffix}".encode()).hexdigest()
    
    def _get_item_code(self, item) -> str:
        """Get item code"""
        if hasattr(item, 'code'):
            return item.code
        return "unknown"
    
    def _get_item_text(self, item) -> str:
        """Get text from item"""
        if hasattr(item, 'get_full_text'):
            return item.get_full_text()
        elif hasattr(item, 'description') and hasattr(item, 'learning_outcomes'):
            return item.description + "\n" + "\n".join(item.learning_outcomes)
        elif hasattr(item, 'description'):
            return item.description
        return str(item)
    
    def _detect_item_type(self, item) -> str:
        """Detect item type"""
        if isinstance(item, UnitOfCompetency):
            return "VET Course"
        elif isinstance(item, UniCourse):
            return "University Course"
        return "unknown"
    
    def _map_category(self, category_str: str) -> SkillCategory:
        """Map to SkillCategory"""
        mapping = {
            "technical": SkillCategory.TECHNICAL,
            "cognitive": SkillCategory.COGNITIVE,
            "practical": SkillCategory.PRACTICAL,
            "foundational": SkillCategory.FOUNDATIONAL,
            "professional": SkillCategory.PROFESSIONAL
        }
        return mapping.get(category_str.lower(), SkillCategory.TECHNICAL)
    
    def _map_level(self, level_val: Union[int, str]) -> SkillLevel:
        """Map to SFIA SkillLevel"""
        if isinstance(level_val, str):
            try:
                level_val = int(level_val)
            except:
                level_val = 3
        
        # Ensure level is within SFIA range (1-7)
        level_val = max(1, min(7, level_val))
        
        level_map = {
            1: SkillLevel.FOLLOW,
            2: SkillLevel.ASSIST,
            3: SkillLevel.APPLY,
            4: SkillLevel.ENABLE,
            5: SkillLevel.ENSURE_ADVISE,
            6: SkillLevel.INITIATE_INFLUENCE,
            7: SkillLevel.SET_STRATEGY
        }
        return level_map.get(level_val, SkillLevel.APPLY)
    
    def _map_context(self, context_str: str) -> SkillContext:
        """Map to SkillContext"""
        mapping = {
            "theoretical": SkillContext.THEORETICAL,
            "practical": SkillContext.PRACTICAL,
            "hybrid": SkillContext.HYBRID
        }
        return mapping.get(context_str.lower(), SkillContext.HYBRID)
    
    def _parse_single_response(self, response: str) -> Any:
        import re
        # pattern = r'[\[\{].*[\]\}]'
        pattern = r'(?:assistantfinal.*?)?(\[\s*\{[^[\]]*\}(?:\s*,\s*\{[^[\]]*\})*\s*\])'
        json_match = re.search(pattern, response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                logger.error(f"Failed to parse JSON from response: {response}")
        return None
           
    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from response"""
        # Handle different response formats
        if isinstance(response, list):
            out_list = []
            for item in response:
                out_single = self._parse_single_response(item)
                if out_single and isinstance(out_single, list):
                    out_list.extend(out_single)
            return out_list
        
        if isinstance(response, dict):
            if "skills" in response:
                return response["skills"]
            return [response]
        
        return self._parse_single_response(response)
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            "backend_type": self.backend_type,
            "is_openai": self.is_openai,
            "is_vllm": self.is_vllm,
            "rate_limit_delay": self.rate_limit_delay if self.is_openai else None,
            "config": {k: v for k, v in self.config.items() if not k.startswith('_')}
        }