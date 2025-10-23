"""
Report generator for credit transfer analysis
Integrated with skill export functionality
"""
import logging
import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import StringIO
from pathlib import Path

import numpy as np

from models.base_models import (
    CreditTransferRecommendation,
    VETQualification,
    UniQualification
)
from models.enums import RecommendationType, StudyLevel
from .skill_export import SkillExportManager
from utils.json_encoder import dumps, loads, make_json_serializable

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate various report formats for credit transfer analysis"""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize report generator with skill export capability
        
        Args:
            output_dir: Base output directory for reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize skill export manager
        self.skill_export = SkillExportManager(str(self.output_dir / "skills"))
    
    def generate_complete_report_package(self,
                                        recommendations: List[CreditTransferRecommendation],
                                        vet_qual: VETQualification,
                                        uni_qual: UniQualification) -> Dict[str, str]:
        """
        Generate a complete report package including all formats and skill exports
        
        Args:
            recommendations: List of credit transfer recommendations
            vet_qual: VET qualification
            uni_qual: University qualification
            
        Returns:
            Dictionary of file types and their paths
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = self.output_dir / f"report_package_{timestamp}"
        package_dir.mkdir(exist_ok=True)
        
        files = {}
        
        # Generate main recommendation report
        files['recommendations_json'] = str(package_dir / "recommendations.json")
        self._export_recommendations_json(recommendations, vet_qual, uni_qual, files['recommendations_json'])
        
        # Generate HTML report
        files['report_html'] = str(package_dir / "report.html")
        html_content = self.generate_html_report(recommendations, vet_qual, uni_qual)
        with open(files['report_html'], 'w') as f:
            f.write(html_content)
        
        # Generate CSV report
        files['recommendations_csv'] = str(package_dir / "recommendations.csv")
        csv_content = self.generate_csv_report(recommendations)
        with open(files['recommendations_csv'], 'w') as f:
            f.write(csv_content)
        
        # Export extracted skills
        skill_export_dir = package_dir / "extracted_skills"
        skill_export_dir.mkdir(exist_ok=True)
        
        # Export VET skills
        files['vet_skills_json'] = str(skill_export_dir / f"{vet_qual.code}_skills.json")
        self._export_skills_json(vet_qual, None, files['vet_skills_json'])
        
        files['vet_skills_excel'] = str(skill_export_dir / f"{vet_qual.code}_skills.xlsx")
        self._export_skills_excel(vet_qual, None, files['vet_skills_excel'])
        
        # Export University skills
        files['uni_skills_json'] = str(skill_export_dir / f"{uni_qual.code}_skills.json")
        self._export_skills_json(None, uni_qual, files['uni_skills_json'])
        
        files['uni_skills_excel'] = str(skill_export_dir / f"{uni_qual.code}_skills.xlsx")
        self._export_skills_excel(None, uni_qual, files['uni_skills_excel'])
        
        # Export combined skills
        files['combined_skills_json'] = str(skill_export_dir / "combined_skills.json")
        self._export_skills_json(vet_qual, uni_qual, files['combined_skills_json'])
        
        # Generate skill analysis report
        files['skill_analysis'] = str(skill_export_dir / "skill_analysis.txt")
        skill_report = self.skill_export.generate_skill_report(vet_qual, uni_qual)
        with open(files['skill_analysis'], 'w') as f:
            f.write(skill_report)
        
        # Create package summary
        files['package_summary'] = str(package_dir / "package_summary.json")
        self._create_package_summary(files, recommendations, vet_qual, uni_qual, files['package_summary'])
        
        # Add after the semantic clusters export
        files['skill_mappings_csv'] = str(package_dir / "skill_mappings.csv")
        self.export_skill_mappings_to_csv(recommendations, files['skill_mappings_csv'])
            
        # In generate_complete_report_package, after the main reports
        
        return files
    
    def _export_skills_json(self, 
                           vet_qual: Optional[VETQualification],
                           uni_qual: Optional[UniQualification],
                           filepath: str):
        """Export skills to JSON using skill export manager"""
        if vet_qual and uni_qual:
            # Combined export
            self.skill_export._export_combined_to_json(vet_qual, uni_qual, Path(filepath))
        elif vet_qual:
            # VET only
            self.skill_export._export_vet_to_json(vet_qual, Path(filepath), include_metadata=True)
        elif uni_qual:
            # University only
            self.skill_export._export_uni_to_json(uni_qual, Path(filepath), include_metadata=True)
    
    def _export_skills_excel(self,
                        vet_qual: Optional[VETQualification],
                        uni_qual: Optional[UniQualification],
                        filepath: str):
        """Export skills to Excel using skill export manager"""
        if vet_qual and not uni_qual:
            self.skill_export._export_vet_to_excel(vet_qual, Path(filepath))
        elif uni_qual and not vet_qual:
            self.skill_export._export_uni_to_excel(uni_qual, Path(filepath))
        else:
            self.skill_export._export_combined_to_excel(vet_qual, uni_qual, Path(filepath))
        
    def _export_recommendations_json(self,
                                recommendations: List[CreditTransferRecommendation],
                                vet_qual: VETQualification,
                                uni_qual: UniQualification,
                                filepath: str):
        """Export recommendations to JSON with skill details"""
        data = {
            "export_timestamp": datetime.now().isoformat(),
            "vet_qualification": {
                "code": vet_qual.code,
                "name": vet_qual.name,
                "level": vet_qual.level
            },
            "uni_qualification": {
                "code": uni_qual.code,
                "name": uni_qual.name
            },
            "summary": self._generate_summary_stats(recommendations),
            "recommendations": []
        }
        
        for rec in recommendations:
            # Get base recommendation data
            rec_data = rec.to_dict()
            
            # Add detailed match analysis
            match_info = self._extract_detailed_match_info(rec)
            rec_data['detailed_analysis'] = {
                'match_breakdown': {
                    'direct': match_info['direct_matches'],
                    'partial': match_info['partial_matches'],
                    'unmapped': match_info['unmapped_critical'],
                    'total_target': match_info['total_uni_skills']
                },
                'score_components': match_info['score_components'],
                'quality_metrics': match_info['quality_breakdown'],
                'edge_cases': match_info['edge_cases'],
                'alignment_formula': match_info['alignment_calculation'],
                'reasoning': self._generate_transfer_reasoning(rec, match_info).replace('<br>', ' | ')
            }
            
            # Add skill details for mapped units and courses
            rec_data["vet_skills"] = []
            for unit in rec.vet_units:
                for skill in unit.extracted_skills:
                    rec_data["vet_skills"].append({
                        "unit": unit.code,
                        "name": skill.name,
                        "category": skill.category.value,
                        "level": skill.level.name,
                        "context": skill.context.value,
                        "confidence": skill.confidence
                    })
            
            rec_data["uni_skills"] = []
            for skill in rec.uni_course.extracted_skills:
                rec_data["uni_skills"].append({
                    "name": skill.name,
                    "category": skill.category.value,
                    "level": skill.level.name,
                    "context": skill.context.value,
                    "confidence": skill.confidence
                })
            
            data["recommendations"].append(rec_data)
        data = make_json_serializable(data)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_package_summary(self,
                               files: Dict[str, str],
                               recommendations: List[CreditTransferRecommendation],
                               vet_qual: VETQualification,
                               uni_qual: UniQualification,
                               filepath: str):
        """Create a summary of the report package"""
        # Calculate skill statistics
        vet_skills = []
        for unit in vet_qual.units:
            vet_skills.extend(unit.extracted_skills)
        
        uni_skills = []
        for course in uni_qual.courses:
            uni_skills.extend(course.extracted_skills)
        
        summary = {
            "package_created": datetime.now().isoformat(),
            "files_generated": files,
            "analysis_summary": {
                "vet_qualification": f"{vet_qual.code} - {vet_qual.name}",
                "uni_qualification": f"{uni_qual.code} - {uni_qual.name}",
                "total_recommendations": len(recommendations),
                "recommendation_breakdown": self._generate_summary_stats(recommendations)
            },
            "skill_extraction_summary": {
                "vet_skills_extracted": len(vet_skills),
                "vet_unique_skills": len(set(s.name.lower() for s in vet_skills)),
                "uni_skills_extracted": len(uni_skills),
                "uni_unique_skills": len(set(s.name.lower() for s in uni_skills)),
                "common_skills_count": len(
                    set(s.name.lower() for s in vet_skills).intersection(
                        set(s.name.lower() for s in uni_skills)
                    )
                )
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
    
    def generate_full_report(self,
                             recommendations: List[CreditTransferRecommendation],
                             vet_qual: VETQualification,
                             uni_qual: UniQualification) -> str:
        """Generate comprehensive text report with skill details"""
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("CREDIT TRANSFER ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nVET Qualification: {vet_qual.code} - {vet_qual.name}")
        report.append(f"Level: {vet_qual.level}")
        report.append(f"Total Units: {len(vet_qual.units)}")
        
        # Add VET skill summary
        vet_skills = []
        for unit in vet_qual.units:
            vet_skills.extend(unit.extracted_skills)
        report.append(f"Total VET Skills Extracted: {len(vet_skills)}")
        report.append(f"Unique VET Skills: {len(set(s.name.lower() for s in vet_skills))}")
        
        report.append(f"\nUniversity Program: {uni_qual.code} - {uni_qual.name}")
        report.append(f"Total Courses: {len(uni_qual.courses)}")
        
        # Add University skill summary
        uni_skills = []
        for course in uni_qual.courses:
            uni_skills.extend(course.extracted_skills)
        report.append(f"Total University Skills Extracted: {len(uni_skills)}")
        report.append(f"Unique University Skills: {len(set(s.name.lower() for s in uni_skills))}")
        
        # Executive Summary
        report.append("\n" + "=" * 80)
        report.append("EXECUTIVE SUMMARY")
        report.append("=" * 80)
        
        summary = self._generate_summary_stats(recommendations)
        report.append(f"\nTotal Recommendations: {summary['total']}")
        report.append(f"  • Full Credit Transfers: {summary['full_count']} ({summary['full_percent']:.1%})")
        report.append(f"  • Conditional Transfers: {summary['conditional_count']} ({summary['conditional_percent']:.1%})")
        report.append(f"  • Partial Transfers: {summary['partial_count']} ({summary['partial_percent']:.1%})")
        
        report.append(f"\nAverage Alignment Score: {summary['avg_alignment']:.1%}")
        report.append(f"Average Confidence: {summary['avg_confidence']:.1%}")
        
        # Skill Matching Summary
        report.append("\n" + "=" * 80)
        report.append("SKILL MATCHING SUMMARY")
        report.append("=" * 80)
        
        common_skills = set(s.name.lower() for s in vet_skills).intersection(
            set(s.name.lower() for s in uni_skills)
        )
        report.append(f"\nCommon Skills Found: {len(common_skills)}")
        if common_skills:
            report.append("Top Common Skills:")
            for skill in sorted(list(common_skills))[:10]:
                report.append(f"  • {skill}")
        
        # Course Coverage Analysis
        report.append("\n" + "=" * 80)
        report.append("COURSE COVERAGE ANALYSIS")
        report.append("=" * 80)
        
        coverage = self._analyze_course_coverage(recommendations, uni_qual)
        report.append(f"\nCourses with Credit Transfer Options: {coverage['courses_covered']}/{coverage['total_courses']}")
        report.append(f"Coverage Rate: {coverage['coverage_rate']:.1%}")
        
        report.append(f"\nBy Study Level:")
        for level in ["introductory", "intermediate", "advanced", "specialized"]:
            if level in coverage['by_level']:
                stats = coverage['by_level'][level]
                report.append(f"  {level.title()}: {stats['covered']}/{stats['total']} courses ({stats['rate']:.1%})")
        
        # Detailed Recommendations
        report.append("\n" + "=" * 80)
        report.append("DETAILED RECOMMENDATIONS")
        report.append("=" * 80)
        
        # Group by recommendation type
        full_recs = [r for r in recommendations if r.recommendation == RecommendationType.FULL]
        conditional_recs = [r for r in recommendations if r.recommendation == RecommendationType.CONDITIONAL]
        partial_recs = [r for r in recommendations if r.recommendation == RecommendationType.PARTIAL]
        
        if full_recs:
            report.append("\n--- FULL CREDIT TRANSFERS ---")
            for i, rec in enumerate(full_recs[:10], 1):
                report.append(self._format_recommendation_with_skills(i, rec))
        
        if conditional_recs:
            report.append("\n--- CONDITIONAL TRANSFERS ---")
            for i, rec in enumerate(conditional_recs[:10], 1):
                report.append(self._format_recommendation_with_skills(i, rec))
        
        if partial_recs:
            report.append("\n--- PARTIAL TRANSFERS ---")
            for i, rec in enumerate(partial_recs[:10], 1):
                report.append(self._format_recommendation_with_skills(i, rec))
        
        # Gap Analysis
        report.append("\n" + "=" * 80)
        report.append("GAP ANALYSIS")
        report.append("=" * 80)
        
        gaps = self._analyze_gaps(recommendations)
        report.append(f"\nMost Common Skill Gaps:")
        for skill, count in gaps['common_gaps'][:10]:
            report.append(f"  • {skill}: {count} occurrences")
        
        report.append(f"\nMost Common Conditions:")
        for condition, count in gaps['common_conditions'][:10]:
            report.append(f"  • {condition}: {count} occurrences")
        
        # Recommendations Summary
        report.append("\n" + "=" * 80)
        report.append("RECOMMENDATIONS")
        report.append("=" * 80)
        
        report.append("\n1. Priority Actions:")
        if gaps['common_gaps']:
            report.append("   • Develop bridging modules for frequently missing skills")
        if any(r.is_combination_transfer() for r in recommendations):
            report.append("   • Consider bundled unit delivery for combination transfers")
        if summary['avg_confidence'] < 0.7:
            report.append("   • Manual review recommended due to lower confidence scores")
        
        report.append("\n2. Implementation Considerations:")
        report.append("   • Review and validate high-scoring recommendations first")
        report.append("   • Develop clear pathways for conditional transfers")
        report.append("   • Create supplementary materials for identified skill gaps")
        report.append("   • Monitor and update skill mappings as curricula evolve")
        
        # Footer
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def _format_recommendation_with_skills(self, index: int, rec: CreditTransferRecommendation) -> str:
        """Format a single recommendation with skill details"""
        lines = []
        lines.append(f"\n{index}. {rec.uni_course.code}: {rec.uni_course.name} (Level: {rec.uni_course.study_level})")
        lines.append("-" * 60)
        
        # VET units
        lines.append("VET Units:")
        for unit in rec.vet_units:
            lines.append(f"  • {unit.code}: {unit.name}")
            lines.append(f"    Skills: {len(unit.extracted_skills)}")
        
        # Scores
        lines.append(f"\nAlignment Score: {rec.alignment_score:.1%}")
        lines.append(f"Confidence: {rec.confidence:.1%}")
        lines.append(f"Recommendation: {rec.recommendation.value.upper()}")
        
        # Evidence
        if rec.evidence:
            lines.append("\nEvidence:")
            for evidence in rec.evidence[:3]:
                lines.append(f"  • {evidence}")
        
        # Skill coverage
        lines.append("\nSkill Coverage:")
        for category, coverage in rec.skill_coverage.items():
            lines.append(f"  • {category}: {coverage:.1%}")
        
        # Show matched skills count
        uni_skill_count = len(rec.uni_course.extracted_skills)
        lines.append(f"\nUniversity Course Skills: {uni_skill_count}")
        
        # Conditions
        if rec.conditions:
            lines.append("\nConditions for Transfer:")
            for condition in rec.conditions[:3]:
                lines.append(f"  • {condition}")
        
        # Gaps
        if rec.gaps:
            lines.append("\nSkill Gaps:")
            for gap in rec.gaps[:5]:
                lines.append(f"  • {gap.name}")
        
        return "\n".join(lines)
    
    def generate_csv_report(self, recommendations: List[CreditTransferRecommendation]) -> str:
        """Generate CSV report with skill counts and detailed match info"""
        output = StringIO()
        
        fieldnames = [
            'VET_Units', 'VET_Skill_Count', 'Uni_Course_Code', 'Uni_Course_Name',
            'Uni_Skill_Count', 'Study_Level', 'Direct_Matches', 'Partial_Matches',
            'Unmapped_Skills', 'Coverage_Score', 'Context_Score', 'Quality_Score',
            'Edge_Penalty', 'Alignment_Score', 'Confidence', 'Recommendation_Type',
            'Transfer_Reasoning', 'Conditions', 'Evidence'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for rec in recommendations:
            # Extract detailed match info
            match_info = self._extract_detailed_match_info(rec)
            
            # Count VET skills
            vet_skill_count = sum(len(unit.extracted_skills) for unit in rec.vet_units)
            
            # Count university skills
            uni_skill_count = len(rec.uni_course.extracted_skills)
            
            writer.writerow({
                'VET_Units': ', '.join(rec.get_vet_unit_codes()),
                'VET_Skill_Count': vet_skill_count,
                'Uni_Course_Code': rec.uni_course.code,
                'Uni_Course_Name': rec.uni_course.name,
                'Uni_Skill_Count': uni_skill_count,
                'Study_Level': rec.uni_course.study_level,
                'Direct_Matches': match_info['direct_matches'],
                'Partial_Matches': match_info['partial_matches'],
                'Unmapped_Skills': match_info['unmapped_critical'],
                'Coverage_Score': f"{match_info['score_components']['coverage']:.2f}",
                'Context_Score': f"{match_info['score_components']['context']:.2f}",
                'Quality_Score': f"{match_info['score_components']['quality']:.2f}",
                'Edge_Penalty': f"{match_info['score_components']['edge_penalty']:.2f}",
                'Alignment_Score': f"{rec.alignment_score:.2%}",
                'Confidence': f"{rec.confidence:.2%}",
                'Recommendation_Type': rec.recommendation.value,
                'Transfer_Reasoning': self._generate_transfer_reasoning(rec, match_info).replace('<br>', '; '),
                'Conditions': '; '.join(rec.conditions[:3]),
                'Evidence': '; '.join(rec.evidence[:3])
            })
        
        return output.getvalue()
    
    def generate_html_report(self,
                         recommendations: List[CreditTransferRecommendation],
                         vet_qual: VETQualification,
                         uni_qual: UniQualification) -> str:
        """Generate HTML report with enhanced interactivity and modern design"""
        html = []
        
        # Enhanced HTML header with modern styles and libraries
        html.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Credit Transfer Analysis Report</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body { 
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }
                
                .container {
                    max-width: 1400px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 20px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    overflow: hidden;
                }
                
                .header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px;
                    position: relative;
                    overflow: hidden;
                }
                
                .header::before {
                    content: '';
                    position: absolute;
                    top: -50%;
                    right: -50%;
                    bottom: -50%;
                    left: -50%;
                    background: repeating-linear-gradient(
                        45deg,
                        transparent,
                        transparent 10px,
                        rgba(255, 255, 255, 0.05) 10px,
                        rgba(255, 255, 255, 0.05) 20px
                    );
                    animation: slide 20s linear infinite;
                }
                
                @keyframes slide {
                    0% { transform: translate(0, 0); }
                    100% { transform: translate(50px, 50px); }
                }
                
                .header-content {
                    position: relative;
                    z-index: 1;
                }
                
                h1 { 
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 10px;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
                }
                
                .header-info {
                    font-size: 0.95rem;
                    opacity: 0.95;
                    line-height: 1.6;
                }
                
                .content {
                    padding: 40px;
                }
                
                h2 { 
                    color: #2d3748;
                    font-size: 1.8rem;
                    font-weight: 600;
                    margin: 40px 0 20px 0;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                h2 i {
                    color: #667eea;
                    font-size: 1.5rem;
                }
                
                h3 { 
                    color: #4a5568;
                    font-size: 1.2rem;
                    font-weight: 500;
                    margin: 20px 0 15px 0;
                }
                
                /* Enhanced table styles */
                table { 
                    border-collapse: separate;
                    border-spacing: 0;
                    width: 100%;
                    margin: 25px 0;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                th { 
                    background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
                    color: white;
                    padding: 14px;
                    text-align: left;
                    font-weight: 600;
                    font-size: 0.9rem;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                }
                
                td { 
                    padding: 12px 14px;
                    border-bottom: 1px solid #e2e8f0;
                    font-size: 0.95rem;
                    transition: all 0.3s ease;
                }
                
                /* Recommendation type colors with gradients */
                .full.rec-group-even { 
                    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                }
                .full.rec-group-odd { 
                    background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
                }
                .conditional.rec-group-even { 
                    background: linear-gradient(135deg, #fff3cd 0%, #ffe8a1 100%);
                }
                .conditional.rec-group-odd { 
                    background: linear-gradient(135deg, #fff8e1 0%, #fff3cd 100%);
                }
                .partial.rec-group-even { 
                    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                }
                .partial.rec-group-odd { 
                    background: linear-gradient(135deg, #fae5e7 0%, #f8d7da 100%);
                }
                
                /* Enhanced hover effects */
                .full.hover-highlight { 
                    background: linear-gradient(135deg, #b8e0c1 0%, #a8d5b1 100%) !important;
                    transform: scale(1.01);
                }
                .conditional.hover-highlight { 
                    background: linear-gradient(135deg, #ffde7d 0%, #ffd966 100%) !important;
                    transform: scale(1.01);
                }
                .partial.hover-highlight { 
                    background: linear-gradient(135deg, #f0a6ad 0%, #eba0a7 100%) !important;
                    transform: scale(1.01);
                }
                
                /* Animated expand button */
                .expand-btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 20px;
                    cursor: pointer;
                    font-size: 0.85rem;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                }
                
                .expand-btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }
                
                .expand-btn i {
                    transition: transform 0.3s ease;
                }
                
                .expand-btn.expanded {
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                }
                
                .expand-btn.expanded i {
                    transform: rotate(180deg);
                }
                
                /* Enhanced expandable content */
                .expandable-content {
                    display: none;
                    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                    padding: 20px;
                    animation: slideDown 0.3s ease;
                }
                
                .expandable-content.show {
                    display: table-cell;
                }
                
                @keyframes slideDown {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                /* Enhanced summary boxes */
                .summary-box { 
                    background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
                    padding: 25px;
                    border-radius: 15px;
                    margin: 30px 0;
                    border-left: 4px solid #667eea;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
                }
                
                /* Enhanced stats grid */
                .stats-grid { 
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                
                .stat-card { 
                    background: white;
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
                    transition: all 0.3s ease;
                    border-top: 3px solid #667eea;
                    text-align: center;
                }
                
                .stat-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.12);
                }
                
                .stat-value { 
                    font-size: 2.5rem;
                    font-weight: 700;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-bottom: 8px;
                }
                
                .stat-label { 
                    color: #718096;
                    font-size: 0.95rem;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                /* Enhanced progress bars */
                .progress-container {
                    margin: 20px 0;
                }
                
                .progress-label {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 8px;
                    font-size: 0.9rem;
                    color: #4a5568;
                }
                
                .progress-bar { 
                    width: 100%;
                    height: 24px;
                    background: #e2e8f0;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
                }
                
                .progress-fill { 
                    height: 100%;
                    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                    border-radius: 12px;
                    transition: width 0.8s ease;
                    position: relative;
                    overflow: hidden;
                }
                
                .progress-fill::after {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: linear-gradient(
                        90deg,
                        transparent,
                        rgba(255, 255, 255, 0.3),
                        transparent
                    );
                    animation: shimmer 2s infinite;
                }
                
                @keyframes shimmer {
                    0% { transform: translateX(-100%); }
                    100% { transform: translateX(100%); }
                }
                
                /* Enhanced skill badges */
                .skill-badge { 
                    display: inline-block;
                    padding: 6px 12px;
                    margin: 4px;
                    background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
                    border-radius: 20px;
                    font-size: 0.85rem;
                    font-weight: 500;
                    transition: all 0.3s ease;
                    border: 1px solid #cbd5e0;
                    cursor: default;
                }
                
                .skill-badge:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-color: transparent;
                }
                
                .skill-level-badge {
                    display: inline-block;
                    padding: 3px 8px;
                    margin-left: 6px;
                    background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
                    color: white;
                    border-radius: 10px;
                    font-size: 0.75rem;
                    font-weight: 600;
                }
                
                .skill-context-badge {
                    display: inline-block;
                    padding: 3px 8px;
                    margin-left: 4px;
                    border-radius: 10px;
                    font-size: 0.75rem;
                    font-weight: 600;
                    color: white;
                }
                
                .skill-context-badge.theoretical {
                    background: linear-gradient(135deg, #9f7aea 0%, #805ad5 100%);
                }
                
                .skill-context-badge.practical {
                    background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
                }
                
                .skill-context-badge.hybrid {
                    background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
                }
                
                /* Enhanced inner skill mapping table */
                .skill-mapping-inner-table {
                    width: 100%;
                    border-collapse: separate;
                    border-spacing: 0;
                    margin: 15px 0;
                    font-size: 0.85rem;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                }
                
                .skill-mapping-inner-table th {
                    background: linear-gradient(135deg, #718096 0%, #4a5568 100%);
                    color: white;
                    padding: 10px;
                    text-align: left;
                    font-size: 0.8rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                .skill-mapping-inner-table td {
                    padding: 10px;
                    border-bottom: 1px solid #e2e8f0;
                    font-size: 0.85rem;
                }
                
                .mapping-direct td {
                    background: linear-gradient(90deg, #d4edda 0%, #c3e6cb 100%);
                    color: #155724;
                    font-weight: 500;
                }
                
                .mapping-partial td {
                    background: linear-gradient(90deg, #fff3cd 0%, #ffeaa7 100%);
                    color: #856404;
                    font-weight: 500;
                }
                
                .mapping-unmapped td {
                    background: linear-gradient(90deg, #f8d7da 0%, #f5c6cb 100%);
                    color: #721c24;
                }
                
                .mapping-summary {
                    margin: 15px 0;
                    padding: 15px;
                    background: linear-gradient(135deg, #edf2f7 0%, #e2e8f0 100%);
                    border-radius: 10px;
                    font-size: 0.9rem;
                    display: flex;
                    justify-content: space-around;
                    align-items: center;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                
                .mapping-stat {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }
                
                .mapping-stat-value {
                    font-size: 1.5rem;
                    font-weight: 700;
                    color: #667eea;
                }
                
                .mapping-stat-label {
                    font-size: 0.8rem;
                    color: #718096;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }
                
                /* Separator between recommendations */
                .rec-group-last {
                    border-bottom: 3px solid #667eea !important;
                }
                
                /* Search/Filter Bar */
                .search-container {
                    margin: 30px 0;
                    display: flex;
                    gap: 15px;
                    align-items: center;
                    flex-wrap: wrap;
                }
                
                .search-box {
                    flex: 1;
                    min-width: 300px;
                    position: relative;
                }
                
                .search-box input {
                    width: 100%;
                    padding: 12px 40px 12px 15px;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    font-size: 0.95rem;
                    transition: all 0.3s ease;
                }
                
                .search-box input:focus {
                    outline: none;
                    border-color: #667eea;
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }
                
                .search-box i {
                    position: absolute;
                    right: 15px;
                    top: 50%;
                    transform: translateY(-50%);
                    color: #718096;
                }
                
                .filter-btn {
                    padding: 12px 20px;
                    background: white;
                    border: 2px solid #e2e8f0;
                    border-radius: 10px;
                    cursor: pointer;
                    font-size: 0.95rem;
                    transition: all 0.3s ease;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                
                .filter-btn:hover {
                    border-color: #667eea;
                    color: #667eea;
                }
                
                .filter-btn.active {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border-color: transparent;
                }
                
                /* Tooltip */
                .tooltip {
                    position: relative;
                    cursor: help;
                }
                
                .tooltip .tooltiptext {
                    visibility: hidden;
                    width: 250px;
                    background: linear-gradient(135deg, #2d3748 0%, #1a202c 100%);
                    color: white;
                    text-align: center;
                    border-radius: 8px;
                    padding: 10px;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%;
                    left: 50%;
                    margin-left: -125px;
                    opacity: 0;
                    transition: opacity 0.3s;
                    font-size: 0.85rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                }
                
                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
                
                /* Back to top button */
                .back-to-top {
                    position: fixed;
                    bottom: 30px;
                    right: 30px;
                    width: 50px;
                    height: 50px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    cursor: pointer;
                    display: none;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.2rem;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                    transition: all 0.3s ease;
                    z-index: 1000;
                }
                
                .back-to-top:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
                }
                
                .back-to-top.show {
                    display: flex;
                }
                
                /* Print styles */
                @media print {
                    .header {
                        background: none;
                        color: black;
                    }
                    .expand-btn, .back-to-top, .search-container {
                        display: none !important;
                    }
                    .expandable-content {
                        display: table-cell !important;
                    }
                }
            </style>
            <script>
                function toggleExpand(btn, rowId) {
                    var content = document.getElementById('expand-' + rowId);
                    var icon = btn.querySelector('i');
                    if (content.classList.contains('show')) {
                        content.classList.remove('show');
                        btn.innerHTML = '<i class="fas fa-chevron-down"></i> Show Skills';
                        btn.classList.remove('expanded');
                    } else {
                        content.classList.add('show');
                        btn.innerHTML = '<i class="fas fa-chevron-up"></i> Hide Skills';
                        btn.classList.add('expanded');
                    }
                }
                
                // Enhanced hover effect for grouped rows
                document.addEventListener('DOMContentLoaded', function() {
                    // Hover effect
                    var rows = document.querySelectorAll('tr[data-rec-group]');
                    rows.forEach(function(row) {
                        row.addEventListener('mouseenter', function() {
                            var groupId = this.getAttribute('data-rec-group');
                            var groupRows = document.querySelectorAll('tr[data-rec-group="' + groupId + '"]');
                            groupRows.forEach(function(r) {
                                r.classList.add('hover-highlight');
                            });
                        });
                        row.addEventListener('mouseleave', function() {
                            var groupId = this.getAttribute('data-rec-group');
                            var groupRows = document.querySelectorAll('tr[data-rec-group="' + groupId + '"]');
                            groupRows.forEach(function(r) {
                                r.classList.remove('hover-highlight');
                            });
                        });
                    });
                    
                    // Search functionality
                    var searchInput = document.getElementById('searchInput');
                    if (searchInput) {
                        searchInput.addEventListener('keyup', function() {
                            var filter = this.value.toLowerCase();
                            var rows = document.querySelectorAll('tbody tr[data-rec-group]');
                            var currentGroup = '';
                            rows.forEach(function(row) {
                                var group = row.getAttribute('data-rec-group');
                                if (group !== currentGroup) {
                                    currentGroup = group;
                                    var text = row.textContent.toLowerCase();
                                    var groupRows = document.querySelectorAll('tr[data-rec-group="' + group + '"]');
                                    if (text.indexOf(filter) > -1) {
                                        groupRows.forEach(function(r) {
                                            r.style.display = '';
                                        });
                                    } else {
                                        groupRows.forEach(function(r) {
                                            r.style.display = 'none';
                                        });
                                    }
                                }
                            });
                        });
                    }
                    
                    // Filter buttons
                    var filterBtns = document.querySelectorAll('.filter-btn');
                    filterBtns.forEach(function(btn) {
                        btn.addEventListener('click', function() {
                            var filterType = this.getAttribute('data-filter');
                            
                            // Toggle active state
                            if (this.classList.contains('active')) {
                                this.classList.remove('active');
                                // Show all rows
                                document.querySelectorAll('tbody tr').forEach(function(row) {
                                    row.style.display = '';
                                });
                            } else {
                                // Remove active from all buttons
                                filterBtns.forEach(function(b) {
                                    b.classList.remove('active');
                                });
                                this.classList.add('active');
                                
                                // Filter rows
                                var rows = document.querySelectorAll('tbody tr[data-rec-group]');
                                rows.forEach(function(row) {
                                    if (row.classList.contains(filterType) || !row.classList.contains('full') && !row.classList.contains('conditional') && !row.classList.contains('partial')) {
                                        row.style.display = '';
                                    } else {
                                        row.style.display = 'none';
                                    }
                                });
                            }
                        });
                    });
                    
                    // Back to top button
                    window.onscroll = function() {
                        var backToTop = document.getElementById('backToTop');
                        if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
                            backToTop.classList.add('show');
                        } else {
                            backToTop.classList.remove('show');
                        }
                    };
                    
                    // Animate progress bars on load
                    setTimeout(function() {
                        var progressFills = document.querySelectorAll('.progress-fill');
                        progressFills.forEach(function(fill) {
                            var width = fill.getAttribute('data-width');
                            if (width) {
                                fill.style.width = width;
                            }
                        });
                    }, 100);
                });
                
                function scrollToTop() {
                    window.scrollTo({top: 0, behavior: 'smooth'});
                }
            </script>
        </head>
        <body>
        <div class="container">
        """)
        
        # Enhanced header
        html.append(f"""
        <div class="header">
            <div class="header-content">
                <h1><i class="fas fa-graduation-cap"></i> Credit Transfer Analysis Report</h1>
                <div class="header-info">
                    <p><i class="fas fa-calendar"></i> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><i class="fas fa-certificate"></i> VET Qualification: {vet_qual.code} - {vet_qual.name}</p>
                    <p><i class="fas fa-university"></i> University Program: {uni_qual.code} - {uni_qual.name}</p>
                </div>
            </div>
        </div>
        """)
        
        html.append('<div class="content">')
        
        # Skill extraction summary with icons
        vet_skills = []
        for unit in vet_qual.units:
            vet_skills.extend(unit.extracted_skills)
        
        uni_skills = []
        for course in uni_qual.courses:
            uni_skills.extend(course.extracted_skills)
        
        html.append("<h2><i class='fas fa-chart-bar'></i> Skill Extraction Summary</h2>")
        html.append("<div class='stats-grid'>")
        
        html.append("<div class='stat-card'>")
        html.append("<i class='fas fa-tools' style='font-size: 2rem; color: #667eea; margin-bottom: 15px;'></i>")
        html.append(f"<div class='stat-value'>{len(vet_skills)}</div>")
        html.append("<div class='stat-label'>VET Skills</div>")
        html.append("</div>")
        
        html.append("<div class='stat-card'>")
        html.append("<i class='fas fa-book' style='font-size: 2rem; color: #764ba2; margin-bottom: 15px;'></i>")
        html.append(f"<div class='stat-value'>{len(uni_skills)}</div>")
        html.append("<div class='stat-label'>University Skills</div>")
        html.append("</div>")
        
        common_count = len(set(s.name.lower() for s in vet_skills).intersection(
            set(s.name.lower() for s in uni_skills)))
        
        html.append("<div class='stat-card'>")
        html.append("<i class='fas fa-link' style='font-size: 2rem; color: #48bb78; margin-bottom: 15px;'></i>")
        html.append(f"<div class='stat-value'>{common_count}</div>")
        html.append("<div class='stat-label'>Common Skills</div>")
        html.append("</div>")
        
        html.append("</div>")
        
        # Executive Summary with enhanced progress bars
        summary = self._generate_summary_stats(recommendations)
        html.append("<div class='summary-box'>")
        html.append("<h2><i class='fas fa-clipboard-list'></i> Executive Summary</h2>")
        html.append(f"<p style='font-size: 1.1rem; margin-bottom: 20px;'><strong>Total Recommendations:</strong> {summary['total']}</p>")
        html.append(f"<p style='font-size: 1.1rem; margin-bottom: 30px;'><strong>Average Alignment Score:</strong> {summary['avg_alignment']:.1%}</p>")
        
        html.append("<h3>Recommendation Distribution</h3>")
        for rec_type, count, percent, icon, color in [
            ('Full Credit', summary['full_count'], summary['full_percent'], 'fa-check-circle', '#48bb78'),
            ('Conditional', summary['conditional_count'], summary['conditional_percent'], 'fa-exclamation-circle', '#ed8936'),
            ('Partial', summary['partial_count'], summary['partial_percent'], 'fa-times-circle', '#f56565')
        ]:
            html.append(f"<div class='progress-container'>")
            html.append(f"<div class='progress-label'>")
            html.append(f"<span><i class='fas {icon}' style='color: {color};'></i> {rec_type}</span>")
            html.append(f"<span><strong>{count}</strong> ({percent:.1%})</span>")
            html.append(f"</div>")
            html.append(f"<div class='progress-bar'><div class='progress-fill' data-width='{percent*100}%' style='width: 0;'></div></div>")
            html.append(f"</div>")
        
        html.append("</div>")
        
        # Search and Filter Bar
        html.append("<h2><i class='fas fa-search'></i> Credit Transfer Recommendations</h2>")
        html.append("<div class='search-container'>")
        html.append("<div class='search-box'>")
        html.append("<input type='text' id='searchInput' placeholder='Search recommendations...' />")
        html.append("<i class='fas fa-search'></i>")
        html.append("</div>")
        html.append("<button class='filter-btn' data-filter='full'><i class='fas fa-check-circle'></i> Full Only</button>")
        html.append("<button class='filter-btn' data-filter='conditional'><i class='fas fa-exclamation-circle'></i> Conditional Only</button>")
        html.append("<button class='filter-btn' data-filter='partial'><i class='fas fa-times-circle'></i> Partial Only</button>")
        html.append("</div>")
        
        # Enhanced recommendations table
        html.append("<table>")
        html.append("<thead><tr>")
        html.append("<th>Action</th>")
        html.append("<th>VET Units</th>")
        html.append("<th>Uni Course</th>")
        html.append("<th>Study Level</th>")
        html.append("<th>Skills</th>")
        html.append("<th>Alignment</th>")
        html.append("<th>Confidence</th>")
        html.append("<th>Type</th>")
        html.append("<th>Conditions</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        
        for idx, rec in enumerate(recommendations[:50], 1):  # Limit to top 50
            rec_class = rec.recommendation.value
            
            # Count skill matches
            vet_skill_count = sum(len(unit.extracted_skills) for unit in rec.vet_units)
            uni_skill_count = len(rec.uni_course.extracted_skills)
            
            # Determine group class for alternating background
            group_class = 'rec-group-even' if idx % 2 == 0 else 'rec-group-odd'
            
            # Create rows for each VET unit
            vet_units = rec.vet_units
            for unit_idx, vet_unit in enumerate(vet_units):
                # Determine if this is the last row of this recommendation group
                is_last_row = (unit_idx == len(vet_units) - 1)
                row_classes = f"{rec_class} {group_class}"
                if is_last_row:
                    row_classes += " rec-group-last"
                
                html.append(f"<tr class='{row_classes}' data-rec-group='rec-{idx}'>")
                
                # First column: Show button only on first row
                if unit_idx == 0:
                    html.append(f"<td rowspan='{len(vet_units)}'><button class='expand-btn' onclick='toggleExpand(this, {idx})'><i class='fas fa-chevron-down'></i> Show Skills</button></td>")
                
                # Second column: VET unit code and name (one per row)
                html.append(f"<td>{vet_unit.code}: {vet_unit.name}</td>")
                
                # Remaining columns: span across all VET unit rows (only on first row)
                if unit_idx == 0:
                    html.append(f"<td rowspan='{len(vet_units)}'>{rec.uni_course.code}: {rec.uni_course.name}</td>")
                    html.append(f"<td rowspan='{len(vet_units)}'><span class='skill-level-badge'>{rec.uni_course.study_level.title()}</span></td>")
                    html.append(f"<td rowspan='{len(vet_units)}'>{vet_skill_count} → {uni_skill_count}</td>")
                    
                    # Alignment with tooltip
                    html.append(f"<td rowspan='{len(vet_units)}'>")
                    html.append(f"<div class='tooltip'>{rec.alignment_score:.1%}")
                    html.append(f"<span class='tooltiptext'>Based on skill coverage, quality, and level alignment</span>")
                    html.append(f"</div>")
                    html.append(f"</td>")
                    
                    html.append(f"<td rowspan='{len(vet_units)}'>{rec.confidence:.1%}</td>")
                    
                    # Type with icon
                    type_icons = {'full': 'fa-check-circle', 'conditional': 'fa-exclamation-circle', 'partial': 'fa-times-circle', 'none': 'fa-ban'}
                    type_colors = {'full': '#48bb78', 'conditional': '#ed8936', 'partial': '#f56565', 'none': '#718096'}
                    icon = type_icons.get(rec.recommendation.value, 'fa-question')
                    color = type_colors.get(rec.recommendation.value, '#718096')
                    html.append(f"<td rowspan='{len(vet_units)}'><i class='fas {icon}' style='color: {color}; margin-right: 5px;'></i>{rec.recommendation.value.upper()}</td>")
                    
                    html.append(f"<td rowspan='{len(vet_units)}'>{'; '.join(rec.conditions[:2]) if rec.conditions else 'None'}</td>")
                
                html.append("</tr>")
            
            # Expandable row with enhanced skill mappings
            html.append(f"<tr class='{group_class}' data-rec-group='rec-{idx}'>")
            html.append(f"<td colspan='9' class='expandable-content' id='expand-{idx}'>")
            
            # Get skill mappings for this specific recommendation
            skill_mappings = self._extract_skill_mappings_for_single_rec(rec)
            
            if skill_mappings:
                # Group mappings by type
                direct_mappings = [m for m in skill_mappings if m['mapping_type'] == 'Direct']
                partial_mappings = [m for m in skill_mappings if m['mapping_type'] == 'Partial']
                unmapped_mappings = [m for m in skill_mappings if m['mapping_type'] == 'Unmapped']
                
                # Enhanced summary with stats
                html.append(f"<div class='mapping-summary'>")
                html.append(f"<div class='mapping-stat'>")
                html.append(f"<div class='mapping-stat-value'>{len(direct_mappings)}</div>")
                html.append(f"<div class='mapping-stat-label'>Direct Matches</div>")
                html.append(f"</div>")
                html.append(f"<div class='mapping-stat'>")
                html.append(f"<div class='mapping-stat-value'>{len(partial_mappings)}</div>")
                html.append(f"<div class='mapping-stat-label'>Partial Matches</div>")
                html.append(f"</div>")
                html.append(f"<div class='mapping-stat'>")
                html.append(f"<div class='mapping-stat-value'>{len(unmapped_mappings)}</div>")
                html.append(f"<div class='mapping-stat-label'>Unmapped Skills</div>")
                html.append(f"</div>")
                html.append(f"</div>")
                
                # Create skill mapping table
                html.append("<table class='skill-mapping-inner-table'>")
                html.append("<thead><tr>")
                html.append("<th>VET Unit</th>")
                html.append("<th>VET Skill</th>")
                html.append("<th>Uni Course</th>")
                html.append("<th>Uni Skill</th>")
                html.append("<th>Type</th>")
                html.append("<th>Match %</th>")
                html.append("<th>Analysis</th>")
                html.append("</tr></thead>")
                html.append("<tbody>")
                
                # Display mappings
                for mapping in direct_mappings[:10]:
                    html.append(f"<tr class='mapping-direct'>")
                    html.append(f"<td>{mapping['vet_unit']}</td>")
                    html.append(f"<td>{mapping['vet_skill']}")
                    html.append(f"<span class='skill-level-badge'>L{mapping['vet_level']}</span>")
                    if 'vet_context' in mapping:
                        html.append(f"<span class='skill-context-badge {mapping['vet_context']}'>{mapping['vet_context'].title()}</span>")
                    html.append(f"</td>")
                    html.append(f"<td>{mapping['uni_course']}</td>")
                    html.append(f"<td>{mapping['uni_skill']}")
                    html.append(f"<span class='skill-level-badge'>L{mapping['uni_level']}</span>")
                    if 'uni_context' in mapping:
                        html.append(f"<span class='skill-context-badge {mapping['uni_context']}'>{mapping['uni_context'].title()}</span>")
                    html.append(f"</td>")
                    html.append(f"<td><i class='fas fa-check-circle'></i> {mapping['mapping_type']}</td>")
                    html.append(f"<td>{mapping['similarity']:.0%}</td>")
                    html.append(f"<td>{mapping['reasoning']}</td>")
                    html.append("</tr>")
                
                for mapping in partial_mappings[:8]:
                    html.append(f"<tr class='mapping-partial'>")
                    html.append(f"<td>{mapping['vet_unit']}</td>")
                    html.append(f"<td>{mapping['vet_skill']}")
                    html.append(f"<span class='skill-level-badge'>L{mapping['vet_level']}</span>")
                    if 'vet_context' in mapping:
                        html.append(f"<span class='skill-context-badge {mapping['vet_context']}'>{mapping['vet_context'].title()}</span>")
                    html.append(f"</td>")
                    html.append(f"<td>{mapping['uni_course']}</td>")
                    html.append(f"<td>{mapping['uni_skill']}")
                    html.append(f"<span class='skill-level-badge'>L{mapping['uni_level']}</span>")
                    if 'uni_context' in mapping:
                        html.append(f"<span class='skill-context-badge {mapping['uni_context']}'>{mapping['uni_context'].title()}</span>")
                    html.append(f"</td>")
                    html.append(f"<td><i class='fas fa-exclamation-circle'></i> {mapping['mapping_type']}</td>")
                    html.append(f"<td>{mapping['similarity']:.0%}</td>")
                    html.append(f"<td>{mapping['reasoning']}</td>")
                    html.append("</tr>")
                
                for mapping in unmapped_mappings[:7]:
                    html.append(f"<tr class='mapping-unmapped'>")
                    html.append(f"<td>{mapping['vet_unit']}</td>")
                    html.append(f"<td>{mapping.get('vet_skill', '-')}</td>")
                    html.append(f"<td>{mapping['uni_course']}</td>")
                    html.append(f"<td>{mapping.get('uni_skill', '-')}</td>")
                    html.append(f"<td><i class='fas fa-times-circle'></i> {mapping['mapping_type']}</td>")
                    html.append(f"<td>-</td>")
                    html.append(f"<td>{mapping['reasoning']}</td>")
                    html.append("</tr>")
                
                # Add note if more mappings exist
                total_mappings = len(skill_mappings)
                shown_mappings = min(25, len(direct_mappings) + len(partial_mappings) + len(unmapped_mappings))
                if total_mappings > shown_mappings:
                    html.append(f"<tr><td colspan='7' style='text-align:center; font-style:italic; color: #718096;'>")
                    html.append(f"<i class='fas fa-ellipsis-h'></i> {total_mappings - shown_mappings} more mappings not shown")
                    html.append(f"</td></tr>")
                
                html.append("</tbody></table>")
            else:
                html.append("<p style='text-align:center; color: #718096;'><i class='fas fa-info-circle'></i> No skill mapping data available.</p>")
            
            html.append("</td>")
            html.append("</tr>")
        
        html.append("</tbody></table>")
        
        # Top Skills Section with enhanced badges
        html.append("<h2><i class='fas fa-star'></i> Top Extracted Skills</h2>")
        
        html.append("<h3>VET Skills (Top 20)</h3>")
        html.append("<div style='padding: 20px;'>")
        vet_skill_names = [s.name for s in sorted(vet_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in vet_skill_names[:20]:
            html.append(f"<span class='skill-badge'><i class='fas fa-tools' style='font-size: 0.8rem; margin-right: 4px;'></i>{skill_name}</span>")
        html.append("</div>")
        
        html.append("<h3>University Skills (Top 20)</h3>")
        html.append("<div style='padding: 20px;'>")
        uni_skill_names = [s.name for s in sorted(uni_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in uni_skill_names[:20]:
            html.append(f"<span class='skill-badge'><i class='fas fa-book' style='font-size: 0.8rem; margin-right: 4px;'></i>{skill_name}</span>")
        html.append("</div>")
        
        # Gap Analysis
        gaps = self._analyze_gaps(recommendations)
        if gaps['common_gaps']:
            html.append("<h2><i class='fas fa-exclamation-triangle'></i> Common Skill Gaps</h2>")
            html.append("<div class='summary-box'>")
            html.append("<ul style='columns: 2; column-gap: 40px;'>")
            for skill, count in gaps['common_gaps'][:10]:
                html.append(f"<li style='margin: 10px 0;'><strong>{skill}</strong> <span style='color: #718096;'>({count} occurrences)</span></li>")
            html.append("</ul>")
            html.append("</div>")
        
        html.append("</div>") # Close content div
        html.append("</div>") # Close container div
        
        # Back to top button
        html.append("""
        <button id="backToTop" class="back-to-top" onclick="scrollToTop()">
            <i class="fas fa-arrow-up"></i>
        </button>
        """)
        
        # Footer
        html.append("""
        </body>
        </html>
        """)
        
        return "\n".join(html)
        
        # Top Skills Section with enhanced badges
        html.append("<h2><i class='fas fa-star'></i> Top Extracted Skills</h2>")
        
        html.append("<h3>VET Skills (Top 20)</h3>")
        html.append("<div style='padding: 20px;'>")
        vet_skill_names = [s.name for s in sorted(vet_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in vet_skill_names[:20]:
            html.append(f"<span class='skill-badge'><i class='fas fa-tools' style='font-size: 0.8rem; margin-right: 4px;'></i>{skill_name}</span>")
        html.append("</div>")
        
        html.append("<h3>University Skills (Top 20)</h3>")
        html.append("<div style='padding: 20px;'>")
        uni_skill_names = [s.name for s in sorted(uni_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in uni_skill_names[:20]:
            html.append(f"<span class='skill-badge'><i class='fas fa-book' style='font-size: 0.8rem; margin-right: 4px;'></i>{skill_name}</span>")
        html.append("</div>")
        
        # Gap Analysis
        gaps = self._analyze_gaps(recommendations)
        if gaps['common_gaps']:
            html.append("<h2><i class='fas fa-exclamation-triangle'></i> Common Skill Gaps</h2>")
            html.append("<div class='summary-box'>")
            html.append("<ul style='columns: 2; column-gap: 40px;'>")
            for skill, count in gaps['common_gaps'][:10]:
                html.append(f"<li style='margin: 10px 0;'><strong>{skill}</strong> <span style='color: #718096;'>({count} occurrences)</span></li>")
            html.append("</ul>")
            html.append("</div>")
        
        html.append("</div>") # Close content div
        html.append("</div>") # Close container div
        
        # Back to top button
        html.append("""
        <button id="backToTop" class="back-to-top" onclick="scrollToTop()">
            <i class="fas fa-arrow-up"></i>
        </button>
        """)
        
        # Footer
        html.append("""
        </body>
        </html>
        """)
        
        return "\n".join(html)
        
    def _generate_summary_stats(self, recommendations: List[CreditTransferRecommendation]) -> Dict:
        """Generate summary statistics"""
        total = len(recommendations)
        
        if total == 0:
            return {
                'total': 0,
                'full_count': 0,
                'full_percent': 0,
                'conditional_count': 0,
                'conditional_percent': 0,
                'partial_count': 0,
                'partial_percent': 0,
                'avg_alignment': 0,
                'avg_confidence': 0
            }
        
        full_count = sum(1 for r in recommendations if r.recommendation == RecommendationType.FULL)
        conditional_count = sum(1 for r in recommendations if r.recommendation == RecommendationType.CONDITIONAL)
        partial_count = sum(1 for r in recommendations if r.recommendation == RecommendationType.PARTIAL)
        
        return {
            'total': total,
            'full_count': full_count,
            'full_percent': full_count / total,
            'conditional_count': conditional_count,
            'conditional_percent': conditional_count / total,
            'partial_count': partial_count,
            'partial_percent': partial_count / total,
            'avg_alignment': sum(r.alignment_score for r in recommendations) / total,
            'avg_confidence': sum(r.confidence for r in recommendations) / total
        }
    
    def _analyze_course_coverage(self, 
                                 recommendations: List[CreditTransferRecommendation],
                                 uni_qual: UniQualification) -> Dict:
        """Analyze which courses have credit transfer options"""
        covered_courses = set(r.uni_course.code for r in recommendations)
        total_courses = len(uni_qual.courses)
        
        # Analyze by study level
        by_level = {}
        all_levels = uni_qual.get_all_study_levels()
        
        for level in all_levels:
            level_courses = uni_qual.get_courses_by_level(level)
            if level_courses:
                level_covered = sum(1 for c in level_courses if c.code in covered_courses)
                by_level[level] = {
                    'total': len(level_courses),
                    'covered': level_covered,
                    'rate': level_covered / len(level_courses)
                }
        
        return {
            'courses_covered': len(covered_courses),
            'total_courses': total_courses,
            'coverage_rate': len(covered_courses) / total_courses if total_courses > 0 else 0,
            'by_level': by_level
        }
        
    def _generate_transfer_reasoning(self, rec: CreditTransferRecommendation, match_info: Dict) -> str:
        """Generate human-readable reasoning for transfer decision"""
        
        reasoning = []
        
        # Check match quality
        if match_info['direct_matches'] > match_info['partial_matches']:
            reasoning.append("High-quality direct matches")
        elif match_info['partial_matches'] > match_info['direct_matches']:
            reasoning.append("Mostly partial matches")
        
        # Check coverage
        coverage_ratio = (match_info['direct_matches'] + match_info['partial_matches'] * 0.5) / max(match_info['total_uni_skills'], 1)
        if coverage_ratio >= 0.9:
            reasoning.append("Excellent skill coverage")
        elif coverage_ratio >= 0.7:
            reasoning.append("Good skill coverage")
        else:
            reasoning.append("Limited coverage")
        
        # Check for critical gaps
        if match_info['unmapped_critical'] == 0:
            reasoning.append("All critical skills covered")
        elif match_info['unmapped_critical'] <= 3:
            reasoning.append(f"{match_info['unmapped_critical']} minor gaps")
        else:
            reasoning.append(f"{match_info['unmapped_critical']} significant gaps")
        
        # Edge cases
        if match_info['edge_cases']:
            if 'context_imbalance' in match_info['edge_cases']:
                reasoning.append("Context adjustment needed")
            if 'outdated_content' in match_info['edge_cases']:
                reasoning.append("Content update required")
        
        # Transfer type reasoning
        if rec.recommendation == RecommendationType.FULL:
            reasoning.append("→ Complete requirements met")
        elif rec.recommendation == RecommendationType.CONDITIONAL:
            reasoning.append("→ Conditions must be met")
        else:
            reasoning.append("→ Supplementary study needed")
        
        return "<br>".join(reasoning[:4])  # Limit to 4 key points
            
    def _extract_detailed_match_info(self, rec: CreditTransferRecommendation) -> Dict:
        """Extract detailed matching information from backend calculations"""
        
        # All match info should be in metadata from backend
        match_stats = rec.metadata.get('match_statistics', {})
        score_breakdown = rec.metadata.get('score_breakdown', {})
        penalties = rec.metadata.get('penalties', {})
        
        # Extract edge cases from edge_case_results
        edge_case_summary = {}
        if rec.edge_case_results:
            for case_type, case_data in rec.edge_case_results.items():
                if isinstance(case_data, dict) and case_data.get('applicable'):
                    edge_case_summary[case_type] = {
                        'impact': penalties.get(case_type, 0),
                        'recommendation': case_data.get('recommendation', ''),
                        'requirements': case_data.get('bridging_requirements', [])
                    }
        
        # Calculate score components if not provided
        if not score_breakdown:
            from mapping.unified_scorer import UnifiedScorer
            scorer = UnifiedScorer()
            coverage = match_stats.get('uni_coverage', 0)
            score_components = {
                'coverage': coverage * scorer.WEIGHTS['skill_coverage'],
                'quality': rec.skill_coverage.get('quality', 0) * scorer.WEIGHTS['skill_quality'],
                'level': rec.skill_coverage.get('level', 0) * scorer.WEIGHTS['level_alignment'],
                'context': rec.skill_coverage.get('context', 0) * scorer.WEIGHTS['context_alignment'],
                'confidence': rec.confidence * scorer.WEIGHTS['confidence'],
                'edge_penalty': sum(penalties.values()) if penalties else 0
            }
        else:
            score_components = {
                'coverage': score_breakdown.get('coverage_weighted', 0),
                'quality': score_breakdown.get('quality_weighted', 0),
                'level': score_breakdown.get('level_weighted', 0),
                'context': score_breakdown.get('context_weighted', 0),
                'confidence': score_breakdown.get('confidence_weighted', 0),
                'edge_penalty': score_breakdown.get('total_penalty', 0)
            }
        
        # Format alignment calculation string
        base_score = sum(score_components.values()) - score_components['edge_penalty']
        matching_strategy = rec.metadata.get('matching_strategy', 'clustering')
        strategy_label = f" [{matching_strategy.title()} Matching]"
        
        if match_stats.get('hybrid_mode'):
            strategy_label += " with clustering supplement"
        
        alignment_calculation = (
            f"({score_components['coverage']:.2f} + {score_components['quality']:.2f} + "
            f"{score_components['level']:.2f} + {score_components['context']:.2f} + "
            f"{score_components['confidence']:.2f}) * (1 - {score_components['edge_penalty']:.2f}) = "
            f"{rec.alignment_score:.2%}{strategy_label}"
        )
        
        # Use backend-calculated values directly
        return {
            'direct_matches': match_stats.get('direct_matches', 0),
            'partial_matches': match_stats.get('partial_matches', 0),
            'unmapped_critical': match_stats.get('unmapped_count', 0),
            'total_uni_skills': len(rec.uni_course.extracted_skills) if hasattr(rec.uni_course, 'extracted_skills') else 0,
            'quality_breakdown': rec.skill_coverage,
            'score_components': score_components,
            'edge_cases': edge_case_summary,
            'alignment_calculation': alignment_calculation,
            'level_analysis': self._analyze_level_alignment(rec),
            'matching_strategy': matching_strategy
        }
        
    def _extract_skill_mappings_for_single_rec(self, rec: CreditTransferRecommendation) -> List[Dict]:
        """Extract skill mappings for a single recommendation"""
        
        from mapping.simple_mapping_types import SimpleMappingClassifier
        classifier = SimpleMappingClassifier()
        
        # Get matching strategy from metadata
        matching_strategy = rec.metadata.get('matching_strategy', 'clustering')
        
        if matching_strategy in ['direct', 'direct_one_vs_all', 'hybrid']:
            return self._extract_direct_skill_mappings(rec, classifier)
        else:
            return self._extract_cluster_skill_mappings(rec, classifier)
        
    def _extract_direct_match_info(self, rec: CreditTransferRecommendation) -> Dict:
        """Extract match info for direct/hybrid matching strategies"""
        
        # Get match statistics from metadata
        match_stats = rec.metadata.get('match_statistics', {})
        score_breakdown = rec.metadata.get('score_breakdown', {})
        penalties = rec.metadata.get('penalties', {})
        
        # Direct match counts
        direct_matches = match_stats.get('direct_matches', 0)
        partial_matches = match_stats.get('partial_matches', 0)
        total_uni_skills = len(rec.uni_course.extracted_skills) if hasattr(rec.uni_course, 'extracted_skills') else 0
        unmapped_critical = total_uni_skills - direct_matches - partial_matches
        
        # Handle hybrid mode
        is_hybrid = match_stats.get('hybrid_mode', False)
        if is_hybrid and 'cluster_supplement' in match_stats:
            cluster_stats = match_stats['cluster_supplement']
            # Add cluster matches to counts
            partial_matches += cluster_stats.get('total_matches', 0)
            unmapped_critical = max(0, unmapped_critical - cluster_stats.get('total_matches', 0))
        
        # Get level alignment analysis
        level_analysis = self._analyze_level_alignment(rec)
        
        # Get score components
        if score_breakdown:
            score_components = {
                'coverage': score_breakdown.get('coverage_weighted', 0),
                'quality': score_breakdown.get('quality_weighted', 0),
                'level': score_breakdown.get('level_weighted', 0),
                'context': score_breakdown.get('context_weighted', 0),
                'confidence': score_breakdown.get('confidence_weighted', 0),
                'edge_penalty': score_breakdown.get('total_penalty', 0)
            }
        else:
            # Calculate based on match statistics
            coverage = (direct_matches + partial_matches * 0.5) / max(total_uni_skills, 1)
            score_components = {
                'coverage': coverage * 0.4,
                'quality': rec.skill_coverage.get('quality', 0) * 0.25,
                'level': rec.skill_coverage.get('level', 0) * 0.2,
                'context': rec.skill_coverage.get('context', 0) * 0.1,
                'confidence': rec.confidence * 0.05,
                'edge_penalty': sum(penalties.values()) if penalties else 0
            }
        
        # Build edge case summary
        edge_case_summary = {}
        if rec.edge_case_results:
            for case_type, case_data in rec.edge_case_results.items():
                if isinstance(case_data, dict) and case_data.get('applicable'):
                    edge_case_summary[case_type] = {
                        'impact': penalties.get(case_type, 0),
                        'recommendation': case_data.get('recommendation', ''),
                        'requirements': case_data.get('bridging_requirements', [])
                    }
        
        # Calculate alignment formula string
        base_score = sum(score_components.values()) - score_components['edge_penalty']
        alignment_calculation = (
            f"({score_components['coverage']:.2f} + {score_components['quality']:.2f} + "
            f"{score_components['level']:.2f} + {score_components['context']:.2f} + "
            f"{score_components['confidence']:.2f}) * (1 - {score_components['edge_penalty']:.2f}) = "
            f"{rec.alignment_score:.2%}"
        )
        
        # Add strategy-specific info
        strategy_info = f" [{rec.metadata.get('matching_strategy', 'unknown').title()} Matching]"
        if is_hybrid:
            strategy_info += " with clustering supplement"
        
        return {
            'direct_matches': direct_matches,
            'partial_matches': partial_matches,
            'unmapped_critical': unmapped_critical,
            'total_uni_skills': total_uni_skills,
            'quality_breakdown': rec.skill_coverage,
            'score_components': score_components,
            'edge_cases': edge_case_summary,
            'alignment_calculation': alignment_calculation + strategy_info,
            'level_analysis': level_analysis,
            'matching_strategy': rec.metadata.get('matching_strategy', 'clustering')
        }
        
    def _analyze_level_alignment(self, rec: CreditTransferRecommendation) -> Dict:
        """Analyze skill level alignment between VET and University"""
        
        # Get average levels
        vet_levels = []
        for unit in rec.vet_units:
            vet_levels.extend([s.level.value for s in unit.extracted_skills])
        
        uni_levels = [s.level.value for s in rec.uni_course.extracted_skills]
        
        if not vet_levels or not uni_levels:
            return {
                "status": "unknown",
                "message": "Insufficient data"
            }
        
        avg_vet = np.mean(vet_levels)
        avg_uni = np.mean(uni_levels)
        level_gap = avg_uni - avg_vet
        
        # Determine status
        if level_gap <= 0:
            status = "exceeds"
            message = f"VET skills exceed requirement by {abs(level_gap):.1f} levels"
            color = "green"
        elif level_gap <= 1:
            status = "adequate"
            message = f"Minor gap of {level_gap:.1f} levels - bridgeable"
            color = "yellow"
        else:
            status = "insufficient"
            message = f"Significant gap of {level_gap:.1f} levels - substantial bridging required"
            color = "red"
        
        return {
            "avg_vet_level": avg_vet,
            "avg_uni_level": avg_uni,
            "level_gap": level_gap,
            "status": status,
            "message": message,
            "color": color,
            "vet_level_distribution": {
                "Novice": sum(1 for l in vet_levels if l == 1),
                "Beginner": sum(1 for l in vet_levels if l == 2),
                "Competent": sum(1 for l in vet_levels if l == 3),
                "Proficient": sum(1 for l in vet_levels if l == 4),
                "Expert": sum(1 for l in vet_levels if l == 5)
            },
            "uni_level_distribution": {
                "Novice": sum(1 for l in uni_levels if l == 1),
                "Beginner": sum(1 for l in uni_levels if l == 2),
                "Competent": sum(1 for l in uni_levels if l == 3),
                "Proficient": sum(1 for l in uni_levels if l == 4),
                "Expert": sum(1 for l in uni_levels if l == 5)
            }
        }
        
    def _analyze_gaps(self, recommendations: List[CreditTransferRecommendation]) -> Dict:
        """Analyze common gaps and conditions"""
        from collections import Counter
        
        all_gaps = []
        all_conditions = []
        
        for rec in recommendations:
            all_gaps.extend([gap.name for gap in rec.gaps])
            all_conditions.extend(rec.conditions)
        
        gap_counts = Counter(all_gaps)
        condition_counts = Counter(all_conditions)
        
        return {
            'common_gaps': gap_counts.most_common(20),
            'common_conditions': condition_counts.most_common(20),
            'total_unique_gaps': len(set(all_gaps)),
            'total_unique_conditions': len(set(all_conditions))
        }

    def _categorize_skills_by_source(self, skills: List) -> Dict[str, List]:
        """Categorize skills by their extraction source"""
        categorized = {
            'explicit': [],
            'implicit': [],
            'decomposed': [],
            'prerequisite': [],
            'fallback': []
        }
        
        for skill in skills:
            if hasattr(skill, 'source'):
                if 'implicit' in skill.source.lower():
                    categorized['implicit'].append(skill)
                elif 'decomposed' in skill.source.lower():
                    categorized['decomposed'].append(skill)
                elif 'prerequisite' in skill.source.lower():
                    categorized['prerequisite'].append(skill)
                elif 'fallback' in skill.source.lower():
                    categorized['fallback'].append(skill)
                else:
                    categorized['explicit'].append(skill)
            else:
                categorized['explicit'].append(skill)
        
        return categorized

    def _get_confidence_class(self, confidence: float) -> str:
        """Get CSS class based on confidence level"""
        if confidence >= 0.8:
            return 'confidence-high'
        elif confidence >= 0.6:
            return 'confidence-medium'
        else:
            return 'confidence-low'
    
    def _get_mapping_color(self, mapping_type: str) -> str:
        """Get color for mapping type"""
        colors = {
            'Direct': '#d4edda',     # Green
            'Partial': '#fff3cd',    # Yellow
            'Unmapped': '#f8d7da'    # Red
        }
        return colors.get(mapping_type, '#ffffff')
    
    def _extract_skill_mappings(self, recommendations: List[CreditTransferRecommendation]) -> List[Dict]:
        """Extract skill mappings for all matching strategies (clustering, direct, hybrid)"""
        
        from mapping.simple_mapping_types import SimpleMappingClassifier
        classifier = SimpleMappingClassifier()
        
        all_mappings = []
        
        for rec in recommendations:
            # Get matching strategy from metadata
            matching_strategy = rec.metadata.get('matching_strategy', 'clustering')
            
            if matching_strategy in ['direct', 'direct_one_vs_all', 'hybrid']:
                # Handle direct and hybrid matching
                all_mappings.extend(self._extract_direct_skill_mappings(rec, classifier))
            else:
                # Original clustering logic
                all_mappings.extend(self._extract_cluster_skill_mappings(rec, classifier))
        
        return all_mappings

    def _extract_direct_skill_mappings(self, rec: CreditTransferRecommendation, classifier) -> List[Dict]:
        """Extract skill mappings from backend-calculated matches"""
        mappings = []
        matching_strategy = rec.metadata.get('matching_strategy', 'clustering')
        # Get pre-calculated skill matches from metadata
        skill_match_details = rec.metadata.get('skill_match_details', [])
        
        if skill_match_details:
            # Use backend-calculated matches
            for detail in skill_match_details['mapped']:
                # Both skills present - normal match
                mapping = {
                    'vet_unit': detail['vet_skill'].code,
                    'vet_skill': detail['vet_skill'].name,
                    'vet_level': detail['vet_skill'].level.value,
                    'vet_context': detail['vet_skill'].context.value,  # Add context
                    'uni_course': detail['uni_skill'].code,
                    'uni_skill': detail['uni_skill'].name,
                    'uni_level': detail['uni_skill'].level.value,
                    'uni_context': detail['uni_skill'].context.value,  # Add context
                    'mapping_type': detail['match_type'],
                    'similarity': detail['similarity'],
                    'reasoning': detail['reasoning']
                }
                mappings.append(mapping)
                
            for unmapped in skill_match_details['unmapped_uni']:
                # Only Uni skill - unmapped Uni
                mapping = {
                    'vet_unit': '-',
                    'vet_skill': '-',
                    'vet_level': '-',
                    'vet_context': '-',
                    'uni_course': unmapped.code,
                    'uni_skill': unmapped.name,
                    'uni_level': unmapped.level.value,
                    'uni_context': unmapped.context.value,  # Add context
                    'mapping_type': 'Unmapped',
                    'similarity': 0,
                    'reasoning': '-'
                }               
                mappings.append(mapping)
                
            if matching_strategy != 'direct_one_vs_all':
                for unmapped in skill_match_details['unmapped_vet']:
                    # Only VET skill - unmapped VET
                    mapping = {
                        'vet_unit': unmapped.code,
                        'vet_skill': unmapped.name,
                        'vet_level': unmapped.level.value,
                        'vet_context': unmapped.context.value,  # Add context
                        'uni_course': '-',
                        'uni_skill': '-',
                        'uni_level': '-',
                        'uni_context': '-',
                        'mapping_type': 'Unmapped',
                        'similarity': 0,
                        'reasoning': '-'
                    }
                    mappings.append(mapping)
        else:
            # Fallback if no pre-calculated matches (shouldn't happen)
            logger.warning(f"No skill match details found for recommendation {rec.id}")
        
        return mappings

    def _get_skill_level(self, rec: CreditTransferRecommendation, skill_name: str, source: str) -> int:
        """Helper to get skill level by name"""
        if source == 'vet':
            for unit in rec.vet_units:
                for skill in unit.extracted_skills:
                    if skill.name == skill_name:
                        return skill.level.value
        else:  # uni
            for skill in rec.uni_course.extracted_skills:
                if skill.name == skill_name:
                    return skill.level.value
        return 0

    def _extract_cluster_skill_mappings(self, rec: CreditTransferRecommendation, classifier) -> List[Dict]:
        """Extract skill mappings for clustering strategy (original logic)"""
        mappings = []
        
        # Create mapping tracking sets
        vet_skill_mapping = {}
        uni_skill_mapping = {}
        
        # Original clustering logic from your existing code
        semantic_clusters = rec.metadata.get('semantic_clusters', [])
        
        for cluster in semantic_clusters:
            # Get average similarity
            avg_similarity = cluster.get('avg_semantic_similarity', 0)
            
            # Get skills
            vet_skills = [item['skill'] for item in cluster.get('vet_skills', [])]
            uni_skills = [item['skill'] for item in cluster.get('uni_skills', [])]
            
            if not vet_skills or not uni_skills:
                continue
            
            # Calculate simple metrics
            avg_vet_level = np.mean([s.level.value for s in vet_skills])
            avg_uni_level = np.mean([s.level.value for s in uni_skills])
            level_gap = abs(int(avg_uni_level - avg_vet_level))
            
            # Simple context check
            vet_contexts = [s.context.value for s in vet_skills]
            uni_contexts = [s.context.value for s in uni_skills]
            context_match = (vet_contexts[0] == uni_contexts[0]) if vet_contexts and uni_contexts else False
            
            # Classify
            mapping_type, reason = classifier.classify_mapping(
                avg_similarity, level_gap, context_match
            )
            
            # Create mapping entries
            for vet_skill in vet_skills:
                for uni_skill in uni_skills:
                    mapping = {
                        'vet_unit': rec.get_vet_unit_codes()[0] if rec.vet_units else 'Unknown',
                        'vet_skill': vet_skill.name,
                        'vet_level': vet_skill.level.value,
                        'vet_context': vet_skill.context.value,  # Add context
                        'uni_course': rec.uni_course.code,
                        'uni_skill': uni_skill.name,
                        'uni_level': uni_skill.level.value,
                        'uni_context': uni_skill.context.value,  # Add context
                        'mapping_type': mapping_type,
                        'similarity': avg_similarity,
                        'reasoning': reason + " [Cluster match]"
                    }
                    mappings.append(mapping)
                    vet_skill_mapping[vet_skill.name] = mapping_type
                    uni_skill_mapping[uni_skill.name] = mapping_type
        
        # Add unmapped skills (original logic)
        for unit in rec.vet_units:
            for skill in unit.extracted_skills:
                if skill.name not in vet_skill_mapping:
                    mapping = {
                        'vet_unit': unit.code,
                        'uni_course': rec.uni_course.code,
                        'vet_skill': skill.name,
                        'vet_level': skill.level.value,
                        'vet_context': skill.context.value,  # Add context
                        'uni_skill': '-',
                        'uni_level': '-',
                        'uni_context': '-',
                        'mapping_type': 'Unmapped',
                        'similarity': 0,
                        'reasoning': 'No matching university skill found [Cluster mode]'
                    }
                    mappings.append(mapping)
        
        for skill in rec.uni_course.extracted_skills:
            if skill.name not in uni_skill_mapping:
                mapping = {
                    'vet_unit': '-',
                    'uni_course': rec.uni_course.code,
                    'vet_skill': '-',
                    'vet_level': '-',
                    'vet_context': '-',
                    'uni_skill': skill.name,
                    'uni_level': skill.level.value,
                    'uni_context': skill.context.value,  # Add context
                    'mapping_type': 'Unmapped',
                    'similarity': 0,
                    'reasoning': 'No matching VET skill found [Cluster mode]'
                }
                mappings.append(mapping)
        
        return mappings
        
    def export_skill_mappings_to_csv(self, 
                                 recommendations: List[CreditTransferRecommendation],
                                 filepath: str = None) -> str:
        """
        Export detailed skill mappings to CSV
        """
        import csv
        from datetime import datetime
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"output/skill_mappings_{timestamp}.csv"
        
        skill_mappings = self._extract_skill_mappings(recommendations)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'vet_unit', 'vet_skill', 'vet_level',
                'uni_course', 'uni_skill', 'uni_level',
                'mapping_type', 'similarity_score', 'reasoning'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for mapping in skill_mappings:
                writer.writerow({
                    'vet_unit': mapping['vet_unit'],
                    'vet_skill': mapping['vet_skill'],
                    'vet_level': mapping['vet_level'],
                    'uni_course': mapping['uni_course'],
                    'uni_skill': mapping['uni_skill'],
                    'uni_level': mapping['uni_level'],
                    'mapping_type': mapping['mapping_type'],
                    'similarity_score': f"{mapping['similarity']:.3f}",
                    'reasoning': mapping['reasoning']
                })
        
        return filepath