"""
Edge case handlers for credit transfer mapping using Gen AI
"""

import logging
from typing import List, Dict, Any, Optional
from collections import defaultdict
import numpy as np

from models.base_models import Skill, UnitOfCompetency, UniCourse, SkillMapping
from models.enums import SkillLevel, SkillContext

logger = logging.getLogger(__name__)


class EdgeCaseHandler:
    """Handles various edge cases in credit transfer mapping using Gen AI"""
    
    def __init__(self, genai=None):
        """
        Initialize edge case handler
        
        Args:
            genai: GenAI interface for AI-based analysis
        """
        self.genai = genai
        
        self.handlers = {
            "split_to_single": self.handle_split_to_single,
            "single_to_multiple": self.handle_single_to_multiple,
            "practical_theoretical_imbalance": self.handle_context_imbalance,
            "outdated_content": self.handle_outdated_content,
            "composite_skills": self.handle_composite_skills,
            "implicit_skills": self.handle_implicit_skills,
            "version_mismatch": self.handle_version_mismatch,
            "prerequisite_chain": self.handle_prerequisite_chain,
            "credit_hour_mismatch": self.handle_credit_hour_mismatch
        }
    
    def process_edge_cases(self, 
                          vet_units: List[UnitOfCompetency],
                          uni_course: UniCourse,
                          mapping: SkillMapping) -> Dict[str, Any]:
        """
        Process all applicable edge cases using Gen AI
        
        Args:
            vet_units: VET units being mapped
            uni_course: Target university course
            mapping: Current skill mapping
            
        Returns:
            Dictionary of edge case results
        """
        logger.info(f"Processing edge cases for {len(vet_units)} VET units to {uni_course.code}")
        
        edge_case_results = {}
        
        # Use Gen AI to detect edge cases if available
        if self.genai:
            # Prepare summary for AI analysis
            vet_text = " ".join([unit.get_full_text()[:500] for unit in vet_units])
            uni_text = uni_course.get_full_text()[:1000]
            
            mapping_info = {
                "vet_units": len(vet_units),
                "direct_matches": len(mapping.direct_matches) if mapping else 0,
                "partial_matches": len(mapping.partial_matches) if mapping else 0,
                "unmapped_skills": len(mapping.unmapped_uni) if mapping else 0,
                "coverage_score": mapping.coverage_score if mapping else 0
            }
            
            # Use AI to detect edge cases
            ai_edge_cases = self.genai.detect_edge_cases(vet_text, uni_text, mapping_info)
            
            # Process AI-detected edge cases
            for edge_case in ai_edge_cases.get("edge_cases", []):
                edge_type = edge_case.get("type", "")
                if edge_type not in edge_case_results:
                    edge_case_results[edge_type] = edge_case
            
            logger.debug(f"AI detected {len(ai_edge_cases.get('edge_cases', []))} edge cases")
        
        # Run specific handlers
        
        # Check for split-to-single mapping
        if len(vet_units) > 1:
            edge_case_results["split_to_single"] = self.handle_split_to_single(
                vet_units, uni_course, mapping
            )
        
        # Check for context imbalance
        edge_case_results["context_imbalance"] = self.handle_context_imbalance(
            vet_units, uni_course, mapping
        )
        
        # Check for outdated content using AI
        edge_case_results["outdated_content"] = self.handle_outdated_content(
            vet_units, uni_course
        )
        
        # Check for composite skills
        edge_case_results["composite_skills"] = self.handle_composite_skills(
            vet_units, uni_course, mapping
        )
        
        # Check for version mismatches
        edge_case_results["version_mismatch"] = self.handle_version_mismatch(
            vet_units, uni_course
        )
        
        # Check prerequisite chains
        edge_case_results["prerequisite_chain"] = self.handle_prerequisite_chain(
            vet_units, uni_course
        )
        
        # Check credit hour alignment
        edge_case_results["credit_hours"] = self.handle_credit_hour_mismatch(
            vet_units, uni_course
        )
        
        return edge_case_results
    
    def handle_single_to_multiple(self,
                                 vet_unit: UnitOfCompetency,
                                 uni_courses: List[UniCourse]) -> Dict[str, Any]:
        """Handle single VET unit mapping to multiple uni courses"""
        result = {
            "applicable": len(uni_courses) > 1,
            "coverage_by_course": {},
            "recommended_transfers": [],
            "partial_transfers": [],
            "credit_distribution": {}
        }
        
        if not result["applicable"]:
            return result
        
        total_coverage = 0
        for course in uni_courses:
            coverage = self._calculate_skill_coverage(
                vet_unit.extracted_skills,
                course.extracted_skills
            )
            
            result["coverage_by_course"][course.code] = {
                "coverage": coverage,
                "study_level": course.study_level,
                "credit_points": course.credit_points
            }
            
            if coverage > 0.7:
                result["recommended_transfers"].append({
                    "course": course.code,
                    "coverage": coverage,
                    "study_level": course.study_level
                })
            elif coverage > 0.4:
                result["partial_transfers"].append({
                    "course": course.code,
                    "coverage": coverage,
                    "missing_skills": self._identify_missing_skills(
                        vet_unit.extracted_skills,
                        course.extracted_skills
                    )
                })
            
            total_coverage += coverage
        
        # Calculate credit distribution
        if result["recommended_transfers"]:
            total_credits = sum(
                c["credit_points"] for code, c in result["coverage_by_course"].items()
                if any(t["course"] == code for t in result["recommended_transfers"])
            )
            result["credit_distribution"]["full_credit"] = total_credits
        
        if result["partial_transfers"]:
            partial_credits = sum(
                c["credit_points"] * c["coverage"] 
                for code, c in result["coverage_by_course"].items()
                if any(t["course"] == code for t in result["partial_transfers"])
            )
            result["credit_distribution"]["partial_credit"] = partial_credits
        
        return result
    
    def handle_split_to_single(self,
                               vet_units: List[UnitOfCompetency],
                               uni_course: UniCourse,
                               mapping: SkillMapping) -> Dict[str, Any]:
        """Handle multiple VET units mapping to single uni course"""
        result = {
            "applicable": len(vet_units) > 1,
            "coverage_by_unit": {},
            "minimum_combination": [],
            "recommended_combination": [],
            "overlap_analysis": {},
            "total_coverage": 0.0
        }
        
        if not result["applicable"]:
            return result
        
        # Calculate individual unit contributions
        for unit in vet_units:
            unit_skills = unit.extracted_skills
            coverage = self._calculate_skill_coverage(unit_skills, uni_course.extracted_skills)
            result["coverage_by_unit"][unit.code] = {
                "coverage": coverage,
                "skill_count": len(unit_skills),
                "unique_contributions": []
            }
        
        # Analyze skill overlap between units using AI if available
        if self.genai:
            # Get AI assessment of overlap
            units_text = {unit.code: unit.get_full_text()[:500] for unit in vet_units}
            # This would need a specific prompt for overlap analysis
            # For now, use basic analysis
        
        result["overlap_analysis"] = self._analyze_unit_overlap(vet_units)
        
        # Find minimum and recommended combinations
        result["minimum_combination"] = self._find_minimum_combination(
            result["coverage_by_unit"], 
            threshold=0.7
        )
        
        result["recommended_combination"] = self._find_optimal_combination(
            vet_units, 
            uni_course, 
            threshold=0.85
        )
        
        # Calculate total coverage
        all_vet_skills = []
        for unit in vet_units:
            all_vet_skills.extend(unit.extracted_skills)
        
        result["total_coverage"] = self._calculate_skill_coverage(
            all_vet_skills, 
            uni_course.extracted_skills
        )
        
        # Add recommendations
        if result["overlap_analysis"]["overlap_ratio"] > 0.5:
            result["recommendation"] = "High overlap between units - consider streamlining"
        elif result["total_coverage"] < 0.7:
            result["recommendation"] = "Insufficient coverage even with all units"
        else:
            result["recommendation"] = f"Use combination: {', '.join(result['recommended_combination'])}"
        
        return result
    
    def handle_context_imbalance(self,
                                 vet_units: List[UnitOfCompetency],
                                 uni_course: UniCourse,
                                 mapping: SkillMapping) -> Dict[str, Any]:
        """Handle practical vs theoretical context imbalance using Gen AI"""
        result = {
            "vet_context_distribution": {},
            "uni_context_distribution": {},
            "imbalance_score": 0.0,
            "bridging_requirements": [],
            "recommended_supplements": []
        }
        
        if self.genai:
            # Use AI to analyze context
            vet_text = " ".join([unit.get_full_text()[:500] for unit in vet_units])
            uni_text = uni_course.get_full_text()[:1000]
            
            vet_context = self.genai.determine_context(vet_text)
            uni_context = self.genai.determine_context(uni_text)
            
            # Extract context distributions
            vet_analysis = vet_context.get("context_analysis", {})
            uni_analysis = uni_context.get("context_analysis", {})
            
            result["vet_context_distribution"] = {
                "theoretical": vet_analysis.get("theoretical_percentage", 0) / 100,
                "practical": vet_analysis.get("practical_percentage", 0) / 100
            }
            
            result["uni_context_distribution"] = {
                "theoretical": uni_analysis.get("theoretical_percentage", 0) / 100,
                "practical": uni_analysis.get("practical_percentage", 0) / 100
            }
            
            # Calculate imbalance
            practical_diff = abs(
                result["vet_context_distribution"].get("practical", 0) -
                result["uni_context_distribution"].get("practical", 0)
            )
            theoretical_diff = abs(
                result["vet_context_distribution"].get("theoretical", 0) -
                result["uni_context_distribution"].get("theoretical", 0)
            )
            result["imbalance_score"] = (practical_diff + theoretical_diff) / 2
            
            # Generate bridging requirements based on imbalance
            if result["uni_context_distribution"].get("theoretical", 0) > \
               result["vet_context_distribution"].get("theoretical", 0) + 0.3:
                gap = result["uni_context_distribution"]["theoretical"] - \
                      result["vet_context_distribution"].get("theoretical", 0)
                result["bridging_requirements"].append(
                    f"Additional theoretical foundation required ({gap:.1%} gap)"
                )
                result["recommended_supplements"].extend([
                    "Theory bridging module",
                    "Academic writing workshop"
                ])
            
            if result["uni_context_distribution"].get("practical", 0) > \
               result["vet_context_distribution"].get("practical", 0) + 0.3:
                gap = result["uni_context_distribution"]["practical"] - \
                      result["vet_context_distribution"].get("practical", 0)
                result["bridging_requirements"].append(
                    f"Additional practical experience required ({gap:.1%} gap)"
                )
                result["recommended_supplements"].extend([
                    "Laboratory skills workshop",
                    "Industry placement"
                ])
        else:
            # Fallback to basic analysis without AI
            result = self._fallback_context_analysis(vet_units, uni_course)
        
        return result
    
    def handle_outdated_content(self,
                                vet_units: List[UnitOfCompetency],
                                uni_course: UniCourse) -> Dict[str, Any]:
        """Handle potentially outdated content using Gen AI"""
        result = {
            "currency_issues": [],
            "version_specific_skills": [],
            "update_requirements": [],
            "estimated_update_effort": "low"
        }
        
        if self.genai:
            # Use AI to detect outdated technologies
            for unit in vet_units:
                text = unit.get_full_text()
                tech_versions = self.genai.extract_technology_versions(text)
                
                for tech in tech_versions.get("technologies", []):
                    if not tech.get("is_current", True):
                        result["currency_issues"].append({
                            "unit": unit.code,
                            "old_technology": f"{tech['name']} {tech.get('version', '')}",
                            "recommended": tech.get("recommended_version", "latest"),
                            "update_effort": tech.get("update_priority", "medium")
                        })
                        
                        result["update_requirements"].append(
                            f"Update {tech['name']} to {tech.get('recommended_version', 'latest')}"
                        )
                
                # Get overall assessment
                overall_effort = tech_versions.get("update_effort", "low")
                if overall_effort in ["medium", "high"]:
                    result["estimated_update_effort"] = overall_effort
        
        return result
    
    def handle_composite_skills(self,
                               vet_units: List[UnitOfCompetency],
                               uni_course: UniCourse,
                               mapping: SkillMapping) -> Dict[str, Any]:
        """Handle composite vs granular skill mismatches using Gen AI"""
        result = {
            "composite_skills_found": [],
            "decomposition_mapping": {},
            "granularity_mismatch": False,
            "coverage_improvement": 0.0
        }
        
        if self.genai:
            # Collect all skills
            all_skills = []
            for unit in vet_units:
                all_skills.extend([s.name for s in unit.extracted_skills])
            
            # Use AI to identify and decompose composite skills
            composite_result = self.genai.decompose_composite_skills(all_skills[:50])
            
            for comp_skill in composite_result.get("composite_skills", []):
                if comp_skill.get("is_composite"):
                    result["composite_skills_found"].append(comp_skill["original_skill"])
                    result["decomposition_mapping"][comp_skill["original_skill"]] = [
                        c["name"] for c in comp_skill.get("components", [])
                    ]
            
            # Check if decomposition improves coverage
            if mapping and result["decomposition_mapping"]:
                # This would require recalculating mapping with decomposed skills
                # For now, estimate improvement
                result["coverage_improvement"] = len(result["decomposition_mapping"]) * 0.05
        
        return result
    
    def handle_implicit_skills(self,
                              vet_units: List[UnitOfCompetency],
                              uni_course: UniCourse) -> Dict[str, Any]:
        """Handle implicit skills using Gen AI"""
        result = {
            "inferred_vet_skills": [],
            "inferred_uni_skills": [],
            "confidence_levels": {},
            "validation_required": []
        }
        
        if self.genai:
            # Get explicit skills
            vet_explicit = []
            for unit in vet_units:
                vet_explicit.extend([s.name for s in unit.extracted_skills])
            
            uni_explicit = [s.name for s in uni_course.extracted_skills]
            
            # Find implicit skills for VET
            vet_text = " ".join([unit.get_full_text()[:500] for unit in vet_units])
            vet_implicit = self.genai.identify_implicit_skills(vet_text, vet_explicit[:20])
            
            for skill in vet_implicit:
                result["inferred_vet_skills"].append(skill["name"])
                result["confidence_levels"][skill["name"]] = skill.get("confidence", 0.6)
                if skill.get("confidence", 0) < 0.7:
                    result["validation_required"].append(skill["name"])
            
            # Find implicit skills for Uni
            uni_text = uni_course.get_full_text()[:1000]
            uni_implicit = self.genai.identify_implicit_skills(uni_text, uni_explicit[:20])
            
            for skill in uni_implicit:
                result["inferred_uni_skills"].append(skill["name"])
                result["confidence_levels"][skill["name"]] = skill.get("confidence", 0.7)
        
        return result
    
    def handle_version_mismatch(self,
                               vet_units: List[UnitOfCompetency],
                               uni_course: UniCourse) -> Dict[str, Any]:
        """Handle version mismatches in technologies using Gen AI"""
        result = {
            "version_mismatches": [],
            "core_skill_preserved": {},
            "update_difficulty": {},
            "training_requirements": []
        }
        
        if self.genai:
            # Extract technology versions from VET
            vet_technologies = {}
            for unit in vet_units:
                text = unit.get_full_text()
                tech_result = self.genai.extract_technology_versions(text)
                for tech in tech_result.get("technologies", []):
                    vet_technologies[tech["name"]] = tech.get("version", "unknown")
            
            # Extract technology versions from Uni
            uni_text = uni_course.get_full_text()
            uni_tech_result = self.genai.extract_technology_versions(uni_text)
            
            # Compare versions
            for uni_tech in uni_tech_result.get("technologies", []):
                tech_name = uni_tech["name"]
                uni_version = uni_tech.get("version", "latest")
                
                if tech_name in vet_technologies:
                    vet_version = vet_technologies[tech_name]
                    
                    if vet_version != uni_version:
                        mismatch = {
                            "technology": tech_name,
                            "vet_version": vet_version,
                            "uni_version": uni_version,
                            "skill_preserved": 0.8  # Default preservation
                        }
                        result["version_mismatches"].append(mismatch)
                        result["core_skill_preserved"][tech_name] = 0.8
                        
                        # Assess difficulty
                        if uni_tech.get("update_priority") == "high":
                            result["update_difficulty"][tech_name] = "high"
                        else:
                            result["update_difficulty"][tech_name] = "medium"
                        
                        result["training_requirements"].append(
                            f"Update {tech_name} from {vet_version} to {uni_version}"
                        )
        
        return result
    
    def handle_prerequisite_chain(self,
                                  vet_units: List[UnitOfCompetency],
                                  uni_course: UniCourse) -> Dict[str, Any]:
        """Handle prerequisite chains using Gen AI"""
        result = {
            "missing_prerequisites": [],
            "prerequisite_coverage": {},
            "dependency_gaps": [],
            "recommended_sequence": []
        }
        
        if self.genai and uni_course.prerequisites:
            # Analyze prerequisites with AI
            uni_text = uni_course.get_full_text()[:1000]
            prereq_analysis = self.genai.analyze_prerequisites(
                uni_course.prerequisites, 
                uni_text
            )
            
            # Check if VET units cover the implied skills
            vet_skills = set()
            for unit in vet_units:
                vet_skills.update([s.name.lower() for s in unit.extracted_skills])
            
            for prereq in prereq_analysis.get("prerequisites", []):
                prereq_name = prereq["prerequisite"]
                covered = False
                
                for impl_skill in prereq.get("implied_skills", []):
                    skill_name = impl_skill["name"].lower()
                    if skill_name in vet_skills:
                        covered = True
                        result["prerequisite_coverage"][prereq_name] = "covered"
                        break
                
                if not covered:
                    result["missing_prerequisites"].append(prereq_name)
                    result["dependency_gaps"].append(
                        f"Prerequisite '{prereq_name}' skills not covered"
                    )
            
            # Recommend sequence if gaps exist
            if result["missing_prerequisites"]:
                result["recommended_sequence"] = [
                    "1. Complete bridging modules for prerequisites",
                    "2. Review VET unit content",
                    "3. Proceed with credit transfer assessment"
                ]
        
        return result
    
    def handle_credit_hour_mismatch(self,
                                vet_units: List[UnitOfCompetency],
                                uni_course: UniCourse) -> Dict[str, Any]:
        """Handle credit hour/nominal hour mismatches"""
        result = {
            "vet_total_hours": 0,
            "uni_credit_points": uni_course.credit_points,
            "hour_ratio": 0.0,
            "recommendation": "",
            "adjustment_needed": False
        }
        
        # Calculate total VET hours - handle None values
        vet_hours_list = []
        for unit in vet_units:
            if unit.nominal_hours is not None:
                vet_hours_list.append(unit.nominal_hours)
            else:
                # Use default value for units without hours specified
                vet_hours_list.append(0)
        
        result["vet_total_hours"] = sum(vet_hours_list)
        
        # If we have no valid hours data, mark as unavailable
        if result["vet_total_hours"] == 0:
            result["recommendation"] = "VET hours data unavailable - manual review required"
            result["adjustment_needed"] = False
            return result
        
        # Typical conversion: 1 credit point = 10-15 hours of study
        estimated_uni_hours = uni_course.credit_points * 12.5 if uni_course.credit_points else 0
        
        if estimated_uni_hours > 0:
            result["hour_ratio"] = result["vet_total_hours"] / estimated_uni_hours
        
        # Determine if adjustment is needed
        if result["hour_ratio"] < 0.7:
            result["adjustment_needed"] = True
            result["recommendation"] = "VET hours insufficient - additional study required"
        elif result["hour_ratio"] > 1.5:
            result["recommendation"] = "VET hours exceed requirements - consider additional credit"
        else:
            result["recommendation"] = "Credit hour alignment is acceptable"
        
        return result
    
    # Helper methods
    
    def _calculate_skill_coverage(self, 
                                  source_skills: List[Skill], 
                                  target_skills: List[Skill]) -> float:
        """Calculate how well source skills cover target skills"""
        if not target_skills:
            return 0.0
        
        covered = 0
        
        if self.genai:
            # Use AI for similarity assessment
            for target in target_skills:
                for source in source_skills:
                    similarity = self.genai.analyze_skill_similarity(
                        source.name, 
                        target.name
                    )
                    if similarity >= 0.7:
                        covered += 1
                        break
        else:
            # Fallback to simple name matching
            target_names = {s.name.lower() for s in target_skills}
            source_names = {s.name.lower() for s in source_skills}
            covered = len(target_names.intersection(source_names))
        
        return covered / len(target_skills)
    
    def _analyze_unit_overlap(self, units: List[UnitOfCompetency]) -> Dict[str, Any]:
        """Analyze skill overlap between units"""
        overlap_analysis = {
            "total_skills": 0,
            "unique_skills": 0,
            "overlap_ratio": 0.0,
            "overlap_matrix": {}
        }
        
        all_skills = []
        unit_skills = {}
        
        for unit in units:
            unit_skill_names = {s.name.lower() for s in unit.extracted_skills}
            unit_skills[unit.code] = unit_skill_names
            all_skills.extend(unit_skill_names)
        
        overlap_analysis["total_skills"] = len(all_skills)
        overlap_analysis["unique_skills"] = len(set(all_skills))
        
        if overlap_analysis["total_skills"] > 0:
            overlap_analysis["overlap_ratio"] = 1 - (
                overlap_analysis["unique_skills"] / overlap_analysis["total_skills"]
            )
        
        # Calculate pairwise overlap
        for i, unit1 in enumerate(units):
            for j, unit2 in enumerate(units):
                if i < j:
                    overlap = len(
                        unit_skills[unit1.code].intersection(unit_skills[unit2.code])
                    )
                    key = f"{unit1.code}_x_{unit2.code}"
                    overlap_analysis["overlap_matrix"][key] = overlap
        
        return overlap_analysis
    
    def _find_minimum_combination(self, 
                                  coverage_by_unit: Dict, 
                                  threshold: float) -> List[str]:
        """Find minimum combination of units to meet threshold"""
        # Sort units by coverage
        sorted_units = sorted(
            coverage_by_unit.items(), 
            key=lambda x: x[1]["coverage"] if isinstance(x[1], dict) else x[1],
            reverse=True
        )
        
        combination = []
        cumulative_coverage = 0.0
        
        for unit_code, info in sorted_units:
            coverage = info["coverage"] if isinstance(info, dict) else info
            
            combination.append(unit_code)
            
            # Update cumulative coverage
            marginal_coverage = coverage * (1 - cumulative_coverage * 0.2)
            cumulative_coverage += marginal_coverage
            
            if cumulative_coverage >= threshold:
                break
        
        return combination
    
    def _find_optimal_combination(self, 
                                  units: List[UnitOfCompetency],
                                  course: UniCourse,
                                  threshold: float) -> List[str]:
        """Find optimal combination for best coverage"""
        best_combination = []
        best_coverage = 0.0
        
        from itertools import combinations
        
        for r in range(1, min(4, len(units) + 1)):
            for combo in combinations(units, r):
                combo_skills = []
                for unit in combo:
                    combo_skills.extend(unit.extracted_skills)
                
                coverage = self._calculate_skill_coverage(combo_skills, course.extracted_skills)
                
                if coverage >= threshold and coverage > best_coverage:
                    best_coverage = coverage
                    best_combination = [u.code for u in combo]
                    
                    if coverage >= 0.95:
                        return best_combination
        
        return best_combination if best_combination else [u.code for u in units]
    
    def _identify_missing_skills(self, 
                                 source_skills: List[Skill],
                                 target_skills: List[Skill]) -> List[str]:
        """Identify skills in target that aren't in source"""
        missing = []
        
        if self.genai:
            # Use AI for better skill matching
            for target in target_skills:
                found = False
                for source in source_skills:
                    similarity = self.genai.analyze_skill_similarity(
                        source.name, 
                        target.name
                    )
                    if similarity >= 0.7:
                        found = True
                        break
                
                if not found:
                    missing.append(target.name)
        else:
            # Fallback to simple name matching
            source_names = {s.name.lower() for s in source_skills}
            for target in target_skills:
                if target.name.lower() not in source_names:
                    missing.append(target.name)
        
        return missing
    
    def _fallback_context_analysis(self, 
                                   vet_units: List[UnitOfCompetency],
                                   uni_course: UniCourse) -> Dict:
        """Fallback context analysis without AI"""
        # Basic context counting from skill objects
        vet_contexts = defaultdict(int)
        total_vet = 0
        
        for unit in vet_units:
            for skill in unit.extracted_skills:
                vet_contexts[skill.context.value] += 1
                total_vet += 1
        
        uni_contexts = defaultdict(int)
        total_uni = len(uni_course.extracted_skills)
        
        for skill in uni_course.extracted_skills:
            uni_contexts[skill.context.value] += 1
        
        result = {
            "vet_context_distribution": {},
            "uni_context_distribution": {},
            "imbalance_score": 0.0,
            "bridging_requirements": [],
            "recommended_supplements": []
        }
        
        if total_vet > 0:
            result["vet_context_distribution"] = {
                k: v/total_vet for k, v in vet_contexts.items()
            }
        
        if total_uni > 0:
            result["uni_context_distribution"] = {
                k: v/total_uni for k, v in uni_contexts.items()
            }
        
        return result