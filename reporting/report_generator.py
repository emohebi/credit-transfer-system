"""
Report generator for credit transfer analysis
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any
from io import StringIO

from ..models.base_models import (
    CreditTransferRecommendation,
    VETQualification,
    UniQualification
)
from ..models.enums import RecommendationType


class ReportGenerator:
    """Generate various report formats for credit transfer analysis"""
    
    def generate_full_report(self,
                             recommendations: List[CreditTransferRecommendation],
                             vet_qual: VETQualification,
                             uni_qual: UniQualification) -> str:
        """Generate comprehensive text report"""
        report = []
        
        # Header
        report.append("=" * 80)
        report.append("CREDIT TRANSFER ANALYSIS REPORT")
        report.append("=" * 80)
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\nVET Qualification: {vet_qual.code} - {vet_qual.name}")
        report.append(f"Level: {vet_qual.level}")
        report.append(f"Total Units: {len(vet_qual.units)}")
        
        report.append(f"\nUniversity Program: {uni_qual.code} - {uni_qual.name}")
        report.append(f"Total Courses: {len(uni_qual.courses)}")
        
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
                report.append(self._format_recommendation(i, rec))
        
        if conditional_recs:
            report.append("\n--- CONDITIONAL TRANSFERS ---")
            for i, rec in enumerate(conditional_recs[:10], 1):
                report.append(self._format_recommendation(i, rec))
        
        if partial_recs:
            report.append("\n--- PARTIAL TRANSFERS ---")
            for i, rec in enumerate(partial_recs[:10], 1):
                report.append(self._format_recommendation(i, rec))
        
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
        
        # Footer
        report.append("\n" + "=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def generate_csv_report(self, recommendations: List[CreditTransferRecommendation]) -> str:
        """Generate CSV report"""
        output = StringIO()
        
        fieldnames = [
            'VET_Units', 'Uni_Course_Code', 'Uni_Course_Name', 'Study_Level',
            'Alignment_Score', 'Confidence', 'Recommendation_Type',
            'Skill_Gaps', 'Conditions', 'Evidence'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for rec in recommendations:
            writer.writerow({
                'VET_Units': ', '.join(rec.get_vet_unit_codes()),
                'Uni_Course_Code': rec.uni_course.code,
                'Uni_Course_Name': rec.uni_course.name,
                'Study_Level': rec.uni_course.study_level,
                'Alignment_Score': f"{rec.alignment_score:.2%}",
                'Confidence': f"{rec.confidence:.2%}",
                'Recommendation_Type': rec.recommendation.value,
                'Skill_Gaps': '; '.join([s.name for s in rec.gaps[:3]]),
                'Conditions': '; '.join(rec.conditions[:3]),
                'Evidence': '; '.join(rec.evidence[:3])
            })
        
        return output.getvalue()
    
    def generate_html_report(self,
                             recommendations: List[CreditTransferRecommendation],
                             vet_qual: VETQualification,
                             uni_qual: UniQualification) -> str:
        """Generate HTML report"""
        html = []
        
        # HTML header
        html.append("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Credit Transfer Analysis Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h1 { color: #2c3e50; border-bottom: 2px solid #3498db; }
                h2 { color: #34495e; margin-top: 30px; }
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
            </style>
        </head>
        <body>
        """)
        
        # Title and header information
        html.append(f"<h1>Credit Transfer Analysis Report</h1>")
        html.append(f"<p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        html.append(f"<p><strong>VET Qualification:</strong> {vet_qual.code} - {vet_qual.name}</p>")
        html.append(f"<p><strong>University Program:</strong> {uni_qual.code} - {uni_qual.name}</p>")
        
        # Summary statistics
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
        
        # Recommendations table
        html.append("<h2>Credit Transfer Recommendations</h2>")
        html.append("<table>")
        html.append("<thead><tr>")
        html.append("<th>VET Units</th>")
        html.append("<th>University Course</th>")
        html.append("<th>Study Level</th>")
        html.append("<th>Alignment</th>")
        html.append("<th>Confidence</th>")
        html.append("<th>Type</th>")
        html.append("<th>Conditions</th>")
        html.append("</tr></thead>")
        html.append("<tbody>")
        
        for rec in recommendations[:50]:  # Limit to top 50
            rec_class = rec.recommendation.value
            html.append(f"<tr class='{rec_class}'>")
            html.append(f"<td>{', '.join(rec.get_vet_unit_codes())}</td>")
            html.append(f"<td>{rec.uni_course.code}: {rec.uni_course.name}</td>")
            html.append(f"<td>{rec.uni_course.study_level.title()}</td>")
            html.append(f"<td>{rec.alignment_score:.1%}</td>")
            html.append(f"<td>{rec.confidence:.1%}</td>")
            html.append(f"<td>{rec.recommendation.value.upper()}</td>")
            html.append(f"<td>{'; '.join(rec.conditions[:2]) if rec.conditions else 'None'}</td>")
            html.append("</tr>")
        
        html.append("</tbody></table>")
        
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
    
    def _format_recommendation(self, index: int, rec: CreditTransferRecommendation) -> str:
        """Format a single recommendation for text report"""
        lines = []
        lines.append(f"\n{index}. {rec.uni_course.code}: {rec.uni_course.name} (Level: {rec.uni_course.study_level})")
        lines.append("-" * 60)
        
        # VET units
        lines.append("VET Units:")
        for unit in rec.vet_units:
            lines.append(f"  • {unit.code}: {unit.name}")
        
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