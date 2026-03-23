"""
Archetype Builder for the Skill Assertion Pipeline.

Adapter that bridges the assertion pipeline's skill_registry dict format
with the ArchetypeClusterer from the faceted pipeline.

The assertion pipeline stores facets inside skill_registry[sid]["facets"],
and progression comes from assertions' level_of_engagement rather than
a facet_LVL column. This module handles that translation.

Usage in pipeline.py:
    from src.archetypes.archetype_builder import build_archetypes_from_registry
    archetypes, arch_stats = build_archetypes_from_registry(
        skill_registry, df, config, embedding_interface, genai_interface
    )
"""

import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

from src.clustering.archetype_clusterer import ArchetypeClusterer

logger = logging.getLogger(__name__)

# Assertion level → numeric for progression ordering
LEVEL_TO_INT = {
    "FOLLOW": 1, "ASSIST": 2, "APPLY": 3, "ENABLE": 4,
    "ENSURE_ADVISE": 5, "INITIATE_INFLUENCE": 6, "SET_STRATEGY": 7,
}


def build_archetypes_from_registry(
    skill_registry: Dict[str, Dict],
    df_assertions: pd.DataFrame,
    config: Dict,
    embedding_interface,
    genai_interface=None,
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Build ability archetypes from the assertion pipeline's skill registry.

    Steps:
    1. Convert skill_registry to a DataFrame with facet_NAT, facet_TRF, facet_COG columns
    2. Compute the dominant level per skill from its assertions
    3. Generate embeddings for unique skills
    4. Run ArchetypeClusterer
    5. Enrich archetypes with assertion-level progression data
       (uses actual assertion levels, not facet_LVL)
    6. Return serialized archetypes + stats

    Args:
        skill_registry: {skill_id: {preferred_label, facets, unit_codes, ...}}
        df_assertions: Full assertions DataFrame with skill_id, level, context columns
        config: Pipeline config dict
        embedding_interface: For embedding generation and similarity
        genai_interface: Optional, for sub-cluster labelling

    Returns:
        (archetypes_list_of_dicts, statistics_dict)
    """
    logger.info("=" * 60)
    logger.info("BUILDING ABILITY ARCHETYPES (Assertion Pipeline)")
    logger.info("=" * 60)

    # ── Step 1: Build skills DataFrame with facet columns ─────────
    rows = []
    for sid, info in skill_registry.items():
        facets = info.get("facets", {})
        row = {
            "skill_id": sid,
            "name": info["preferred_label"],
            "description": info.get("definition", ""),
            "category": info.get("category", ""),
            "unit_codes": info.get("unit_codes", []),
            "alternative_labels": info.get("alternative_labels", []),
        }

        # Extract facet values into flat columns
        for fid in ["NAT", "TRF", "COG", "ASCED", "LVL"]:
            fdata = facets.get(fid, {})
            row[f"facet_{fid}"] = fdata.get("code") if fdata else None
            row[f"facet_{fid}_name"] = fdata.get("name") if fdata else None
            row[f"facet_{fid}_confidence"] = float(fdata.get("confidence", 0)) if fdata else 0.0

        # Compute dominant level from assertions
        skill_assertions = df_assertions[df_assertions["skill_id"] == sid]
        if len(skill_assertions) > 0:
            level_counts = skill_assertions["level"].value_counts()
            dominant_level = int(level_counts.index[0])
        else:
            dominant_level = 3  # Default

        row["level"] = dominant_level
        row["context"] = "hybrid"  # Not used for clustering, just for compatibility

        # Build LVL facet from assertions if not already assigned
        if row["facet_LVL"] is None:
            row["facet_LVL"] = f"LVL.{dominant_level}"
            row["facet_LVL_name"] = _level_name(dominant_level)
            row["facet_LVL_confidence"] = 1.0

        rows.append(row)

    df_skills = pd.DataFrame(rows)
    df_skills = df_skills.reset_index(drop=True)
    logger.info(f"Prepared {len(df_skills)} skills for archetype clustering")

    # ── Step 2: Generate embeddings ───────────────────────────────
    logger.info("Generating embeddings for skill names...")
    texts = df_skills["name"].tolist()
    embeddings = embedding_interface.encode(
        texts,
        batch_size=config["embedding"].get("batch_size", 64),
        normalize_embeddings=config["embedding"].get("normalize_embeddings", True),
    )
    logger.info(f"Embeddings shape: {embeddings.shape}")

    # ── Step 3: Run ArchetypeClusterer ────────────────────────────
    clusterer = ArchetypeClusterer(
        config,
        embedding_interface=embedding_interface,
        genai_interface=genai_interface,
    )

    archetypes, arch_stats = clusterer.build_archetypes(df_skills, embeddings)

    # ── Step 4: Enrich with assertion-level progression ───────────
    logger.info("Enriching archetypes with assertion-level progression data...")
    archetypes = _enrich_with_assertion_progression(
        archetypes, skill_registry, df_assertions
    )

    # ── Step 5: Serialize ─────────────────────────────────────────
    archetypes_data = clusterer.archetypes_to_dict(archetypes)

    # Add qualification/occupation coverage to each archetype
    for arch_dict, arch_obj in zip(archetypes_data, archetypes):
        qual_codes = set()
        occ_codes = set()
        for sc in arch_obj.sub_clusters:
            for sid in sc.skill_ids:
                info = skill_registry.get(sid, {})
                qual_codes.update(info.get("qualification_codes", []) if isinstance(info.get("qualification_codes"), list) else [])
                occ_codes.update(info.get("occupation_codes", []) if isinstance(info.get("occupation_codes"), list) else [])

        arch_dict["qualification_count"] = len(qual_codes)
        arch_dict["occupation_count"] = len(occ_codes)

    logger.info(f"Built {len(archetypes)} archetypes with {arch_stats.get('total_sub_clusters', 0)} sub-clusters")

    return archetypes_data, arch_stats


def _enrich_with_assertion_progression(archetypes, skill_registry, df_assertions):
    """
    Replace facet_LVL-based progression with actual assertion-level progression.

    For each sub-cluster, re-build the progression rungs using
    the level_of_engagement from assertions, which is richer than
    the single dominant level assigned to the skill.

    A skill can have assertions at multiple levels (e.g., APPLY in one unit,
    ENABLE in another). This captures that spread.
    """
    from src.clustering.archetype_clusterer import ProgressionRung, LEVEL_NAMES

    for archetype in archetypes:
        for sc in archetype.sub_clusters:
            # Group all assertions for skills in this sub-cluster by level
            level_groups = defaultdict(lambda: {"skill_ids": set(), "skill_names": set(), "asced_fields": set(), "asced_names": set()})

            for sid in sc.skill_ids:
                info = skill_registry.get(sid, {})
                skill_name = info.get("preferred_label", sid)

                # Get all assertions for this skill
                skill_assertions = df_assertions[df_assertions["skill_id"] == sid]

                for _, a_row in skill_assertions.iterrows():
                    lvl_str = str(a_row.get("level", 3))
                    try:
                        lvl_int = int(float(lvl_str))
                    except (ValueError, TypeError):
                        lvl_int = LEVEL_TO_INT.get(str(lvl_str).upper(), 3)

                    lvl_int = max(1, min(7, lvl_int))

                    level_groups[lvl_int]["skill_ids"].add(sid)
                    level_groups[lvl_int]["skill_names"].add(skill_name)

                    # ASCED from skill facets
                    facets = info.get("facets", {})
                    asced_data = facets.get("ASCED", {})
                    if asced_data:
                        code = asced_data.get("code", "")
                        name = asced_data.get("name", "")
                        if isinstance(code, str) and code.startswith("["):
                            try:
                                codes = json.loads(code)
                                names = name.split(", ") if name else codes
                                for i, c in enumerate(codes):
                                    level_groups[lvl_int]["asced_fields"].add(c)
                                    if i < len(names):
                                        level_groups[lvl_int]["asced_names"].add(names[i])
                            except:
                                level_groups[lvl_int]["asced_fields"].add(str(code))
                        elif code:
                            level_groups[lvl_int]["asced_fields"].add(str(code))
                            if name:
                                level_groups[lvl_int]["asced_names"].add(name)

            # Rebuild progression rungs from assertion data
            if level_groups:
                new_progression = []
                for lvl in sorted(level_groups.keys()):
                    g = level_groups[lvl]
                    new_progression.append(ProgressionRung(
                        level=lvl,
                        level_name=LEVEL_NAMES.get(lvl, f"Level {lvl}"),
                        skill_ids=sorted(g["skill_ids"]),
                        skill_names=sorted(g["skill_names"]),
                        asced_fields=sorted(g["asced_fields"]),
                        asced_names=sorted(g["asced_names"]),
                    ))

                sc.progression = new_progression

                # Recompute progression metadata
                levels_present = sorted(level_groups.keys())
                sc.level_span = (min(levels_present), max(levels_present))
                full_range = set(range(min(levels_present), max(levels_present) + 1))
                sc.level_gaps = sorted(full_range - set(levels_present))

                n_levels = len(levels_present)
                n_gaps = len(sc.level_gaps)
                if n_levels <= 1:
                    sc.progression_type = "flat"
                elif n_levels >= 4 and n_gaps <= 1:
                    sc.progression_type = "full"
                elif n_levels >= 2 and n_gaps == 0:
                    sc.progression_type = "partial"
                else:
                    sc.progression_type = "sparse"

    return archetypes


def _level_name(level_int: int) -> str:
    """Map integer level to name."""
    names = {
        1: "Follow", 2: "Assist", 3: "Apply", 4: "Enable",
        5: "Ensure & Advise", 6: "Initiate & Influence", 7: "Set Strategy",
    }
    return names.get(level_int, f"Level {level_int}")
