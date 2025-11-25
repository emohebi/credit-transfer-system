# """
# Taxonomy Builder module for skill taxonomy pipeline
# Constructs hierarchical taxonomy from clustered skills
# """
# import pandas as pd
# import numpy as np
# from typing import List, Dict, Optional, Tuple, Any
# import logging
# from pathlib import Path
# import json
# import networkx as nx
# from collections import defaultdict, Counter
# from tqdm import tqdm
# import pickle

# logger = logging.getLogger(__name__)


# class TaxonomyNode:
#     """Represents a node in the taxonomy tree"""
    
#     def __init__(self, node_id: str, name: str, level: int, node_type: str = "category"):
#         self.id = node_id
#         self.name = name
#         self.level = level
#         self.type = node_type  # category, cluster, skill
#         self.children = []
#         self.parent = None
#         self.skills = []  # Skill IDs belonging to this node
#         self.metadata = {}
        
#     def add_child(self, child_node):
#         """Add a child node"""
#         self.children.append(child_node)
#         child_node.parent = self
        
#     def add_skill(self, skill_id: str):
#         """Add a skill to this node"""
#         self.skills.append(skill_id)
        
#     def to_dict(self) -> Dict:
#         """Convert node to dictionary"""
#         return {
#             'id': self.id,
#             'name': self.name,
#             'level': self.level,
#             'type': self.type,
#             'children': [child.to_dict() for child in self.children],
#             'skills': self.skills,
#             'metadata': self.metadata,
#             'num_skills': len(self.skills),
#             'num_children': len(self.children)
#         }


# class HierarchicalTaxonomyBuilder:
#     """Builds hierarchical taxonomy from clustered skills"""
    
#     def __init__(self, config: Dict):
#         self.config = config
#         self.max_depth = config['hierarchy']['max_depth']
#         self.min_children = config['hierarchy']['min_children']
#         self.max_children = config['hierarchy']['max_children']
#         self.balance_factor = config['hierarchy']['balance_factor']
        
#         self.root = None
#         self.nodes = {}  # node_id -> node mapping
#         self.skill_to_node = {}  # skill_id -> node_id mapping
        
#     def build_taxonomy(self, 
#                        df: pd.DataFrame,
#                        cluster_names: Dict[int, str],
#                        category_hierarchy: Dict) -> TaxonomyNode:
#         """
#         Build hierarchical taxonomy from clustered skills
        
#         Args:
#             df: Dataframe with clustered skills
#             cluster_names: Names for each cluster
#             category_hierarchy: Category hierarchy configuration
            
#         Returns:
#             Root node of taxonomy tree
#         """
#         logger.info("Building hierarchical taxonomy")
        
#         # Create root node
#         self.root = TaxonomyNode("root", "Skill Taxonomy", 0, "root")
#         self.nodes["root"] = self.root
        
#         # Level 1: Main categories
#         self._build_category_level(df, category_hierarchy)
        
#         # Level 2: Subcategories
#         self._build_subcategory_level(df, category_hierarchy)
        
#         # Level 3: Clusters
#         self._build_cluster_level(df, cluster_names)
        
#         # Level 4+: Skill groups and individual skills
#         self._build_skill_levels(df)
        
#         # Optimize structure
#         self._optimize_taxonomy()
        
#         # Add metadata
#         self._add_taxonomy_metadata(df)
        
#         logger.info(f"Taxonomy built with {len(self.nodes)} nodes")
        
#         return self.root
    
#     def _build_category_level(self, df: pd.DataFrame, category_hierarchy: Dict):
#         """Build top-level categories"""
#         categories = df['category'].unique()
        
#         for category in categories:
#             # Get parent category name from hierarchy config
#             parent_name = category_hierarchy.get(category, {}).get('parent', category.title())
            
#             node_id = f"cat_{category.replace(' ', '_')}"
#             node = TaxonomyNode(node_id, parent_name, 1, "category")
            
#             self.root.add_child(node)
#             self.nodes[node_id] = node
            
#             # Add metadata
#             node.metadata['original_category'] = category
#             node.metadata['skill_count'] = len(df[df['category'] == category])
    
#     def _build_subcategory_level(self, df: pd.DataFrame, category_hierarchy: Dict):
#         """Build subcategory level"""
#         for category_node in self.root.children:
#             original_category = category_node.metadata['original_category']
#             subcategories = category_hierarchy.get(original_category, {}).get('subcategories', [])
            
