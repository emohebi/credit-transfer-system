"""
Skill Assertion Pipeline — Main Orchestrator

Five-object model:
  Skill → SkillAssertion → Unit → Qualification → Occupation (ANZSCO)

Pipeline steps:
  1. Preprocess data (clean, normalize — keep all rows)
  2. Deduplicate skill LABELS (embed unique names, cluster, validate)
  3. Init embedding + GenAI interfaces
  4. Load concordance (unit → qualification → occupation)
  5. Assign facets to deduplicated Skills (ASCED uses unit titles for context)
  6. Build five-object schema with precomputed traversals + export
"""
import logging
import json
import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
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
    Orchestrates: preprocess → dedup labels → assign facets → build schema → export.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or CONFIG
        self.preprocessor = AssertionDataPreprocessor(self.config)

        # Lazy-init interfaces
        self.embedding_interface = None
        self.genai_interface = None
        
        # ── 2. INIT INTERFACES ────────────────────────────────
        logger.info("\nInitialising model interfaces...")
        self._init_embedding()
        self._init_genai()

    # ═══════════════════════════════════════════════════════════════
    #  INTERFACE INITIALISATION (reuses original project's code)
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
    #  FACET ASSIGNMENT (reuse FacetAssigner from original project)
    # ═══════════════════════════════════════════════════════════════

    def _assign_facets_to_skills(self, skill_registry: Dict, df_unique_skills: pd.DataFrame, concordance=None):
        """
        Assign facets to the deduplicated Skill objects.
        Uses embedding similarity + optional LLM re-ranking.

        For ASCED, uses unit-title-enriched embedding text so the assigner
        has field-of-education context from the concordance.
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

        facets_to_assign = self.config["facet_assignment"]["facets_to_assign"]

        # Determine which embedding text to use:
        # - For ASCED: use embedding_text_asced (includes unit titles)
        # - For all others: use embedding_text (skill name + definition only)
        has_asced = "ASCED" in facets_to_assign
        has_asced_col = "embedding_text_asced" in df_unique_skills.columns

        if has_asced and has_asced_col and concordance:
            # Run non-ASCED facets with standard embedding text
            non_asced = [f for f in facets_to_assign if f != "ASCED"]
            asced_only = ["ASCED"]

            if non_asced:
                logger.info(f"  Assigning non-ASCED facets {non_asced} with skill text...")
                texts = df_unique_skills["embedding_text"].tolist()
                embeddings = self.embedding_interface.encode(
                    texts,
                    batch_size=self.config["embedding"]["batch_size"],
                    normalize_embeddings=self.config["embedding"]["normalize_embeddings"],
                )
                df_faceted = assigner.assign_facets(df_unique_skills, embeddings, facets_override=non_asced)
            else:
                df_faceted = df_unique_skills.copy()

            # Run ASCED with unit-title-enriched embedding text
            logger.info("  Assigning ASCED facet with unit-title-enriched text...")
            texts_asced = df_unique_skills["embedding_text_asced"].tolist()
            embeddings_asced = self.embedding_interface.encode(
                texts_asced,
                batch_size=self.config["embedding"]["batch_size"],
                normalize_embeddings=self.config["embedding"]["normalize_embeddings"],
            )
            df_asced = assigner.assign_facets(df_unique_skills, embeddings_asced, facets_override=asced_only)

            # Merge ASCED columns into df_faceted
            asced_cols = [c for c in df_asced.columns if c.startswith("facet_ASCED")]
            for col in asced_cols:
                df_faceted[col] = df_asced[col]
        else:
            # No concordance or no ASCED — run all facets with standard text
            texts = df_unique_skills["embedding_text"].tolist()
            embeddings = self.embedding_interface.encode(
                texts,
                batch_size=self.config["embedding"]["batch_size"],
                normalize_embeddings=self.config["embedding"]["normalize_embeddings"],
            )
            df_faceted = assigner.assign_facets(df_unique_skills, embeddings)

        # Write facets back into skill_registry
        for _, row in df_faceted.iterrows():
            sid = row["skill_id"]
            if sid not in skill_registry:
                continue
            facets = {}
            for fid in facets_to_assign:
                col = f"facet_{fid}"
                if col in row and pd.notna(row[col]):
                    facets[fid] = {
                        "code": row[col],
                        "name": row.get(f"facet_{fid}_name", row[col]),
                        "confidence": float(row.get(f"facet_{fid}_confidence", 0)),
                    }
            skill_registry[sid]["facets"] = facets

        return skill_registry

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
        logger.info("=" * 70)

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        start = datetime.now()

        try:
            # ── 1. PREPROCESS ─────────────────────────────────────
            logger.info("\n[1/6] Preprocessing...")
            df = self.preprocessor.preprocess(input_data)

            # ── 2. INIT INTERFACES ────────────────────────────────
            logger.info("\n[2/6] Check Interfaces...")
            if self.embedding_interface and self.genai_interface:
                logger.info("\nPass")

            # ── 3. DEDUPLICATE SKILL LABELS ───────────────────────
            logger.info("\n[3/6] Deduplicating skill labels...")
            deduplicator = SkillDeduplicator(
                self.config,
                embedding_interface=self.embedding_interface,
                genai_interface=self.genai_interface if not skip_genai else None,
            )
            df, skill_registry = deduplicator.deduplicate(df)

            # ── 4. LOAD CONCORDANCE ───────────────────────────────
            concordance = None
            if concordance_path:
                logger.info(f"\n[4/6] Loading concordance from: {concordance_path}")
                concordance = load_concordance(concordance_path)
            else:
                logger.info("\n[4/6] No concordance file — skipping qual/occ enrichment")

            # ── 5. ASSIGN FACETS TO SKILLS ────────────────────────
            logger.info("\n[5/6] Assigning facets to deduplicated skills...")

            unique_rows = []
            for sid, info in skill_registry.items():
                # For ASCED, enrich embedding text with unit titles from concordance
                # so the facet assigner has field-of-education context
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
                    "embedding_text": f"{info['preferred_label']}",#. {info['definition']}",
                    "embedding_text_asced": f"{info['preferred_label']}. {unit_titles_text}",#{info['definition']}{unit_titles_text}",
                    "confidence": 1.0,
                })
            df_unique = pd.DataFrame(unique_rows)

            skill_registry = self._assign_facets_to_skills(skill_registry, df_unique, concordance)

            # ── 6. BUILD SCHEMA & EXPORT ──────────────────────────
            logger.info("\n[6/6] Building schema and exporting...")
            builder = AssertionBuilder()
            skills, assertions, units, qualifications, occupations = builder.build(
                df, skill_registry, concordance
            )

            # === Export ===
            export_data = self._build_export(
                skills, assertions, units, qualifications, occupations, concordance
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
            self._export_excel(skills, assertions, units, qualifications, occupations, output_path)

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
            logger.info(f"  Time:            {duration:.1f}s")
            logger.info("=" * 70)
            return results

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    # ═══════════════════════════════════════════════════════════════
    #  EXPORT HELPERS
    # ═══════════════════════════════════════════════════════════════

    def _build_export(self, skills, assertions, units, qualifications, occupations, concordance):
        """Build the JSON export structure with all 5 object types."""
        # Index assertions
        assertions_by_skill = {}
        for a in assertions:
            assertions_by_skill.setdefault(a.skill_id, []).append(a)

        # Skills export
        skills_export = []
        for s in skills:
            sa = assertions_by_skill.get(s.skill_id, [])
            ctx_dist = {}
            for a in sa:
                ctx_dist[a.teaching_context] = ctx_dist.get(a.teaching_context, 0) + 1
            lvl_dist = {}
            for a in sa:
                lvl_dist[a.level_of_engagement] = lvl_dist.get(a.level_of_engagement, 0) + 1

            # Resolve qual/occ titles for display
            qual_list = []
            if concordance:
                for qc in s.qualification_codes:
                    qual_list.append({"code": qc, "title": concordance.qual_titles.get(qc, "")})
            occ_list = []
            if concordance:
                for ac in s.occupation_codes:
                    occ_list.append({"code": ac, "title": concordance.occupation_titles.get(ac, "")})

            skills_export.append({
                "skill_id": s.skill_id,
                "preferred_label": s.preferred_label,
                "alternative_labels": s.alternative_labels,
                "definition": s.definition,
                "category": s.category,
                "facets": s.facets,
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

        # Units export
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

        # Qualifications export
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

        # Occupations export
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

        # Facets meta
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
                "facets": list(facets_meta.keys()),
            },
            "facets": facets_meta,
            "skills": skills_export,
            "units": units_export,
            "qualifications": quals_export,
            "occupations": occs_export,
        }

    def _export_excel(self, skills, assertions, units, qualifications, occupations, output_path):
        """Export summary Excel with 5 sheets."""
        try:
            skills_rows = []
            for s in skills:
                row = {
                    "skill_id": s.skill_id,
                    "preferred_label": s.preferred_label,
                    "alternative_labels": "; ".join(s.alternative_labels),
                    "definition": s.definition,
                    "category": s.category,
                    "assertion_count": s.assertion_count,
                    "unit_codes": "; ".join(s.unit_codes[:20]),
                    "qualification_codes": "; ".join(s.qualification_codes[:10]),
                    "occupation_codes": "; ".join(s.occupation_codes[:10]),
                }
                for fid, fdata in s.facets.items():
                    row[f"facet_{fid}"] = fdata.get("name", "")
                skills_rows.append(row)

            assertion_rows = [
                {
                    "assertion_id": a.assertion_id,
                    "skill_id": a.skill_id,
                    "unit_code": a.unit_code,
                    "teaching_context": a.teaching_context,
                    "level_of_engagement": a.level_of_engagement,
                    "evidence": a.evidence[:200],
                    "keywords": "; ".join(a.keywords[:10]),
                    "confidence": a.confidence,
                    "qualification_codes": "; ".join(a.qualification_codes[:10]),
                    "occupation_codes": "; ".join(a.occupation_codes[:10]),
                }
                for a in assertions
            ]

            unit_rows = [
                {
                    "unit_code": u.unit_code,
                    "unit_title": u.unit_title,
                    "skill_count": u.skill_count,
                    "qualification_codes": "; ".join(u.qualification_codes[:10]),
                }
                for u in units
            ]

            qual_rows = [
                {
                    "qualification_code": q.qualification_code,
                    "qualification_title": q.qualification_title,
                    "unit_count": len(q.unit_codes),
                    "skill_count": q.skill_count,
                    "occupation_codes": "; ".join(q.occupation_codes[:10]),
                }
                for q in qualifications
            ]

            occ_rows = [
                {
                    "anzsco_code": o.anzsco_code,
                    "anzsco_title": o.anzsco_title,
                    "qualification_count": len(o.qualification_codes),
                    "skill_count": o.skill_count,
                }
                for o in occupations
            ]

            with pd.ExcelWriter(output_path / "skill_assertion_export.xlsx", engine="openpyxl") as writer:
                pd.DataFrame(skills_rows).to_excel(writer, sheet_name="Skills", index=False)
                pd.DataFrame(assertion_rows).to_excel(writer, sheet_name="Assertions", index=False)
                pd.DataFrame(unit_rows).to_excel(writer, sheet_name="Units", index=False)
                pd.DataFrame(qual_rows).to_excel(writer, sheet_name="Qualifications", index=False)
                pd.DataFrame(occ_rows).to_excel(writer, sheet_name="Occupations", index=False)

            logger.info(f"Exported Excel: {output_path / 'skill_assertion_export.xlsx'}")
        except Exception as e:
            logger.warning(f"Excel export failed: {e}")

    def _export_search_engine(self, export_data, html_path, data_js_path):
        """Generate the HTML search engine + data JS file."""
        from src.export.search_engine import generate_search_html
        generate_search_html(export_data, str(html_path), str(data_js_path))