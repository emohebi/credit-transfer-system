"""
Skill Deduplicator for the Assertion Pipeline.

Principle: Deduplicate skill LABELS, not teaching/context evidence.

Steps:
  1. Compute embeddings for unique skill names (not all 200k rows).
  2. Find clusters of semantically similar names (threshold ≥ 0.90).
  3. Optionally validate clusters with GenAI.
  4. Choose canonical name = most frequently occurring name in the cluster.
  5. Output: skill_groups mapping each group to a canonical Skill,
     and every original row becomes a SkillAssertion.
"""
import logging
import hashlib
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from collections import Counter, defaultdict
from tqdm import tqdm

logger = logging.getLogger(__name__)


class SkillDeduplicator:

    def __init__(self, config: Dict, embedding_interface=None, genai_interface=None):
        self.config = config
        self.embedding_interface = embedding_interface
        self.genai_interface = genai_interface

        dedup_cfg = config["dedup"]
        self.threshold = dedup_cfg["similarity_threshold"]
        self.use_genai = dedup_cfg["use_genai_validation"] and genai_interface is not None
        self.genai_batch_size = dedup_cfg["genai_batch_size"]
        self.max_candidates = dedup_cfg["max_candidates_per_skill"]

        logger.info(f"SkillDeduplicator: threshold={self.threshold}, genai={self.use_genai}")

    # ═══════════════════════════════════════════════════════════════
    #  PUBLIC API
    # ═══════════════════════════════════════════════════════════════

    def deduplicate(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Deduplicate skill names.

        Args:
            df: Preprocessed DataFrame (all rows = potential assertions)

        Returns:
            df with added column 'skill_id' mapping each row to its canonical skill,
            and a dict of {skill_id: SkillInfo} with canonical names and alt labels.
        """
        logger.info("=" * 60)
        logger.info("SKILL LABEL DEDUPLICATION")
        logger.info("=" * 60)

        # ── Step 1: Get unique names with counts ──────────────────
        name_counts = df["name"].value_counts()
        unique_names = name_counts.index.tolist()
        logger.info(f"Total rows: {len(df)}, Unique skill names: {len(unique_names)}")

        # ── Step 2: Embed unique names ────────────────────────────
        logger.info("Generating embeddings for unique skill names...")

        # Use name + best description for embedding
        name_to_desc = {}
        for name in unique_names:
            rows = df[df["name"] == name]
            # Pick the longest description for this name
            descs = rows["description"].dropna().astype(str)
            best = descs.loc[descs.str.len().idxmax()] if len(descs) > 0 else ""
            name_to_desc[name] = best
        # "{name}. {name_to_desc[name]}"
        texts = [f"{name}".strip() for name in unique_names]
        embeddings = self.embedding_interface.encode(
            texts,
            batch_size=self.config["embedding"]["batch_size"],
            normalize_embeddings=self.config["embedding"]["normalize_embeddings"],
        )
        logger.info(f"Embeddings shape: {embeddings.shape}")

        # ── Step 3: Find clusters ─────────────────────────────────
        logger.info(f"Computing similarity and clustering at threshold {self.threshold}...")
        clusters = self._cluster_names(unique_names, embeddings)
        logger.info(f"Found {len(clusters)} skill clusters from {len(unique_names)} unique names")

        # ── Step 4: Optionally validate with GenAI ────────────────
        if self.use_genai:
            multi_clusters = [c for c in clusters if len(c) > 1]
            if multi_clusters:
                logger.info(f"Validating {len(multi_clusters)} multi-name clusters with GenAI...")
                clusters = self._validate_clusters_genai(clusters, name_counts)

        # ── Step 5: Build skill registry ──────────────────────────
        skill_registry, name_to_skill_id = self._build_skill_registry(
            clusters, name_counts, df, name_to_desc
        )

        # ── Step 6: Assign skill_id to every row ─────────────────
        df = df.copy()
        df["skill_id"] = df["name"].map(name_to_skill_id)

        # Handle any unmapped names (shouldn't happen, but safety)
        unmapped = df["skill_id"].isna().sum()
        if unmapped > 0:
            logger.warning(f"{unmapped} rows could not be mapped to a skill_id")
            df["skill_id"] = df["skill_id"].fillna("SKL-UNMAPPED")

        # ── Log stats ─────────────────────────────────────────────
        single_name = sum(1 for c in clusters if len(c) == 1)
        merged = sum(1 for c in clusters if len(c) > 1)
        total_alt = sum(len(info["alternative_labels"]) for info in skill_registry.values())

        logger.info("=" * 60)
        logger.info("DEDUPLICATION RESULTS")
        logger.info(f"  Unique names input:    {len(unique_names)}")
        logger.info(f"  Skills output:         {len(skill_registry)}")
        logger.info(f"  Single-name skills:    {single_name}")
        logger.info(f"  Merged clusters:       {merged}")
        logger.info(f"  Alternative labels:    {total_alt}")
        logger.info(f"  Assertions (all rows): {len(df)}")
        logger.info("=" * 60)

        return df, skill_registry

    # ═══════════════════════════════════════════════════════════════
    #  CLUSTERING
    # ═══════════════════════════════════════════════════════════════

    def _cluster_names(
        self, names: List[str], embeddings: np.ndarray
    ) -> List[List[str]]:
        """Union-find clustering based on pairwise similarity ≥ threshold."""
        n = len(names)

        # Parent array for union-find
        parent = list(range(n))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[ra] = rb

        # Compute similarity in batches to manage memory
        batch_size = 1000
        for i in tqdm(range(0, n, batch_size), desc="Clustering"):
            end_i = min(i + batch_size, n)
            # Only check upper triangle: j >= i
            sims = self.embedding_interface.similarity(
                embeddings[i:end_i], embeddings[i:]
            )
            for local_i in range(end_i - i):
                global_i = i + local_i
                for local_j in range(sims.shape[1]):
                    global_j = i + local_j
                    if global_j <= global_i:
                        continue
                    if sims[local_i, local_j] >= self.threshold:
                        union(global_i, global_j)

        # Collect clusters
        groups = defaultdict(list)
        for idx in range(n):
            groups[find(idx)].append(names[idx])

        return list(groups.values())

    # ═══════════════════════════════════════════════════════════════
    #  GENAI VALIDATION
    # ═══════════════════════════════════════════════════════════════

    def _validate_clusters_genai(
        self, clusters: List[List[str]], name_counts: pd.Series
    ) -> List[List[str]]:
        """Use LLM to validate whether names in a cluster are truly the same skill."""
        multi_clusters = [c for c in clusters if len(c) > 1]
        single_clusters = [c for c in clusters if len(c) == 1]

        validated = list(single_clusters)  # Singles pass through

        system_prompt = (
            "You are an expert in vocational skills classification.\n"
            "Given a group of skill names, decide which ones refer to the SAME skill.\n"
            "Return a JSON object with a key 'groups' containing a list of lists.\n"
            "Each inner list is a group of skill names that are the same skill.\n"
            "If all are the same skill, return one group. If some are different, split them.\n"
            "Respond with valid JSON only."
        )

        for batch_start in range(0, len(multi_clusters), self.genai_batch_size):
            batch = multi_clusters[batch_start : batch_start + self.genai_batch_size]
            user_prompts = []

            for cluster in batch:
                names_text = "\n".join(f"  {i+1}. {name}" for i, name in enumerate(cluster))
                user_prompts.append(
                    f"Are these skill names referring to the SAME skill?\n\n{names_text}\n\n"
                    f'Respond with JSON: {{"groups": [[...], ...]}}'
                )

            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=user_prompts, system_prompt=system_prompt
                )

                for cluster, response in zip(batch, responses):
                    try:
                        parsed = self.genai_interface._parse_json_response(response)
                        if isinstance(parsed, dict) and "groups" in parsed:
                            for group in parsed["groups"]:
                                # Map numbered items back to names
                                if all(isinstance(g, int) for g in group):
                                    sub = [cluster[g - 1] for g in group if 1 <= g <= len(cluster)]
                                elif all(isinstance(g, str) for g in group):
                                    sub = [n for n in group if n in cluster]
                                else:
                                    sub = list(cluster)
                                if sub:
                                    validated.append(sub)
                        else:
                            validated.append(cluster)  # Fallback: keep as-is
                    except Exception:
                        validated.append(cluster)
            except Exception as e:
                logger.warning(f"GenAI validation batch failed: {e}. Keeping clusters as-is.")
                validated.extend(batch)

        logger.info(f"After GenAI validation: {len(validated)} clusters")
        return validated

    # ═══════════════════════════════════════════════════════════════
    #  BUILD SKILL REGISTRY
    # ═══════════════════════════════════════════════════════════════

    def _build_skill_registry(
        self,
        clusters: List[List[str]],
        name_counts: pd.Series,
        df: pd.DataFrame,
        name_to_desc: Dict[str, str],
    ) -> Tuple[Dict, Dict[str, str]]:
        """
        Build the skill registry from clusters.
        Canonical name = most frequently occurring name in the cluster.

        Returns:
            skill_registry: {skill_id: {preferred_label, alternative_labels, definition, category}}
            name_to_skill_id: {original_name: skill_id}
        """
        skill_registry = {}
        name_to_skill_id = {}

        for cluster_idx, cluster in enumerate(clusters):
            # Choose canonical name: most frequent
            counts = {name: name_counts.get(name, 0) for name in cluster}
            canonical = max(counts, key=counts.get)

            # Alternative labels: everything else in the cluster
            alt_labels = sorted(set(n for n in cluster if n != canonical))

            # Skill ID: deterministic hash from canonical name
            skill_id = self._make_skill_id(canonical, cluster_idx)

            # Best definition: longest description across all names in the cluster
            best_desc = ""
            for name in cluster:
                desc = name_to_desc.get(name, "")
                if len(desc) > len(best_desc):
                    best_desc = desc

            # Most common category
            categories = []
            for name in cluster:
                cats = df[df["name"] == name]["category"].tolist()
                categories.extend(cats)
            most_common_cat = Counter(categories).most_common(1)
            category = most_common_cat[0][0] if most_common_cat else "general"

            # All unit codes
            unit_codes = []
            for name in cluster:
                codes = df[df["name"] == name]["code"].unique().tolist()
                unit_codes.extend(codes)
            unit_codes = sorted(set(unit_codes))

            # Total assertion count
            assertion_count = sum(counts.values())

            skill_registry[skill_id] = {
                "skill_id": skill_id,
                "preferred_label": canonical,
                "alternative_labels": alt_labels,
                "definition": best_desc,
                "category": category,
                "unit_codes": unit_codes,
                "assertion_count": assertion_count,
            }

            # Map all names to this skill_id
            for name in cluster:
                name_to_skill_id[name] = skill_id

        return skill_registry, name_to_skill_id

    def _make_skill_id(self, canonical_name: str, idx: int) -> str:
        """Create a deterministic skill ID."""
        h = hashlib.md5(canonical_name.lower().encode()).hexdigest()[:6]
        return f"SKL-{idx:05d}-{h}"
