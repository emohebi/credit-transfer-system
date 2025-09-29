"""
Simplified credit transfer analyzer with progressive analysis
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import numpy as np

from models.base_models import (
    VETQualification, UniQualification, 
    CreditTransferRecommendation, Skill
)
from models.enums import RecommendationType
from extraction.unified_extractor import UnifiedSkillExtractor
from mapping.cluster_matcher import ClusterSkillMatcher
from utils.prompt_manager import PromptManager
from mapping.unified_scorer import UnifiedScorer, MatchScore


logger = logging.getLogger(__name__)


class SimplifiedAnalyzer:
    """Simplified analyzer with cleaner logic and progressive analysis"""
    
    def __init__(self, genai=None, embeddings=None, config=None):
        self.genai = genai
        self.embeddings = embeddings
        self.config = config or {}
        
        # Check if robust mode is enabled
        if self.config.get("ensemble_runs".upper(), 0) > 1:
            from extraction.ensemble_extractor import EnsembleSkillExtractor
            base_extractor = UnifiedSkillExtractor(genai, config)
            
            # Create ensemble extractor with embeddings for similarity matching
            ensemble_extractor = EnsembleSkillExtractor(
                base_extractor, 
                num_runs=self.config.get("ensemble_runs".upper(), 3),
                embeddings=embeddings,  # Pass the embedding model
                similarity_threshold=self.config.get("ensemble_similarity_threshold".upper(), 0.9)
            )
            # Use the ensemble extractor
            self.extractor = ensemble_extractor
        else:
            self.extractor = UnifiedSkillExtractor(genai, config)
        
        self.matcher = ClusterSkillMatcher(embeddings, config)
        self.prompt_manager = PromptManager()
        self.unified_scorer = UnifiedScorer()
        
        # Simple thresholds
        self.thresholds = {
            "full": self.config.get("FULL_TRANSFER", 0.8),
            "partial": self.config.get("PARTIAL_TRANSFER", 0.5),
            "minimum": self.config.get("MINIMUM_VIABLE", 0.3)
        }
        
    def _validate_qualification_data(self, vet_qual: VETQualification, uni_qual: UniQualification):
        """Validate and fix qualification data before analysis"""
        # Fix missing nominal hours in VET units
        for unit in vet_qual.units:
            if unit.nominal_hours is None:
                logger.warning(f"Unit {unit.code} has no nominal_hours specified, defaulting to 0")
                unit.nominal_hours = 0
        
        # Fix missing credit points in Uni courses
        for course in uni_qual.courses:
            if course.credit_points is None:
                logger.warning(f"Course {course.code} has no credit_points specified, defaulting to 0")
                course.credit_points = 0
    
    def analyze(self, 
                vet_qual: VETQualification,
                uni_qual: UniQualification,
                depth: str = "auto") -> List[CreditTransferRecommendation]:
        """
        Analyze credit transfer with progressive depth
        
        Args:
            vet_qual: VET qualification
            uni_qual: University qualification  
            depth: Analysis depth ('quick', 'balanced', 'deep', or 'auto')
            
        Returns:
            List of recommendations
        """
        self._validate_qualification_data(vet_qual, uni_qual)
        
        logger.info(f"Starting simplified analysis: {vet_qual.code} -> {uni_qual.code}")
        
        # Determine depth automatically if needed
        if depth == "auto":
            depth = self._determine_depth(vet_qual, uni_qual)
        
        # Progressive analysis based on depth
        if depth == "quick":
            return self._quick_analysis(vet_qual, uni_qual)
        elif depth == "balanced":
            return self._balanced_analysis(vet_qual, uni_qual)
        else:  # deep
            return self._deep_analysis(vet_qual, uni_qual)
    
    def _determine_depth(self, vet_qual, uni_qual) -> str:
        """Automatically determine appropriate analysis depth"""
        
        # Use quick analysis for large qualifications
        if len(vet_qual.units) * len(uni_qual.courses) > 100:
            return "quick"
        # Use deep for small, important analyses
        elif len(vet_qual.units) < 5 and len(uni_qual.courses) < 5:
            return "deep"
        # Default to balanced
        else:
            return "balanced"
    
    def _quick_analysis(self, vet_qual, uni_qual) -> List[CreditTransferRecommendation]:
        """Quick analysis using embeddings only"""
        logger.info("Performing quick analysis")
        
        # Extract skills (uses cache if available)
        vet_skills = self.extractor.extract_skills(vet_qual.units)
        uni_skills = self.extractor.extract_skills(uni_qual.courses)
        logger.info(f"Extracted {sum(len(s) for s in vet_skills.values())} VET skills and {sum(len(s) for s in uni_skills.values())} Uni skills")
        recommendations = []
        
        # Simple matching for each course
        for course in uni_qual.courses:
            if course.code not in uni_skills:
                continue
            
            course_skills = uni_skills[course.code]
            
            # Find best matching VET units using clustering
            best_match = None
            best_score = 0
            
            for unit_code, unit_skills in vet_skills.items():
                # Quick similarity check
                match_result = self.matcher.match_skills(unit_skills, course_skills)
                score = match_result["statistics"]["uni_coverage"]
                
                if score > best_score:
                    best_score = score
                    best_match = (unit_code, match_result)
            
            if best_match and best_score >= self.thresholds["minimum"]:
                # Create recommendation with edge case analysis
                unit = next(u for u in vet_qual.units if u.code == best_match[0])
                
                # Run edge case analysis if enabled
                edge_case_results = {}
                if self.config.get("EDGE_CASES_ENABLED", False):
                    from mapping.edge_cases import EdgeCaseHandler
                    edge_handler = EdgeCaseHandler(self.genai)
                    edge_case_results = edge_handler.process_edge_cases(
                        [unit], course, None
                    )
                
                rec = self._create_recommendation(
                    [unit], course, best_match[1], edge_case_results
                )
                if hasattr(self.matcher, 'last_semantic_clusters'):
                    rec.metadata['semantic_clusters'] = self.matcher.last_semantic_clusters
                recommendations.append(rec)
        
        return recommendations
    
    def _balanced_analysis(self, vet_qual, uni_qual) -> List[CreditTransferRecommendation]:
        """Balanced analysis with AI refinement"""
        logger.info("Performing balanced analysis")
        
        # Start with quick analysis
        quick_recs = self._quick_analysis(vet_qual, uni_qual)
        
        # Refine top recommendations with AI
        refined_recs = []
        
        for rec in sorted(quick_recs, key=lambda x: x.alignment_score, reverse=True)[:20]:
            # Use AI to refine the match
            if self.genai:
                refined_score = self._refine_with_ai(rec)
                rec.alignment_score = refined_score
                rec.confidence = min(1.0, rec.confidence * 1.1)  # Boost confidence
            
            refined_recs.append(rec)
        
        # Add any unrefined recommendations
        refined_codes = {r.uni_course.code for r in refined_recs}
        for rec in quick_recs:
            if rec.uni_course.code not in refined_codes:
                refined_recs.append(rec)
        
        return refined_recs
    
    def _deep_analysis(self, vet_qual, uni_qual) -> List[CreditTransferRecommendation]:
        """Deep analysis with full features"""
        logger.info("Performing deep analysis")
        
        # Get balanced analysis
        balanced_recs = self._balanced_analysis(vet_qual, uni_qual)
        
        # Enhance with additional analysis
        enhanced_recs = []
        
        for rec in balanced_recs:
            # Check for combinations
            if rec.alignment_score < self.thresholds["full"]:
                combo_rec = self._check_combinations(
                    rec.uni_course, vet_qual.units, uni_qual
                )
                if combo_rec and combo_rec.alignment_score > rec.alignment_score:
                    enhanced_recs.append(combo_rec)
                    continue
            
            # Add edge case analysis if configured
            if self.config.get("EDGE_CASES_ENABLED", False):
                rec.edge_case_results = self._simple_edge_check(rec)
            
            enhanced_recs.append(rec)
        
        return enhanced_recs
    
    def _create_recommendation(self, 
                           vet_units: List,
                           uni_course: Any,
                           match_result: Dict,
                           edge_case_results: Dict = None) -> CreditTransferRecommendation:
        """Create a recommendation using unified scoring"""
        
        # Collect all skills
        vet_skills = []
        for unit in vet_units:
            vet_skills.extend(unit.extracted_skills)
        
        uni_skills = uni_course.extracted_skills
        
        # Calculate unified score
        score_result = self.unified_scorer.calculate_alignment_score(
            vet_skills,
            uni_skills,
            match_result,
            edge_case_results
        )
        
        # Determine recommendation type based on final score
        final_score = score_result.final_score
        if final_score >= self.thresholds["full"]:
            rec_type = RecommendationType.FULL
        elif final_score >= self.thresholds["partial"]:
            rec_type = RecommendationType.PARTIAL
        else:
            rec_type = RecommendationType.NONE
        
        # Generate evidence with score breakdown
        evidence = []
        evidence.append(f"Skill coverage: {score_result.skill_coverage:.1%}")
        evidence.append(f"Match quality: {score_result.skill_quality:.1%}")
        evidence.append(f"Level alignment: {score_result.level_alignment:.1%}")
        evidence.append(f"Context alignment: {score_result.context_alignment:.1%}")
        
        # Add penalties if any
        if score_result.edge_penalties:
            for penalty_type, penalty_value in score_result.edge_penalties.items():
                if penalty_value > 0:
                    evidence.append(f"Penalty - {penalty_type}: -{penalty_value:.1%}")
        
        # Add match statistics
        stats = match_result.get("statistics", {})
        if stats.get("total_matches", 0) > 0:
            evidence.append(f"{stats['total_matches']} skill clusters matched")
        
        # Identify gaps
        gaps = match_result.get("unmapped_uni", [])
        
        # Get study level if available
        study_level = getattr(uni_course, 'study_level', 'Unknown')
        if study_level and study_level != 'Unknown':
            evidence.append(f"Course level: {study_level}")
        
        return CreditTransferRecommendation(
            vet_units=vet_units,
            uni_course=uni_course,
            alignment_score=final_score,
            skill_coverage={
                "overall": score_result.skill_coverage,
                "quality": score_result.skill_quality,
                "level": score_result.level_alignment,
                "context": score_result.context_alignment
            },
            gaps=gaps[:5] if gaps else [],
            evidence=evidence,
            recommendation=rec_type,
            conditions=[],
            confidence=score_result.confidence,
            edge_case_results=edge_case_results,
            metadata={
                "match_statistics": stats,
                "match_count": stats.get("total_matches", 0),
                "analysis_depth": self.config.get("PROGRESSIVE_DEPTH", "balanced"),
                "study_level": study_level,
                "score_breakdown": score_result.components,
                "penalties": score_result.edge_penalties
            }
        )
    
    def _refine_with_ai(self, recommendation: CreditTransferRecommendation) -> float:
        """Use AI to refine alignment score"""
        
        if not self.genai:
            return recommendation.alignment_score
        
        # Get skills for comparison
        vet_skills = []
        for unit in recommendation.vet_units:
            vet_skills.extend([s.name for s in unit.extracted_skills[:10]])
        
        uni_skills = [s.name for s in recommendation.uni_course.extracted_skills[:10]]
        
        # Detect backend type
        backend_type = "openai" if hasattr(self.genai, '_call_openai_api') else "vllm"
        
        # Get standardized prompt from PromptManager
        system_prompt, user_prompt = self.prompt_manager.get_skill_comparison_prompt(
            vet_skills=vet_skills,
            uni_skills=uni_skills,
            backend_type=backend_type
        )
        
        try:
            # Use unified method
            if hasattr(self.genai, 'generate_response'):
                response = self.genai.generate_response(system_prompt, user_prompt, max_tokens=50)
            elif hasattr(self.genai, '_call_openai_api'):
                response = self.genai._call_openai_api(system_prompt, user_prompt)
            elif hasattr(self.genai, '_generate_with_prompt'):
                response = self.genai._generate_with_prompt(system_prompt, user_prompt, 50)
            else:
                logger.warning("No compatible GenAI method found")
                return recommendation.alignment_score
            
            # Extract score from response
            import re
            match = re.search(r'0?\.\d+|1\.0', response)
            if match:
                return float(match.group())
                
        except Exception as e:
            logger.warning(f"AI refinement failed: {e}")
        
        return recommendation.alignment_score
    
    def _check_combinations(self, course, vet_units, uni_qual) -> Optional[CreditTransferRecommendation]:
        """Check if combining VET units improves coverage"""
        
        # Simple combination check - try pairs
        best_combo = None
        best_score = 0
        
        for i, unit1 in enumerate(vet_units):
            for unit2 in vet_units[i+1:]:
                # Combine skills with deduplication
                combined_skills = self._deduplicate_combined_skills(
                    unit1.extracted_skills + unit2.extracted_skills
                )
                
                # Match against course
                match_result = self.matcher.match_skills(
                    combined_skills,
                    course.extracted_skills
                )
                
                score = match_result["statistics"]["uni_coverage"]
                
                if score > best_score:
                    best_score = score
                    best_combo = ([unit1, unit2], match_result)
        
        if best_combo and best_score > self.thresholds["partial"]:
            # Run edge case analysis for combination
            edge_case_results = {}
            if self.config.get("EDGE_CASES_ENABLED", False):
                from mapping.edge_cases import EdgeCaseHandler
                edge_handler = EdgeCaseHandler(self.genai)
                edge_case_results = edge_handler.process_edge_cases(
                    best_combo[0], course, None
                )
            
            return self._create_recommendation(
                best_combo[0], course, best_combo[1], edge_case_results
            )
    
        return None
    
    def _deduplicate_combined_skills(self, skills: List[Skill]) -> List[Skill]:
        """Deduplicate skills when combining multiple VET units"""
        seen = {}
        deduplicated = []
        
        for skill in skills:
            skill_key = skill.name.lower().strip()
            
            if skill_key not in seen:
                seen[skill_key] = skill
                deduplicated.append(skill)
            else:
                # Keep the one with higher confidence
                if skill.confidence > seen[skill_key].confidence:
                    # Replace with higher confidence version
                    deduplicated = [s for s in deduplicated if s.name.lower().strip() != skill_key]
                    deduplicated.append(skill)
                    seen[skill_key] = skill
        
        return deduplicated
    
    def _simple_edge_check(self, rec: CreditTransferRecommendation) -> Dict:
        """Simplified edge case checking"""
        
        edge_cases = {}
        
        # Check for large skill gaps
        if len(rec.gaps) > 5:
            edge_cases["skill_gaps"] = {
                "severity": "high" if len(rec.gaps) > 10 else "medium",
                "gap_count": len(rec.gaps)
            }
        
        # Check for level mismatch
        vet_levels = [s.level.value for u in rec.vet_units for s in u.extracted_skills]
        uni_levels = [s.level.value for s in rec.uni_course.extracted_skills]
        
        if vet_levels and uni_levels:
            avg_vet = sum(vet_levels) / len(vet_levels)
            avg_uni = sum(uni_levels) / len(uni_levels)
            
            if avg_uni - avg_vet > 1:
                edge_cases["level_gap"] = {
                    "vet_avg": avg_vet,
                    "uni_avg": avg_uni,
                    "gap": avg_uni - avg_vet
                }
        
        return edge_cases
    
    def export_results(self, 
                       recommendations: List[CreditTransferRecommendation],
                       filepath: str):
        """Export recommendations in simple format"""
        
        import json
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "config": {
                "depth": self.config.get("PROGRESSIVE_DEPTH", "balanced"),
                "thresholds": self.thresholds
            },
            "recommendations": []
        }
        
        for rec in recommendations:
            data["recommendations"].append({
                "vet_units": rec.get_vet_unit_codes(),
                "uni_course": rec.uni_course.code,
                "score": rec.alignment_score,
                "type": rec.recommendation.value,
                "confidence": rec.confidence,
                "evidence": rec.evidence,
                "gaps": [g.name for g in rec.gaps] if rec.gaps else []
            })
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported {len(recommendations)} recommendations to {filepath}")