#             if not subcategories:
#                 # Generate subcategories based on clusters
#                 subcategories = self._generate_subcategories(df, original_category)
            
#             for subcat_name in subcategories:
#                 node_id = f"subcat_{original_category}_{subcat_name.replace(' ', '_')}"
#                 node = TaxonomyNode(node_id, subcat_name, 2, "subcategory")
                
#                 category_node.add_child(node)
#                 self.nodes[node_id] = node
    
#     def _build_cluster_level(self, df: pd.DataFrame, cluster_names: Dict[int, str]):
#         """Build cluster level"""
#         for category_node in self.root.children:
#             original_category = category_node.metadata['original_category']
#             category_df = df[df['category'] == original_category]
            
#             # Group clusters by subcategory
#             cluster_assignments = self._assign_clusters_to_subcategories(
#                 category_df, category_node.children, cluster_names
#             )
            
#             for subcat_node, cluster_ids in cluster_assignments.items():
#                 for cluster_id in cluster_ids:
#                     if cluster_id == -1:  # Skip noise
#                         continue
                    
#                     cluster_name = cluster_names.get(cluster_id, f"Cluster {cluster_id}")
#                     node_id = f"cluster_{cluster_id}"
                    
#                     node = TaxonomyNode(node_id, cluster_name, 3, "cluster")
#                     node.metadata['cluster_id'] = cluster_id
                    
#                     subcat_node.add_child(node)
#                     self.nodes[node_id] = node
                    
#                     # Add skills from this cluster
#                     cluster_skills = category_df[category_df['cluster_id'] == cluster_id]
#                     for _, skill in cluster_skills.iterrows():
#                         node.add_skill(skill['skill_id'])
#                         self.skill_to_node[skill['skill_id']] = node_id
    
#     def _build_skill_levels(self, df: pd.DataFrame):
#         """Build additional skill grouping levels if needed"""
#         for node_id, node in self.nodes.items():
#             if node.type == "cluster" and len(node.skills) > self.max_children:
#                 # Create skill groups within large clusters
#                 self._create_skill_groups(node, df)
    
#     def _create_skill_groups(self, cluster_node: TaxonomyNode, df: pd.DataFrame):
#         """Create skill groups within a large cluster"""
#         cluster_skills = df[df['skill_id'].isin(cluster_node.skills)]
        
#         # Group by level or context
#         if 'level' in cluster_skills.columns:
#             groups = cluster_skills.groupby('level')
            
#             for level, group_df in groups:
#                 if len(group_df) >= self.min_children:
#                     group_id = f"group_{cluster_node.id}_{level}"
#                     group_name = f"{cluster_node.name} - {level}"
                    
#                     group_node = TaxonomyNode(group_id, group_name, 4, "skill_group")
#                     cluster_node.add_child(group_node)
#                     self.nodes[group_id] = group_node
                    
#                     # Move skills to group
#                     for skill_id in group_df['skill_id']:
#                         group_node.add_skill(skill_id)
#                         cluster_node.skills.remove(skill_id)
#                         self.skill_to_node[skill_id] = group_id
    
#     def _generate_subcategories(self, df: pd.DataFrame, category: str) -> List[str]:
#         """Generate subcategories based on data patterns"""
#         category_df = df[df['category'] == category]
        
#         # Use keywords to generate subcategories
#         all_keywords = []
#         for keywords in category_df['keywords']:
#             all_keywords.extend(keywords)
        
#         # Get top keyword themes
#         keyword_counts = Counter(all_keywords)
#         top_keywords = [k for k, _ in keyword_counts.most_common(20)]
        
#         # Group similar keywords
#         subcategories = self._group_keywords_into_themes(top_keywords)
        
#         return subcategories[:5]  # Limit to 5 subcategories
    
#     def _group_keywords_into_themes(self, keywords: List[str]) -> List[str]:
#         """Group keywords into thematic subcategories"""
#         # Simple grouping based on common patterns
#         themes = defaultdict(list)
        
#         theme_patterns = {
#             'Management': ['management', 'leadership', 'planning', 'strategy'],
#             'Technical': ['technical', 'engineering', 'development', 'programming'],
#             'Communication': ['communication', 'presentation', 'writing', 'speaking'],
#             'Analysis': ['analysis', 'research', 'data', 'evaluation'],
#             'Operations': ['operations', 'process', 'quality', 'safety']
#         }
        
#         for keyword in keywords:
#             assigned = False
#             for theme, patterns in theme_patterns.items():
#                 if any(pattern in keyword.lower() for pattern in patterns):
#                     themes[theme].append(keyword)
#                     assigned = True
#                     break
            
