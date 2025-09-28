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

import numpy as np

from models.base_models import (
    CreditTransferRecommendation,
    VETQualification,
    UniQualification
)
from models.enums import RecommendationType
from .skill_export import SkillExportManager
from utils.json_encoder import dumps, loads, make_json_serializable


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
        
        semantic_clusters = []
        for rec in recommendations:
            if 'semantic_clusters' in rec.metadata:
                semantic_clusters.extend(rec.metadata['semantic_clusters'])
        
        # Alternative: Load from JSON file if available
        import os
        if os.path.exists("./output/semantic_clusters.json"):
            import json
            with open("./output/semantic_clusters.json", 'r') as f:
                semantic_clusters = json.load(f)
        
        if semantic_clusters:
            files['semantic_clusters_csv'] = str(package_dir / "semantic_clusters.csv")
            self.export_semantic_clusters_to_csv(semantic_clusters, files['semantic_clusters_csv'])
            
        # In generate_complete_report_package, after the main reports:

        # Generate skill extraction journey report
        files['skill_journey_html'] = str(package_dir / "skill_extraction_journey.html")
        journey_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Skill Extraction Journey Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; }}
            </style>
        </head>
        <body>
            <h1>Skill Extraction Journey Report</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            {self._generate_skill_extraction_journey_html(vet_qual, uni_qual, max_units=10, max_skills_per_unit=15)}
        </body>
        </html>
        """
        with open(files['skill_journey_html'], 'w') as f:
            f.write(journey_content)
        
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
        html.append("<th>Level Alignment</th>")
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
            
            level_analysis = match_info.get('level_analysis', {})
            html.append(f"<td>")
            html.append(f"<div style='color: {level_analysis.get('color', 'black')}'>")
            html.append(f"<strong>{level_analysis.get('status', 'unknown').title()}</strong><br>")
            html.append(f"VET Avg: {level_analysis.get('avg_vet_level', 0):.1f}<br>")
            html.append(f"Uni Req: {level_analysis.get('avg_uni_level', 0):.1f}<br>")
            html.append(f"<small>{level_analysis.get('message', '')}</small>")
            html.append(f"</div>")
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
            
        journey_html = self._generate_skill_extraction_journey_html(
            vet_qual=vet_qual,
            uni_qual=uni_qual,
            max_units=5,
            max_skills_per_unit=8
        )
        html.append(journey_html)
        
        html.append(self._generate_semantic_clusters_html(recommendations))

        
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
        
        # Add level alignment analysis
        level_analysis = self._analyze_level_alignment(rec)
        
        # Get skill mapping details from metadata if available
        if 'skill_mapping' in rec.metadata:
            mapping = rec.metadata['skill_mapping']
            # Handle both list of skills and list of dicts
            if mapping.get('direct_matches'):
                direct_matches = len(mapping['direct_matches'])
            if mapping.get('partial_matches'):
                partial_matches = len(mapping['partial_matches'])
            if mapping.get('unmapped_uni'):
                unmapped_critical = len(mapping['unmapped_uni'])
        
        # Calculate quality scores breakdown
        quality_breakdown = {
            'coverage_score': rec.skill_coverage if isinstance(rec.skill_coverage, dict) else {},
            'context_alignment': rec.metadata.get('skill_mapping', {}).get('context_alignment', 0.0),
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
        
        # Get the total number of university skills
        total_uni_skills = len(rec.uni_course.extracted_skills) if hasattr(rec.uni_course, 'extracted_skills') else 0
        
        # Calculate component scores
        coverage_component = 0.5 * (direct_matches + partial_matches * 0.5) / max(total_uni_skills, 1)
        context_component = 0.25 * quality_breakdown['context_alignment']
        quality_component = 0.15 * rec.confidence
        edge_penalty = min(0.1, len(edge_case_summary) * 0.02)  # Cap penalty at 0.1
        
        return {
            'direct_matches': direct_matches,
            'partial_matches': partial_matches,
            'unmapped_critical': unmapped_critical,
            'total_uni_skills': total_uni_skills,
            'quality_breakdown': quality_breakdown,
            'score_components': {
                'coverage': coverage_component,
                'context': context_component,
                'quality': quality_component,
                'edge_penalty': edge_penalty
            },
            'edge_cases': edge_case_summary,
            'alignment_calculation': f"({coverage_component:.2f} + {context_component:.2f} + {quality_component:.2f} - {edge_penalty:.2f}) = {rec.alignment_score:.2%}",
            'level_analysis': level_analysis
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
        
    def _generate_skill_extraction_journey_html(self, 
                                           vet_qual: Optional[VETQualification] = None,
                                           uni_qual: Optional[UniQualification] = None,
                                           max_units: int = 5,
                                           max_skills_per_unit: int = 10) -> str:
        """Generate HTML showing the journey of skill extraction from source to final skills"""
        
        html = []
        
        # Add CSS for the journey table
        html.append("""
        <style>
            .journey-table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 20px 0;
                font-size: 14px;
            }
            .journey-table th { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; 
                padding: 12px; 
                text-align: left;
                position: sticky;
                top: 0;
            }
            .journey-table td { 
                padding: 10px; 
                border: 1px solid #e0e0e0;
                vertical-align: top;
            }
            .journey-table tr:nth-child(even) { background-color: #f9f9f9; }
            .source-text { 
                background: #f0f8ff; 
                padding: 8px; 
                border-radius: 5px;
                font-size: 12px;
                max-height: 150px;
                overflow-y: auto;
            }
            .skill-stage {
                background: #e8f5e9;
                padding: 6px;
                margin: 4px 0;
                border-radius: 4px;
                font-size: 12px;
            }
            .final-skill {
                background: #fff3e0;
                padding: 8px;
                margin: 4px 0;
                border-radius: 4px;
                border-left: 4px solid #ff9800;
            }
            .skill-meta {
                font-size: 11px;
                color: #666;
                margin-top: 4px;
            }
            .extraction-method {
                display: inline-block;
                padding: 2px 6px;
                background: #e3f2fd;
                border-radius: 3px;
                font-size: 11px;
                margin: 2px;
            }
            .confidence-high { color: #2e7d32; font-weight: bold; }
            .confidence-medium { color: #f57c00; }
            .confidence-low { color: #d32f2f; }
            .processing-arrow {
                text-align: center;
                color: #9c27b0;
                font-size: 18px;
                padding: 5px;
            }
            .highlighted-text {
                background: yellow;
                padding: 2px;
                border-radius: 3px;
            }
        </style>
        """)
        
        html.append("<h2>Skill Extraction Journey</h2>")
        html.append("<p><em>Showing how skills are extracted from source text through various processing stages</em></p>")
        
        # Process VET units
        if vet_qual:
            html.append("<h3>VET Units - Skill Extraction Process</h3>")
            html.append("<table class='journey-table'>")
            html.append("<thead><tr>")
            html.append("<th width='15%'>Unit</th>")
            html.append("<th width='25%'>Source Text Sample</th>")
            html.append("<th width='20%'>Initial Extraction</th>")
            html.append("<th width='20%'>Processing Steps</th>")
            html.append("<th width='20%'>Final Skills</th>")
            html.append("</tr></thead>")
            html.append("<tbody>")
            
            for unit in vet_qual.units[:max_units]:
                html.append("<tr>")
                
                # Unit info
                html.append(f"<td><strong>{unit.code}</strong><br>{unit.name}<br>")
                html.append(f"<span class='skill-meta'>Hours: {unit.nominal_hours}</span></td>")
                
                # Source text sample
                html.append("<td>")
                html.append("<div class='source-text'>")
                
                # Show snippets from different sources
                if unit.description:
                    html.append(f"<strong>Description:</strong><br>{unit.description[:200]}...<br><br>")
                
                if unit.learning_outcomes:
                    html.append(f"<strong>Learning Outcome Sample:</strong><br>")
                    html.append(f"{unit.learning_outcomes[0][:150]}...<br><br>" if unit.learning_outcomes else "")
                
                if unit.assessment_requirements:
                    html.append(f"<strong>Assessment Sample:</strong><br>")
                    html.append(f"{unit.assessment_requirements[:150]}...")
                
                html.append("</div>")
                html.append("</td>")
                
                # Initial extraction stage
                html.append("<td>")
                html.append("<div class='skill-stage'>")
                html.append("<strong>Stage 1: AI Extraction</strong><br>")
                
                # Show extraction metadata if available
                skills_by_source = self._categorize_skills_by_source(unit.extracted_skills)
                
                if skills_by_source.get('explicit', []):
                    html.append(f"<span class='extraction-method'>Explicit: {len(skills_by_source['explicit'])}</span>")
                if skills_by_source.get('implicit', []):
                    html.append(f"<span class='extraction-method'>Implicit: {len(skills_by_source['implicit'])}</span>")
                if skills_by_source.get('decomposed', []):
                    html.append(f"<span class='extraction-method'>Decomposed: {len(skills_by_source['decomposed'])}</span>")
                
                html.append("<br><br><strong>Sample Skills Found:</strong><br>")
                for skill in unit.extracted_skills[:3]:
                    confidence_class = self._get_confidence_class(skill.confidence)
                    html.append(f"• {skill.name} <span class='{confidence_class}'>({skill.confidence:.1f})</span><br>")
                
                html.append("</div>")
                html.append("</td>")
                
                # Processing steps
                html.append("<td>")
                html.append("<div class='skill-stage'>")
                html.append("<strong>Stage 2: Processing</strong><br>")
                html.append("<span class='extraction-method'>✓ Deduplication</span><br>")
                html.append("<span class='extraction-method'>✓ Categorization</span><br>")
                html.append("<span class='extraction-method'>✓ Level Assignment</span><br>")
                html.append("<span class='extraction-method'>✓ Context Analysis</span><br>")
                
                if unit.extracted_skills:
                    html.append("<br><strong>Categories Found:</strong><br>")
                    categories = set(s.category.value for s in unit.extracted_skills)
                    for cat in list(categories)[:3]:
                        html.append(f"<span class='extraction-method'>{cat}</span>")
                
                html.append("</div>")
                html.append("</td>")
                
                # Final skills
                html.append("<td>")
                for skill in unit.extracted_skills[:max_skills_per_unit]:
                    html.append("<div class='final-skill'>")
                    html.append(f"<strong>{skill.name}</strong><br>")
                    html.append(f"<span class='skill-meta'>")
                    html.append(f"Category: {skill.category.value}<br>")
                    html.append(f"Level: {skill.level.name}<br>")
                    html.append(f"Context: {skill.context.value}<br>")
                    confidence_class = self._get_confidence_class(skill.confidence)
                    html.append(f"Confidence: <span class='{confidence_class}'>{skill.confidence:.2f}</span><br>")
                    
                    # Add evidence and rationale display
                    if skill.evidence:
                        html.append(f"<strong>Evidence:</strong> <em>\"{skill.evidence}\"</em><br>")
                    if skill.translation_rationale:
                        html.append(f"<strong>Derivation:</strong> {skill.translation_rationale}<br>")
                    
                    if skill.keywords:
                        html.append(f"Keywords: {', '.join(skill.keywords[:3])}")
                    html.append("</span>")
                    html.append("</div>")
                
                if len(unit.extracted_skills) > max_skills_per_unit:
                    html.append(f"<div class='skill-meta'>... and {len(unit.extracted_skills) - max_skills_per_unit} more skills</div>")
                
                html.append("</td>")
                html.append("</tr>")
            
            html.append("</tbody></table>")
        
        # Process University courses
        if uni_qual:
            html.append("<h3>University Courses - Skill Extraction Process</h3>")
            html.append("<table class='journey-table'>")
            html.append("<thead><tr>")
            html.append("<th width='15%'>Course</th>")
            html.append("<th width='25%'>Source Text Sample</th>")
            html.append("<th width='20%'>Initial Extraction</th>")
            html.append("<th width='20%'>Processing Steps</th>")
            html.append("<th width='20%'>Final Skills</th>")
            html.append("</tr></thead>")
            html.append("<tbody>")
            
            for course in uni_qual.courses[:max_units]:
                html.append("<tr>")
                
                # Course info
                html.append(f"<td><strong>{course.code}</strong><br>{course.name}<br>")
                html.append(f"<span class='skill-meta'>Level: {course.study_level}<br>")
                html.append(f"Credits: {course.credit_points}</span></td>")
                
                # Source text sample
                html.append("<td>")
                html.append("<div class='source-text'>")
                
                if course.description:
                    html.append(f"<strong>Description:</strong><br>{course.description[:200]}...<br><br>")
                
                if course.learning_outcomes:
                    html.append(f"<strong>Learning Outcome Sample:</strong><br>")
                    html.append(f"{course.learning_outcomes[0][:150]}...<br><br>" if course.learning_outcomes else "")
                
                if course.topics:
                    html.append(f"<strong>Topics:</strong><br>")
                    html.append(f"{', '.join(course.topics[:3])}...")
                
                html.append("</div>")
                html.append("</td>")
                
                # Initial extraction
                html.append("<td>")
                html.append("<div class='skill-stage'>")
                html.append("<strong>Stage 1: AI Extraction</strong><br>")
                
                skills_by_source = self._categorize_skills_by_source(course.extracted_skills)
                
                if skills_by_source.get('explicit', []):
                    html.append(f"<span class='extraction-method'>Explicit: {len(skills_by_source['explicit'])}</span>")
                if skills_by_source.get('implicit', []):
                    html.append(f"<span class='extraction-method'>Implicit: {len(skills_by_source['implicit'])}</span>")
                if skills_by_source.get('prerequisite', []):
                    html.append(f"<span class='extraction-method'>Prerequisites: {len(skills_by_source['prerequisite'])}</span>")
                
                html.append("<br><br><strong>Sample Skills Found:</strong><br>")
                for skill in course.extracted_skills[:3]:
                    confidence_class = self._get_confidence_class(skill.confidence)
                    html.append(f"• {skill.name} <span class='{confidence_class}'>({skill.confidence:.1f})</span><br>")
                
                html.append("</div>")
                html.append("</td>")
                
                # Processing steps
                html.append("<td>")
                html.append("<div class='skill-stage'>")
                html.append("<strong>Stage 2: Processing</strong><br>")
                html.append("<span class='extraction-method'>✓ Study Level Adjustment</span><br>")
                html.append("<span class='extraction-method'>✓ Prerequisite Analysis</span><br>")
                html.append("<span class='extraction-method'>✓ Assessment Context</span><br>")
                html.append("<span class='extraction-method'>✓ Skill Refinement</span><br>")
                
                if course.extracted_skills:
                    html.append("<br><strong>Levels Adjusted to:</strong><br>")
                    levels = set(s.level.name for s in course.extracted_skills)
                    for level in list(levels)[:3]:
                        html.append(f"<span class='extraction-method'>{level}</span>")
                
                html.append("</div>")
                html.append("</td>")
                
                # Final skills
                html.append("<td>")
                for skill in course.extracted_skills[:max_skills_per_unit]:
                    html.append("<div class='final-skill'>")
                    html.append(f"<strong>{skill.name}</strong><br>")
                    html.append(f"<span class='skill-meta'>")
                    html.append(f"Category: {skill.category.value}<br>")
                    html.append(f"Level: {skill.level.name}<br>")
                    html.append(f"Context: {skill.context.value}<br>")
                    confidence_class = self._get_confidence_class(skill.confidence)
                    html.append(f"Confidence: <span class='{confidence_class}'>{skill.confidence:.2f}</span><br>")
                    # Add evidence and rationale display
                    if skill.evidence:
                        html.append(f"<strong>Evidence:</strong> <em>\"{skill.evidence}\"</em><br>")
                    if skill.translation_rationale:
                        html.append(f"<strong>Derivation:</strong> {skill.translation_rationale}<br>")

                    if skill.keywords:
                        html.append(f"Keywords: {', '.join(skill.keywords[:3])}")
                    html.append("</span>")
                    html.append("</div>")
                
                if len(course.extracted_skills) > max_skills_per_unit:
                    html.append(f"<div class='skill-meta'>... and {len(course.extracted_skills) - max_skills_per_unit} more skills</div>")
                
                html.append("</td>")
                html.append("</tr>")
            
            html.append("</tbody></table>")
        
        # Add extraction process summary
        html.append(self._generate_extraction_summary_html(vet_qual, uni_qual))
        
        return "\n".join(html)

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

    def _generate_extraction_summary_html(self, 
                                        vet_qual: Optional[VETQualification],
                                        uni_qual: Optional[UniQualification]) -> str:
        """Generate summary of extraction process"""
        html = []
        
        html.append("<div class='summary-box' style='margin-top: 30px;'>")
        html.append("<h3>Skill Extraction Process Summary</h3>")
        
        html.append("<h4>Extraction Pipeline:</h4>")
        html.append("<ol>")
        html.append("<li><strong>Source Text Analysis:</strong> Course descriptions, learning outcomes, assessment requirements</li>")
        html.append("<li><strong>AI Skill Extraction:</strong> Using GenAI to identify explicit skills from text</li>")
        html.append("<li><strong>Implicit Skill Detection:</strong> Identifying skills not explicitly mentioned but required</li>")
        html.append("<li><strong>Composite Skill Decomposition:</strong> Breaking down broad skills into components</li>")
        html.append("<li><strong>Context Determination:</strong> Classifying as theoretical, practical, or hybrid</li>")
        html.append("<li><strong>Level Adjustment:</strong> Aligning skill levels with study level</li>")
        html.append("<li><strong>Deduplication:</strong> Merging similar or duplicate skills</li>")
        html.append("<li><strong>Quality Assessment:</strong> Calculating confidence scores</li>")
        html.append("</ol>")
        
        if vet_qual or uni_qual:
            html.append("<h4>Extraction Statistics:</h4>")
            html.append("<table style='width: 50%; margin: 10px 0;'>")
            
            if vet_qual:
                total_vet_skills = sum(len(unit.extracted_skills) for unit in vet_qual.units)
                html.append(f"<tr><td>Total VET Skills Extracted:</td><td><strong>{total_vet_skills}</strong></td></tr>")
                
                # Categorize all VET skills
                all_vet_skills = []
                for unit in vet_qual.units:
                    all_vet_skills.extend(unit.extracted_skills)
                
                vet_categories = self._categorize_skills_by_source(all_vet_skills)
                for category, skills in vet_categories.items():
                    if skills:
                        html.append(f"<tr><td>&nbsp;&nbsp;- {category.title()}:</td><td>{len(skills)}</td></tr>")
            
            if uni_qual:
                total_uni_skills = sum(len(course.extracted_skills) for course in uni_qual.courses)
                html.append(f"<tr><td>Total University Skills Extracted:</td><td><strong>{total_uni_skills}</strong></td></tr>")
                
                # Categorize all Uni skills
                all_uni_skills = []
                for course in uni_qual.courses:
                    all_uni_skills.extend(course.extracted_skills)
                
                uni_categories = self._categorize_skills_by_source(all_uni_skills)
                for category, skills in uni_categories.items():
                    if skills:
                        html.append(f"<tr><td>&nbsp;&nbsp;- {category.title()}:</td><td>{len(skills)}</td></tr>")
            
            html.append("</table>")
        
        html.append("</div>")
        
        return "\n".join(html)
    
    # Add study level analysis to the HTML report
    def _generate_study_level_summary(self, recommendations: List[CreditTransferRecommendation]) -> str:
        """Generate study level alignment summary"""
        
        html = []
        html.append("<div class='summary-box'>")
        html.append("<h3>Study Level Alignment Analysis</h3>")
        
        # Group by study level
        by_level = {}
        for rec in recommendations:
            level = rec.uni_course.study_level
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(rec)
        
        html.append("<table style='width: 100%;'>")
        html.append("<thead><tr>")
        html.append("<th>University Study Level</th>")
        html.append("<th>Expected Skill Range</th>")
        html.append("<th>Courses</th>")
        html.append("<th>Avg VET Level</th>")
        html.append("<th>Alignment</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        
        for level in sorted(by_level.keys()):
            recs = by_level[level]
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(level)
            
            # Calculate average VET levels for this study level
            all_vet_levels = []
            for rec in recs:
                for unit in rec.vet_units:
                    all_vet_levels.extend([s.level.value for s in unit.extracted_skills])
            
            avg_vet = np.mean(all_vet_levels) if all_vet_levels else 0
            
            # Determine alignment
            if avg_vet < expected_min:
                alignment = f"<span style='color: orange;'>Below ({avg_vet:.1f} < {expected_min})</span>"
            elif avg_vet > expected_max:
                alignment = f"<span style='color: green;'>Exceeds ({avg_vet:.1f} > {expected_max})</span>"
            else:
                alignment = f"<span style='color: green;'>Good ({expected_min} ≤ {avg_vet:.1f} ≤ {expected_max})</span>"
            
            html.append("<tr>")
            html.append(f"<td><strong>{level.title()}</strong></td>")
            html.append(f"<td>Level {expected_min}-{expected_max}</td>")
            html.append(f"<td>{len(recs)} courses</td>")
            html.append(f"<td>{avg_vet:.1f}</td>")
            html.append(f"<td>{alignment}</td>")
            html.append("</tr>")
        
        html.append("</tbody></table>")
        html.append("</div>")
        
        return "\n".join(html)
    
    def export_semantic_clusters_to_csv(self, 
                                        semantic_clusters: List[Dict],
                                        filepath: str = None) -> str:
        """
        Export semantic clusters to CSV for analysis
        
        Args:
            semantic_clusters: List of cluster dictionaries from matching
            filepath: Optional path for CSV file
            
        Returns:
            Path to exported CSV file
        """
        import csv
        from datetime import datetime
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"output/semantic_clusters_{timestamp}.csv"
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'cluster_id', 'cluster_size', 'avg_semantic_similarity',
                'vet_skills', 'vet_skill_count', 'vet_skill_names',
                'uni_skills', 'uni_skill_count', 'uni_skill_names',
                'match_type', 'level_alignment_potential'
            ]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for cluster in semantic_clusters:
                # Extract VET skill details
                vet_skill_objects = [item['skill'] for item in cluster.get('vet_skills', [])]
                vet_skill_names = [skill["name"] for skill in vet_skill_objects]
                vet_levels = [skill["level"] for skill in vet_skill_objects]
                
                # Extract Uni skill details
                uni_skill_objects = [item['skill'] for item in cluster.get('uni_skills', [])]
                uni_skill_names = [skill["name"] for skill in uni_skill_objects]
                uni_levels = [skill["level"] for skill in uni_skill_objects]
                
                # Determine match type
                if len(vet_skill_objects) == 1 and len(uni_skill_objects) == 1:
                    match_type = "one-to-one"
                elif len(vet_skill_objects) > 1 and len(uni_skill_objects) == 1:
                    match_type = "many-to-one"
                elif len(vet_skill_objects) == 1 and len(uni_skill_objects) > 1:
                    match_type = "one-to-many"
                else:
                    match_type = "many-to-many"
                
                # Calculate level alignment
                avg_vet_level = sum(vet_levels) / len(vet_levels) if vet_levels else 0
                avg_uni_level = sum(uni_levels) / len(uni_levels) if uni_levels else 0
                level_gap = avg_uni_level - avg_vet_level
                
                if level_gap <= 0:
                    level_alignment = "VET exceeds"
                elif level_gap <= 1:
                    level_alignment = "Well aligned"
                else:
                    level_alignment = "Gap exists"
                
                writer.writerow({
                    'cluster_id': cluster.get('cluster_id', ''),
                    'cluster_size': cluster.get('size', len(cluster.get('vet_skills', [])) + len(cluster.get('uni_skills', []))),
                    'avg_semantic_similarity': f"{cluster.get('avg_semantic_similarity', 0):.3f}",
                    'vet_skills': '; '.join([f"{s['skill']['name']} ({s['skill']['level']})" for s in cluster.get('vet_skills', [])]),
                    'vet_skill_count': len(vet_skill_objects),
                    'vet_skill_names': '; '.join(vet_skill_names),
                    'uni_skills': '; '.join([f"{s['skill']['name']} ({s['skill']['level']})" for s in cluster.get('uni_skills', [])]),
                    'uni_skill_count': len(uni_skill_objects),
                    'uni_skill_names': '; '.join(uni_skill_names),
                    'match_type': match_type,
                    'level_alignment_potential': level_alignment
                })
        
        return filepath
    
    def _generate_semantic_clusters_html(self, recommendations: List[CreditTransferRecommendation]) -> str:
        """Generate HTML section for semantic clusters visualization"""
        
        html = []
        
        # Add CSS for clusters
        html.append("""
        <style>
            .cluster-section { margin: 30px 0; }
            .cluster-card {
                background: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
            }
            .cluster-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            .skill-column {
                display: inline-block;
                width: 45%;
                vertical-align: top;
                padding: 10px;
                background: white;
                border-radius: 5px;
                margin: 5px;
            }
            .vet-column { border-left: 4px solid #28a745; }
            .uni-column { border-left: 4px solid #007bff; }
            .skill-item {
                padding: 5px;
                margin: 3px 0;
                background: #f0f0f0;
                border-radius: 3px;
                font-size: 14px;
            }
            .similarity-score {
                display: inline-block;
                padding: 3px 8px;
                background: #ffc107;
                color: #000;
                border-radius: 12px;
                font-weight: bold;
                font-size: 12px;
            }
            .level-badge {
                display: inline-block;
                padding: 2px 6px;
                background: #6c757d;
                color: white;
                border-radius: 3px;
                font-size: 11px;
                margin-left: 5px;
            }
            .cluster-stats {
                display: flex;
                justify-content: space-around;
                margin: 10px 0;
                font-size: 13px;
            }
            .stat-item {
                text-align: center;
                padding: 5px;
            }
            .stat-value {
                font-size: 18px;
                font-weight: bold;
                color: #495057;
            }
            .stat-label {
                color: #6c757d;
                font-size: 11px;
            }
        </style>
        """)
        
        html.append("<div class='cluster-section'>")
        html.append("<h2>Semantic Skill Clusters</h2>")
        html.append("<p>Skills grouped by semantic similarity, showing potential matches between VET and University competencies.</p>")
        
        # Get semantic clusters from recommendations metadata
        # Note: This assumes clusters are stored in recommendation metadata
        # You may need to modify based on your actual data structure
        
        clusters_to_display = []
        for rec in recommendations:
            if 'semantic_clusters' in rec.metadata:
                clusters_to_display.extend(rec.metadata['semantic_clusters'])
        
        # Alternative: Load from the JSON file if saved
        import json
        import os
        if os.path.exists("./output/semantic_clusters.json"):
            with open("./output/semantic_clusters.json", 'r') as f:
                clusters_data = json.load(f)
                clusters_to_display = clusters_data if isinstance(clusters_data, list) else []
        
        if not clusters_to_display:
            html.append("<p><em>No semantic clusters available. Run the analysis with clustering enabled.</em></p>")
        else:
            # Display statistics
            html.append("<div class='cluster-stats'>")
            html.append(f"<div class='stat-item'><div class='stat-value'>{len(clusters_to_display)}</div><div class='stat-label'>Total Clusters</div></div>")
            
            one_to_one = sum(1 for c in clusters_to_display if len(c.get('vet_skills', [])) == 1 and len(c.get('uni_skills', [])) == 1)
            many_to_many = sum(1 for c in clusters_to_display if len(c.get('vet_skills', [])) > 1 and len(c.get('uni_skills', [])) > 1)
            
            html.append(f"<div class='stat-item'><div class='stat-value'>{one_to_one}</div><div class='stat-label'>One-to-One Matches</div></div>")
            html.append(f"<div class='stat-item'><div class='stat-value'>{many_to_many}</div><div class='stat-label'>Many-to-Many Matches</div></div>")
            
            avg_sim = sum(c.get('avg_semantic_similarity', 0) for c in clusters_to_display) / len(clusters_to_display) if clusters_to_display else 0
            html.append(f"<div class='stat-item'><div class='stat-value'>{avg_sim:.2%}</div><div class='stat-label'>Avg Similarity</div></div>")
            html.append("</div>")
            
            # Display top clusters (limit to 20 for readability)
            html.append("<h3>Top Semantic Clusters</h3>")
            
            # Sort by similarity score
            sorted_clusters = sorted(clusters_to_display, 
                                key=lambda x: x.get('avg_semantic_similarity', 0), 
                                reverse=True)[:20]
            
            for idx, cluster in enumerate(sorted_clusters, 1):
                html.append(f"<div class='cluster-card'>")
                
                # Cluster header
                html.append(f"<div class='cluster-header'>")
                html.append(f"<strong>Cluster {cluster.get('cluster_id', idx)}</strong>")
                html.append(f"<span class='similarity-score'>Similarity: {cluster.get('avg_semantic_similarity', 0):.1%}</span>")
                html.append(f"</div>")
                
                # Two columns for VET and Uni skills
                html.append("<div style='display: flex; justify-content: space-between;'>")
                
                # VET skills column
                html.append("<div class='skill-column vet-column'>")
                html.append("<strong>VET Skills:</strong><br>")
                for skill_item in cluster.get('vet_skills', [])[:5]:  # Limit to 5 for readability
                    skill = skill_item.get('skill')
                    if hasattr(skill, 'name'):
                        html.append(f"<div class='skill-item'>")
                        html.append(f"{skill['name']}")
                        html.append(f"<span class='level-badge'>L{skill['level']}</span>")
                        if skill["evidence"]:
                            html.append(f"<br><small style='color: #666;'>Evidence: \"{skill['evidence'][:50]}...\"</small>")
                        html.append(f"</div>")
                
                if len(cluster.get('vet_skills', [])) > 5:
                    html.append(f"<small>... and {len(cluster.get('vet_skills', [])) - 5} more</small>")
                html.append("</div>")
                
                # University skills column
                html.append("<div class='skill-column uni-column'>")
                html.append("<strong>University Skills:</strong><br>")
                for skill_item in cluster.get('uni_skills', [])[:5]:
                    skill = skill_item.get('skill')
                    if hasattr(skill, 'name'):
                        html.append(f"<div class='skill-item'>")
                        html.append(f"{skill['name']}")
                        html.append(f"<span class='level-badge'>L{skill['level']}</span>")
                        if skill.evidence:
                            html.append(f"<br><small style='color: #666;'>Evidence: \"{skill['evidence'][:50]}...\"</small>")
                        html.append(f"</div>")
                
                if len(cluster.get('uni_skills', [])) > 5:
                    html.append(f"<small>... and {len(cluster.get('uni_skills', [])) - 5} more</small>")
                html.append("</div>")
                
                html.append("</div>")  # End columns
                
                # Cluster analysis
                vet_count = len(cluster.get('vet_skills', []))
                uni_count = len(cluster.get('uni_skills', []))
                
                if vet_count > 0 and uni_count > 0:
                    if vet_count == 1 and uni_count == 1:
                        match_desc = "Direct one-to-one skill correspondence"
                    elif vet_count > uni_count:
                        match_desc = f"Multiple VET skills ({vet_count}) map to fewer university skills ({uni_count})"
                    elif uni_count > vet_count:
                        match_desc = f"Few VET skills ({vet_count}) map to multiple university skills ({uni_count})"
                    else:
                        match_desc = f"Complex many-to-many relationship ({vet_count} to {uni_count})"
                    
                    html.append(f"<div style='margin-top: 10px; padding: 8px; background: #e9ecef; border-radius: 4px; font-size: 13px;'>")
                    html.append(f"<strong>Analysis:</strong> {match_desc}")
                    html.append(f"</div>")
                
                html.append("</div>")  # End cluster card
            
            # Add link to full CSV export
            html.append("<div style='margin-top: 20px; padding: 10px; background: #d1ecf1; border-radius: 5px;'>")
            html.append("<strong>📊 Full Analysis:</strong> Semantic clusters have been exported to CSV for detailed analysis.")
            html.append("</div>")
        
        html.append("</div>")  # End cluster section
        
        return "\n".join(html)