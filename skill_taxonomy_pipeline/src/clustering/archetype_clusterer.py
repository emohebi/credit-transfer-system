"""
Ability Archetype Clustering Module

Clusters skills into Ability Archetypes based on facet signatures,
then sub-clusters within each archetype using agglomerative clustering
on embeddings, and builds progression ladders ordered by proficiency level.

Architecture:
    Ability Archetype  (NAT, TRF)
      └── Skill Sub-cluster  (embedding-based, agglomerative clustering)
            └── Progression Ladder  (skills ordered by LVL within sub-cluster)
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import squareform
import json

from config.facets import ALL_FACETS, MULTI_VALUE_FACETS

logger = logging.getLogger(__name__)

# Maximum retries for LLM JSON parsing failures
MAX_LLM_RETRIES = 5


# ═══════════════════════════════════════════════════════════════════
#  DATA CLASSES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ProgressionRung:
    """A single level rung in a progression ladder"""
    level: int
    level_name: str
    skill_ids: List[str]
    skill_names: List[str]
    asced_fields: List[str]  # ASCED codes present at this rung
    asced_names: List[str]   # ASCED names present at this rung
    skill_count: int = 0

    def __post_init__(self):
        self.skill_count = len(self.skill_ids)


@dataclass
class SkillSubCluster:
    """A thematically coherent sub-cluster within an archetype"""
    cluster_id: str
    archetype_id: str
    label: str
    representative_skills: List[Dict]  # Top skills nearest centroid
    progression: List[ProgressionRung]
    progression_type: str  # 'full', 'partial', 'flat', 'sparse'
    level_span: Tuple[int, int]
    level_gaps: List[int]
    asced_spread: Dict[str, int]  # ASCED code -> count
    asced_names: Dict[str, str]   # ASCED code -> name
    total_skills: int
    avg_intra_similarity: float = 0.0
    skill_ids: List[str] = field(default_factory=list)


@dataclass
class AbilityArchetype:
    """A group of skills sharing the same ability signature (NAT, TRF)"""
    archetype_id: str
    nat_code: str
    nat_name: str
    trf_code: str
    trf_name: str
    label: str  # Human-readable composite label
    sub_clusters: List[SkillSubCluster]
    unclassified_skills: List[Dict]  # Noise points
    total_skills: int
    asced_coverage: Dict[str, int]
    level_distribution: Dict[int, int]
    progression_summary: Dict[str, int]  # progression_type -> count


# ═══════════════════════════════════════════════════════════════════
#  LEVEL NAME MAPPING
# ═══════════════════════════════════════════════════════════════════

LEVEL_NAMES = {
    1: "Follow",
    2: "Assist",
    3: "Apply",
    4: "Enable",
    5: "Ensure & Advise",
    6: "Initiate & Influence",
    7: "Set Strategy",
}


# ═══════════════════════════════════════════════════════════════════
#  MAIN CLUSTERER CLASS
# ═══════════════════════════════════════════════════════════════════

class ArchetypeClusterer:
    """
    Clusters skills into Ability Archetypes and builds progression ladders.

    Uses existing pipeline components:
    - Facet assignments from FacetAssigner (NAT, TRF, LVL, ASCED; COG on skills only)
    - Precomputed embeddings from EmbeddingManager
    - Embedding similarity via EmbeddingInterface

    Algorithm:
    1. Group skills by (NAT, TRF) -> Ability Archetypes
    2. Within each archetype, agglomerative clustering on embeddings -> Sub-clusters
    3. Within each sub-cluster, order by LVL -> Progression Ladders
    4. Compute cross-industry pathway analysis from ASCED distribution
    """

    def __init__(self, config: Dict, embedding_interface=None, genai_interface=None):
        self.config = config
        self.embedding_interface = embedding_interface
        self.genai_interface = genai_interface

        # Clustering settings
        cluster_config = config.get('archetype_clustering', {})
        self.min_archetype_size = cluster_config.get('min_archetype_size', 5)
        self.min_subcluster_size = cluster_config.get('min_subcluster_size', 3)
        self.distance_threshold_floor = cluster_config.get('distance_threshold_floor', 0.45)
        self.distance_threshold_ceiling = cluster_config.get('distance_threshold_ceiling', 0.65)
        self.distance_threshold_sigma = cluster_config.get('distance_threshold_sigma', 0.5)
        self.large_archetype_threshold = cluster_config.get('large_archetype_threshold', 5000)
        self.facet_confidence_threshold = cluster_config.get('facet_confidence_threshold', 0.4)
        self.use_llm_labels = cluster_config.get('use_llm_labels', True) and genai_interface is not None
        self.llm_label_batch_size = cluster_config.get('llm_label_batch_size', 20)
        self.representative_skill_count = cluster_config.get('representative_skill_count', 5)

        # Key facets for archetype signature (NAT × TRF = 24 archetypes)
        # COG is excluded — it's a depth indicator, not a type indicator.
        # Skills of the same nature and transferability but different cognitive
        # complexity should be in the same archetype so progression ladders
        # can capture the depth variation.
        self.signature_facets = ['NAT', 'TRF']
        # Progression axis
        self.progression_facet = 'LVL'
        # Industry spread facet
        self.industry_facet = 'ASCED'

        # Statistics
        self.stats = {}

        logger.info("Initialized ArchetypeClusterer")
        logger.info(f"  Signature facets: {self.signature_facets}")
        logger.info(f"  Min archetype size: {self.min_archetype_size}")
        logger.info(f"  Facet confidence threshold: {self.facet_confidence_threshold}")
        logger.info(f"  Use LLM labels: {self.use_llm_labels}")

    # ═══════════════════════════════════════════════════════════════
    #  MAIN ENTRY POINT
    # ═══════════════════════════════════════════════════════════════

    def build_archetypes(
        self,
        df: pd.DataFrame,
        embeddings: np.ndarray
    ) -> Tuple[List[AbilityArchetype], Dict[str, Any]]:
        """
        Main method: build ability archetypes with sub-clusters and progression ladders.
        """
        logger.info("=" * 80)
        logger.info("BUILDING ABILITY ARCHETYPES WITH PROGRESSION LADDERS")
        logger.info("=" * 80)
        logger.info(f"Input: {len(df)} skills, embeddings shape: {embeddings.shape}")

        # Step 1: Filter skills with low facet confidence
        df_valid, embeddings_valid, df_excluded = self._filter_by_facet_confidence(df, embeddings)

        # Step 2: Build archetype keys and group
        archetype_groups = self._build_archetype_groups(df_valid)

        # Step 3: Process each archetype
        archetypes = []
        for archetype_key, group_indices in archetype_groups.items():
            if len(group_indices) < self.min_archetype_size:
                continue

            archetype = self._process_archetype(
                archetype_key, group_indices, df_valid, embeddings_valid
            )
            if archetype is not None:
                archetypes.append(archetype)

        # Step 4: Generate sub-cluster labels (batch LLM if available)
        if self.use_llm_labels:
            self._generate_llm_labels(archetypes)

        # Step 5: Compute statistics
        stats = self._compute_statistics(archetypes, df_valid, df_excluded)
        self.stats = stats

        self._log_summary(archetypes, stats)

        return archetypes, stats

    # ═══════════════════════════════════════════════════════════════
    #  STEP 1: FILTER BY FACET CONFIDENCE
    # ═══════════════════════════════════════════════════════════════

    def _filter_by_facet_confidence(
        self, df: pd.DataFrame, embeddings: np.ndarray
    ) -> Tuple[pd.DataFrame, np.ndarray, pd.DataFrame]:
        """Filter out skills where key facets have low confidence."""

        mask = pd.Series(True, index=df.index)

        for facet_id in self.signature_facets:
            conf_col = f'facet_{facet_id}_confidence'
            val_col = f'facet_{facet_id}'
            if conf_col in df.columns:
                mask &= (df[conf_col] >= self.facet_confidence_threshold)
            if val_col in df.columns:
                mask &= df[val_col].notna()

        df_valid = df[mask].copy()
        df_excluded = df[~mask].copy()

        # Align embeddings with filtered df
        valid_positions = [df.index.get_loc(idx) for idx in df_valid.index]
        embeddings_valid = embeddings[valid_positions]

        excluded_count = len(df) - len(df_valid)
        if excluded_count > 0:
            logger.info(
                f"Filtered {excluded_count} skills with low facet confidence "
                f"(threshold={self.facet_confidence_threshold})"
            )
        logger.info(f"Valid skills for archetype clustering: {len(df_valid)}")

        return df_valid, embeddings_valid, df_excluded

    # ═══════════════════════════════════════════════════════════════
    #  STEP 2: BUILD ARCHETYPE GROUPS
    # ═══════════════════════════════════════════════════════════════

    def _build_archetype_groups(self, df: pd.DataFrame) -> Dict[Tuple[str, ...], List[int]]:
        """Group skills by their ability signature (NAT, TRF)."""

        groups = defaultdict(list)

        for i, idx in enumerate(df.index):
            key_parts = []
            valid = True
            for facet_id in self.signature_facets:
                val = df.loc[idx, f'facet_{facet_id}']
                if pd.isna(val):
                    valid = False
                    break
                key_parts.append(str(val))

            if valid:
                archetype_key = tuple(key_parts)
                groups[archetype_key].append(i)  # Store position index, not df index

        logger.info(f"Found {len(groups)} unique archetype signatures")

        # Log size distribution
        sizes = [len(v) for v in groups.values()]
        if sizes:
            logger.info(
                f"  Archetype sizes: min={min(sizes)}, max={max(sizes)}, "
                f"median={sorted(sizes)[len(sizes)//2]}, "
                f"total groups with >={self.min_archetype_size} skills: "
                f"{sum(1 for s in sizes if s >= self.min_archetype_size)}"
            )

        return dict(groups)

    # ═══════════════════════════════════════════════════════════════
    #  STEP 3: PROCESS INDIVIDUAL ARCHETYPE
    # ═══════════════════════════════════════════════════════════════

    def _process_archetype(
        self,
        archetype_key: Tuple[str, ...],
        group_positions: List[int],
        df: pd.DataFrame,
        embeddings: np.ndarray
    ) -> Optional[AbilityArchetype]:
        """Process a single archetype: sub-cluster + build progression ladders."""

        nat_code, trf_code = archetype_key
        archetype_id = f"{nat_code}_{trf_code}"

        # Get facet names
        nat_name = ALL_FACETS.get('NAT', {}).get('values', {}).get(nat_code, {}).get('name', nat_code)
        trf_name = ALL_FACETS.get('TRF', {}).get('values', {}).get(trf_code, {}).get('name', trf_code)

        label = f"{nat_name} + {trf_name}"

        # Extract embeddings for this archetype
        arch_embeddings = embeddings[group_positions]
        arch_df_indices = [df.index[pos] for pos in group_positions]

        # Sub-cluster using agglomerative clustering
        cluster_labels = self._agglomerative_subcluster(arch_embeddings)

        # Build sub-clusters with progression ladders
        sub_clusters = []
        unclassified_skills = []

        unique_labels = set(cluster_labels)
        for cl_label in sorted(unique_labels):
            cl_mask = [i for i, l in enumerate(cluster_labels) if l == cl_label]

            if cl_label == -1:
                # Noise points
                for pos_in_arch in cl_mask:
                    df_idx = arch_df_indices[pos_in_arch]
                    unclassified_skills.append(self._extract_skill_summary(df, df_idx))
                continue

            if len(cl_mask) < self.min_subcluster_size:
                # Too small — treat as unclassified
                for pos_in_arch in cl_mask:
                    df_idx = arch_df_indices[pos_in_arch]
                    unclassified_skills.append(self._extract_skill_summary(df, df_idx))
                continue

            # Build sub-cluster
            cl_positions = [group_positions[i] for i in cl_mask]
            cl_df_indices = [arch_df_indices[i] for i in cl_mask]
            cl_embeddings = arch_embeddings[cl_mask]

            sub_cluster = self._build_subcluster(
                cluster_id=f"{archetype_id}_SC{cl_label:03d}",
                archetype_id=archetype_id,
                df=df,
                df_indices=cl_df_indices,
                cl_embeddings=cl_embeddings,
                all_arch_embeddings=arch_embeddings,
                cl_mask=cl_mask
            )
            sub_clusters.append(sub_cluster)

        # Compute archetype-level statistics
        asced_coverage = defaultdict(int)
        level_distribution = defaultdict(int)
        for pos in group_positions:
            df_idx = df.index[pos]
            # ASCED
            asced_val = df.loc[df_idx, f'facet_{self.industry_facet}'] if f'facet_{self.industry_facet}' in df.columns else None
            if pd.notna(asced_val):
                if isinstance(asced_val, str) and asced_val.startswith('['):
                    try:
                        for code in json.loads(asced_val):
                            asced_coverage[code] += 1
                    except:
                        asced_coverage[str(asced_val)] += 1
                else:
                    asced_coverage[str(asced_val)] += 1
            # Level
            lvl_val = df.loc[df_idx, f'facet_LVL'] if 'facet_LVL' in df.columns else None
            if pd.notna(lvl_val):
                try:
                    lvl_int = int(str(lvl_val).replace('LVL.', ''))
                    level_distribution[lvl_int] += 1
                except:
                    pass

        # Progression summary
        progression_summary = defaultdict(int)
        for sc in sub_clusters:
            progression_summary[sc.progression_type] += 1

        return AbilityArchetype(
            archetype_id=archetype_id,
            nat_code=nat_code,
            nat_name=nat_name,
            trf_code=trf_code,
            trf_name=trf_name,
            label=label,
            sub_clusters=sub_clusters,
            unclassified_skills=unclassified_skills,
            total_skills=len(group_positions),
            asced_coverage=dict(asced_coverage),
            level_distribution=dict(level_distribution),
            progression_summary=dict(progression_summary),
        )

    # ═══════════════════════════════════════════════════════════════
    #  AGGLOMERATIVE SUB-CLUSTERING
    # ═══════════════════════════════════════════════════════════════

    def _agglomerative_subcluster(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Sub-cluster embeddings using agglomerative clustering with
        complete linkage and cosine distance. Uses adaptive distance threshold.

        Complete linkage merges clusters based on the maximum distance between
        any pair of members, producing tighter, more coherent clusters than
        average linkage. This prevents chain-effect merges where A~B and B~C
        leads to A and C being grouped even when they are dissimilar.
        """
        n = len(embeddings)

        if n < self.min_subcluster_size:
            return np.zeros(n, dtype=int)

        # Compute pairwise cosine similarity
        if self.embedding_interface is not None:
            sim_matrix = self.embedding_interface.similarity(embeddings, embeddings)
        else:
            sim_matrix = np.dot(embeddings, embeddings.T)

        sim_matrix = np.clip(sim_matrix, 0.0, 1.0)

        # Convert to cosine distance
        dist_matrix = 1.0 - sim_matrix
        np.fill_diagonal(dist_matrix, 0.0)

        # Adaptive threshold
        threshold = self._compute_adaptive_threshold(dist_matrix)

        # Condensed form for scipy
        dist_condensed = squareform(dist_matrix, checks=False)

        # Agglomerative clustering with complete linkage
        # Complete linkage uses the maximum distance between any two members
        # of merging clusters, preventing chain-effect merges of unrelated skills
        Z = linkage(dist_condensed, method='complete')
        labels = fcluster(Z, t=threshold, criterion='distance')

        # Shift to 0-indexed
        labels = labels - 1

        n_clusters = len(set(labels))
        logger.debug(
            f"  Agglomerative clustering: {n} skills -> {n_clusters} sub-clusters "
            f"(threshold={threshold:.3f})"
        )

        return labels

    def _compute_adaptive_threshold(self, dist_matrix: np.ndarray) -> float:
        """
        Compute an adaptive distance threshold for agglomerative clustering.

        With complete linkage, the threshold represents the maximum allowed
        distance between ANY two members of a merged cluster. This needs to
        be tighter than with average linkage.

        Uses: threshold = median_dist - sigma * std_dist
        Clamped to [floor, ceiling].

        Median is used instead of mean for robustness to outlier pairs.
        """
        upper_tri = dist_matrix[np.triu_indices_from(dist_matrix, k=1)]

        if len(upper_tri) == 0:
            return self.distance_threshold_floor

        median_dist = float(np.median(upper_tri))
        std_dist = float(np.std(upper_tri))

        threshold = median_dist - self.distance_threshold_sigma * std_dist

        threshold = np.clip(
            threshold,
            self.distance_threshold_floor,
            self.distance_threshold_ceiling
        )

        return float(threshold)

    # ═══════════════════════════════════════════════════════════════
    #  BUILD SUB-CLUSTER WITH PROGRESSION LADDER
    # ═══════════════════════════════════════════════════════════════

    def _build_subcluster(
        self,
        cluster_id: str,
        archetype_id: str,
        df: pd.DataFrame,
        df_indices: List,
        cl_embeddings: np.ndarray,
        all_arch_embeddings: np.ndarray,
        cl_mask: List[int]
    ) -> SkillSubCluster:
        """Build a sub-cluster with progression ladder and metadata."""

        # Compute centroid
        centroid = cl_embeddings.mean(axis=0, keepdims=True)

        # Find representative skills (nearest to centroid)
        if self.embedding_interface is not None:
            dists_to_centroid = self.embedding_interface.similarity(centroid, cl_embeddings)[0]
        else:
            dists_to_centroid = np.dot(centroid, cl_embeddings.T)[0]

        top_k = min(self.representative_skill_count, len(df_indices))
        top_indices = np.argsort(dists_to_centroid)[-top_k:][::-1]

        representative_skills = []
        for ti in top_indices:
            df_idx = df_indices[ti]
            representative_skills.append(self._extract_skill_summary(df, df_idx))

        # Generate default label from top skill names
        label = self._generate_default_label(representative_skills)

        # Build progression ladder
        level_groups = defaultdict(list)
        asced_spread = defaultdict(int)
        asced_names_map = {}
        all_skill_ids = []

        for df_idx in df_indices:
            skill_id = df.loc[df_idx, 'skill_id'] if 'skill_id' in df.columns else str(df_idx)
            all_skill_ids.append(skill_id)

            # Get level
            lvl_val = df.loc[df_idx, 'facet_LVL'] if 'facet_LVL' in df.columns else None
            lvl_int = self._parse_level(lvl_val, df.loc[df_idx, 'level'] if 'level' in df.columns else 3)

            level_groups[lvl_int].append(df_idx)

            # Get ASCED
            asced_col = f'facet_{self.industry_facet}'
            if asced_col in df.columns and pd.notna(df.loc[df_idx, asced_col]):
                asced_val = df.loc[df_idx, asced_col]
                asced_name_col = f'facet_{self.industry_facet}_name'
                asced_name = df.loc[df_idx, asced_name_col] if asced_name_col in df.columns else ''

                if isinstance(asced_val, str) and asced_val.startswith('['):
                    try:
                        codes = json.loads(asced_val)
                        names = str(asced_name).split(', ') if asced_name else codes
                        for i, code in enumerate(codes):
                            asced_spread[code] += 1
                            if i < len(names):
                                asced_names_map[code] = names[i]
                    except:
                        asced_spread[str(asced_val)] += 1
                else:
                    asced_spread[str(asced_val)] += 1
                    asced_names_map[str(asced_val)] = str(asced_name) if asced_name else str(asced_val)

        # Build progression rungs
        progression = []
        for lvl in sorted(level_groups.keys()):
            rung_df_indices = level_groups[lvl]
            rung_skill_ids = []
            rung_skill_names = []
            rung_asced = set()
            rung_asced_names = set()

            for df_idx in rung_df_indices:
                sid = df.loc[df_idx, 'skill_id'] if 'skill_id' in df.columns else str(df_idx)
                sname = df.loc[df_idx, 'name']
                rung_skill_ids.append(sid)
                rung_skill_names.append(sname)

                # ASCED at this rung
                asced_col = f'facet_{self.industry_facet}'
                if asced_col in df.columns and pd.notna(df.loc[df_idx, asced_col]):
                    asced_val = df.loc[df_idx, asced_col]
                    if isinstance(asced_val, str) and asced_val.startswith('['):
                        try:
                            for code in json.loads(asced_val):
                                rung_asced.add(code)
                                if code in asced_names_map:
                                    rung_asced_names.add(asced_names_map[code])
                        except:
                            rung_asced.add(str(asced_val))
                    else:
                        rung_asced.add(str(asced_val))
                        if str(asced_val) in asced_names_map:
                            rung_asced_names.add(asced_names_map[str(asced_val)])

            progression.append(ProgressionRung(
                level=lvl,
                level_name=LEVEL_NAMES.get(lvl, f"Level {lvl}"),
                skill_ids=rung_skill_ids,
                skill_names=rung_skill_names,
                asced_fields=sorted(rung_asced),
                asced_names=sorted(rung_asced_names),
            ))

        # Classify progression type
        levels_present = sorted(level_groups.keys())
        level_span = (min(levels_present), max(levels_present)) if levels_present else (0, 0)
        level_gaps = self._find_level_gaps(levels_present)
        progression_type = self._classify_progression(levels_present, level_gaps)

        # Compute intra-cluster similarity
        avg_intra_sim = self._compute_intra_similarity(cl_embeddings)

        return SkillSubCluster(
            cluster_id=cluster_id,
            archetype_id=archetype_id,
            label=label,
            representative_skills=representative_skills,
            progression=progression,
            progression_type=progression_type,
            level_span=level_span,
            level_gaps=level_gaps,
            asced_spread=dict(asced_spread),
            asced_names=dict(asced_names_map),
            total_skills=len(df_indices),
            avg_intra_similarity=avg_intra_sim,
            skill_ids=all_skill_ids,
        )

    # ═══════════════════════════════════════════════════════════════
    #  PROGRESSION HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _parse_level(self, lvl_facet_val, lvl_col_val) -> int:
        """Parse level value from facet or column."""
        if pd.notna(lvl_facet_val):
            try:
                return int(str(lvl_facet_val).replace('LVL.', ''))
            except:
                pass
        try:
            return int(lvl_col_val)
        except:
            return 3

    def _find_level_gaps(self, levels_present: List[int]) -> List[int]:
        """Find missing levels between min and max."""
        if len(levels_present) < 2:
            return []
        full_range = set(range(min(levels_present), max(levels_present) + 1))
        return sorted(full_range - set(levels_present))

    def _classify_progression(self, levels_present: List[int], level_gaps: List[int]) -> str:
        """Classify progression type."""
        n_levels = len(levels_present)
        n_gaps = len(level_gaps)

        if n_levels <= 1:
            return 'flat'
        elif n_levels >= 4 and n_gaps <= 1:
            return 'full'
        elif n_levels >= 2 and n_gaps == 0:
            return 'partial'
        else:
            return 'sparse'

    # ═══════════════════════════════════════════════════════════════
    #  SIMILARITY & LABELLING HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _compute_intra_similarity(self, embeddings: np.ndarray) -> float:
        """Compute average pairwise cosine similarity within a cluster."""
        if len(embeddings) < 2:
            return 1.0

        if self.embedding_interface is not None:
            sim_matrix = self.embedding_interface.similarity(embeddings, embeddings)
        else:
            sim_matrix = np.dot(embeddings, embeddings.T)

        upper_tri = sim_matrix[np.triu_indices_from(sim_matrix, k=1)]
        return float(np.mean(upper_tri)) if len(upper_tri) > 0 else 1.0

    def _generate_default_label(self, representative_skills: List[Dict]) -> str:
        """Generate a default label from representative skill names."""
        if not representative_skills:
            return "Unnamed cluster"
        names = [s.get('name', '') for s in representative_skills[:3]]
        return " / ".join(names)

    def _extract_skill_summary(self, df: pd.DataFrame, df_idx) -> Dict:
        """Extract a skill summary dictionary from a dataframe row."""
        return {
            'skill_id': df.loc[df_idx, 'skill_id'] if 'skill_id' in df.columns else str(df_idx),
            'name': df.loc[df_idx, 'name'],
            'level': int(df.loc[df_idx, 'level']) if 'level' in df.columns else None,
            'category': df.loc[df_idx, 'category'] if 'category' in df.columns else '',
        }

    # ═══════════════════════════════════════════════════════════════
    #  STEP 4: LLM-BASED SUB-CLUSTER LABELLING
    # ═══════════════════════════════════════════════════════════════

    def _generate_llm_labels(self, archetypes: List[AbilityArchetype]):
        """
        Generate concise labels for sub-clusters using LLM.
        Includes retry logic with single-item regeneration on JSON parse failure.
        Tightened prompts to suppress verbose thinking.
        """
        if not self.genai_interface:
            return

        # Collect all sub-clusters that need labelling
        items_to_label = []
        for archetype in archetypes:
            for sc in archetype.sub_clusters:
                skill_names = [s['name'] for s in sc.representative_skills[:5]]
                items_to_label.append({
                    'archetype_id': archetype.archetype_id,
                    'cluster_id': sc.cluster_id,
                    'archetype_label': archetype.label,
                    'skill_names': skill_names,
                    'sub_cluster_ref': sc,
                })

        if not items_to_label:
            return

        logger.info(f"Generating LLM labels for {len(items_to_label)} sub-clusters...")

        system_prompt = (
            "You generate short labels for vocational skill clusters.\n\n"
            "RULES:\n"
            "- Output ONLY a JSON object: {\"label\": \"your label here\"}\n"
            "- The label must be 3-8 words capturing the common theme\n"
            "- Do NOT output any reasoning, explanation, or text outside the JSON\n"
            "- Do NOT wrap in markdown code blocks"
        )

        def _build_label_prompt(item):
            names_text = "\n".join(f"- {n}" for n in item['skill_names'])
            return (
                f"Archetype: {item['archetype_label']}\n"
                f"Skills:\n{names_text}\n\n"
                f"{{\"label\":"
            )

        # Process in batches
        for batch_start in range(0, len(items_to_label), self.llm_label_batch_size):
            batch = items_to_label[batch_start:batch_start + self.llm_label_batch_size]
            user_prompts = [_build_label_prompt(item) for item in batch]

            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=user_prompts,
                    system_prompt=system_prompt
                )

                for response, item in zip(responses, batch):
                    retry_count = MAX_LLM_RETRIES
                    current_response = response

                    while retry_count > 0:
                        try:
                            parsed = self.genai_interface._parse_json_response(current_response)
                            if parsed and isinstance(parsed, dict) and 'label' in parsed:
                                label = str(parsed['label']).strip()
                                if label:
                                    item['sub_cluster_ref'].label = label
                                    break
                                else:
                                    raise ValueError("Empty label")
                            else:
                                raise ValueError(f"Response missing 'label' key: {type(parsed)}")

                        except Exception as e:
                            retry_count -= 1
                            if retry_count > 0:
                                logger.debug(
                                    f"Retry label for {item['cluster_id']}, "
                                    f"{retry_count} attempts left: {e}"
                                )
                                try:
                                    single_responses = self.genai_interface._generate_batch(
                                        user_prompts=[_build_label_prompt(item)],
                                        system_prompt=system_prompt
                                    )
                                    current_response = single_responses[0]
                                except Exception as retry_e:
                                    logger.debug(f"Retry generation failed: {retry_e}")
                                    break
                            else:
                                logger.debug(
                                    f"All retries exhausted for label, "
                                    f"cluster {item['cluster_id']}"
                                )

            except Exception as e:
                logger.warning(f"LLM label generation batch failed: {e}")

    # ═══════════════════════════════════════════════════════════════
    #  STEP 5: STATISTICS
    # ═══════════════════════════════════════════════════════════════

    def _compute_statistics(
        self,
        archetypes: List[AbilityArchetype],
        df_valid: pd.DataFrame,
        df_excluded: pd.DataFrame
    ) -> Dict[str, Any]:
        """Compute comprehensive statistics."""

        total_sub_clusters = sum(len(a.sub_clusters) for a in archetypes)
        total_unclassified = sum(len(a.unclassified_skills) for a in archetypes)

        # Progression type distribution
        progression_dist = defaultdict(int)
        for a in archetypes:
            for sc in a.sub_clusters:
                progression_dist[sc.progression_type] += 1

        # ASCED spread across archetypes
        asced_archetype_count = defaultdict(int)
        for a in archetypes:
            for code in a.asced_coverage:
                asced_archetype_count[code] += 1

        # Average intra-similarity
        all_intra_sims = []
        for a in archetypes:
            for sc in a.sub_clusters:
                all_intra_sims.append(sc.avg_intra_similarity)

        # Level coverage per sub-cluster
        level_spans = []
        for a in archetypes:
            for sc in a.sub_clusters:
                span = sc.level_span[1] - sc.level_span[0] + 1 if sc.level_span[0] > 0 else 0
                level_spans.append(span)

        stats = {
            'total_valid_skills': len(df_valid),
            'total_excluded_skills': len(df_excluded),
            'total_archetypes': len(archetypes),
            'total_sub_clusters': total_sub_clusters,
            'total_unclassified_skills': total_unclassified,
            'progression_type_distribution': dict(progression_dist),
            'avg_sub_clusters_per_archetype': (
                total_sub_clusters / len(archetypes) if archetypes else 0
            ),
            'avg_skills_per_sub_cluster': (
                sum(sc.total_skills for a in archetypes for sc in a.sub_clusters) / total_sub_clusters
                if total_sub_clusters > 0 else 0
            ),
            'avg_intra_similarity': float(np.mean(all_intra_sims)) if all_intra_sims else 0,
            'avg_level_span': float(np.mean(level_spans)) if level_spans else 0,
            'asced_fields_per_archetype': {
                code: count for code, count in sorted(
                    asced_archetype_count.items(), key=lambda x: -x[1]
                )[:20]
            },
            'archetype_size_distribution': {
                'min': min(a.total_skills for a in archetypes) if archetypes else 0,
                'max': max(a.total_skills for a in archetypes) if archetypes else 0,
                'mean': float(np.mean([a.total_skills for a in archetypes])) if archetypes else 0,
            },
        }

        return stats

    def _log_summary(self, archetypes: List[AbilityArchetype], stats: Dict):
        """Log summary of archetype clustering."""
        logger.info("\n" + "=" * 80)
        logger.info("ABILITY ARCHETYPE CLUSTERING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Valid skills: {stats['total_valid_skills']}")
        logger.info(f"Excluded (low confidence): {stats['total_excluded_skills']}")
        logger.info(f"Archetypes: {stats['total_archetypes']}")
        logger.info(f"Sub-clusters: {stats['total_sub_clusters']}")
        logger.info(f"Unclassified skills: {stats['total_unclassified_skills']}")
        logger.info(f"Avg sub-clusters per archetype: {stats['avg_sub_clusters_per_archetype']:.1f}")
        logger.info(f"Avg skills per sub-cluster: {stats['avg_skills_per_sub_cluster']:.1f}")
        logger.info(f"Avg intra-cluster similarity: {stats['avg_intra_similarity']:.3f}")
        logger.info(f"Avg level span: {stats['avg_level_span']:.1f}")

        logger.info("\nProgression type distribution:")
        for ptype, count in stats['progression_type_distribution'].items():
            logger.info(f"  {ptype}: {count}")

        # Top 5 largest archetypes
        top_archetypes = sorted(archetypes, key=lambda a: a.total_skills, reverse=True)[:5]
        logger.info("\nTop 5 largest archetypes:")
        for a in top_archetypes:
            logger.info(
                f"  {a.archetype_id}: {a.label} "
                f"({a.total_skills} skills, {len(a.sub_clusters)} sub-clusters)"
            )

    # ═══════════════════════════════════════════════════════════════
    #  SERIALIZATION
    # ═══════════════════════════════════════════════════════════════

    def archetypes_to_dict(self, archetypes: List[AbilityArchetype]) -> List[Dict]:
        """Convert archetypes to serializable dictionaries."""
        result = []
        for a in archetypes:
            arch_dict = {
                'archetype_id': a.archetype_id,
                'nat': {'code': a.nat_code, 'name': a.nat_name},
                'trf': {'code': a.trf_code, 'name': a.trf_name},
                'label': a.label,
                'total_skills': a.total_skills,
                'asced_coverage': a.asced_coverage,
                'level_distribution': {str(k): v for k, v in a.level_distribution.items()},
                'progression_summary': a.progression_summary,
                'sub_clusters': [],
                'unclassified_skills': a.unclassified_skills,
            }

            for sc in a.sub_clusters:
                sc_dict = {
                    'cluster_id': sc.cluster_id,
                    'label': sc.label,
                    'total_skills': sc.total_skills,
                    'progression_type': sc.progression_type,
                    'level_span': list(sc.level_span),
                    'level_gaps': sc.level_gaps,
                    'asced_spread': sc.asced_spread,
                    'asced_names': sc.asced_names,
                    'avg_intra_similarity': round(sc.avg_intra_similarity, 4),
                    'representative_skills': sc.representative_skills,
                    'skill_ids': sc.skill_ids,
                    'progression': [],
                }

                for rung in sc.progression:
                    sc_dict['progression'].append({
                        'level': rung.level,
                        'level_name': rung.level_name,
                        'skill_count': rung.skill_count,
                        'skill_ids': rung.skill_ids,
                        'skill_names': rung.skill_names,
                        'asced_fields': rung.asced_fields,
                        'asced_names': rung.asced_names,
                    })

                arch_dict['sub_clusters'].append(sc_dict)

            result.append(arch_dict)

        return result