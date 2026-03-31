"""
Ability Grouper for the Skill Assertion Pipeline.

Replaces archetype clustering with facet-based grouping:
  TRF (Transferability) → THA (Transferable Human Ability) → LVL (Progression)

No clustering algorithm needed — skills are grouped by their assigned
THA facet values, and progression ladders are built from LVL values
within each THA group.

Produces the same output format as the old ArchetypeClusterer so the
search engine HTML works without changes.

Output structure:
  archetypes_data = [
    {
      "archetype_id": "TRF.BRD",        # TRF code
      "label": "Cross-Sector",           # TRF name
      "nat": ..., "trf": ...,            # kept for compatibility
      "total_skills": N,
      "sub_clusters": [
        {
          "cluster_id": "THA.BRD.RSK",   # THA code
          "label": "Risk Assessment & Mitigation",  # THA name
          "skill_ids": [...],
          "total_skills": N,
          "progression_type": "full|partial|flat|sparse",
          "level_span": [min, max],
          "level_gaps": [...],
          "progression": [
            {"level": 1, "level_name": "Follow", "skill_count": N,
             "skill_ids": [...], "skill_names": [...]}
          ],
          ...
        }
      ]
    }
  ]
"""

import logging
import json
import pandas as pd
from typing import Dict, List, Any, Tuple
from collections import defaultdict

from config.facets import ALL_FACETS
from config.tha_facet import TRF_TO_THA

logger = logging.getLogger(__name__)

LEVEL_NAMES = {
    1: "Follow", 2: "Assist", 3: "Apply", 4: "Enable",
    5: "Ensure & Advise", 6: "Initiate & Influence", 7: "Set Strategy",
}


