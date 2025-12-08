"""
Multi-Dimensional Taxonomy Hierarchy Builder
Builds hierarchy: Domain → Family → Group (by Level) → Atomic Skills
Includes alternative titles from deduplication
Includes all_related_kw and all_related_codes aggregated from duplicates
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import json
from sklearn.metrics.pairwise import cosine_similarity
from config.settings import (
    SKILL_DOMAINS,
    SKILL_FAMILIES,
    TRAINING_PACKAGES,
    COMPLEXITY_LEVELS,
    TRANSFERABILITY_TYPES,
    DIGITAL_INTENSITY_LEVELS,
    FUTURE_READINESS,
    SKILL_NATURE_TYPES,
    CONTEXT_TYPES,
    HIERARCHY_CONFIG as DEFAULT_HIERARCHY_CONFIG
)

logger = logging.getLogger(__name__)


class MultiDimensionalTaxonomyBuilder:
    """
    Builds multi-dimensional hierarchical taxonomy
    
    Structure:
    - Level 0: Root
    - Level 1: Domains (15 major skill domains)
    - Level 2: Families (90+ skill families)
    - Level 3: Groups (organized by skill level within family)
    - Level 4: Atomic Skills (individual skills with metadata)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.hierarchy_config = config.get('hierarchy', {})
        self.taxonomy_config = config.get('taxonomy', {})
        
        # Load taxonomy definitions
        self.domains = SKILL_DOMAINS
        self.families = SKILL_FAMILIES
        self.complexity_levels = COMPLEXITY_LEVELS
        self.transferability_types = TRANSFERABILITY_TYPES
        self.digital_intensity_levels = DIGITAL_INTENSITY_LEVELS
        self.future_readiness = FUTURE_READINESS
        self.skill_nature_types = SKILL_NATURE_TYPES
        self.context_types = CONTEXT_TYPES
        
        # Settings
        self.max_depth = self.hierarchy_config.get('max_depth', 4)
        self.min_children = self.hierarchy_config.get('min_children', 2)
        self.max_children = self.hierarchy_config.get('max_children', 25)
        
        # Feature flags
        self.enable_transferability = self.hierarchy_config.get('enable_transferability_scoring', True)
        self.enable_digital_intensity = self.hierarchy_config.get('enable_digital_intensity_scoring', True)
        self.enable_future_readiness = self.hierarchy_config.get('enable_future_readiness_scoring', True)
        self.enable_skill_nature = self.hierarchy_config.get('enable_skill_nature_classification', True)
        self.build_relationships = self.hierarchy_config.get('build_skill_relationships', True)
        
        self.skill_embeddings = None
        
        logger.info(f"Initialized Taxonomy Builder")
        logger.info(f"  Domains: {len(self.domains)}")
        logger.info(f"  Families: {len(self.families)}")
        logger.info(f"  Hierarchy: Domain → Family → Group → Skills")
    
    def build_hierarchy(self, df_assigned: pd.DataFrame, 
                       embeddings: Optional[np.ndarray] = None,
                       embedding_model=None) -> Dict:
        """
        Build the taxonomy hierarchy from family-assigned skills
        
        Args:
            df_assigned: DataFrame with 'assigned_family' and 'assigned_domain' columns
            embeddings: Optional skill embeddings for relationship building
            embedding_model: Optional embedding model
            
        Returns:
            Hierarchical taxonomy dictionary
        """
        logger.info("=" * 80)
        logger.info("BUILDING TAXONOMY HIERARCHY")
        logger.info("=" * 80)
        
        self.skill_embeddings = embeddings
        
        # Filter to assigned skills only
        df_valid = df_assigned[df_assigned['assigned_family'].notna()].copy()
        
        if len(df_valid) == 0:
            logger.warning("No skills assigned to families, returning empty taxonomy")
            return self._create_empty_taxonomy()
        
        logger.info(f"Building taxonomy from {len(df_valid)} assigned skills")
        logger.info(f"Families with skills: {df_valid['assigned_family'].nunique()}")
        logger.info(f"Domains with skills: {df_valid['assigned_domain'].nunique()}")
        
        # Step 1: Calculate cross-cutting dimensions
        logger.info("\n[Step 1] Calculating cross-cutting dimensions...")
        df_enriched = self._calculate_cross_cutting_dimensions(df_assigned)
        
        # Step 2: Build the 4-level hierarchy
        logger.info("\n[Step 2] Building 4-level hierarchy...")
        taxonomy = self._build_four_level_hierarchy(df_enriched)
        
        # Step 3: Build skill relationships
        if self.build_relationships and self.skill_embeddings is not None:
            logger.info("\n[Step 3] Building skill relationships...")
            taxonomy = self._add_skill_relationships(taxonomy, df_enriched, embeddings)
        
        # Step 4: Add metadata
        logger.info("\n[Step 4] Adding metadata and statistics...")
        taxonomy = self._add_comprehensive_metadata(taxonomy, df_enriched)
        
        # Step 5: Balance taxonomy
        logger.info("\n[Step 5] Balancing taxonomy...")
        taxonomy = self._balance_taxonomy(taxonomy)
        
        logger.info("\n" + "=" * 80)
        logger.info(f"✓ Taxonomy built successfully!")
        logger.info(f"  Total nodes: {self._count_nodes(taxonomy)}")
        logger.info(f"  Depth: {self._get_taxonomy_depth(taxonomy)}")
        logger.info(f"  Domains: {len(taxonomy.get('children', []))}")
        logger.info("=" * 80)
        
        return taxonomy
    
    def _calculate_cross_cutting_dimensions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all cross-cutting dimensions for skills"""
        df_enriched = df.copy()
        
        # 1. Complexity Level (map from SFIA level)
        df_enriched['complexity_level'] = df_enriched['level'].apply(self._map_to_complexity_level)
        
        # 2. Transferability Index
        if self.enable_transferability:
            df_enriched['transferability'] = df_enriched.apply(
                lambda row: self._calculate_transferability(row), axis=1
            )
        
        # 3. Digital Intensity
        if self.enable_digital_intensity:
            df_enriched['digital_intensity'] = df_enriched.apply(
                lambda row: self._calculate_digital_intensity(row), axis=1
            )
        
        # 4. Future-Readiness
        if self.enable_future_readiness:
            df_enriched['future_readiness'] = df_enriched.apply(
                lambda row: self._calculate_future_readiness(row), axis=1
            )
        
        # 5. Skill Nature
        if self.enable_skill_nature:
            df_enriched['skill_nature'] = df_enriched.apply(
                lambda row: self._classify_skill_nature(row), axis=1
            )
        
        logger.info(f"  ✓ Calculated cross-cutting dimensions for {len(df_enriched)} skills")
        
        return df_enriched
    
    def _map_to_complexity_level(self, level) -> int:
        """Map SFIA level (1-7) to complexity level (1-5)"""
        if hasattr(level, 'value'):
            level = level.value
        try:
            level = int(level)
        except:
            level = 3
        return level
        
        # if level <= 2:
        #     return 1  # Foundational
        # elif level <= 3:
        #     return 2  # Basic
        # elif level <= 4:
        #     return 3  # Intermediate
        # elif level <= 5:
        #     return 4  # Advanced
        # else:
        #     return 5  # Expert
    
    def _calculate_transferability(self, row: pd.Series) -> str:
        """Calculate transferability index for a skill"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        scores = {}
        for trans_type, trans_info in self.transferability_types.items():
            keywords = trans_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[trans_type] = score
        
        if not scores:
            return 'sector_specific'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'sector_specific'
    
    def _calculate_digital_intensity(self, row: pd.Series) -> int:
        """Calculate digital intensity level (0-4)"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        high_digital_keywords = ['software', 'programming', 'code', 'algorithm', 'digital', 'data', 'ai', 'machine learning']
        medium_digital_keywords = ['computer', 'email', 'spreadsheet', 'database', 'online', 'web']
        low_digital_keywords = ['technology', 'electronic', 'automated']
        
        if any(kw in text for kw in ['ai', 'artificial intelligence', 'machine learning', 'blockchain', 'quantum']):
            return 4
        
        high_count = sum(1 for kw in high_digital_keywords if kw in text)
        if high_count >= 2:
            return 3
        
        medium_count = sum(1 for kw in medium_digital_keywords if kw in text)
        if medium_count >= 2:
            return 2
        
        if any(kw in text for kw in low_digital_keywords):
            return 1
        
        return 0
    
    def _calculate_future_readiness(self, row: pd.Series) -> str:
        """Calculate future-readiness category"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        scores = {}
        for readiness_type, readiness_info in self.future_readiness.items():
            keywords = readiness_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[readiness_type] = score
        
        if not scores:
            return 'stable'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'stable'
    
    def _classify_skill_nature(self, row: pd.Series) -> str:
        """Classify the nature of the skill"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        scores = {}
        for nature_type, nature_info in self.skill_nature_types.items():
            keywords = nature_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[nature_type] = score
        
        if not scores:
            return 'process'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'process'
    
    def _build_four_level_hierarchy(self, df: pd.DataFrame) -> Dict:
        """
        Build the 4-level taxonomy hierarchy
        
        Structure:
        - Root (Level 0)
        - Domains (Level 1)
        - Families (Level 2)
        - Groups by Level (Level 3)
        - Skills (Level 4 - leaf nodes within groups)
        """
        
        # Level 0: Root
        root = {
            "name": "VET Skills Taxonomy",
            "type": "root",
            "level": 0,
            "description": "Comprehensive taxonomy of vocational education and training skills",
            "children": []
        }
        
        # Level 1: Domains
        for domain_key, domain_info in self.domains.items():
            domain_skills = df[df['assigned_domain'] == domain_key]
            
            if len(domain_skills) == 0:
                continue
            
            domain_node = {
                "name": domain_info['name'],
                "type": "domain",
                "level": 1,
                "domain_key": domain_key,
                "description": domain_info.get('description', ''),
                "training_packages": domain_info.get('training_packages', []),
                "children": [],
                "statistics": self._calculate_node_statistics(domain_skills)
            }
            
            # Level 2: Families within domain
            domain_families = domain_skills['assigned_family'].unique()
            
            for family_key in sorted(domain_families):
                if pd.isna(family_key):
                    continue
                    
                family_skills = domain_skills[domain_skills['assigned_family'] == family_key]
                
                if len(family_skills) == 0:
                    continue
                
                family_info = self.families.get(family_key, {'name': family_key.replace('_', ' ').title()})
                
                family_node = {
                    "name": family_info.get('name', family_key),
                    "type": "family",
                    "level": 2,
                    "family_key": family_key,
                    "description": family_info.get('description', ''),
                    "training_package": family_info.get('training_package', ''),
                    "keywords": family_info.get('keywords', [])[:10],
                    "children": [],
                    "statistics": self._calculate_node_statistics(family_skills)
                }
                
                # Level 3: Groups by skill level within family
                groups = self._create_level_based_groups(family_skills)
                
                for group in groups:
                    family_node['children'].append(group)
                
                if family_node['children']:
                    domain_node['children'].append(family_node)
            
            if domain_node['children']:
                root['children'].append(domain_node)
        
        return root
    
    def _create_level_based_groups(self, family_df: pd.DataFrame) -> List[Dict]:
        """
        Create skill groups based on skill level
        
        Groups skills by their complexity/proficiency level to organize
        skills from foundational to expert within each family.
        """
        groups = []
        
        # Get complexity levels present in this family
        complexity_levels = sorted(family_df['complexity_level'].unique())
        
        level_names = {
            1: "FOLLOW",
            2: "ASSIST", 
            3: "APPLY",
            4: "ENABLE",
            5: "ENSURE_ADVISE"
        }
        
        for complexity_level in complexity_levels:
            level_skills = family_df[family_df['complexity_level'] == complexity_level]
            
            if len(level_skills) == 0:
                continue
            
            # Create group name
            level_name = level_names.get(complexity_level, f"Level {complexity_level}")
            group_theme = None #self._extract_group_theme(level_skills)
            
            if group_theme:
                group_name = f"{level_name} {group_theme}"
            else:
                group_name = f"{level_name} Skills"
            
            # Create skills list
            skills_list = self._create_skills_list(level_skills)
            
            group_node = {
                "name": group_name,
                "type": "group",
                "level": 3,
                "complexity_level": int(complexity_level),
                "complexity_name": level_name,
                "size": len(level_skills),
                "statistics": self._calculate_node_statistics(level_skills),
                "skills": skills_list
            }
            
            groups.append(group_node)
        
        return groups
    
    def _extract_group_theme(self, group_df: pd.DataFrame) -> str:
        """Extract common theme from skills in a group"""
        # Collect keywords
        all_keywords = []
        if 'keywords' in group_df.columns:
            for keywords in group_df['keywords']:
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
                elif isinstance(keywords, str):
                    all_keywords.extend(keywords.split())
        
        if all_keywords:
            common_keywords = Counter(all_keywords).most_common(5)
            
            # Filter out generic words
            generic_words = {'skill', 'skills', 'work', 'use', 'using', 'ability', 
                           'knowledge', 'understand', 'apply', 'and', 'the', 'of', 'to'}
            
            theme_words = [word for word, count in common_keywords 
                          if word.lower() not in generic_words and count > 1]
            
            if theme_words:
                return ' & '.join([w.title() for w in theme_words[:2]])
        
        return ""
    
    def _create_skills_list(self, skills_df: pd.DataFrame) -> List[Dict]:
        """Create list of skill dictionaries with full metadata including alternative titles and aggregated data"""
        skills = []
        
        for _, skill in skills_df.iterrows():
            skill_dict = {
                "id": skill.get('skill_id', ''),
                "name": skill.get('name', ''),
                "description": skill.get('description', ''),
                "code": skill.get('code', ''),
                
                # Alternative titles from deduplication
                "alternative_titles": skill.get('alternative_titles', []) if isinstance(skill.get('alternative_titles'), list) else [],
                
                # Aggregated keywords from exact duplicates and semantic duplicates
                "all_related_kw": skill.get('all_related_kw', []) if isinstance(skill.get('all_related_kw'), list) else [],
                
                # Aggregated codes (UOC codes) from exact duplicates and semantic duplicates
                "all_related_codes": skill.get('all_related_codes', []) if isinstance(skill.get('all_related_codes'), list) else [],
                
                # Core attributes
                "level": self._extract_level_value(skill.get('level', 3)),
                "context": skill.get('context', 'hybrid'),
                "category": skill.get('category', 'general'),
                "confidence": float(skill.get('confidence', 0.5)) if pd.notna(skill.get('confidence')) else 0.5,
                
                # Cross-cutting dimensions
                "dimensions": {
                    "complexity_level": int(skill.get('complexity_level', 3)),
                    # "transferability": skill.get('transferability', 'sector_specific'),
                    # "digital_intensity": int(skill.get('digital_intensity', 1)) if pd.notna(skill.get('digital_intensity')) else 1,
                    # "future_readiness": skill.get('future_readiness', 'stable'),
                    # "skill_nature": skill.get('skill_nature', 'process'),
                },
                
                # Assignment info
                "assignment": {
                    "family": skill.get('assigned_family', ''),
                    "domain": skill.get('assigned_domain', ''),
                    "method": skill.get('family_assignment_method', ''),
                    "confidence": float(skill.get('family_assignment_confidence', 0)) if pd.notna(skill.get('family_assignment_confidence')) else 0,
                },
                
                # Evidence and keywords (original)
                "evidence": skill.get('evidence', ''),
                "keywords": skill.get('keywords', []) if isinstance(skill.get('keywords'), list) else [],
            }
            
            # Add merge info if present
            if 'merge_count' in skill and pd.notna(skill.get('merge_count')):
                skill_dict['merged_from_count'] = int(skill.get('merge_count', 1))
            
            # Add relationships if present
            if 'relationships' in skill:
                skill_dict['relationships'] = skill['relationships']
            
            skills.append(skill_dict)
        
        # Sort skills by name
        skills.sort(key=lambda x: x['name'])
        
        return skills
    
    def _calculate_node_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive statistics for a node"""
        stats = {
            "size": len(df),
            "avg_confidence": float(df['confidence'].mean()) if 'confidence' in df.columns and df['confidence'].notna().any() else 0.0
        }
        
        # Complexity level distribution
        if 'complexity_level' in df.columns:
            complexity_dist = df['complexity_level'].value_counts().to_dict()
            stats['complexity_distribution'] = {int(k): int(v) for k, v in complexity_dist.items()}
            stats['avg_complexity'] = float(df['complexity_level'].mean())
        
        # Transferability distribution
        if 'transferability' in df.columns:
            stats['transferability_distribution'] = df['transferability'].value_counts().to_dict()
        
        # Digital intensity
        if 'digital_intensity' in df.columns:
            stats['avg_digital_intensity'] = float(df['digital_intensity'].mean())
        
        # Future readiness
        if 'future_readiness' in df.columns:
            stats['future_readiness_distribution'] = df['future_readiness'].value_counts().to_dict()
        
        # Context distribution
        if 'context' in df.columns:
            stats['context_distribution'] = df['context'].value_counts().to_dict()
            stats['dominant_context'] = df['context'].mode()[0] if len(df) > 0 else 'hybrid'
        
        # Level statistics
        if 'level' in df.columns:
            levels = df['level'].apply(self._extract_level_value)
            stats['level_range'] = [int(levels.min()), int(levels.max())]
            stats['avg_level'] = float(levels.mean())
        
        # Alternative titles count
        if 'alternative_titles' in df.columns:
            alt_count = df['alternative_titles'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            stats['alternative_titles_count'] = int(alt_count)
        
        # Aggregated keywords count
        if 'all_related_kw' in df.columns:
            kw_count = df['all_related_kw'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            stats['total_related_keywords'] = int(kw_count)
        
        # Aggregated codes count
        if 'all_related_codes' in df.columns:
            codes_count = df['all_related_codes'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            ).sum()
            stats['total_related_codes'] = int(codes_count)
        
        return stats
    
    def _extract_level_value(self, level) -> int:
        """Extract numeric level value"""
        if hasattr(level, 'value'):
            return level.value
        try:
            return int(level)
        except:
            return 3
    
    def _add_skill_relationships(self, taxonomy: Dict, df: pd.DataFrame, 
                                 embeddings: np.ndarray) -> Dict:
        """Build skill relationship graph"""
        logger.info("  Building skill relationships...")
        
        # Create skill index
        skill_index = {row['skill_id']: idx for idx, row in df.iterrows()}
        
        similarity_threshold = self.hierarchy_config.get('relationship_similarity_threshold', 0.75)
        max_related = self.hierarchy_config.get('max_related_skills', 5)
        
        def add_relationships_to_skills(node):
            if 'skills' in node and node['skills']:
                for skill in node['skills']:
                    skill_id = skill['id']
                    if skill_id in skill_index:
                        idx = skill_index[skill_id]
                        
                        # Find similar skills
                        similarities = np.dot(embeddings, embeddings[idx])
                        similar_indices = np.argsort(similarities)[::-1][1:max_related+1]
                        
                        related_skills = []
                        for sim_idx in similar_indices:
                            if similarities[sim_idx] >= similarity_threshold:
                                related_id = df.iloc[sim_idx]['skill_id']
                                related_skills.append({
                                    'skill_id': related_id,
                                    'skill_name': df.iloc[sim_idx]['name'],
                                    'similarity': float(similarities[sim_idx]),
                                    'relationship_type': 'related'
                                })
                        
                        if related_skills:
                            skill['relationships'] = {
                                'related': related_skills,
                                'prerequisites': [],
                                'co_occurring': []
                            }
            
            if 'children' in node:
                for child in node['children']:
                    add_relationships_to_skills(child)
        
        add_relationships_to_skills(taxonomy)
        logger.info(f"  ✓ Added skill relationships")
        
        return taxonomy
    
    def _add_comprehensive_metadata(self, taxonomy: Dict, df: pd.DataFrame) -> Dict:
        """Add comprehensive metadata to taxonomy"""
        
        # Count alternative titles
        total_alt_titles = df['alternative_titles'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum() if 'alternative_titles' in df.columns else 0
        
        # Count aggregated keywords and codes
        total_related_kw = df['all_related_kw'].apply(
            lambda x: len(x) if isinstance(x, list) else 0
        ).sum() if 'all_related_kw' in df.columns else 0
        
        # Count unique unit codes across all skills
        unique_codes = set()
        if 'all_related_codes' in df.columns:
            for codes in df['all_related_codes']:
                if isinstance(codes, list):
                    unique_codes.update(codes)
        total_related_codes = len(unique_codes)
        
        taxonomy['metadata'] = {
            "version": "2.0",
            "structure": "Domain → Family → Group → Skills",
            "levels": {
                0: "Root",
                1: f"Domains ({len(self.domains)})",
                2: f"Families ({len(self.families)})",
                3: "Groups (by complexity level)",
                4: "Atomic Skills"
            },
            "cross_cutting_dimensions": {
                "complexity": {
                    "enabled": True,
                    "levels": len(self.complexity_levels),
                    "description": "Dreyfus Model + Bloom's Taxonomy (1-5)"
                },
                "transferability": {
                    "enabled": self.enable_transferability,
                    "types": list(self.transferability_types.keys()),
                },
                "digital_intensity": {
                    "enabled": self.enable_digital_intensity,
                    "range": "0-4",
                },
                "future_readiness": {
                    "enabled": self.enable_future_readiness,
                    "categories": list(self.future_readiness.keys()),
                },
                "skill_nature": {
                    "enabled": self.enable_skill_nature,
                    "types": list(self.skill_nature_types.keys()),
                }
            },
            "statistics": {
                "total_skills": len(df),
                "total_families": df['assigned_family'].nunique(),
                "total_domains": df['assigned_domain'].nunique(),
                "total_alternative_titles": int(total_alt_titles),
                "total_related_keywords": int(total_related_kw),
                "total_related_codes": int(total_related_codes),
                "depth": self._get_taxonomy_depth(taxonomy),
                "total_nodes": self._count_nodes(taxonomy)
            },
            "configuration": {
                "max_depth": self.max_depth,
                "min_children": self.min_children,
                "max_children": self.max_children,
                "relationship_building": self.build_relationships
            },
            "timestamp": pd.Timestamp.now().isoformat()
        }
        
        return taxonomy
    
    def _balance_taxonomy(self, taxonomy: Dict) -> Dict:
        """Balance the taxonomy tree"""
        
        def rebalance_node(node, depth=0):
            if 'children' not in node or not node['children']:
                return node
            
            # Remove empty children
            node['children'] = [c for c in node['children'] 
                              if c.get('children') or c.get('skills')]
            
            # Recursively balance children
            node['children'] = [rebalance_node(child, depth + 1) 
                              for child in node['children']]
            
            return node
        
        return rebalance_node(taxonomy)
    
    def _count_nodes(self, node: Dict) -> int:
        """Count total nodes in taxonomy"""
        count = 1
        if 'children' in node:
            for child in node['children']:
                count += self._count_nodes(child)
        return count
    
    def _get_taxonomy_depth(self, taxonomy: Dict) -> int:
        """Calculate maximum depth of taxonomy"""
        def get_depth(node, current_depth=0):
            if 'children' not in node or not node['children']:
                return current_depth
            return max(get_depth(child, current_depth + 1) for child in node['children'])
        
        return get_depth(taxonomy)
    
    def _create_empty_taxonomy(self) -> Dict:
        """Create an empty taxonomy structure"""
        return {
            "name": "VET Skills Taxonomy",
            "type": "root",
            "level": 0,
            "children": [],
            "metadata": {
                "structure": "Domain → Family → Group → Skills",
                "status": "empty",
                "timestamp": pd.Timestamp.now().isoformat()
            }
        }
    
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
            stats = node.get('statistics', {})
            size = stats.get('size', 0)
            
            line = f"{indent}[{node_type.upper()}] {name}"
            if size > 0:
                line += f" ({size} skills)"
            lines.append(line)
            
            # Show sample skills with alternative titles and related codes
            if 'skills' in node and node['skills'] and depth <= 3:
                for i, skill in enumerate(node['skills'][:3]):
                    skill_line = f"{indent}  • {skill['name']} (L{skill['level']})"
                    alt_titles = skill.get('alternative_titles', [])
                    if alt_titles:
                        skill_line += f" [aka: {', '.join(alt_titles[:2])}]"
                    related_codes = skill.get('all_related_codes', [])
                    if related_codes:
                        skill_line += f" [codes: {', '.join(related_codes[:3])}]"
                    lines.append(skill_line)
                if len(node['skills']) > 3:
                    lines.append(f"{indent}  ... and {len(node['skills']) - 3} more")
            
            if 'children' in node:
                for child in node['children']:
                    traverse(child, depth + 1)
        
        traverse(taxonomy)
        
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        
        logger.info(f"Exported taxonomy as text to {filepath}")


# Backward compatibility alias
class TaxonomyBuilder(MultiDimensionalTaxonomyBuilder):
    """Backward compatible class name"""
    pass