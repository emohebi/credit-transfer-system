"""
Skill export and import module for storing extracted skills
Supports JSON and CSV formats for VET and University courses
"""

import json
import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from io import StringIO

from models.base_models import (
    VETQualification, UniQualification, 
    UnitOfCompetency, UniCourse, Skill
)
from models.enums import SkillLevel, SkillContext, SkillCategory

logger = logging.getLogger(__name__)


class SkillExportManager:
    """Manages export and import of extracted skills for courses"""
    
    def __init__(self, output_dir: str = "output/skills"):
        """
        Initialize skill export manager
        
        Args:
            output_dir: Directory for saving skill files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.vet_dir = self.output_dir / "vet"
        self.uni_dir = self.output_dir / "uni"
        self.combined_dir = self.output_dir / "combined"
        
        for dir_path in [self.vet_dir, self.uni_dir, self.combined_dir]:
            dir_path.mkdir(exist_ok=True)
    
    # ========== EXPORT METHODS ==========
    
    def export_vet_skills(self, 
                         vet_qual: VETQualification,
                         format: str = "json",
                         include_metadata: bool = True) -> str:
        """
        Export VET qualification skills to file
        
        Args:
            vet_qual: VET qualification with extracted skills
            format: Output format ('json' or 'csv')
            include_metadata: Whether to include metadata in export
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filepath = self.vet_dir / f"{vet_qual.code}_skills_{timestamp}.json"
            self._export_vet_to_json(vet_qual, filepath, include_metadata)
        elif format == "csv":
            filepath = self.vet_dir / f"{vet_qual.code}_skills_{timestamp}.csv"
            self._export_vet_to_csv(vet_qual, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported VET skills to {filepath}")
        return str(filepath)
    
    def export_uni_skills(self,
                         uni_qual: UniQualification,
                         format: str = "json",
                         include_metadata: bool = True) -> str:
        """
        Export University qualification skills to file
        
        Args:
            uni_qual: University qualification with extracted skills
            format: Output format ('json' or 'csv')
            include_metadata: Whether to include metadata in export
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filepath = self.uni_dir / f"{uni_qual.code}_skills_{timestamp}.json"
            self._export_uni_to_json(uni_qual, filepath, include_metadata)
        elif format == "csv":
            filepath = self.uni_dir / f"{uni_qual.code}_skills_{timestamp}.csv"
            self._export_uni_to_csv(uni_qual, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported University skills to {filepath}")
        return str(filepath)
    
    def export_combined_skills(self,
                               vet_qual: VETQualification,
                               uni_qual: UniQualification,
                               format: str = "json") -> str:
        """
        Export both VET and University skills in a combined file
        
        Args:
            vet_qual: VET qualification with extracted skills
            uni_qual: University qualification with extracted skills
            format: Output format ('json' or 'csv')
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filepath = self.combined_dir / f"combined_skills_{timestamp}.json"
            self._export_combined_to_json(vet_qual, uni_qual, filepath)
        elif format == "csv":
            filepath = self.combined_dir / f"combined_skills_{timestamp}.csv"
            self._export_combined_to_csv(vet_qual, uni_qual, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Exported combined skills to {filepath}")
        return str(filepath)
    
    # ========== JSON EXPORT METHODS ==========
    
    def _export_vet_to_json(self, 
                           vet_qual: VETQualification, 
                           filepath: Path,
                           include_metadata: bool = True):
        """Export VET skills to JSON file"""
        data = {
            "qualification": {
                "code": vet_qual.code,
                "name": vet_qual.name,
                "level": vet_qual.level,
                "total_units": len(vet_qual.units)
            },
            "export_timestamp": datetime.now().isoformat(),
            "units": []
        }
        
        # Add metadata if requested
        if include_metadata:
            data["metadata"] = vet_qual.metadata
        
        # Export each unit's skills
        for unit in vet_qual.units:
            unit_data = {
                "code": unit.code,
                "name": unit.name,
                "nominal_hours": unit.nominal_hours,
                "prerequisites": unit.prerequisites,
                "total_skills": len(unit.extracted_skills),
                "skills": []
            }
            
            # Add each skill with all attributes
            for skill in unit.extracted_skills:
                skill_data = {
                    "name": skill.name,
                    "category": skill.category.value,
                    "level": skill.level.name,
                    "level_value": skill.level.value,
                    "context": skill.context.value,
                    "keywords": skill.keywords,
                    "evidence_type": skill.evidence_type,
                    "confidence": skill.confidence,
                    "source": skill.source
                }
                
                if include_metadata and skill.metadata:
                    skill_data["metadata"] = skill.metadata
                
                unit_data["skills"].append(skill_data)
            
            # Add skill statistics
            unit_data["statistics"] = self._calculate_skill_statistics(unit.extracted_skills)
            
            data["units"].append(unit_data)
        
        # Add overall statistics
        all_skills = []
        for unit in vet_qual.units:
            all_skills.extend(unit.extracted_skills)
        
        data["overall_statistics"] = self._calculate_skill_statistics(all_skills)
        data["total_skills"] = len(all_skills)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_uni_to_json(self,
                           uni_qual: UniQualification,
                           filepath: Path,
                           include_metadata: bool = True):
        """Export University skills to JSON file"""
        data = {
            "qualification": {
                "code": uni_qual.code,
                "name": uni_qual.name,
                "total_credit_points": uni_qual.total_credit_points,
                "duration_years": uni_qual.duration_years,
                "total_courses": len(uni_qual.courses)
            },
            "export_timestamp": datetime.now().isoformat(),
            "courses": []
        }
        
        # Add metadata if requested
        if include_metadata:
            data["metadata"] = uni_qual.metadata
        
        # Export each course's skills
        for course in uni_qual.courses:
            course_data = {
                "code": course.code,
                "name": course.name,
                "study_level": course.study_level,
                "credit_points": course.credit_points,
                "prerequisites": course.prerequisites,
                "topics": course.topics,
                "total_skills": len(course.extracted_skills),
                "skills": []
            }
            
            # Add each skill with all attributes
            for skill in course.extracted_skills:
                skill_data = {
                    "name": skill.name,
                    "category": skill.category.value,
                    "level": skill.level.name,
                    "level_value": skill.level.value,
                    "context": skill.context.value,
                    "keywords": skill.keywords,
                    "evidence_type": skill.evidence_type,
                    "confidence": skill.confidence,
                    "source": skill.source
                }
                
                if include_metadata and skill.metadata:
                    skill_data["metadata"] = skill.metadata
                
                course_data["skills"].append(skill_data)
            
            # Add skill statistics
            course_data["statistics"] = self._calculate_skill_statistics(course.extracted_skills)
            
            data["courses"].append(course_data)
        
        # Group courses by study level
        study_levels = {}
        for course in uni_qual.courses:
            level = course.study_level
            if level not in study_levels:
                study_levels[level] = []
            study_levels[level].append(course.code)
        
        data["courses_by_study_level"] = study_levels
        
        # Add overall statistics
        all_skills = []
        for course in uni_qual.courses:
            all_skills.extend(course.extracted_skills)
        
        data["overall_statistics"] = self._calculate_skill_statistics(all_skills)
        data["total_skills"] = len(all_skills)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_combined_to_json(self,
                                 vet_qual: VETQualification,
                                 uni_qual: UniQualification,
                                 filepath: Path):
        """Export combined VET and University skills to JSON"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "vet_qualification": {
                "code": vet_qual.code,
                "name": vet_qual.name,
                "level": vet_qual.level,
                "units": []
            },
            "uni_qualification": {
                "code": uni_qual.code,
                "name": uni_qual.name,
                "courses": []
            },
            "comparison": {}
        }
        
        # Add VET units
        vet_skills = []
        for unit in vet_qual.units:
            unit_summary = {
                "code": unit.code,
                "name": unit.name,
                "skill_count": len(unit.extracted_skills),
                "skills": [s.name for s in unit.extracted_skills]
            }
            data["vet_qualification"]["units"].append(unit_summary)
            vet_skills.extend(unit.extracted_skills)
        
        # Add University courses
        uni_skills = []
        for course in uni_qual.courses:
            course_summary = {
                "code": course.code,
                "name": course.name,
                "study_level": course.study_level,
                "skill_count": len(course.extracted_skills),
                "skills": [s.name for s in course.extracted_skills]
            }
            data["uni_qualification"]["courses"].append(course_summary)
            uni_skills.extend(course.extracted_skills)
        
        # Add comparison statistics
        data["comparison"] = {
            "vet_total_skills": len(vet_skills),
            "uni_total_skills": len(uni_skills),
            "vet_unique_skills": len(set(s.name.lower() for s in vet_skills)),
            "uni_unique_skills": len(set(s.name.lower() for s in uni_skills)),
            "common_skills": self._find_common_skills(vet_skills, uni_skills),
            "vet_statistics": self._calculate_skill_statistics(vet_skills),
            "uni_statistics": self._calculate_skill_statistics(uni_skills)
        }
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ========== CSV EXPORT METHODS ==========
    
    def _export_vet_to_csv(self, vet_qual: VETQualification, filepath: Path):
        """Export VET skills to CSV file"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'qualification_code', 'qualification_name', 'unit_code', 'unit_name',
                'unit_hours', 'skill_name', 'category', 'level', 'level_value',
                'context', 'confidence', 'keywords', 'source', 'evidence_type'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for unit in vet_qual.units:
                for skill in unit.extracted_skills:
                    writer.writerow({
                        'qualification_code': vet_qual.code,
                        'qualification_name': vet_qual.name,
                        'unit_code': unit.code,
                        'unit_name': unit.name,
                        'unit_hours': unit.nominal_hours,
                        'skill_name': skill.name,
                        'category': skill.category.value,
                        'level': skill.level.name,
                        'level_value': skill.level.value,
                        'context': skill.context.value,
                        'confidence': f"{skill.confidence:.2f}",
                        'keywords': '; '.join(skill.keywords),
                        'source': skill.source,
                        'evidence_type': skill.evidence_type
                    })
    
    def _export_uni_to_csv(self, uni_qual: UniQualification, filepath: Path):
        """Export University skills to CSV file"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'qualification_code', 'qualification_name', 'course_code', 'course_name',
                'study_level', 'credit_points', 'skill_name', 'category', 'level',
                'level_value', 'context', 'confidence', 'keywords', 'source', 'evidence_type'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for course in uni_qual.courses:
                for skill in course.extracted_skills:
                    writer.writerow({
                        'qualification_code': uni_qual.code,
                        'qualification_name': uni_qual.name,
                        'course_code': course.code,
                        'course_name': course.name,
                        'study_level': course.study_level,
                        'credit_points': course.credit_points,
                        'skill_name': skill.name,
                        'category': skill.category.value,
                        'level': skill.level.name,
                        'level_value': skill.level.value,
                        'context': skill.context.value,
                        'confidence': f"{skill.confidence:.2f}",
                        'keywords': '; '.join(skill.keywords),
                        'source': skill.source,
                        'evidence_type': skill.evidence_type
                    })
    
    def _export_combined_to_csv(self,
                                vet_qual: VETQualification,
                                uni_qual: UniQualification,
                                filepath: Path):
        """Export combined VET and University skills to CSV"""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'source_type', 'qualification_code', 'qualification_name',
                'unit_course_code', 'unit_course_name', 'study_level_or_hours',
                'skill_name', 'category', 'level', 'context', 'confidence'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write VET skills
            for unit in vet_qual.units:
                for skill in unit.extracted_skills:
                    writer.writerow({
                        'source_type': 'VET',
                        'qualification_code': vet_qual.code,
                        'qualification_name': vet_qual.name,
                        'unit_course_code': unit.code,
                        'unit_course_name': unit.name,
                        'study_level_or_hours': f"{unit.nominal_hours}h",
                        'skill_name': skill.name,
                        'category': skill.category.value,
                        'level': skill.level.name,
                        'context': skill.context.value,
                        'confidence': f"{skill.confidence:.2f}"
                    })
            
            # Write University skills
            for course in uni_qual.courses:
                for skill in course.extracted_skills:
                    writer.writerow({
                        'source_type': 'University',
                        'qualification_code': uni_qual.code,
                        'qualification_name': uni_qual.name,
                        'unit_course_code': course.code,
                        'unit_course_name': course.name,
                        'study_level_or_hours': course.study_level,
                        'skill_name': skill.name,
                        'category': skill.category.value,
                        'level': skill.level.name,
                        'context': skill.context.value,
                        'confidence': f"{skill.confidence:.2f}"
                    })
    
    # ========== IMPORT METHODS ==========
    
    def import_vet_skills(self, filepath: str) -> VETQualification:
        """
        Import VET skills from JSON file
        
        Args:
            filepath: Path to JSON file with VET skills
            
        Returns:
            VETQualification object with loaded skills
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create VET qualification
        qual_data = data["qualification"]
        vet_qual = VETQualification(
            code=qual_data["code"],
            name=qual_data["name"],
            level=qual_data["level"]
        )
        
        # Load units and skills
        for unit_data in data["units"]:
            unit = UnitOfCompetency(
                code=unit_data["code"],
                name=unit_data["name"],
                description="",
                nominal_hours=unit_data.get("nominal_hours", 0),
                prerequisites=unit_data.get("prerequisites", [])
            )
            
            # Load skills
            for skill_data in unit_data["skills"]:
                skill = Skill(
                    name=skill_data["name"],
                    category=SkillCategory(skill_data["category"]),
                    level=SkillLevel[skill_data["level"]],
                    context=SkillContext(skill_data["context"]),
                    keywords=skill_data.get("keywords", []),
                    evidence_type=skill_data.get("evidence_type", ""),
                    confidence=skill_data.get("confidence", 1.0),
                    source=skill_data.get("source", ""),
                    metadata=skill_data.get("metadata", {})
                )
                unit.extracted_skills.append(skill)
            
            vet_qual.units.append(unit)
        
        logger.info(f"Imported VET skills from {filepath}")
        return vet_qual
    
    def import_uni_skills(self, filepath: str) -> UniQualification:
        """
        Import University skills from JSON file
        
        Args:
            filepath: Path to JSON file with University skills
            
        Returns:
            UniQualification object with loaded skills
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create University qualification
        qual_data = data["qualification"]
        uni_qual = UniQualification(
            code=qual_data["code"],
            name=qual_data["name"],
            total_credit_points=qual_data.get("total_credit_points", 0),
            duration_years=qual_data.get("duration_years", 4)
        )
        
        # Load courses and skills
        for course_data in data["courses"]:
            course = UniCourse(
                code=course_data["code"],
                name=course_data["name"],
                description="",
                study_level=course_data.get("study_level", "intermediate"),
                credit_points=course_data.get("credit_points", 0),
                prerequisites=course_data.get("prerequisites", []),
                topics=course_data.get("topics", [])
            )
            
            # Load skills
            for skill_data in course_data["skills"]:
                skill = Skill(
                    name=skill_data["name"],
                    category=SkillCategory(skill_data["category"]),
                    level=SkillLevel[skill_data["level"]],
                    context=SkillContext(skill_data["context"]),
                    keywords=skill_data.get("keywords", []),
                    evidence_type=skill_data.get("evidence_type", ""),
                    confidence=skill_data.get("confidence", 1.0),
                    source=skill_data.get("source", ""),
                    metadata=skill_data.get("metadata", {})
                )
                course.extracted_skills.append(skill)
            
            uni_qual.courses.append(course)
        
        logger.info(f"Imported University skills from {filepath}")
        return uni_qual
    
    # ========== UTILITY METHODS ==========
    
    def _calculate_skill_statistics(self, skills: List[Skill]) -> Dict[str, Any]:
        """Calculate statistics for a list of skills"""
        if not skills:
            return {}
        
        stats = {
            "total_count": len(skills),
            "unique_count": len(set(s.name.lower() for s in skills)),
            "average_confidence": sum(s.confidence for s in skills) / len(skills),
            "by_category": {},
            "by_level": {},
            "by_context": {}
        }
        
        # Count by category
        for category in SkillCategory:
            count = sum(1 for s in skills if s.category == category)
            if count > 0:
                stats["by_category"][category.value] = count
        
        # Count by level
        for level in SkillLevel:
            count = sum(1 for s in skills if s.level == level)
            if count > 0:
                stats["by_level"][level.name] = count
        
        # Count by context
        for context in SkillContext:
            count = sum(1 for s in skills if s.context == context)
            if count > 0:
                stats["by_context"][context.value] = count
        
        # Top keywords
        all_keywords = []
        for skill in skills:
            all_keywords.extend(skill.keywords)
        
        if all_keywords:
            from collections import Counter
            keyword_counts = Counter(all_keywords)
            stats["top_keywords"] = [kw for kw, _ in keyword_counts.most_common(10)]
        
        return stats
    
    def _find_common_skills(self, 
                           vet_skills: List[Skill], 
                           uni_skills: List[Skill]) -> List[str]:
        """Find skills common to both VET and University"""
        vet_names = {s.name.lower() for s in vet_skills}
        uni_names = {s.name.lower() for s in uni_skills}
        
        common = vet_names.intersection(uni_names)
        return sorted(list(common))[:20]  # Return top 20 common skills
    
    def generate_skill_report(self,
                             vet_qual: Optional[VETQualification] = None,
                             uni_qual: Optional[UniQualification] = None) -> str:
        """
        Generate a detailed text report of extracted skills
        
        Args:
            vet_qual: VET qualification with extracted skills
            uni_qual: University qualification with extracted skills
            
        Returns:
            Text report as string
        """
        report = []
        report.append("=" * 80)
        report.append("EXTRACTED SKILLS REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if vet_qual:
            report.append("\n" + "=" * 80)
            report.append(f"VET QUALIFICATION: {vet_qual.code} - {vet_qual.name}")
            report.append("=" * 80)
            
            total_vet_skills = 0
            for unit in vet_qual.units:
                report.append(f"\nUnit: {unit.code} - {unit.name}")
                report.append(f"Nominal Hours: {unit.nominal_hours}")
                report.append(f"Skills Extracted: {len(unit.extracted_skills)}")
                
                if unit.extracted_skills:
                    report.append("\nTop Skills (by confidence):")
                    sorted_skills = sorted(unit.extracted_skills, 
                                         key=lambda s: s.confidence, 
                                         reverse=True)
                    
                    for skill in sorted_skills[:5]:
                        report.append(f"  • {skill.name}")
                        report.append(f"    Category: {skill.category.value}, "
                                    f"Level: {skill.level.name}, "
                                    f"Context: {skill.context.value}, "
                                    f"Confidence: {skill.confidence:.2f}")
                
                total_vet_skills += len(unit.extracted_skills)
            
            report.append(f"\nTotal VET Skills: {total_vet_skills}")
            
            # VET statistics
            all_vet_skills = []
            for unit in vet_qual.units:
                all_vet_skills.extend(unit.extracted_skills)
            
            if all_vet_skills:
                stats = self._calculate_skill_statistics(all_vet_skills)
                report.append("\nVET Skills Statistics:")
                report.append(f"  Unique Skills: {stats['unique_count']}")
                report.append(f"  Average Confidence: {stats['average_confidence']:.2f}")
                
                report.append("  By Category:")
                for cat, count in stats['by_category'].items():
                    report.append(f"    {cat}: {count}")
                
                report.append("  By Level:")
                for level, count in stats['by_level'].items():
                    report.append(f"    {level}: {count}")
        
        if uni_qual:
            report.append("\n" + "=" * 80)
            report.append(f"UNIVERSITY QUALIFICATION: {uni_qual.code} - {uni_qual.name}")
            report.append("=" * 80)
            
            total_uni_skills = 0
            
            # Group courses by study level
            by_level = {}
            for course in uni_qual.courses:
                level = course.study_level
                if level not in by_level:
                    by_level[level] = []
                by_level[level].append(course)
            
            for study_level in sorted(by_level.keys()):
                report.append(f"\n{study_level.upper()} Level Courses:")
                
                for course in by_level[study_level]:
                    report.append(f"\nCourse: {course.code} - {course.name}")
                    report.append(f"Credit Points: {course.credit_points}")
                    report.append(f"Skills Extracted: {len(course.extracted_skills)}")
                    
                    if course.extracted_skills:
                        report.append("\nTop Skills (by confidence):")
                        sorted_skills = sorted(course.extracted_skills, 
                                             key=lambda s: s.confidence, 
                                             reverse=True)
                        
                        for skill in sorted_skills[:5]:
                            report.append(f"  • {skill.name}")
                            report.append(f"    Category: {skill.category.value}, "
                                        f"Level: {skill.level.name}, "
                                        f"Context: {skill.context.value}, "
                                        f"Confidence: {skill.confidence:.2f}")
                    
                    total_uni_skills += len(course.extracted_skills)
            
            report.append(f"\nTotal University Skills: {total_uni_skills}")
            
            # University statistics
            all_uni_skills = []
            for course in uni_qual.courses:
                all_uni_skills.extend(course.extracted_skills)
            
            if all_uni_skills:
                stats = self._calculate_skill_statistics(all_uni_skills)
                report.append("\nUniversity Skills Statistics:")
                report.append(f"  Unique Skills: {stats['unique_count']}")
                report.append(f"  Average Confidence: {stats['average_confidence']:.2f}")
                
                report.append("  By Category:")
                for cat, count in stats['by_category'].items():
                    report.append(f"    {cat}: {count}")
                
                report.append("  By Level:")
                for level, count in stats['by_level'].items():
                    report.append(f"    {level}: {count}")
        
        # Comparison section if both are provided
        if vet_qual and uni_qual:
            report.append("\n" + "=" * 80)
            report.append("SKILL COMPARISON")
            report.append("=" * 80)
            
            all_vet_skills = []
            for unit in vet_qual.units:
                all_vet_skills.extend(unit.extracted_skills)
            
            all_uni_skills = []
            for course in uni_qual.courses:
                all_uni_skills.extend(course.extracted_skills)
            
            common_skills = self._find_common_skills(all_vet_skills, all_uni_skills)
            
            report.append(f"\nTotal VET Skills: {len(all_vet_skills)}")
            report.append(f"Total University Skills: {len(all_uni_skills)}")
            report.append(f"Common Skills Found: {len(common_skills)}")
            
            if common_skills:
                report.append("\nTop Common Skills:")
                for skill_name in common_skills[:10]:
                    report.append(f"  • {skill_name}")
        
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def export_skill_summary(self,
                            vet_qual: Optional[VETQualification] = None,
                            uni_qual: Optional[UniQualification] = None,
                            format: str = "json") -> str:
        """
        Export a summary of extracted skills
        
        Args:
            vet_qual: VET qualification with extracted skills
            uni_qual: University qualification with extracted skills
            format: Output format ('json' or 'text')
            
        Returns:
            Path to exported file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "json":
            filepath = self.output_dir / f"skill_summary_{timestamp}.json"
            
            summary = {
                "export_timestamp": datetime.now().isoformat(),
                "summary": {}
            }
            
            if vet_qual:
                all_vet_skills = []
                for unit in vet_qual.units:
                    all_vet_skills.extend(unit.extracted_skills)
                
                summary["summary"]["vet"] = {
                    "qualification": vet_qual.code,
                    "total_units": len(vet_qual.units),
                    "total_skills": len(all_vet_skills),
                    "statistics": self._calculate_skill_statistics(all_vet_skills)
                }
            
            if uni_qual:
                all_uni_skills = []
                for course in uni_qual.courses:
                    all_uni_skills.extend(course.extracted_skills)
                
                summary["summary"]["university"] = {
                    "qualification": uni_qual.code,
                    "total_courses": len(uni_qual.courses),
                    "total_skills": len(all_uni_skills),
                    "statistics": self._calculate_skill_statistics(all_uni_skills)
                }
            
            if vet_qual and uni_qual:
                all_vet_skills = []
                for unit in vet_qual.units:
                    all_vet_skills.extend(unit.extracted_skills)
                
                all_uni_skills = []
                for course in uni_qual.courses:
                    all_uni_skills.extend(course.extracted_skills)
                
                summary["summary"]["comparison"] = {
                    "common_skills": self._find_common_skills(all_vet_skills, all_uni_skills),
                    "vet_unique_count": len(set(s.name.lower() for s in all_vet_skills)),
                    "uni_unique_count": len(set(s.name.lower() for s in all_uni_skills))
                }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
        
        else:  # text format
            filepath = self.output_dir / f"skill_summary_{timestamp}.txt"
            report = self.generate_skill_report(vet_qual, uni_qual)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report)
        
        logger.info(f"Exported skill summary to {filepath}")
        return str(filepath)