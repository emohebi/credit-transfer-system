"""
Facet Assignment Module
Assigns skills to multiple facet values using embedding similarity + LLM re-ranking

Each skill receives values across multiple independent facets (dimensions),
enabling multi-dimensional querying and flexible taxonomy views.

Facets:
- NAT: Skill Nature (Technical, Cognitive, Social, Self-Management, Foundational, Regulatory)
- TRF: Transferability (Universal, Broad, Sector-Specific, Occupation-Specific)
- COG: Cognitive Complexity (Remember, Understand, Apply, Analyse, Evaluate, Create)
- CTX: Work Context (Information, People, Things, Systems, Ideas)
- FUT: Future Readiness (Uniquely Human, Collaborative, Augmentable, Automatable, Emerging)
- LRN: Learning Context (Theoretical, Practical, Workplace, Hybrid, Digital)
- DIG: Digital Intensity (Minimal, Low, Medium, High, Advanced)
- IND: Industry Domain (multi-value - Construction, Health, ICT, etc.)
- LVL: Proficiency Level (1-7, mapped from existing level column)
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from tqdm import tqdm
import json
import re

try:
    from config.facets import (
        ALL_FACETS, MULTI_VALUE_FACETS, ORDERED_FACETS, FACET_PRIORITY,
        get_facet_text_for_embedding, get_all_facet_embeddings_texts
    )
except ImportError:
    # Fallback if running from different directory
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from config.facets import (
        ALL_FACETS, MULTI_VALUE_FACETS, ORDERED_FACETS, FACET_PRIORITY,
        get_facet_text_for_embedding, get_all_facet_embeddings_texts
    )

logger = logging.getLogger(__name__)


class FacetAssigner:
    """
    Assigns skills to multiple facet values using:
    1. Embedding similarity to find top-K candidates
    2. LLM re-ranking to select best match from candidates
    
    Supports both single-value and multi-value facets.
    """
    
    def __init__(self, config: Dict, genai_interface=None, embedding_interface=None):
        """
        Initialize the facet assigner
        
        Args:
            config: Configuration dictionary
            genai_interface: GenAI interface for LLM-based re-ranking
            embedding_interface: Embedding interface for similarity matching
        """
        self.config = config
        self.genai_interface = genai_interface
        self.embedding_interface = embedding_interface
        
        # Load settings
        self.facet_config = config.get('facet_assignment', {})
        
        # Settings
        self.use_genai = self.facet_config.get('use_genai', True) and genai_interface is not None
        self.batch_size = self.facet_config.get('genai_batch_size', 50)
        self.use_llm_reranking = self.facet_config.get('use_llm_reranking', True) and genai_interface is not None
        self.rerank_top_k = self.facet_config.get('rerank_top_k', 3)
        self.embedding_threshold = self.facet_config.get('embedding_similarity_threshold', 0.3)
        self.multi_value_threshold = self.facet_config.get('multi_value_threshold', 0.25)
        self.max_multi_values = self.facet_config.get('max_multi_values', 3)
        
        # Facets to assign
        self.facets_to_assign = self.facet_config.get('facets_to_assign', FACET_PRIORITY)
        
        # Precomputed embeddings for each facet
        self.facet_embeddings = {}  # {facet_id: {value_code: embedding}}
        self.facet_value_keys = {}  # {facet_id: [value_codes]}
        
        # Statistics
        self.assignment_stats = defaultdict(lambda: defaultdict(int))
        
        logger.info(f"Initialized FacetAssigner")
        logger.info(f"  Facets to assign: {self.facets_to_assign}")
        logger.info(f"  Use GenAI: {self.use_genai}")
        logger.info(f"  Use LLM Re-ranking: {self.use_llm_reranking}")
        logger.info(f"  Re-rank Top-K: {self.rerank_top_k}")
    
    def _precompute_facet_embeddings(self):
        """Precompute embeddings for all facet values"""
        if self.embedding_interface is None:
            logger.warning("No embedding interface provided, skipping facet embedding precomputation")
            return
        
        logger.info("Precomputing facet embeddings...")
        
        all_texts = get_all_facet_embeddings_texts()
        
        for facet_id in self.facets_to_assign:
            if facet_id not in all_texts:
                continue
                
            facet_texts = all_texts[facet_id]
            texts_list = []
            keys_list = []
            
            for value_code, text in facet_texts.items():
                texts_list.append(text)
                keys_list.append(value_code)
            
            if texts_list:
                embeddings = self.embedding_interface.encode(
                    texts_list,
                    batch_size=32,
                    show_progress=False
                )
                
                self.facet_embeddings[facet_id] = embeddings
                self.facet_value_keys[facet_id] = keys_list
                
                logger.info(f"  {facet_id}: {len(keys_list)} values")
    
    def assign_facets(self, df: pd.DataFrame, embeddings: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Assign facet values to all skills
        
        Args:
            df: DataFrame with skills data
            embeddings: Precomputed skill embeddings
            
        Returns:
            DataFrame with facet columns added
        """
        logger.info("=" * 80)
        logger.info("ASSIGNING FACETS TO SKILLS")
        logger.info("=" * 80)
        logger.info(f"Processing {len(df)} skills across {len(self.facets_to_assign)} facets")
        
        df_result = df.copy()
        
        # Precompute facet embeddings
        self._precompute_facet_embeddings()
        
        # Store skill embeddings
        self.skill_embeddings = embeddings
        
        # Initialize facet columns
        for facet_id in self.facets_to_assign:
            df_result[f'facet_{facet_id}'] = None
            df_result[f'facet_{facet_id}_name'] = None
            df_result[f'facet_{facet_id}_confidence'] = 0.0
            df_result[f'facet_{facet_id}_method'] = None
        
        # Special handling for LVL facet - use existing level column
        if 'LVL' in self.facets_to_assign and 'level' in df_result.columns:
            df_result = self._assign_level_facet(df_result)
        
        # Special handling for LRN facet - use existing context column
        # if 'LRN' in self.facets_to_assign and 'context' in df_result.columns:
        #     df_result = self._assign_learning_context_facet(df_result)
        
        # Assign other facets using embedding + LLM
        facets_for_embedding = [f for f in self.facets_to_assign 
                               if f not in ['LVL'] or f not in df_result.columns]
        
        if facets_for_embedding and self.skill_embeddings is not None:
            df_result = self._assign_facets_with_embeddings(df_result, facets_for_embedding)
        
        # Log statistics
        self._log_assignment_statistics(df_result)
        
        return df_result
    
    def _assign_level_facet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map existing level column to LVL facet"""
        logger.info("Mapping existing level column to LVL facet...")
        
        level_map = {
            1: "LVL.1", 2: "LVL.2", 3: "LVL.3", 4: "LVL.4",
            5: "LVL.5", 6: "LVL.6", 7: "LVL.7"
        }
        
        level_names = {
            "LVL.1": "Foundation", "LVL.2": "Developing", "LVL.3": "Competent",
            "LVL.4": "Proficient", "LVL.5": "Advanced", "LVL.6": "Expert",
            "LVL.7": "Master"
        }
        
        for idx in df.index:
            level = df.loc[idx, 'level']
            try:
                level_int = int(level)
                level_code = level_map.get(level_int, "LVL.3")
            except (ValueError, TypeError):
                level_code = "LVL.3"
            
            df.loc[idx, 'facet_LVL'] = level_code
            df.loc[idx, 'facet_LVL_name'] = level_names.get(level_code, "Competent")
            df.loc[idx, 'facet_LVL_confidence'] = 1.0
            df.loc[idx, 'facet_LVL_method'] = 'direct_mapping'
            self.assignment_stats['LVL']['direct_mapping'] += 1
        
        return df
    
    def _assign_learning_context_facet(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map existing context column to LRN facet"""
        logger.info("Mapping existing context column to LRN facet...")
        
        context_map = {
            'practical': "LRN.PRA",
            'theoretical': "LRN.THE",
            'hybrid': "LRN.HYB"
        }
        
        context_names = {
            "LRN.PRA": "Practical/Hands-on",
            "LRN.THE": "Theoretical/Academic",
            "LRN.HYB": "Hybrid/Blended",
            "LRN.WRK": "Workplace/On-the-Job",
            "LRN.DIG": "Digital/Self-Paced"
        }
        
        for idx in df.index:
            context = str(df.loc[idx, 'context']).lower()
            context_code = context_map.get(context, "LRN.HYB")
            
            df.loc[idx, 'facet_LRN'] = context_code
            df.loc[idx, 'facet_LRN_name'] = context_names.get(context_code, "Hybrid/Blended")
            df.loc[idx, 'facet_LRN_confidence'] = 1.0
            df.loc[idx, 'facet_LRN_method'] = 'direct_mapping'
            self.assignment_stats['LRN']['direct_mapping'] += 1
        
        return df
    
    def _assign_facets_with_embeddings(self, df: pd.DataFrame, facets: List[str]) -> pd.DataFrame:
        """Assign facets using embedding similarity + optional LLM re-ranking"""
        
        indices = df.index.tolist()
        
        # Collect skills that need LLM re-ranking for each facet
        to_be_reranked = {facet_id: [] for facet_id in facets}
        
        for idx in tqdm(indices, desc="Computing facet similarities"):
            position = df.index.get_loc(idx)
            skill_emb = self.skill_embeddings[position].reshape(1, -1)
            skill_name = df.loc[idx, 'name']
            skill_desc = df.loc[idx, 'description'] if 'description' in df.columns else ''
            skill_category = df.loc[idx, 'category'] if 'category' in df.columns else ''
            
            for facet_id in facets:
                if facet_id not in self.facet_embeddings:
                    continue
                
                facet_embs = self.facet_embeddings[facet_id]
                facet_keys = self.facet_value_keys[facet_id]
                
                # Calculate similarity to all facet values
                similarities = self.embedding_interface.similarity(skill_emb, facet_embs)[0]
                
                # Get top-K candidates
                top_k = self.rerank_top_k
                top_indices = np.argsort(similarities)[-top_k:][::-1]
                top_similarities = similarities[top_indices]
                
                best_idx = top_indices[0]
                best_similarity = top_similarities[0]
                
                # Check if we need LLM re-ranking
                is_multi_value = facet_id in MULTI_VALUE_FACETS
                
                if self.use_llm_reranking and len(top_indices) > 1 and best_similarity < self.embedding_threshold:
                    # Collect for batch LLM re-ranking
                    candidates = []
                    for i, fval_idx in enumerate(top_indices):
                        if top_similarities[i] >= self.multi_value_threshold:
                            value_code = facet_keys[fval_idx]
                            facet_info = ALL_FACETS[facet_id]['values'][value_code]
                            candidates.append({
                                'code': value_code,
                                'name': facet_info.get('name', value_code),
                                'description': facet_info.get('description', ''),
                                'similarity': float(top_similarities[i])
                            })
                    
                    if len(candidates) > 1:
                        to_be_reranked[facet_id].append({
                            'idx': idx,
                            'skill_name': skill_name,
                            'skill_desc': str(skill_desc)[:300],
                            'skill_category': skill_category,
                            'candidates': candidates,
                            'is_multi_value': is_multi_value
                        })
                        continue
                
                # Direct assignment based on embedding
                if best_similarity >= self.embedding_threshold:
                    value_code = facet_keys[best_idx]
                    facet_info = ALL_FACETS[facet_id]['values'][value_code]
                    
                    if is_multi_value:
                        # Collect all values above threshold for multi-value facets
                        multi_values = []
                        for i, fval_idx in enumerate(top_indices[:self.max_multi_values]):
                            if top_similarities[i] >= self.multi_value_threshold:
                                multi_values.append(facet_keys[fval_idx])
                        df.loc[idx, f'facet_{facet_id}'] = json.dumps(multi_values)
                        df.loc[idx, f'facet_{facet_id}_name'] = ", ".join([
                            ALL_FACETS[facet_id]['values'][v]['name'] for v in multi_values
                        ])
                    else:
                        df.loc[idx, f'facet_{facet_id}'] = value_code
                        df.loc[idx, f'facet_{facet_id}_name'] = facet_info.get('name', value_code)
                    
                    df.loc[idx, f'facet_{facet_id}_confidence'] = float(best_similarity)
                    df.loc[idx, f'facet_{facet_id}_method'] = 'embedding'
                    self.assignment_stats[facet_id]['embedding'] += 1
                else:
                    # Below threshold - still assign best match but mark as low confidence
                    value_code = facet_keys[best_idx]
                    facet_info = ALL_FACETS[facet_id]['values'][value_code]
                    df.loc[idx, f'facet_{facet_id}'] = value_code
                    df.loc[idx, f'facet_{facet_id}_name'] = facet_info.get('name', value_code)
                    df.loc[idx, f'facet_{facet_id}_confidence'] = float(best_similarity)
                    df.loc[idx, f'facet_{facet_id}_method'] = 'embedding_low_conf'
                    self.assignment_stats[facet_id]['embedding_low_conf'] += 1
        
        # Process LLM re-ranking in batches for each facet
        for facet_id, items in to_be_reranked.items():
            if not items:
                continue
            
            logger.info(f"LLM re-ranking {len(items)} skills for facet {facet_id}...")
            
            # Process in batches
            for batch_start in range(0, len(items), self.batch_size):
                batch_end = min(batch_start + self.batch_size, len(items))
                batch_items = items[batch_start:batch_end]
                
                results = self._rerank_facet_batch(facet_id, batch_items)
                
                for item in batch_items:
                    idx = item['idx']
                    if idx in results:
                        value_code, confidence = results[idx]
                        facet_info = ALL_FACETS[facet_id]['values'].get(value_code, {})
                        
                        df.loc[idx, f'facet_{facet_id}'] = value_code
                        df.loc[idx, f'facet_{facet_id}_name'] = facet_info.get('name', value_code)
                        df.loc[idx, f'facet_{facet_id}_confidence'] = confidence
                        df.loc[idx, f'facet_{facet_id}_method'] = 'embedding+llm_rerank'
                        self.assignment_stats[facet_id]['embedding+llm_rerank'] += 1
                    else:
                        # Fallback to best embedding candidate
                        best_candidate = item['candidates'][0]
                        df.loc[idx, f'facet_{facet_id}'] = best_candidate['code']
                        df.loc[idx, f'facet_{facet_id}_name'] = best_candidate['name']
                        df.loc[idx, f'facet_{facet_id}_confidence'] = best_candidate['similarity']
                        df.loc[idx, f'facet_{facet_id}_method'] = 'embedding_fallback'
                        self.assignment_stats[facet_id]['embedding_fallback'] += 1
        
        return df
    
    def _get_facet_prompt(self, facet_id: str, item: Dict) -> Tuple[str, str]:
        """
        Generate system and user prompts for LLM re-ranking of a specific facet.
        
        Args:
            facet_id: The facet ID (NAT, TRF, COG, etc.)
            item: Dictionary with skill info and candidates
        """
        facet_info = ALL_FACETS[facet_id]
        facet_name = facet_info['facet_name']
        
        system_prompt = f"""You are an expert in vocational skills classification.
Your task is to select the BEST matching {facet_name} category for each skill.

{facet_info['description']}

Analyze the skill's name, description, and category, then select the most appropriate {facet_name} value.
Consider:
1. The skill's core functionality and purpose
2. How the skill is typically applied
3. The best match based on the category definitions

You MUST respond with valid JSON only. No additional text, explanation, or markdown."""

        candidates_text = "\n".join([
            f"{i+1}. {c['name']}: {c['description']}"
            for i, c in enumerate(item['candidates'])
        ])
        
        user_prompt = f"""Select the BEST {facet_name} category for this skill:

SKILL: {item['skill_name']}
DESCRIPTION: {item['skill_desc']}
ORIGINAL CATEGORY: {item['skill_category']}

CANDIDATE {facet_name.upper()} CATEGORIES:
{candidates_text}

Which category (1-{len(item['candidates'])}) is the BEST match? Think carefully and respond with JSON only:
{{"choice": <number>, "confidence": <0.0-1.0>}}

Respond with valid JSON only:"""

        return system_prompt, user_prompt
    
    def _rerank_facet_batch(self, facet_id: str, batch_items: List[Dict]) -> Dict[Any, Tuple[str, float]]:
        """Batch re-rank facet candidates using LLM with retry logic"""
        
        results = {}
        user_prompts = []
        system_prompt = None
        
        for item in batch_items:
            sys_prompt, user_prompt = self._get_facet_prompt(facet_id, item)
            if system_prompt is None:
                system_prompt = sys_prompt
            user_prompts.append(user_prompt)
        
        try:
            responses = self.genai_interface._generate_batch(
                user_prompts=user_prompts,
                system_prompt=system_prompt
            )
            
            for response, item in zip(responses, batch_items):
                idx = item['idx']
                retry_count = 5
                current_response = response
                
                while retry_count > 0:
                    try:
                        parsed = self.genai_interface._parse_json_response(current_response)
                        if parsed and isinstance(parsed, dict):
                            choice = parsed.get('choice', 1)
                            confidence = parsed.get('confidence', 0.7)
                            
                            if 1 <= choice <= len(item['candidates']):
                                selected = item['candidates'][choice - 1]
                                final_confidence = (confidence + selected['similarity']) / 2
                                results[idx] = (selected['code'], final_confidence)
                                break
                            else:
                                logger.debug(f"Invalid choice {choice} for facet {facet_id}, skill {idx}")
                                raise ValueError(f"Invalid choice: {choice}")
                        else:
                            logger.debug(f"Response not a dictionary for facet {facet_id}, skill {idx}")
                            raise ValueError("Response not a dictionary")
                            
                    except Exception as e:
                        retry_count -= 1
                        if retry_count > 0:
                            logger.debug(f"Retrying facet {facet_id} for skill {idx}, {retry_count} attempts left: {e}")
                            # Regenerate single response
                            try:
                                sys_prompt, user_prompt = self._get_facet_prompt(facet_id, item)
                                single_responses = self.genai_interface._generate_batch(
                                    user_prompts=[user_prompt],
                                    system_prompt=sys_prompt
                                )
                                current_response = single_responses[0]
                            except Exception as retry_e:
                                logger.debug(f"Retry generation failed: {retry_e}")
                                break
                        else:
                            logger.debug(f"All retries exhausted for facet {facet_id}, skill {idx}")
                            
        except Exception as e:
            logger.error(f"LLM batch re-ranking failed for facet {facet_id}: {e}")
        
        return results
    
    def _log_assignment_statistics(self, df: pd.DataFrame):
        """Log statistics about facet assignments"""
        logger.info("\n" + "=" * 60)
        logger.info("FACET ASSIGNMENT STATISTICS")
        logger.info("=" * 60)
        
        total_skills = len(df)
        
        for facet_id in self.facets_to_assign:
            col = f'facet_{facet_id}'
            if col not in df.columns:
                continue
            
            assigned = df[col].notna().sum()
            facet_name = ALL_FACETS.get(facet_id, {}).get('facet_name', facet_id)
            
            logger.info(f"\n{facet_name} ({facet_id}):")
            logger.info(f"  Assigned: {assigned} ({100*assigned/total_skills:.1f}%)")
            
            # Method breakdown
            method_col = f'facet_{facet_id}_method'
            if method_col in df.columns:
                methods = df[method_col].value_counts()
                for method, count in methods.items():
                    if method:
                        logger.info(f"    {method}: {count}")
            
            # Value distribution (top 5)
            value_dist = df[col].value_counts().head(5)
            logger.info(f"  Top values:")
            for value, count in value_dist.items():
                if value:
                    value_name = ALL_FACETS.get(facet_id, {}).get('values', {}).get(value, {}).get('name', value)
                    logger.info(f"    {value_name}: {count}")
    
    def get_faceted_skill_data(self, df: pd.DataFrame) -> List[Dict]:
        """
        Export skills with all facet data for visualization
        
        Returns list of skill dictionaries with facet values
        """
        skills = []
        
        for idx in df.index:
            skill = {
                'id': df.loc[idx, 'skill_id'] if 'skill_id' in df.columns else str(idx),
                'name': df.loc[idx, 'name'],
                'description': df.loc[idx, 'description'] if 'description' in df.columns else '',
                'code': df.loc[idx, 'code'] if 'code' in df.columns else '',
                'category': df.loc[idx, 'category'] if 'category' in df.columns else '',
                'level': int(df.loc[idx, 'level']) if 'level' in df.columns else None,
                'context': df.loc[idx, 'context'] if 'context' in df.columns else '',
                'confidence': float(df.loc[idx, 'confidence']) if 'confidence' in df.columns else None,
                'keywords': df.loc[idx, 'keywords'] if 'keywords' in df.columns else [],
                'alternative_titles': df.loc[idx, 'alternative_titles'] if 'alternative_titles' in df.columns else [],
                'all_related_codes': df.loc[idx, 'all_related_codes'] if 'all_related_codes' in df.columns else [],
                'all_related_kw': df.loc[idx, 'all_related_kw'] if 'all_related_kw' in df.columns else [],
                'facets': {}
            }
            
            # Add facet data
            for facet_id in self.facets_to_assign:
                col = f'facet_{facet_id}'
                if col in df.columns and pd.notna(df.loc[idx, col]):
                    value = df.loc[idx, col]
                    
                    # Handle multi-value facets (stored as JSON)
                    if facet_id in MULTI_VALUE_FACETS and isinstance(value, str) and value.startswith('['):
                        try:
                            value = json.loads(value)
                        except:
                            pass
                    
                    skill['facets'][facet_id] = {
                        'code': value,
                        'name': df.loc[idx, f'facet_{facet_id}_name'] if f'facet_{facet_id}_name' in df.columns else value,
                        'confidence': float(df.loc[idx, f'facet_{facet_id}_confidence']) if f'facet_{facet_id}_confidence' in df.columns else None
                    }
            
            skills.append(skill)
        
        return skills
