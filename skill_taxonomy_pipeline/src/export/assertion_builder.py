"""
Assertion Builder

Takes deduplicated skill registry + original rows + concordance data
and produces the full schema:

  - skills:          Deduplicated Skill objects (with denormalised qual/occ codes)
  - assertions:      SkillAssertion objects (one per original row)
  - units:           UnitOfCompetency objects (enriched from concordance)
  - qualifications:  Qualification objects (with precomputed skill_ids)
  - occupations:     Occupation objects (with precomputed skill_ids)

Precomputes all traversals at build time so the search engine
doesn't need to do graph traversal client-side.
"""
import logging
import pandas as pd
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from src.models.schema import (
    Skill, SkillAssertion, UnitOfCompetency, Qualification, Occupation,
)
from src.data_processing.concordance import ConcordanceData

logger = logging.getLogger(__name__)

LEVEL_NAMES = {
    1: "FOLLOW", 2: "ASSIST", 3: "APPLY", 4: "ENABLE",
    5: "ENSURE_ADVISE", 6: "INITIATE_INFLUENCE", 7: "SET_STRATEGY",
}


class AssertionBuilder:
    """Builds the full schema from preprocessed data + skill registry + concordance."""

    def build(
        self,
        df: pd.DataFrame,
        skill_registry: Dict,
        concordance: Optional[ConcordanceData] = None,
    ) -> Tuple[List[Skill], List[SkillAssertion], List[UnitOfCompetency],
               List[Qualification], List[Occupation]]:
        """
        Returns:
            (skills, assertions, units, qualifications, occupations)
        """
        logger.info("Building schema (5 objects)...")
        has_concordance = concordance is not None

        # ── 1. Assertions (one per original row) ─────────────────
        assertions = []
        for idx, row in df.iterrows():
            uc = row["code"]
            # Resolve qual/occ codes for this assertion's unit
            a_qual_codes = []
            a_occ_codes = []
            if has_concordance:
                a_qual_codes = concordance.unit_to_quals.get(uc, [])
                for qc in a_qual_codes:
                    a_occ_codes.extend(concordance.qual_to_occupations.get(qc, []))
                a_occ_codes = sorted(set(a_occ_codes))

            assertions.append(SkillAssertion(
                assertion_id=f"SA-{idx:06d}",
                skill_id=row["skill_id"],
                unit_code=uc,
                teaching_context=row["context"],
                level_of_engagement=LEVEL_NAMES.get(int(row["level"]), "APPLY"),
                evidence=str(row.get("evidence", "")),
                keywords=row.get("keywords_list", []) if isinstance(row.get("keywords_list"), list) else [],
                confidence=float(row.get("confidence", 0.0)),
                category=str(row.get("category", "")),
                qualification_codes=a_qual_codes,
                occupation_codes=a_occ_codes,
            ))

        # ── 2. unit_code → skill_ids index ───────────────────────
        unit_to_skill_ids: Dict[str, set] = defaultdict(set)
        for a in assertions:
            unit_to_skill_ids[a.unit_code].add(a.skill_id)

        # ── 3. Units ─────────────────────────────────────────────
        units = []
        for code in sorted(df["code"].unique()):
            sids = sorted(unit_to_skill_ids.get(code, set()))
            units.append(UnitOfCompetency(
                unit_code=code,
                unit_title=concordance.unit_titles.get(code, "") if has_concordance else "",
                qualification_codes=concordance.unit_to_quals.get(code, []) if has_concordance else [],
                skill_count=len(sids),
                skill_ids=sids,
            ))

        # ── 4. Precompute traversals ─────────────────────────────
        qual_to_skill_ids: Dict[str, set] = defaultdict(set)
        occ_to_skill_ids: Dict[str, set] = defaultdict(set)

        if has_concordance:
            for qc, ucs in concordance.qual_to_units.items():
                for uc in ucs:
                    qual_to_skill_ids[qc].update(unit_to_skill_ids.get(uc, set()))
            for ac, qcs in concordance.occupation_to_quals.items():
                for qc in qcs:
                    occ_to_skill_ids[ac].update(qual_to_skill_ids.get(qc, set()))

        # ── 5. Qualifications ────────────────────────────────────
        qualifications = []
        if has_concordance:
            for qc, qt in sorted(concordance.qual_titles.items()):
                sids = sorted(qual_to_skill_ids.get(qc, set()))
                qualifications.append(Qualification(
                    qualification_code=qc,
                    qualification_title=qt,
                    unit_codes=concordance.qual_to_units.get(qc, []),
                    occupation_codes=concordance.qual_to_occupations.get(qc, []),
                    skill_ids=sids,
                    skill_count=len(sids),
                ))

        # ── 6. Occupations ───────────────────────────────────────
        occupations = []
        if has_concordance:
            for ac, at in sorted(concordance.occupation_titles.items()):
                sids = sorted(occ_to_skill_ids.get(ac, set()))
                occupations.append(Occupation(
                    anzsco_code=ac,
                    anzsco_title=at,
                    qualification_codes=concordance.occupation_to_quals.get(ac, []),
                    skill_ids=sids,
                    skill_count=len(sids),
                ))

        # ── 7. Skills (denormalise qual/occ onto skill) ──────────
        skill_qual_codes: Dict[str, set] = defaultdict(set)
        skill_occ_codes: Dict[str, set] = defaultdict(set)
        for q in qualifications:
            for sid in q.skill_ids:
                skill_qual_codes[sid].add(q.qualification_code)
        for o in occupations:
            for sid in o.skill_ids:
                skill_occ_codes[sid].add(o.anzsco_code)

        skills = []
        for sid, info in skill_registry.items():
            skills.append(Skill(
                skill_id=sid,
                preferred_label=info["preferred_label"],
                alternative_labels=info["alternative_labels"],
                definition=info["definition"],
                category=info["category"],
                assertion_count=info["assertion_count"],
                unit_codes=info["unit_codes"],
                facets=info.get("facets", {}),
                qualification_codes=sorted(skill_qual_codes.get(sid, set())),
                occupation_codes=sorted(skill_occ_codes.get(sid, set())),
            ))

        # ── Log ──────────────────────────────────────────────────
        logger.info(f"Built: {len(skills)} skills, {len(assertions)} assertions, "
                     f"{len(units)} units, {len(qualifications)} quals, {len(occupations)} occs")
        if has_concordance:
            logger.info(f"  Skills with qualifications: {sum(1 for s in skills if s.qualification_codes)}")
            logger.info(f"  Skills with occupations: {sum(1 for s in skills if s.occupation_codes)}")

        return skills, assertions, units, qualifications, occupations
