"""
Simplified credit transfer analyzer with progressive analysis
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

import numpy as np

from models.base_models import (
    VETQualification, UniQualification, 
    CreditTransferRecommendation, Skill, SkillMatchResult
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
        # Matching strategy configuration
        self.matching_strategy = self.config.get("matching_strategy".upper(), "clustering")
        self.direct_threshold = self.config.get("direct_match_threshold".upper(), 0.85)
        
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
        logger.info(f"Using matching strategy: {self.matching_strategy}")
        # Simple matching for each course
        for course in uni_qual.courses:
            if course.code not in uni_skills:
                continue
            
            course_skills = uni_skills[course.code]
            
            # Choose matching strategy
            if self.matching_strategy == "direct":
                best_match = self._find_best_direct_match(
                    vet_skills, course_skills, course.code
                )
            elif self.matching_strategy == "hybrid":
                best_match = self._find_best_hybrid_match(
                    vet_skills, course_skills, course.code
                )
            else:  # clustering (default)
                best_match = self._find_best_cluster_match(
                    vet_skills, course_skills
                )
            
            if best_match and best_match[1] >= self.thresholds["minimum"]:
                # Create recommendation (existing code from lines 156-169)
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
                    [unit], course, best_match[2], edge_case_results  # Note: best_match[2] is the match_result
                )
                if hasattr(self.matcher, 'last_semantic_clusters'):
                    rec.metadata['semantic_clusters'] = self.matcher.last_semantic_clusters
                if self.matching_strategy:
                    rec.metadata['matching_strategy'] = self.matching_strategy
                #
                recommendations.append(rec)
        
        return recommendations
  
    def _calculate_skill_match(self, vet_skill, uni_skill) -> SkillMatchResult:
        """Calculate match between two skills including semantic, level, and context compatibility"""
        
        # Calculate semantic similarity
        if self.embeddings:
            semantic_similarity = self.embeddings.similarity_score(
                vet_skill.name, uni_skill.name
            )
        else:
            semantic_similarity = 1.0 if vet_skill.name.lower() == uni_skill.name.lower() else 0.0
        
        # Calculate level compatibility using the unified scorer matrix
        vet_idx = min(max(0, vet_skill.level.value - 1), 6)
        uni_idx = min(max(0, uni_skill.level.value - 1), 6)
        level_compatibility = self.unified_scorer.level_compatibility_matrix[vet_idx, uni_idx]
        
        # Calculate context similarity (NEW - using graduated scoring)
        context_similarity_matrix = {
            ('practical', 'practical'): 1.0,
            ('practical', 'hybrid'): 0.7,
            ('practical', 'theoretical'): 0.3,
            ('theoretical', 'theoretical'): 1.0,
            ('theoretical', 'hybrid'): 0.7,
            ('theoretical', 'practical'): 0.3,
            ('hybrid', 'practical'): 0.7,
            ('hybrid', 'theoretical'): 0.7,
            ('hybrid', 'hybrid'): 1.0,
        }
        
        vet_context = vet_skill.context.value
        uni_context = uni_skill.context.value
        context_similarity = context_similarity_matrix.get(
            (vet_context, uni_context), 0.5
        )
        
        # Calculate combined score with context weighting
        semantic_weight = self.config.get("SEMANTIC_WEIGHT", 0.6)
        level_weight = self.config.get("LEVEL_WEIGHT", 0.25)
        context_weight = self.config.get("CONTEXT_WEIGHT", 0.15)
        
        # Normalize weights
        total_weight = semantic_weight + level_weight + context_weight
        semantic_weight /= total_weight
        level_weight /= total_weight
        context_weight /= total_weight
        
        combined_score = (
            semantic_similarity * semantic_weight + 
            level_compatibility * level_weight +
            context_similarity * context_weight
        )
        
        # Determine match type with context consideration
        from mapping.simple_mapping_types import SimpleMappingClassifier
        classifier = SimpleMappingClassifier()
        level_gap = abs(uni_skill.level.value - vet_skill.level.value)
        
        # Modified classification considering context similarity
        if self.matching_strategy == "direct":
            if combined_score >= self.direct_threshold and semantic_similarity >= 0.7:
                match_type = "Direct"
                reasoning = f"High match (sem: {semantic_similarity:.0%}, lvl: {level_compatibility:.0%}, ctx: {context_similarity:.0%}, cmb: {combined_score:.0%})"
            elif combined_score >= 0.65 and semantic_similarity >= 0.7:
                match_type = "Partial"
                reasoning = f"Moderate match (sem: {semantic_similarity:.0%}, lvl: {level_compatibility:.0%}, ctx: {context_similarity:.0%}, cmb: {combined_score:.0%})"
            else:
                match_type = "Unmapped"
                reasoning = f"Insufficient match (sem: {semantic_similarity:.0%}, lvl: {level_compatibility:.0%}, ctx: {context_similarity:.0%}, cmb: {combined_score:.0%})"
        else:
            match_type, base_reasoning = classifier.classify_mapping(
                semantic_similarity, level_gap, context_similarity > 0.7
            )
            reasoning = f"{base_reasoning} (ctx similarity: {context_similarity:.0%})"
        
        return SkillMatchResult(
            vet_skill=vet_skill,
            uni_skill=uni_skill,
            similarity_score=semantic_similarity,
            level_compatibility=level_compatibility,
            match_type=match_type,
            reasoning=reasoning,
            combined_score=combined_score,
            metadata={'context_similarity': context_similarity}
        )

    def _calculate_all_skill_matches(self, vet_skills_list, uni_skills_list):
        """Calculate all skill-to-skill matches and store in metadata"""
        
        skill_matches = []
        
        for vet_skill in vet_skills_list:
            best_match = None
            best_score = 0
            
            for uni_skill in uni_skills_list:
                match_result = self._calculate_skill_match(vet_skill, uni_skill)
                
                if match_result.combined_score > best_score:
                    best_score = match_result.combined_score
                    best_match = match_result
            
            if best_match:
                skill_matches.append(best_match)
            else:
                # Create unmapped entry
                skill_matches.append(SkillMatchResult(
                    vet_skill=vet_skill,
                    uni_skill=None,
                    similarity_score=0,
                    level_compatibility=0,
                    match_type="Unmapped",
                    reasoning="No matching university skill found",
                    combined_score=0
                ))
        
        # Add unmapped uni skills
        matched_uni_skills = {m.uni_skill.name for m in skill_matches if m.uni_skill}
        for uni_skill in uni_skills_list:
            if uni_skill.name not in matched_uni_skills:
                skill_matches.append(SkillMatchResult(
                    vet_skill=None,
                    uni_skill=uni_skill,
                    similarity_score=0,
                    level_compatibility=0,
                    match_type="Unmapped",
                    reasoning="No matching VET skill found",
                    combined_score=0
                ))
        
        return skill_matches
    
    def _find_best_cluster_match(self, vet_skills: Dict, course_skills: List) -> Tuple:
        """Original clustering-based matching"""
        best_match = None
        best_score = 0
        
        for unit_code, unit_skills in vet_skills.items():
            match_result = self.matcher.match_skills(unit_skills, course_skills)
            score = match_result["statistics"]["uni_coverage"]
            
            if score > best_score:
                best_score = score
                best_match = (unit_code, score, match_result)
        
        return best_match

    def _find_best_direct_match(self, vet_skills: Dict, course_skills: List, course_code: str) -> Tuple:
        """Direct skill matching with one-to-many relationship support"""
        best_match = None
        best_score = 0
        best_skill_matches_uni = {}
        
        # Pre-filter optimization
        # if not self._has_potential_overlap(vet_skills, course_skills):
        #     return None
        
        for unit_code, unit_skills in vet_skills.items():
            # Calculate ALL skill matches (not just best)
            all_skill_matches = []
            vet_skill_coverage = {}  # Track which VET skills are used
            uni_skill_coverage = {}  # Track which Uni skills are covered
            
            # Build complete match matrix
            for vet_skill in unit_skills:
                vet_matches = []
                for uni_skill in course_skills:
                    match_result = self._calculate_skill_match(vet_skill, uni_skill)
                    if match_result.combined_score >= 0.4:  # Keep all reasonable matches
                        vet_matches.append({
                            'uni_skill': uni_skill,
                            'match_result': match_result,
                            'score': match_result.combined_score
                        })
                
                # Sort matches for this VET skill by score
                vet_matches.sort(key=lambda x: x['score'], reverse=True)
                
                # Track all valid matches (one-to-many support)
                for match in vet_matches:
                    if match['score'] >= self.config.get("PARTIAL_THRESHOLD", 0.5):
                        all_skill_matches.append(match['match_result'])
                        
                        vet_skill_coverage[vet_skill.name] = max(
                            vet_skill_coverage.get(vet_skill.name, 0),
                            match['score']
                        )
                        if match['score'] >= uni_skill_coverage.get(match['uni_skill'].name, 0):
                            best_skill_matches_uni[match['uni_skill'].name] = match['match_result']
                        uni_skill_coverage[match['uni_skill'].name] = max(
                            uni_skill_coverage.get(match['uni_skill'].name, 0),
                            match['score']
                        )
            
            # Calculate bidirectional coverage
            uni_coverage = len(uni_skill_coverage) / len(course_skills) if course_skills else 0
            vet_coverage = len(vet_skill_coverage) / len(unit_skills) if unit_skills else 0
            
            # Use minimum coverage (addresses the coverage calculation issue)
            bidirectional_coverage = min(uni_coverage, vet_coverage)
            
            # Calculate weighted coverage score
            total_score = 0
            for uni_skill in course_skills:
                if uni_skill.name in uni_skill_coverage:
                    score = uni_skill_coverage[uni_skill.name]
                    if score >= self.direct_threshold:
                        total_score += 1.0
                    elif score >= 0.5:
                        total_score += 0.5
            
            coverage_score = total_score / len(course_skills) if course_skills else 0
            
            # Consider both coverage metrics
            final_score = (coverage_score * 0.8 + bidirectional_coverage * 0.2)
            
            if final_score > best_score:
                best_score = final_score
                best_skill_matches = list(best_skill_matches_uni.values())
                
                # Count match types from all matches
                direct_matches = sum(1 for m in best_skill_matches if m.match_type == "Direct")
                partial_matches = sum(1 for m in best_skill_matches if m.match_type == "Partial")
                unmapped = len(course_skills) - len(uni_skill_coverage)
                
                # Create detailed match result
                match_result = {
                    "matches": [{
                        "vet_skills": unit_skills,
                        "uni_skills": course_skills,
                        "semantic_similarity": coverage_score,
                        "level_alignment": np.mean([m.level_compatibility for m in best_skill_matches]) if best_skill_matches else 0,
                        "combined_score": final_score,
                        "match_type": "direct"
                    }],
                    "statistics": {
                        "uni_coverage": uni_coverage,
                        "vet_coverage": vet_coverage,
                        "bidirectional_coverage": bidirectional_coverage,
                        "total_matches": len(best_skill_matches),
                        "unique_uni_matched": len(uni_skill_coverage),
                        "unique_vet_matched": len(vet_skill_coverage),
                        "direct_matches": direct_matches,
                        "partial_matches": partial_matches,
                        "unmapped_count": unmapped,
                        "one_to_many_mappings": sum(1 for matches in [m for m in best_skill_matches] 
                                                if len([m2 for m2 in best_skill_matches 
                                                        if m2.vet_skill == m2.vet_skill]) > 1)
                    },
                    "skill_match_details": [
                        {
                            "vet_skill": m.vet_skill.name if m.vet_skill else None,
                            "uni_skill": m.uni_skill.name if m.uni_skill else None,
                            "match_type": m.match_type,
                            "similarity": m.similarity_score,
                            "level_compatibility": m.level_compatibility,
                            "context_similarity": m.metadata.get('context_similarity', 0),
                            "combined_score": m.combined_score,
                            "reasoning": m.reasoning
                        } for m in best_skill_matches
                    ],
                    "unmapped_vet": [s for s in unit_skills if s.name not in vet_skill_coverage],
                    "unmapped_uni": [s for s in course_skills if s.name not in uni_skill_coverage]
                }
                best_match = (unit_code, final_score, match_result)
        
        return best_match

    # Add helper method for pre-filtering:
    def _has_potential_overlap(self, vet_skills: Dict, course_skills: List) -> bool:
        """Quick pre-filter based on skill categories and keywords"""
        if not course_skills:
            return False
        
        # Get categories from course skills
        course_categories = set(s.category.value for s in course_skills)
        
        # Check if any VET unit has overlapping categories
        for unit_code, unit_skills in vet_skills.items():
            vet_categories = set(s.category.value for s in unit_skills)
            if vet_categories.intersection(course_categories):
                return True
        
        # If no category overlap, check for keyword overlap (sampling for speed)
        course_keywords = set()
        for skill in course_skills[:10]:  # Sample first 10
            course_keywords.update(skill.keywords)
        
        if course_keywords:
            for unit_code, unit_skills in vet_skills.items():
                for skill in unit_skills[:10]:  # Sample first 10
                    if any(kw in course_keywords for kw in skill.keywords):
                        return True
        
        return False

    def _find_best_hybrid_match(self, vet_skills: Dict, course_skills: List, course_code: str) -> Tuple:
        """Enhanced hybrid approach with direct matching validation via clustering"""
        
        # First, get direct matches with all relationships
        direct_result = self._find_best_direct_match(vet_skills, course_skills, course_code)
        
        if not direct_result:
            # Fall back to pure clustering if no direct matches
            return self._find_best_cluster_match(vet_skills, course_skills)
        
        unit_code = direct_result[0]
        match_result = direct_result[2]
        
        # Extract matched and unmapped skills
        skill_details = match_result.get("skill_match_details", [])
        matched_uni_skills = set()
        matched_vet_skills = set()
        
        for detail in skill_details:
            if detail["match_type"] in ["Direct", "Partial"]:
                if detail["uni_skill"]:
                    matched_uni_skills.add(detail["uni_skill"])
                if detail["vet_skill"]:
                    matched_vet_skills.add(detail["vet_skill"])
        
        # Get unmapped skills for clustering
        unmapped_uni_skills = [s for s in course_skills if s.name not in matched_uni_skills]
        unmapped_vet_skills = [s for s in vet_skills[unit_code] if s.name not in matched_vet_skills]
        
        # Use clustering for validation and unmapped skills
        validation_result = None
        cluster_supplement = None
        
        if len(matched_uni_skills) > 2:  # Validate if we have enough matches
            # Use clustering to validate direct matches
            sample_matched_uni = [s for s in course_skills if s.name in matched_uni_skills][:5]
            sample_matched_vet = [s for s in vet_skills[unit_code] if s.name in matched_vet_skills][:5]
            
            if sample_matched_uni and sample_matched_vet:
                validation_result = self.matcher.match_skills(sample_matched_vet, sample_matched_uni)
                validation_score = validation_result["statistics"].get("uni_coverage", 0)
                
                # Adjust confidence based on validation
                if validation_score < 0.5:
                    # Clustering disagrees with direct matching
                    match_result["statistics"]["confidence_adjustment"] = 0.8
                else:
                    # Clustering confirms direct matching
                    match_result["statistics"]["confidence_adjustment"] = 1.1
        
        # Use clustering on unmapped skills
        if unmapped_uni_skills and unmapped_vet_skills:
            cluster_supplement = self.matcher.match_skills(unmapped_vet_skills, unmapped_uni_skills)
            
            # Add cluster matches to statistics
            cluster_matches = cluster_supplement["statistics"].get("total_matches", 0)
            
            # Update statistics with hybrid information
            match_result["statistics"]["hybrid_mode"] = True
            match_result["statistics"]["cluster_validation"] = validation_result["statistics"] if validation_result else None
            match_result["statistics"]["cluster_supplement"] = cluster_supplement["statistics"]
            match_result["statistics"]["cluster_supplement_matches"] = cluster_matches
            
            # Recalculate coverage with supplement
            direct_matched = match_result["statistics"]["unique_uni_matched"]
            cluster_matched = cluster_supplement["statistics"].get("total_matches", 0)
            
            total_matched = min(len(course_skills), direct_matched + cluster_matched)
            enhanced_coverage = total_matched / len(course_skills) if course_skills else 0
            
            # Weighted combination of direct and cluster scores
            direct_weight = 0.7
            cluster_weight = 0.3
            
            final_score = (
                direct_result[1] * direct_weight + 
                cluster_supplement["statistics"]["uni_coverage"] * cluster_weight
            )
            
            # Apply confidence adjustment if validation was performed
            if "confidence_adjustment" in match_result["statistics"]:
                final_score *= match_result["statistics"]["confidence_adjustment"]
            
            match_result["statistics"]["enhanced_coverage"] = enhanced_coverage
            match_result["statistics"]["hybrid_final_score"] = final_score
            
            return (unit_code, final_score, match_result)
        
        # Return original if no enhancement possible
        return direct_result

    def _is_skill_matched(self, target_skill: Any, skill_list: List) -> bool:
        """Check if a skill is matched in a list"""
        if not self.embeddings:
            return any(s.name.lower() == target_skill.name.lower() for s in skill_list)
        
        for skill in skill_list:
            similarity = self.embeddings.similarity_score(skill.name, target_skill.name)
            if similarity >= self.direct_threshold:
                return True
        return False
    
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
        if self.matching_strategy == "direct":
            evidence.append(f"Direct matching: {match_result.get('statistics', {}).get('direct_matches', 0)} exact matches")
        elif self.matching_strategy == "hybrid":
            if match_result.get("statistics", {}).get("hybrid_mode"):
                evidence.append("Hybrid: Direct + clustering supplement")
        
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
        
        rec =  CreditTransferRecommendation(
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
        #  Store skill match details in metadata if available
        if "skill_match_details" in match_result:
            rec.metadata["skill_match_details"] = match_result["skill_match_details"]
        return rec
    
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