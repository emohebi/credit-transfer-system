"""
Advanced skill extraction from course descriptions using pure Gen AI
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict

from models.base_models import Skill, UnitOfCompetency, UniCourse
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel
from interfaces.genai_interface import GenAIInterface
from interfaces.embedding_interface import EmbeddingInterface

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Advanced skill extraction using pure Gen AI approach"""
    
    def __init__(self, 
                 genai: Optional[GenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 use_genai: bool = True):
        """
        Initialize skill extractor with Gen AI only approach
        
        Args:
            genai: GenAI interface for advanced extraction
            embeddings: Embedding interface for similarity
            use_genai: Whether to use GenAI for extraction
        """
        self.genai = genai
        self.embeddings = embeddings
        self.use_genai = use_genai and genai is not None
        
        # Cache for processed texts
        self.cache = {}
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """
        Extract skills from VET unit using Gen AI
        
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
        
        if self.use_genai:
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
                    context=SkillContext.PRACTICAL,
                    confidence=impl_skill.get("confidence", 0.6),
                    source=f"VET:{unit.code}_implicit"
                )
                skills.append(skill)
            
            # Step 3: Handle composite skills
            skill_names = [s.name for s in skills]
            composite_result = self.genai.decompose_composite_skills(skill_names)
            
            for comp_skill in composite_result.get("composite_skills", []):
                if comp_skill.get("is_composite"):
                    for component in comp_skill.get("components", []):
                        # Validate category
                        category = self._validate_category(component.get("category", "technical"))
                        
                        new_skill = Skill(
                            name=component["name"],
                            category=category,
                            level=SkillLevel.COMPETENT,
                            context=SkillContext.PRACTICAL,
                            confidence=0.7,
                            source=f"VET:{unit.code}_decomposed"
                        )
                        skills.append(new_skill)
            
            # Step 4: Determine context
            context_result = self.genai.determine_context(full_text)
            primary_context = context_result.get("context_analysis", {}).get("primary_context", "practical")
            
            for skill in skills:
                if primary_context == "practical":
                    skill.context = SkillContext.PRACTICAL
                elif primary_context == "theoretical":
                    skill.context = SkillContext.THEORETICAL
                else:
                    skill.context = SkillContext.HYBRID
            
            # Step 5: Deduplicate skills
            skills = self._deduplicate_skills_with_ai(skills)
        
        else:
            # Fallback: Create minimal skills from learning outcomes
            logger.warning(f"No GenAI available, using minimal extraction for {unit.code}")
            for outcome in unit.learning_outcomes[:5]:  # Limit to avoid too many
                skill = Skill(
                    name=self._clean_text(outcome)[:50],
                    category=SkillCategory.TECHNICAL,
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.PRACTICAL,
                    confidence=0.5,
                    source=f"VET:{unit.code}_fallback"
                )
                skills.append(skill)
        
        # Cache and assign
        self.cache[cache_key] = skills
        unit.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {unit.code}")
        return skills
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """
        Extract skills from university course using Gen AI
        
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
        
        if self.use_genai:
            # Step 1: Identify study level
            if not course.study_level or course.study_level == "intermediate":
                study_level_result = self.genai.identify_study_level(full_text)
                course.study_level = study_level_result.get("study_level", "intermediate")
            
            # Step 2: Extract skills using Gen AI
            ai_skills = self.genai.extract_skills_prompt(full_text, "university course")
            skills.extend(self._convert_ai_skills(ai_skills, f"UNI:{course.code}"))
            logger.debug(f"AI extracted {len(ai_skills)} skills from {course.code}")
            
            # Step 3: Analyze prerequisites
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
            
            # Step 4: Analyze assessment context
            if course.assessment:
                assessment_result = self.genai.analyze_assessment(course.assessment)
                assessment_context = assessment_result.get("primary_assessment_context", "hybrid")
                
                for skill in skills:
                    if assessment_context == "practical" and skill.context == SkillContext.THEORETICAL:
                        skill.context = SkillContext.HYBRID
            
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
            
            # Step 6: Adjust skill levels
            skills_dict = [{"name": s.name, "level": s.level.name} for s in skills]
            level_adjustment = self.genai.adjust_skill_levels(skills_dict, course.study_level, full_text)
            
            for adj_skill in level_adjustment.get("adjusted_skills", []):
                for skill in skills:
                    if skill.name == adj_skill["skill_name"]:
                        skill.level = SkillLevel.from_string(adj_skill["adjusted_level"])
                        break
            
            # Step 7: Deduplicate skills
            skills = self._deduplicate_skills_with_ai(skills)
        
        else:
            # Fallback: Create minimal skills from learning outcomes
            logger.warning(f"No GenAI available, using minimal extraction for {course.code}")
            for outcome in course.learning_outcomes[:5]:
                skill = Skill(
                    name=self._clean_text(outcome)[:50],
                    category=SkillCategory.TECHNICAL,
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.THEORETICAL,
                    confidence=0.5,
                    source=f"UNI:{course.code}_fallback"
                )
                skills.append(skill)
            
            # Add skills from topics
            for topic in course.topics[:5]:
                skill = Skill(
                    name=self._clean_text(topic)[:50],
                    category=SkillCategory.TECHNICAL,
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.THEORETICAL,
                    confidence=0.5,
                    source=f"UNI:{course.code}_topic"
                )
                skills.append(skill)
        
        # Cache and assign
        self.cache[cache_key] = skills
        course.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {course.code}")
        return skills
    
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
        
        if category_lower in valid_categories:
            return valid_categories[category_lower]
        
        # Try to find closest match
        for valid_cat in valid_categories:
            if valid_cat in category_lower or category_lower in valid_cat:
                return valid_categories[valid_cat]
        
        # Default to technical
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
        
        # Default to hybrid
        logger.debug(f"Invalid context '{context_str}' defaulting to 'hybrid'")
        return SkillContext.HYBRID
    
    def _convert_ai_skills(self, ai_skills: List[Dict], source: str) -> List[Skill]:
        """Convert AI-extracted skills to Skill objects"""
        skills = []
        
        for ai_skill in ai_skills:
            try:
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
        
        if not self.genai:
            # Simple deduplication without AI
            return self._simple_deduplicate(skills)
        
        # Convert skills for AI
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
        
        # Process skill groups
        for group in dedup_result.get("skill_groups", []):
            similar_names = [s.lower() for s in group.get("similar_skills", [])]
            merged_name = group.get("merged_name", "")
            
            if merged_name:
                best_skill = None
                best_confidence = 0
                
                for skill in skills:
                    if skill.name.lower() in similar_names:
                        if skill.confidence > best_confidence:
                            best_skill = skill
                            best_confidence = skill.confidence
                        processed_names.add(skill.name.lower())
                
                if best_skill:
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
        
        # Add any remaining skills
        for skill in skills:
            if skill.name.lower() not in processed_names:
                final_skills.append(skill)
        
        return final_skills
    
    def _simple_deduplicate(self, skills: List[Skill]) -> List[Skill]:
        """Simple deduplication without AI"""
        skill_dict = {}
        
        for skill in skills:
            key = skill.name.lower().strip()
            
            if key not in skill_dict:
                skill_dict[key] = skill
            else:
                # Keep the one with higher confidence
                if skill.confidence > skill_dict[key].confidence:
                    skill_dict[key] = skill
        
        return list(skill_dict.values())
    
    def _clean_text(self, text: str) -> str:
        """Clean text for skill name"""
        text = " ".join(text.split())  # Remove extra whitespace
        text = text.strip()
        
        # Remove common prefixes
        prefixes = ["ability to", "knowledge of", "understanding of", "skills in"]
        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                text = text[len(prefix):].strip()
        
        return text[:100]  # Limit length
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        logger.info("Extraction cache cleared")