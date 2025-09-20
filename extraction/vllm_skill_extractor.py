"""
Optimized skill extraction using vLLM for batch processing
"""

import re
import logging
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict

from models.base_models import Skill, UnitOfCompetency, UniCourse, VETQualification, UniQualification
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel
from interfaces.vllm_genai_interface import VLLMGenAIInterface
from interfaces.embedding_interface import EmbeddingInterface
from .patterns import ExtractionPatterns, SkillOntology, CompositeSkillDecomposer

logger = logging.getLogger(__name__)


class VLLMSkillExtractor:
    """Optimized skill extraction using vLLM batch processing"""
    
    def __init__(self, 
                 genai: Optional[VLLMGenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 use_genai: bool = True,
                 batch_size: int = 8):
        """
        Initialize vLLM skill extractor
        
        Args:
            genai: vLLM GenAI interface for batch extraction
            embeddings: Embedding interface for similarity
            use_genai: Whether to use GenAI for extraction
            batch_size: Batch size for vLLM processing
        """
        self.genai = genai
        self.embeddings = embeddings
        self.use_genai = use_genai and genai is not None
        self.batch_size = batch_size
        
        self.patterns = ExtractionPatterns()
        self.ontology = SkillOntology()
        self.decomposer = CompositeSkillDecomposer()
        
        # Cache for processed texts
        self.cache = {}
    
    def extract_from_vet_qualification(self, vet_qual: VETQualification) -> Dict[str, List[Skill]]:
        """
        Extract skills from entire VET qualification using batch processing
        
        Args:
            vet_qual: VET qualification to process
            
        Returns:
            Dictionary mapping unit codes to extracted skills
        """
        logger.info(f"Batch extracting skills from VET qualification: {vet_qual.code}")
        
        if not vet_qual.units:
            return {}
        
        # Prepare batch data
        unit_texts = []
        unit_codes = []
        
        for unit in vet_qual.units:
            # Check cache first
            cache_key = f"vet_{unit.code}"
            if cache_key in self.cache:
                unit.extracted_skills = self.cache[cache_key]
                continue
            
            unit_texts.append(unit.get_full_text())
            unit_codes.append(unit.code)
        
        if not unit_texts:
            logger.info("All units already cached")
            return {unit.code: unit.extracted_skills for unit in vet_qual.units}
        
        # Batch process with vLLM if available
        all_skills = {}
        
        if self.use_genai and unit_texts:
            try:
                # Process in batches
                logger.info(f"Processing {len(unit_texts)} units in batches of {self.batch_size}")
                
                batch_results = []
                for i in range(0, len(unit_texts), self.batch_size):
                    batch_texts = unit_texts[i:i + self.batch_size]
                    batch_codes = unit_codes[i:i + self.batch_size]
                    
                    # Get AI-extracted skills for batch
                    ai_skills_batch = self.genai.extract_skills_batch(batch_texts, "VET unit")
                    
                    # Process each result
                    for j, (text, code, ai_skills) in enumerate(zip(batch_texts, batch_codes, ai_skills_batch)):
                        skills = self._process_extracted_skills(ai_skills, f"VET:{code}")
                        
                        # Add pattern-based extraction as supplement
                        pattern_skills = self._extract_with_patterns(text, "VET", code)
                        skills.extend(pattern_skills)
                        
                        # Process and deduplicate
                        skills = self._handle_composite_skills(skills)
                        skills = self._deduplicate_skills(skills)
                        
                        # Adjust for VET context
                        for skill in skills:
                            if skill.context == SkillContext.HYBRID:
                                skill.context = SkillContext.PRACTICAL
                        
                        batch_results.append((code, skills))
                    
                    logger.info(f"Processed batch {i//self.batch_size + 1}")
                
                # Assign results
                for code, skills in batch_results:
                    # Find corresponding unit
                    for unit in vet_qual.units:
                        if unit.code == code:
                            unit.extracted_skills = skills
                            self.cache[f"vet_{code}"] = skills
                            all_skills[code] = skills
                            break
                            
            except Exception as e:
                logger.warning(f"vLLM batch processing failed: {e}. Falling back to pattern extraction.")
                
                # Fallback to pattern-based extraction
                for text, code in zip(unit_texts, unit_codes):
                    skills = self._fallback_extract(text, "VET", code)
                    
                    for unit in vet_qual.units:
                        if unit.code == code:
                            unit.extracted_skills = skills
                            self.cache[f"vet_{code}"] = skills
                            all_skills[code] = skills
                            break
        else:
            # Pattern-based extraction only
            for text, code in zip(unit_texts, unit_codes):
                skills = self._fallback_extract(text, "VET", code)
                
                for unit in vet_qual.units:
                    if unit.code == code:
                        unit.extracted_skills = skills
                        self.cache[f"vet_{code}"] = skills
                        all_skills[code] = skills
                        break
        
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
        
        if not uni_qual.courses:
            return {}
        
        # Prepare batch data
        course_texts = []
        course_codes = []
        course_levels = []
        
        for course in uni_qual.courses:
            # Check cache first
            cache_key = f"uni_{course.code}"
            if cache_key in self.cache:
                course.extracted_skills = self.cache[cache_key]
                continue
            
            course_texts.append(course.get_full_text())
            course_codes.append(course.code)
            course_levels.append(course.study_level)
        
        if not course_texts:
            logger.info("All courses already cached")
            return {course.code: course.extracted_skills for course in uni_qual.courses}
        
        # Batch process with vLLM if available
        all_skills = {}
        
        if self.use_genai and course_texts:
            try:
                logger.info(f"Processing {len(course_texts)} courses in batches of {self.batch_size}")
                
                batch_results = []
                for i in range(0, len(course_texts), self.batch_size):
                    batch_texts = course_texts[i:i + self.batch_size]
                    batch_codes = course_codes[i:i + self.batch_size]
                    batch_levels = course_levels[i:i + self.batch_size]
                    
                    # Get AI-extracted skills for batch
                    ai_skills_batch = self.genai.extract_skills_batch(batch_texts, "university course")
                    
                    # Process each result
                    for text, code, level, ai_skills in zip(batch_texts, batch_codes, batch_levels, ai_skills_batch):
                        skills = self._process_extracted_skills(ai_skills, f"UNI:{code}")
                        
                        # Add pattern-based extraction
                        pattern_skills = self._extract_with_patterns(text, "UNI", code)
                        skills.extend(pattern_skills)
                        
                        # Process and deduplicate
                        skills = self._handle_composite_skills(skills)
                        skills = self._deduplicate_skills(skills)
                        
                        # Adjust for study level
                        study_level_enum = StudyLevel.from_string(level)
                        for skill in skills:
                            skill.level = self._adjust_level_by_study_level(skill.level, study_level_enum)
                        
                        batch_results.append((code, skills))
                    
                    logger.info(f"Processed batch {i//self.batch_size + 1}")
                
                # Assign results
                for code, skills in batch_results:
                    for course in uni_qual.courses:
                        if course.code == code:
                            course.extracted_skills = skills
                            self.cache[f"uni_{code}"] = skills
                            all_skills[code] = skills
                            break
                            
            except Exception as e:
                logger.warning(f"vLLM batch processing failed: {e}. Falling back to pattern extraction.")
                
                # Fallback
                for text, code, level in zip(course_texts, course_codes, course_levels):
                    skills = self._fallback_extract(text, "UNI", code)
                    
                    # Adjust for study level
                    study_level_enum = StudyLevel.from_string(level)
                    for skill in skills:
                        skill.level = self._adjust_level_by_study_level(skill.level, study_level_enum)
                    
                    for course in uni_qual.courses:
                        if course.code == code:
                            course.extracted_skills = skills
                            self.cache[f"uni_{code}"] = skills
                            all_skills[code] = skills
                            break
        else:
            # Pattern-based extraction only
            for text, code, level in zip(course_texts, course_codes, course_levels):
                skills = self._fallback_extract(text, "UNI", code)
                
                # Adjust for study level
                study_level_enum = StudyLevel.from_string(level)
                for skill in skills:
                    skill.level = self._adjust_level_by_study_level(skill.level, study_level_enum)
                
                for course in uni_qual.courses:
                    if course.code == code:
                        course.extracted_skills = skills
                        self.cache[f"uni_{code}"] = skills
                        all_skills[code] = skills
                        break
        
        logger.info(f"Extracted skills from {len(all_skills)} courses")
        return all_skills
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """Extract skills from a single VET unit (for compatibility)"""
        cache_key = f"vet_{unit.code}"
        if cache_key in self.cache:
            unit.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        # Process single unit
        qual = VETQualification(code="TEMP", name="Temp", level="", units=[unit])
        results = self.extract_from_vet_qualification(qual)
        
        return results.get(unit.code, [])
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """Extract skills from a single university course (for compatibility)"""
        cache_key = f"uni_{course.code}"
        if cache_key in self.cache:
            course.extracted_skills = self.cache[cache_key]
            return self.cache[cache_key]
        
        # Process single course
        qual = UniQualification(code="TEMP", name="Temp", courses=[course])
        results = self.extract_from_uni_qualification(qual)
        
        return results.get(course.code, [])
    
    def _process_extracted_skills(self, ai_skills: List[Dict], source: str) -> List[Skill]:
        """Convert AI-extracted skills to Skill objects"""
        skills = []
        
        for skill_dict in ai_skills:
            try:
                skill = Skill(
                    name=skill_dict.get("name", ""),
                    category=SkillCategory(skill_dict.get("category", "technical")),
                    level=SkillLevel.from_string(skill_dict.get("level", "competent")),
                    context=SkillContext(skill_dict.get("context", "hybrid")),
                    keywords=skill_dict.get("keywords", []),
                    confidence=skill_dict.get("confidence", 0.8),
                    source=source
                )
                skills.append(skill)
            except Exception as e:
                logger.debug(f"Failed to process skill: {e}")
        
        return skills
    
    def _fallback_extract(self, text: str, source_type: str, source_code: str) -> List[Skill]:
        """Fallback extraction using patterns"""
        skills = self._extract_with_patterns(text, source_type, source_code)
        
        # Extract from learning outcomes if present
        outcome_pattern = r"(?:will be able to|demonstrate|develop|understand|apply)\s+([^.;]+)"
        outcomes = re.findall(outcome_pattern, text.lower())
        
        for outcome in outcomes[:10]:  # Limit to prevent too many
            skill_name = self._clean_skill_name(outcome)
            if skill_name:
                skill = Skill(
                    name=skill_name,
                    category=self._categorize_skill(skill_name),
                    level=SkillLevel.COMPETENT,
                    context=SkillContext.HYBRID,
                    confidence=0.6,
                    source=f"{source_type}:{source_code}"
                )
                skills.append(skill)
        
        skills = self._handle_composite_skills(skills)
        skills = self._deduplicate_skills(skills)
        
        return skills
    
    def _extract_with_patterns(self, text: str, source_type: str, source_code: str) -> List[Skill]:
        """Extract skills using patterns"""
        skills = []
        text_lower = text.lower()
        
        for pattern, pattern_type in self.patterns.SKILL_PATTERNS:
            matches = re.findall(pattern, text_lower)
            
            for match in matches:
                skill_name = self._clean_skill_name(match)
                if not skill_name:
                    continue
                
                skill = Skill(
                    name=skill_name,
                    category=self._categorize_skill(skill_name),
                    level=SkillLevel.COMPETENT,
                    context=self._determine_context(text_lower),
                    keywords=self._extract_keywords(skill_name, text_lower),
                    evidence_type=pattern_type,
                    confidence=0.7,
                    source=f"{source_type}:{source_code}"
                )
                skills.append(skill)
        
        return skills
    
    def _clean_skill_name(self, name: str) -> str:
        """Clean and normalize skill name"""
        if not name:
            return ""
        
        # Remove extra whitespace
        name = " ".join(name.split())
        
        # Remove common stop words at the beginning
        stop_prefixes = ["the", "a", "an", "and", "or", "of", "in", "on", "at", "to", "for"]
        words = name.split()
        while words and words[0].lower() in stop_prefixes:
            words.pop(0)
        
        name = " ".join(words)
        
        # Limit length
        if len(name) > 100:
            name = name[:100]
        
        # Basic validation
        if len(name) < 3 or len(name.split()) > 10:
            return ""
        
        return name.strip()
    
    def _categorize_skill(self, skill_name: str) -> SkillCategory:
        """Categorize skill based on keywords and ontology"""
        skill_lower = skill_name.lower()
        
        # Check keyword categories
        for category, keywords in self.patterns.CATEGORY_KEYWORDS.items():
            if any(keyword in skill_lower for keyword in keywords):
                return SkillCategory(category)
        
        return SkillCategory.TECHNICAL
    
    def _determine_context(self, text: str) -> SkillContext:
        """Determine if content is theoretical, practical, or hybrid"""
        text_lower = text.lower()
        
        practical_count = sum(
            1 for ind in self.patterns.CONTEXT_INDICATORS["practical"] 
            if ind in text_lower
        )
        theoretical_count = sum(
            1 for ind in self.patterns.CONTEXT_INDICATORS["theoretical"] 
            if ind in text_lower
        )
        
        if practical_count > theoretical_count * 1.5:
            return SkillContext.PRACTICAL
        elif theoretical_count > practical_count * 1.5:
            return SkillContext.THEORETICAL
        else:
            return SkillContext.HYBRID
    
    def _extract_keywords(self, skill_name: str, context_text: str) -> List[str]:
        """Extract relevant keywords for a skill"""
        keywords = []
        skill_words = set(skill_name.lower().split())
        
        # Find words that frequently appear near the skill name
        if skill_name.lower() in context_text.lower():
            pattern = f"\\b\\w+\\s+{re.escape(skill_name.lower())}\\s+\\w+\\b"
            matches = re.findall(pattern, context_text.lower())
            
            for match in matches[:5]:
                words = match.split()
                for word in words:
                    if word not in skill_words and len(word) > 3:
                        keywords.append(word)
        
        return list(set(keywords))[:10]
    
    def _handle_composite_skills(self, skills: List[Skill]) -> List[Skill]:
        """Handle composite skills by decomposing them"""
        expanded_skills = []
        
        for skill in skills:
            if self.decomposer.is_composite(skill.name):
                components = self.decomposer.decompose(skill.name)
                expanded_skills.append(skill)
                
                for component_name in components:
                    if component_name != skill.name:
                        component_skill = Skill(
                            name=component_name,
                            category=skill.category,
                            level=skill.level,
                            context=skill.context,
                            confidence=skill.confidence * 0.8,
                            source=f"decomposed_from_{skill.source}"
                        )
                        expanded_skills.append(component_skill)
            else:
                expanded_skills.append(skill)
        
        return expanded_skills
    
    def _deduplicate_skills(self, skills: List[Skill]) -> List[Skill]:
        """Remove duplicate skills, keeping highest confidence"""
        skill_dict = {}
        
        for skill in skills:
            key = skill.name.lower().strip()
            
            if key not in skill_dict:
                skill_dict[key] = skill
            else:
                if skill.confidence > skill_dict[key].confidence:
                    skill_dict[key] = skill
                elif skill.keywords:
                    existing_keywords = set(skill_dict[key].keywords)
                    existing_keywords.update(skill.keywords)
                    skill_dict[key].keywords = list(existing_keywords)[:10]
        
        return list(skill_dict.values())
    
    def _adjust_level_by_study_level(self, base_level: SkillLevel, study_level: StudyLevel) -> SkillLevel:
        """Adjust skill level based on study level"""
        if study_level == StudyLevel.INTRODUCTORY:
            return min(base_level, SkillLevel.ADVANCED_BEGINNER)
        elif study_level == StudyLevel.INTERMEDIATE:
            return base_level
        elif study_level == StudyLevel.ADVANCED:
            return max(base_level, SkillLevel.COMPETENT)
        elif study_level == StudyLevel.SPECIALIZED:
            return max(base_level, SkillLevel.PROFICIENT)
        else:  # POSTGRADUATE
            return max(base_level, SkillLevel.EXPERT)
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        logger.info("Extraction cache cleared")