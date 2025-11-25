"""
Taxonomy Validator module for validating the quality of generated taxonomies
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class TaxonomyValidator:
    """Validates taxonomy structure and quality metrics"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.coverage_threshold = config['validation']['coverage_threshold']
        self.coherence_threshold = config['validation']['coherence_threshold']
        self.distinctiveness_threshold = config['validation']['distinctiveness_threshold']
        self.max_orphan_skills = config['validation']['max_orphan_skills']
        
        # Multi-factor validation settings
        self.check_level_consistency = config['validation'].get('check_level_consistency', True)
        self.check_context_alignment = config['validation'].get('check_context_alignment', True)
        self.minimum_cluster_coherence = config['validation'].get('minimum_cluster_coherence', 0.6)
        
    def validate(self, taxonomy: Dict, df_clustered: pd.DataFrame) -> Dict:
        """
        Validate the generated taxonomy
        
        Args:
            taxonomy: The generated taxonomy structure
            df_clustered: DataFrame with clustered skills
            
        Returns:
            Dictionary with validation results and metrics
        """
        logger.info("Validating taxonomy structure and quality")
        
        validation_results = {
            'is_valid': True,
            'warnings': [],
            'errors': [],
            'metrics': {}
        }
        
        # 1. Check coverage (how many skills are in the taxonomy)
        coverage = self._check_coverage(taxonomy, df_clustered)
        validation_results['metrics']['coverage'] = coverage
        validation_results['coverage'] = coverage
        
        if coverage < self.coverage_threshold:
            warning = f"Low coverage: {coverage:.1%} (threshold: {self.coverage_threshold:.1%})"
            validation_results['warnings'].append(warning)
            logger.warning(warning)
        
        # 2. Check cluster coherence
        avg_coherence = self._check_cluster_coherence(df_clustered)
        validation_results['metrics']['avg_coherence'] = avg_coherence
        validation_results['avg_coherence'] = avg_coherence
        
        if avg_coherence < self.coherence_threshold:
            warning = f"Low average coherence: {avg_coherence:.3f} (threshold: {self.coherence_threshold:.3f})"
            validation_results['warnings'].append(warning)
            logger.warning(warning)
        
        # 3. Check cluster distinctiveness
        avg_distinctiveness = self._check_cluster_distinctiveness(df_clustered)
        validation_results['metrics']['avg_distinctiveness'] = avg_distinctiveness
        validation_results['avg_distinctiveness'] = avg_distinctiveness
        
        if avg_distinctiveness < self.distinctiveness_threshold:
            warning = f"Low distinctiveness: {avg_distinctiveness:.3f} (threshold: {self.distinctiveness_threshold:.3f})"
            validation_results['warnings'].append(warning)
            logger.warning(warning)
        
        # 4. Check for orphan skills (skills not in any cluster)
        orphan_count = self._check_orphan_skills(df_clustered)
        validation_results['metrics']['orphan_skills'] = orphan_count
        validation_results['orphan_skills'] = orphan_count
        
        if orphan_count > self.max_orphan_skills:
            warning = f"Too many orphan skills: {orphan_count} (max: {self.max_orphan_skills})"
            validation_results['warnings'].append(warning)
            logger.warning(warning)
        
        # 5. Check taxonomy structure
        structure_issues = self._check_taxonomy_structure(taxonomy)
        validation_results['structure_issues'] = structure_issues
        
        if structure_issues:
            validation_results['warnings'].extend(structure_issues)
            for issue in structure_issues:
                logger.warning(f"Structure issue: {issue}")
        
        # 6. Multi-factor validation checks
        if self.check_level_consistency:
            level_issues = self._check_level_consistency(df_clustered)
            if level_issues:
                validation_results['warnings'].extend(level_issues)
                validation_results['level_consistency_issues'] = level_issues
        
        if self.check_context_alignment:
            context_issues = self._check_context_alignment(df_clustered)
            if context_issues:
                validation_results['warnings'].extend(context_issues)
                validation_results['context_alignment_issues'] = context_issues
        
        # 7. Calculate overall validity
        has_critical_issues = (
            coverage < 0.5 or  # Less than 50% coverage
            avg_coherence < 0.3 or  # Very low coherence
            orphan_count > len(df_clustered) * 0.3  # More than 30% orphans
        )
        
        if has_critical_issues:
            validation_results['is_valid'] = False
            validation_results['errors'].append("Taxonomy has critical quality issues")
        
        # 8. Generate summary statistics
        validation_results['summary'] = self._generate_summary(df_clustered, taxonomy)
        
        return validation_results
    
    def _check_coverage(self, taxonomy: Dict, df_clustered: pd.DataFrame) -> float:
        """Check how many skills are covered by the taxonomy"""
        total_skills = len(df_clustered)
        
        # Count skills in taxonomy (excluding noise points)
        covered_skills = len(df_clustered[df_clustered['cluster_id'] != -1])
        
        if total_skills == 0:
            return 0.0
        
        coverage = covered_skills / total_skills
        logger.info(f"Taxonomy coverage: {covered_skills}/{total_skills} = {coverage:.1%}")
        
        return coverage
    
    def _check_cluster_coherence(self, df_clustered: pd.DataFrame) -> float:
        """Check average coherence of clusters"""
        if 'cluster_coherence' not in df_clustered.columns:
            # Calculate basic coherence if not present
            return self._calculate_basic_coherence(df_clustered)
        
        # Get coherence for non-noise clusters
        valid_clusters = df_clustered[df_clustered['cluster_id'] != -1]
        
        if len(valid_clusters) == 0:
            return 0.0
        
        avg_coherence = valid_clusters['cluster_coherence'].mean()
        
        # Check individual clusters
        low_coherence_clusters = []
        for cluster_id in valid_clusters['cluster_id'].unique():
            cluster_coherence = valid_clusters[valid_clusters['cluster_id'] == cluster_id]['cluster_coherence'].iloc[0]
            if cluster_coherence < self.minimum_cluster_coherence:
                low_coherence_clusters.append((cluster_id, cluster_coherence))
        
        if low_coherence_clusters:
            logger.warning(f"Found {len(low_coherence_clusters)} clusters with low coherence")
            for cluster_id, coherence in low_coherence_clusters[:5]:  # Show top 5
                logger.warning(f"  Cluster {cluster_id}: coherence = {coherence:.3f}")
        
        return avg_coherence
    
    def _calculate_basic_coherence(self, df_clustered: pd.DataFrame) -> float:
        """Calculate basic coherence when not pre-computed"""
        coherence_scores = []
        
        for cluster_id in df_clustered['cluster_id'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df_clustered[df_clustered['cluster_id'] == cluster_id]
            
            # Basic coherence based on cluster size and level consistency
            size_score = min(1.0, len(cluster_df) / 50)  # Optimal size around 50
            
            level_score = 1.0
            if 'level' in cluster_df.columns:
                levels = cluster_df['level'].apply(lambda x: x if isinstance(x, (int, float)) else 3)
                level_std = levels.std()
                level_score = 1.0 / (1.0 + level_std)
            
            coherence = (size_score + level_score) / 2
            coherence_scores.append(coherence)
        
        return np.mean(coherence_scores) if coherence_scores else 0.0
    
    def _check_cluster_distinctiveness(self, df_clustered: pd.DataFrame) -> float:
        """Check how distinct clusters are from each other"""
        # For now, use a simple metric based on unique categories per cluster
        distinctiveness_scores = []
        
        unique_clusters = df_clustered[df_clustered['cluster_id'] != -1]['cluster_id'].unique()
        
        for cluster_id in unique_clusters:
            cluster_df = df_clustered[df_clustered['cluster_id'] == cluster_id]
            
            # Check category diversity
            if 'category' in cluster_df.columns:
                n_categories = cluster_df['category'].nunique()
                total_categories = df_clustered['category'].nunique()
                distinctiveness = 1.0 - (n_categories - 1) / max(1, total_categories - 1)
            else:
                distinctiveness = 0.5  # Default if no category info
            
            distinctiveness_scores.append(distinctiveness)
        
        return np.mean(distinctiveness_scores) if distinctiveness_scores else 0.0
    
    def _check_orphan_skills(self, df_clustered: pd.DataFrame) -> int:
        """Count skills not assigned to any cluster (noise points)"""
        orphan_count = (df_clustered['cluster_id'] == -1).sum()
        
        if orphan_count > 0:
            logger.info(f"Found {orphan_count} orphan skills (noise points)")
            
            # Show some examples
            orphans = df_clustered[df_clustered['cluster_id'] == -1]
            if len(orphans) > 0 and 'name' in orphans.columns:
                examples = orphans['name'].head(5).tolist()
                logger.debug(f"Example orphan skills: {examples}")
        
        return orphan_count
    
    def _check_taxonomy_structure(self, taxonomy: Dict) -> List[str]:
        """Check for structural issues in the taxonomy"""
        issues = []
        
        # Check if taxonomy is empty
        if not taxonomy:
            issues.append("Taxonomy is empty")
            return issues
        
        # Check depth
        depth = self._get_taxonomy_depth(taxonomy)
        if depth < 2:
            issues.append(f"Taxonomy is too shallow (depth: {depth})")
        elif depth > 10:
            issues.append(f"Taxonomy is too deep (depth: {depth})")
        
        # Check balance
        balance_score = self._check_taxonomy_balance(taxonomy)
        if balance_score < 0.5:
            issues.append(f"Taxonomy is unbalanced (balance score: {balance_score:.2f})")
        
        # Check for empty nodes
        empty_nodes = self._find_empty_nodes(taxonomy)
        if empty_nodes:
            issues.append(f"Found {len(empty_nodes)} empty nodes")
        
        return issues
    
    def _check_level_consistency(self, df_clustered: pd.DataFrame) -> List[str]:
        """Check if skill levels are consistent within clusters"""
        issues = []
        
        if 'level' not in df_clustered.columns:
            return issues
        
        for cluster_id in df_clustered['cluster_id'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df_clustered[df_clustered['cluster_id'] == cluster_id]
            levels = cluster_df['level'].apply(lambda x: x if isinstance(x, (int, float)) else 3)
            
            level_range = levels.max() - levels.min()
            if level_range > 3:
                issue = f"Cluster {cluster_id} has high level variance (range: {level_range})"
                issues.append(issue)
        
        return issues
    
    def _check_context_alignment(self, df_clustered: pd.DataFrame) -> List[str]:
        """Check if contexts are aligned within clusters"""
        issues = []
        
        if 'context' not in df_clustered.columns:
            return issues
        
        for cluster_id in df_clustered['cluster_id'].unique():
            if cluster_id == -1:
                continue
            
            cluster_df = df_clustered[df_clustered['cluster_id'] == cluster_id]
            contexts = cluster_df['context'].value_counts()
            
            # Check if cluster has mixed contexts
            if len(contexts) > 1:
                dominant_context = contexts.index[0]
                dominant_ratio = contexts.iloc[0] / len(cluster_df)
                
                if dominant_ratio < 0.7:  # Less than 70% same context
                    issue = f"Cluster {cluster_id} has mixed contexts (dominant: {dominant_context} at {dominant_ratio:.1%})"
                    issues.append(issue)
        
        return issues
    
    def _get_taxonomy_depth(self, taxonomy: Dict) -> int:
        """Calculate the depth of the taxonomy tree"""
        def get_depth(node, current_depth=0):
            if isinstance(node, dict):
                if 'children' in node and node['children']:
                    return max(get_depth(child, current_depth + 1) for child in node['children'])
                elif 'subcategories' in node and node['subcategories']:
                    return max(get_depth(subcat, current_depth + 1) for subcat in node['subcategories'])
            return current_depth
        
        return get_depth(taxonomy)
    
    def _check_taxonomy_balance(self, taxonomy: Dict) -> float:
        """Check how balanced the taxonomy tree is"""
        # Simple balance metric based on standard deviation of branch sizes
        def count_children(node):
            if isinstance(node, dict):
                if 'children' in node:
                    return len(node.get('children', []))
                elif 'subcategories' in node:
                    return len(node.get('subcategories', []))
            return 0
        
        child_counts = []
        
        def traverse(node):
            count = count_children(node)
            if count > 0:
                child_counts.append(count)
            
            if isinstance(node, dict):
                for child in node.get('children', []) + node.get('subcategories', []):
                    traverse(child)
        
        traverse(taxonomy)
        
        if not child_counts:
            return 1.0
        
        # Calculate balance score (inverse of coefficient of variation)
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
            if isinstance(node, dict):
                node_name = node.get('name', 'unnamed')
                current_path = f"{path}/{node_name}" if path else node_name
                
                # Check if node has skills
                if not node.get('skills', []) and not node.get('children', []) and not node.get('subcategories', []):
                    empty_nodes.append(current_path)
                
                # Traverse children
                for child in node.get('children', []) + node.get('subcategories', []):
                    traverse(child, current_path)
        
        traverse(taxonomy)
        
        return empty_nodes
    
    def _generate_summary(self, df_clustered: pd.DataFrame, taxonomy: Dict) -> Dict:
        """Generate summary statistics"""
        summary = {
            'total_skills': len(df_clustered),
            'clustered_skills': len(df_clustered[df_clustered['cluster_id'] != -1]),
            'orphan_skills': len(df_clustered[df_clustered['cluster_id'] == -1]),
            'num_clusters': df_clustered['cluster_id'].nunique() - 1,  # Exclude noise
            'taxonomy_depth': self._get_taxonomy_depth(taxonomy),
            'taxonomy_balance': self._check_taxonomy_balance(taxonomy)
        }
        
        # Add level statistics if available
        if 'level' in df_clustered.columns:
            levels = df_clustered['level'].apply(lambda x: x if isinstance(x, (int, float)) else 3)
            summary['level_distribution'] = levels.value_counts().to_dict()
            summary['avg_level'] = levels.mean()
        
        # Add context statistics if available
        if 'context' in df_clustered.columns:
            summary['context_distribution'] = df_clustered['context'].value_counts().to_dict()
        
        return summary
