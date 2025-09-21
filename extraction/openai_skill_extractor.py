"""
OpenAI skill extraction using pure Gen AI approach - no patterns
"""

import logging
import time
from typing import List, Dict, Optional, Any
from collections import defaultdict

from models.base_models import Skill, UnitOfCompetency, UniCourse
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel
from interfaces.genai_interface import GenAIInterface
from interfaces.embedding_interface import EmbeddingInterface

logger = logging.getLogger(__name__)


class OpenAISkillExtractor:
    """OpenAI skill extraction using pure Gen AI - no pattern matching"""
    
    def __init__(self, 
                 genai: Optional[GenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 delay_between_requests: float = 1.0):
        """
        Initialize OpenAI skill extractor with Gen AI only approach
        
        Args:
            genai: Azure OpenAI GenAI interface for extraction
            embeddings: Embedding interface for similarity
            delay_between_requests: Delay between API requests to avoid rate limits
        """
        self.genai = genai
        self.embeddings = embeddings
        self.delay_between_requests = delay_between_requests
        
        # Cache for processed texts
        self.cache = {}
        
        # Rate limiting tracking
        self.last_request_time = 0
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """
        Extract skills from VET unit using pure Gen AI
        
        Args:
            unit: VET unit to extract skills from
            
        Returns:
            List of extracted skills
        """
        logger.info(f"Extracting skills from VET unit: {unit.code}")
        
        # Check cache
        cache_key = f"vet_{unit.code}"
        if cache_key in self.cache:
            unit.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        skills = []
        
        # Combine all text sources
        full_text = unit.get_full_text()
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Step 1: Extract skills using Gen AI
        ai_skills = self.genai.extract_skills_prompt(full_text, "VET unit")
        skills.extend(self._convert_ai_skills(ai_skills, f"VET:{unit.code}"))
        logger.debug(f"AI extracted {len(ai_skills)} skills from {unit.code}")
        
        # Step 2: Identify implicit skills
        explicit_skill_names = [s["name"] for s in ai_skills]
        implicit_skills = self.genai.identify_implicit_skills(full_text, explicit_skill_names)
        
        for impl_skill in implicit_skills:
            # Get category from AI and validate it
            category_str = self.genai.categorize_skill(impl_skill["name"], full_text)
            category = self._validate_category(category_str)
            
            skill = Skill(
                name=impl_skill["name"],
                category=category,
                level=SkillLevel.COMPETENT,
                context=SkillContext.HYBRID,
                confidence=impl_skill.get("confidence", 0.6),
                source=f"VET:{unit.code}_implicit"
            )
            skills.append(skill)
        logger.debug(f"Found {len(implicit_skills)} implicit skills in {unit.code}")
        
        # Step 3: Decompose composite skills
        skill_names = [s.name for s in skills]
        composite_result = self.genai.decompose_composite_skills(skill_names)
        
        # Add decomposed components
        for comp_skill in composite_result.get("composite_skills", []):
            if comp_skill.get("is_composite"):
                for component in comp_skill.get("components", []):
                    # Validate and get category
                    category = self._validate_category(component.get("category", "technical"))
                    
                    new_skill = Skill(
                        name=component["name"],
                        category=category,
                        level=SkillLevel.COMPETENT,
                        context=SkillContext.PRACTICAL,  # VET is typically practical
                        confidence=0.7,
                        source=f"VET:{unit.code}_decomposed"
                    )
                    skills.append(new_skill)
        
        # Step 4: Determine context for all skills
        context_result = self.genai.determine_context(full_text)
        primary_context = context_result.get("context_analysis", {}).get("primary_context", "practical")
        
        # Apply context to skills
        for skill in skills:
            if primary_context == "practical":
                skill.context = SkillContext.PRACTICAL
            elif primary_context == "theoretical":
                skill.context = SkillContext.THEORETICAL
            else:
                skill.context = SkillContext.HYBRID
        
        # Step 5: Extract keywords for each skill
        for skill in skills[:20]:  # Limit to avoid too many API calls
            keywords = self.genai.extract_keywords(skill.name, full_text)
            skill.keywords = keywords
        
        # Step 6: Deduplicate skills
        skills = self._deduplicate_skills_with_ai(skills)
        
        # Cache and assign
        self.cache[cache_key] = skills
        unit.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {unit.code} (Gen AI only)")
        return skills
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """
        Extract skills from university course using pure Gen AI
        
        Args:
            course: University course to extract skills from
            
        Returns:
            List of extracted skills
        """
        logger.info(f"Extracting skills from Uni course: {course.code}")
        
        # Check cache
        cache_key = f"uni_{course.code}"
        if cache_key in self.cache:
            course.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        skills = []
        
        # Combine all text sources
        full_text = course.get_full_text()
        
        # Rate limiting
        self._enforce_rate_limit()
        
        # Step 1: Identify study level if not provided
        if not course.study_level or course.study_level == "intermediate":
            study_level_result = self.genai.identify_study_level(full_text)
            course.study_level = study_level_result.get("study_level", "intermediate")
            logger.debug(f"Identified study level: {course.study_level}")
        
        # Step 2: Extract skills using Gen AI
        ai_skills = self.genai.extract_skills_prompt(full_text, "university course")
        skills.extend(self._convert_ai_skills(ai_skills, f"UNI:{course.code}"))
        logger.debug(f"AI extracted {len(ai_skills)} skills from {course.code}")
        
        # Step 3: Analyze prerequisites for foundational skills
        if course.prerequisites:
            prereq_result = self.genai.analyze_prerequisites(course.prerequisites, full_text)
            for prereq in prereq_result.get("prerequisites", []):
                for impl_skill in prereq.get("implied_skills", []):
                    skill = Skill(
                        name=impl_skill["name"],
                        category=SkillCategory.FOUNDATIONAL,
                        level=SkillLevel.from_string(impl_skill.get("level", "competent")),
                        context=SkillContext.THEORETICAL,
                        confidence=0.8,
                        source=f"UNI:{course.code}_prerequisite"
                    )
                    skills.append(skill)
        
        # Step 4: Analyze assessment for skill context
        if course.assessment:
            assessment_result = self.genai.analyze_assessment(course.assessment)
            assessment_context = assessment_result.get("primary_assessment_context", "hybrid")
            
            # Use assessment context to refine skill contexts
            for skill in skills:
                if assessment_context == "practical":
                    skill.context = SkillContext.PRACTICAL
                elif assessment_context == "theoretical":
                    skill.context = SkillContext.THEORETICAL
        
        # Step 5: Identify implicit skills
        explicit_skill_names = [s.name for s in skills]
        implicit_skills = self.genai.identify_implicit_skills(full_text, explicit_skill_names)
        
        for impl_skill in implicit_skills:
            # Get category from AI and validate it
            category_str = self.genai.categorize_skill(impl_skill["name"], full_text)
            category = self._validate_category(category_str)
            
            skill = Skill(
                name=impl_skill["name"],
                category=category,
                level=SkillLevel.COMPETENT,
                context=SkillContext.HYBRID,
                confidence=impl_skill.get("confidence", 0.6),
                source=f"UNI:{course.code}_implicit"
            )
            skills.append(skill)
        
        # Step 6: Adjust skill levels based on study level
        skills_dict = [{"name": s.name, "level": s.level.name} for s in skills]
        level_adjustment = self.genai.adjust_skill_levels(skills_dict, course.study_level, full_text)
        
        for adj_skill in level_adjustment.get("adjusted_skills", []):
            for skill in skills:
                if skill.name == adj_skill["skill_name"]:
                    skill.level = SkillLevel.from_string(adj_skill["adjusted_level"])
                    break
        
        # Step 7: Deduplicate skills
        skills = self._deduplicate_skills_with_ai(skills)
        
        # Cache and assign
        self.cache[cache_key] = skills
        course.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {course.code} (Gen AI only)")
        return skills
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.delay_between_requests:
            sleep_time = self.delay_between_requests - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _validate_category(self, category_str: str) -> SkillCategory:
        """Validate and convert category string to SkillCategory enum"""
        valid_categories = {
            "technical": SkillCategory.TECHNICAL,
            "cognitive": SkillCategory.COGNITIVE,
            "practical": SkillCategory.PRACTICAL,
            "foundational": SkillCategory.FOUNDATIONAL,
            "professional": SkillCategory.PROFESSIONAL
        }
        
        category_lower = category_str.lower().strip()
        
        # Try exact match first
        if category_lower in valid_categories:
            return valid_categories[category_lower]
        
        # Try to find closest match
        for valid_cat in valid_categories:
            if valid_cat in category_lower or category_lower in valid_cat:
                return valid_categories[valid_cat]
        
        # Default to technical if no match
        logger.debug(f"Invalid category '{category_str}' defaulting to 'technical'")
        return SkillCategory.TECHNICAL
    
    def _validate_context(self, context_str: str) -> SkillContext:
        """Validate and convert context string to SkillContext enum"""
        valid_contexts = {
            "theoretical": SkillContext.THEORETICAL,
            "practical": SkillContext.PRACTICAL,
            "hybrid": SkillContext.HYBRID
        }
        
        context_lower = context_str.lower().strip()
        
        if context_lower in valid_contexts:
            return valid_contexts[context_lower]
        
        # Default to hybrid if no match
        logger.debug(f"Invalid context '{context_str}' defaulting to 'hybrid'")
        return SkillContext.HYBRID
    
    def _convert_ai_skills(self, ai_skills: List[Dict], source: str) -> List[Skill]:
        """Convert AI-extracted skills to Skill objects"""
        skills = []
        
        for ai_skill in ai_skills:
            try:
                # Validate and clean the skill name
                skill_name = ai_skill.get("name", "").strip()
                if len(skill_name) < 3 or len(skill_name) > 100:
                    continue
                
                # Validate category and context
                category = self._validate_category(ai_skill.get("category", "technical"))
                context = self._validate_context(ai_skill.get("context", "hybrid"))
                
                skill = Skill(
                    name=skill_name,
                    category=category,
                    level=SkillLevel.from_string(ai_skill.get("level", "competent")),
                    context=context,
                    keywords=ai_skill.get("keywords", [])[:10],
                    confidence=min(1.0, max(0.0, ai_skill.get("confidence", 0.8))),
                    source=source
                )
                skills.append(skill)
            except Exception as e:
                logger.debug(f"Failed to convert AI skill: {e}")
        
        return skills
    
    def _deduplicate_skills_with_ai(self, skills: List[Skill]) -> List[Skill]:
        """Deduplicate skills using Gen AI"""
        if len(skills) <= 1:
            return skills
        
        # Convert skills to dict format for AI
        skills_dict = [
            {
                "name": s.name,
                "category": s.category.value,
                "level": s.level.name,
                "confidence": s.confidence
            }
            for s in skills
        ]
        
        # Use AI to identify duplicates
        dedup_result = self.genai.deduplicate_skills(skills_dict)
        
        # Build merged skills
        final_skills = []
        processed_names = set()
        
        # Process skill groups (duplicates to merge)
        for group in dedup_result.get("skill_groups", []):
            similar_names = [s.lower() for s in group.get("similar_skills", [])]
            merged_name = group.get("merged_name", "")
            
            if merged_name:
                # Find the best skill from the group
                best_skill = None
                best_confidence = 0
                
                for skill in skills:
                    if skill.name.lower() in similar_names:
                        if skill.confidence > best_confidence:
                            best_skill = skill
                            best_confidence = skill.confidence
                        processed_names.add(skill.name.lower())
                
                if best_skill:
                    # Update with merged properties
                    best_skill.name = merged_name
                    # Validate category before setting
                    merged_category = self._validate_category(group.get("merged_category", best_skill.category.value))
                    best_skill.category = merged_category
                    best_skill.level = SkillLevel.from_string(group.get("merged_level", best_skill.level.name))
                    final_skills.append(best_skill)
        
        # Add unique skills
        for skill_name in dedup_result.get("unique_skills", []):
            for skill in skills:
                if skill.name == skill_name and skill.name.lower() not in processed_names:
                    final_skills.append(skill)
                    processed_names.add(skill.name.lower())
        
        # Add any skills not mentioned by AI (fallback)
        for skill in skills:
            if skill.name.lower() not in processed_names:
                final_skills.append(skill)
        
        return final_skills
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        logger.info("Extraction cache cleared")
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about the extraction process"""
        return {
            "cache_size": len(self.cache),
            "delay_between_requests": self.delay_between_requests,
            "last_request_time": self.last_request_time,
            "extraction_mode": "pure_genai_no_patterns",
            "features": [
                "comprehensive_ai_extraction",
                "ai_based_deduplication",
                "ai_study_level_detection",
                "ai_context_determination",
                "ai_skill_categorization",
                "ai_implicit_skill_detection",
                "ai_composite_decomposition",
                "ai_level_adjustment"
            ]
        }