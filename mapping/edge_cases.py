"""
Edge case handlers for credit transfer mapping
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict
import numpy as np

from ..models.base_models import Skill, UnitOfCompetency, UniCourse, SkillMapping
from ..models.enums import SkillLevel, SkillDepth, SkillContext

logger = logging.getLogger(__name__)


class EdgeCaseHandler:
    """Handles various edge cases in credit transfer mapping"""
    
    def __init__(self):
        """Initialize edge case handler"""
        self.handlers = {
            "split_to_single": self.handle_split_to_single,
            "single_to_multiple": self.handle_single_to_multiple,
            "practical_theoretical_imbalance": self.handle_context_imbalance,
            "outdated_content": self.handle_outdated_content,
            "depth_vs_breadth": self.handle_depth_breadth,
            "composite_skills": self.handle_composite_skills,
            "implicit_skills": self.handle_implicit_skills,
            "version_mismatch": self.handle_version_mismatch,
            "prerequisite_chain": self.handle_prerequisite_chain,
            "credit_hour_mismatch": self.handle_credit_hour_mismatch
        }
        
        # Technology currency windows (years)
        self.currency_windows = {
            "default": 3,
            "programming_language": 5,
            "framework": 2,
            "methodology": 10,
            "fundamental": 20
        }
    
    def process_edge_cases(self, 
                          vet_units: List[UnitOfCompetency],
                          uni_course: UniCourse,
                          mapping: SkillMapping) -> Dict[str, Any]:
        """
        Process all applicable edge cases
        
        Args:
            vet_units: VET units being mapped
            uni_course: Target university course
            mapping: Current skill mapping
            
        Returns:
            Dictionary of edge case results
        """
        logger.info(f"Processing edge cases for {len(vet_units)} VET units to {uni_course.code}")
        
        edge_case_results = {}
        
        # Check for split-to-single mapping (multiple VET to single Uni)
        if len(vet_units) > 1:
            edge_case_results["split_to_single"] = self.handle_split_to_single(
                vet_units, uni_course, mapping
            )
        
        # Check for context imbalance
        edge_case_results["context_imbalance"] = self.handle_context_imbalance(
            vet_units, uni_course, mapping
        )
        
        # Check for outdated content
        edge_case_results["outdated_content"] = self.handle_outdated_content(
            vet_units, uni_course
        )
        
        # Check depth vs breadth
        edge_case_results["depth_breadth"] = self.handle_depth_breadth(
            vet_units, uni_course, mapping
        )
        
        # Check for composite skills
        edge_case_results["composite_skills"] = self.handle_composite_skills(
            vet_units, uni_course, mapping
        )
        
        # Check for version mismatches
        if mapping:
            all_vet_skills = []
            for unit in vet_units:
                all_vet_skills.extend(unit.extracted_skills)
            
            edge_case_results["version_mismatch"] = self.handle_version_mismatch(
                all_vet_skills, uni_course.extracted_skills
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
        
        # Analyze skill overlap between units
        result["overlap_analysis"] = self._analyze_unit_overlap(vet_units)
        
        # Find minimum combination for adequate coverage
        result["minimum_combination"] = self._find_minimum_combination(
            result["coverage_by_unit"], 
            threshold=0.7
        )
        
        # Find recommended combination for optimal coverage
        result["recommended_combination"] = self._find_optimal_combination(
            vet_units, 
            uni_course, 
            threshold=0.85
        )
        
        # Calculate total coverage with all units
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
                "year": course.year,
                "credit_points": course.credit_points
            }
            
            if coverage > 0.7:
                result["recommended_transfers"].append({
                    "course": course.code,
                    "coverage": coverage,
                    "year": course.year
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
    
    def handle_context_imbalance(self,
                                 vet_units: List[UnitOfCompetency],
                                 uni_course: UniCourse,
                                 mapping: SkillMapping) -> Dict[str, Any]:
        """Handle practical vs theoretical context imbalance"""
        result = {
            "vet_context_distribution": {},
            "uni_context_distribution": {},
            "imbalance_score": 0.0,
            "bridging_requirements": [],
            "recommended_supplements": []
        }
        
        # Calculate VET context distribution
        vet_contexts = defaultdict(int)
        total_vet_skills = 0
        for unit in vet_units:
            for skill in unit.extracted_skills:
                vet_contexts[skill.context.value] += 1
                total_vet_skills += 1
        
        # Calculate Uni context distribution
        uni_contexts = defaultdict(int)
        for skill in uni_course.extracted_skills:
            uni_contexts[skill.context.value] += 1
        
        # Normalize to percentages
        if total_vet_skills > 0:
            result["vet_context_distribution"] = {
                k: v/total_vet_skills for k, v in vet_contexts.items()
            }
        
        total_uni_skills = len(uni_course.extracted_skills)
        if total_uni_skills > 0:
            result["uni_context_distribution"] = {
                k: v/total_uni_skills for k, v in uni_contexts.items()
            }
        
        # Calculate imbalance score
        if total_vet_skills > 0 and total_uni_skills > 0:
            practical_diff = abs(
                result["vet_context_distribution"].get("practical", 0) -
                result["uni_context_distribution"].get("practical", 0)
            )
            theoretical_diff = abs(
                result["vet_context_distribution"].get("theoretical", 0) -
                result["uni_context_distribution"].get("theoretical", 0)
            )
            result["imbalance_score"] = (practical_diff + theoretical_diff) / 2
            
            # Generate bridging requirements
            if result["uni_context_distribution"].get("theoretical", 0) > \
               result["vet_context_distribution"].get("theoretical", 0) + 0.3:
                gap = result["uni_context_distribution"]["theoretical"] - \
                      result["vet_context_distribution"].get("theoretical", 0)
                result["bridging_requirements"].append(
                    f"Additional theoretical foundation required ({gap:.1%} gap)"
                )
                result["recommended_supplements"].append("Theory bridging module")
                result["recommended_supplements"].append("Academic writing workshop")
            
            if result["uni_context_distribution"].get("practical", 0) > \
               result["vet_context_distribution"].get("practical", 0) + 0.3:
                gap = result["uni_context_distribution"]["practical"] - \
                      result["vet_context_distribution"].get("practical", 0)
                result["bridging_requirements"].append(
                    f"Additional practical experience required ({gap:.1%} gap)"
                )
                result["recommended_supplements"].append("Laboratory skills workshop")
                result["recommended_supplements"].append("Industry placement")
        
        return result
    
    def handle_outdated_content(self,
                                vet_units: List[UnitOfCompetency],
                                uni_course: UniCourse) -> Dict[str, Any]:
        """Handle potentially outdated content"""
        result = {
            "currency_issues": [],
            "version_specific_skills": [],
            "update_requirements": [],
            "estimated_update_effort": "low"  # low, medium, high
        }
        
        # Technology version patterns
        version_patterns = [
            (r"python\s*2\.?\d*", "Python 2.x", "Python 3.x", "medium"),
            (r"java\s*[678]\b", "Java 6/7/8", "Java 11+", "low"),
            (r"angular\s*js", "AngularJS", "Angular 2+", "high"),
            (r"flash", "Flash", "HTML5/Canvas", "high"),
            (r"vb6|visual\s*basic\s*6", "Visual Basic 6", "Modern .NET", "high"),
            (r"php\s*[45]\b", "PHP 4/5", "PHP 8+", "medium"),
            (r"mysql\s*[45]\b", "MySQL 4/5", "MySQL 8+", "low"),
            (r"windows\s*xp|windows\s*7", "Legacy Windows", "Windows 10/11", "medium"),
        ]
        
        update_efforts = []
        
        for unit in vet_units:
            text = unit.get_full_text().lower()
            
            for pattern, old_tech, new_tech, effort in version_patterns:
                if re.search(pattern, text):
                    result["currency_issues"].append({
                        "unit": unit.code,
                        "old_technology": old_tech,
                        "recommended": new_tech,
                        "update_effort": effort
                    })
                    update_efforts.append(effort)
                    
                    result["update_requirements"].append(
                        f"Update from {old_tech} to {new_tech}"
                    )
        
        # Estimate overall update effort
        if update_efforts:
            if "high" in update_efforts:
                result["estimated_update_effort"] = "high"
            elif "medium" in update_efforts:
                result["estimated_update_effort"] = "medium"
            else:
                result["estimated_update_effort"] = "low"
        
        # Check for deprecated methodologies
        deprecated_methods = [
            ("waterfall", "Agile/Scrum methodologies"),
            ("big data hadoop only", "Modern data platforms (Spark, Cloud)"),
            ("on-premise only", "Cloud and hybrid architectures"),
        ]
        
        for unit in vet_units:
            text = unit.get_full_text().lower()
            for old_method, new_method in deprecated_methods:
                if old_method in text and new_method.lower() not in text:
                    result["update_requirements"].append(
                        f"Modernize from {old_method} to {new_method}"
                    )
        
        return result
    
    def handle_depth_breadth(self,
                            vet_units: List[UnitOfCompetency],
                            uni_course: UniCourse,
                            mapping: SkillMapping) -> Dict[str, Any]:
        """Handle depth vs breadth mismatches"""
        result = {
            "vet_skill_depth_avg": 0.0,
            "uni_skill_depth_avg": 0.0,
            "vet_skill_depth_distribution": {},
            "uni_skill_depth_distribution": {},
            "breadth_ratio": 0.0,
            "depth_adequate": False,
            "recommendations": [],
            "focus_areas": []
        }
        
        # Calculate VET depth distribution
        vet_depths = []
        for unit in vet_units:
            for skill in unit.extracted_skills:
                vet_depths.append(skill.depth.value)
        
        if vet_depths:
            result["vet_skill_depth_avg"] = np.mean(vet_depths)
            result["vet_skill_depth_distribution"] = self._calculate_distribution(vet_depths)
        
        # Calculate Uni depth distribution
        uni_depths = [skill.depth.value for skill in uni_course.extracted_skills]
        
        if uni_depths:
            result["uni_skill_depth_avg"] = np.mean(uni_depths)
            result["uni_skill_depth_distribution"] = self._calculate_distribution(uni_depths)
        
        # Calculate breadth ratio
        total_vet_skills = sum(len(u.extracted_skills) for u in vet_units)
        total_uni_skills = len(uni_course.extracted_skills)
        
        if total_uni_skills > 0:
            result["breadth_ratio"] = total_vet_skills / total_uni_skills
        
        # Assess depth adequacy
        if result["vet_skill_depth_avg"] > 0 and result["uni_skill_depth_avg"] > 0:
            result["depth_adequate"] = \
                result["vet_skill_depth_avg"] >= result["uni_skill_depth_avg"] * 0.8
        
        # Generate recommendations
        if not result["depth_adequate"]:
            depth_gap = result["uni_skill_depth_avg"] - result["vet_skill_depth_avg"]
            result["recommendations"].append(
                f"Enhance cognitive depth (gap: {depth_gap:.1f} levels)"
            )
            result["focus_areas"].append("Critical analysis and evaluation skills")
            result["focus_areas"].append("Research methodology")
        
        if result["breadth_ratio"] < 0.7:
            result["recommendations"].append(
                "Insufficient breadth - additional topics need coverage"
            )
            result["focus_areas"].append("Broaden skill coverage")
        elif result["breadth_ratio"] > 1.5:
            result["recommendations"].append(
                "VET covers broader scope - can focus on depth for uni requirements"
            )
            result["focus_areas"].append("Deepen understanding of core concepts")
        
        return result
    
    def handle_composite_skills(self,
                               vet_units: List[UnitOfCompetency],
                               uni_course: UniCourse,
                               mapping: SkillMapping) -> Dict[str, Any]:
        """Handle composite vs granular skill mismatches"""
        result = {
            "composite_skills_found": [],
            "decomposition_mapping": {},
            "granularity_mismatch": False,
            "coverage_improvement": 0.0
        }
        
        # Identify composite skills
        composite_indicators = [
            "management", "development", "analysis", "design", 
            "maintenance", "administration", "engineering"
        ]
        
        original_coverage = mapping.coverage_score if mapping else 0.0
        
        for unit in vet_units:
            for skill in unit.extracted_skills:
                skill_lower = skill.name.lower()
                
                # Check if skill is composite
                is_composite = any(ind in skill_lower for ind in composite_indicators)
                is_composite = is_composite and len(skill.name.split()) <= 3
                
                if is_composite:
                    result["composite_skills_found"].append(skill.name)
                    
                    # Simulate decomposition (in practice, use actual decomposer)
                    components = self._decompose_skill(skill.name)
                    result["decomposition_mapping"][skill.name] = components
                    
                    # Check if components match uni skills better
                    for component in components:
                        for uni_skill in uni_course.extracted_skills:
                            if self._skills_similar(component, uni_skill.name):
                                result["coverage_improvement"] += 0.1
        
        # Normalize coverage improvement
        if uni_course.extracted_skills:
            result["coverage_improvement"] /= len(uni_course.extracted_skills)
        
        # Check for granularity mismatch
        avg_vet_skill_words = np.mean([
            len(skill.name.split()) 
            for unit in vet_units 
            for skill in unit.extracted_skills
        ]) if vet_units else 0
        
        avg_uni_skill_words = np.mean([
            len(skill.name.split()) 
            for skill in uni_course.extracted_skills
        ]) if uni_course.extracted_skills else 0
        
        if avg_vet_skill_words > 0 and avg_uni_skill_words > 0:
            granularity_ratio = avg_vet_skill_words / avg_uni_skill_words
            result["granularity_mismatch"] = granularity_ratio > 1.5 or granularity_ratio < 0.67
        
        return result
    
    def handle_implicit_skills(self,
                              vet_units: List[UnitOfCompetency],
                              uni_course: UniCourse) -> Dict[str, Any]:
        """Handle implicit skills that aren't explicitly stated"""
        result = {
            "inferred_vet_skills": [],
            "inferred_uni_skills": [],
            "confidence_levels": {},
            "validation_required": []
        }
        
        # Common implicit skill patterns
        implicit_patterns = {
            "programming": ["debugging", "testing", "version control", "documentation"],
            "database": ["backup", "security", "optimization", "migration"],
            "web development": ["responsive design", "cross-browser compatibility", "accessibility"],
            "project": ["time management", "risk assessment", "stakeholder communication"],
            "analysis": ["data collection", "interpretation", "reporting", "validation"],
        }
        
        # Check VET units for implicit skills
        for unit in vet_units:
            text = unit.get_full_text().lower()
            explicit_skills = {s.name.lower() for s in unit.extracted_skills}
            
            for trigger, implied in implicit_patterns.items():
                if trigger in text:
                    for skill in implied:
                        if skill not in explicit_skills and skill not in text:
                            result["inferred_vet_skills"].append(skill)
                            result["confidence_levels"][skill] = 0.6
                            result["validation_required"].append(skill)
        
        # Check Uni course for implicit skills
        uni_text = uni_course.get_full_text().lower()
        uni_explicit = {s.name.lower() for s in uni_course.extracted_skills}
        
        for trigger, implied in implicit_patterns.items():
            if trigger in uni_text:
                for skill in implied:
                    if skill not in uni_explicit and skill not in uni_text:
                        result["inferred_uni_skills"].append(skill)
                        result["confidence_levels"][skill] = result["confidence_levels"].get(skill, 0.7)
        
        return result
    
    def handle_version_mismatch(self,
                               vet_skills: List[Skill],
                               uni_skills: List[Skill]) -> Dict[str, Any]:
        """Handle version mismatches in technologies/tools"""
        result = {
            "version_mismatches": [],
            "core_skill_preserved": {},
            "update_difficulty": {},
            "training_requirements": []
        }
        
        # Technology version extraction patterns
        tech_patterns = {
            "python": (r"python\s*(\d+(?:\.\d+)?)", 0.85),
            "java": (r"java\s*(?:se\s*)?(\d+)", 0.9),
            "javascript": (r"(?:javascript|js)\s*(?:es)?(\d+)?", 0.8),
            "react": (r"react(?:\.?js)?\s*(?:v)?(\d+(?:\.\d+)?)", 0.7),
            "angular": (r"angular(?:js)?\s*(?:v)?(\d+)?", 0.5),
            ".net": (r"\.net\s*(?:core\s*)?(?:framework\s*)?(\d+(?:\.\d+)?)", 0.8),
        }
        
        for vet_skill in vet_skills:
            for tech, (pattern, preservation_rate) in tech_patterns.items():
                if tech in vet_skill.name.lower():
                    vet_match = re.search(pattern, vet_skill.name.lower())
                    
                    if vet_match:
                        vet_version = vet_match.group(1) or "unspecified"
                        
                        # Check uni skills for same tech
                        for uni_skill in uni_skills:
                            if tech in uni_skill.name.lower():
                                uni_match = re.search(pattern, uni_skill.name.lower())
                                
                                if uni_match:
                                    uni_version = uni_match.group(1) or "latest"
                                    
                                    if vet_version != uni_version:
                                        mismatch = {
                                            "technology": tech,
                                            "vet_version": vet_version,
                                            "uni_version": uni_version,
                                            "skill_preserved": preservation_rate
                                        }
                                        result["version_mismatches"].append(mismatch)
                                        result["core_skill_preserved"][tech] = preservation_rate
                                        
                                        # Assess update difficulty
                                        difficulty = self._assess_update_difficulty(
                                            tech, vet_version, uni_version
                                        )
                                        result["update_difficulty"][tech] = difficulty
                                        
                                        # Add training requirement
                                        result["training_requirements"].append(
                                            f"Update {tech} from {vet_version} to {uni_version}"
                                        )
        
        return result
    
    def handle_prerequisite_chain(self,
                                  vet_units: List[UnitOfCompetency],
                                  uni_course: UniCourse) -> Dict[str, Any]:
        """Handle prerequisite chains and dependencies"""
        result = {
            "missing_prerequisites": [],
            "prerequisite_coverage": {},
            "dependency_gaps": [],
            "recommended_sequence": []
        }
        
        # Check if VET units cover uni course prerequisites
        for prereq in uni_course.prerequisites:
            prereq_lower = prereq.lower()
            covered = False
            
            for unit in vet_units:
                # Check in unit name, description, and skills
                if (prereq_lower in unit.name.lower() or 
                    prereq_lower in unit.description.lower() or
                    any(prereq_lower in s.name.lower() for s in unit.extracted_skills)):
                    covered = True
                    result["prerequisite_coverage"][prereq] = unit.code
                    break
            
            if not covered:
                result["missing_prerequisites"].append(prereq)
                result["dependency_gaps"].append(f"Prerequisite '{prereq}' not covered")
        
        # Check VET prerequisite alignment
        vet_prereqs = set()
        for unit in vet_units:
            vet_prereqs.update(unit.prerequisites)
        
        # Recommend sequence if prerequisites are missing
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
        
        # Calculate total VET hours
        result["vet_total_hours"] = sum(unit.nominal_hours for unit in vet_units)
        
        # Typical conversion: 1 credit point = 10-15 hours of study
        estimated_uni_hours = uni_course.credit_points * 12.5  # Using middle value
        
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
        for target in target_skills:
            for source in source_skills:
                if self._skills_similar(source.name, target.name, threshold=0.7):
                    covered += 1
                    break
        
        return covered / len(target_skills)
    
    def _skills_similar(self, skill1: str, skill2: str, threshold: float = 0.7) -> bool:
        """Check if two skill names are similar"""
        skill1_lower = skill1.lower()
        skill2_lower = skill2.lower()
        
        # Exact match
        if skill1_lower == skill2_lower:
            return True
        
        # One contains the other
        if skill1_lower in skill2_lower or skill2_lower in skill1_lower:
            return True
        
        # Word overlap
        words1 = set(skill1_lower.split())
        words2 = set(skill2_lower.split())
        
        if words1 and words2:
            jaccard = len(words1.intersection(words2)) / len(words1.union(words2))
            return jaccard >= threshold
        
        return False
    
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
        # Sort units by coverage (greedy approach)
        sorted_units = sorted(
            coverage_by_unit.items(), 
            key=lambda x: x[1]["coverage"] if isinstance(x[1], dict) else x[1],
            reverse=True
        )
        
        combination = []
        cumulative_coverage = 0.0
        
        for unit_code, info in sorted_units:
            coverage = info["coverage"] if isinstance(info, dict) else info
            
            # Add unit to combination
            combination.append(unit_code)
            
            # Update cumulative coverage (with diminishing returns)
            marginal_coverage = coverage * (1 - cumulative_coverage * 0.2)
            cumulative_coverage += marginal_coverage
            
            if cumulative_coverage >= threshold:
                break
        
        return combination
    
    def _find_optimal_combination(self, 
                                  units: List[UnitOfCompetency],
                                  course: UniCourse,
                                  threshold: float) -> List[str]:
        """Find optimal combination for best coverage with minimal redundancy"""
        # More sophisticated than minimum - considers overlap
        best_combination = []
        best_coverage = 0.0
        
        # Try different combinations (simplified - in practice use optimization)
        from itertools import combinations
        
        for r in range(1, min(4, len(units) + 1)):  # Limit to combinations of 3
            for combo in combinations(units, r):
                combo_skills = []
                for unit in combo:
                    combo_skills.extend(unit.extracted_skills)
                
                coverage = self._calculate_skill_coverage(combo_skills, course.extracted_skills)
                
                if coverage >= threshold and coverage > best_coverage:
                    best_coverage = coverage
                    best_combination = [u.code for u in combo]
                    
                    # Early exit if excellent coverage
                    if coverage >= 0.95:
                        return best_combination
        
        return best_combination if best_combination else [u.code for u in units]
    
    def _identify_missing_skills(self, 
                                 source_skills: List[Skill],
                                 target_skills: List[Skill]) -> List[str]:
        """Identify skills in target that aren't in source"""
        missing = []
        
        for target in target_skills:
            found = False
            for source in source_skills:
                if self._skills_similar(source.name, target.name):
                    found = True
                    break
            
            if not found:
                missing.append(target.name)
        
        return missing
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, float]:
        """Calculate distribution statistics"""
        if not values:
            return {}
        
        return {
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values))
        }
    
    def _decompose_skill(self, skill_name: str) -> List[str]:
        """Decompose composite skill into components"""
        # Simplified decomposition rules
        decomposition_rules = {
            "project management": ["planning", "execution", "monitoring", "closure"],
            "software development": ["design", "coding", "testing", "deployment"],
            "data analysis": ["collection", "processing", "visualization", "interpretation"],
            "system administration": ["configuration", "monitoring", "maintenance", "security"],
            "web development": ["frontend", "backend", "database", "deployment"],
        }
        
        skill_lower = skill_name.lower()
        
        for composite, components in decomposition_rules.items():
            if composite in skill_lower:
                # Add context from original skill
                context = skill_lower.replace(composite, "").strip()
                if context:
                    return [f"{comp} {context}" for comp in components]
                return components
        
        return [skill_name]
    
    def _assess_update_difficulty(self, 
                                  tech: str, 
                                  old_version: str,
                                  new_version: str) -> str:
        """Assess difficulty of updating from old to new version"""
        # Difficulty assessment rules
        difficulty_map = {
            "python": {
                ("2", "3"): "medium",
                ("3", "3"): "low"
            },
            "java": {
                ("8", "11"): "low",
                ("8", "17"): "medium",
                ("6", "11"): "high"
            },
            "angular": {
                ("js", "2"): "high",
                ("2", "latest"): "medium"
            }
        }
        
        # Try to extract major version numbers
        old_major = re.match(r"(\d+)", old_version)
        new_major = re.match(r"(\d+)", new_version)
        
        if old_major and new_major:
            old_v = old_major.group(1)
            new_v = new_major.group(1)
            
            if tech in difficulty_map:
                for (from_v, to_v), difficulty in difficulty_map[tech].items():
                    if old_v == from_v and new_v == to_v:
                        return difficulty
        
        # Default based on version difference
        try:
            if old_major and new_major:
                diff = int(new_major.group(1)) - int(old_major.group(1))
                if diff <= 1:
                    return "low"
                elif diff <= 3:
                    return "medium"
                else:
                    return "high"
        except:
            pass
        
        return "medium"  # Default
