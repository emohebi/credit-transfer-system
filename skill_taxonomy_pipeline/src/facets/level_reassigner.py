"""
Level Reassigner for Skill Assertion Pipeline.

Assigns SFIA-aligned proficiency levels (LVL facet) to each assertion row
using embedding similarity + optional LLM re-ranking, enriched with unit
title context from the concordance.

This runs BEFORE deduplication so that all downstream steps (dedup,
facet assignment, archetype clustering) use facet-derived levels
consistently.

Design:
  - Groups rows by unique (skill_name, unit_code) to avoid redundant encoding
  - Encodes "{skill_name}. {unit_title}" for each unique pair
  - Computes similarity against the 7 LVL facet value descriptions
  - Optionally uses LLM to re-rank ambiguous cases
  - Overwrites the 'level' column with the assigned LVL integer
  - Adds 'level_confidence' column with assignment confidence

Usage in pipeline.py:
    reassigner = LevelReassigner(config, embedding_interface, genai_interface)
    df = reassigner.reassign_levels(df, concordance)
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from tqdm import tqdm

from config.facets import ALL_FACETS, get_facet_text_for_embedding

logger = logging.getLogger(__name__)

# LVL facet code → integer level
LVL_CODE_TO_INT = {
    "LVL.1": 1, "LVL.2": 2, "LVL.3": 3, "LVL.4": 4,
    "LVL.5": 5, "LVL.6": 6, "LVL.7": 7,
}

# Integer level → LVL facet code
INT_TO_LVL_CODE = {v: k for k, v in LVL_CODE_TO_INT.items()}


class LevelReassigner:
    """
    Reassigns proficiency levels to assertion rows using facet-based
    embedding similarity against SFIA level descriptions.

    Instead of trusting the raw 'level' column from the extractor,
    this uses semantic similarity (and optionally LLM judgement) to
    determine the appropriate SFIA level for each skill-in-unit pair.
    """

    def __init__(self, config: Dict, embedding_interface, genai_interface=None):
        self.config = config
        self.embedding_interface = embedding_interface
        self.genai_interface = genai_interface

        fc = config.get("facet_assignment", {})
        self.use_llm = fc.get("use_llm_reranking", True) and genai_interface is not None
        self.batch_size = config["embedding"].get("batch_size", 64)
        self.normalize = config["embedding"].get("normalize_embeddings", True)
        self.llm_batch_size = fc.get("genai_batch_size", 50)
        self.rerank_top_k = fc.get("rerank_top_k", 3)
        # Threshold below which we consider the assignment ambiguous
        # and queue for LLM re-ranking
        self.ambiguity_threshold = fc.get("level_ambiguity_threshold", 0.85)

        # Precompute LVL facet embeddings
        self.lvl_embeddings = None
        self.lvl_codes = None
        self._precompute_lvl_embeddings()

    def _precompute_lvl_embeddings(self):
        """Precompute embeddings for the 7 LVL facet value descriptions."""
        lvl_facet = ALL_FACETS.get("LVL", {})
        values = lvl_facet.get("values", {})

        codes = []
        texts = []
        for code in sorted(values.keys()):
            text = get_facet_text_for_embedding("LVL", code)
            codes.append(code)
            texts.append(text)

        if texts:
            self.lvl_embeddings = self.embedding_interface.encode(
                texts,
                batch_size=32,
                normalize_embeddings=self.normalize,
                show_progress=False,
            )
            self.lvl_codes = codes
            logger.info(f"Precomputed LVL facet embeddings: {len(codes)} levels")
        else:
            logger.warning("No LVL facet values found — level reassignment will be skipped")

    def reassign_levels(
        self,
        df: pd.DataFrame,
        concordance=None,
    ) -> pd.DataFrame:
        """
        Reassign proficiency levels to all assertion rows.

        Groups by unique (name, code) pairs to avoid redundant encoding.
        Each unique pair gets a unit-title-enriched embedding text.

        Args:
            df: Preprocessed DataFrame with 'name', 'code', 'level' columns
            concordance: Optional ConcordanceData for unit title enrichment

        Returns:
            DataFrame with 'level' column overwritten by facet-assigned values
            and 'level_confidence' column added.
        """
        if self.lvl_embeddings is None:
            logger.warning("LVL embeddings not available — keeping original levels")
            df["level_confidence"] = 0.0
            return df

        logger.info("=" * 60)
        logger.info("LEVEL REASSIGNMENT (LVL facet-based)")
        logger.info("=" * 60)

        df = df.copy()
        original_levels = df["level"].copy()

        # ── Step 1: Build unique (name, code) pairs ───────────────
        df["_pair_key"] = df["name"] + "|||" + df["code"]
        unique_pairs = df[["name", "code", "_pair_key"]].drop_duplicates(subset="_pair_key")
        logger.info(
            f"Total rows: {len(df)}, Unique (skill, unit) pairs: {len(unique_pairs)}"
        )

        # ── Step 2: Build enriched text for each pair ─────────────
        pair_texts = {}
        for _, row in unique_pairs.iterrows():
            key = row["_pair_key"]
            skill_name = row["name"]
            unit_code = row["code"]

            unit_title = ""
            if concordance:
                unit_title = concordance.unit_titles.get(unit_code, "")

            if unit_title:
                text = f"{skill_name}. Unit: {unit_title}"
            else:
                text = skill_name

            pair_texts[key] = text

        # ── Step 3: Encode unique pairs ───────────────────────────
        pair_keys_ordered = list(pair_texts.keys())
        texts_ordered = [pair_texts[k] for k in pair_keys_ordered]

        logger.info(f"Encoding {len(texts_ordered)} unique (skill, unit) pairs...")
        pair_embeddings = self.embedding_interface.encode(
            texts_ordered,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize,
        )
        logger.info(f"Pair embeddings shape: {pair_embeddings.shape}")

        # ── Step 4: Compute similarity against LVL facet values ───
        logger.info("Computing similarity against 7 LVL facet descriptions...")
        # (n_pairs, 7) similarity matrix
        sim_matrix = self.embedding_interface.similarity(
            pair_embeddings, self.lvl_embeddings
        )

        # ── Step 5: Assign best level + identify ambiguous cases ──
        pair_assignments = {}  # key → (lvl_int, confidence)
        ambiguous_items = []   # items to send to LLM

        for i, key in enumerate(pair_keys_ordered):
            sims = sim_matrix[i]
            best_idx = int(np.argmax(sims))
            best_sim = float(sims[best_idx])
            best_code = self.lvl_codes[best_idx]
            best_lvl = LVL_CODE_TO_INT[best_code]

            # Check for ambiguity: if top-2 are close, queue for LLM
            sorted_indices = np.argsort(sims)[::-1]
            if (
                self.use_llm
                and len(sorted_indices) > 1
                and best_sim < self.ambiguity_threshold
            ):
                second_sim = float(sims[sorted_indices[1]])
                gap = best_sim - second_sim
                if gap < 0.05:
                    # Ambiguous — queue for LLM re-ranking
                    top_candidates = []
                    for rank in range(min(self.rerank_top_k, len(sorted_indices))):
                        idx = sorted_indices[rank]
                        code = self.lvl_codes[idx]
                        info = ALL_FACETS["LVL"]["values"][code]
                        top_candidates.append({
                            "code": code,
                            "name": info.get("name", code),
                            "description": info.get("description", ""),
                            "similarity": float(sims[idx]),
                        })
                    ambiguous_items.append({
                        "key": key,
                        "text": pair_texts[key],
                        "candidates": top_candidates,
                        "embedding_best": (best_lvl, best_sim),
                    })
                    continue

            pair_assignments[key] = (best_lvl, best_sim)

        logger.info(
            f"Direct assignment: {len(pair_assignments)} pairs, "
            f"Ambiguous (queued for LLM): {len(ambiguous_items)} pairs"
        )

        # ── Step 6: LLM re-ranking for ambiguous cases ────────────
        if ambiguous_items and self.use_llm:
            logger.info(f"LLM re-ranking {len(ambiguous_items)} ambiguous level assignments...")
            llm_results = self._rerank_levels_llm(ambiguous_items)
            for item in ambiguous_items:
                key = item["key"]
                if key in llm_results:
                    pair_assignments[key] = llm_results[key]
                else:
                    # Fallback to embedding-based best
                    pair_assignments[key] = item["embedding_best"]
        elif ambiguous_items:
            # No LLM available — use embedding-based best
            for item in ambiguous_items:
                pair_assignments[item["key"]] = item["embedding_best"]

        # ── Step 7: Write back to DataFrame ───────────────────────
        new_levels = []
        new_confidences = []
        for _, row in df.iterrows():
            key = row["_pair_key"]
            if key in pair_assignments:
                lvl, conf = pair_assignments[key]
                new_levels.append(lvl)
                new_confidences.append(conf)
            else:
                # Should not happen, but fallback to original
                new_levels.append(row["level"])
                new_confidences.append(0.0)

        df["level"] = new_levels
        df["level_confidence"] = new_confidences

        # Clean up temp column
        df.drop(columns=["_pair_key"], inplace=True)

        # ── Log statistics ────────────────────────────────────────
        changed = (df["level"] != original_levels).sum()
        level_dist = df["level"].value_counts().sort_index().to_dict()
        avg_confidence = df["level_confidence"].mean()

        logger.info("=" * 60)
        logger.info("LEVEL REASSIGNMENT RESULTS")
        logger.info(f"  Total rows:        {len(df)}")
        logger.info(f"  Levels changed:    {changed} ({100*changed/len(df):.1f}%)")
        logger.info(f"  Avg confidence:    {avg_confidence:.3f}")
        logger.info(f"  Level distribution: {level_dist}")
        logger.info("=" * 60)

        return df

    def _rerank_levels_llm(self, items: List[Dict]) -> Dict[str, Tuple[int, float]]:
        """
        Use LLM to re-rank ambiguous level assignments.

        Args:
            items: List of dicts with 'key', 'text', 'candidates'

        Returns:
            Dict of {pair_key: (lvl_int, confidence)}
        """
        results = {}

        system_prompt = (
            "You are an expert in vocational education and SFIA proficiency levels.\n"
            "Given a skill name (optionally with its unit of competency title), "
            "select the most appropriate SFIA proficiency level.\n"
            "Consider:\n"
            "- Level 1 (Follow): Simple tasks under close supervision\n"
            "- Level 2 (Assist): Routine tasks with some guidance\n"
            "- Level 3 (Apply): Independent work in familiar contexts\n"
            "- Level 4 (Enable): Managing work, enabling others\n"
            "- Level 5 (Ensure & Advise): Ensuring compliance, advising on best practice\n"
            "- Level 6 (Initiate & Influence): Initiating improvements, influencing direction\n"
            "- Level 7 (Set Strategy): Setting strategy at the highest level\n\n"
            "Respond with valid JSON only: {\"choice\": <number>, \"confidence\": <0.0-1.0>}"
        )

        for batch_start in range(0, len(items), self.llm_batch_size):
            batch = items[batch_start:batch_start + self.llm_batch_size]
            user_prompts = []

            for item in batch:
                cands = "\n".join(
                    f"{i+1}. {c['name']}: {c['description']}"
                    for i, c in enumerate(item["candidates"])
                )
                prompt = (
                    f"SKILL IN CONTEXT: {item['text']}\n\n"
                    f"CANDIDATE LEVELS:\n{cands}\n\n"
                    f"Which level best fits this skill? Respond JSON only:"
                )
                user_prompts.append(prompt)

            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=user_prompts,
                    system_prompt=system_prompt,
                )

                for item, resp in zip(batch, responses):
                    try:
                        parsed = self.genai_interface._parse_json_response(resp)
                        if isinstance(parsed, dict):
                            choice = parsed.get("choice", 1)
                            conf = parsed.get("confidence", 0.7)
                            if 1 <= choice <= len(item["candidates"]):
                                code = item["candidates"][choice - 1]["code"]
                                lvl_int = LVL_CODE_TO_INT.get(code, 3)
                                results[item["key"]] = (lvl_int, float(conf))
                    except Exception as e:
                        logger.debug(f"Failed to parse LLM level response: {e}")

            except Exception as e:
                logger.warning(f"LLM level re-ranking batch failed: {e}")

        logger.info(f"LLM resolved {len(results)}/{len(items)} ambiguous level assignments")
        return results
