"""
OpenAI skill extraction with maximum accuracy - individual requests with comprehensive extraction
"""

import re
import logging
import time
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import defaultdict

from models.base_models import Skill, UnitOfCompetency, UniCourse
from models.enums import SkillLevel, SkillContext, SkillCategory, StudyLevel
from interfaces.genai_interface import GenAIInterface
from interfaces.embedding_interface import EmbeddingInterface
from .patterns import ExtractionPatterns, SkillOntology, CompositeSkillDecomposer

logger = logging.getLogger(__name__)


class OpenAISkillExtractor:
    """OpenAI skill extraction with maximum accuracy - comprehensive extraction with rate limiting"""
    
    def __init__(self, 
                 genai: Optional[GenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 use_genai: bool = True,
                 delay_between_requests: float = 1.0):
        """
        Initialize OpenAI skill extractor with maximum accuracy
        
        Args:
            genai: Azure OpenAI GenAI interface for extraction
            embeddings: Embedding interface for similarity
            use_genai: Whether to use GenAI for extraction
            delay_between_requests: Delay between API requests to avoid rate limits
        """
        self.genai = genai
        self.embeddings = embeddings
        self.use_genai = use_genai and genai is not None
        self.delay_between_requests = delay_between_requests
        
        self.patterns = ExtractionPatterns()
        self.ontology = SkillOntology()
        self.decomposer = CompositeSkillDecomposer()
        
        # Cache for processed texts
        self.cache = {}
        
        # Rate limiting tracking
        self.last_request_time = 0
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """
        Extract skills from VET unit of competency with maximum accuracy
        
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
        
        # Use GenAI for extraction if available
        if self.use_genai:
            try:
                # Rate limiting
                self._enforce_rate_limit()
                
                ai_skills = self.genai.extract_skills_prompt(full_text, "VET unit")
                skills.extend(self._convert_ai_skills(ai_skills, f"VET:{unit.code}"))
                logger.debug(f"AI extracted {len(ai_skills)} skills from {unit.code}")
            except Exception as e:
                logger.warning(f"GenAI extraction failed for {unit.code}: {e}")
        
        # Pattern-based extraction as supplement
        pattern_skills = self._extract_with_patterns(full_text, "VET", unit.code)
        skills.extend(pattern_skills)
        logger.debug(f"Pattern extraction added {len(pattern_skills)} skills from {unit.code}")
        
        # Parse learning outcomes individually for higher accuracy
        for i, outcome in enumerate(unit.learning_outcomes):
            outcome_skills = self._parse_learning_outcome(outcome, f"VET:{unit.code}")
            skills.extend(outcome_skills)
            logger.debug(f"Learning outcome {i+1} added {len(outcome_skills)} skills from {unit.code}")
        
        # Extract from assessment requirements
        if unit.assessment_requirements:
            assessment_skills = self._extract_from_assessment(
                unit.assessment_requirements, 
                f"VET:{unit.code}"
            )
            skills.extend(assessment_skills)
            logger.debug(f"Assessment extraction added {len(assessment_skills)} skills from {unit.code}")
        
        # Extract implicit skills using comprehensive approach
        implicit_skills = self._extract_implicit_skills(full_text, skills)
        skills.extend(implicit_skills)
        logger.debug(f"Implicit extraction added {len(implicit_skills)} skills from {unit.code}")
        
        # Handle composite skills with full decomposition
        skills = self._handle_composite_skills(skills)
        
        # Deduplicate and validate
        skills = self._deduplicate_skills(skills)
        
        # Adjust for VET context (typically more practical)
        for skill in skills:
            if skill.context == SkillContext.HYBRID:
                skill.context = SkillContext.PRACTICAL
        
        # Cache and assign
        self.cache[cache_key] = skills
        unit.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {unit.code} (maximum accuracy mode)")
        return skills
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """
        Extract skills from university course with maximum accuracy
        
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
        
        # Use GenAI for extraction if available
        if self.use_genai:
            try:
                # Rate limiting
                self._enforce_rate_limit()
                
                ai_skills = self.genai.extract_skills_prompt(full_text, "university course")
                skills.extend(self._convert_ai_skills(ai_skills, f"UNI:{course.code}"))
                logger.debug(f"AI extracted {len(ai_skills)} skills from {course.code}")
            except Exception as e:
                logger.warning(f"GenAI extraction failed for {course.code}: {e}")
        
        # Pattern-based extraction as supplement
        pattern_skills = self._extract_with_patterns(full_text, "UNI", course.code)
        skills.extend(pattern_skills)
        logger.debug(f"Pattern extraction added {len(pattern_skills)} skills from {course.code}")
        
        # Parse learning outcomes individually
        for i, outcome in enumerate(course.learning_outcomes):
            outcome_skills = self._parse_learning_outcome(outcome, f"UNI:{course.code}")
            skills.extend(outcome_skills)
            logger.debug(f"Learning outcome {i+1} added {len(outcome_skills)} skills from {course.code}")
        
        # Extract from topics with study level awareness
        for topic in course.topics:
            topic_skills = self._extract_from_topic(topic, course.study_level)
            skills.extend(topic_skills)
        logger.debug(f"Topic extraction added skills from {len(course.topics)} topics in {course.code}")
        
        # Extract from assessment with detailed analysis
        if course.assessment:
            assessment_skills = self._extract_from_assessment(
                course.assessment,
                f"UNI:{course.code}"
            )
            skills.extend(assessment_skills)
            logger.debug(f"Assessment extraction added {len(assessment_skills)} skills from {course.code}")
        
        # Extract from prerequisites
        prereq_skills = self._extract_from_prerequisites(course.prerequisites)
        skills.extend(prereq_skills)
        logger.debug(f"Prerequisite extraction added {len(prereq_skills)} skills from {course.code}")
        
        # Extract implicit skills with comprehensive approach
        implicit_skills = self._extract_implicit_skills(full_text, skills)
        skills.extend(implicit_skills)
        logger.debug(f"Implicit extraction added {len(implicit_skills)} skills from {course.code}")
        
        # Handle composite skills with full decomposition
        skills = self._handle_composite_skills(skills)
        
        # Deduplicate and validate
        skills = self._deduplicate_skills(skills)
        
        # Adjust levels based on study_level with sophisticated logic
        study_level_enum = StudyLevel.from_string(course.study_level)
        expected_level = StudyLevel.expected_skill_level(study_level_enum)
        
        for skill in skills:
            skill.level = self._adjust_level_by_study_level(skill.level, study_level_enum)
        
        # Cache and assign
        self.cache[cache_key] = skills
        course.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {course.code} (maximum accuracy mode)")
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
    
    def _extract_with_patterns(self, text: str, source_type: str, source_code: str) -> List[Skill]:
        """Extract skills using comprehensive pattern analysis"""
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
                    level=SkillLevel.COMPETENT,  # Default
                    context=self._determine_context(text_lower),
                    keywords=self._extract_keywords(skill_name, text_lower),
                    evidence_type=pattern_type,
                    confidence=0.7,  # Pattern-based extraction confidence
                    source=f"{source_type}:{source_code}"
                )
                skills.append(skill)
        
        return skills
    
    def _parse_learning_outcome(self, outcome: str, source: str) -> List[Skill]:
        """Parse a learning outcome statement for skills with high accuracy"""
        skills = []
        outcome_lower = outcome.lower()
        
        # Extract skill phrases from outcome using all patterns
        for pattern, pattern_type in self.patterns.SKILL_PATTERNS[:5]:  # Focus on main patterns
            matches = re.findall(pattern, outcome_lower)
            for match in matches:
                skill_name = self._clean_skill_name(match)
                if skill_name:
                    skill = Skill(
                        name=skill_name,
                        category=self._categorize_skill(skill_name),
                        level=SkillLevel.COMPETENT,
                        context=SkillContext.HYBRID,
                        confidence=0.9,  # High confidence from learning outcomes
                        source=source
                    )
                    skills.append(skill)
        
        return skills
    
    def _extract_from_topic(self, topic: str, study_level: str) -> List[Skill]:
        """Extract skills from course topic with study level awareness"""
        topic_clean = self._clean_skill_name(topic)
        if not topic_clean:
            return []
        
        study_level_enum = StudyLevel.from_string(study_level)
        
        skill = Skill(
            name=topic_clean,
            category=self._categorize_skill(topic_clean),
            level=StudyLevel.expected_skill_level(study_level_enum),
            context=SkillContext.THEORETICAL,  # Topics are typically theoretical
            confidence=0.7,
            source=f"topic_{study_level}"
        )
        
        return [skill]
    
    def _extract_from_assessment(self, assessment_text: str, source: str) -> List[Skill]:
        """Extract skills from assessment descriptions with detailed analysis"""
        skills = []
        assessment_lower = assessment_text.lower()
        
        # Determine context from assessment type
        context = SkillContext.HYBRID
        for assess_type, indicators in self.patterns.ASSESSMENT_INDICATORS.items():
            if any(ind in assessment_lower for ind in indicators):
                if assess_type in ["exam", "test"]:
                    context = SkillContext.THEORETICAL
                elif assess_type in ["practical", "project"]:
                    context = SkillContext.PRACTICAL
                break
        
        # Extract skills mentioned in assessment
        skill_indicators = [
            "assess", "evaluate", "demonstrate", "apply", "analyze",
            "design", "implement", "solve", "create", "develop"
        ]
        
        for indicator in skill_indicators:
            if indicator in assessment_lower:
                pattern = f"{indicator}\\s+([\\w\\s]+?)(?:[,\\.;]|$)"
                matches = re.findall(pattern, assessment_lower)
                
                for match in matches[:5]:  # Increased limit for maximum accuracy
                    skill_name = f"{indicator} {match.strip()}"
                    skill = Skill(
                        name=skill_name,
                        category=SkillCategory.COGNITIVE,
                        level=SkillLevel.COMPETENT,
                        context=context,
                        confidence=0.6,
                        source=source
                    )
                    skills.append(skill)
        
        return skills
    
    def _extract_from_prerequisites(self, prerequisites: List[str]) -> List[Skill]:
        """Extract foundational skills from prerequisites"""
        skills = []
        
        for prereq in prerequisites:
            # Prerequisites indicate foundational skills
            skill = Skill(
                name=self._clean_skill_name(prereq),
                category=SkillCategory.FOUNDATIONAL,
                level=SkillLevel.COMPETENT,
                context=SkillContext.THEORETICAL,
                confidence=0.8,
                source="prerequisite"
            )
            skills.append(skill)
        
        return skills
    
    def _extract_implicit_skills(self, text: str, explicit_skills: List[Skill]) -> List[Skill]:
        """Extract implicit skills using comprehensive AI + ontology approach"""
        implicit_skills = []
        text_lower = text.lower()
        explicit_names = {s.name.lower() for s in explicit_skills}
        
        # Use GenAI for comprehensive implicit skill extraction
        if self.use_genai and self.genai:
            try:
                # Rate limiting for additional API call
                self._enforce_rate_limit()
                
                ai_implicit = self.genai.identify_implicit_skills(
                    text, 
                    list(explicit_names)[:20]  # Limit for API efficiency
                )
                for skill_dict in ai_implicit:
                    if skill_dict["name"].lower() not in explicit_names:
                        skill = Skill(
                            name=skill_dict["name"],
                            category=SkillCategory.TECHNICAL,
                            level=SkillLevel.COMPETENT,
                            context=SkillContext.HYBRID,
                            confidence=skill_dict.get("confidence", 0.5),
                            source="implicit_ai"
                        )
                        implicit_skills.append(skill)
                        logger.debug(f"AI identified implicit skill: {skill_dict['name']}")
            except Exception as e:
                logger.debug(f"Failed to extract implicit skills with AI: {e}")
        
        # Use comprehensive ontology-based inference
        for explicit_skill in explicit_skills:
            implied = self.ontology.get_implied_skills(explicit_skill.name)
            for implied_name in implied:
                if implied_name.lower() not in explicit_names:
                    skill = Skill(
                        name=implied_name,
                        category=self._categorize_skill(implied_name),
                        level=explicit_skill.level,  # Inherit from parent skill
                        context=explicit_skill.context,
                        confidence=0.6,  # Lower confidence for inferred
                        source="implicit_inference"
                    )
                    implicit_skills.append(skill)
                    explicit_names.add(implied_name.lower())  # Prevent duplicates
                    logger.debug(f"Ontology inferred implicit skill: {implied_name}")
        
        return implicit_skills
    
    def _handle_composite_skills(self, skills: List[Skill]) -> List[Skill]:
        """Handle composite skills with comprehensive decomposition"""
        expanded_skills = []
        
        for skill in skills:
            if self.decomposer.is_composite(skill.name):
                # Decompose the skill comprehensively
                components = self.decomposer.decompose(skill.name)
                
                # Add original composite skill
                expanded_skills.append(skill)
                logger.debug(f"Decomposing composite skill: {skill.name} -> {len(components)} components")
                
                # Add component skills with inherited properties
                for component_name in components:
                    if component_name != skill.name:  # Avoid duplicate
                        component_skill = Skill(
                            name=component_name,
                            category=skill.category,
                            level=skill.level,
                            context=skill.context,
                            confidence=skill.confidence * 0.8,  # Slightly lower confidence
                            source=f"decomposed_from_{skill.source}"
                        )
                        expanded_skills.append(component_skill)
            else:
                expanded_skills.append(skill)
        
        return expanded_skills
    
    def _convert_ai_skills(self, ai_skills: List[Dict], source: str) -> List[Skill]:
        """Convert AI-extracted skills to Skill objects with validation"""
        skills = []
        
        for ai_skill in ai_skills:
            try:
                skill = Skill(
                    name=ai_skill["name"],
                    category=SkillCategory(ai_skill.get("category", "technical")),
                    level=SkillLevel.from_string(ai_skill.get("level", "competent")),
                    context=SkillContext(ai_skill.get("context", "hybrid")),
                    keywords=ai_skill.get("keywords", []),
                    confidence=ai_skill.get("confidence", 0.8),
                    source=source
                )
                skills.append(skill)
            except Exception as e:
                logger.debug(f"Failed to convert AI skill: {e}")
        
        return skills
    
    def _clean_skill_name(self, name: str) -> str:
        """Clean and normalize skill name with comprehensive validation"""
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
        
        # Comprehensive validation
        if len(name) < 3 or len(name.split()) > 10:
            return ""
        
        # Remove obviously invalid patterns
        invalid_patterns = [
            r"^\d+$",  # Only numbers
            r"^[^a-zA-Z]*$",  # No letters
            r"^(and|or|the|a|an)$"  # Only stop words
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, name.lower()):
                return ""
        
        return name.strip()
    
    def _categorize_skill(self, skill_name: str) -> SkillCategory:
        """Categorize skill using comprehensive keyword and ontology analysis"""
        skill_lower = skill_name.lower()
        
        # Check keyword categories with priority order
        category_priorities = [
            ("professional", self.patterns.CATEGORY_KEYWORDS["professional"]),
            ("technical", self.patterns.CATEGORY_KEYWORDS["technical"]),
            ("cognitive", self.patterns.CATEGORY_KEYWORDS["cognitive"]),
            ("practical", self.patterns.CATEGORY_KEYWORDS["practical"]),
            ("foundational", self.patterns.CATEGORY_KEYWORDS["foundational"])
        ]
        
        for category, keywords in category_priorities:
            if any(keyword in skill_lower for keyword in keywords):
                return SkillCategory(category)
        
        # Use comprehensive ontology categorization
        ontology_category = self.ontology.categorize_skill(skill_name)
        if "software" in ontology_category or "data" in ontology_category:
            return SkillCategory.TECHNICAL
        elif "engineering" in ontology_category:
            return SkillCategory.PRACTICAL
        
        # Default with context awareness
        return SkillCategory.TECHNICAL
    
    def _determine_context(self, text: str) -> SkillContext:
        """Determine context using comprehensive indicator analysis"""
        text_lower = text.lower()
        
        # Enhanced context indicators
        practical_indicators = [
            "hands-on", "laboratory", "workshop", "practical", "project", "real-world", 
            "industry", "workplace", "applied", "fieldwork", "experiential", "practicum", 
            "internship", "placement", "simulation", "case study", "implementation"
        ]
        
        theoretical_indicators = [
            "theory", "concept", "principle", "framework", "model", "academic", 
            "research", "analysis", "study", "examination", "foundation", "fundamental", 
            "abstract", "scholarly", "literature", "conceptual", "philosophical"
        ]
        
        practical_count = sum(1 for ind in practical_indicators if ind in text_lower)
        theoretical_count = sum(1 for ind in theoretical_indicators if ind in text_lower)
        
        # More nuanced threshold for context determination
        if practical_count > theoretical_count * 1.3:
            return SkillContext.PRACTICAL
        elif theoretical_count > practical_count * 1.3:
            return SkillContext.THEORETICAL
        else:
            return SkillContext.HYBRID
    
    def _extract_keywords(self, skill_name: str, context_text: str) -> List[str]:
        """Extract relevant keywords using comprehensive text analysis"""
        keywords = []
        skill_words = set(skill_name.lower().split())
        context_lower = context_text.lower()
        
        # Find words that frequently appear near the skill name
        if skill_name.lower() in context_lower:
            # Get surrounding context with larger window
            pattern = f"\\b\\w+\\s+\\w*\\s*{re.escape(skill_name.lower())}\\s*\\w*\\s+\\w+\\b"
            matches = re.findall(pattern, context_lower)
            
            for match in matches[:10]:  # Increased limit for maximum accuracy
                words = match.split()
                for word in words:
                    if (word not in skill_words and 
                        len(word) > 3 and 
                        word.isalpha() and 
                        word not in ["will", "able", "with", "from", "that", "this"]):
                        keywords.append(word)
        
        # Remove duplicates and limit
        return list(set(keywords))[:15]  # Increased limit
    
    def _adjust_level_by_study_level(self, base_level: SkillLevel, study_level: StudyLevel) -> SkillLevel:
        """Adjust skill level based on study level with sophisticated logic"""
        try:
            if study_level == StudyLevel.INTRODUCTORY:
                # Cap at ADVANCED_BEGINNER for introductory courses
                if base_level.value <= SkillLevel.ADVANCED_BEGINNER.value:
                    return base_level
                else:
                    return SkillLevel.ADVANCED_BEGINNER
                    
            elif study_level == StudyLevel.INTERMEDIATE:
                # No adjustment for intermediate, but ensure minimum competent
                if base_level.value < SkillLevel.COMPETENT.value:
                    return SkillLevel.COMPETENT
                return base_level
                
            elif study_level == StudyLevel.ADVANCED:
                # Ensure at least COMPETENT for advanced courses
                if base_level.value >= SkillLevel.COMPETENT.value:
                    return base_level
                else:
                    return SkillLevel.COMPETENT
                    
            elif study_level == StudyLevel.SPECIALIZED:
                # Ensure at least PROFICIENT for specialized courses
                if base_level.value >= SkillLevel.PROFICIENT.value:
                    return base_level
                else:
                    return SkillLevel.PROFICIENT
                    
            else:  # POSTGRADUATE
                # Ensure at least EXPERT for postgraduate courses
                if base_level.value >= SkillLevel.EXPERT.value:
                    return base_level
                else:
                    return SkillLevel.EXPERT
                    
        except (AttributeError, TypeError) as e:
            # Fallback in case of any comparison issues
            logger.warning(f"Error in level adjustment: {e}. Using base level.")
            return base_level
    
    def _deduplicate_skills(self, skills: List[Skill]) -> List[Skill]:
        """Remove duplicate skills with sophisticated merging logic"""
        skill_dict = {}
        
        for skill in skills:
            key = skill.name.lower().strip()
            
            if key not in skill_dict:
                skill_dict[key] = skill
            else:
                existing = skill_dict[key]
                
                # Keep the one with higher confidence
                if skill.confidence > existing.confidence:
                    # Merge beneficial properties from existing
                    skill.keywords = list(set(skill.keywords + existing.keywords))[:15]
                    skill_dict[key] = skill
                else:
                    # Merge beneficial properties into existing
                    existing.keywords = list(set(existing.keywords + skill.keywords))[:15]
                    
                    # Take higher level if different
                    if skill.level.value > existing.level.value:
                        existing.level = skill.level
        
        return list(skill_dict.values())
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        logger.info("Extraction cache cleared")
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the extraction process"""
        return {
            "cache_size": len(self.cache),
            "delay_between_requests": self.delay_between_requests,
            "use_genai": self.use_genai,
            "last_request_time": self.last_request_time,
            "extraction_mode": "individual_requests_max_accuracy",
            "features": [
                "comprehensive_ai_extraction",
                "detailed_pattern_analysis", 
                "sophisticated_implicit_skills",
                "full_composite_decomposition",
                "advanced_study_level_adjustment",
                "enhanced_keyword_extraction",
                "intelligent_deduplication"
            ]
        }