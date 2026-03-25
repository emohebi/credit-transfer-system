"""
Facet Assigner for Skill Assertion Pipeline.

Assigns facets to deduplicated Skill objects (not assertions).
Reuses the same embedding + LLM re-ranking approach as the original pipeline
but operates on a smaller set (unique skills only).
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

# Maximum retries for LLM JSON parsing failures
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
        self.stats = defaultdict(lambda: defaultdict(int))

        logger.info(f"FacetAssigner: facets={self.facets_to_assign}, llm={self.use_llm}")

    def assign_facets(self, df: pd.DataFrame, embeddings: np.ndarray, facets_override: List[str] = None) -> pd.DataFrame:
        """Assign facets to skills DataFrame.

        Args:
            facets_override: If provided, only assign these facets (ignores config).
        """
        active_facets = facets_override if facets_override is not None else self.facets_to_assign
        logger.info(f"Assigning {len(active_facets)} facets ({active_facets}) to {len(df)} skills")
        df = df.copy()

        self._precompute_facet_embeddings()

        # Init columns
        for fid in active_facets:
            df[f"facet_{fid}"] = None
            df[f"facet_{fid}_name"] = None
            df[f"facet_{fid}_confidence"] = 0.0

        # Assign using embedding similarity
        to_rerank = {fid: [] for fid in active_facets}

        for i in tqdm(range(len(df)), desc="Facet similarity"):
            skill_emb = embeddings[i].reshape(1, -1)

            for fid in active_facets:
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

                # Queue for LLM if ambiguous
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
                        # For ASCED, include unit titles as extra context
                        if fid == "ASCED" and "embedding_text_asced" in df.columns:
                            item["unit_context"] = str(df.iloc[i].get("embedding_text_asced", ""))[:500]
                        to_rerank[fid].append(item)
                        continue

                # Direct assignment
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

        # LLM re-ranking with retry logic
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

        self._log_stats(df, active_facets)
        return df

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

    def _build_rerank_prompt(self, fid: str, item: Dict) -> Tuple[str, str]:
        """
        Build tightly constrained system and user prompts for LLM re-ranking.
        Designed to suppress verbose thinking and force short JSON output.
        """
        fi = ALL_FACETS[fid]
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
        """
        Batch re-rank facet candidates using LLM with retry logic.

        For each item in the batch:
        - Attempts to parse the LLM response as JSON
        - On failure, retries up to MAX_LLM_RETRIES times with single-item regeneration
        - Falls back to embedding-based best candidate if all retries exhaust
        """
        results = {}

        # Build prompts
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
                                raise ValueError(f"Invalid choice: {choice}, expected 1-{len(item['candidates'])}")
                        else:
                            raise ValueError(f"Response is not a dict: {type(parsed)}")

                    except Exception as e:
                        retry_count -= 1
                        if retry_count > 0:
                            logger.debug(
                                f"Retry {fid} for skill idx={idx}, "
                                f"{retry_count} attempts left: {e}"
                            )
                            # Regenerate single response with fresh prompt
                            try:
                                sys_p, usr_p = self._build_rerank_prompt(fid, item)
                                single_responses = self.genai_interface._generate_batch(
                                    user_prompts=[usr_p],
                                    system_prompt=sys_p,
                                )
                                current_response = single_responses[0]
                            except Exception as retry_e:
                                logger.debug(f"Retry generation failed: {retry_e}")
                                break
                        else:
                            logger.debug(
                                f"All retries exhausted for {fid}, skill idx={idx}"
                            )

        except Exception as e:
            logger.warning(f"LLM rerank batch failed for {fid}: {e}")

        return results

    def _log_stats(self, df, facets=None):
        for fid in (facets or self.facets_to_assign):
            col = f"facet_{fid}"
            if col in df.columns:
                assigned = df[col].notna().sum()
                logger.info(f"  {fid}: {assigned}/{len(df)} assigned ({100*assigned/len(df):.1f}%)")