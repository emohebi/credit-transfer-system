"""
Facet Assigner for Skill Assertion Pipeline.

Assigns facets to deduplicated Skill objects (not assertions).
Uses embedding similarity + optional LLM re-ranking.

Special handling for THA (Transferable Human Ability):
  - THA values are scoped by TRF (Transferability)
  - A skill with TRF.BRD only matches against THA.BRD.* values
  - TRF must be assigned before THA in the facet ordering
"""
import logging
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from tqdm import tqdm

from config.facets import (
    ALL_FACETS, MULTI_VALUE_FACETS,
    get_all_facet_embeddings_texts,
)

logger = logging.getLogger(__name__)

MAX_LLM_RETRIES = 5


class FacetAssigner:
    """Assigns configurable facet values to skills using embedding + LLM."""

    def __init__(self, config: Dict, genai_interface=None, embedding_interface=None):
        self.config = config
        self.genai_interface = genai_interface
        self.embedding_interface = embedding_interface

        fc = config.get("facet_assignment", {})
        self.facets_to_assign = fc.get("facets_to_assign", [])
        self.use_llm = fc.get("use_llm_reranking", True) and genai_interface is not None
        self.rerank_top_k = fc.get("rerank_top_k", 5)
        self.threshold = fc.get("embedding_similarity_threshold", 0.3)
        self.multi_value_threshold = fc.get("multi_value_threshold", 0.25)
        self.max_multi_values = fc.get("max_multi_values", 5)
        self.batch_size = fc.get("genai_batch_size", 50)

        self.facet_embeddings = {}
        self.facet_value_keys = {}

        # THA-specific: embeddings grouped by parent TRF
        self._tha_embeddings_by_trf = {}
        self._tha_keys_by_trf = {}

        self.stats = defaultdict(lambda: defaultdict(int))

        logger.info(f"FacetAssigner: facets={self.facets_to_assign}, llm={self.use_llm}")

    def assign_facets(self, df: pd.DataFrame, embeddings: np.ndarray, facets_override: List[str] = None) -> pd.DataFrame:
        """Assign facets to skills DataFrame."""
        active_facets = facets_override if facets_override is not None else self.facets_to_assign
        logger.info(f"Assigning {len(active_facets)} facets ({active_facets}) to {len(df)} skills")
        df = df.copy()

        self._precompute_facet_embeddings()

        # Init columns
        for fid in active_facets:
            df[f"facet_{fid}"] = None
            df[f"facet_{fid}_name"] = None
            df[f"facet_{fid}_confidence"] = 0.0

        # Separate THA from other facets (THA needs special TRF-scoped handling)
        standard_facets = [f for f in active_facets if f != "THA"]
        has_tha = "THA" in active_facets

        # Assign standard facets
        if standard_facets:
            df = self._assign_standard_facets(df, embeddings, standard_facets)

        # Assign THA (must run after TRF is assigned)
        if has_tha:
            if "facet_TRF" not in df.columns or df["facet_TRF"].isna().all():
                logger.warning("TRF not assigned — cannot scope THA assignment. Skipping THA.")
            else:
                df = self._assign_tha_facet(df, embeddings)

        self._log_stats(df, active_facets)
        return df

    # ═══════════════════════════════════════════════════════════════
    #  STANDARD FACET ASSIGNMENT
    # ═══════════════════════════════════════════════════════════════

    def _assign_standard_facets(self, df: pd.DataFrame, embeddings: np.ndarray, facets: List[str]) -> pd.DataFrame:
        """Assign non-THA facets using embedding similarity + optional LLM re-ranking."""
        to_rerank = {fid: [] for fid in facets}

        for i in tqdm(range(len(df)), desc="Facet similarity"):
            skill_emb = embeddings[i].reshape(1, -1)

            for fid in facets:
                if fid not in self.facet_embeddings:
                    continue

                sims = self.embedding_interface.similarity(
                    skill_emb, self.facet_embeddings[fid]
                )[0]
                top_idx = np.argsort(sims)[-self.rerank_top_k:][::-1]
                top_sims = sims[top_idx]
                keys = self.facet_value_keys[fid]

                best_sim = top_sims[0]
                best_code = keys[top_idx[0]]

                if self.use_llm and len(top_idx) > 1 and best_sim < self.threshold:
                    candidates = [
                        {"code": keys[j], "name": ALL_FACETS[fid]["values"][keys[j]].get("name", keys[j]),
                         "description": ALL_FACETS[fid]["values"][keys[j]].get("description", ""),
                         "similarity": float(top_sims[k])}
                        for k, j in enumerate(top_idx) if top_sims[k] >= self.multi_value_threshold
                    ]
                    if len(candidates) > 1:
                        item = {
                            "idx": df.index[i],
                            "skill_name": df.iloc[i]["name"],
                            "skill_desc": str(df.iloc[i].get("description", ""))[:300],
                            "candidates": candidates,
                        }
                        if fid == "ASCED" and "embedding_text_asced" in df.columns:
                            item["unit_context"] = str(df.iloc[i].get("embedding_text_asced", ""))[:500]
                        to_rerank[fid].append(item)
                        continue

                info = ALL_FACETS[fid]["values"].get(best_code, {})
                if fid in MULTI_VALUE_FACETS:
                    codes = [keys[top_idx[k]] for k in range(min(self.max_multi_values, len(top_idx)))
                             if top_sims[k] >= self.multi_value_threshold]
                    df.at[df.index[i], f"facet_{fid}"] = json.dumps(codes)
                    df.at[df.index[i], f"facet_{fid}_name"] = ", ".join(
                        ALL_FACETS[fid]["values"][c]["name"] for c in codes
                    )
                else:
                    df.at[df.index[i], f"facet_{fid}"] = best_code
                    df.at[df.index[i], f"facet_{fid}_name"] = info.get("name", best_code)
                df.at[df.index[i], f"facet_{fid}_confidence"] = float(best_sim)

        # LLM re-ranking
        for fid, items in to_rerank.items():
            if not items:
                continue
            logger.info(f"LLM re-ranking {len(items)} skills for {fid}")
            for batch_start in range(0, len(items), self.batch_size):
                batch = items[batch_start:batch_start + self.batch_size]
                results = self._rerank_batch(fid, batch)
                for item in batch:
                    idx = item["idx"]
                    if idx in results:
                        code, conf = results[idx]
                        info = ALL_FACETS[fid]["values"].get(code, {})
                        df.at[idx, f"facet_{fid}"] = code
                        df.at[idx, f"facet_{fid}_name"] = info.get("name", code)
                        df.at[idx, f"facet_{fid}_confidence"] = conf
                    else:
                        c = item["candidates"][0]
                        df.at[idx, f"facet_{fid}"] = c["code"]
                        df.at[idx, f"facet_{fid}_name"] = c["name"]
                        df.at[idx, f"facet_{fid}_confidence"] = c["similarity"]

        return df

    # ═══════════════════════════════════════════════════════════════
    #  THA ASSIGNMENT (TRF-SCOPED)
    # ═══════════════════════════════════════════════════════════════

    def _assign_tha_facet(self, df: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
        """
        Assign THA facet using TRF-scoped candidate filtering.

        For each skill:
        1. Look up its assigned TRF value (e.g., TRF.BRD)
        2. Only compare against THA values whose parent_trf matches (e.g., THA.BRD.*)
        3. Assign best-matching THA(s) using embedding similarity
        4. Optionally LLM re-rank ambiguous cases
        """
        logger.info("Assigning THA facet (TRF-scoped)...")

        # Prepare TRF-grouped THA embeddings
        self._prepare_tha_by_trf()

        to_rerank = []

        for i in tqdm(range(len(df)), desc="THA similarity (TRF-scoped)"):
            skill_emb = embeddings[i].reshape(1, -1)
            trf_code = df.iloc[i].get("facet_TRF")

            if pd.isna(trf_code) or trf_code not in self._tha_embeddings_by_trf:
                # No TRF or no THA values for this TRF — skip
                continue

            tha_embs = self._tha_embeddings_by_trf[trf_code]
            tha_keys = self._tha_keys_by_trf[trf_code]

            if len(tha_keys) == 0:
                continue

            sims = self.embedding_interface.similarity(skill_emb, tha_embs)[0]
            top_k = min(self.rerank_top_k, len(tha_keys))
            top_idx = np.argsort(sims)[-top_k:][::-1]
            top_sims = sims[top_idx]

            best_sim = top_sims[0]
            best_code = tha_keys[top_idx[0]]

            # Queue for LLM if ambiguous
            if self.use_llm and len(top_idx) > 1 and best_sim < self.threshold:
                candidates = [
                    {"code": tha_keys[j],
                     "name": ALL_FACETS["THA"]["values"][tha_keys[j]].get("name", tha_keys[j]),
                     "description": ALL_FACETS["THA"]["values"][tha_keys[j]].get("description", ""),
                     "similarity": float(top_sims[k])}
                    for k, j in enumerate(top_idx) if top_sims[k] >= self.multi_value_threshold
                ]
                if len(candidates) > 1:
                    to_rerank.append({
                        "idx": df.index[i],
                        "skill_name": df.iloc[i]["name"],
                        "skill_desc": str(df.iloc[i].get("description", ""))[:300],
                        "candidates": candidates,
                    })
                    continue

            # Direct assignment (single best match)
            df.at[df.index[i], "facet_THA"] = best_code
            df.at[df.index[i], "facet_THA_name"] = ALL_FACETS["THA"]["values"].get(best_code, {}).get("name", best_code)
            df.at[df.index[i], "facet_THA_confidence"] = float(best_sim)

        # LLM re-ranking for ambiguous THA assignments
        if to_rerank:
            logger.info(f"LLM re-ranking {len(to_rerank)} skills for THA")
            for batch_start in range(0, len(to_rerank), self.batch_size):
                batch = to_rerank[batch_start:batch_start + self.batch_size]
                results = self._rerank_batch("THA", batch)
                for item in batch:
                    idx = item["idx"]
                    if idx in results:
                        code, conf = results[idx]
                        info = ALL_FACETS["THA"]["values"].get(code, {})
                        df.at[idx, "facet_THA"] = code
                        df.at[idx, "facet_THA_name"] = info.get("name", code)
                        df.at[idx, "facet_THA_confidence"] = conf
                    else:
                        c = item["candidates"][0]
                        df.at[idx, "facet_THA"] = c["code"]
                        df.at[idx, "facet_THA_name"] = c["name"]
                        df.at[idx, "facet_THA_confidence"] = c["similarity"]

        return df

    def _prepare_tha_by_trf(self):
        """Group THA embeddings by their parent TRF code."""
        if self._tha_embeddings_by_trf:
            return  # Already prepared

        if "THA" not in self.facet_embeddings:
            return

        all_embs = self.facet_embeddings["THA"]
        all_keys = self.facet_value_keys["THA"]
        tha_values = ALL_FACETS["THA"]["values"]

        # Group indices by parent_trf
        trf_groups = defaultdict(list)
        for i, key in enumerate(all_keys):
            parent_trf = tha_values[key].get("parent_trf", "")
            if parent_trf:
                trf_groups[parent_trf].append(i)

        for trf_code, indices in trf_groups.items():
            self._tha_embeddings_by_trf[trf_code] = all_embs[indices]
            self._tha_keys_by_trf[trf_code] = [all_keys[i] for i in indices]

        logger.info(f"THA embeddings grouped by TRF: {', '.join(f'{k}:{len(v)}' for k, v in self._tha_keys_by_trf.items())}")

    # ═══════════════════════════════════════════════════════════════
    #  PRECOMPUTATION
    # ═══════════════════════════════════════════════════════════════

    def _precompute_facet_embeddings(self):
        if not self.embedding_interface:
            return
        all_texts = get_all_facet_embeddings_texts()
        for fid in self.facets_to_assign:
            if fid not in all_texts:
                continue
            texts, keys = [], []
            for code, text in all_texts[fid].items():
                texts.append(text)
                keys.append(code)
            if texts:
                self.facet_embeddings[fid] = self.embedding_interface.encode(
                    texts, batch_size=32, show_progress=False
                )
                self.facet_value_keys[fid] = keys

    # ═══════════════════════════════════════════════════════════════
    #  LLM RE-RANKING (shared by standard and THA)
    # ═══════════════════════════════════════════════════════════════

    def _build_rerank_prompt(self, fid: str, item: Dict) -> Tuple[str, str]:
        """Build tightly constrained prompts for LLM re-ranking."""
        fi = ALL_FACETS[fid]

        if fid == "TRF":
            # Special TRF prompt that discriminates on domain knowledge
            system = (
                "You classify Australian VET skills by their transferability level.\n\n"
                "CATEGORIES:\n"
                "1. Universal — Generic employability skills everyone needs: communication, "
                "numeracy, teamwork, time management, digital literacy, ethics.\n"
                "2. Cross-Sector — Professional/management skills transferable WITHOUT "
                "specialist trade or domain knowledge: project management, risk assessment, "
                "compliance, data analysis, leadership, budgeting, reporting. A general "
                "professional could perform this skill in any industry.\n"
                "3. Sector-Specific — Technical skills shared across related occupations "
                "requiring some specialist knowledge: fault diagnosis, inspection, calibration, "
                "care planning, clinical assessment, process monitoring, laboratory work.\n"
                "4. Occupation-Specific — Hands-on skills requiring specialist tools, materials, "
                "physical techniques, or deep domain knowledge unique to a trade or occupation: "
                "welding, wiring, plumbing, animal handling, cooking, hairdressing, concreting, "
                "crane operation, medication administration, farming, shearing.\n\n"
                "KEY DECISION RULE:\n"
                "If the skill mentions specific animals, plants, crops, chemicals, body parts, "
                "machinery, or trade materials — it likely requires domain-specific knowledge "
                "and should be Occupation-Specific, even if the ACTIVITY sounds like management, "
                "compliance, or risk assessment.\n"
                "Example: 'Alpaca Hazard Assessment' = Occupation-Specific (needs alpaca knowledge)\n"
                "Example: 'Workplace Risk Assessment' = Cross-Sector (generic process)\n"
                "Example: 'Carcass Biosecurity Management' = Occupation-Specific (needs meat industry knowledge)\n"
                "Example: 'Regulatory Compliance Auditing' = Cross-Sector (generic process)\n\n"
                "RULES:\n"
                "- Output ONLY a JSON object: {\"choice\": <int>, \"confidence\": <float>}\n"
                "- choice = the candidate number (1-based) that best fits\n"
                "- confidence = your confidence from 0.0 to 1.0\n"
                "- Do NOT output any reasoning, explanation, or text outside the JSON\n"
                "- Do NOT wrap in markdown code blocks"
            )
        else:
            system = (
                f"You classify vocational skills into {fi['facet_name']} categories.\n"
                f"{fi['description']}\n\n"
                f"RULES:\n"
                f"- Output ONLY a JSON object: {{\"choice\": <int>, \"confidence\": <float>}}\n"
                f"- choice = the candidate number (1-based) that best fits\n"
                f"- confidence = your confidence from 0.0 to 1.0\n"
                f"- Do NOT output any reasoning, explanation, or text outside the JSON\n"
                f"- Do NOT wrap in markdown code blocks"
            )

        cands = "\n".join(
            f"{i+1}. {c['name']}: {c['description']}"
            for i, c in enumerate(item["candidates"])
        )
        prompt = f"SKILL: {item['skill_name']}\n"
        if item.get("skill_desc"):
            prompt += f"DESCRIPTION: {item['skill_desc']}\n"
        if item.get("unit_context"):
            prompt += f"TEACHING CONTEXT: {item['unit_context']}\n"
        prompt += f"\nCANDIDATES:\n{cands}\n\n{{\"choice\":"

        return system, prompt

    def _rerank_batch(self, fid: str, batch: List[Dict]) -> Dict:
        """Batch re-rank with retry logic."""
        results = {}

        system_prompt = None
        user_prompts = []
        for item in batch:
            sys_p, usr_p = self._build_rerank_prompt(fid, item)
            if system_prompt is None:
                system_prompt = sys_p
            user_prompts.append(usr_p)

        try:
            responses = self.genai_interface._generate_batch(
                user_prompts=user_prompts, system_prompt=system_prompt
            )

            for item, response in zip(batch, responses):
                idx = item["idx"]
                retry_count = MAX_LLM_RETRIES
                current_response = response

                while retry_count > 0:
                    try:
                        parsed = self.genai_interface._parse_json_response(current_response)
                        if isinstance(parsed, dict):
                            choice = parsed.get("choice", 1)
                            conf = parsed.get("confidence", 0.7)
                            if 1 <= choice <= len(item["candidates"]):
                                results[idx] = (item["candidates"][choice - 1]["code"], float(conf))
                                break
                            else:
                                raise ValueError(f"Invalid choice: {choice}")
                        else:
                            raise ValueError(f"Not a dict: {type(parsed)}")

                    except Exception as e:
                        retry_count -= 1
                        if retry_count > 0:
                            logger.debug(f"Retry {fid} idx={idx}, {retry_count} left: {e}")
                            try:
                                sys_p, usr_p = self._build_rerank_prompt(fid, item)
                                single = self.genai_interface._generate_batch(
                                    user_prompts=[usr_p], system_prompt=sys_p,
                                )
                                current_response = single[0]
                            except Exception as retry_e:
                                logger.debug(f"Retry generation failed: {retry_e}")
                                break
                        else:
                            logger.debug(f"All retries exhausted for {fid} idx={idx}")

        except Exception as e:
            logger.warning(f"LLM rerank batch failed for {fid}: {e}")

        return results

    # ═══════════════════════════════════════════════════════════════
    #  LOGGING
    # ═══════════════════════════════════════════════════════════════

    def _log_stats(self, df, facets=None):
        for fid in (facets or self.facets_to_assign):
            col = f"facet_{fid}"
            if col in df.columns:
                assigned = df[col].notna().sum()
                logger.info(f"  {fid}: {assigned}/{len(df)} assigned ({100*assigned/len(df):.1f}%)")