"""
Enhanced Multi-Dimensional Taxonomy Hierarchy Builder
Implements state-of-the-art 5-level hierarchy with cross-cutting dimensions:
Level 1: Domains → Level 2: Families → Level 3: Clusters → Level 4: Groups → Level 5: Atomic Skills
Plus: Transferability, Digital Intensity, Future-Readiness, Skill Nature, etc.

Updated to use comprehensive settings and embedding-based matching.
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import json
import re
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
USE_COMPREHENSIVE_SETTINGS = True


logger = logging.getLogger(__name__)


class MultiDimensionalTaxonomyBuilder:
    """Builds multi-dimensional hierarchical taxonomy with 5 levels and cross-cutting dimensions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.hierarchy_config = config.get('hierarchy', {})
        self.taxonomy_config = config.get('taxonomy', {})
        
        # Load taxonomy definitions - prefer comprehensive settings if available
        if USE_COMPREHENSIVE_SETTINGS:
            logger.info("Loading comprehensive settings (14 domains, 85 families, 54 training packages)")
            self.domains = SKILL_DOMAINS
            self.families = SKILL_FAMILIES
            self.complexity_levels = COMPLEXITY_LEVELS
            self.transferability_types = TRANSFERABILITY_TYPES
            self.digital_intensity_levels = DIGITAL_INTENSITY_LEVELS
            self.future_readiness = FUTURE_READINESS
            self.skill_nature_types = SKILL_NATURE_TYPES
            self.context_types = CONTEXT_TYPES
        else:
            logger.warning("Comprehensive settings not found, using config taxonomy definitions")
            self.domains = self.taxonomy_config.get('domains', {})
            self.families = self.taxonomy_config.get('families', {})
            self.complexity_levels = self.taxonomy_config.get('complexity_levels', {})
            self.transferability_types = self.taxonomy_config.get('transferability', {})
            self.digital_intensity_levels = self.taxonomy_config.get('digital_intensity', {})
            self.future_readiness = self.taxonomy_config.get('future_readiness', {})
            self.skill_nature_types = self.taxonomy_config.get('skill_nature', {})
            self.context_types = self.taxonomy_config.get('context_types', {})
        
        # Settings
        self.max_depth = self.hierarchy_config.get('max_depth', 5)
        self.min_children = self.hierarchy_config.get('min_children', 3)
        self.max_children = self.hierarchy_config.get('max_children', 25)
        
        # Feature flags
        self.use_multi_dimensional = self.hierarchy_config.get('use_multi_dimensional_structure', True)
        self.enable_transferability = self.hierarchy_config.get('enable_transferability_scoring', True)
        self.enable_digital_intensity = self.hierarchy_config.get('enable_digital_intensity_scoring', True)
        self.enable_future_readiness = self.hierarchy_config.get('enable_future_readiness_scoring', True)
        self.enable_skill_nature = self.hierarchy_config.get('enable_skill_nature_classification', True)
        self.build_relationships = self.hierarchy_config.get('build_skill_relationships', True)
        
        # Embedding-based matching
        self.use_embeddings = self.hierarchy_config.get('use_embeddings_for_matching', True)
        self.embedding_threshold = self.hierarchy_config.get('embedding_similarity_threshold', 0.3)
        
        # Precompute embeddings for domains/families if using sentence transformer
        self.domain_embeddings = None
        self.family_embeddings = None
        
        logger.info(f"Initialized Multi-Dimensional Taxonomy Builder")
        logger.info(f"  Domains: {len(self.domains)}")
        logger.info(f"  Families: {len(self.families)}")
        logger.info(f"  Cross-cutting dimensions enabled: {self._count_enabled_dimensions()}")
        logger.info(f"  Embedding-based matching: {self.use_embeddings}")
        
    def _count_enabled_dimensions(self) -> int:
        """Count enabled cross-cutting dimensions"""
        count = 1  # Complexity always enabled
        if self.enable_transferability: count += 1
        if self.enable_digital_intensity: count += 1
        if self.enable_future_readiness: count += 1
        if self.enable_skill_nature: count += 1
        return count
    
    def precompute_category_embeddings(self, model):
        """
        Precompute embeddings for domains and families using the provided model.
        This enables efficient embedding-based matching.
        
        Args:
            model: Sentence transformer model with encode() method
        """
        if not self.use_embeddings:
            return
            
        logger.info("Precomputing embeddings for domains and families...")
        
        # Create domain texts from name + description + keywords
        domain_texts = []
        domain_keys = []
        for domain_key, domain_info in self.domains.items():
            text = f"{domain_info['name']}. {domain_info.get('description', '')}. "
            keywords = domain_info.get('keywords', [])
            if keywords:
                text += ' '.join(keywords[:10])  # Use first 10 keywords
            domain_texts.append(text)
            domain_keys.append(domain_key)
        
        # Compute domain embeddings
        if domain_texts:
            self.domain_embeddings = model.encode(domain_texts, show_progress=False)
            self.domain_keys = domain_keys
            logger.info(f"  Computed embeddings for {len(domain_keys)} domains")
        
        # Create family texts
        family_texts = []
        family_keys = []
        for family_key, family_info in self.families.items():
            text = f"{family_info['name']}. "
            keywords = family_info.get('keywords', [])
            if keywords:
                text += ' '.join(keywords[:10])  # Use first 10 keywords
            family_texts.append(text)
            family_keys.append(family_key)
        
        # Compute family embeddings
        if family_texts:
            self.family_embeddings = model.encode(family_texts, show_progress=False)
            self.family_keys = family_keys
            logger.info(f"  Computed embeddings for {len(family_keys)} families")
    
    def build_hierarchy(self, df_clustered: pd.DataFrame, embeddings: Optional[np.ndarray] = None,
                       embedding_model = None) -> Dict:
        """
        Build multi-dimensional 5-level taxonomy
        
        Args:
            df_clustered: DataFrame with clustered skills
            embeddings: Optional skill embeddings for relationship building
            embedding_model: Optional sentence transformer model for embedding-based matching
            
        Returns:
            Multi-dimensional hierarchical taxonomy
        """
        logger.info("=" * 80)
        logger.info("BUILDING MULTI-DIMENSIONAL TAXONOMY")
        logger.info("=" * 80)
        
        # Precompute category embeddings if using embeddings and model provided
        if self.use_embeddings and embedding_model is not None:
            self.precompute_category_embeddings(embedding_model)
            
            # Compute skill embeddings if not provided
            if embeddings is None:
                logger.info("Computing skill embeddings for matching...")
                skill_texts = (df_clustered['name'] + '. ' + 
                             df_clustered.get('description', '').fillna('')).tolist()
                embeddings = embedding_model.encode(skill_texts, show_progress=True)
        
        self.skill_embeddings = embeddings
        
        # Filter out noise points
        df_valid = df_clustered[df_clustered['cluster_id'] != -1].copy()
        
        if len(df_valid) == 0:
            logger.warning("No valid clusters found, returning empty taxonomy")
            return self._create_empty_taxonomy()
        
        logger.info(f"Building taxonomy from {len(df_valid)} skills in {df_valid['cluster_id'].nunique()} clusters")
        
        # Step 1: Calculate cross-cutting dimensions for all skills
        logger.info("\n[Step 1] Calculating cross-cutting dimensions...")
        df_enriched = self._calculate_cross_cutting_dimensions(df_valid)
        
        # Step 2: Assign skills to domains and families
        logger.info("\n[Step 2] Assigning skills to domains and families...")
        df_enriched = self._assign_domains_and_families(df_enriched)
        
        # Step 3: Build 5-level hierarchy
        logger.info("\n[Step 3] Building 5-level hierarchy...")
        taxonomy = self._build_five_level_hierarchy(df_enriched)
        
        # Step 4: Build skill relationships
        if self.build_relationships and self.skill_embeddings is not None:
            logger.info("\n[Step 4] Building skill relationships...")
            taxonomy = self._add_skill_relationships(taxonomy, df_enriched, embeddings)
        
        # Step 5: Add metadata and statistics
        logger.info("\n[Step 5] Adding metadata and statistics...")
        taxonomy = self._add_comprehensive_metadata(taxonomy, df_enriched)
        
        # Step 6: Validate and balance
        logger.info("\n[Step 6] Validating and balancing taxonomy...")
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
        
        # 1. Complexity Level (already have as 'level')
        df_enriched['complexity_level'] = df_enriched['level'].apply(self._map_to_complexity_level)
        
        # 2. Transferability Index
        if self.enable_transferability:
            df_enriched['transferability'] = df_enriched.apply(
                lambda row: self._calculate_transferability(row), axis=1
            )
            logger.info(f"  ✓ Calculated transferability scores")
        
        # 3. Digital Intensity
        if self.enable_digital_intensity:
            df_enriched['digital_intensity'] = df_enriched.apply(
                lambda row: self._calculate_digital_intensity(row), axis=1
            )
            logger.info(f"  ✓ Calculated digital intensity scores")
        
        # 4. Future-Readiness
        if self.enable_future_readiness:
            df_enriched['future_readiness'] = df_enriched.apply(
                lambda row: self._calculate_future_readiness(row), axis=1
            )
            logger.info(f"  ✓ Calculated future-readiness scores")
        
        # 5. Skill Nature
        if self.enable_skill_nature:
            df_enriched['skill_nature'] = df_enriched.apply(
                lambda row: self._classify_skill_nature(row), axis=1
            )
            logger.info(f"  ✓ Classified skill nature")
        
        return df_enriched
    
    def _map_to_complexity_level(self, level) -> int:
        """Map SFIA level (1-7) to complexity level (1-5)"""
        if hasattr(level, 'value'):
            level = level.value
        try:
            level = int(level)
        except:
            level = 3
        
        # Map 1-7 to 1-5
        if level <= 2:
            return 1  # Foundational
        elif level <= 3:
            return 2  # Basic
        elif level <= 4:
            return 3  # Intermediate
        elif level <= 5:
            return 4  # Advanced
        else:
            return 5  # Expert
    
    def _calculate_transferability(self, row: pd.Series) -> str:
        """Calculate transferability index for a skill"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        # Check keywords for each transferability type
        scores = {}
        for trans_type, trans_info in self.transferability_types.items():
            keywords = trans_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[trans_type] = score
        
        # Return type with highest score, or default to sector_specific
        if not scores:
            return 'sector_specific'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'sector_specific'
    
    def _calculate_digital_intensity(self, row: pd.Series) -> int:
        """Calculate digital intensity level (0-4)"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        # Keywords for different digital intensity levels
        high_digital_keywords = ['software', 'programming', 'code', 'algorithm', 'digital', 'data', 'ai', 'machine learning']
        medium_digital_keywords = ['computer', 'email', 'spreadsheet', 'database', 'online', 'web']
        low_digital_keywords = ['technology', 'electronic', 'automated']
        
        # Check for advanced/emerging tech
        if any(kw in text for kw in ['ai', 'artificial intelligence', 'machine learning', 'blockchain', 'quantum']):
            return 4
        
        # Check for high digital
        high_count = sum(1 for kw in high_digital_keywords if kw in text)
        if high_count >= 2:
            return 3
        
        # Check for medium digital
        medium_count = sum(1 for kw in medium_digital_keywords if kw in text)
        if medium_count >= 2:
            return 2
        
        # Check for low digital
        if any(kw in text for kw in low_digital_keywords):
            return 1
        
        return 0
    
    def _calculate_future_readiness(self, row: pd.Series) -> str:
        """Calculate future-readiness category"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        # Check keywords for each readiness category
        scores = {}
        for readiness_type, readiness_info in self.future_readiness.items():
            keywords = readiness_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[readiness_type] = score
        
        # Return type with highest score
        if not scores:
            return 'stable'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'stable'
    
    def _classify_skill_nature(self, row: pd.Series) -> str:
        """Classify the nature of the skill"""
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        # Check keywords for each skill nature type
        scores = {}
        for nature_type, nature_info in self.skill_nature_types.items():
            keywords = nature_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            scores[nature_type] = score
        
        # Return type with highest score
        if not scores:
            return 'process'
        
        max_type = max(scores, key=scores.get)
        return max_type if scores[max_type] > 0 else 'process'
    
    def _assign_domains_and_families(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign each skill to a domain and family"""
        df_enriched = df.copy()
        
        # Assign domains (with index for embedding lookup)
        df_enriched['assigned_domain'] = df_enriched.apply(
            lambda row: self._match_to_domain(row, row.name), axis=1
        )
        
        # Assign families (with index for embedding lookup)
        df_enriched['assigned_family'] = df_enriched.apply(
            lambda row: self._match_to_family(row, row.name), axis=1
        )
        
        # Log distribution
        domain_dist = df_enriched['assigned_domain'].value_counts()
        logger.info(f"  Domain distribution:")
        for domain, count in domain_dist.head(10).items():
            domain_name = self.domains.get(domain, {}).get('name', domain)
            logger.info(f"    {domain_name}: {count} skills ({100*count/len(df_enriched):.1f}%)")
        
        return df_enriched
    
    def _match_to_domain(self, row: pd.Series, skill_idx: int = None) -> str:
        """Match a skill to the most appropriate domain using embeddings or keywords"""
        
        # Use embedding-based matching if available
        if self.use_embeddings and self.domain_embeddings is not None and self.skill_embeddings is not None:
            if skill_idx is not None:
                skill_emb = self.skill_embeddings[skill_idx].reshape(1, -1)
                similarities = cosine_similarity(skill_emb, self.domain_embeddings)[0]
                
                # Get best match above threshold
                best_idx = np.argmax(similarities)
                if similarities[best_idx] >= self.embedding_threshold:
                    return self.domain_keys[best_idx]
        
        # Fallback to keyword-based matching
        text = str(row.get('name', '')) + ' ' + str(row.get('description', '')) + ' ' + str(row.get('keywords', ''))
        text = text.lower()
        
        # Score each domain
        domain_scores = {}
        for domain_key, domain_info in self.domains.items():
            keywords = domain_info.get('keywords', [])
            score = sum(1 for kw in keywords if kw in text)
            domain_scores[domain_key] = score
        
        # Also consider existing category if available
        if 'category' in row:
            category = str(row['category']).lower()
            # Map old categories to new comprehensive domains
            category_domain_map = {
                'technical': 'construction_building',
                'cognitive': 'business_finance',
                'interpersonal': 'healthcare_community',
                'digital': 'digital_technology'
            }
            if category in category_domain_map:
                mapped_domain = category_domain_map[category]
                if mapped_domain in domain_scores:
                    domain_scores[mapped_domain] = domain_scores.get(mapped_domain, 0) + 5
        
        # Return domain with highest score
        if not domain_scores or max(domain_scores.values()) == 0:
            # Default to first domain
            return list(self.domains.keys())[0] if self.domains else 'business_finance'
        
        return max(domain_scores, key=domain_scores.get)
    
    def _match_to_family(self, row: pd.Series, skill_idx: int = None) -> str:
        """Match a skill to the most appropriate family using embeddings or keywords"""
        assigned_domain = row.get('assigned_domain', list(self.domains.keys())[0] if self.domains else 'business_finance')
        
        # Get families for this domain
        domain_families = {k: v for k, v in self.families.items() if v['domain'] == assigned_domain}
        
        if not domain_families:
            # Return first family in any domain
            return list(self.families.keys())[0] if self.families else 'business_administration'
        
        # Use embedding-based matching if available
        if self.use_embeddings and self.family_embeddings is not None and self.skill_embeddings is not None:
            if skill_idx is not None:
                skill_emb = self.skill_embeddings[skill_idx].reshape(1, -1)
                
                # Get indices of families in this domain
                domain_family_indices = [i for i, fk in enumerate(self.family_keys) 
                                        if fk in domain_families]
                
                if domain_family_indices:
                    # Compute similarities only for families in this domain
                    domain_family_embs = self.family_embeddings[domain_family_indices]
                    similarities = cosine_similarity(skill_emb, domain_family_embs)[0]
                    
                    # Get best match
                    best_local_idx = np.argmax(similarities)
                    if similarities[best_local_idx] >= self.embedding_threshold:
                        best_global_idx = domain_family_indices[best_local_idx]
                        return self.family_keys[best_global_idx]
        
        # Fallback to keyword-based matching
        text = str(row.get('name', '')) + ' ' + str(row.get('description', ''))
        text = text.lower()
        
        # Score each family by keywords
        family_scores = {}
        for family_key, family_info in domain_families.items():
            keywords = family_info.get('keywords', [])
            # Also use family name words as keywords
            family_name_words = family_info['name'].lower().split()
            all_keywords = set(keywords + family_name_words)
            score = sum(1 for kw in all_keywords if kw in text)
            family_scores[family_key] = score
        
        # Return family with highest score
        if not family_scores or max(family_scores.values()) == 0:
            return list(domain_families.keys())[0]  # Return first family
        
        return max(family_scores, key=family_scores.get)
    
    def _build_five_level_hierarchy(self, df: pd.DataFrame) -> Dict:
        """Build the 5-level taxonomy hierarchy"""
        
        # Level 1: Root
        root = {
            "name": "Skills Taxonomy",
            "type": "root",
            "level": 0,
            "children": []
        }
        
        # Level 2: Domains
        for domain_key, domain_info in self.domains.items():
            domain_skills = df[df['assigned_domain'] == domain_key]
            
            if len(domain_skills) == 0:
                continue
            
            domain_node = {
                "name": domain_info['name'],
                "type": "domain",
                "level": 1,
                "domain_key": domain_key,
                "description": domain_info['description'],
                "children": [],
                "statistics": self._calculate_node_statistics(domain_skills)
            }
            
            # Level 3: Families (within domain)
            domain_families = domain_skills['assigned_family'].unique()
            
            for family_key in domain_families:
                family_skills = domain_skills[domain_skills['assigned_family'] == family_key]
                
                if len(family_skills) < self.min_children:
                    continue
                
                family_info = self.families.get(family_key, {'name': family_key.replace('_', ' ').title()})
                
                family_node = {
                    "name": family_info.get('name', family_key),
                    "type": "family",
                    "level": 2,
                    "family_key": family_key,
                    "children": [],
                    "statistics": self._calculate_node_statistics(family_skills)
                }
                
                # Level 4: Clusters (within family)
                family_clusters = family_skills['cluster_id'].unique()
                
                for cluster_id in sorted(family_clusters):
                    cluster_skills = family_skills[family_skills['cluster_id'] == cluster_id]
                    
                    # Create cluster node (Level 3)
                    cluster_node = self._create_cluster_node_with_groups(cluster_id, cluster_skills)
                    
                    family_node['children'].append(cluster_node)
                
                if family_node['children']:
                    domain_node['children'].append(family_node)
            
            if domain_node['children']:
                root['children'].append(domain_node)
        
        return root
    
    def _create_cluster_node_with_groups(self, cluster_id: int, cluster_df: pd.DataFrame) -> Dict:
        """
        Create a cluster node (Level 3) with groups (Level 4) underneath
        
        Hierarchy: Cluster → Groups → Skills
        """
        # Generate cluster name from common keywords
        cluster_name = self._generate_cluster_name(cluster_df)
        
        # Create cluster node
        cluster_node = {
            "name": cluster_name,
            "type": "cluster",
            "level": 3,
            "cluster_id": int(cluster_id),
            "size": len(cluster_df),
            "statistics": self._calculate_node_statistics(cluster_df),
            "children": []  # Will contain groups
        }
        
        # Create groups within this cluster
        groups = self._create_skill_groups(cluster_df)
        
        for group in groups:
            cluster_node['children'].append(group)
        
        return cluster_node
    
    def _create_skill_groups(self, cluster_df: pd.DataFrame) -> List[Dict]:
        """
        Create skill groups (Level 4) with meaningful names
        
        Groups are created based on:
        1. Complexity level (primary)
        2. Context (secondary, if complexity levels are similar)
        3. Skill content/keywords (for naming)
        
        Returns: List of group nodes
        """
        groups = []
        
        # Strategy 1: Group by complexity level if there's variation
        complexity_levels = cluster_df['complexity_level'].unique() if 'complexity_level' in cluster_df.columns else [3]
        
        if len(complexity_levels) > 1 or len(cluster_df) > self.max_children:
            # Group by complexity level
            for level in sorted(complexity_levels):
                level_skills = cluster_df[cluster_df['complexity_level'] == level]
                
                if len(level_skills) == 0:
                    continue
                
                # Generate meaningful group name
                group_name = self._generate_group_name(level_skills, level)
                
                # Create skills list for this group
                skills_list = self._create_skills_list(level_skills)
                
                group_node = {
                    "name": group_name,
                    "type": "group",
                    "level": 4,
                    "complexity_level": int(level),
                    "size": len(level_skills),
                    "statistics": self._calculate_node_statistics(level_skills),
                    "skills": skills_list,
                    "children": []  # Groups don't have children, they contain skills directly
                }
                
                groups.append(group_node)
        
        else:
            # Single group for small/homogeneous clusters
            # Still create a group for consistency
            group_name = self._generate_group_name(cluster_df, complexity_levels[0] if len(complexity_levels) > 0 else 3)
            
            skills_list = self._create_skills_list(cluster_df)
            
            group_node = {
                "name": group_name,
                "type": "group",
                "level": 4,
                "complexity_level": int(complexity_levels[0]) if len(complexity_levels) > 0 else 3,
                "size": len(cluster_df),
                "statistics": self._calculate_node_statistics(cluster_df),
                "skills": skills_list,
                "children": []
            }
            
            groups.append(group_node)
        
        return groups
    
    def _generate_group_name(self, group_df: pd.DataFrame, complexity_level: int) -> str:
        """
        Generate a meaningful name for a skill group
        
        Combines:
        - Complexity level descriptor (Foundational/Basic/Intermediate/Advanced/Expert)
        - Common theme from keywords
        
        Examples:
        - "Basic Python Programming"
        - "Advanced Data Analysis"
        - "Foundational Carpentry Techniques"
        """
        # Get complexity level descriptor
        level_descriptors = {
            1: "Foundational",
            2: "Basic",
            3: "Intermediate",
            4: "Advanced",
            5: "Expert"
        }
        
        level_name = level_descriptors.get(complexity_level, "Intermediate")
        
        # Extract common theme from keywords if available
        all_keywords = []
        if 'keywords' in group_df.columns:
            for keywords in group_df['keywords']:
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
                elif isinstance(keywords, str):
                    all_keywords.extend(keywords.split())
        
        if all_keywords:
            # Get most common keywords (excluding very common words)
            common_words = Counter(all_keywords).most_common(10)
            
            # Filter out generic words
            generic_words = {'skill', 'skills', 'work', 'use', 'using', 'ability', 'knowledge', 
                           'understand', 'understanding', 'apply', 'application', 'and', 'the', 'of', 'to'}
            
            meaningful_keywords = [word for word, count in common_words 
                                  if word.lower() not in generic_words and count > 1]
            
            if meaningful_keywords:
                # Create theme from top 2-3 keywords
                theme = ' & '.join([word.title() for word in meaningful_keywords[:2]])
                return f"{level_name} {theme}"
        
        # Fallback: try to extract theme from skill names
        skill_names = group_df['name'].tolist()
        if skill_names:
            # Find common words in skill names
            name_words = []
            for name in skill_names:
                words = name.lower().split()
                name_words.extend([w for w in words if len(w) > 3])
            
            if name_words:
                common_name_words = Counter(name_words).most_common(5)
                generic_words = {'skill', 'skills', 'work', 'use', 'using', 'ability', 'knowledge', 
                               'understand', 'understanding', 'apply', 'application', 'and', 'the', 'of', 'to'}
                theme_words = [word for word, count in common_name_words 
                             if word not in generic_words and count > 1]
                
                if theme_words:
                    theme = ' & '.join([word.title() for word in theme_words[:2]])
                    return f"{level_name} {theme}"
        
        # Final fallback: just use complexity descriptor
        context = group_df['context'].mode()[0] if 'context' in group_df.columns and len(group_df) > 0 else 'Skills'
        return f"{level_name} {context.title()} Skills"
    
    def _create_skills_list(self, skills_df: pd.DataFrame) -> List[Dict]:
        """Create list of skill dictionaries with full metadata"""
        skills = []
        
        for _, skill in skills_df.iterrows():
            skill_dict = {
                "id": skill.get('skill_id', ''),
                "name": skill.get('name', ''),
                "description": skill.get('description', ''),
                "code": skill.get('code', ''),
                
                # Core attributes
                "level": self._extract_level_value(skill.get('level', 3)),
                "context": skill.get('context', 'hybrid'),
                "category": skill.get('category', 'general'),
                "confidence": float(skill.get('confidence', 0.5)),
                
                # Cross-cutting dimensions
                "dimensions": {
                    "complexity_level": int(skill.get('complexity_level', 3)),
                    "transferability": skill.get('transferability', 'sector_specific'),
                    "digital_intensity": int(skill.get('digital_intensity', 1)),
                    "future_readiness": skill.get('future_readiness', 'stable'),
                    "skill_nature": skill.get('skill_nature', 'process'),
                },
                
                # Evidence
                "evidence": skill.get('evidence', ''),
                "keywords": skill.get('keywords', []),
            }
            
            # Add relationships if present
            if 'relationships' in skill:
                skill_dict['relationships'] = skill['relationships']
            
            skills.append(skill_dict)
        
        # Sort skills by name
        skills.sort(key=lambda x: x['name'])
        
        return skills
    
    def _generate_cluster_name(self, cluster_df: pd.DataFrame) -> str:
        """Generate a descriptive name for a cluster"""
        # Extract common keywords if available
        all_keywords = []
        if 'keywords' in cluster_df.columns:
            for keywords in cluster_df['keywords']:
                if isinstance(keywords, list):
                    all_keywords.extend(keywords)
                elif isinstance(keywords, str):
                    all_keywords.extend(keywords.split())
        
        if all_keywords:
            common_keywords = Counter(all_keywords).most_common(3)
            if common_keywords and common_keywords[0][1] > 1:  # At least 2 occurrences
                name_parts = [k for k, _ in common_keywords[:2]]
                cluster_name = " & ".join(name_parts).title()
                return cluster_name
        
        # Fallback: use first skill name
        if len(cluster_df) > 0:
            first_skill = cluster_df.iloc[0]['name']
            # Take first few words
            words = str(first_skill).split()[:3]
            return " ".join(words) + " Skills"
        
        return "Skill Group"
    
    def _calculate_node_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive statistics for a node"""
        stats = {
            "size": len(df),
            "avg_confidence": float(df['confidence'].mean()) if 'confidence' in df.columns else 0.0
        }
        
        # Complexity level distribution
        if 'complexity_level' in df.columns:
            complexity_dist = df['complexity_level'].value_counts().to_dict()
            stats['complexity_distribution'] = {int(k): int(v) for k, v in complexity_dist.items()}
            stats['avg_complexity'] = float(df['complexity_level'].mean())
        
        # Transferability distribution
        if 'transferability' in df.columns:
            stats['transferability_distribution'] = df['transferability'].value_counts().to_dict()
        
        # Digital intensity distribution
        if 'digital_intensity' in df.columns:
            stats['avg_digital_intensity'] = float(df['digital_intensity'].mean())
            stats['digital_intensity_distribution'] = df['digital_intensity'].value_counts().to_dict()
        
        # Future readiness distribution
        if 'future_readiness' in df.columns:
            stats['future_readiness_distribution'] = df['future_readiness'].value_counts().to_dict()
        
        # Skill nature distribution
        if 'skill_nature' in df.columns:
            stats['skill_nature_distribution'] = df['skill_nature'].value_counts().to_dict()
        
        # Context distribution
        if 'context' in df.columns:
            stats['context_distribution'] = df['context'].value_counts().to_dict()
            stats['dominant_context'] = df['context'].mode()[0] if len(df) > 0 else 'hybrid'
        
        # Level statistics
        if 'level' in df.columns:
            levels = df['level'].apply(self._extract_level_value)
            stats['level_range'] = [int(levels.min()), int(levels.max())]
            stats['avg_level'] = float(levels.mean())
        
        return stats
    
    def _extract_level_value(self, level) -> int:
        """Extract numeric level value"""
        if hasattr(level, 'value'):
            return level.value
        try:
            return int(level)
        except:
            return 3
    
    def _add_skill_relationships(self, taxonomy: Dict, df: pd.DataFrame, embeddings: np.ndarray) -> Dict:
        """Build skill relationship graph"""
        logger.info("  Building skill relationships...")
        
        # Create skill index
        skill_index = {row['skill_id']: idx for idx, row in df.iterrows()}
        
        # Calculate similarity threshold
        similarity_threshold = self.hierarchy_config.get('relationship_similarity_threshold', 0.75)
        max_related = self.hierarchy_config.get('max_related_skills', 5)
        
        # Build relationships for each skill
        def add_relationships_to_skills(node):
            if 'skills' in node and node['skills']:
                for skill in node['skills']:
                    skill_id = skill['id']
                    if skill_id in skill_index:
                        idx = skill_index[skill_id]
                        
                        # Find similar skills (using embeddings)
                        similarities = np.dot(embeddings, embeddings[idx])
                        similar_indices = np.argsort(similarities)[::-1][1:max_related+1]  # Exclude self
                        
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
                                'prerequisites': [],  # Could be enhanced with level-based logic
                                'co_occurring': []  # Could be enhanced with co-occurrence analysis
                            }
            
            # Recursively process children
            if 'children' in node:
                for child in node['children']:
                    add_relationships_to_skills(child)
        
        add_relationships_to_skills(taxonomy)
        logger.info(f"  ✓ Added skill relationships")
        
        return taxonomy
    
    def _add_comprehensive_metadata(self, taxonomy: Dict, df: pd.DataFrame) -> Dict:
        """Add comprehensive metadata to taxonomy"""
        
        taxonomy['metadata'] = {
            "version": "1.0",
            "structure": "Multi-Dimensional 5-Level Hierarchy",
            "levels": {
                0: "Root",
                1: "Domains (8)",
                2: "Families (25+)",
                3: "Clusters (Auto-generated)",
                4: "Groups (Level-based)",
                5: "Atomic Skills"
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
                    "description": "Universal to Occupation-specific"
                },
                "digital_intensity": {
                    "enabled": self.enable_digital_intensity,
                    "range": "0-4",
                    "description": "No digital to Advanced digital"
                },
                "future_readiness": {
                    "enabled": self.enable_future_readiness,
                    "categories": list(self.future_readiness.keys()),
                    "description": "Declining to Transformative"
                },
                "skill_nature": {
                    "enabled": self.enable_skill_nature,
                    "types": list(self.skill_nature_types.keys()),
                    "description": "Process, Content, Social, System, Resource"
                }
            },
            "statistics": {
                "total_skills": len(df),
                "total_clusters": df['cluster_id'].nunique(),
                "total_domains": len(taxonomy.get('children', [])),
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
            
            # If too many children, group them
            if len(node['children']) > self.max_children and depth < self.max_depth - 1:
                node = self._group_children(node)
            
            # Recursively balance children
            node['children'] = [rebalance_node(child, depth + 1) 
                              for child in node['children']]
            
            return node
        
        return rebalance_node(taxonomy)
    
    def _group_children(self, node: Dict) -> Dict:
        """Group children if a node has too many"""
        if len(node['children']) <= self.max_children:
            return node
        
        # IMPORTANT: Don't group families - they contain clusters which already have groups
        # Only apply batching to very large domain-level structures
        if node.get('type') in ['family', 'cluster', 'group']:
            return node  # Skip balancing for these - they're already properly structured
        
        # Group by similarity in statistics
        # For simplicity, group by batches
        batch_size = self.max_children
        grouped_children = []
        
        for i in range(0, len(node['children']), batch_size):
            batch = node['children'][i:i + batch_size]
            
            if len(batch) == 1:
                grouped_children.append(batch[0])
            else:
                # Create a section node (NOT a group - to avoid confusion with skill groups)
                section_node = {
                    "name": f"Section {i // batch_size + 1}",
                    "type": "section",  # Changed from "group" to "section"
                    "level": node.get('level', 0) + 1,
                    "children": batch,
                    "statistics": self._aggregate_statistics(batch)
                }
                grouped_children.append(section_node)
        
        node['children'] = grouped_children
        return node
    
    def _aggregate_statistics(self, nodes: List[Dict]) -> Dict:
        """Aggregate statistics from multiple nodes"""
        total_size = sum(n.get('statistics', {}).get('size', 0) for n in nodes)
        return {"size": total_size}
    
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
            "name": "Skills Taxonomy",
            "type": "root",
            "level": 0,
            "children": [],
            "metadata": {
                "structure": "Multi-Dimensional 5-Level Hierarchy",
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
            
            # Add node info
            line = f"{indent}[{node_type.upper()}] {name}"
            if size > 0:
                line += f" ({size} skills)"
            lines.append(line)
            
            # Show sample skills if present
            if 'skills' in node and node['skills'] and depth <= 3:
                for i, skill in enumerate(node['skills'][:3]):
                    skill_line = f"{indent}  • {skill['name']} (L{skill['level']})"
                    lines.append(skill_line)
                if len(node['skills']) > 3:
                    lines.append(f"{indent}  ... and {len(node['skills']) - 3} more")
            
            # Traverse children
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