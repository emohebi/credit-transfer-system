"""
Simplified credit transfer analyzer with progressive analysis
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from tqdm import tqdm
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
            "full": self.config.get('THRESHOLDS', {}).get("FULL_TRANSFER".lower(), 0.8),
            "partial": self.config.get('THRESHOLDS', {}).get("PARTIAL_TRANSFER".lower(), 0.5),
            "minimum": self.config.get('THRESHOLDS', {}).get("MINIMUM_VIABLE".lower(), 0.3)
        }
        logger.info(f"Using thresholds for combined score to outupt recommendation: {self.thresholds}")
        # Matching strategy configuration
        self.matching_strategy = self.config.get("matching_strategy".upper(), "clustering")
        self.direct_threshold = self.config.get("direct_match_threshold".upper(), 0.9)
        self.partial_threshold = self.config.get("partial_threshold".upper(), 0.8)
        logger.info(f"Direct match threshold: {self.direct_threshold}, Partial match threshold: {self.partial_threshold}")
        
    def _log_skill_extraction_status(self, vet_qual: VETQualification, uni_qual: UniQualification):
        """
        Log the final status of skill extraction for all units and courses
        """
        # Count VET units with skills
        vet_with_skills = sum(1 for unit in vet_qual.units if unit.extracted_skills)
        vet_total = len(vet_qual.units)
        
        # Count Uni courses with skills
        uni_with_skills = sum(1 for course in uni_qual.courses if course.extracted_skills)
        uni_total = len(uni_qual.courses)
        
        # Count total skills
        total_vet_skills = sum(len(unit.extracted_skills) for unit in vet_qual.units)
        total_uni_skills = sum(len(course.extracted_skills) for course in uni_qual.courses)
        
        logger.info("=" * 60)
        logger.info("SKILL EXTRACTION STATUS")
        logger.info("=" * 60)
        logger.info(f"VET Units: {vet_with_skills}/{vet_total} have skills ({total_vet_skills} total skills)")
        logger.info(f"Uni Courses: {uni_with_skills}/{uni_total} have skills ({total_uni_skills} total skills)")
        
        # Log any units/courses without skills
        missing_vet = [unit.code for unit in vet_qual.units if not unit.extracted_skills]
        missing_uni = [course.code for course in uni_qual.courses if not course.extracted_skills]
        
        if missing_vet:
            logger.warning(f"VET units without skills: {', '.join(missing_vet)}")
        if missing_uni:
            logger.warning(f"Uni courses without skills: {', '.join(missing_uni)}")
        
        logger.info("=" * 60)
        
    def load_pre_extracted_skills_selective(self, 
                                       vet_qual: VETQualification, 
                                       uni_qual: UniQualification) -> Tuple[bool, Dict]:
        """
        Try to load pre-extracted skills from disk, tracking which units/courses have cached skills
        
        Returns:
            Tuple of (all_skills_loaded, load_status_dict)
            load_status_dict has 'vet' and 'uni' keys with unit/course codes as keys and bool as values
        """
        load_status = {'vet': {}, 'uni': {}}
        
        try:
            from reporting.skill_export import SkillExportManager
            skill_export = SkillExportManager(output_dir="output/skills")
            
            # Look for most recent skill files
            vet_dir = Path("output/skills/vet")
            uni_dir = Path("output/skills/uni")
            
            # Track overall success
            all_vet_loaded = False
            all_uni_loaded = False
            
            # Load VET skills
            if vet_dir.exists():
                # Find matching VET skills file
                vet_files = list(vet_dir.glob(f"{vet_qual.code}_skills_*.json"))
                if vet_files:
                    # Get most recent file
                    latest_vet = max(vet_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"Loading pre-extracted VET skills from {latest_vet}")
                    
                    try:
                        # Load the skills
                        loaded_vet_qual = skill_export.import_vet_skills(str(latest_vet))
                        
                        # Map loaded skills back to original qualification units
                        loaded_units_map = {unit.code: unit for unit in loaded_vet_qual.units}
                        
                        for unit in vet_qual.units:
                            if unit.code in loaded_units_map:
                                loaded_unit = loaded_units_map[unit.code]
                                if loaded_unit.extracted_skills:
                                    unit.extracted_skills = loaded_unit.extracted_skills
                                    load_status['vet'][unit.code] = True
                                    logger.info(f"Loaded {len(unit.extracted_skills)} skills for VET unit {unit.code}")
                                else:
                                    load_status['vet'][unit.code] = False
                                    logger.warning(f"No skills found in cache for VET unit {unit.code}")
                            else:
                                load_status['vet'][unit.code] = False
                                logger.warning(f"VET unit {unit.code} not found in cached file")
                        
                        # Check if all VET units have skills
                        all_vet_loaded = all(load_status['vet'].get(unit.code, False) 
                                            for unit in vet_qual.units)
                        
                    except Exception as e:
                        logger.error(f"Error loading VET skills from cache: {e}")
                        # Mark all as not loaded
                        for unit in vet_qual.units:
                            load_status['vet'][unit.code] = False
                else:
                    logger.info(f"No cached VET skills file found for {vet_qual.code}")
                    for unit in vet_qual.units:
                        load_status['vet'][unit.code] = False
            else:
                for unit in vet_qual.units:
                    load_status['vet'][unit.code] = False
            
            # Load University skills
            if uni_dir.exists():
                # Find matching University skills file
                uni_files = list(uni_dir.glob(f"{uni_qual.code}_skills_*.json"))
                if uni_files:
                    # Get most recent file
                    latest_uni = max(uni_files, key=lambda p: p.stat().st_mtime)
                    logger.info(f"Loading pre-extracted University skills from {latest_uni}")
                    
                    try:
                        # Load the skills
                        loaded_uni_qual = skill_export.import_uni_skills(str(latest_uni))
                        
                        # Map loaded skills back to original qualification courses
                        loaded_courses_map = {course.code: course for course in loaded_uni_qual.courses}
                        
                        for course in uni_qual.courses:
                            if course.code in loaded_courses_map:
                                loaded_course = loaded_courses_map[course.code]
                                if loaded_course.extracted_skills:
                                    course.extracted_skills = loaded_course.extracted_skills
                                    load_status['uni'][course.code] = True
                                    logger.info(f"Loaded {len(course.extracted_skills)} skills for Uni course {course.code}")
                                else:
                                    load_status['uni'][course.code] = False
                                    logger.warning(f"No skills found in cache for Uni course {course.code}")
                            else:
                                load_status['uni'][course.code] = False
                                logger.warning(f"Uni course {course.code} not found in cached file")
                        
                        # Check if all Uni courses have skills
                        all_uni_loaded = all(load_status['uni'].get(course.code, False) 
                                        for course in uni_qual.courses)
                        
                    except Exception as e:
                        logger.error(f"Error loading University skills from cache: {e}")
                        # Mark all as not loaded
                        for course in uni_qual.courses:
                            load_status['uni'][course.code] = False
                else:
                    logger.info(f"No cached University skills file found for {uni_qual.code}")
                    for course in uni_qual.courses:
                        load_status['uni'][course.code] = False
            else:
                for course in uni_qual.courses:
                    load_status['uni'][course.code] = False
            
            # Log summary
            vet_cached = sum(1 for v in load_status['vet'].values() if v)
            uni_cached = sum(1 for v in load_status['uni'].values() if v)
            
            logger.info(f"Cache load summary: "
                    f"VET: {vet_cached}/{len(vet_qual.units)} units have cached skills, "
                    f"Uni: {uni_cached}/{len(uni_qual.courses)} courses have cached skills")
            
            # Return true only if ALL units/courses have skills loaded
            return (all_vet_loaded and all_uni_loaded), load_status
            
        except Exception as e:
            logger.warning(f"Could not load pre-extracted skills: {e}")
            # Mark all as not loaded
            for unit in vet_qual.units:
                load_status['vet'][unit.code] = False
            for course in uni_qual.courses:
                load_status['uni'][course.code] = False
            return False, load_status
        
    def _save_newly_extracted_skills(self,
                                vet_qual: Optional[VETQualification],
                                uni_qual: Optional[UniQualification],
                                partial_load_status: Dict):
        """
        Save newly extracted skills to cache, merging with existing cached skills
        
        Args:
            vet_qual: VET qualification with some newly extracted skills
            uni_qual: University qualification with some newly extracted skills
            partial_load_status: Dict indicating which units/courses already had cached skills
        """
        try:
            from reporting.skill_export import SkillExportManager
            skill_export = SkillExportManager(output_dir="output/skills")
            
            # Save VET skills if any were newly extracted
            if vet_qual:
                newly_extracted_vet = [
                    unit.code for unit in vet_qual.units 
                    if unit.extracted_skills and not partial_load_status['vet'].get(unit.code, False)
                ]
                
                if newly_extracted_vet:
                    logger.info(f"Saving newly extracted skills for {len(newly_extracted_vet)} VET units")
                    filepath = skill_export.export_vet_skills(vet_qual, format="json")
                    logger.info(f"Saved VET skills to {filepath}")
            
            # Save University skills if any were newly extracted
            if uni_qual:
                newly_extracted_uni = [
                    course.code for course in uni_qual.courses 
                    if course.extracted_skills and not partial_load_status['uni'].get(course.code, False)
                ]
                
                if newly_extracted_uni:
                    logger.info(f"Saving newly extracted skills for {len(newly_extracted_uni)} Uni courses")
                    filepath = skill_export.export_uni_skills(uni_qual, format="json")
                    logger.info(f"Saved University skills to {filepath}")
                    
        except Exception as e:
            logger.warning(f"Failed to save newly extracted skills: {e}")
            
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
        depth: str = "auto",
        use_cached_skills: bool = True) -> List[CreditTransferRecommendation]:
        """
        Analyze credit transfer with progressive depth
        
        Args:
            vet_qual: VET qualification
            uni_qual: University qualification  
            depth: Analysis depth ('quick', 'balanced', 'deep', or 'auto')
            use_cached_skills: Whether to try loading pre-extracted skills
            
        Returns:
            List of recommendations
        """
        self._validate_qualification_data(vet_qual, uni_qual)
        
        logger.info(f"Starting simplified analysis: {vet_qual.code} -> {uni_qual.code}")
        
        # Try to load pre-extracted skills if requested
        skills_loaded = False
        partial_load_status = {'vet': {}, 'uni': {}}
        
        if use_cached_skills:
            skills_loaded, partial_load_status = self.load_pre_extracted_skills_selective(
                vet_qual, uni_qual
            )
        
        # Extract skills only for units/courses that don't have them
        if not skills_loaded:
            logger.info("Extracting skills for units/courses without cached skills...")
            
            # Identify which units need skill extraction
            vet_units_needing_extraction = [
                unit for unit in vet_qual.units 
                if not partial_load_status['vet'].get(unit.code, False)
            ]
            
            uni_courses_needing_extraction = [
                course for course in uni_qual.courses 
                if not partial_load_status['uni'].get(course.code, False)
            ]
            
            if vet_units_needing_extraction:
                logger.info(f"Extracting skills for {len(vet_units_needing_extraction)} VET units "
                        f"(skipping {len(vet_qual.units) - len(vet_units_needing_extraction)} with cached skills)")
                
                # Extract skills only for units without cached skills
                vet_skills = self.extractor.extract_skills(vet_units_needing_extraction)
                
                # Assign extracted skills back to objects
                for unit in vet_units_needing_extraction:
                    if unit.code in vet_skills:
                        unit.extracted_skills = vet_skills[unit.code]
                        logger.info(f"Extracted {len(unit.extracted_skills)} skills for VET unit {unit.code}")
            
            if uni_courses_needing_extraction:
                logger.info(f"Extracting skills for {len(uni_courses_needing_extraction)} Uni courses "
                        f"(skipping {len(uni_qual.courses) - len(uni_courses_needing_extraction)} with cached skills)")
                
                # Extract skills only for courses without cached skills
                uni_skills = self.extractor.extract_skills(uni_courses_needing_extraction)
                
                # Assign extracted skills back to objects
                for course in uni_courses_needing_extraction:
                    if course.code in uni_skills:
                        course.extracted_skills = uni_skills[course.code]
                        logger.info(f"Extracted {len(course.extracted_skills)} skills for Uni course {course.code}")
            
            # Optionally save newly extracted skills to cache
            if vet_units_needing_extraction or uni_courses_needing_extraction:
                self._save_newly_extracted_skills(
                    vet_qual if vet_units_needing_extraction else None,
                    uni_qual if uni_courses_needing_extraction else None,
                    partial_load_status
                )
        
        # Log final skill status
        self._log_skill_extraction_status(vet_qual, uni_qual)
        
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
        
        # Skills should already be loaded in the qualification objects
        # Build skill dictionaries from loaded skills
        vet_skills = {}
        for unit in vet_qual.units:
            if unit.extracted_skills:
                vet_skills[unit.code] = unit.extracted_skills
        
        uni_skills = {}
        for course in uni_qual.courses:
            if course.extracted_skills:
                uni_skills[course.code] = course.extracted_skills
        
        if not vet_skills or not uni_skills:
            logger.error("No skills available for analysis. Please extract skills first.")
            return []
        
        logger.info(f"Using {sum(len(s) for s in vet_skills.values())} VET skills and {sum(len(s) for s in uni_skills.values())} Uni skills")
        
        recommendations = []
        logger.info(f"Using matching strategy: {self.matching_strategy}")
        # Simple matching for each course
        for course in tqdm(uni_qual.courses):
            if course.code not in uni_skills:
                logger.warning(f"Course {course.code} not available in {list(uni_skills.keys())}")
                continue
            
            course_skills = uni_skills[course.code]
            
            # Choose matching strategy
            if self.matching_strategy == "direct":
                best_match = self._find_best_direct_match(
                    vet_skills, course_skills, course.code
                )
            if self.matching_strategy == "direct_one_vs_all":
                best_match = self._find_best_direct_match_one_vs_all_vet(
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
                units = [u for unit_code in best_match[0] for u in vet_qual.units if u.code == unit_code]
                
                # Run edge case analysis if enabled
                edge_case_results = {}
                if self.config.get("EDGE_CASES_ENABLED", False):
                    from mapping.edge_cases import EdgeCaseHandler
                    edge_handler = EdgeCaseHandler(self.genai)
                    edge_case_results = edge_handler.process_edge_cases(
                        units, course, None
                    )
                
                rec = self._create_recommendation(
                    units, course, best_match[2], edge_case_results  # Note: best_match[2] is the match_result
                )
                if hasattr(self.matcher, 'last_semantic_clusters'):
                    rec.metadata['semantic_clusters'] = self.matcher.last_semantic_clusters
                if self.matching_strategy:
                    rec.metadata['matching_strategy'] = self.matching_strategy
                #
                recommendations.append(rec)
        
        recommendations = sorted(recommendations, key=lambda x: x.alignment_score, reverse=True)
        return recommendations
    
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
        """Direct skill matching with vectorized computation"""
        best_match = None
        best_score = 0
        
        for unit_code, unit_skills in vet_skills.items():
            if not unit_skills or not course_skills:
                continue
                
            # Vectorized skill matching using embeddings
            match_result = self._calculate_vectorized_skill_matches(
                unit_skills, course_skills
            )
            if match_result is None:
                continue
                
            # Extract results from vectorized computation
            all_skill_matches = match_result['all_matches']
            uni_skill_coverage = match_result['uni_coverage']
            vet_skill_coverage = match_result['vet_coverage']
            best_skill_matches_uni = match_result['best_uni_matches']
            
            vet_total_score = 0
            for vet_skill in unit_skills:
                if vet_skill.name in vet_skill_coverage:
                    score = vet_skill_coverage[vet_skill.name]
                    if score >= self.direct_threshold:
                        vet_total_score += 1.0
                    elif score >= self.partial_threshold:
                        vet_total_score += 0.5
            
            # Calculate weighted coverage score
            uni_total_score = 0
            for uni_skill in course_skills:
                if uni_skill.name in uni_skill_coverage:
                    score = uni_skill_coverage[uni_skill.name]
                    if score >= self.direct_threshold:
                        uni_total_score += 1.0
                    elif score >= self.partial_threshold:
                        uni_total_score += 0.5
            
            uni_coverage = uni_total_score / len(course_skills) if course_skills else 0
            vet_coverage = vet_total_score / len(unit_skills) if unit_skills else 0
            bidirectional_coverage = min(uni_coverage, vet_coverage)
            final_score = uni_coverage# * 0.8 + bidirectional_coverage * 0.2)
            
            if final_score > best_score:
                best_score = final_score
                best_skill_matches = list(best_skill_matches_uni.values())
                
                # Count match types
                direct_matches = [m for m in best_skill_matches if m['match_type'] == "Direct"]
                partial_matches = [m for m in best_skill_matches if m['match_type'] == "Partial"]
                unmapped_matches = [m for m in best_skill_matches if m['match_type'] == "Unmapped"]
                mapped_vet_skills = list(set([m['vet_skill'].name for m in best_skill_matches if m['match_type'] in ["Direct", "Partial"]]))
                mapped_uni_skills = [m['uni_skill'].name for m in best_skill_matches if m['match_type'] in ["Direct", "Partial"]]
                # unmapped = len(course_skills) - len(direct_matches) - len(partial_matches)
                
                # Create detailed match result (same structure as before)
                match_result_final = {
                    "best_match": {
                        "vet_skills": unit_skills,
                        "uni_skills": course_skills,
                        "weighted_uni_coverage": uni_coverage,
                        "best_uni_skill_matches": best_skill_matches,
                    },
                    "statistics": {
                        "uni_coverage": uni_coverage,
                        "vet_coverage": vet_coverage,
                        "bidirectional_coverage": bidirectional_coverage,
                        "total_matches": len(best_skill_matches),
                        "unique_uni_matched": len(mapped_uni_skills),
                        "unique_vet_matched": len(mapped_vet_skills),
                        "direct_matches": len(direct_matches),
                        "partial_matches": len(partial_matches),
                        "unmapped_count": len(unmapped_matches),
                        "one_to_many_mappings": sum(1 for matches in [m for m in best_skill_matches] 
                                                if len([m2 for m2 in best_skill_matches 
                                                        if m2['vet_skill'] == m2['vet_skill']]) > 1)
                    },
                    "skill_match_details": {
                        'mapped': direct_matches + partial_matches,
                        "unmapped_vet": [s for s in unit_skills if s.name not in mapped_vet_skills],
                        "unmapped_uni": [s for s in course_skills if s.name not in mapped_uni_skills],
                    }
                }
                best_match = ([unit_code], final_score, match_result_final)
        
        return best_match
    
    def _find_best_direct_match_one_vs_all_vet(self, vet_skills: Dict, course_skills: List, course_code: str) -> Tuple:
        """Direct skill matching with vectorized computation"""
        best_match = None

        unit_skills = [s for skills in vet_skills.values() for s in skills]
        if not unit_skills or not course_skills:
            logger.warning(f"No skills available for direct matching for course {course_code}")
            return None
        # Vectorized skill matching using embeddings
        match_result = self._calculate_vectorized_skill_matches(
            unit_skills, course_skills
        )
        if match_result is None:
            logger.warning(f"Vectorized skill matching failed for course {course_code}")
            return None
            
        # Extract results from vectorized computation
        all_skill_matches = match_result['all_matches']
        uni_skill_coverage = match_result['uni_coverage']
        vet_skill_coverage = match_result['vet_coverage']
        best_skill_matches_uni = match_result['best_uni_matches']
        
        vet_total_score = 0
        for vet_skill in unit_skills:
            if vet_skill.name in vet_skill_coverage:
                score = vet_skill_coverage[vet_skill.name]
                if score >= self.direct_threshold:
                    vet_total_score += 1.0
                elif score >= self.partial_threshold:
                    vet_total_score += 0.5
        
        # Calculate weighted coverage score
        uni_total_score = 0
        for uni_skill in course_skills:
            if uni_skill.name in uni_skill_coverage:
                score = uni_skill_coverage[uni_skill.name]
                if score >= self.direct_threshold:
                    uni_total_score += 1.0
                elif score >= self.partial_threshold:
                    uni_total_score += 0.5
        
        uni_coverage = uni_total_score / len(course_skills) if course_skills else 0
        vet_coverage = vet_total_score / len(unit_skills) if unit_skills else 0
        bidirectional_coverage = min(uni_coverage, vet_coverage)
        final_score = uni_coverage# * 0.8 + bidirectional_coverage * 0.2)
        

        best_skill_matches = list(best_skill_matches_uni.values())
        
        # Count match types
        direct_matches = [m for m in best_skill_matches if m['match_type'] == "Direct"]
        partial_matches = [m for m in best_skill_matches if m['match_type'] == "Partial"]
        unmapped_matches = [m for m in best_skill_matches if m['match_type'] == "Unmapped"]
        mapped_vet_skills = list(set([m['vet_skill'].name for m in best_skill_matches if m['match_type'] in ["Direct", "Partial"]]))
        mapped_vet_units = list(set([m['vet_skill'].code for m in best_skill_matches if m['match_type'] in ["Direct", "Partial"]]))
        mapped_uni_skills = [m['uni_skill'].name for m in best_skill_matches if m['match_type'] in ["Direct", "Partial"]]
        # unmapped = len(course_skills) - len(direct_matches) - len(partial_matches)
        
        # Create detailed match result (same structure as before)
        match_result_final = {
            "best_match": {
                "vet_skills": unit_skills,
                "uni_skills": course_skills,
                "weighted_uni_coverage": uni_coverage,
                "best_uni_skill_matches": best_skill_matches,
            },
            "statistics": {
                "uni_coverage": uni_coverage,
                "vet_coverage": vet_coverage,
                "bidirectional_coverage": bidirectional_coverage,
                "total_matches": len(best_skill_matches),
                "unique_uni_matched": len(mapped_uni_skills),
                "unique_vet_matched": len(mapped_vet_skills),
                "direct_matches": len(direct_matches),
                "partial_matches": len(partial_matches),
                "unmapped_count": len(unmapped_matches),
                "one_to_many_mappings": sum(1 for matches in [m for m in best_skill_matches] 
                                        if len([m2 for m2 in best_skill_matches 
                                                if m2['vet_skill'] == m2['vet_skill']]) > 1)
            },
            "skill_match_details": {
                'mapped': direct_matches + partial_matches,
                "unmapped_vet": [s for s in unit_skills if s.name not in mapped_vet_skills],
                "unmapped_uni": [s for s in course_skills if s.name not in mapped_uni_skills],
            }
        }
        best_match = (mapped_vet_units, final_score, match_result_final)
        
        return best_match
    
    def _calculate_vectorized_skill_matches(self, vet_skills: List, uni_skills: List) -> Dict:
        """
        Vectorized computation of skill matches using batch embeddings
        Returns complete match matrix and coverage information
        """
        if not self.embeddings or not vet_skills or not uni_skills:
            return None
        
        # Extract skill names for embedding
        vet_names = [s.name for s in vet_skills]
        uni_names = [s.name for s in uni_skills]
        
        # Get embeddings in batch (much faster than individual calls)
        all_names = vet_names + uni_names
        all_embeddings = self.embeddings.encode(all_names, show_progress=False)
        
        # Split embeddings back
        vet_embeddings = all_embeddings[:len(vet_names)]
        uni_embeddings = all_embeddings[len(vet_names):]
        
        # Compute similarity matrix in one operation
        similarity_matrix = self.embeddings.similarity(vet_embeddings, uni_embeddings)
        
        # Build level and context matrices for vectorized computation
        vet_levels = np.array([s.level.value for s in vet_skills])
        uni_levels = np.array([s.level.value for s in uni_skills])
        
        # Vectorized level compatibility computation
        level_compat_matrix = self._compute_level_compatibility_matrix(vet_levels, uni_levels)
        
        # Vectorized context compatibility
        vet_contexts = [s.context.value for s in vet_skills]
        uni_contexts = [s.context.value for s in uni_skills]
        context_compat_matrix = self._compute_context_compatibility_matrix(vet_contexts, uni_contexts)
        
        # Compute combined scores in vectorized manner
        semantic_weight = self.config.get("SEMANTIC_WEIGHT", 0.6)
        level_weight = self.config.get("LEVEL_WEIGHT", 0.25)
        context_weight = self.config.get("CONTEXT_WEIGHT", 0.15)
        
        # Normalize weights
        total_weight = semantic_weight + level_weight + context_weight
        semantic_weight /= total_weight
        level_weight /= total_weight
        context_weight /= total_weight
        
        # Combined score matrix
        combined_scores = (
            similarity_matrix * semantic_weight +
            level_compat_matrix * level_weight +
            context_compat_matrix * context_weight
        )
        
        # Process results to maintain one-to-many support
        all_skill_matches = []
        vet_skill_coverage = {}
        uni_skill_coverage = {}
        best_uni_matches = {}
        
        # Find best matches for each skill (vectorized approach)
        # threshold = self.config.get("PARTIAL_THRESHOLD", 0.5)
        
        # For each VET skill, find all matching UNI skills above threshold
        for i, vet_skill in enumerate(vet_skills):
            # matches_for_vet = []
            for j, uni_skill in enumerate(uni_skills):
                score = combined_scores[i, j]
                # if score >= threshold:
                match_type, reasoning = self._classify_match_vectorized(
                    similarity_matrix[i, j],
                    level_compat_matrix[i, j],
                    context_compat_matrix[i, j],
                    score
                )
                
                match_result = {
                    "vet_skill": vet_skill,
                    "uni_skill": uni_skill,
                    "match_type": match_type,
                    "similarity": float(similarity_matrix[i, j]),
                    "level_compatibility": float(level_compat_matrix[i, j]),
                    "context_similarity": float(context_compat_matrix[i, j]),
                    "combined_score": float(score),
                    "reasoning": reasoning
                }
                
                # matches_for_vet.append(match_result)
                all_skill_matches.append(match_result)
                
                # Update coverage tracking
                vet_skill_coverage[vet_skill.name] = max(
                    vet_skill_coverage.get(vet_skill.name, 0), score
                )
                uni_skill_coverage[uni_skill.name] = max(
                    uni_skill_coverage.get(uni_skill.name, 0), score
                )
                if score >= uni_skill_coverage.get(uni_skill.name, 0):
                    best_uni_matches[uni_skill.name] = match_result
                    
        return {
                    'all_matches': all_skill_matches,
                    'vet_coverage': vet_skill_coverage,
                    'uni_coverage': uni_skill_coverage,
                    'best_uni_matches': best_uni_matches,
                    'similarity_matrix': similarity_matrix,
                    'combined_scores': combined_scores
                }
        
    def _compute_level_compatibility_matrix(self, vet_levels: np.ndarray, uni_levels: np.ndarray) -> np.ndarray:
        """
        Compute level compatibility matrix in vectorized manner
        """
        # Create the unified scorer's level compatibility matrix
        from mapping.unified_scorer import UnifiedScorer
        scorer = UnifiedScorer()
        base_matrix = scorer.level_compatibility_matrix
        
        # Vectorized indexing - clip to valid range [0, 6]
        vet_indices = np.clip(vet_levels - 1, 0, 6).astype(int)
        uni_indices = np.clip(uni_levels - 1, 0, 6).astype(int)
        
        # Create result matrix using advanced indexing
        n_vet = len(vet_indices)
        n_uni = len(uni_indices)
        result = np.zeros((n_vet, n_uni))
        
        for i, v_idx in enumerate(vet_indices):
            result[i, :] = base_matrix[v_idx, uni_indices]
        
        return result

    def _compute_context_compatibility_matrix(self, vet_contexts: List[str], uni_contexts: List[str]) -> np.ndarray:
        """
        Compute context compatibility matrix in vectorized manner
        """
        context_similarity_lookup = {
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
        
        n_vet = len(vet_contexts)
        n_uni = len(uni_contexts)
        result = np.zeros((n_vet, n_uni))
        
        for i, v_ctx in enumerate(vet_contexts):
            for j, u_ctx in enumerate(uni_contexts):
                result[i, j] = context_similarity_lookup.get((v_ctx, u_ctx), 0.5)
        
        return result

    def _classify_match_vectorized(self, semantic_sim: float, level_compat: float, 
                                context_compat: float, combined_score: float) -> Tuple[str, str]:
        """
        Classify match type based on precomputed scores
        """
        if self.matching_strategy in "direct" or self.matching_strategy == "direct_one_vs_all":
            if combined_score >= self.direct_threshold: #and semantic_sim >= 0.9:
                return ("Direct", f"High match (sem: {semantic_sim:.0%}, lvl: {level_compat:.0%}, ctx: {context_compat:.0%}, cmb: {combined_score:.0%})")
            elif combined_score >= self.partial_threshold:# and semantic_sim >= 0.8:
                return ("Partial", f"Moderate match (sem: {semantic_sim:.0%}, lvl: {level_compat:.0%}, ctx: {context_compat:.0%}, cmb: {combined_score:.0%})")
            else:
                return ("Unmapped", f"Insufficient match (sem: {semantic_sim:.0%}, lvl: {level_compat:.0%}, ctx: {context_compat:.0%}, cmb: {combined_score:.0%})")
        else:
            # Use simplified classification for non-direct strategies
            level_gap = abs(level_compat - 1.0) * 7  # Approximate level gap
            from mapping.simple_mapping_types import SimpleMappingClassifier
            classifier = SimpleMappingClassifier()
            return classifier.classify_mapping(semantic_sim, int(level_gap), context_compat > 0.7)

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
        
        
        # Calculate unified score
        score_result = self.unified_scorer.calculate_alignment_score(
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
        if self.matching_strategy in ["direct", "direct_one_vs_all"]:
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