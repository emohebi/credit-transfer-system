"""
Report generator for credit transfer analysis
Integrated with skill export functionality
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from io import StringIO
from pathlib import Path

from models.base_models import (
    CreditTransferRecommendation,
    VETQualification,
    UniQualification
)
from models.enums import RecommendationType
from .skill_export import SkillExportManager


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
        
        # Generate text report
        files['report_text'] = str(package_dir / "report.txt")
        text_content = self.generate_full_report(recommendations, vet_qual, uni_qual)
        with open(files['report_text'], 'w') as f:
            f.write(text_content)
        
        # Export extracted skills
        skill_export_dir = package_dir / "extracted_skills"
        skill_export_dir.mkdir(exist_ok=True)
        
        # Export VET skills
        files['vet_skills_json'] = str(skill_export_dir / f"{vet_qual.code}_skills.json")
        self._export_skills_json(vet_qual, None, files['vet_skills_json'])
        
        files['vet_skills_csv'] = str(skill_export_dir / f"{vet_qual.code}_skills.csv")
        self._export_skills_csv(vet_qual, None, files['vet_skills_csv'])
        
        # Export University skills
        files['uni_skills_json'] = str(skill_export_dir / f"{uni_qual.code}_skills.json")
        self._export_skills_json(None, uni_qual, files['uni_skills_json'])
        
        files['uni_skills_csv'] = str(skill_export_dir / f"{uni_qual.code}_skills.csv")
        self._export_skills_csv(None, uni_qual, files['uni_skills_csv'])
        
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
    
    def _export_skills_csv(self,
                          vet_qual: Optional[VETQualification],
                          uni_qual: Optional[UniQualification],
                          filepath: str):
        """Export skills to CSV using skill export manager"""
        if vet_qual and not uni_qual:
            self.skill_export._export_vet_to_csv(vet_qual, Path(filepath))
        elif uni_qual and not vet_qual:
            self.skill_export._export_uni_to_csv(uni_qual, Path(filepath))
        else:
            self.skill_export._export_combined_to_csv(vet_qual, uni_qual, Path(filepath))
    
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
                rec_data["vet_skills"].extend([
                    {
                        "unit": unit.code,
                        "name": skill.name,
                        "category": skill.category.value,
                        "level": skill.level.name,
                        "context": skill.context.value,
                        "confidence": skill.confidence
                    }
                    for skill in unit.extracted_skills
                ])
            
            rec_data["uni_skills"] = [
                {
                    "name": skill.name,
                    "category": skill.category.value,
                    "level": skill.level.name,
                    "context": skill.context.value,
                    "confidence": skill.confidence
                }
                for skill in rec.uni_course.extracted_skills
            ]
            
            data["recommendations"].append(rec_data)
        
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
        """Generate CSV report with skill counts"""
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
            # Count VET skills
            vet_skill_count = sum(len(unit.extracted_skills) for unit in rec.vet_units)
            
            # Count university skills
            uni_skill_count = len(rec.uni_course.extracted_skills)
            match_info = self._extract_detailed_match_info(rec)
            
            writer.writerow({
                'VET_Units': ', '.join(rec.get_vet_unit_codes()),
                'VET_Skill_Count': vet_skill_count,
                'Uni_Course_Code': rec.uni_course.code,
                'Uni_Course_Name': rec.uni_course.name,
                'Uni_Skill_Count': uni_skill_count,
                'Study_Level': rec.uni_course.study_level,
                'Alignment_Score': f"{rec.alignment_score:.2%}",
                'Confidence': f"{rec.confidence:.2%}",
                'Recommendation_Type': rec.recommendation.value,
                'Direct_Matches': len([e for e in rec.evidence if 'direct' in e.lower()]),
                'Partial_Matches': len([e for e in rec.evidence if 'partial' in e.lower()]),
                'Skill_Gaps': '; '.join([s.name for s in rec.gaps[:3]]),
                'Conditions': '; '.join(rec.conditions[:3]),
                'Evidence': '; '.join(rec.evidence[:3]),
                'Direct_Matches': match_info['direct_matches'],
                'Partial_Matches': match_info['partial_matches'],
                'Unmapped_Skills': match_info['unmapped_critical'],
                'Coverage_Score': f"{match_info['score_components']['coverage']:.2f}",
                'Context_Score': f"{match_info['score_components']['context']:.2f}",
                'Quality_Score': f"{match_info['score_components']['quality']:.2f}",
                'Edge_Penalty': f"{match_info['score_components']['edge_penalty']:.2f}",
                'Transfer_Reasoning': self._generate_transfer_reasoning(rec, match_info).replace('<br>', '; ')
            })
        
        return output.getvalue()
    
    def generate_html_report(self,
                             recommendations: List[CreditTransferRecommendation],
                             vet_qual: VETQualification,
                             uni_qual: UniQualification) -> str:
        """Generate HTML report with skill information"""
        html = []
        
        # HTML header with enhanced styles
        html.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Credit Transfer Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th { background-color: #3498db; color: white; padding: 10px; text-align: left; }
                td { padding: 8px; border-bottom: 1px solid #ddd; }
                tr:hover { background-color: #f5f5f5; }
                .full { background-color: #d4edda; }
                .conditional { background-color: #fff3cd; }
                .partial { background-color: #f8d7da; }
                .summary-box { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 20px 0; }
                .progress-bar { width: 100%; height: 20px; background-color: #e0e0e0; border-radius: 10px; }
                .progress-fill { height: 100%; background-color: #3498db; border-radius: 10px; }
                .skill-badge { display: inline-block; padding: 3px 8px; margin: 2px; background-color: #e3f2fd; border-radius: 12px; font-size: 12px; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
                .stat-card { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                .stat-value { font-size: 24px; font-weight: bold; color: #3498db; }
                .stat-label { color: #7f8c8d; font-size: 14px; }
                /* New styles for detailed analysis */
                .detail-table { font-size: 14px; }
                .score-component { 
                    display: inline-block; 
                    padding: 2px 6px; 
                    margin: 2px;
                    background: #f0f0f0;
                    border-radius: 4px;
                    font-size: 12px;
                }
                .match-quality-high { color: #27ae60; font-weight: bold; }
                .match-quality-medium { color: #f39c12; }
                .match-quality-low { color: #e74c3c; }
                .reasoning-box {
                    background: #fafafa;
                    padding: 8px;
                    border-left: 3px solid #3498db;
                    margin: 5px 0;
                    font-size: 13px;
                }
                .edge-case-warning {
                    background: #fff3cd;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 11px;
                    margin: 2px 0;
                }
            </style>
        </head>
        <body>
        """)
        
        # Title and header information
        html.append(f"<h1>Credit Transfer Analysis Report</h1>")
        html.append(f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html.append(f"<p><strong>VET Qualification:</strong> {vet_qual.code} - {vet_qual.name}</p>")
        html.append(f"<p><strong>University Program:</strong> {uni_qual.code} - {uni_qual.name}</p>")
        
        # Skill extraction summary
        vet_skills = []
        for unit in vet_qual.units:
            vet_skills.extend(unit.extracted_skills)
        
        uni_skills = []
        for course in uni_qual.courses:
            uni_skills.extend(course.extracted_skills)
        
        html.append("<div class='summary-box'>")
        html.append("<h2>Skill Extraction Summary</h2>")
        html.append("<div class='stats-grid'>")
        
        html.append("<div class='stat-card'>")
        html.append(f"<div class='stat-value'>{len(vet_skills)}</div>")
        html.append("<div class='stat-label'>VET Skills Extracted</div>")
        html.append("</div>")
        
        html.append("<div class='stat-card'>")
        html.append(f"<div class='stat-value'>{len(uni_skills)}</div>")
        html.append("<div class='stat-label'>University Skills Extracted</div>")
        html.append("</div>")
        
        common_count = len(set(s.name.lower() for s in vet_skills).intersection(
            set(s.name.lower() for s in uni_skills)))
        
        html.append("<div class='stat-card'>")
        html.append(f"<div class='stat-value'>{common_count}</div>")
        html.append("<div class='stat-label'>Common Skills</div>")
        html.append("</div>")
        
        html.append("</div>")
        html.append("</div>")
        
        # Executive Summary
        summary = self._generate_summary_stats(recommendations)
        html.append("<div class='summary-box'>")
        html.append("<h2>Executive Summary</h2>")
        html.append(f"<p><strong>Total Recommendations:</strong> {summary['total']}</p>")
        html.append(f"<p><strong>Average Alignment Score:</strong> {summary['avg_alignment']:.1%}</p>")
        
        # Progress bars for recommendation types
        html.append("<h3>Recommendation Distribution</h3>")
        for rec_type, count, percent in [
            ('Full Credit', summary['full_count'], summary['full_percent']),
            ('Conditional', summary['conditional_count'], summary['conditional_percent']),
            ('Partial', summary['partial_count'], summary['partial_percent'])
        ]:
            html.append(f"<p>{rec_type}: {count} ({percent:.1%})</p>")
            html.append(f"<div class='progress-bar'><div class='progress-fill' style='width: {percent*100}%;'></div></div>")
        
        html.append("</div>")
        
        # Recommendations table with skills
        html.append("<h2>Credit Transfer Recommendations</h2>")
        html.append("<table>")
        html.append("<thead><tr>")
        html.append("<th>VET Units</th>")
        html.append("<th>University Course</th>")
        html.append("<th>Study Level</th>")
        html.append("<th>Skills Match</th>")
        html.append("<th>Alignment</th>")
        html.append("<th>Confidence</th>")
        html.append("<th>Type</th>")
        html.append("<th>Conditions</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        
        for rec in recommendations[:50]:  # Limit to top 50
            rec_class = rec.recommendation.value
            
            # Count skill matches
            vet_skill_count = sum(len(unit.extracted_skills) for unit in rec.vet_units)
            uni_skill_count = len(rec.uni_course.extracted_skills)
            
            html.append(f"<tr class='{rec_class}'>")
            html.append(f"<td>{', '.join(rec.get_vet_unit_codes())}</td>")
            html.append(f"<td>{rec.uni_course.code}: {rec.uni_course.name}</td>")
            html.append(f"<td>{rec.uni_course.study_level.title()}</td>")
            html.append(f"<td>{vet_skill_count} → {uni_skill_count}</td>")
            html.append(f"<td>{rec.alignment_score:.1%}</td>")
            html.append(f"<td>{rec.confidence:.1%}</td>")
            html.append(f"<td>{rec.recommendation.value.upper()}</td>")
            html.append(f"<td>{'; '.join(rec.conditions[:2]) if rec.conditions else 'None'}</td>")
            html.append("</tr>")
        
        html.append("</tbody></table>")
        
        # Add this after the main recommendations table (around line 700)

        # Detailed Match Analysis Table
        html.append("<h2>Detailed Match Analysis</h2>")
        html.append("<table>")
        html.append("<thead><tr>")
        html.append("<th>VET → Uni</th>")
        html.append("<th>Match Type</th>")
        html.append("<th>Score Breakdown</th>")
        html.append("<th>Quality Factors</th>")
        html.append("<th>Edge Cases</th>")
        html.append("<th>Reasoning</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")

        for rec in recommendations[:20]:  # Top 20 detailed
            match_info = self._extract_detailed_match_info(rec)
            
            html.append(f"<tr class='{rec.recommendation.value}'>")
            
            # VET to Uni mapping
            html.append(f"<td>{', '.join(rec.get_vet_unit_codes())}<br>→<br>{rec.uni_course.code}</td>")
            
            # Match breakdown
            html.append(f"<td>")
            html.append(f"<strong>Direct:</strong> {match_info['direct_matches']}/{match_info['total_uni_skills']}<br>")
            html.append(f"<strong>Partial:</strong> {match_info['partial_matches']}/{match_info['total_uni_skills']}<br>")
            html.append(f"<strong>Unmapped:</strong> {match_info['unmapped_critical']}")
            html.append(f"</td>")
            
            # Score components
            html.append(f"<td>")
            for comp, value in match_info['score_components'].items():
                if comp != 'edge_penalty':
                    html.append(f"<small>{comp.title()}: {value:.2f}</small><br>")
                else:
                    html.append(f"<small style='color: red;'>Penalty: -{value:.2f}</small><br>")
            html.append(f"<strong>Total: {rec.alignment_score:.1%}</strong>")
            html.append(f"</td>")
            
            # Quality factors
            html.append(f"<td>")
            for category, coverage in rec.skill_coverage.items():
                html.append(f"<small>{category}: {coverage:.0%}</small><br>")
            html.append(f"<strong>Confidence: {rec.confidence:.1%}</strong>")
            html.append(f"</td>")
            
            # Edge cases
            html.append(f"<td style='font-size: 12px;'>")
            if match_info['edge_cases']:
                for case_type, case_data in list(match_info['edge_cases'].items())[:2]:
                    html.append(f"<small>• {case_type.replace('_', ' ').title()}</small><br>")
            else:
                html.append("None detected")
            html.append(f"</td>")
            
            # Reasoning
            html.append(f"<td style='font-size: 12px;'>")
            html.append(self._generate_transfer_reasoning(rec, match_info))
            html.append(f"</td>")
            
            html.append("</tr>")

        html.append("</tbody></table>")

        # Add Score Calculation Legend
        html.append("<div class='summary-box'>")
        html.append("<h3>Score Calculation Method</h3>")
        html.append("<p><strong>Alignment Score = </strong>")
        html.append("(0.5 × Coverage) + (0.25 × Context) + (0.15 × Quality) - (0.1 × Edge Penalties)</p>")
        html.append("<ul>")
        html.append("<li><strong>Coverage:</strong> Direct matches count 100%, partial matches count 50%</li>")
        html.append("<li><strong>Context:</strong> Alignment between practical/theoretical requirements</li>")
        html.append("<li><strong>Quality:</strong> Match confidence and skill level alignment</li>")
        html.append("<li><strong>Edge Penalties:</strong> Deductions for outdated content, missing prerequisites, etc.</li>")
        html.append("</ul>")
        html.append("</div>")
                
        # Top Skills Section
        html.append("<h2>Top Extracted Skills</h2>")
        
        html.append("<h3>VET Skills (Top 20)</h3>")
        html.append("<div>")
        vet_skill_names = [s.name for s in sorted(vet_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in vet_skill_names[:20]:
            html.append(f"<span class='skill-badge'>{skill_name}</span>")
        html.append("</div>")
        
        html.append("<h3>University Skills (Top 20)</h3>")
        html.append("<div>")
        uni_skill_names = [s.name for s in sorted(uni_skills, key=lambda x: x.confidence, reverse=True)]
        for skill_name in uni_skill_names[:20]:
            html.append(f"<span class='skill-badge'>{skill_name}</span>")
        html.append("</div>")
        
        # Gap Analysis
        gaps = self._analyze_gaps(recommendations)
        if gaps['common_gaps']:
            html.append("<h2>Common Skill Gaps</h2>")
            html.append("<ul>")
            for skill, count in gaps['common_gaps'][:10]:
                html.append(f"<li>{skill} ({count} occurrences)</li>")
            html.append("</ul>")
        
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
        """Extract detailed matching information from recommendation"""
        
        # Initialize counters
        direct_matches = 0
        partial_matches = 0
        unmapped_critical = 0
        
        # Get skill mapping details from metadata if available
        if 'skill_mapping' in rec.metadata:
            mapping = rec.metadata['skill_mapping']
            direct_matches = len(mapping.get('direct_matches', []))
            partial_matches = len(mapping.get('partial_matches', []))
            unmapped_critical = len(mapping.get('unmapped_uni', []))
        
        # Calculate quality scores breakdown
        quality_breakdown = {
            'coverage_score': rec.skill_coverage,
            'context_alignment': 0.0,
            'level_alignment': 0.0,
            'confidence_average': rec.confidence
        }
        
        # Extract edge case information
        edge_case_summary = {}
        if rec.edge_case_results:
            for case_type, case_data in rec.edge_case_results.items():
                if isinstance(case_data, dict) and case_data.get('applicable'):
                    edge_case_summary[case_type] = {
                        'impact': case_data.get('imbalance_score', 0),
                        'recommendation': case_data.get('recommendation', ''),
                        'requirements': case_data.get('bridging_requirements', [])
                    }
        
        # Calculate component scores
        coverage_component = 0.5 * (direct_matches + partial_matches * 0.5) / max(rec.uni_course.extracted_skills, 1) if hasattr(rec.uni_course, 'extracted_skills') else 0
        context_component = 0.25 * quality_breakdown['context_alignment']
        quality_component = 0.15 * rec.confidence
        edge_penalty = 0.1 * len(edge_case_summary)
        
        return {
            'direct_matches': direct_matches,
            'partial_matches': partial_matches,
            'unmapped_critical': unmapped_critical,
            'total_uni_skills': len(rec.uni_course.extracted_skills) if hasattr(rec.uni_course, 'extracted_skills') else 0,
            'quality_breakdown': quality_breakdown,
            'score_components': {
                'coverage': coverage_component,
                'context': context_component,
                'quality': quality_component,
                'edge_penalty': edge_penalty
            },
            'edge_cases': edge_case_summary,
            'alignment_calculation': f"({coverage_component:.2f} + {context_component:.2f} + {quality_component:.2f} - {edge_penalty:.2f}) = {rec.alignment_score:.2%}"
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