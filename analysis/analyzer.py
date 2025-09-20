"""
Main credit transfer analyzer - Updated to support OpenAI extractor
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
from config import Config

from models.base_models import (
    VETQualification, UniQualification, CreditTransferRecommendation,
    UnitOfCompetency, UniCourse, SkillMapping
)
from models.enums import RecommendationType
from extraction.skill_extractor import SkillExtractor
from mapping.skill_mapper import SkillMapper
from mapping.edge_cases import EdgeCaseHandler
from interfaces.genai_interface import GenAIInterface
from interfaces.embedding_interface import EmbeddingInterface
if Config.USE_VLLM:
    from interfaces.vllm_genai_interface import VLLMGenAIInterface
    from extraction.vllm_skill_extractor import VLLMSkillExtractor
from extraction.openai_skill_extractor import OpenAISkillExtractor

logger = logging.getLogger(__name__)


class CreditTransferAnalyzer:
    """Main analyzer for credit transfer recommendations"""
    
    def __init__(self,
                 genai: Optional[GenAIInterface] = None,
                 embeddings: Optional[EmbeddingInterface] = None,
                 config: Optional[Dict] = None):
        """
        Initialize credit transfer analyzer
        
        Args:
            genai: GenAI interface for advanced extraction
            embeddings: Embedding interface for similarity
            config: Configuration dictionary
        """
        self.genai = genai
        self.embeddings = embeddings
        self.config = config or {}
        
        # Initialize components based on interface type
        if Config.USE_VLLM and isinstance(genai, VLLMGenAIInterface):
            # Use optimized vLLM extractor for batch processing
            self.extractor = VLLMSkillExtractor(genai, embeddings)
            logger.info("Using vLLM skill extractor for batch processing")
            
        elif isinstance(genai, GenAIInterface) and hasattr(genai, 'client'):
            # Use OpenAI extractor for Azure OpenAI (individual requests, no batch)
            delay = self.config.get("openai_delay_between_requests", 1.0)
            
            self.extractor = OpenAISkillExtractor(
                genai, 
                embeddings, 
                delay_between_requests=delay
            )
            logger.info("Using OpenAI skill extractor for Azure OpenAI API (individual requests)")
            
        else:
            # Use standard extractor
            self.extractor = SkillExtractor(genai, embeddings)
            logger.info("Using standard skill extractor")
        
        self.mapper = SkillMapper(embeddings)
        self.edge_handler = EdgeCaseHandler()
        
        # Configuration
        self.min_alignment_score = self.config.get("min_alignment_score", 0.5)
        self.combination_limit = self.config.get("max_unit_combination", 3)
        
        # Analysis cache
        self.analysis_cache = {}
    
    def analyze_transfer(self,
                        vet_qual: VETQualification,
                        uni_qual: UniQualification,
                        target_courses: Optional[List[str]] = None) -> List[CreditTransferRecommendation]:
        """
        Analyze credit transfer possibilities
        
        Args:
            vet_qual: VET qualification to analyze
            uni_qual: University qualification target
            target_courses: Optional list of specific course codes to analyze
            
        Returns:
            List of credit transfer recommendations
        """
        logger.info(f"Starting credit transfer analysis: {vet_qual.code} -> {uni_qual.code}")
        
        recommendations = []
        
        # Check if we have vLLM batch extractor
        if Config.USE_VLLM and isinstance(self.extractor, VLLMSkillExtractor):
            # Use batch extraction for efficiency with vLLM
            logger.info("Using batch extraction for VET units...")
            self.extractor.extract_from_vet_qualification(vet_qual)
            
            logger.info("Using batch extraction for University courses...")
            if target_courses:
                # Filter courses first
                filtered_qual = UniQualification(
                    code=uni_qual.code,
                    name=uni_qual.name,
                    courses=[c for c in uni_qual.courses if c.code in target_courses]
                )
                self.extractor.extract_from_uni_qualification(filtered_qual)
                courses_to_analyze = filtered_qual.courses
            else:
                self.extractor.extract_from_uni_qualification(uni_qual)
                courses_to_analyze = uni_qual.courses
        else:
            # Standard extraction (one by one)
            logger.info("Extracting skills from VET units...")
            for unit in vet_qual.units:
                if not unit.extracted_skills:
                    self.extractor.extract_from_vet_unit(unit)
            
            # Filter target courses if specified
            courses_to_analyze = uni_qual.courses
            if target_courses:
                courses_to_analyze = [c for c in uni_qual.courses if c.code in target_courses]
            
            # Extract skills from university courses
            logger.info(f"Extracting skills from {len(courses_to_analyze)} university courses...")
            for course in courses_to_analyze:
                if not course.extracted_skills:
                    self.extractor.extract_from_uni_course(course)
        
        # Analyze each university course
        for course in courses_to_analyze:
            logger.info(f"Analyzing transfers for {course.code}: {course.name}")
            
            # Try single unit mappings
            single_recs = self._analyze_single_mappings(vet_qual.units, course)
            recommendations.extend(single_recs)
            
            # Try combination mappings if enabled
            if self.combination_limit > 1:
                combo_recs = self._analyze_combination_mappings(vet_qual.units, course)
                recommendations.extend(combo_recs)
        
        # Filter and sort recommendations
        recommendations = self._filter_recommendations(recommendations)
        recommendations.sort(key=lambda x: (x.alignment_score, x.confidence), reverse=True)
        
        # Add analysis metadata
        self._add_analysis_metadata(recommendations, vet_qual, uni_qual)
        
        logger.info(f"Analysis complete: {len(recommendations)} recommendations generated")
        
        return recommendations
    
    def _analyze_single_mappings(self,
                                 units: List[UnitOfCompetency],
                                 course: UniCourse) -> List[CreditTransferRecommendation]:
        """Analyze single unit to course mappings"""
        recommendations = []
        
        for unit in units:
            # Check cache
            cache_key = f"{unit.code}_{course.code}"
            if cache_key in self.analysis_cache:
                rec = self.analysis_cache[cache_key]
                if rec.alignment_score >= self.min_alignment_score:
                    recommendations.append(rec)
                continue
            
            # Perform analysis
            rec = self._analyze_single_mapping(unit, course)
            
            # Cache result
            self.analysis_cache[cache_key] = rec
            
            # Add if meets threshold
            if rec.alignment_score >= self.min_alignment_score:
                recommendations.append(rec)
                logger.debug(f"Single mapping {unit.code} -> {course.code}: {rec.alignment_score:.2%}")
        
        return recommendations
    
    def _analyze_single_mapping(self,
                               unit: UnitOfCompetency,
                               course: UniCourse) -> CreditTransferRecommendation:
        """Analyze single unit to course mapping"""
        
        # Map skills
        mapping = self.mapper.map_skills(unit.extracted_skills, course.extracted_skills)
        
        # Handle edge cases
        edge_cases = self.edge_handler.process_edge_cases([unit], course, mapping)
        
        # Calculate scores
        alignment_score = self._calculate_alignment_score(mapping, edge_cases)
        skill_coverage = self._calculate_skill_coverage_breakdown(mapping)
        confidence = self._calculate_confidence(mapping, edge_cases)
        
        # Determine recommendation type
        recommendation_type = self._determine_recommendation_type(
            alignment_score, mapping, edge_cases
        )
        
        # Identify conditions
        conditions = self._identify_conditions(mapping, edge_cases)
        
        # Generate evidence
        evidence = self._generate_evidence(mapping, edge_cases)
        
        # Create recommendation
        rec = CreditTransferRecommendation(
            vet_units=[unit],
            uni_course=course,
            alignment_score=alignment_score,
            skill_coverage=skill_coverage,
            gaps=mapping.unmapped_uni,
            evidence=evidence,
            recommendation=recommendation_type,
            conditions=conditions,
            confidence=confidence,
            edge_case_results=edge_cases
        )
        
        return rec
    
    def _analyze_combination_mappings(self,
                                      units: List[UnitOfCompetency],
                                      course: UniCourse) -> List[CreditTransferRecommendation]:
        """Analyze combinations of units mapping to course"""
        recommendations = []
        
        from itertools import combinations
        
        # Try combinations up to the limit
        for r in range(2, min(self.combination_limit + 1, len(units) + 1)):
            for combo in combinations(units, r):
                # Skip if too many units
                if len(combo) > self.combination_limit:
                    continue
                
                # Combine skills from all units
                combined_skills = []
                for unit in combo:
                    combined_skills.extend(unit.extracted_skills)
                
                # Map combined skills
                mapping = self.mapper.map_skills(combined_skills, course.extracted_skills)
                
                # Only proceed if combination significantly improves coverage
                if mapping.coverage_score < 0.7:
                    continue
                
                # Perform full analysis
                edge_cases = self.edge_handler.process_edge_cases(list(combo), course, mapping)
                alignment_score = self._calculate_alignment_score(mapping, edge_cases)
                
                if alignment_score >= self.min_alignment_score * 1.2:  # Higher threshold for combinations
                    rec = CreditTransferRecommendation(
                        vet_units=list(combo),
                        uni_course=course,
                        alignment_score=alignment_score,
                        skill_coverage=self._calculate_skill_coverage_breakdown(mapping),
                        gaps=mapping.unmapped_uni,
                        evidence=self._generate_evidence(mapping, edge_cases),
                        recommendation=self._determine_recommendation_type(
                            alignment_score, mapping, edge_cases
                        ),
                        conditions=self._identify_conditions(mapping, edge_cases),
                        confidence=self._calculate_confidence(mapping, edge_cases),
                        edge_case_results=edge_cases
                    )
                    recommendations.append(rec)
                    
                    logger.debug(
                        f"Combination {'+'.join(u.code for u in combo)} -> "
                        f"{course.code}: {alignment_score:.2%}"
                    )
        
        return recommendations
    
    def _calculate_alignment_score(self,
                                   mapping: SkillMapping,
                                   edge_cases: Dict[str, Any]) -> float:
        """Calculate overall alignment score"""
        
        # Base weights (adjusted without depth component)
        weights = {
            "coverage": 0.5,
            "context": 0.25,
            "quality": 0.15,
            "edge_penalty": 0.1
        }
        
        # Calculate quality score
        quality_score = 0.0
        if mapping.direct_matches:
            quality_scores = [m["quality"]["overall"] for m in mapping.direct_matches]
            quality_score = sum(quality_scores) / len(quality_scores)
        
        # Calculate edge case penalty
        edge_penalty = 0.0
        
        if "context_imbalance" in edge_cases:
            edge_penalty += edge_cases["context_imbalance"].get("imbalance_score", 0) * 0.3
        
        if "outdated_content" in edge_cases:
            if edge_cases["outdated_content"].get("currency_issues"):
                edge_penalty += 0.2
        
        # Calculate final score
        score = (
            mapping.coverage_score * weights["coverage"] +
            mapping.context_alignment * weights["context"] +
            quality_score * weights["quality"] -
            edge_penalty * weights["edge_penalty"]
        )
        
        return max(0.0, min(1.0, score))
    
    def _determine_recommendation_type(self,
                                       score: float,
                                       mapping: SkillMapping,
                                       edge_cases: Dict[str, Any]) -> RecommendationType:
        """Determine recommendation type based on analysis"""
        
        has_gaps = len(mapping.unmapped_uni) > 0
        has_major_issues = any([
            edge_cases.get("outdated_content", {}).get("estimated_update_effort") == "high",
            edge_cases.get("context_imbalance", {}).get("imbalance_score", 0) > 0.5
        ])
        
        if score >= 0.8 and not has_gaps and not has_major_issues:
            return RecommendationType.FULL
        elif score >= 0.7 and not has_major_issues:
            return RecommendationType.CONDITIONAL
        elif score >= 0.5:
            return RecommendationType.PARTIAL
        else:
            return RecommendationType.NONE
    
    def _identify_conditions(self,
                            mapping: SkillMapping,
                            edge_cases: Dict[str, Any]) -> List[str]:
        """Identify conditions for credit transfer"""
        conditions = []
        
        # Missing skills
        if mapping.unmapped_uni:
            skill_names = [s.name for s in mapping.unmapped_uni[:3]]  # Limit display
            conditions.append(f"Bridge missing skills: {', '.join(skill_names)}")
        
        # Context imbalance
        if "context_imbalance" in edge_cases:
            conditions.extend(edge_cases["context_imbalance"].get("bridging_requirements", []))
        
        # Outdated content
        if "outdated_content" in edge_cases:
            conditions.extend(edge_cases["outdated_content"].get("update_requirements", []))
        
        # Prerequisites
        if "prerequisite_chain" in edge_cases:
            missing = edge_cases["prerequisite_chain"].get("missing_prerequisites", [])
            if missing:
                conditions.append(f"Complete prerequisites: {', '.join(missing[:3])}")
        
        return conditions
    
    def _generate_evidence(self,
                          mapping: SkillMapping,
                          edge_cases: Dict[str, Any]) -> List[str]:
        """Generate evidence statements for recommendation"""
        evidence = []
        
        # Skill matches
        if mapping.direct_matches:
            evidence.append(f"{len(mapping.direct_matches)} direct skill matches")
        
        if mapping.partial_matches:
            evidence.append(f"{len(mapping.partial_matches)} partial skill matches")
        
        # Coverage metrics
        evidence.append(f"Skill coverage: {mapping.coverage_score:.1%}")
        
        if mapping.context_alignment > 0.8:
            evidence.append("Good practical/theoretical balance")
        
        # Edge case findings
        if "split_to_single" in edge_cases:
            if edge_cases["split_to_single"].get("total_coverage", 0) > 0.8:
                evidence.append("Unit combination provides comprehensive coverage")
        
        if "credit_hours" in edge_cases:
            if not edge_cases["credit_hours"].get("adjustment_needed", False):
                evidence.append("Credit hour alignment acceptable")
        
        return evidence
    
    def _calculate_skill_coverage_breakdown(self,
                                           mapping: SkillMapping) -> Dict[str, float]:
        """Calculate detailed skill coverage breakdown"""
        from collections import defaultdict
        
        breakdown = defaultdict(float)
        category_totals = defaultdict(int)
        category_matched = defaultdict(float)
        
        # Count totals by category
        for match in mapping.direct_matches:
            category = match["uni_skill"].category.value
            category_matched[category] += 1.0
            category_totals[category] += 1
        
        for match in mapping.partial_matches:
            category = match["uni_skill"].category.value
            category_matched[category] += 0.5
            category_totals[category] += 1
        
        for skill in mapping.unmapped_uni:
            category = skill.category.value
            category_totals[category] += 1
        
        # Calculate percentages
        for category in category_totals:
            if category_totals[category] > 0:
                breakdown[category] = category_matched[category] / category_totals[category]
        
        return dict(breakdown)
    
    def _calculate_confidence(self,
                             mapping: SkillMapping,
                             edge_cases: Dict[str, Any]) -> float:
        """Calculate confidence in the recommendation"""
        confidence = 1.0
        
        # Reduce for unmapped skills
        unmapped_ratio = len(mapping.unmapped_uni) / (
            len(mapping.direct_matches) + len(mapping.partial_matches) + len(mapping.unmapped_uni)
        ) if (mapping.direct_matches or mapping.partial_matches or mapping.unmapped_uni) else 0
        
        confidence -= unmapped_ratio * 0.3
        
        # Reduce for edge case issues
        if "context_imbalance" in edge_cases:
            imbalance = edge_cases["context_imbalance"].get("imbalance_score", 0)
            confidence -= imbalance * 0.2
        
        if "outdated_content" in edge_cases:
            if edge_cases["outdated_content"].get("currency_issues"):
                confidence -= 0.15
        
        # Boost for strong direct matches
        if mapping.direct_matches:
            direct_ratio = len(mapping.direct_matches) / (
                len(mapping.direct_matches) + len(mapping.partial_matches)
            ) if (mapping.direct_matches or mapping.partial_matches) else 0
            
            if direct_ratio > 0.7:
                confidence += 0.1
        
        return max(0.3, min(1.0, confidence))
    
    def _filter_recommendations(self,
                               recommendations: List[CreditTransferRecommendation]
                               ) -> List[CreditTransferRecommendation]:
        """Filter recommendations to avoid duplicates and conflicts"""
        filtered = []
        seen_mappings = set()
        
        for rec in recommendations:
            # Create unique key for this mapping
            vet_codes = tuple(sorted(rec.get_vet_unit_codes()))
            uni_code = rec.uni_course.code
            mapping_key = (vet_codes, uni_code)
            
            # Skip if already seen
            if mapping_key in seen_mappings:
                continue
            
            seen_mappings.add(mapping_key)
            
            # Skip if recommendation is "none"
            if rec.recommendation == RecommendationType.NONE:
                continue
            
            filtered.append(rec)
        
        return filtered
    
    def _add_analysis_metadata(self,
                               recommendations: List[CreditTransferRecommendation],
                               vet_qual: VETQualification,
                               uni_qual: UniQualification):
        """Add metadata to recommendations"""
        timestamp = datetime.now().isoformat()
        
        for rec in recommendations:
            rec.metadata.update({
                "vet_qualification": vet_qual.code,
                "uni_qualification": uni_qual.code,
                "analysis_timestamp": timestamp,
                "analyzer_version": "1.0.0",
                "extractor_type": type(self.extractor).__name__
            })
    
    def export_recommendations(self,
                               recommendations: List[CreditTransferRecommendation],
                               filepath: str):
        """Export recommendations to JSON file"""
        data = {
            "recommendations": [rec.to_dict() for rec in recommendations],
            "summary": self._generate_summary(recommendations),
            "timestamp": datetime.now().isoformat(),
            "extractor_stats": self._get_extractor_stats()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(recommendations)} recommendations to {filepath}")
    
    def _generate_summary(self,
                         recommendations: List[CreditTransferRecommendation]) -> Dict:
        """Generate summary of recommendations"""
        full = [r for r in recommendations if r.recommendation == RecommendationType.FULL]
        conditional = [r for r in recommendations if r.recommendation == RecommendationType.CONDITIONAL]
        partial = [r for r in recommendations if r.recommendation == RecommendationType.PARTIAL]
        
        return {
            "total_recommendations": len(recommendations),
            "full_credit": len(full),
            "conditional_credit": len(conditional),
            "partial_credit": len(partial),
            "average_alignment": sum(r.alignment_score for r in recommendations) / len(recommendations) if recommendations else 0,
            "average_confidence": sum(r.confidence for r in recommendations) / len(recommendations) if recommendations else 0
        }
    
    def _get_extractor_stats(self) -> Dict:
        """Get statistics from the extractor if available"""
        if hasattr(self.extractor, 'get_extraction_stats'):
            return self.extractor.get_extraction_stats()
        elif hasattr(self.extractor, 'cache'):
            return {"cache_size": len(self.extractor.cache)}
        else:
            return {"extractor_type": type(self.extractor).__name__}