#             if not assigned:
#                 themes['General'].append(keyword)
        
#         return list(themes.keys())
    
#     def _assign_clusters_to_subcategories(self, 
#                                          df: pd.DataFrame,
#                                          subcategory_nodes: List[TaxonomyNode],
#                                          cluster_names: Dict[int, str]) -> Dict:
#         """Assign clusters to appropriate subcategories"""
#         assignments = defaultdict(list)
        
#         cluster_ids = df['cluster_id'].unique()
        
#         for cluster_id in cluster_ids:
#             if cluster_id == -1:
#                 continue
            
#             # Find best matching subcategory
#             cluster_df = df[df['cluster_id'] == cluster_id]
#             cluster_keywords = []
#             for keywords in cluster_df['keywords']:
#                 cluster_keywords.extend(keywords)
            
#             # Simple assignment: use first subcategory or create distribution
#             if len(subcategory_nodes) > 0:
#                 # Distribute evenly for now (can be improved with semantic matching)
#                 subcat_idx = cluster_id % len(subcategory_nodes)
#                 assignments[subcategory_nodes[subcat_idx]].append(cluster_id)
#             else:
#                 # If no subcategories, assign to parent
#                 assignments[subcategory_nodes[0] if subcategory_nodes else None].append(cluster_id)
        
#         return assignments
    
#     def _optimize_taxonomy(self):
#         """Optimize taxonomy structure for balance and usability"""
#         logger.info("Optimizing taxonomy structure")
        
#         # Balance tree
#         self._balance_tree()
        
#         # Merge small nodes
#         self._merge_small_nodes()
        
#         # Split large nodes
#         self._split_large_nodes()
        
#         # Remove empty nodes
#         self._remove_empty_nodes()
    
#     def _balance_tree(self):
#         """Balance the taxonomy tree"""
#         # Calculate balance metrics
#         depths = self._calculate_depths(self.root)
        
#         if max(depths) - min(depths) > 2:
#             logger.info(f"Tree imbalanced: depth range {min(depths)}-{max(depths)}")
#             # Rebalancing logic here
    
#     def _merge_small_nodes(self):
#         """Merge nodes with too few children"""
#         nodes_to_merge = []
        
#         for node_id, node in self.nodes.items():
#             if node.level > 0 and len(node.children) < self.min_children and len(node.children) > 0:
#                 nodes_to_merge.append(node)
        
#         for node in nodes_to_merge:
#             if node.parent and node.parent != self.root:
#                 # Merge with sibling or parent
#                 logger.debug(f"Merging small node: {node.name}")
#                 self._merge_node_with_sibling(node)
    
#     def _split_large_nodes(self):
#         """Split nodes with too many children"""
#         nodes_to_split = []
        
#         for node_id, node in self.nodes.items():
#             if len(node.children) > self.max_children:
#                 nodes_to_split.append(node)
        
#         for node in nodes_to_split:
#             logger.debug(f"Splitting large node: {node.name}")
#             self._split_node(node)
    
#     def _remove_empty_nodes(self):
#         """Remove nodes with no skills or children"""
#         nodes_to_remove = []
        
#         for node_id, node in list(self.nodes.items()):
#             if node != self.root and len(node.children) == 0 and len(node.skills) == 0:
#                 nodes_to_remove.append(node_id)
        
#         for node_id in nodes_to_remove:
#             node = self.nodes[node_id]
#             if node.parent:
#                 node.parent.children.remove(node)
#             del self.nodes[node_id]
#             logger.debug(f"Removed empty node: {node.name}")
    
#     def _merge_node_with_sibling(self, node: TaxonomyNode):
#         """Merge a node with its sibling"""
#         if not node.parent:
#             return
        
#         siblings = [n for n in node.parent.children if n != node]
#         if siblings:
#             # Merge with first sibling
#             target = siblings[0]
            
#             # Move children
#             for child in node.children:
#                 target.add_child(child)
            
#             # Move skills
#             for skill in node.skills:
#                 target.add_skill(skill)
#                 self.skill_to_node[skill] = target.id
            
#             # Remove node
#             node.parent.children.remove(node)
#             del self.nodes[node.id]
    
#     def _split_node(self, node: TaxonomyNode):
#         """Split a node with too many children"""
#         if len(node.children) <= self.max_children:
#             return
        
#         # Create intermediate grouping nodes
#         num_groups = (len(node.children) + self.max_children - 1) // self.max_children
#         groups = []
        
