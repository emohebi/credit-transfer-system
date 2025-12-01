"""
Enhanced Taxonomy Validator for Multi-Dimensional 5-Level Hierarchy
Validates structure, dimensions, relationships, and quality metrics
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import defaultdict

logger = logging.getLogger(__name__)


class MultiDimensionalTaxonomyValidator:
    """Validates multi-dimensional taxonomy structure and quality"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.validation_config = config['validation']
        self.taxonomy_config = config.get('taxonomy', {})
        
        # Standard thresholds
        self.coverage_threshold = self.validation_config['coverage_threshold']
        self.coherence_threshold = self.validation_config['coherence_threshold']
        self.distinctiveness_threshold = self.validation_config['distinctiveness_threshold']
        self.max_orphan_skills = self.validation_config['max_orphan_skills']
        
        # Multi-dimensional validation settings
        self.validate_domains = self.validation_config.get('validate_domain_assignment', True)
        self.validate_transferability = self.validation_config.get('validate_transferability_scores', True)
        self.validate_relationships = self.validation_config.get('validate_skill_relationships', True)
        self.min_skills_per_family = self.validation_config.get('min_skills_per_family', 5)
        
        # Get domain and family definitions
        self.domains = self.taxonomy_config.get('domains', {})
        self.families = self.taxonomy_config.get('families', {})
        
        logger.info("Initialized Multi-Dimensional Taxonomy Validator")
    
    def validate(self, taxonomy: Dict, df_clustered: pd.DataFrame) -> Dict:
        """
        Comprehensive validation of multi-dimensional taxonomy
        
        Args:
            taxonomy: The generated taxonomy structure
            df_clustered: DataFrame with clustered and enriched skills
            
        Returns:
            Dictionary with validation results and metrics
        """
        logger.info("=" * 80)
        logger.info("VALIDATING MULTI-DIMENSIONAL TAXONOMY")
        logger.info("=" * 80)
        
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'metrics': {},
            'dimension_metrics': {}
        }
        
        # 1. Structural Validation
        logger.info("\n[1/8] Validating taxonomy structure...")
        structure_results = self._validate_structure(taxonomy)
        validation_results['metrics'].update(structure_results['metrics'])
        validation_results['warnings'].extend(structure_results['warnings'])
        validation_results['errors'].extend(structure_results['errors'])
        
        # 2. Coverage Validation
        logger.info("[2/8] Validating skill coverage...")
        coverage = self._check_coverage(taxonomy, df_clustered)
        validation_results['metrics']['coverage'] = coverage
        validation_results['coverage'] = coverage
        
        if coverage < self.coverage_threshold:
            warning = f"Low coverage: {coverage:.1%} (threshold: {self.coverage_threshold:.1%})"
            validation_results['warnings'].append(warning)
            logger.warning(f"  ⚠ {warning}")
        else:
            logger.info(f"  ✓ Coverage: {coverage:.1%}")
        
        # 3. Cluster Coherence
        logger.info("[3/8] Validating cluster coherence...")
        coherence_results = self._validate_cluster_coherence(df_clustered)
        validation_results['metrics'].update(coherence_results)
        if coherence_results['avg_coherence'] < self.coherence_threshold:
            validation_results['warnings'].append(
                f"Low average coherence: {coherence_results['avg_coherence']:.3f}"
            )
        logger.info(f"  ✓ Avg coherence: {coherence_results['avg_coherence']:.3f}")
        
        # 4. Domain Assignment Validation
        if self.validate_domains:
            logger.info("[4/8] Validating domain assignments...")
            domain_results = self._validate_domain_assignments(taxonomy, df_clustered)
            validation_results['dimension_metrics']['domain_assignment'] = domain_results
            validation_results['warnings'].extend(domain_results.get('warnings', []))
            logger.info(f"  ✓ Domains validated: {domain_results['num_domains']} domains")
        
        # 5. Cross-Cutting Dimensions Validation
        logger.info("[5/8] Validating cross-cutting dimensions...")
        dimension_results = self._validate_dimensions(df_clustered)
        validation_results['dimension_metrics'].update(dimension_results)
        logger.info(f"  ✓ Dimensions validated")
        
        # 6. Skill Relationships Validation
        if self.validate_relationships:
            logger.info("[6/8] Validating skill relationships...")
            relationship_results = self._validate_relationships(taxonomy)
            validation_results['dimension_metrics']['relationships'] = relationship_results
            logger.info(f"  ✓ Relationships: {relationship_results.get('total_relationships', 0)}")
        
        # 7. Level Consistency
        logger.info("[7/8] Validating level consistency...")
        level_results = self._validate_level_consistency(df_clustered)
        validation_results['metrics']['level_consistency'] = level_results
        validation_results['warnings'].extend(level_results.get('warnings', []))
        
        # 8. Generate Summary
        logger.info("[8/8] Generating validation summary...")
        validation_results['summary'] = self._generate_comprehensive_summary(
            df_clustered, taxonomy, validation_results
        )
        
        # Determine overall validity
        critical_issues = self._check_critical_issues(validation_results)
        if critical_issues:
            validation_results['is_valid'] = False
            validation_results['errors'].extend(critical_issues)
            logger.error(f"  ✗ Validation FAILED: {len(critical_issues)} critical issues")
        else:
            logger.info(f"  ✓ Validation PASSED")
        
        logger.info("\n" + "=" * 80)
        logger.info(f"VALIDATION COMPLETE")
        logger.info(f"  Status: {'✓ PASSED' if validation_results['is_valid'] else '✗ FAILED'}")
        logger.info(f"  Warnings: {len(validation_results['warnings'])}")
        logger.info(f"  Errors: {len(validation_results['errors'])}")
        logger.info("=" * 80)
        
        return validation_results
    
    def _validate_structure(self, taxonomy: Dict) -> Dict:
        """Validate the 5-level hierarchical structure"""
        results = {
            'metrics': {},
            'warnings': [],
            'errors': []
        }
        
        # Check if taxonomy exists and is not empty
        if not taxonomy or not taxonomy.get('children'):
            results['errors'].append("Taxonomy is empty or has no children")
            return results
        
        # Validate depth (should be 5 levels: Root → Domain → Family → Cluster → Group → Skills)
        depth = self._get_max_depth(taxonomy)
        results['metrics']['depth'] = depth
        
        if depth < 3:
            results['warnings'].append(f"Taxonomy is too shallow (depth: {depth}, expected: 4-5)")
        elif depth > 6:
            results['warnings'].append(f"Taxonomy is too deep (depth: {depth}, expected: 4-5)")
        
        # Validate node types
        type_counts = self._count_node_types(taxonomy)
        results['metrics']['node_type_counts'] = type_counts
        
        # Check for expected node types
        expected_types = ['root', 'domain', 'family', 'cluster']
        for expected_type in expected_types:
            if type_counts.get(expected_type, 0) == 0 and expected_type != 'root':
                results['warnings'].append(f"No nodes of type '{expected_type}' found")
        
        # Validate balance
        balance_score = self._calculate_balance_score(taxonomy)
        results['metrics']['balance_score'] = balance_score
        
        if balance_score < 0.5:
            results['warnings'].append(f"Taxonomy is unbalanced (score: {balance_score:.2f})")
        
        # Check for empty nodes
        empty_nodes = self._find_empty_nodes(taxonomy)
        results['metrics']['empty_nodes'] = len(empty_nodes)
        
        if empty_nodes:
            results['warnings'].append(f"Found {len(empty_nodes)} empty nodes")
        
        return results
    
    def _validate_domain_assignments(self, taxonomy: Dict, df: pd.DataFrame) -> Dict:
        """Validate that skills are properly assigned to domains"""
        results = {
            'num_domains': 0,
            'domain_distribution': {},
            'warnings': []
        }
        
        # Count skills per domain
        if 'assigned_domain' in df.columns:
            domain_dist = df['assigned_domain'].value_counts().to_dict()
            results['domain_distribution'] = domain_dist
            results['num_domains'] = len(domain_dist)
            
            # Check if any domain has too few skills
            for domain, count in domain_dist.items():
                if count < 10:
                    results['warnings'].append(
                        f"Domain '{domain}' has very few skills ({count})"
                    )
        
        # Validate domains in taxonomy match configuration
        taxonomy_domains = set()
        if 'children' in taxonomy:
            for child in taxonomy['children']:
                if child.get('type') == 'domain':
                    taxonomy_domains.add(child.get('domain_key', child.get('name')))
        
        results['taxonomy_domains'] = list(taxonomy_domains)
        
        # Check coverage of configured domains
        configured_domains = set(self.domains.keys())
        missing_domains = configured_domains - taxonomy_domains
        
        if missing_domains:
            results['warnings'].append(
                f"Missing domains in taxonomy: {missing_domains}"
            )
        
        return results
    
    def _validate_dimensions(self, df: pd.DataFrame) -> Dict:
        """Validate cross-cutting dimensions"""
        results = {}
        
        # Validate complexity levels
        if 'complexity_level' in df.columns:
            complexity_dist = df['complexity_level'].value_counts().to_dict()
            results['complexity_distribution'] = complexity_dist
            results['avg_complexity'] = float(df['complexity_level'].mean())
            
            # Check if distribution is reasonable
            if len(complexity_dist) == 1:
                results['complexity_warning'] = "All skills have same complexity level"
        
        # Validate transferability
        if 'transferability' in df.columns:
            trans_dist = df['transferability'].value_counts().to_dict()
            results['transferability_distribution'] = trans_dist
            
            # Check for variety
            if len(trans_dist) < 2:
                results['transferability_warning'] = "Limited transferability variety"
        
        # Validate digital intensity
        if 'digital_intensity' in df.columns:
            digital_dist = df['digital_intensity'].value_counts().to_dict()
            results['digital_intensity_distribution'] = digital_dist
            results['avg_digital_intensity'] = float(df['digital_intensity'].mean())
        
        # Validate future readiness
        if 'future_readiness' in df.columns:
            future_dist = df['future_readiness'].value_counts().to_dict()
            results['future_readiness_distribution'] = future_dist
        
        # Validate skill nature
        if 'skill_nature' in df.columns:
            nature_dist = df['skill_nature'].value_counts().to_dict()
            results['skill_nature_distribution'] = nature_dist
        
        return results
    
    def _validate_relationships(self, taxonomy: Dict) -> Dict:
        """Validate skill relationships"""
        results = {
            'total_relationships': 0,
            'skills_with_relationships': 0,
            'avg_relationships_per_skill': 0.0,
            'relationship_types': defaultdict(int)
        }
        
        def count_relationships(node):
            if 'skills' in node:
                for skill in node['skills']:
                    if 'relationships' in skill:
                        results['skills_with_relationships'] += 1
                        
                        for rel_type, rel_list in skill['relationships'].items():
                            if rel_list:
                                count = len(rel_list)
                                results['total_relationships'] += count
                                results['relationship_types'][rel_type] += count
            
            if 'children' in node:
                for child in node['children']:
                    count_relationships(child)
        
        count_relationships(taxonomy)
        
        if results['skills_with_relationships'] > 0:
            results['avg_relationships_per_skill'] = (
                results['total_relationships'] / results['skills_with_relationships']
            )
        
        results['relationship_types'] = dict(results['relationship_types'])
        
        return results
    
    def _validate_cluster_coherence(self, df: pd.DataFrame) -> Dict:
        """Validate cluster coherence metrics"""
        results = {}
        
        if 'cluster_coherence' in df.columns:
            valid_clusters = df[df['cluster_id'] != -1]
            
            if len(valid_clusters) > 0:
                results['avg_coherence'] = float(valid_clusters['cluster_coherence'].mean())
                results['min_coherence'] = float(valid_clusters['cluster_coherence'].min())
                results['max_coherence'] = float(valid_clusters['cluster_coherence'].max())
                
                # Find low coherence clusters
                min_coherence = self.validation_config.get('minimum_cluster_coherence', 0.6)
                low_coherence = valid_clusters[
                    valid_clusters['cluster_coherence'] < min_coherence
                ]
                
                if len(low_coherence) > 0:
                    cluster_ids = low_coherence['cluster_id'].unique()
                    results['low_coherence_clusters'] = cluster_ids.tolist()
            else:
                results['avg_coherence'] = 0.0
        else:
            # Calculate basic coherence
            results['avg_coherence'] = self._calculate_basic_coherence(df)
        
        return results
    
    def _calculate_basic_coherence(self, df: pd.DataFrame) -> float:
        """Calculate basic coherence when not pre-computed"""
        coherence_scores = []
        
        for cluster_id in df['cluster_id'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df[df['cluster_id'] == cluster_id]
            
            # Size-based coherence
            size_score = min(1.0, len(cluster_df) / 50)
            
            # Level consistency
            level_score = 1.0
            if 'level' in cluster_df.columns:
                levels = cluster_df['level'].apply(lambda x: x if isinstance(x, (int, float)) else 3)
                level_std = levels.std()
                level_score = 1.0 / (1.0 + level_std)
            
            coherence = (size_score + level_score) / 2
            coherence_scores.append(coherence)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    def _validate_level_consistency(self, df: pd.DataFrame) -> Dict:
        """Validate level consistency within clusters"""
        results = {
            'warnings': [],
            'cluster_level_variance': {}
        }
        
        if 'level' not in df.columns:
            return results
        
        for cluster_id in df['cluster_id'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df[df['cluster_id'] == cluster_id]
            levels = cluster_df['level'].apply(lambda x: x if isinstance(x, (int, float)) else 3)
            
            level_range = levels.max() - levels.min()
            level_std = levels.std()
            
            results['cluster_level_variance'][int(cluster_id)] = {
                'range': float(level_range),
                'std': float(level_std),
                'mean': float(levels.mean())
            }
            
            if level_range > 3:
                results['warnings'].append(
                    f"Cluster {cluster_id} has high level variance (range: {level_range})"
                )
        
        return results
    
    def _check_coverage(self, taxonomy: Dict, df: pd.DataFrame) -> float:
        """Check what percentage of skills are in the taxonomy"""
        total_skills = len(df)
        covered_skills = len(df[df['cluster_id'] != -1])
        
        if total_skills == 0:
            return 0.0
        
        return covered_skills / total_skills
    
    def _get_max_depth(self, taxonomy: Dict) -> int:
        """Get maximum depth of taxonomy"""
        def get_depth(node, current=0):
            if 'children' not in node or not node['children']:
                return current
            return max(get_depth(child, current + 1) for child in node['children'])
        
        return get_depth(taxonomy)
    
    def _count_node_types(self, taxonomy: Dict) -> Dict[str, int]:
        """Count nodes by type"""
        type_counts = defaultdict(int)
        
        def count(node):
            node_type = node.get('type', 'unknown')
            type_counts[node_type] += 1
            
            if 'children' in node:
                for child in node['children']:
                    count(child)
        
        count(taxonomy)
        return dict(type_counts)
    
    def _calculate_balance_score(self, taxonomy: Dict) -> float:
        """Calculate how balanced the tree is"""
        child_counts = []
        
        def collect_counts(node):
            if 'children' in node and node['children']:
                child_counts.append(len(node['children']))
                for child in node['children']:
                    collect_counts(child)
        
        collect_counts(taxonomy)
        
        if not child_counts:
            return 1.0
        
        mean_children = np.mean(child_counts)
        std_children = np.std(child_counts)
        
        if mean_children == 0:
            return 0.0
        
        cv = std_children / mean_children
        balance_score = 1.0 / (1.0 + cv)
        
        return balance_score
    
    def _find_empty_nodes(self, taxonomy: Dict) -> List[str]:
        """Find nodes with no skills"""
        empty_nodes = []
        
        def traverse(node, path=""):
            node_name = node.get('name', 'unnamed')
            current_path = f"{path}/{node_name}" if path else node_name
            
            has_skills = bool(node.get('skills'))
            has_children = bool(node.get('children'))
            
            if not has_skills and not has_children:
                empty_nodes.append(current_path)
            
            if 'children' in node:
                for child in node['children']:
                    traverse(child, current_path)
        
        traverse(taxonomy)
        return empty_nodes
    
    def _check_critical_issues(self, validation_results: Dict) -> List[str]:
        """Check for critical issues that invalidate the taxonomy"""
        critical = []
        
        # Very low coverage
        coverage = validation_results.get('coverage', 0)
        if coverage < 0.5:
            critical.append(f"Critical: Coverage too low ({coverage:.1%})")
        
        # Very low coherence
        avg_coherence = validation_results.get('metrics', {}).get('avg_coherence', 0)
        if avg_coherence < 0.3:
            critical.append(f"Critical: Coherence too low ({avg_coherence:.2f})")
        
        # Too many errors
        if len(validation_results.get('errors', [])) > 5:
            critical.append("Critical: Too many structural errors")
        
        # Empty taxonomy
        if validation_results.get('metrics', {}).get('node_type_counts', {}).get('domain', 0) == 0:
            critical.append("Critical: No domains in taxonomy")
        
        return critical
    
    def _generate_comprehensive_summary(self, df: pd.DataFrame, taxonomy: Dict, 
                                       validation_results: Dict) -> Dict:
        """Generate comprehensive validation summary"""
        summary = {
            # Basic counts
            'total_skills': len(df),
            'clustered_skills': len(df[df['cluster_id'] != -1]),
            'orphan_skills': len(df[df['cluster_id'] == -1]),
            'num_clusters': df['cluster_id'].nunique() - 1,
            
            # Structure
            'taxonomy_depth': validation_results['metrics'].get('depth', 0),
            'taxonomy_balance': validation_results['metrics'].get('balance_score', 0),
            'total_nodes': self._count_total_nodes(taxonomy),
            
            # Quality metrics
            'coverage': validation_results.get('coverage', 0),
            'avg_coherence': validation_results['metrics'].get('avg_coherence', 0),
            
            # Dimensions
            'num_domains': len(taxonomy.get('children', [])),
            'num_families': self._count_nodes_by_type(taxonomy, 'family'),
            
            # Validation status
            'num_warnings': len(validation_results.get('warnings', [])),
            'num_errors': len(validation_results.get('errors', [])),
            'is_valid': validation_results.get('is_valid', False)
        }
        
        # Add dimension summaries
        if 'dimension_metrics' in validation_results:
            dim_metrics = validation_results['dimension_metrics']
            
            if 'complexity_distribution' in dim_metrics:
                summary['complexity_levels'] = dim_metrics['complexity_distribution']
            
            if 'transferability_distribution' in dim_metrics:
                summary['transferability_types'] = dim_metrics['transferability_distribution']
            
            if 'relationships' in dim_metrics:
                summary['total_relationships'] = dim_metrics['relationships'].get('total_relationships', 0)
        
        return summary
    
    def _count_total_nodes(self, taxonomy: Dict) -> int:
        """Count all nodes"""
        count = 1
        if 'children' in taxonomy:
            for child in taxonomy['children']:
                count += self._count_total_nodes(child)
        return count
    
    def _count_nodes_by_type(self, taxonomy: Dict, node_type: str) -> int:
        """Count nodes of specific type"""
        count = 0
        if taxonomy.get('type') == node_type:
            count = 1
        
        if 'children' in taxonomy:
            for child in taxonomy['children']:
                count += self._count_nodes_by_type(child, node_type)
        
        return count


# Backward compatibility alias
class TaxonomyValidator(MultiDimensionalTaxonomyValidator):
    """Backward compatible class name"""
    pass