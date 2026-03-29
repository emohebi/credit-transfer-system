"""
Skill Assertion Pipeline — Main Orchestrator

Five-object model + Ability Archetypes:
  Skill → SkillAssertion → Unit → Qualification → Occupation (ANZSCO)
  Skill → Ability Archetype → Sub-cluster → Progression Ladder

Pipeline steps:
  1. Preprocess data (clean, normalize — keep all rows)
  2. Load concordance (needed early for LVL assignment)
  3. Reassign proficiency levels (LVL facet-based, per assertion row)
  4. Deduplicate skill LABELS (embed unique names, cluster, validate)
  5. Assign remaining facets (NAT, TRF, COG, ASCED) to deduplicated Skills
  6. Build ability archetypes with progression ladders
  7. Build five-object schema with precomputed traversals + export
"""
import logging
import json
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import asdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from config.settings import CONFIG
from config.facets import ALL_FACETS
from src.data_processing.preprocessor import AssertionDataPreprocessor
from src.data_processing.concordance import ConcordanceData, load_concordance
from src.dedup.deduplicator import SkillDeduplicator
from src.export.assertion_builder import AssertionBuilder

logger = logging.getLogger(__name__)


class SkillAssertionPipeline:
    """
    Orchestrates:
      preprocess → load concordance → reassign levels → dedup labels
      → assign facets → build archetypes → build schema → export.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or CONFIG
        self.preprocessor = AssertionDataPreprocessor(self.config)

        # Lazy-init interfaces
        self.embedding_interface = None
        self.genai_interface = None

        # Init interfaces
        logger.info("\nInitialising model interfaces...")
        self._init_embedding()
        self._init_genai()

    # ═══════════════════════════════════════════════════════════════
    #  INTERFACE INITIALISATION
    # ═══════════════════════════════════════════════════════════════

    def _init_embedding(self):
        if self.embedding_interface is not None:
            return
        try:
            from src.interfaces.embedding_interface import EmbeddingInterface
            cfg = self.config["embedding"]
            self.embedding_interface = EmbeddingInterface(
                model_name=cfg["model_name"],
                device=cfg.get("device", "cuda"),
                batch_size=cfg.get("batch_size", 64),
                model_cache_dir=cfg.get("model_cache_dir"),
                external_model_dir=cfg.get("external_model_dir"),
            )
            logger.info(f"Embedding interface ready: {cfg['model_name']}")
        except Exception as e:
            logger.error(f"Failed to init embedding interface: {e}")
            raise

    def _init_genai(self):
        if self.genai_interface is not None:
            return
        try:
            from src.interfaces.model_factory import ModelFactory
            self.genai_interface = ModelFactory.create_genai_interface(self.config)
            if self.genai_interface:
                logger.info("GenAI interface ready")
            else:
                logger.warning("GenAI interface not available — will skip LLM steps")
        except Exception as e:
            logger.warning(f"Could not init GenAI interface: {e}")

    # ═══════════════════════════════════════════════════════════════
    #  LEVEL REASSIGNMENT (EARLY STEP)
    # ═══════════════════════════════════════════════════════════════

    def _reassign_levels(self, df: pd.DataFrame, concordance, skip_genai: bool = False):
        """
        Reassign proficiency levels using LVL facet embedding similarity.
        Runs on ALL rows (before dedup) so every assertion gets a
        facet-derived level. Uses unit title context from concordance.

        Args:
            df: Preprocessed DataFrame (all rows)
            concordance: ConcordanceData (may be None)
            skip_genai: Skip LLM re-ranking for ambiguous cases

        Returns:
            DataFrame with 'level' overwritten and 'level_confidence' added
        """
        from src.facets.level_reassigner import LevelReassigner

        reassigner = LevelReassigner(
            config=self.config,
            embedding_interface=self.embedding_interface,
            genai_interface=self.genai_interface if not skip_genai else None,
        )

        return reassigner.reassign_levels(df, concordance)

    # ═══════════════════════════════════════════════════════════════
    #  EMBEDDING GENERATION (SINGLE PASS)
    # ═══════════════════════════════════════════════════════════════

    def _generate_skill_embeddings(self, df_unique: pd.DataFrame, concordance=None):
        """
        Generate all embeddings needed for the pipeline in a single pass.

        Returns:
            skill_embeddings: np.ndarray of shape (n_skills, embed_dim)
                Embeddings from skill name text, used for non-ASCED facets
                and archetype clustering.
            asced_embeddings: np.ndarray or None
                Embeddings from unit-title-enriched text, used for ASCED
                facet assignment. None if ASCED is not being assigned or
                no concordance is available.
        """
        batch_size = self.config["embedding"]["batch_size"]
        normalize = self.config["embedding"]["normalize_embeddings"]

        # Primary embeddings: skill name text (used for NAT/TRF/COG facets + archetypes)
        texts = df_unique["embedding_text"].tolist()
        logger.info(f"Generating primary skill embeddings for {len(texts)} unique skills...")
        skill_embeddings = self.embedding_interface.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=normalize,
        )
        logger.info(f"Primary embeddings shape: {skill_embeddings.shape}")

        # ASCED embeddings: unit-title-enriched text (only if needed)
        asced_embeddings = None
        remaining_facets = self._get_remaining_facets()
        has_asced = "ASCED" in remaining_facets
        has_asced_col = "embedding_text_asced" in df_unique.columns

        if has_asced and has_asced_col and concordance:
            texts_asced = df_unique["embedding_text_asced"].tolist()
            logger.info(f"Generating ASCED-enriched embeddings for {len(texts_asced)} unique skills...")
            asced_embeddings = self.embedding_interface.encode(
                texts_asced,
                batch_size=batch_size,
                normalize_embeddings=normalize,
            )
            logger.info(f"ASCED embeddings shape: {asced_embeddings.shape}")

        return skill_embeddings, asced_embeddings

    # ═══════════════════════════════════════════════════════════════
    #  FACET ASSIGNMENT (REMAINING FACETS — excludes LVL)
    # ═══════════════════════════════════════════════════════════════

    def _get_remaining_facets(self) -> List[str]:
        """Get facets to assign at the skill level (excludes LVL, handled earlier)."""
        all_facets = self.config["facet_assignment"]["facets_to_assign"]
        return [f for f in all_facets if f != "LVL"]

    def _assign_facets_to_skills(self, skill_registry: Dict, df_unique_skills: pd.DataFrame,
                                  skill_embeddings: np.ndarray, asced_embeddings: np.ndarray = None,
                                  concordance=None):
        """
        Assign remaining facets (NAT, TRF, COG, ASCED) to deduplicated Skills.
        LVL is excluded — it was already assigned per-row in the early step.

        Uses precomputed embeddings + optional LLM re-ranking.
        """
        try:
            from src.facets.facet_assigner import FacetAssigner
        except ImportError:
            from src.clustering.facet_assigner import FacetAssigner

        assigner = FacetAssigner(
            self.config,
            genai_interface=self.genai_interface,
            embedding_interface=self.embedding_interface,
        )

        remaining_facets = self._get_remaining_facets()
        has_asced = "ASCED" in remaining_facets

        if has_asced and asced_embeddings is not None:
            non_asced = [f for f in remaining_facets if f != "ASCED"]
            asced_only = ["ASCED"]

            if non_asced:
                logger.info(f"  Assigning non-ASCED facets {non_asced} with skill text embeddings...")
                df_faceted = assigner.assign_facets(df_unique_skills, skill_embeddings, facets_override=non_asced)
            else:
                df_faceted = df_unique_skills.copy()

            logger.info("  Assigning ASCED facet with unit-title-enriched embeddings...")
            df_asced = assigner.assign_facets(df_unique_skills, asced_embeddings, facets_override=asced_only)

            asced_cols = [c for c in df_asced.columns if c.startswith("facet_ASCED")]
            for col in asced_cols:
                df_faceted[col] = df_asced[col]
        else:
            df_faceted = assigner.assign_facets(df_unique_skills, skill_embeddings, facets_override=remaining_facets)

        # Write facets back into skill_registry
        for _, row in df_faceted.iterrows():
            sid = row["skill_id"]
            if sid not in skill_registry:
                continue
            facets = skill_registry[sid].get("facets", {})
            for fid in remaining_facets:
                col = f"facet_{fid}"
                if col in row and pd.notna(row[col]):
                    facets[fid] = {
                        "code": row[col],
                        "name": row.get(f"facet_{fid}_name", row[col]),
                        "confidence": float(row.get(f"facet_{fid}_confidence", 0)),
                    }
            skill_registry[sid]["facets"] = facets

        return skill_registry

    def _assign_lvl_facet_to_registry(self, skill_registry: Dict, df: pd.DataFrame):
        """
        Compute the dominant LVL facet for each deduplicated skill from its
        assertion rows (which now have facet-assigned levels).

        This populates the LVL facet on the Skill object for export and
        archetype grouping.
        """
        logger.info("Computing dominant LVL facet per skill from reassigned assertion levels...")

        for sid, info in skill_registry.items():
            skill_assertions = df[df["skill_id"] == sid]
            if len(skill_assertions) > 0:
                level_counts = skill_assertions["level"].value_counts()
                dominant_level = int(level_counts.index[0])
                avg_conf = float(skill_assertions["level_confidence"].mean()) if "level_confidence" in skill_assertions.columns else 0.8
            else:
                dominant_level = 3
                avg_conf = 0.0

            facets = info.get("facets", {})
            facets["LVL"] = {
                "code": f"LVL.{dominant_level}",
                "name": _level_name(dominant_level),
                "confidence": avg_conf,
            }
            info["facets"] = facets

    # ═══════════════════════════════════════════════════════════════
    #  ARCHETYPE CLUSTERING
    # ═══════════════════════════════════════════════════════════════

    def _build_archetypes(self, skill_registry: Dict, df: pd.DataFrame,
                           skill_embeddings: np.ndarray, df_unique: pd.DataFrame,
                           skip_genai: bool = False):
        """
        Build ability archetypes from faceted skill registry.
        Uses precomputed skill_embeddings instead of re-encoding.
        """
        try:
            from src.archetypes.archetype_builder import build_archetypes_from_registry

            skill_id_to_emb_idx = {
                row["skill_id"]: i for i, (_, row) in enumerate(df_unique.iterrows())
            }

            archetypes_data, arch_stats = build_archetypes_from_registry(
                skill_registry=skill_registry,
                df_assertions=df,
                config=self.config,
                embedding_interface=self.embedding_interface,
                genai_interface=self.genai_interface if not skip_genai else None,
                precomputed_embeddings=skill_embeddings,
                skill_id_to_emb_idx=skill_id_to_emb_idx,
            )

            return archetypes_data, arch_stats

        except Exception as e:
            logger.warning(f"Archetype clustering failed: {e}", exc_info=True)
            logger.info("Continuing without archetypes")
            return [], {}

    # ═══════════════════════════════════════════════════════════════
    #  RUN
    # ═══════════════════════════════════════════════════════════════

    def run(
        self,
        input_data: pd.DataFrame,
        output_dir: str = "output",
        skip_genai: bool = False,
        concordance_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run the full pipeline.

        Args:
            input_data: Raw extracted skills DataFrame
            output_dir: Where to write output files
            skip_genai: Skip all LLM steps
            concordance_path: Path to concordance Excel/CSV (optional)

        Returns:
            Results dict with stats and file paths.
        """
        logger.info("=" * 70)
        logger.info("  SKILL ASSERTION PIPELINE")
        logger.info("  Skill → Assertion → Unit → Qualification → Occupation")
        logger.info("  + Ability Archetypes with Progression Ladders")
        logger.info("=" * 70)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        start = datetime.now()

        try:
            # ── 1. PREPROCESS ─────────────────────────────────────
            logger.info("\n[1/7] Preprocessing...")
            df = self.preprocessor.preprocess(input_data)

            # ── 2. LOAD CONCORDANCE (early — needed for LVL) ─────
            concordance = None
            if concordance_path:
                logger.info(f"\n[2/7] Loading concordance from: {concordance_path}")
                concordance = load_concordance(concordance_path)
            else:
                logger.info("\n[2/7] No concordance file — LVL assignment will use skill names only")

            # ── 3. REASSIGN PROFICIENCY LEVELS (LVL facet) ────────
            logger.info("\n[3/7] Reassigning proficiency levels (LVL facet-based)...")
            df = self._reassign_levels(df, concordance, skip_genai=skip_genai)

            # ── 4. DEDUPLICATE SKILL LABELS ───────────────────────
            logger.info("\n[4/7] Deduplicating skill labels...")
            deduplicator = SkillDeduplicator(
                self.config,
                embedding_interface=self.embedding_interface,
                genai_interface=self.genai_interface if not skip_genai else None,
            )
            df, skill_registry = deduplicator.deduplicate(df)

            # ── 5. ASSIGN REMAINING FACETS TO SKILLS ──────────────
            logger.info("\n[5/7] Assigning facets to deduplicated skills...")
            remaining_facets = self._get_remaining_facets()
            logger.info(f"  Remaining facets (LVL already done): {remaining_facets}")

            unique_rows = []
            for sid, info in skill_registry.items():
                unit_titles_text = ""
                if concordance:
                    titles = []
                    for uc in info.get("unit_codes", []):
                        t = concordance.unit_titles.get(uc, "")
                        if t:
                            titles.append(t)
                    if titles:
                        unit_titles_text = " Units: " + "; ".join(titles[:5])

                unique_rows.append({
                    "skill_id": sid,
                    "name": info["preferred_label"],
                    "description": info["definition"],
                    "category": info["category"],
                    "level": 3,
                    "context": "HYBRID",
                    "embedding_text": f"{info['preferred_label']}",
                    "embedding_text_asced": f"{info['preferred_label']}. {unit_titles_text}",
                    "confidence": 1.0,
                })
            df_unique = pd.DataFrame(unique_rows)

            # Generate embeddings ONCE for all downstream uses
            logger.info("Generating skill embeddings (single pass for facets + archetypes)...")
            skill_embeddings, asced_embeddings = self._generate_skill_embeddings(
                df_unique, concordance
            )

            # Assign remaining facets (NAT, TRF, COG, ASCED) using precomputed embeddings
            skill_registry = self._assign_facets_to_skills(
                skill_registry, df_unique,
                skill_embeddings=skill_embeddings,
                asced_embeddings=asced_embeddings,
                concordance=concordance,
            )

            # Assign LVL facet to skill registry from reassigned assertion levels
            self._assign_lvl_facet_to_registry(skill_registry, df)

            # ── 6. BUILD ABILITY ARCHETYPES ───────────────────────
            logger.info("\n[6/7] Building ability archetypes with progression ladders...")
            archetypes_data, arch_stats = self._build_archetypes(
                skill_registry, df,
                skill_embeddings=skill_embeddings,
                df_unique=df_unique,
                skip_genai=skip_genai,
            )

            # Save archetypes JSON
            if archetypes_data:
                with open(output_path / "archetypes.json", "w") as f:
                    json.dump({
                        "metadata": {
                            "generated_at": datetime.now().isoformat(),
                            "statistics": arch_stats,
                        },
                        "archetypes": archetypes_data,
                    }, f, indent=2, default=str)
                logger.info(f"Saved {len(archetypes_data)} archetypes to archetypes.json")

            # ── 7. BUILD SCHEMA & EXPORT ──────────────────────────
            logger.info("\n[7/7] Building schema and exporting...")
            builder = AssertionBuilder()
            skills, assertions, units, qualifications, occupations = builder.build(
                df, skill_registry, concordance
            )

            # === Export ===
            export_data = self._build_export(
                skills, assertions, units, qualifications, occupations,
                concordance, archetypes_data, arch_stats
            )

            # JSON
            json_path = output_path / "skill_assertion_data.json"
            with open(json_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            logger.info(f"Exported JSON: {json_path}")

            # HTML search engine
            html_path = output_path / "skill_search.html"
            data_js_path = output_path / "skill_search_data.js"
            self._export_search_engine(export_data, html_path, data_js_path)
            logger.info(f"Exported HTML: {html_path}")

            # Summary Excel
            self._export_excel(skills, assertions, units, qualifications, occupations, output_path, archetypes_data)

            # ── DONE ──────────────────────────────────────────────
            duration = (datetime.now() - start).total_seconds()
            results = {
                "status": "success",
                "total_rows": len(df),
                "skills": len(skills),
                "assertions": len(assertions),
                "units": len(units),
                "qualifications": len(qualifications),
                "occupations": len(occupations),
                "archetypes": len(archetypes_data),
                "sub_clusters": arch_stats.get("total_sub_clusters", 0),
                "facets_assigned": self.config["facet_assignment"]["facets_to_assign"],
                "duration_seconds": duration,
                "output_dir": str(output_path),
            }

            logger.info("\n" + "=" * 70)
            logger.info("  PIPELINE COMPLETE")
            logger.info(f"  Skills:          {results['skills']}")
            logger.info(f"  Assertions:      {results['assertions']}")
            logger.info(f"  Units:           {results['units']}")
            logger.info(f"  Qualifications:  {results['qualifications']}")
            logger.info(f"  Occupations:     {results['occupations']}")
            logger.info(f"  Archetypes:      {results['archetypes']}")
            logger.info(f"  Sub-clusters:    {results['sub_clusters']}")
            logger.info(f"  Time:            {duration:.1f}s")
            logger.info("=" * 70)
            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    #  EXPORT HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _build_export(self, skills, assertions, units, qualifications, occupations,
                      concordance, archetypes_data=None, arch_stats=None):
        """Build the JSON export structure with all 5 object types + archetypes."""
        assertions_by_skill = {}
        for a in assertions:
            assertions_by_skill.setdefault(a.skill_id, []).append(a)

        skill_to_archetype = {}
        if archetypes_data:
            for arch in archetypes_data:
                arch_id = arch.get("archetype_id", "")
                arch_label = arch.get("label", "")
                for sc in arch.get("sub_clusters", []):
                    sc_id = sc.get("cluster_id", "")
                    sc_label = sc.get("label", "")
                    sc_prog_type = sc.get("progression_type", "")
                    for sid in sc.get("skill_ids", []):
                        skill_to_archetype[sid] = {
                            "archetype_id": arch_id,
                            "archetype_label": arch_label,
                            "sub_cluster_id": sc_id,
                            "sub_cluster_label": sc_label,
                            "progression_type": sc_prog_type,
                        }
                for us in arch.get("unclassified_skills", []):
                    sid = us.get("skill_id", "")
                    if sid and sid not in skill_to_archetype:
                        skill_to_archetype[sid] = {
                            "archetype_id": arch_id,
                            "archetype_label": arch_label,
                            "sub_cluster_id": "",
                            "sub_cluster_label": "(unclassified)",
                            "progression_type": "",
                        }

        skills_export = []
        for s in skills:
            sa = assertions_by_skill.get(s.skill_id, [])
            ctx_dist = {}
            for a in sa:
                ctx_dist[a.teaching_context] = ctx_dist.get(a.teaching_context, 0) + 1
            lvl_dist = {}
            for a in sa:
                lvl_dist[a.level_of_engagement] = lvl_dist.get(a.level_of_engagement, 0) + 1

            qual_list = []
            if concordance:
                for qc in s.qualification_codes:
                    qual_list.append({"code": qc, "title": concordance.qual_titles.get(qc, "")})
            occ_list = []
            if concordance:
                for ac in s.occupation_codes:
                    occ_list.append({"code": ac, "title": concordance.occupation_titles.get(ac, "")})

            arch_info = skill_to_archetype.get(s.skill_id, {})

            skills_export.append({
                "skill_id": s.skill_id,
                "preferred_label": s.preferred_label,
                "alternative_labels": s.alternative_labels,
                "definition": s.definition,
                "category": s.category,
                "facets": s.facets,
                "archetype_id": arch_info.get("archetype_id", ""),
                "archetype_label": arch_info.get("archetype_label", ""),
                "sub_cluster_id": arch_info.get("sub_cluster_id", ""),
                "sub_cluster_label": arch_info.get("sub_cluster_label", ""),
                "progression_type": arch_info.get("progression_type", ""),
                "assertion_count": len(sa),
                "unit_codes": s.unit_codes,
                "qualifications": qual_list,
                "occupations": occ_list,
                "context_distribution": ctx_dist,
                "level_distribution": lvl_dist,
                "assertions": [
                    {
                        "assertion_id": a.assertion_id,
                        "unit_code": a.unit_code,
                        "teaching_context": a.teaching_context,
                        "level_of_engagement": a.level_of_engagement,
                        "evidence": a.evidence,
                        "keywords": a.keywords,
                        "confidence": a.confidence,
                        "qualification_codes": a.qualification_codes,
                        "occupation_codes": a.occupation_codes,
                    }
                    for a in sa
                ],
            })

        units_export = []
        for u in units:
            qual_list = []
            if concordance:
                for qc in u.qualification_codes:
                    qual_list.append({"code": qc, "title": concordance.qual_titles.get(qc, "")})
            units_export.append({
                "unit_code": u.unit_code,
                "unit_title": u.unit_title,
                "qualification_codes": u.qualification_codes,
                "qualifications": qual_list,
                "skill_count": u.skill_count,
                "skill_ids": u.skill_ids,
            })

        quals_export = [
            {
                "qualification_code": q.qualification_code,
                "qualification_title": q.qualification_title,
                "unit_codes": q.unit_codes,
                "occupation_codes": q.occupation_codes,
                "skill_ids": q.skill_ids,
                "skill_count": q.skill_count,
            }
            for q in qualifications
        ]

        occs_export = [
            {
                "anzsco_code": o.anzsco_code,
                "anzsco_title": o.anzsco_title,
                "qualification_codes": o.qualification_codes,
                "skill_ids": o.skill_ids,
                "skill_count": o.skill_count,
            }
            for o in occupations
        ]

        facets_meta = {}
        for fid in self.config["facet_assignment"]["facets_to_assign"]:
            fi = ALL_FACETS.get(fid, {})
            facets_meta[fid] = {
                "name": fi.get("facet_name", fid),
                "description": fi.get("description", ""),
                "values": {
                    code: {"name": v.get("name", code), "description": v.get("description", "")}
                    for code, v in fi.get("values", {}).items()
                },
            }

        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "pipeline": "skill-assertion-pipeline",
                "total_skills": len(skills),
                "total_assertions": len(assertions),
                "total_units": len(units),
                "total_qualifications": len(qualifications),
                "total_occupations": len(occupations),
                "total_archetypes": len(archetypes_data) if archetypes_data else 0,
                "facets": list(facets_meta.keys()),
                "archetype_statistics": arch_stats or {},
            },
            "facets": facets_meta,
            "skills": skills_export,
            "units": units_export,
            "qualifications": quals_export,
            "occupations": occs_export,
            "archetypes": archetypes_data or [],
        }

    def _export_excel(self, skills, assertions, units, qualifications, occupations, output_path, archetypes_data=None):
        """Export summary Excel with 7 sheets."""
        try:
            skill_to_arch = {}
            if archetypes_data:
                for arch in archetypes_data:
                    arch_id = arch.get("archetype_id", "")
                    arch_label = arch.get("label", "")
                    for sc in arch.get("sub_clusters", []):
                        sc_id = sc.get("cluster_id", "")
                        sc_label = sc.get("label", "")
                        sc_prog = sc.get("progression_type", "")
                        for sid in sc.get("skill_ids", []):
                            skill_to_arch[sid] = {
                                "archetype_id": arch_id,
                                "archetype_label": arch_label,
                                "sub_cluster_id": sc_id,
                                "sub_cluster_label": sc_label,
                                "progression_type": sc_prog,
                            }

            skills_rows = []
            for s in skills:
                arch_info = skill_to_arch.get(s.skill_id, {})
                row = {
                    "skill_id": s.skill_id,
                    "preferred_label": s.preferred_label,
                    "alternative_labels": "; ".join(s.alternative_labels),
                    "definition": s.definition,
                    "category": s.category,
                    "assertion_count": s.assertion_count,
                    "archetype_id": arch_info.get("archetype_id", ""),
                    "archetype_label": arch_info.get("archetype_label", ""),
                    "sub_cluster_id": arch_info.get("sub_cluster_id", ""),
                    "sub_cluster_label": arch_info.get("sub_cluster_label", ""),
                    "progression_type": arch_info.get("progression_type", ""),
                    "unit_codes": "; ".join(s.unit_codes[:20]),
                    "qualification_codes": "; ".join(s.qualification_codes[:10]),
                    "occupation_codes": "; ".join(s.occupation_codes[:10]),
                }
                for fid, fdata in s.facets.items():
                    row[f"facet_{fid}"] = fdata.get("name", "")
                skills_rows.append(row)

            assertion_rows = [
                {
                    "assertion_id": a.assertion_id, "skill_id": a.skill_id,
                    "unit_code": a.unit_code, "teaching_context": a.teaching_context,
                    "level_of_engagement": a.level_of_engagement,
                    "evidence": a.evidence[:200],
                    "keywords": "; ".join(a.keywords[:10]),
                    "confidence": a.confidence,
                    "qualification_codes": "; ".join(a.qualification_codes[:10]),
                    "occupation_codes": "; ".join(a.occupation_codes[:10]),
                }
                for a in assertions
            ]

            unit_rows = [{"unit_code": u.unit_code, "unit_title": u.unit_title, "skill_count": u.skill_count, "qualification_codes": "; ".join(u.qualification_codes[:10])} for u in units]
            qual_rows = [{"qualification_code": q.qualification_code, "qualification_title": q.qualification_title, "unit_count": len(q.unit_codes), "skill_count": q.skill_count, "occupation_codes": "; ".join(q.occupation_codes[:10])} for q in qualifications]
            occ_rows = [{"anzsco_code": o.anzsco_code, "anzsco_title": o.anzsco_title, "qualification_count": len(o.qualification_codes), "skill_count": o.skill_count} for o in occupations]

            archetype_rows = []
            subcluster_rows = []
            if archetypes_data:
                for arch in archetypes_data:
                    levels = arch.get("level_distribution", {})
                    level_keys = sorted(levels.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)
                    level_range = f"{level_keys[0]}-{level_keys[-1]}" if level_keys else "-"
                    archetype_rows.append({
                        "archetype_id": arch.get("archetype_id", ""), "label": arch.get("label", ""),
                        "skill_nature": arch.get("nat", {}).get("name", ""),
                        "transferability": arch.get("trf", {}).get("name", ""),
                        "total_skills": arch.get("total_skills", 0),
                        "sub_cluster_count": len(arch.get("sub_clusters", [])),
                        "asced_field_count": len(arch.get("asced_coverage", {})),
                        "level_range": level_range,
                        "qualification_count": arch.get("qualification_count", 0),
                        "occupation_count": arch.get("occupation_count", 0),
                        "progression_summary": "; ".join(f"{k}: {v}" for k, v in arch.get("progression_summary", {}).items()),
                    })
                    for sc in arch.get("sub_clusters", []):
                        progression = sc.get("progression", [])
                        level_skills = [f"L{r['level']}({r.get('skill_count',0)}): {'; '.join(r.get('skill_names',[])[:5])}" for r in progression]
                        subcluster_rows.append({
                            "cluster_id": sc.get("cluster_id", ""), "archetype_id": arch.get("archetype_id", ""),
                            "archetype_label": arch.get("label", ""), "label": sc.get("label", ""),
                            "total_skills": sc.get("total_skills", 0), "progression_type": sc.get("progression_type", ""),
                            "level_span": f"{sc.get('level_span',[0,0])[0]}-{sc.get('level_span',[0,0])[1]}",
                            "level_gaps": "; ".join(str(g) for g in sc.get("level_gaps", [])),
                            "asced_field_count": len(sc.get("asced_spread", {})),
                            "asced_fields": "; ".join(f"{c} ({sc.get('asced_names',{}).get(c,c)})" for c in sorted(sc.get("asced_spread",{}).keys())[:10]),
                            "avg_intra_similarity": round(sc.get("avg_intra_similarity", 0), 4),
                            "representative_skills": "; ".join(rs.get("name","") for rs in sc.get("representative_skills",[])[:5]),
                            "progression_detail": " | ".join(level_skills[:7]),
                        })

            with pd.ExcelWriter(output_path / "skill_assertion_export.xlsx", engine="openpyxl") as writer:
                pd.DataFrame(skills_rows).to_excel(writer, sheet_name="Skills", index=False)
                pd.DataFrame(assertion_rows).to_excel(writer, sheet_name="Assertions", index=False)
                pd.DataFrame(unit_rows).to_excel(writer, sheet_name="Units", index=False)
                pd.DataFrame(qual_rows).to_excel(writer, sheet_name="Qualifications", index=False)
                pd.DataFrame(occ_rows).to_excel(writer, sheet_name="Occupations", index=False)
                if archetype_rows:
                    pd.DataFrame(archetype_rows).to_excel(writer, sheet_name="Archetypes", index=False)
                if subcluster_rows:
                    pd.DataFrame(subcluster_rows).to_excel(writer, sheet_name="Sub-Clusters", index=False)

            n_sheets = 5 + (1 if archetype_rows else 0) + (1 if subcluster_rows else 0)
            logger.info(f"Exported Excel ({n_sheets} sheets): {output_path / 'skill_assertion_export.xlsx'}")
        except Exception as e:
            logger.warning(f"Excel export failed: {e}")

    def _export_search_engine(self, export_data, html_path, data_js_path):
        """Generate the HTML search engine + data JS file."""
        from src.export.search_engine import generate_search_html
        generate_search_html(export_data, str(html_path), str(data_js_path))


def _level_name(level_int: int) -> str:
    """Map integer level to name."""
    names = {
        1: "Follow", 2: "Assist", 3: "Apply", 4: "Enable",
        5: "Ensure & Advise", 6: "Initiate & Influence", 7: "Set Strategy",
    }
    return names.get(level_int, f"Level {level_int}")