def build_ability_groups(
    skill_registry: Dict[str, Dict],
    df_assertions: pd.DataFrame,
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Build ability groups from THA facet assignments.

    Args:
        skill_registry: {skill_id: {preferred_label, facets, ...}}
        df_assertions: Full assertions DataFrame with skill_id, level columns

    Returns:
        (groups_data, statistics) in the same format as the old clusterer output
    """
    logger.info("=" * 60)
    logger.info("BUILDING ABILITY GROUPS (THA facet-based)")
    logger.info("=" * 60)

    # ── Step 1: Group skills by THA ───────────────────────────
    tha_groups = defaultdict(list)  # THA code → [skill_ids]
    unassigned = []

    for sid, info in skill_registry.items():
        facets = info.get("facets", {})
        tha_data = facets.get("THA", {})
        tha_code = tha_data.get("code", "")

        if not tha_code:
            unassigned.append(sid)
            continue

        # Handle legacy JSON-wrapped codes (e.g. '["THA.BRD.RSK"]')
        if isinstance(tha_code, str) and tha_code.startswith("["):
            try:
                codes = json.loads(tha_code)
                tha_code = codes[0] if codes else ""
            except (json.JSONDecodeError, TypeError):
                pass

        if tha_code:
            tha_groups[tha_code].append(sid)
        else:
            unassigned.append(sid)

    logger.info(f"Skills with THA: {sum(len(v) for v in tha_groups.values())}")
    logger.info(f"Skills without THA: {len(unassigned)}")
    logger.info(f"Unique THA groups: {len(tha_groups)}")

    # ── Step 2: Organize by TRF parent ────────────────────────
    trf_to_subclusters = defaultdict(list)

    tha_values = ALL_FACETS.get("THA", {}).get("values", {})
    trf_values = ALL_FACETS.get("TRF", {}).get("values", {})

    for tha_code, skill_ids in sorted(tha_groups.items()):
        tha_info = tha_values.get(tha_code, {})
        parent_trf = tha_info.get("parent_trf", "")

        if not parent_trf:
            # Infer from code prefix: THA.BRD.RSK → TRF.BRD
            parts = tha_code.split(".")
            if len(parts) >= 2:
                parent_trf = f"TRF.{parts[1]}"

        # Build progression ladder from assertion levels
        sc_data = _build_subcluster(
            cluster_id=tha_code,
            label=tha_info.get("name", tha_code),
            skill_ids=skill_ids,
            skill_registry=skill_registry,
            df_assertions=df_assertions,
        )

        trf_to_subclusters[parent_trf].append(sc_data)

    # ── Step 3: Build archetype-level dicts (one per TRF) ─────
    archetypes_data = []

    for trf_code in ["TRF.UNI", "TRF.BRD", "TRF.SEC", "TRF.OCC"]:
        subclusters = trf_to_subclusters.get(trf_code, [])
        if not subclusters:
            continue

        trf_info = trf_values.get(trf_code, {})
        trf_name = trf_info.get("name", trf_code)

        total_skills = sum(sc["total_skills"] for sc in subclusters)

        # Level distribution across all subclusters
        level_dist = defaultdict(int)
        for sc in subclusters:
            for rung in sc.get("progression", []):
                level_dist[rung["level"]] += rung["skill_count"]

        # Progression summary
        prog_summary = defaultdict(int)
        for sc in subclusters:
            prog_summary[sc["progression_type"]] += 1

        # Sort subclusters by total_skills descending
        subclusters.sort(key=lambda x: x["total_skills"], reverse=True)

        archetypes_data.append({
            "archetype_id": trf_code,
            "label": trf_name,
            "nat": {"code": "", "name": ""},  # Not applicable for THA grouping
            "trf": {"code": trf_code, "name": trf_name},
            "total_skills": total_skills,
            "sub_clusters": subclusters,
            "unclassified_skills": [],
            "level_distribution": {str(k): v for k, v in sorted(level_dist.items())},
            "progression_summary": dict(prog_summary),
            "asced_coverage": {},
            "qualification_count": 0,
            "occupation_count": 0,
        })

    # ── Step 4: Statistics ────────────────────────────────────
    total_subclusters = sum(len(a["sub_clusters"]) for a in archetypes_data)
    total_skills_grouped = sum(a["total_skills"] for a in archetypes_data)

    prog_dist = defaultdict(int)
    for a in archetypes_data:
        for sc in a["sub_clusters"]:
            prog_dist[sc["progression_type"]] += 1

    stats = {
        "total_valid_skills": len(skill_registry),
        "total_excluded_skills": len(unassigned),
        "total_archetypes": len(archetypes_data),
        "total_sub_clusters": total_subclusters,
        "total_unclassified_skills": len(unassigned),
        "total_skills_grouped": total_skills_grouped,
        "progression_type_distribution": dict(prog_dist),
        "avg_sub_clusters_per_archetype": (
            total_subclusters / len(archetypes_data) if archetypes_data else 0
        ),
        "avg_skills_per_sub_cluster": (
            total_skills_grouped / total_subclusters if total_subclusters > 0 else 0
        ),
    }

    logger.info(f"Built {len(archetypes_data)} TRF groups with {total_subclusters} THA sub-groups")
    logger.info(f"Total skills grouped: {total_skills_grouped}")
    logger.info(f"Unassigned skills: {len(unassigned)}")
    for ptype, count in prog_dist.items():
        logger.info(f"  {ptype}: {count}")

    return archetypes_data, stats


def _build_subcluster(
    cluster_id: str,
    label: str,
    skill_ids: List[str],
    skill_registry: Dict[str, Dict],
    df_assertions: pd.DataFrame,
) -> Dict:
    """
    Build a sub-cluster dict for one THA group.

    Groups assertions by level to build progression rungs.
    A skill can appear at multiple levels if it has assertions at different levels.
    """
    # Group all assertions for skills in this group by level
    level_groups = defaultdict(lambda: {"skill_ids": set(), "skill_names": set()})

    for sid in skill_ids:
        info = skill_registry.get(sid, {})
        skill_name = info.get("preferred_label", sid)

        skill_assertions = df_assertions[df_assertions["skill_id"] == sid]

        if len(skill_assertions) == 0:
            # No assertions — use LVL facet
            facets = info.get("facets", {})
            lvl_data = facets.get("LVL", {})
            lvl_code = lvl_data.get("code", "LVL.3")
            try:
                lvl_int = int(str(lvl_code).replace("LVL.", ""))
            except (ValueError, TypeError):
                lvl_int = 3
            lvl_int = max(1, min(7, lvl_int))
            level_groups[lvl_int]["skill_ids"].add(sid)
            level_groups[lvl_int]["skill_names"].add(skill_name)
        else:
            for _, a_row in skill_assertions.iterrows():
                try:
                    lvl_int = int(float(a_row.get("level", 3)))
                except (ValueError, TypeError):
                    lvl_int = 3
                lvl_int = max(1, min(7, lvl_int))
                level_groups[lvl_int]["skill_ids"].add(sid)
                level_groups[lvl_int]["skill_names"].add(skill_name)

    # Build progression rungs
    progression = []
    for lvl in sorted(level_groups.keys()):
        g = level_groups[lvl]
        progression.append({
            "level": lvl,
            "level_name": LEVEL_NAMES.get(lvl, f"Level {lvl}"),
            "skill_count": len(g["skill_ids"]),
            "skill_ids": sorted(g["skill_ids"]),
            "skill_names": sorted(g["skill_names"]),
            "asced_fields": [],
            "asced_names": [],
        })

    # Classify progression type
    levels_present = sorted(level_groups.keys())
    if len(levels_present) == 0:
        level_span = [0, 0]
        level_gaps = []
        progression_type = "flat"
    else:
        level_span = [min(levels_present), max(levels_present)]
        full_range = set(range(min(levels_present), max(levels_present) + 1))
        level_gaps = sorted(full_range - set(levels_present))

        n_levels = len(levels_present)
        n_gaps = len(level_gaps)
        if n_levels <= 1:
            progression_type = "flat"
        elif n_levels >= 4 and n_gaps <= 1:
            progression_type = "full"
        elif n_levels >= 2 and n_gaps == 0:
            progression_type = "partial"
        else:
            progression_type = "sparse"

    # Unique skill_ids (a skill might appear at multiple levels)
    all_unique_sids = set()
    for lvl_data in level_groups.values():
        all_unique_sids.update(lvl_data["skill_ids"])

    return {
        "cluster_id": cluster_id,
        "label": label,
        "total_skills": len(all_unique_sids),
        "skill_ids": sorted(all_unique_sids),
        "progression_type": progression_type,
        "level_span": level_span,
        "level_gaps": level_gaps,
        "avg_intra_similarity": 0.0,  # Not applicable for facet-based grouping
        "progression": progression,
        "representative_skills": [],
        "asced_spread": {},
        "asced_names": {},
    }