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
        self.direct_threshold = self.config.get("direct_match_threshold".upper(), 0.85)
        
    def load_pre_extracted_skills(self, vet_qual: VETQualification, uni_qual: UniQualification) -> bool:
        """
        Try to load pre-extracted skills from disk
        
        Returns:
            True if skills were loaded successfully, False otherwise
        """
        try:
            from reporting.skill_export import SkillExportManager
            skill_export = SkillExportManager(output_dir="output/skills")
            
            # Look for most recent skill files
            vet_dir = Path("output/skills/vet")
            uni_dir = Path("output/skills/uni")
            
            # Find matching VET skills file
            vet_files = list(vet_dir.glob(f"{vet_qual.code}_skills_*.json"))
            if vet_files:
                # Get most recent file
                latest_vet = max(vet_files, key=lambda p: p.stat().st_mtime)
                logger.info(f"Loading pre-extracted VET skills from {latest_vet}")
                
                # Load the skills
                loaded_vet_qual = skill_export.import_vet_skills(str(latest_vet))
                
                # Map loaded skills back to original qualification units
                for unit in vet_qual.units:
                    for loaded_unit in loaded_vet_qual.units:
                        if unit.code == loaded_unit.code:
                            unit.extracted_skills = loaded_unit.extracted_skills
                            logger.info(f"Loaded {len(unit.extracted_skills)} skills for VET unit {unit.code}")
                            break
            
            # Find matching University skills file
            uni_files = list(uni_dir.glob(f"{uni_qual.code}_skills_*.json"))
            if uni_files:
                # Get most recent file
                latest_uni = max(uni_files, key=lambda p: p.stat().st_mtime)
                logger.info(f"Loading pre-extracted University skills from {latest_uni}")
                
                # Load the skills
                loaded_uni_qual = skill_export.import_uni_skills(str(latest_uni))
                
                # Map loaded skills back to original qualification courses
                for course in uni_qual.courses:
                    for loaded_course in loaded_uni_qual.courses:
                        if course.code == loaded_course.code:
                            course.extracted_skills = loaded_course.extracted_skills
                            logger.info(f"Loaded {len(course.extracted_skills)} skills for Uni course {course.code}")
                            break
            
            # Check if we have skills for all units/courses
            vet_has_skills = all(len(unit.extracted_skills) > 0 for unit in vet_qual.units)
            uni_has_skills = all(len(course.extracted_skills) > 0 for course in uni_qual.courses)
            
            if vet_has_skills and uni_has_skills:
                logger.info("Successfully loaded all pre-extracted skills")
                return True
            else:
                logger.warning("Some units/courses missing extracted skills")
                return False
                
        except Exception as e:
            logger.warning(f"Could not load pre-extracted skills: {e}")
            return False
            
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
        if use_cached_skills:
            skills_loaded = self.load_pre_extracted_skills(vet_qual, uni_qual)
        
        if not skills_loaded:
            logger.info("Extracting skills (not found in cache)...")
            # Extract skills using the extractor
            vet_skills = self.extractor.extract_skills(vet_qual.units)
            uni_skills = self.extractor.extract_skills(uni_qual.courses)
            
            # Assign extracted skills back to objects
            for unit in vet_qual.units:
                if unit.code in vet_skills:
                    unit.extracted_skills = vet_skills[unit.code]
            
            for course in uni_qual.courses:
                if course.code in uni_skills:
                    course.extracted_skills = uni_skills[course.code]
        
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
            if combined_score >= self.direct_threshold and semantic_similarity >= 0.9:
                match_type = "Direct"
                reasoning = f"High match (sem: {semantic_similarity:.0%}, lvl: {level_compatibility:.0%}, ctx: {context_similarity:.0%}, cmb: {combined_score:.0%})"
            elif combined_score >= 0.65 and semantic_similarity >= 0.8:
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
        best_skill_matches_uni = {}
        
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
            best_skill_matches_uni_local = match_result['best_uni_matches']
            
            # Calculate bidirectional coverage
            uni_coverage = len(uni_skill_coverage) / len(course_skills) if course_skills else 0
            vet_coverage = len(vet_skill_coverage) / len(unit_skills) if unit_skills else 0
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
            final_score = (coverage_score * 0.8 + bidirectional_coverage * 0.2)
            
            if final_score > best_score:
                best_score = final_score
                best_skill_matches = list(best_skill_matches_uni_local.values())
                
                # Count match types
                direct_matches = sum(1 for m in best_skill_matches if m.match_type == "Direct")
                partial_matches = sum(1 for m in best_skill_matches if m.match_type == "Partial")
                unmapped = len(course_skills) - len(uni_skill_coverage)
                
                # Create detailed match result (same structure as before)
                match_result_final = {
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
                    "skill_match_details": {
                        'mapped': all_skill_matches,
                        "unmapped_vet": [s for s in unit_skills if s.name not in vet_skill_coverage],
                        "unmapped_uni": [s for s in course_skills if s.name not in uni_skill_coverage]
                    }
                }
                best_match = (unit_code, final_score, match_result_final)
        
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
        threshold = self.config.get("PARTIAL_THRESHOLD", 0.5)
        
        # For each VET skill, find all matching UNI skills above threshold
        for i, vet_skill in enumerate(vet_skills):
            matches_for_vet = []
            for j, uni_skill in enumerate(uni_skills):
                score = combined_scores[i, j]
                if score >= threshold:
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
                    
                    matches_for_vet.append(match_result)
                    all_skill_matches.append(match_result)
                    
                    # Update coverage tracking
                    vet_skill_coverage[vet_skill.name] = max(
                        vet_skill_coverage.get(vet_skill.name, 0), score
                    )
                    
                    if score >= uni_skill_coverage.get(uni_skill.name, 0):
                        best_uni_matches[uni_skill.name] = SkillMatchResult(
                            vet_skill=vet_skill,
                            uni_skill=uni_skill,
                            similarity_score=float(similarity_matrix[i, j]),
                            level_compatibility=float(level_compat_matrix[i, j]),
                            match_type=match_type,
                            reasoning=reasoning,
                            combined_score=float(score),
                            metadata={'context_similarity': float(context_compat_matrix[i, j])}
                        )
                    uni_skill_coverage[uni_skill.name] = max(
                        uni_skill_coverage.get(uni_skill.name, 0), score
                    )
        
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
        if self.matching_strategy == "direct":
            if combined_score >= self.direct_threshold and semantic_sim >= 0.9:
                return ("Direct", f"High match (sem: {semantic_sim:.0%}, lvl: {level_compat:.0%}, ctx: {context_compat:.0%}, cmb: {combined_score:.0%})")
            elif combined_score >= 0.65 and semantic_sim >= 0.8:
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