"""
Taxonomy Hierarchy Builder module for creating hierarchical skill taxonomies
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class TaxonomyBuilder:
    """Builds hierarchical taxonomy from clustered skills"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_depth = config['hierarchy']['max_depth']
        self.min_children = config['hierarchy']['min_children']
        self.max_children = config['hierarchy']['max_children']
        self.balance_factor = config['hierarchy']['balance_factor']
        
        # Multi-factor hierarchy settings
        self.group_by_level_first = config['hierarchy'].get('group_by_level_first', True)
        self.max_level_span_per_node = config['hierarchy'].get('max_level_span_per_node', 2)
        self.preserve_context_groups = config['hierarchy'].get('preserve_context_groups', True)
        
        # Category hierarchy from config
        self.category_hierarchy = config.get('categories', {})
        
    def build_hierarchy(self, df_clustered: pd.DataFrame) -> Dict:
        """
        Build hierarchical taxonomy from clustered skills
        
        Args:
            df_clustered: DataFrame with clustered skills
            
        Returns:
            Hierarchical taxonomy structure
        """
        logger.info("Building hierarchical taxonomy structure")
        
        # Filter out noise points
        df_valid = df_clustered[df_clustered['cluster_id'] != -1].copy()
        
        if len(df_valid) == 0:
            logger.warning("No valid clusters found, returning empty taxonomy")
            return {"name": "Skills Taxonomy", "children": []}
        
        # Build hierarchy based on configuration
        if self.group_by_level_first and 'level' in df_valid.columns:
            taxonomy = self._build_level_based_hierarchy(df_valid)
        else:
            taxonomy = self._build_category_based_hierarchy(df_valid)
        
        # Post-process to ensure balance
        taxonomy = self._balance_taxonomy(taxonomy)
        
        # Add metadata
        taxonomy = self._add_taxonomy_metadata(taxonomy, df_valid)
        
        logger.info(f"Built taxonomy with {self._count_nodes(taxonomy)} nodes")
        
        return taxonomy
    
    def _build_level_based_hierarchy(self, df: pd.DataFrame) -> Dict:
        """Build hierarchy grouped by skill levels first"""
        logger.info("Building level-based hierarchy")
        
        root = {
            "name": "Skills Taxonomy",
            "type": "root",
            "children": []
        }
        
        # Group skills by level ranges
        level_groups = {
            "Foundation (Levels 1-2)": (1, 2),
            "Intermediate (Levels 3-4)": (3, 4),
            "Advanced (Levels 5-6)": (5, 6),
            "Expert (Level 7)": (7, 7)
        }
        
        for level_name, (min_level, max_level) in level_groups.items():
            # Get skills in this level range
            level_skills = df[
                df['level'].apply(lambda x: min_level <= self._extract_level(x) <= max_level)
            ]
            
            if len(level_skills) == 0:
                continue
            
            level_node = {
                "name": level_name,
                "type": "level_group",
                "level_range": [min_level, max_level],
                "children": []
            }
            
            # Within each level group, organize by category
            if 'category' in level_skills.columns:
                categories = level_skills['category'].unique()
                
                for category in sorted(categories):
                    cat_skills = level_skills[level_skills['category'] == category]
                    
                    if len(cat_skills) == 0:
                        continue
                    
                    category_node = {
                        "name": self._format_category_name(category),
                        "type": "category",
                        "category": category,
                        "children": []
                    }
                    
                    # Add clusters within this category
                    clusters = cat_skills['cluster_id'].unique()
                    
                    for cluster_id in sorted(clusters):
                        cluster_skills = cat_skills[cat_skills['cluster_id'] == cluster_id]
                        
                        if len(cluster_skills) < self.min_children and len(clusters) > 1:
                            continue  # Skip very small clusters
                        
                        cluster_node = self._create_cluster_node(cluster_id, cluster_skills)
                        category_node['children'].append(cluster_node)
                    
                    if category_node['children']:
                        level_node['children'].append(category_node)
            else:
                # No categories, add clusters directly
                clusters = level_skills['cluster_id'].unique()
                
                for cluster_id in sorted(clusters):
                    cluster_skills = level_skills[level_skills['cluster_id'] == cluster_id]
                    cluster_node = self._create_cluster_node(cluster_id, cluster_skills)
                    level_node['children'].append(cluster_node)
            
            if level_node['children']:
                root['children'].append(level_node)
        
        return root
    
    def _build_category_based_hierarchy(self, df: pd.DataFrame) -> Dict:
        """Build hierarchy grouped by categories first"""
        logger.info("Building category-based hierarchy")
        
        root = {
            "name": "Skills Taxonomy",
            "type": "root",
            "children": []
        }
        
        # Group by categories
        if 'category' in df.columns:
            categories = df['category'].unique()
            
            for category in sorted(categories):
                cat_skills = df[df['category'] == category]
                
                if len(cat_skills) == 0:
                    continue
                
                # Create category node with hierarchy from config
                category_info = self.category_hierarchy.get(category, {})
                parent_name = category_info.get('parent', self._format_category_name(category))
                
                category_node = {
                    "name": parent_name,
                    "type": "category",
                    "category": category,
                    "children": []
                }
                
                # Check for subcategories
                if 'subcategories' in category_info:
                    for subcategory in category_info['subcategories']:
                        subcat_node = {
                            "name": subcategory,
                            "type": "subcategory",
                            "children": []
                        }
                        category_node['children'].append(subcat_node)
                
                # Add clusters to category or subcategories
                clusters = cat_skills['cluster_id'].unique()
                
                for cluster_id in sorted(clusters):
                    cluster_skills = cat_skills[cat_skills['cluster_id'] == cluster_id]
                    cluster_node = self._create_cluster_node(cluster_id, cluster_skills)
                    
                    # If we have subcategories, try to assign cluster to best matching one
                    if category_node['children'] and all(c.get('type') == 'subcategory' for c in category_node['children']):
                        best_subcat = self._find_best_subcategory(cluster_node, category_node['children'])
                        best_subcat['children'].append(cluster_node)
                    else:
                        category_node['children'].append(cluster_node)
                
                if category_node['children']:
                    root['children'].append(category_node)
        else:
            # No categories, add clusters directly to root
            clusters = df['cluster_id'].unique()
            
            for cluster_id in sorted(clusters):
                cluster_skills = df[df['cluster_id'] == cluster_id]
                cluster_node = self._create_cluster_node(cluster_id, cluster_skills)
                root['children'].append(cluster_node)
        
        return root
    
    def _create_cluster_node(self, cluster_id: int, cluster_df: pd.DataFrame) -> Dict:
        """Create a node for a skill cluster"""
        # Determine cluster name
        cluster_name = f"Cluster {cluster_id}"
        
        # Try to create a better name from common keywords
        if 'keywords' in cluster_df.columns:
            all_keywords = []
            for keywords in cluster_df['keywords']:
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
                elif isinstance(keywords, str):
                    all_keywords.extend(keywords.split())
            
            if all_keywords:
                from collections import Counter
                common_keywords = Counter(all_keywords).most_common(3)
                if common_keywords:
                    cluster_name = " & ".join([k for k, _ in common_keywords[:2]])
                    cluster_name = cluster_name.title()
        
        # Get cluster statistics
        cluster_stats = self._calculate_cluster_stats(cluster_df)
        
        # Create skills list
        skills = []
        for _, skill in cluster_df.iterrows():
            skill_dict = {
                "id": skill.get('skill_id', ''),
                "name": skill.get('name', ''),
                "description": skill.get('description', ''),
                "level": self._extract_level(skill.get('level', 3)),
                "context": skill.get('context', 'hybrid'),
                "confidence": skill.get('confidence', 0.5)
            }
            skills.append(skill_dict)
        
        # Sort skills by level and name
        skills.sort(key=lambda x: (x['level'], x['name']))
        
        cluster_node = {
            "name": cluster_name,
            "type": "cluster",
            "cluster_id": int(cluster_id),
            "size": len(cluster_df),
            "skills": skills,
            "statistics": cluster_stats,
            "children": []  # Can add sub-clusters if needed
        }
        
        # If cluster is very large, consider splitting into sub-groups
        if len(skills) > self.max_children:
            cluster_node = self._split_large_cluster(cluster_node, cluster_df)
        
        return cluster_node
    
    def _split_large_cluster(self, cluster_node: Dict, cluster_df: pd.DataFrame) -> Dict:
        """Split large clusters into sub-groups"""
        skills = cluster_node['skills']
        
        # Group by level if possible
        if 'level' in cluster_df.columns:
            level_groups = defaultdict(list)
            for skill in skills:
                level_groups[skill['level']].append(skill)
            
            if len(level_groups) > 1:
                # Create sub-nodes for each level
                cluster_node['skills'] = []  # Move skills to sub-nodes
                cluster_node['children'] = []
                
                for level, level_skills in sorted(level_groups.items()):
                    sub_node = {
                        "name": f"Level {level} Skills",
                        "type": "level_subgroup",
                        "level": level,
                        "size": len(level_skills),
                        "skills": level_skills,
                        "children": []
                    }
                    cluster_node['children'].append(sub_node)
        
        return cluster_node
    
    def _calculate_cluster_stats(self, cluster_df: pd.DataFrame) -> Dict:
        """Calculate statistics for a cluster"""
        stats = {
            "size": len(cluster_df),
            "avg_confidence": float(cluster_df['confidence'].mean()) if 'confidence' in cluster_df.columns else 0.0
        }
        
        # Level statistics
        if 'level' in cluster_df.columns:
            levels = cluster_df['level'].apply(self._extract_level)
            stats['avg_level'] = float(levels.mean())
            stats['level_range'] = [int(levels.min()), int(levels.max())]
        
        # Context distribution
        if 'context' in cluster_df.columns:
            context_counts = cluster_df['context'].value_counts().to_dict()
            stats['context_distribution'] = context_counts
            stats['dominant_context'] = cluster_df['context'].mode()[0] if len(cluster_df) > 0 else 'hybrid'
        
        # Category distribution
        if 'category' in cluster_df.columns:
            stats['categories'] = cluster_df['category'].unique().tolist()
        
        return stats
    
    def _extract_level(self, level) -> int:
        """Extract numeric level value"""
        if hasattr(level, 'value'):
            return level.value
        try:
            return int(level)
        except:
            return 3  # Default
    
    def _format_category_name(self, category: str) -> str:
        """Format category name for display"""
        if isinstance(category, str):
            return category.replace('_', ' ').title()
        return str(category)
    
    def _find_best_subcategory(self, cluster_node: Dict, subcategories: List[Dict]) -> Dict:
        """Find the best matching subcategory for a cluster"""
        # For now, distribute evenly or based on cluster name matching
        cluster_name_lower = cluster_node['name'].lower()
        
        for subcat in subcategories:
            subcat_name_lower = subcat['name'].lower()
            # Simple keyword matching
            if any(word in cluster_name_lower for word in subcat_name_lower.split()):
                return subcat
        
        # Default to subcategory with fewest children (balance)
        return min(subcategories, key=lambda x: len(x.get('children', [])))
    
    def _balance_taxonomy(self, taxonomy: Dict) -> Dict:
        """Balance the taxonomy tree to avoid too deep or too shallow structures"""
        
        def rebalance_node(node, depth=0):
            if depth >= self.max_depth:
                # Flatten if too deep
                return self._flatten_node(node)
            
            if 'children' in node:
                # Check if node has too many children
                if len(node['children']) > self.max_children:
                    node = self._group_children(node)
                
                # Recursively balance children
                node['children'] = [rebalance_node(child, depth + 1) for child in node['children']]
                
                # Remove empty children
                node['children'] = [c for c in node['children'] if c.get('children') or c.get('skills')]
            
            return node
        
        return rebalance_node(taxonomy)
    
    def _flatten_node(self, node: Dict) -> Dict:
        """Flatten a node if the tree is too deep"""
        if 'children' not in node:
            return node
        
        # Collect all skills from children
        all_skills = []
        
        def collect_skills(n):
            if 'skills' in n:
                all_skills.extend(n['skills'])
            if 'children' in n:
                for child in n['children']:
                    collect_skills(child)
        
        collect_skills(node)
        
        # Create flattened node
        flattened = {
            "name": node['name'],
            "type": node.get('type', 'flattened'),
            "skills": all_skills,
            "children": []
        }
        
        return flattened
    
    def _group_children(self, node: Dict) -> Dict:
        """Group children if a node has too many"""
        if len(node['children']) <= self.max_children:
            return node
        
        # Group children into batches
        batch_size = self.max_children
        grouped_children = []
        
        for i in range(0, len(node['children']), batch_size):
            batch = node['children'][i:i + batch_size]
            
            if len(batch) == 1:
                grouped_children.append(batch[0])
            else:
                group_node = {
                    "name": f"Group {i // batch_size + 1}",
                    "type": "group",
                    "children": batch
                }
                grouped_children.append(group_node)
        
        node['children'] = grouped_children
        return node
    
    def _add_taxonomy_metadata(self, taxonomy: Dict, df: pd.DataFrame) -> Dict:
        """Add metadata to the taxonomy"""
        taxonomy['metadata'] = {
            "total_skills": len(df),
            "total_clusters": df['cluster_id'].nunique(),
            "depth": self._count_depth(taxonomy),
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        # Add configuration used
        taxonomy['metadata']['config'] = {
            "max_depth": self.max_depth,
            "min_children": self.min_children,
            "max_children": self.max_children,
            "group_by_level": self.group_by_level_first
        }
        
        return taxonomy
    
    def _count_nodes(self, node: Dict) -> int:
        """Count total nodes in taxonomy"""
        count = 1
        if 'children' in node:
            for child in node['children']:
                count += self._count_nodes(child)
        return count
    
    def _count_depth(self, node: Dict, current_depth=0) -> int:
        """Calculate maximum depth of taxonomy"""
        if 'children' not in node or not node['children']:
            return current_depth
        
        max_child_depth = 0
        for child in node['children']:
            child_depth = self._count_depth(child, current_depth + 1)
            max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def export_taxonomy(self, taxonomy: Dict, filepath: str, format: str = 'json'):
        """Export taxonomy to file"""
        if format == 'json':
            with open(filepath, 'w') as f:
                json.dump(taxonomy, f, indent=2)
            logger.info(f"Exported taxonomy to {filepath}")
        elif format == 'txt':
            self._export_as_text(taxonomy, filepath)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_as_text(self, taxonomy: Dict, filepath: str):
        """Export taxonomy as indented text"""
        lines = []
        
        def traverse(node, depth=0):
            indent = "  " * depth
            name = node.get('name', 'Unnamed')
            node_type = node.get('type', '')
            
            # Add node info
            if 'skills' in node and node['skills']:
                lines.append(f"{indent}{name} ({len(node['skills'])} skills)")
                if depth < 3:  # Only show skills for first few levels
                    for skill in node['skills'][:3]:  # Show first 3 skills
                        lines.append(f"{indent}  - {skill['name']} (Level {skill['level']})")
                    if len(node['skills']) > 3:
                        lines.append(f"{indent}  ... and {len(node['skills']) - 3} more")
            else:
                lines.append(f"{indent}{name}")
            
            # Traverse children
            if 'children' in node:
                for child in node['children']:
                    traverse(child, depth + 1)
        
        traverse(taxonomy)
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Exported taxonomy as text to {filepath}")
