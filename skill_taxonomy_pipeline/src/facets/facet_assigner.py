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

    def assign_facets(self, df: pd.DataFrame, embeddings: np.ndarray) -> pd.DataFrame:
        """Assign facets to skills DataFrame."""
        logger.info(f"Assigning {len(self.facets_to_assign)} facets to {len(df)} skills")
        df = df.copy()

        self._precompute_facet_embeddings()

        # Init columns
        for fid in self.facets_to_assign:
            df[f"facet_{fid}"] = None
            df[f"facet_{fid}_name"] = None
            df[f"facet_{fid}_confidence"] = 0.0

        # Assign using embedding similarity
        to_rerank = {fid: [] for fid in self.facets_to_assign}

        for i in tqdm(range(len(df)), desc="Facet similarity"):
            skill_emb = embeddings[i].reshape(1, -1)

            for fid in self.facets_to_assign:
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

        self._log_stats(df)
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

    def _rerank_batch(self, fid: str, batch: List[Dict]) -> Dict:
        fi = ALL_FACETS[fid]
        system = (
            f"You are an expert in vocational skills classification.\n"
            f"Select the BEST {fi['facet_name']} category for each skill.\n"
            f"{fi['description']}\n"
            f"Respond with valid JSON only: {{\"choice\": <number>, \"confidence\": <0-1>}}"
        )
        prompts = []
        for item in batch:
            cands = "\n".join(f"{i+1}. {c['name']}: {c['description']}" for i, c in enumerate(item["candidates"]))
            prompt = f"SKILL: {item['skill_name']}\nDESCRIPTION: {item['skill_desc']}\n"
            # Include unit title context for ASCED
            if "unit_context" in item and item["unit_context"]:
                prompt += f"TEACHING CONTEXT: {item['unit_context']}\n"
            prompt += f"\nCANDIDATES:\n{cands}\n\nRespond JSON only:"
            prompts.append(prompt)
        results = {}
        try:
            responses = self.genai_interface._generate_batch(user_prompts=prompts, system_prompt=system)
            for item, resp in zip(batch, responses):
                try:
                    parsed = self.genai_interface._parse_json_response(resp)
                    if isinstance(parsed, dict):
                        choice = parsed.get("choice", 1)
                        conf = parsed.get("confidence", 0.7)
                        if 1 <= choice <= len(item["candidates"]):
                            c = item["candidates"][choice - 1]
                            results[item["idx"]] = (c["code"], conf)
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"LLM rerank failed for {fid}: {e}")
        return results

    def _log_stats(self, df):
        for fid in self.facets_to_assign:
            col = f"facet_{fid}"
            if col in df.columns:
                assigned = df[col].notna().sum()
                logger.info(f"  {fid}: {assigned}/{len(df)} assigned ({100*assigned/len(df):.1f}%)")