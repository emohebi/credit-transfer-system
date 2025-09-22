"""
vLLM skill extraction using true batch processing for efficient multi-unit/course processing
"""

import logging
from typing import List, Dict, Optional, Any

from models.base_models import Skill, UnitOfCompetency, UniCourse, VETQualification, UniQualification
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel
from interfaces.embedding_interface import EmbeddingInterface

logger = logging.getLogger(__name__)


class VLLMSkillExtractorBatch:
    """vLLM skill extraction using true batch processing"""
    
    def __init__(self, 
                 genai=None,
                 embeddings: Optional[EmbeddingInterface] = None):
        """
        Initialize vLLM skill extractor with batch processing
        
        Args:
            genai: vLLM GenAI batch interface for extraction
            embeddings: Embedding interface for similarity
        """
        self.genai = genai
        self.embeddings = embeddings
        
        # Cache for processed texts
        self.cache = {}
        
        # Batch processing size
        self.batch_size = getattr(genai, 'batch_size', 8) if genai else 8
    
    def extract_from_vet_qualification(self, vet_qual: VETQualification) -> Dict[str, List[Skill]]:
        """
        Extract skills from entire VET qualification using batch processing
        
        Args:
            vet_qual: VET qualification to process
            
        Returns:
            Dictionary mapping unit codes to extracted skills
        """
        logger.info(f"Batch extracting skills from VET qualification: {vet_qual.code}")
        
        # Check which units need processing
        units_to_process = []
        units_cached = []
        
        for unit in vet_qual.units:
            cache_key = f"vet_{unit.code}"
            if cache_key in self.cache:
                unit.extracted_skills = self.cache[cache_key]
                units_cached.append(unit)
            else:
                units_to_process.append(unit)
        
        if units_cached:
            logger.info(f"Using cached skills for {len(units_cached)} units")
        
        if units_to_process:
            logger.info(f"Processing {len(units_to_process)} VET units in batches")
            
            # Process all units in batches
            for i in range(0, len(units_to_process), self.batch_size):
                batch_units = units_to_process[i:i + self.batch_size]
                self._process_vet_batch(batch_units)
        
        # Return all skills
        all_skills = {}
        for unit in vet_qual.units:
            all_skills[unit.code] = unit.extracted_skills
        
        logger.info(f"Extracted skills from {len(all_skills)} units")
        return all_skills
    
    def extract_from_uni_qualification(self, uni_qual: UniQualification) -> Dict[str, List[Skill]]:
        """
        Extract skills from entire university qualification using batch processing
        
        Args:
            uni_qual: University qualification to process
            
        Returns:
            Dictionary mapping course codes to extracted skills
        """
        logger.info(f"Batch extracting skills from Uni qualification: {uni_qual.code}")
        
        # Check which courses need processing
        courses_to_process = []
        courses_cached = []
        
        for course in uni_qual.courses:
            cache_key = f"uni_{course.code}"
            if cache_key in self.cache:
                course.extracted_skills = self.cache[cache_key]
                courses_cached.append(course)
            else:
                courses_to_process.append(course)
        
        if courses_cached:
            logger.info(f"Using cached skills for {len(courses_cached)} courses")
        
        if courses_to_process:
            logger.info(f"Processing {len(courses_to_process)} Uni courses in batches")
            
            # Process all courses in batches
            for i in range(0, len(courses_to_process), self.batch_size):
                batch_courses = courses_to_process[i:i + self.batch_size]
                self._process_uni_batch(batch_courses)
        
        # Return all skills
        all_skills = {}
        for course in uni_qual.courses:
            all_skills[course.code] = course.extracted_skills
        
        logger.info(f"Extracted skills from {len(all_skills)} courses")
        return all_skills
    
    def _process_vet_batch(self, units: List[UnitOfCompetency]):
        """Process a batch of VET units"""
        # Step 1: Extract skills using batch GenAI
        texts = [unit.get_full_text() for unit in units]
        contexts = ["VET unit"] * len(units)
        
        ai_skills_batch = self.genai.extract_skills_batch(texts, contexts)
        
        # Step 2: Identify implicit skills in batch
        explicit_skills_lists = [[s["name"] for s in skills] for skills in ai_skills_batch]
        implicit_skills_batch = self.genai.identify_implicit_skills_batch(texts, explicit_skills_lists)
        
        # Step 3: Determine contexts in batch
        context_results = self.genai.determine_contexts_batch(texts)
        
        # Step 4: Process each unit with batch results
        for idx, unit in enumerate(units):
            skills = []
            
            # Add explicit skills
            ai_skills = ai_skills_batch[idx] if idx < len(ai_skills_batch) else []
            skills.extend(self._convert_ai_skills(ai_skills, f"VET:{unit.code}"))
            
            # Add implicit skills
            implicit_skills = implicit_skills_batch[idx] if idx < len(implicit_skills_batch) else []
            for impl_skill in implicit_skills:
                skill = Skill(
                    name=impl_skill["name"],
                    category=self._validate_category(impl_skill.get("category", "technical")),
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.PRACTICAL,
                    confidence=impl_skill.get("confidence", 0.6),
                    source=f"VET:{unit.code}_implicit"
                )
                skills.append(skill)
            
            # Apply context
            context_result = context_results[idx] if idx < len(context_results) else {}
            primary_context = context_result.get("context_analysis", {}).get("primary_context", "practical")
            
            for skill in skills:
                if primary_context == "practical":
                    skill.context = SkillContext.PRACTICAL
                elif primary_context == "theoretical":
                    skill.context = SkillContext.THEORETICAL
                else:
                    skill.context = SkillContext.HYBRID
            
            # Step 5: Decompose composite skills (done per unit for now)
            skill_names = [s.name for s in skills]
            if skill_names:
                composite_result = self.genai.decompose_composite_skills(skill_names)
                
                for comp_skill in composite_result.get("composite_skills", []):
                    if comp_skill.get("is_composite"):
                        for component in comp_skill.get("components", []):
                            new_skill = Skill(
                                name=component["name"],
                                category=self._validate_category(component.get("category", "technical")),
                                level=SkillLevel.COMPETENT,
                                context=SkillContext.PRACTICAL,
                                confidence=0.7,
                                source=f"VET:{unit.code}_decomposed"
                            )
                            skills.append(new_skill)
            
            # Step 6: Deduplicate skills
            skills = self._deduplicate_skills_with_ai(skills)
            
            # Cache and assign
            cache_key = f"vet_{unit.code}"
            self.cache[cache_key] = skills
            unit.extracted_skills = skills
            
            logger.debug(f"Extracted {len(skills)} skills from {unit.code}")
    
    def _process_uni_batch(self, courses: List[UniCourse]):
        """Process a batch of University courses"""
        # Step 1: Identify study levels in batch
        texts = [course.get_full_text() for course in courses]
        study_level_results = self.genai.identify_study_levels_batch(texts)
        
        for idx, course in enumerate(courses):
            if not course.study_level or course.study_level == "intermediate":
                if idx < len(study_level_results):
                    course.study_level = study_level_results[idx].get("study_level", "intermediate")
        
        # Step 2: Extract skills using batch GenAI
        contexts = ["university course"] * len(courses)
        ai_skills_batch = self.genai.extract_skills_batch(texts, contexts)
        
        # Step 3: Identify implicit skills in batch
        explicit_skills_lists = [[s["name"] for s in skills] for skills in ai_skills_batch]
        implicit_skills_batch = self.genai.identify_implicit_skills_batch(texts, explicit_skills_lists)
        
        # Step 4: Determine contexts in batch
        context_results = self.genai.determine_contexts_batch(texts)
        
        # Step 5: Process each course with batch results
        for idx, course in enumerate(courses):
            skills = []
            
            # Add explicit skills
            ai_skills = ai_skills_batch[idx] if idx < len(ai_skills_batch) else []
            skills.extend(self._convert_ai_skills(ai_skills, f"UNI:{course.code}"))
            
            # Add implicit skills
            implicit_skills = implicit_skills_batch[idx] if idx < len(implicit_skills_batch) else []
            for impl_skill in implicit_skills:
                skill = Skill(
                    name=impl_skill["name"],
                    category=self._validate_category(impl_skill.get("category", "technical")),
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.HYBRID,
                    confidence=impl_skill.get("confidence", 0.6),
                    source=f"UNI:{course.code}_implicit"
                )
                skills.append(skill)
            
            # Analyze prerequisites (individual processing for now)
            if course.prerequisites:
                prereq_result = self.genai.analyze_prerequisites(course.prerequisites, texts[idx][:1000])
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
            
            # Apply context
            context_result = context_results[idx] if idx < len(context_results) else {}
            primary_context = context_result.get("context_analysis", {}).get("primary_context", "hybrid")
            
            for skill in skills:
                if primary_context == "practical":
                    skill.context = SkillContext.PRACTICAL
                elif primary_context == "theoretical":
                    skill.context = SkillContext.THEORETICAL
                else:
                    skill.context = SkillContext.HYBRID
            
            # Adjust skill levels based on study level
            skills_dict = [{"name": s.name, "level": s.level.name} for s in skills]
            if skills_dict:
                level_adjustment = self.genai.adjust_skill_levels(skills_dict, course.study_level, texts[idx][:1000])
                
                for adj_skill in level_adjustment.get("adjusted_skills", []):
                    for skill in skills:
                        if skill.name == adj_skill["skill_name"]:
                            skill.level = SkillLevel.from_string(adj_skill["adjusted_level"])
                            break
            
            # Deduplicate skills
            skills = self._deduplicate_skills_with_ai(skills)
            
            # Cache and assign
            cache_key = f"uni_{course.code}"
            self.cache[cache_key] = skills
            course.extracted_skills = skills
            
            logger.debug(f"Extracted {len(skills)} skills from {course.code}")
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """
        Extract skills from a single VET unit (uses batch processing with size 1)
        
        Args:
            unit: VET unit to extract skills from
            
        Returns:
            List of extracted skills
        """
        logger.info(f"Extracting skills from single VET unit: {unit.code}")
        
        cache_key = f"vet_{unit.code}"
        if cache_key in self.cache:
            unit.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        # Process as a batch of 1
        self._process_vet_batch([unit])
        return unit.extracted_skills
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """
        Extract skills from a single university course (uses batch processing with size 1)
        
        Args:
            course: University course to extract skills from
            
        Returns:
            List of extracted skills
        """
        logger.info(f"Extracting skills from single Uni course: {course.code}")
        
        cache_key = f"uni_{course.code}"
        if cache_key in self.cache:
            course.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        # Process as a batch of 1
        self._process_uni_batch([course])
        return course.extracted_skills
    
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
        
        for valid_cat in valid_categories:
            if valid_cat in category_lower or category_lower in valid_cat:
                return valid_categories[valid_cat]
        
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
        
        skills_dict = [
            {
                "name": s.name,
                "category": s.category.value,
                "level": s.level.name,
                "confidence": s.confidence
            }
            for s in skills
        ]
        
        dedup_result = self.genai.deduplicate_skills(skills_dict)
        
        final_skills = []
        processed_names = set()
        
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
                    merged_category = self._validate_category(group.get("merged_category", best_skill.category.value))
                    best_skill.category = merged_category
                    best_skill.level = SkillLevel.from_string(group.get("merged_level", best_skill.level.name))
                    final_skills.append(best_skill)
        
        for skill_name in dedup_result.get("unique_skills", []):
            for skill in skills:
                if skill.name == skill_name and skill.name.lower() not in processed_names:
                    final_skills.append(skill)
                    processed_names.add(skill.name.lower())
        
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
            "batch_size": self.batch_size,
            "extraction_mode": "vllm_batch_processing",
            "features": [
                "true_batch_processing",
                "batch_skill_extraction",
                "batch_context_determination",
                "batch_study_level_detection",
                "parallel_implicit_skill_detection",
                "efficient_multi_unit_processing",
                "optimized_for_qualifications"
            ]
        }