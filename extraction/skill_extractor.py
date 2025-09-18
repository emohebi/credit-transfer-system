"""
Advanced skill extraction from course descriptions
"""
"""
Advanced skill extraction from course descriptions
"""

import re
import logging
from typing import List, Dict, Set, Optional
from collections import defaultdict

from ..models.base_models import Skill, UnitOfCompetency, UniCourse
from ..models.enums import SkillLevel, SkillDepth, SkillContext, SkillCategory
from ..interfaces.genai_interface import GenAIInterface
from ..interfaces.embedding_interface import EmbeddingInterface
from .patterns import ExtractionPatterns, SkillOntology, CompositeSkillDecomposer

logger = logging.getLogger(__name__)


class SkillExtractor:
    """Advanced skill extraction from course descriptions"""
    
    def __init__(self, 
                 genai: Optional[GenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 use_genai: bool = True):
        """
        Initialize skill extractor
        
        Args:
            genai: GenAI interface for advanced extraction
            embeddings: Embedding interface for similarity
            use_genai: Whether to use GenAI for extraction
        """
        self.genai = genai
        self.embeddings = embeddings
        self.use_genai = use_genai and genai is not None
        
        self.patterns = ExtractionPatterns()
        self.ontology = SkillOntology()
        self.decomposer = CompositeSkillDecomposer()
        
        # Cache for processed texts
        self.cache = {}
    
    def extract_from_vet_unit(self, unit: UnitOfCompetency) -> List[Skill]:
        """
        Extract skills from VET unit of competency
        
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
                ai_skills = self.genai.extract_skills_prompt(full_text, "VET unit")
                skills.extend(self._convert_ai_skills(ai_skills, f"VET:{unit.code}"))
            except Exception as e:
                logger.warning(f"GenAI extraction failed: {e}")
        
        # Pattern-based extraction
        pattern_skills = self._extract_with_patterns(full_text, "VET", unit.code)
        skills.extend(pattern_skills)
        
        # Parse learning outcomes
        for outcome in unit.learning_outcomes:
            outcome_skills = self._parse_learning_outcome(outcome, f"VET:{unit.code}")
            skills.extend(outcome_skills)
        
        # Extract from assessment requirements
        if unit.assessment_requirements:
            assessment_skills = self._extract_from_assessment(
                unit.assessment_requirements, 
                f"VET:{unit.code}"
            )
            skills.extend(assessment_skills)
        
        # Extract implicit skills
        implicit_skills = self._extract_implicit_skills(full_text, skills)
        skills.extend(implicit_skills)
        
        # Handle composite skills
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
        
        logger.info(f"Extracted {len(skills)} skills from {unit.code}")
        return skills
    
    def extract_from_uni_course(self, course: UniCourse) -> List[Skill]:
        """
        Extract skills from university course
        
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
                ai_skills = self.genai.extract_skills_prompt(full_text, "university course")
                skills.extend(self._convert_ai_skills(ai_skills, f"UNI:{course.code}"))
            except Exception as e:
                logger.warning(f"GenAI extraction failed: {e}")
        
        # Pattern-based extraction
        pattern_skills = self._extract_with_patterns(full_text, "UNI", course.code)
        skills.extend(pattern_skills)
        
        # Parse learning outcomes
        for outcome in course.learning_outcomes:
            outcome_skills = self._parse_learning_outcome(outcome, f"UNI:{course.code}")
            skills.extend(outcome_skills)
        
        # Extract from topics
        for topic in course.topics:
            topic_skills = self._extract_from_topic(topic, course.year)
            skills.extend(topic_skills)
        
        # Extract from assessment
        if course.assessment:
            assessment_skills = self._extract_from_assessment(
                course.assessment,
                f"UNI:{course.code}"
            )
            skills.extend(assessment_skills)
        
        # Extract from prerequisites
        prereq_skills = self._extract_from_prerequisites(course.prerequisites)
        skills.extend(prereq_skills)
        
        # Extract implicit skills
        implicit_skills = self._extract_implicit_skills(full_text, skills)
        skills.extend(implicit_skills)
        
        # Handle composite skills
        skills = self._handle_composite_skills(skills)
        
        # Deduplicate and validate
        skills = self._deduplicate_skills(skills)
        
        # Adjust levels based on year
        for skill in skills:
            skill.level = self._adjust_level_by_year(skill.level, course.year)
            if skill.depth == SkillDepth.APPLY and course.year >= 3:
                skill.depth = SkillDepth.ANALYZE
        
        # Cache and assign
        self.cache[cache_key] = skills
        course.extracted_skills = skills
        
        logger.info(f"Extracted {len(skills)} skills from {course.code}")
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
                    level=SkillLevel.COMPETENT,  # Default
                    depth=self._determine_depth_from_text(text_lower),
                    context=self._determine_context(text_lower),
                    keywords=self._extract_keywords(skill_name, text_lower),
                    evidence_type=pattern_type,
                    confidence=0.7,  # Pattern-based extraction confidence
                    source=f"{source_type}:{source_code}"
                )
                skills.append(skill)
        
        return skills
    
    def _parse_learning_outcome(self, outcome: str, source: str) -> List[Skill]:
        """Parse a learning outcome statement for skills"""
        skills = []
        outcome_lower = outcome.lower()
        
        # Determine cognitive depth from action verbs
        depth = SkillDepth.APPLY  # Default
        for depth_level, verbs in self.patterns.ACTION_VERB_PATTERNS.items():
            if any(verb in outcome_lower for verb in verbs):
                depth = SkillDepth.from_verb(verbs[0])
                break
        
        # Extract skill phrases from outcome
        for pattern, pattern_type in self.patterns.SKILL_PATTERNS[:5]:  # Focus on main patterns
            matches = re.findall(pattern, outcome_lower)
            for match in matches:
                skill_name = self._clean_skill_name(match)
                if skill_name:
                    skill = Skill(
                        name=skill_name,
                        category=self._categorize_skill(skill_name),
                        level=SkillLevel.COMPETENT,
                        depth=depth,
                        context=SkillContext.HYBRID,
                        confidence=0.9,  # High confidence from learning outcomes
                        source=source
                    )
                    skills.append(skill)
        
        return skills
    
    def _extract_from_topic(self, topic: str, year: int) -> List[Skill]:
        """Extract skills from course topic"""
        topic_clean = self._clean_skill_name(topic)
        if not topic_clean:
            return []
        
        skill = Skill(
            name=topic_clean,
            category=self._categorize_skill(topic_clean),
            level=self._adjust_level_by_year(SkillLevel.COMPETENT, year),
            depth=self._parse_depth_by_year(year),
            context=SkillContext.THEORETICAL,  # Topics are typically theoretical
            confidence=0.7,
            source=f"topic_year{year}"
        )
        
        return [skill]
    
    def _extract_from_assessment(self, assessment_text: str, source: str) -> List[Skill]:
        """Extract skills from assessment descriptions"""
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
                
                for match in matches[:3]:  # Limit to avoid noise
                    skill_name = f"{indicator} {match.strip()}"
                    skill = Skill(
                        name=skill_name,
                        category=SkillCategory.COGNITIVE,
                        level=SkillLevel.COMPETENT,
                        depth=SkillDepth.from_verb(indicator),
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
                depth=SkillDepth.UNDERSTAND,
                context=SkillContext.THEORETICAL,
                confidence=0.8,
                source="prerequisite"
            )
            skills.append(skill)
        
        return skills
    
    def _extract_implicit_skills(self, text: str, explicit_skills: List[Skill]) -> List[Skill]:
        """Extract implicit skills using inference rules"""
        implicit_skills = []
        text_lower = text.lower()
        explicit_names = {s.name.lower() for s in explicit_skills}
        
        # Use GenAI if available
        if self.use_genai and self.genai:
            try:
                ai_implicit = self.genai.identify_implicit_skills(
                    text, 
                    list(explicit_names)[:20]  # Limit for API
                )
                for skill_dict in ai_implicit:
                    if skill_dict["name"].lower() not in explicit_names:
                        skill = Skill(
                            name=skill_dict["name"],
                            category=SkillCategory.TECHNICAL,
                            level=SkillLevel.COMPETENT,
                            depth=SkillDepth.APPLY,
                            context=SkillContext.HYBRID,
                            confidence=skill_dict.get("confidence", 0.5),
                            source="implicit_ai"
                        )
                        implicit_skills.append(skill)
            except Exception as e:
                logger.debug(f"Failed to extract implicit skills with AI: {e}")
        
        # Use ontology-based inference
        for explicit_skill in explicit_skills:
            implied = self.ontology.get_implied_skills(explicit_skill.name)
            for implied_name in implied:
                if implied_name.lower() not in explicit_names:
                    skill = Skill(
                        name=implied_name,
                        category=self._categorize_skill(implied_name),
                        level=explicit_skill.level,  # Inherit from parent skill
                        depth=SkillDepth.APPLY,
                        context=explicit_skill.context,
                        confidence=0.6,  # Lower confidence for inferred
                        source="implicit_inference"
                    )
                    implicit_skills.append(skill)
                    explicit_names.add(implied_name.lower())  # Prevent duplicates
        
        return implicit_skills
    
    def _handle_composite_skills(self, skills: List[Skill]) -> List[Skill]:
        """Handle composite skills by decomposing them"""
        expanded_skills = []
        
        for skill in skills:
            if self.decomposer.is_composite(skill.name):
                # Decompose the skill
                components = self.decomposer.decompose(skill.name)
                
                # Add original composite skill
                expanded_skills.append(skill)
                
                # Add component skills
                for component_name in components:
                    if component_name != skill.name:  # Avoid duplicate
                        component_skill = Skill(
                            name=component_name,
                            category=skill.category,
                            level=skill.level,
                            depth=skill.depth,
                            context=skill.context,
                            confidence=skill.confidence * 0.8,  # Slightly lower
                            source=f"decomposed_from_{skill.source}"
                        )
                        expanded_skills.append(component_skill)
            else:
                expanded_skills.append(skill)
        
        return expanded_skills
    
    def _convert_ai_skills(self, ai_skills: List[Dict], source: str) -> List[Skill]:
        """Convert AI-extracted skills to Skill objects"""
        skills = []
        
        for ai_skill in ai_skills:
            try:
                skill = Skill(
                    name=ai_skill["name"],
                    category=SkillCategory(ai_skill.get("category", "technical")),
                    level=SkillLevel.from_string(ai_skill.get("level", "competent")),
                    depth=SkillDepth.from_verb(ai_skill.get("depth", "apply")),
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
        
        # Use ontology categorization
        ontology_category = self.ontology.categorize_skill(skill_name)
        if "software" in ontology_category or "data" in ontology_category:
            return SkillCategory.TECHNICAL
        elif "engineering" in ontology_category:
            return SkillCategory.PRACTICAL
        
        # Default
        return SkillCategory.TECHNICAL
    
    def _determine_depth_from_text(self, text: str) -> SkillDepth:
        """Determine cognitive depth from text content"""
        text_lower = text.lower()
        
        # Check for depth indicators
        depth_indicators = {
            SkillDepth.CREATE: ["create", "design", "develop", "innovate", "invent"],
            SkillDepth.EVALUATE: ["evaluate", "assess", "critique", "judge", "validate"],
            SkillDepth.ANALYZE: ["analyze", "examine", "investigate", "compare"],
            SkillDepth.APPLY: ["apply", "implement", "use", "demonstrate"],
            SkillDepth.UNDERSTAND: ["understand", "explain", "describe", "interpret"],
            SkillDepth.REMEMBER: ["identify", "list", "name", "recall"]
        }
        
        # Count occurrences of each depth level
        depth_counts = {}
        for depth, indicators in depth_indicators.items():
            count = sum(1 for ind in indicators if ind in text_lower)
            if count > 0:
                depth_counts[depth] = count
        
        # Return highest occurring depth
        if depth_counts:
            return max(depth_counts.items(), key=lambda x: x[1])[0]
        
        return SkillDepth.APPLY  # Default
    
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
        context_lower = context_text.lower()
        if skill_name.lower() in context_lower:
            # Get surrounding context
            pattern = f"\\b\\w+\\s+{re.escape(skill_name.lower())}\\s+\\w+\\b"
            matches = re.findall(pattern, context_lower)
            
            for match in matches[:5]:  # Limit keywords
                words = match.split()
                for word in words:
                    if word not in skill_words and len(word) > 3:
                        keywords.append(word)
        
        return list(set(keywords))[:10]  # Unique and limited
    
    def _adjust_level_by_year(self, base_level: SkillLevel, year: int) -> SkillLevel:
        """Adjust skill level based on university year"""
        if year == 1:
            return min(base_level, SkillLevel.ADVANCED_BEGINNER)
        elif year == 2:
            return base_level
        elif year == 3:
            return max(base_level, SkillLevel.COMPETENT)
        else:  # year 4+
            return max(base_level, SkillLevel.PROFICIENT)
    
    def _parse_depth_by_year(self, year: int) -> SkillDepth:
        """Expected cognitive depth by year"""
        year_depth_map = {
            1: SkillDepth.UNDERSTAND,
            2: SkillDepth.APPLY,
            3: SkillDepth.ANALYZE,
            4: SkillDepth.EVALUATE
        }
        return year_depth_map.get(year, SkillDepth.APPLY)
    
    def _deduplicate_skills(self, skills: List[Skill]) -> List[Skill]:
        """Remove duplicate skills, keeping highest confidence"""
        skill_dict = {}
        
        for skill in skills:
            key = skill.name.lower().strip()
            
            if key not in skill_dict:
                skill_dict[key] = skill
            else:
                # Keep the one with higher confidence
                if skill.confidence > skill_dict[key].confidence:
                    skill_dict[key] = skill
                # Merge keywords
                elif skill.keywords:
                    existing_keywords = set(skill_dict[key].keywords)
                    existing_keywords.update(skill.keywords)
                    skill_dict[key].keywords = list(existing_keywords)[:10]
        
        return list(skill_dict.values())
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.cache.clear()
        logger.info("Extraction cache cleared")