#         for i in range(num_groups):
#             group_id = f"{node.id}_group_{i}"
#             group_name = f"{node.name} Group {i+1}"
#             group_node = TaxonomyNode(group_id, group_name, node.level + 1, "group")
#             groups.append(group_node)
#             self.nodes[group_id] = group_node
        
#         # Distribute children among groups
#         children_per_group = len(node.children) // num_groups
        
#         for i, child in enumerate(node.children[:]):
#             group_idx = min(i // children_per_group, num_groups - 1)
#             groups[group_idx].add_child(child)
#             node.children.remove(child)
        
#         # Add groups as new children
#         for group in groups:
#             node.add_child(group)
    
#     def _calculate_depths(self, node: TaxonomyNode) -> List[int]:
#         """Calculate all leaf depths in the tree"""
#         if len(node.children) == 0:
#             return [node.level]
        
#         depths = []
#         for child in node.children:
#             depths.extend(self._calculate_depths(child))
        
#         return depths
    
#     def _add_taxonomy_metadata(self, df: pd.DataFrame):
#         """Add metadata to taxonomy nodes"""
#         for node_id, node in self.nodes.items():
#             if node.type in ["cluster", "skill_group"]:
#                 # Add statistics
#                 node_skills = df[df['skill_id'].isin(node.skills)]
                
#                 if len(node_skills) > 0:
#                     node.metadata['avg_confidence'] = node_skills['confidence'].mean()
#                     node.metadata['skill_levels'] = node_skills['level'].value_counts().to_dict()
#                     node.metadata['skill_contexts'] = node_skills['context'].value_counts().to_dict()
                    
#                     # Top keywords
#                     all_keywords = []
#                     for keywords in node_skills['keywords']:
#                         all_keywords.extend(keywords)
#                     keyword_counts = Counter(all_keywords)
#                     node.metadata['top_keywords'] = [k for k, _ in keyword_counts.most_common(10)]
    
#     def export_taxonomy(self, output_path: Path):
#         """Export taxonomy to various formats"""
#         output_path.mkdir(parents=True, exist_ok=True)
        
#         # Export as JSON
#         taxonomy_dict = self.root.to_dict()
#         with open(output_path / "taxonomy.json", 'w') as f:
#             json.dump(taxonomy_dict, f, indent=2)
        
#         # Export as pickle for Python use
#         with open(output_path / "taxonomy.pkl", 'wb') as f:
#             pickle.dump(self.root, f)
        
#         # Export flat structure as CSV
#         flat_taxonomy = self._flatten_taxonomy()
#         flat_df = pd.DataFrame(flat_taxonomy)
#         flat_df.to_csv(output_path / "taxonomy_flat.csv", index=False)
        
#         logger.info(f"Taxonomy exported to {output_path}")
    
#     def _flatten_taxonomy(self) -> List[Dict]:
#         """Flatten taxonomy to a list of records"""
#         flat = []
        
#         def traverse(node: TaxonomyNode, path: str = ""):
#             current_path = f"{path}/{node.name}" if path else node.name
            
#             record = {
#                 'node_id': node.id,
#                 'name': node.name,
#                 'path': current_path,
#                 'level': node.level,
#                 'type': node.type,
#                 'parent_id': node.parent.id if node.parent else None,
#                 'num_children': len(node.children),
#                 'num_skills': len(node.skills),
#                 'skills': ','.join(node.skills[:10])  # Sample of skills
#             }
            
#             # Add metadata
#             for key, value in node.metadata.items():
#                 if not isinstance(value, (list, dict)):
#                     record[f'meta_{key}'] = value
            
#             flat.append(record)
            
#             for child in node.children:
#                 traverse(child, current_path)
        
#         traverse(self.root)
#         return flat
    
#     def get_statistics(self) -> Dict:
#         """Get taxonomy statistics"""
#         stats = {
#             'total_nodes': len(self.nodes),
#             'max_depth': max(self._calculate_depths(self.root)),
#             'total_categories': sum(1 for n in self.nodes.values() if n.type == 'category'),
#             'total_clusters': sum(1 for n in self.nodes.values() if n.type == 'cluster'),
#             'total_skills': sum(len(n.skills) for n in self.nodes.values()),
#             'avg_children_per_node': np.mean([len(n.children) for n in self.nodes.values()]),
#             'avg_skills_per_leaf': np.mean([len(n.skills) for n in self.nodes.values() if len(n.children) == 0])
#         }
        
#         return stats
