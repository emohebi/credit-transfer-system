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
        
        # Load cache if enabled
        if self.config.get("USE_CACHE", True):
            self._load_cache()
        
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
    
    def _generate_prompt(self, text: str, item_type: str) -> str:
        """Generate extraction prompt optimized for backend"""
        
        if self.is_openai:
            # More detailed prompt for OpenAI
            return f"""
            Analyze this {item_type} text and extract ALL skills comprehensively.
            
            For each skill provide:
            1. name: Clear, concise skill name (3-50 characters)
            2. category: One of [technical, cognitive, practical, foundational, professional]
            3. level: Rate 1-5 where 1=novice, 5=expert
            4. context: One of [theoretical, practical, hybrid]
            5. confidence: Your confidence score (0.0-1.0)
            6. is_explicit: true if directly stated, false if implied
            7. keywords: 3-5 relevant keywords
            
            Requirements:
            - Include both explicit and implicit skills
            - Decompose composite skills
            - Remove duplicates
            - Consider prerequisites
            
            Text: {text[:3000]}
            
            Return ONLY a JSON array of skill objects.
            """
        else:
            # Shorter prompt for vLLM (local models)
            return f"""
            Extract skills from this {item_type} text.
            
            For each skill: name, category (technical/cognitive/practical/foundational/professional), 
            level (1-5), context (theoretical/practical/hybrid), confidence (0-1).
            
            Text: {text[:2000]}
            
            Return JSON array.
            """
    
    def _call_genai(self, prompt: str, system_prompt: str = None) -> str:
        """Call GenAI with appropriate method for backend"""
        
        self._enforce_rate_limit()
        
        if not system_prompt:
            system_prompt = "You are an expert skill extractor and education level classifier."
        
        try:
            # Try unified method first
            if hasattr(self.genai, 'generate_response'):
                return self.genai.generate_response(system_prompt, prompt)
            
            # Fallback to backend-specific methods
            elif self.is_openai and hasattr(self.genai, '_call_openai_api'):
                return self.genai._call_openai_api(system_prompt, prompt)
            
            elif self.is_vllm and hasattr(self.genai, '_generate_with_prompt'):
                return self.genai._generate_with_prompt(system_prompt, prompt)
            
            else:
                logger.warning("No compatible GenAI method found")
                return "[]"
                
        except Exception as e:
            logger.error(f"GenAI call failed: {e}")
            return "[]"
    
    def _batch_call_genai(self, prompts: List[str], system_prompt: str = None) -> List[str]:
        """Batch call GenAI if supported"""
        
        if self.is_vllm and hasattr(self.genai, '_generate_batch'):
            # vLLM batch processing
            return self.genai._generate_batch(
                system_prompt or "You are an expert skill extractor.",
                prompts
            )
        else:
            # Fall back to individual calls
            results = []
            for prompt in prompts:
                results.append(self._call_genai(prompt, system_prompt))
            return results
    
    def extract_skills(self, 
                       items: Union[List, Any],
                       item_type: str = "auto") -> Union[List[Skill], Dict[str, List[Skill]]]:
        """
        Universal extraction method supporting both backends with study level consideration
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
            cache_key = self._get_cache_key(item)
            
            if cache_key in self.cache and self.config.get("USE_CACHE", True):
                results[self._get_item_code(item)] = self.cache[cache_key]
                logger.debug(f"Using cached skills for {self._get_item_code(item)}")
            else:
                texts_to_process.append(self._get_item_text(item))
                items_to_process.append(item)
                
                # Get or infer study level
                study_level = self._get_or_infer_study_level(item, item_type)
                study_levels_to_process.append(study_level)
        
        # Process uncached items
        if texts_to_process:
            if self.genai and len(texts_to_process) > 1 and self.config.get("USE_BATCH", True):
                # Batch processing with study levels
                extracted_skills = self._batch_extract(texts_to_process, item_type, study_levels_to_process)
            else:
                # Individual processing with study levels
                extracted_skills = []
                for text, study_level in zip(texts_to_process, study_levels_to_process):
                    skills = self._single_extract(text, item_type, study_level)
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
                
                # Cache results
                if self.config.get("USE_CACHE", True):
                    cache_key = self._get_cache_key(item)
                    self.cache[cache_key] = skills
                    self.study_level_cache[cache_key] = study_level
        
        # Save cache
        if self.config.get("USE_CACHE", True):
            self._save_cache()
        
        # Return results
        if single_item:
            return results[self._get_item_code(items[0])]
        else:
            return results
    
    def _get_or_infer_study_level(self, item, item_type: str) -> str:
        """Get study level from item or infer it"""
        
        # For University courses, use existing study level or infer
        if item_type == "uni" and hasattr(item, 'study_level'):
            if item.study_level and item.study_level.lower() != "unknown":
                return item.study_level
        
        # Check cache first
        cache_key = self._get_cache_key(item) + "_level"
        if cache_key in self.study_level_cache:
            return self.study_level_cache[cache_key]
        
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
        
        # Cache the result
        self.study_level_cache[cache_key] = inferred_level
        
        logger.debug(f"Inferred study level for {self._get_item_code(item)}: {inferred_level}")
        
        return inferred_level
    
    # In the UnifiedSkillExtractor class, update the _single_extract method:

    def _single_extract(self, text: str, item_type: str, study_level: str = None) -> List[Skill]:
        """Extract skills from single text with built-in standardization"""
        
        if not self.genai:
            return self._fallback_extraction(text, study_level)
        
        # Get standardized extraction prompt (standardization is now embedded)
        system_prompt, user_prompt = self.prompt_manager.get_skill_extraction_prompt(
            text=text,
            item_type=item_type,
            study_level=study_level,
            backend_type=self.backend_type
        )
        
        try:
            response = self._call_genai(user_prompt, system_prompt)
            skills_data = self._parse_json_response(response)
            
            # Convert to Skill objects
            skills = []
            seen_names = set()  # Track seen names for deduplication
            
            for skill_dict in skills_data:
                if isinstance(skill_dict, dict):
                    skill_name = skill_dict.get("name", "").lower().strip()
                    
                    # Skip if we've already seen this exact name
                    if skill_name in seen_names:
                        continue
                    
                    seen_names.add(skill_name)
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
            
            # Limit to configured maximum
            max_skills = self.config.get("MAX_SKILLS_PER_UNIT", 100)
            if len(skills) > max_skills:
                # Sort by confidence and take top N
                skills.sort(key=lambda s: s.confidence, reverse=True)
                skills = skills[:max_skills]
            
            return skills
            
        except Exception as e:
            logger.error(f"Error in skill extraction: {e}")
            return self._fallback_extraction(text, study_level)
        
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
    
    def _batch_extract(self, texts: List[str], item_type: str, study_levels: List[str]) -> List[List[Skill]]:
        """Batch extract skills with study level consideration"""
        
        batch_size = self.config.get("BATCH_SIZE", 8)
        all_results = []
        
        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_levels = study_levels[i:i + batch_size]
            
            if self.is_vllm and len(batch_texts) > 1:
                # Get standardized batch prompt
                system_prompt, user_prompt = self.prompt_manager.get_batch_extraction_prompt(
                    texts=batch_texts,
                    item_type=item_type,
                    study_levels=batch_levels,
                    backend_type=self.backend_type
                )
                
                try:
                    # For batch, we send a single consolidated prompt
                    response = self._call_genai(user_prompt, system_prompt)
                    batch_results = self._parse_batch_response(response, len(batch_texts))
                    
                    # Process each result with level adjustment
                    for idx, skills_data in enumerate(batch_results):
                        skills = []
                        study_level = batch_levels[idx] if idx < len(batch_levels) else None
                        
                        if study_level:
                            study_enum = StudyLevel.from_string(study_level)
                            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
                        else:
                            expected_min, expected_max = 2, 4
                        
                        for s in skills_data:
                            if isinstance(s, dict):
                                skill = self._dict_to_skill(s)
                                
                                # Adjust skill level
                                if study_level:
                                    original_level = skill.level.value
                                    adjusted_level = self._adjust_skill_level_for_study(
                                        original_level, expected_min, expected_max
                                    )
                                    if adjusted_level != original_level:
                                        skill.level = SkillLevel(adjusted_level)
                                        skill.confidence *= 0.95
                                
                                skills.append(skill)
                        
                        all_results.append(skills)
                        
                except Exception as e:
                    logger.error(f"Batch extraction failed: {e}")
                    # Fall back to individual processing
                    for text, study_level in zip(batch_texts, batch_levels):
                        all_results.append(self._single_extract(text, item_type, study_level))
            else:
                # Process individually
                for text, study_level in zip(batch_texts, batch_levels):
                    all_results.append(self._single_extract(text, item_type, study_level))
        
        return all_results
    
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
        """Adjust skill level to fit within expected range"""
        
        # Allow some flexibility (1 level outside range)
        if skill_level < expected_min - 1:
            return expected_min
        elif skill_level > expected_max + 1:
            return expected_max
        else:
            return skill_level
    
    def _fallback_extraction(self, text: str, study_level: str = None) -> List[Skill]:
        """Fallback extraction without AI, considering study level"""
        skills = []
        
        # Determine expected skill level based on study level
        if study_level:
            study_enum = StudyLevel.from_string(study_level)
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
            default_level = int((expected_min + expected_max) / 2)
        else:
            default_level = 3
        
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
    
    def _dict_to_skill(self, skill_dict: Dict) -> Skill:
        """Convert dictionary to Skill object with evidence and rationale"""
        return Skill(
            name=skill_dict.get("name", "Unknown").strip()[:100],
            category=self._map_category(skill_dict.get("category", "technical")),
            level=self._map_level(skill_dict.get("level", 3)),
            context=self._map_context(skill_dict.get("context", "hybrid")),
            confidence=min(1.0, max(0.0, skill_dict.get("confidence", 0.7))),
            keywords=skill_dict.get("keywords", [])[:5],
            source=skill_dict.get("source", f"{self.backend_type}_extracted"),
            evidence=skill_dict.get("evidence", "")[:100],  # Limit to 100 chars
            translation_rationale=skill_dict.get("translation_rationale", "")[:200]  # Limit to 200 chars
        )
    
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
        """Map to SkillLevel"""
        if isinstance(level_val, str):
            try:
                level_val = int(level_val)
            except:
                level_val = 3
        
        level_map = {
            1: SkillLevel.NOVICE,
            2: SkillLevel.ADVANCED_BEGINNER,
            3: SkillLevel.COMPETENT,
            4: SkillLevel.PROFICIENT,
            5: SkillLevel.EXPERT
        }
        return level_map.get(level_val, SkillLevel.COMPETENT)
    
    def _map_context(self, context_str: str) -> SkillContext:
        """Map to SkillContext"""
        mapping = {
            "theoretical": SkillContext.THEORETICAL,
            "practical": SkillContext.PRACTICAL,
            "hybrid": SkillContext.HYBRID
        }
        return mapping.get(context_str.lower(), SkillContext.HYBRID)
    
    def _parse_json_response(self, response: str) -> Any:
        """Parse JSON from response"""
        import re
        
        # Handle different response formats
        if isinstance(response, list):
            return response
        
        if isinstance(response, dict):
            if "skills" in response:
                return response["skills"]
            return [response]
        
        # Extract JSON from string
        json_match = re.search(r'[\[\{].*[\]\}]', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        
        return []
    
    def _load_cache(self):
        """Load cache from disk"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if "timestamp" in cache_data:
                        cache_age = datetime.now() - cache_data["timestamp"]
                        ttl_days = self.config.get("CACHE_TTL_DAYS", 7)
                        if cache_age < timedelta(days=ttl_days):
                            self.cache = cache_data.get("data", {})
                            logger.info(f"Loaded cache with {len(self.cache)} entries")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def _save_cache(self):
        """Save cache to disk including study levels"""
        try:
            self.cache_file.parent.mkdir(exist_ok=True)
            with open(self.cache_file, 'wb') as f:
                pickle.dump({
                    "timestamp": datetime.now(),
                    "data": self.cache,
                    "study_levels": self.study_level_cache
                }, f)
        except Exception as e:
            logger.warning(f"Could not save cache: {e}")
    
    def _load_cache(self):
        """Load cache from disk including study levels"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'rb') as f:
                    cache_data = pickle.load(f)
                    if "timestamp" in cache_data:
                        cache_age = datetime.now() - cache_data["timestamp"]
                        ttl_days = self.config.get("CACHE_TTL_DAYS", 7)
                        if cache_age < timedelta(days=ttl_days):
                            self.cache = cache_data.get("data", {})
                            self.study_level_cache = cache_data.get("study_levels", {})
                            logger.info(f"Loaded cache with {len(self.cache)} entries")
            except Exception as e:
                logger.warning(f"Could not load cache: {e}")
    
    def get_stats(self) -> Dict:
        """Get statistics including study level info"""
        return {
            "cache_entries": len(self.cache),
            "study_level_cache_entries": len(self.study_level_cache),
            "backend_type": self.backend_type,
            "is_openai": self.is_openai,
            "is_vllm": self.is_vllm,
            "rate_limit_delay": self.rate_limit_delay if self.is_openai else None,
            "config": {k: v for k, v in self.config.items() if not k.startswith('_')}
        }