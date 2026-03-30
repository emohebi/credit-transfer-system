"""
Skill Assertion Pipeline — Main Orchestrator

Five-object model + Ability Groups:
  Skill → SkillAssertion → Unit → Qualification → Occupation (ANZSCO)
  Skill → TRF group → THA ability group → LVL progression ladder

Pipeline steps:
  1. Preprocess data (clean, normalize — keep all rows)
  2. Load concordance (needed early for LVL assignment)
  3. Reassign proficiency levels (LVL facet-based, per assertion row)
  4. Deduplicate skill LABELS (embed unique names, cluster, validate)
  5. Assign facets (NAT, TRF, COG, ASCED, THA) to deduplicated Skills
  6. Build ability groups (TRF → THA → LVL progression ladders)
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
      → assign facets (incl. THA) → build ability groups → build schema → export.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or CONFIG
        self.preprocessor = AssertionDataPreprocessor(self.config)
        self.embedding_interface = None
        self.genai_interface = None
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
    #  LEVEL REASSIGNMENT
    # ═══════════════════════════════════════════════════════════════

    def _reassign_levels(self, df: pd.DataFrame, concordance, skip_genai: bool = False):
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
        batch_size = self.config["embedding"]["batch_size"]
        normalize = self.config["embedding"]["normalize_embeddings"]

        texts = df_unique["embedding_text"].tolist()
        logger.info(f"Generating primary skill embeddings for {len(texts)} unique skills...")
        skill_embeddings = self.embedding_interface.encode(
            texts, batch_size=batch_size, normalize_embeddings=normalize,
        )
        logger.info(f"Primary embeddings shape: {skill_embeddings.shape}")

        asced_embeddings = None
        remaining_facets = self._get_remaining_facets()
        has_asced = "ASCED" in remaining_facets
        has_asced_col = "embedding_text_asced" in df_unique.columns

        if has_asced and has_asced_col and concordance:
            texts_asced = df_unique["embedding_text_asced"].tolist()
            logger.info(f"Generating ASCED-enriched embeddings for {len(texts_asced)} unique skills...")
            asced_embeddings = self.embedding_interface.encode(
                texts_asced, batch_size=batch_size, normalize_embeddings=normalize,
            )
            logger.info(f"ASCED embeddings shape: {asced_embeddings.shape}")

        return skill_embeddings, asced_embeddings

    # ═══════════════════════════════════════════════════════════════
    #  FACET ASSIGNMENT (excludes LVL, includes THA)
    # ═══════════════════════════════════════════════════════════════

    def _get_remaining_facets(self) -> List[str]:
        """Get facets to assign at the skill level (excludes LVL, handled earlier)."""
        all_facets = self.config["facet_assignment"]["facets_to_assign"]
        return [f for f in all_facets if f != "LVL"]

    def _assign_facets_to_skills(self, skill_registry: Dict, df_unique_skills: pd.DataFrame,
                                  skill_embeddings: np.ndarray, asced_embeddings: np.ndarray = None,
                                  concordance=None):
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

        # Separate ASCED (uses enriched embeddings) from others
        if has_asced and asced_embeddings is not None:
            non_asced = [f for f in remaining_facets if f != "ASCED"]
            asced_only = ["ASCED"]

            if non_asced:
                logger.info(f"  Assigning facets {non_asced} with skill text embeddings...")
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
    #  ABILITY GROUPING (THA-based, replaces clustering)
    # ═══════════════════════════════════════════════════════════════

    def _build_ability_groups(self, skill_registry: Dict, df: pd.DataFrame):
        """
        Build ability groups from THA facet assignments.
        Replaces archetype clustering — no algorithm, just facet grouping.
        """
        try:
            from src.grouping.ability_grouper import build_ability_groups
            return build_ability_groups(
                skill_registry=skill_registry,
                df_assertions=df,
            )
        except Exception as e:
            logger.warning(f"Ability grouping failed: {e}", exc_info=True)
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
        logger.info("=" * 70)
        logger.info("  SKILL ASSERTION PIPELINE")
        logger.info("  Skill → Assertion → Unit → Qualification → Occupation")
        logger.info("  + TRF → THA Ability Groups with Progression Ladders")
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

            # ── 5. ASSIGN FACETS (NAT, TRF, COG, ASCED, THA) ─────
            logger.info("\n[5/7] Assigning facets to deduplicated skills...")
            remaining_facets = self._get_remaining_facets()
            logger.info(f"  Facets to assign (LVL already done): {remaining_facets}")

            unique_rows = []
            for sid, info in skill_registry.items():
                unit_titles_text = ""
                if concordance:
                    titles = [concordance.unit_titles.get(uc, "") for uc in info.get("unit_codes", [])]
                    titles = [t for t in titles if t]
                    if titles:
                        unit_titles_text = " Units: " + "; ".join(titles[:5])
                unique_rows.append({
                    "skill_id": sid,
                    "name": info["preferred_label"],
                    "description": info["definition"],
                    "category": info["category"],
                    "level": 3, "context": "HYBRID",
                    "embedding_text": f"{info['preferred_label']}",
                    "embedding_text_asced": f"{info['preferred_label']}. {unit_titles_text}",
                    "confidence": 1.0,
                })
            df_unique = pd.DataFrame(unique_rows)

            logger.info("Generating skill embeddings (single pass for facets)...")
            skill_embeddings, asced_embeddings = self._generate_skill_embeddings(df_unique, concordance)

            skill_registry = self._assign_facets_to_skills(
                skill_registry, df_unique,
                skill_embeddings=skill_embeddings,
                asced_embeddings=asced_embeddings,
                concordance=concordance,
            )
            self._assign_lvl_facet_to_registry(skill_registry, df)

            # ── 6. BUILD ABILITY GROUPS (TRF → THA → LVL) ────────
            logger.info("\n[6/7] Building ability groups (TRF → THA → LVL)...")
            groups_data, group_stats = self._build_ability_groups(skill_registry, df)

            if groups_data:
                with open(output_path / "ability_groups.json", "w") as f:
                    json.dump({
                        "metadata": {"generated_at": datetime.now().isoformat(), "statistics": group_stats},
                        "groups": groups_data,
                    }, f, indent=2, default=str)
                logger.info(f"Saved {len(groups_data)} TRF groups to ability_groups.json")

            # ── 7. BUILD SCHEMA & EXPORT ──────────────────────────
            logger.info("\n[7/7] Building schema and exporting...")
            builder = AssertionBuilder()
            skills, assertions, units, qualifications, occupations = builder.build(
                df, skill_registry, concordance
            )

            export_data = self._build_export(
                skills, assertions, units, qualifications, occupations,
                concordance, groups_data, group_stats
            )

            json_path = output_path / "skill_assertion_data.json"
            with open(json_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)
            logger.info(f"Exported JSON: {json_path}")

            html_path = output_path / "skill_search.html"
            data_js_path = output_path / "skill_search_data.js"
            self._export_search_engine(export_data, html_path, data_js_path)
            logger.info(f"Exported HTML: {html_path}")

            self._export_excel(skills, assertions, units, qualifications, occupations, output_path, groups_data)

            duration = (datetime.now() - start).total_seconds()
            results = {
                "status": "success",
                "total_rows": len(df),
                "skills": len(skills),
                "assertions": len(assertions),
                "units": len(units),
                "qualifications": len(qualifications),
                "occupations": len(occupations),
                "ability_groups": sum(len(g.get("sub_clusters", [])) for g in groups_data),
                "facets_assigned": self.config["facet_assignment"]["facets_to_assign"],
                "duration_seconds": duration,
                "output_dir": str(output_path),
            }

            logger.info("\n" + "=" * 70)
            logger.info("  PIPELINE COMPLETE")
            for k, v in results.items():
                if k not in ("status", "output_dir"):
                    logger.info(f"  {k}: {v}")
            logger.info("=" * 70)
            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    #  EXPORT HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _build_export(self, skills, assertions, units, qualifications, occupations,
                      concordance, groups_data=None, group_stats=None):
        assertions_by_skill = {}
        for a in assertions:
            assertions_by_skill.setdefault(a.skill_id, []).append(a)

        # Build skill → THA group reverse mapping
        skill_to_group = {}
        if groups_data:
            for grp in groups_data:
                grp_id = grp.get("archetype_id", "")
                grp_label = grp.get("label", "")
                for sc in grp.get("sub_clusters", []):
                    sc_id = sc.get("cluster_id", "")
                    sc_label = sc.get("label", "")
                    sc_prog = sc.get("progression_type", "")
                    for sid in sc.get("skill_ids", []):
                        skill_to_group[sid] = {
                            "archetype_id": grp_id,
                            "archetype_label": grp_label,
                            "sub_cluster_id": sc_id,
                            "sub_cluster_label": sc_label,
                            "progression_type": sc_prog,
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

            gi = skill_to_group.get(s.skill_id, {})
            skills_export.append({
                "skill_id": s.skill_id,
                "preferred_label": s.preferred_label,
                "alternative_labels": s.alternative_labels,
                "definition": s.definition,
                "category": s.category,
                "facets": s.facets,
                "archetype_id": gi.get("archetype_id", ""),
                "archetype_label": gi.get("archetype_label", ""),
                "sub_cluster_id": gi.get("sub_cluster_id", ""),
                "sub_cluster_label": gi.get("sub_cluster_label", ""),
                "progression_type": gi.get("progression_type", ""),
                "assertion_count": len(sa),
                "unit_codes": s.unit_codes,
                "qualifications": qual_list,
                "occupations": occ_list,
                "context_distribution": ctx_dist,
                "level_distribution": lvl_dist,
                "assertions": [
                    {
                        "assertion_id": a.assertion_id, "unit_code": a.unit_code,
                        "teaching_context": a.teaching_context,
                        "level_of_engagement": a.level_of_engagement,
                        "evidence": a.evidence, "keywords": a.keywords,
                        "confidence": a.confidence,
                        "qualification_codes": a.qualification_codes,
                        "occupation_codes": a.occupation_codes,
                    }
                    for a in sa
                ],
            })

        units_export = [{
            "unit_code": u.unit_code, "unit_title": u.unit_title,
            "qualification_codes": u.qualification_codes,
            "qualifications": [{"code": qc, "title": concordance.qual_titles.get(qc, "")} for qc in u.qualification_codes] if concordance else [],
            "skill_count": u.skill_count, "skill_ids": u.skill_ids,
        } for u in units]

        quals_export = [{"qualification_code": q.qualification_code, "qualification_title": q.qualification_title, "unit_codes": q.unit_codes, "occupation_codes": q.occupation_codes, "skill_ids": q.skill_ids, "skill_count": q.skill_count} for q in qualifications]
        occs_export = [{"anzsco_code": o.anzsco_code, "anzsco_title": o.anzsco_title, "qualification_codes": o.qualification_codes, "skill_ids": o.skill_ids, "skill_count": o.skill_count} for o in occupations]

        facets_meta = {}
        for fid in self.config["facet_assignment"]["facets_to_assign"]:
            fi = ALL_FACETS.get(fid, {})
            facets_meta[fid] = {
                "name": fi.get("facet_name", fid),
                "description": fi.get("description", ""),
                "values": {code: {"name": v.get("name", code), "description": v.get("description", "")} for code, v in fi.get("values", {}).items()},
            }

        return {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "pipeline": "skill-assertion-pipeline",
                "total_skills": len(skills), "total_assertions": len(assertions),
                "total_units": len(units), "total_qualifications": len(qualifications),
                "total_occupations": len(occupations),
                "total_ability_groups": sum(len(g.get("sub_clusters", [])) for g in groups_data) if groups_data else 0,
                "facets": list(facets_meta.keys()),
                "group_statistics": group_stats or {},
            },
            "facets": facets_meta,
            "skills": skills_export,
            "units": units_export,
            "qualifications": quals_export,
            "occupations": occs_export,
            "archetypes": groups_data or [],  # Keep key name "archetypes" for search engine compat
        }

    def _export_excel(self, skills, assertions, units, qualifications, occupations, output_path, groups_data=None):
        try:
            skill_to_grp = {}
            if groups_data:
                for grp in groups_data:
                    for sc in grp.get("sub_clusters", []):
                        for sid in sc.get("skill_ids", []):
                            skill_to_grp[sid] = {
                                "trf_group": grp.get("label", ""),
                                "ability_group": sc.get("label", ""),
                                "progression_type": sc.get("progression_type", ""),
                            }

            skills_rows = []
            for s in skills:
                gi = skill_to_grp.get(s.skill_id, {})
                row = {
                    "skill_id": s.skill_id,
                    "preferred_label": s.preferred_label,
                    "alternative_labels": "; ".join(s.alternative_labels),
                    "definition": s.definition,
                    "category": s.category,
                    "assertion_count": s.assertion_count,
                    "trf_group": gi.get("trf_group", ""),
                    "ability_group": gi.get("ability_group", ""),
                    "progression_type": gi.get("progression_type", ""),
                    "unit_codes": "; ".join(s.unit_codes[:20]),
                    "qualification_codes": "; ".join(s.qualification_codes[:10]),
                    "occupation_codes": "; ".join(s.occupation_codes[:10]),
                }
                for fid, fdata in s.facets.items():
                    row[f"facet_{fid}"] = fdata.get("name", "")
                skills_rows.append(row)

            assertion_rows = [{"assertion_id": a.assertion_id, "skill_id": a.skill_id, "unit_code": a.unit_code, "teaching_context": a.teaching_context, "level_of_engagement": a.level_of_engagement, "evidence": a.evidence[:200], "keywords": "; ".join(a.keywords[:10]), "confidence": a.confidence, "qualification_codes": "; ".join(a.qualification_codes[:10]), "occupation_codes": "; ".join(a.occupation_codes[:10])} for a in assertions]
            unit_rows = [{"unit_code": u.unit_code, "unit_title": u.unit_title, "skill_count": u.skill_count, "qualification_codes": "; ".join(u.qualification_codes[:10])} for u in units]
            qual_rows = [{"qualification_code": q.qualification_code, "qualification_title": q.qualification_title, "unit_count": len(q.unit_codes), "skill_count": q.skill_count, "occupation_codes": "; ".join(q.occupation_codes[:10])} for q in qualifications]
            occ_rows = [{"anzsco_code": o.anzsco_code, "anzsco_title": o.anzsco_title, "qualification_count": len(o.qualification_codes), "skill_count": o.skill_count} for o in occupations]

            # Ability groups sheet
            group_rows = []
            if groups_data:
                for grp in groups_data:
                    for sc in grp.get("sub_clusters", []):
                        prog = sc.get("progression", [])
                        level_detail = " | ".join(f"L{r['level']}({r.get('skill_count',0)}): {'; '.join(r.get('skill_names',[])[:5])}" for r in prog[:7])
                        group_rows.append({
                            "tha_code": sc.get("cluster_id", ""),
                            "ability_name": sc.get("label", ""),
                            "trf_group": grp.get("label", ""),
                            "total_skills": sc.get("total_skills", 0),
                            "progression_type": sc.get("progression_type", ""),
                            "level_span": f"{sc.get('level_span',[0,0])[0]}-{sc.get('level_span',[0,0])[1]}",
                            "level_gaps": "; ".join(str(g) for g in sc.get("level_gaps", [])),
                            "progression_detail": level_detail,
                        })

            with pd.ExcelWriter(output_path / "skill_assertion_export.xlsx", engine="openpyxl") as writer:
                pd.DataFrame(skills_rows).to_excel(writer, sheet_name="Skills", index=False)
                pd.DataFrame(assertion_rows).to_excel(writer, sheet_name="Assertions", index=False)
                pd.DataFrame(unit_rows).to_excel(writer, sheet_name="Units", index=False)
                pd.DataFrame(qual_rows).to_excel(writer, sheet_name="Qualifications", index=False)
                pd.DataFrame(occ_rows).to_excel(writer, sheet_name="Occupations", index=False)
                if group_rows:
                    pd.DataFrame(group_rows).to_excel(writer, sheet_name="Ability Groups", index=False)

            n_sheets = 5 + (1 if group_rows else 0)
            logger.info(f"Exported Excel ({n_sheets} sheets): {output_path / 'skill_assertion_export.xlsx'}")
        except Exception as e:
            logger.warning(f"Excel export failed: {e}")

    def _export_search_engine(self, export_data, html_path, data_js_path):
        from src.export.search_engine import generate_search_html
        generate_search_html(export_data, str(html_path), str(data_js_path))


def _level_name(level_int: int) -> str:
    names = {1: "Follow", 2: "Assist", 3: "Apply", 4: "Enable", 5: "Ensure & Advise", 6: "Initiate & Influence", 7: "Set Strategy"}
    return names.get(level_int, f"Level {level_int}")
