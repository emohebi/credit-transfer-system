"""
Family Assignment Module - Replaces Clustering
Assigns skills to predefined skill families using GenAI and embedding-based matching
"""
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from tqdm import tqdm
import json
import re

logger = logging.getLogger(__name__)


class SkillFamilyAssigner:
    """
    Assigns skills to predefined skill families using GenAI prompts
    Replaces HDBSCAN clustering with deterministic family assignment
    """
    
    def __init__(self, config: Dict, genai_interface=None, embedding_interface=None):
        """
        Initialize the family assigner
        
        Args:
            config: Configuration dictionary
            genai_interface: GenAI interface for LLM-based assignment
            embedding_interface: Embedding interface for similarity-based fallback
        """
        self.config = config
        self.genai_interface = genai_interface
        self.embedding_interface = embedding_interface
        
        # Load settings
        self.family_config = config.get('family_assignment', {})
        self.taxonomy_config = config.get('taxonomy', {})
        
        # Load family and domain definitions
        self.families = self.taxonomy_config.get('families', {})
        self.domains = self.taxonomy_config.get('domains', {})
        
        # Settings
        self.use_genai = self.family_config.get('use_genai', True) and genai_interface is not None
        self.batch_size = self.family_config.get('genai_batch_size', 50)
        self.fallback_to_keywords = self.family_config.get('fallback_to_keyword_matching', True)
        self.keyword_threshold = self.family_config.get('keyword_match_threshold', 2)
        self.use_embedding_similarity = self.family_config.get('use_embedding_similarity', True)
        self.embedding_threshold = self.family_config.get('embedding_similarity_threshold', 0.35)
        
        # LLM re-ranking settings (Solution 1: Top-K + LLM Re-ranking)
        self.use_llm_reranking = self.family_config.get('use_llm_reranking', False) and genai_interface is not None
        self.rerank_top_k = self.family_config.get('rerank_top_k', 5)
        self.rerank_similarity_threshold = self.family_config.get('rerank_similarity_threshold', 0.5)
        
        # Precompute family embeddings for similarity matching
        self.family_embeddings = None
        self.family_keys = None
        self.family_names = {k: v.get('name', k) for k, v in self.families.items()}
        self.domain_names = {k: v.get('name', k) for k, v in self.domains.items()}
        
        # Statistics
        self.assignment_stats = defaultdict(int)
        
        logger.info(f"Initialized SkillFamilyAssigner")
        logger.info(f"  Families: {len(self.families)}")
        logger.info(f"  Domains: {len(self.domains)}")
        logger.info(f"  Use GenAI: {self.use_genai}")
        logger.info(f"  Fallback to keywords: {self.fallback_to_keywords}")
    
    def _precompute_family_embeddings(self):
        """Precompute embeddings for all families for similarity matching"""
        if self.embedding_interface is None:
            logger.warning("No embedding interface provided, skipping family embedding precomputation")
            return
        
        logger.info("Precomputing family embeddings...")
        
        family_texts = []
        self.family_keys = []
        
        for family_key, family_info in self.families.items():
            # Create rich text representation of family
            text_parts = [
                family_info.get('name', ''),
                family_info.get('description', '')
            ]
            # keywords = family_info.get('keywords', [])
            # if keywords:
            #     text_parts.append(' '.join(keywords[:20]))
            
            family_text = '. '.join([p for p in text_parts if p]) #+ f". Domain: {self.domains.get(family_info.get('domain', ''), {}).get('name', '')}"
            family_texts.append(family_text)
            self.family_keys.append(family_key)
        
        if family_texts:
            self.family_embeddings = self.embedding_interface.encode(
                family_texts,
                batch_size=32,
                show_progress=True
            )
            logger.info(f"  Computed embeddings for {len(self.family_keys)} families")
    
    def assign_families(self, df: pd.DataFrame, embeddings: Optional[np.ndarray] = None) -> pd.DataFrame:
        """
        Assign skills to families
        
        Args:
            df: DataFrame with skills data (must have 'name' and 'description' columns)
            embeddings: Optional precomputed skill embeddings
            
        Returns:
            DataFrame with 'assigned_family', 'assigned_domain', and 'cluster_id' columns
        """
        logger.info("=" * 80)
        logger.info("ASSIGNING SKILLS TO FAMILIES")
        logger.info("=" * 80)
        logger.info(f"Processing {len(df)} skills")
        
        df_result = df.copy()
        
        # Initialize assignment columns
        df_result['assigned_family'] = None
        df_result['assigned_domain'] = None
        df_result['cluster_id'] = -1  # For compatibility with existing code
        df_result['family_assignment_method'] = None
        df_result['family_assignment_confidence'] = 0.0
        
        # Precompute family embeddings if using similarity
        if self.use_embedding_similarity and self.embedding_interface is not None:
            self._precompute_family_embeddings()
        
        # Store skill embeddings for similarity matching
        self.skill_embeddings = embeddings
        
        # Method 1: Try GenAI-based assignment first
        if self.use_genai:
            df_result = self._assign_with_genai(df_result)
        
        # Method 2: Use embedding similarity for unassigned skills
        unassigned_mask = df_result['assigned_family'].isna()
        if unassigned_mask.any() and self.use_embedding_similarity and self.family_embeddings is not None:
            logger.info(f"Using embedding similarity for {unassigned_mask.sum()} unassigned skills")
            df_result = self._assign_with_embeddings_batch(df_result, unassigned_mask)
        
        # Method 3: Keyword matching fallback
        # unassigned_mask = df_result['assigned_family'].isna()
        # if unassigned_mask.any() and self.fallback_to_keywords:
        #     logger.info(f"Using keyword matching for {unassigned_mask.sum()} remaining unassigned skills")
        #     df_result = self._assign_with_keywords(df_result, unassigned_mask)
        
        # Assign domains based on families
        df_result = self._assign_domains(df_result)
        
        # Create cluster_id from family for compatibility (each family = one cluster)
        df_result = self._create_cluster_ids(df_result)
        
        # Log statistics
        self._log_assignment_statistics(df_result)
        
        return df_result
    
    def _assign_with_genai(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign skills to families using GenAI"""
        logger.info("Assigning skills using GenAI...")
        
        # Create family summary for prompt
        family_summary = self._create_family_summary()
        
        # Process in batches
        unassigned_indices = df[df['assigned_family'].isna()].index.tolist()
        
        for batch_start in tqdm(range(0, len(unassigned_indices), self.batch_size), 
                                desc="GenAI family assignment"):
            batch_end = min(batch_start + self.batch_size, len(unassigned_indices))
            batch_indices = unassigned_indices[batch_start:batch_end]
            
            # Prepare batch of skills
            skills_batch = []
            for idx in batch_indices:
                skill_name = df.loc[idx, 'name']
                skill_desc = df.loc[idx, 'description'] if 'description' in df.columns else ''
                skills_batch.append({
                    'index': idx,
                    'name': skill_name,
                    'description': str(skill_desc)[:200]  # Truncate description
                })
            
            # Call GenAI for assignment
            try:
                assignments = self._call_genai_for_assignment(skills_batch, family_summary)
                
                # Apply assignments
                for assignment in assignments:
                    idx = assignment.get('index')
                    family_key = assignment.get('family_key')
                    confidence = assignment.get('confidence', 0.7)
                    
                    if idx is not None and family_key in self.families:
                        df.loc[idx, 'assigned_family'] = family_key
                        df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                        df.loc[idx, 'family_assignment_method'] = 'genai'
                        df.loc[idx, 'family_assignment_confidence'] = confidence
                        self.assignment_stats['genai'] += 1
                        
            except Exception as e:
                logger.warning(f"GenAI assignment failed for batch: {e}")
                continue
        
        return df
    
    def _call_genai_for_assignment(self, skills_batch: List[Dict], family_summary: str) -> List[Dict]:
        """Call GenAI to assign skills to families"""
        
        system_prompt = """You are an expert in vocational education and training (VET) skill classification.
Your task is to assign skills to the most appropriate skill family from the provided list.

For each skill, analyze its name and description, then select the SINGLE most appropriate skill family.
Consider the following when making assignments:
1. Match the skill's domain and technical area to the family's focus
2. Look for keyword matches between the skill and family keywords
3. Consider the training package alignment
4. If uncertain, choose the closest match based on the skill's primary function

You MUST respond with valid JSON only. No other text."""

        # Format skills for prompt
        skills_text = "\n".join([
            f"{i+1}. Skill: {s['name']}\n   Description: {s['description']}"
            for i, s in enumerate(skills_batch)
        ])
        
        user_prompt = f"""Assign each of the following skills to the most appropriate skill family.

SKILL FAMILIES:
{family_summary}

SKILLS TO ASSIGN:
{skills_text}

Respond with a JSON array where each element has:
- "skill_number": the skill number (1-based)
- "family_key": the family key (e.g., "software_development", "nursing_clinical")
- "confidence": confidence score from 0.0 to 1.0

Example response:
[
  {{"skill_number": 1, "family_key": "software_development", "confidence": 0.85}},
  {{"skill_number": 2, "family_key": "nursing_clinical", "confidence": 0.92}}
]

Respond with JSON only:"""

        try:
            # Use generate_json for structured output
            try:
                parsed = self.genai_interface.generate_json(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=2000,
                    temperature=0.1
                )
                # If generate_json returns a list directly
                if isinstance(parsed, list):
                    assignments = []
                    for item in parsed:
                        skill_num = item.get('skill_number', 0)
                        family_key = item.get('family_key', '')
                        confidence = item.get('confidence', 0.7)
                        
                        if 1 <= skill_num <= len(skills_batch):
                            original_idx = skills_batch[skill_num - 1]['index']
                            assignments.append({
                                'index': original_idx,
                                'family_key': family_key,
                                'confidence': confidence
                            })
                    return assignments
                else:
                    # Response might be wrapped in an object
                    items = parsed.get('assignments', parsed.get('skills', []))
                    if isinstance(items, list):
                        assignments = []
                        for item in items:
                            skill_num = item.get('skill_number', 0)
                            family_key = item.get('family_key', '')
                            confidence = item.get('confidence', 0.7)
                            
                            if 1 <= skill_num <= len(skills_batch):
                                original_idx = skills_batch[skill_num - 1]['index']
                                assignments.append({
                                    'index': original_idx,
                                    'family_key': family_key,
                                    'confidence': confidence
                                })
                        return assignments
                        
            except (ValueError, AttributeError) as e:
                # Fallback to text generation and parsing
                logger.debug(f"generate_json failed, falling back to text generation: {e}")
                response = self.genai_interface.generate(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=2000,
                    temperature=0.1
                )
                assignments = self._parse_genai_response(response, skills_batch)
                return assignments
            
        except Exception as e:
            logger.warning(f"GenAI call failed: {e}")
            return []
    
    def _parse_genai_response(self, response: str, skills_batch: List[Dict]) -> List[Dict]:
        """Parse GenAI response and map back to skill indices"""
        assignments = []
        
        try:
            # Extract JSON from response
            json_match = re.search(r'\[[\s\S]*\]', response)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                for item in parsed:
                    skill_num = item.get('skill_number', 0)
                    family_key = item.get('family_key', '')
                    confidence = item.get('confidence', 0.7)
                    
                    # Map skill number back to original index
                    if 1 <= skill_num <= len(skills_batch):
                        original_idx = skills_batch[skill_num - 1]['index']
                        assignments.append({
                            'index': original_idx,
                            'family_key': family_key,
                            'confidence': confidence
                        })
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse GenAI JSON response: {e}")
        except Exception as e:
            logger.warning(f"Error parsing GenAI response: {e}")
        
        return assignments
    
    def _create_family_summary(self) -> str:
        """Create a concise summary of families for the prompt"""
        lines = []
        
        # Group families by domain
        domain_families = defaultdict(list)
        for family_key, family_info in self.families.items():
            domain = family_info.get('domain', 'other')
            domain_families[domain].append((family_key, family_info))
        
        for domain_key, families in domain_families.items():
            domain_name = self.domains.get(domain_key, {}).get('name', domain_key)
            lines.append(f"\n[{domain_name}]")
            
            for family_key, family_info in families:
                family_name = family_info.get('name', family_key)
                keywords = family_info.get('keywords', [])[:5]  # First 5 keywords
                keywords_str = ', '.join(keywords) if keywords else ''
                lines.append(f"  - {family_key}: {family_name}")
                if keywords_str:
                    lines.append(f"    Keywords: {keywords_str}")
        
        return '\n'.join(lines)
    
    def _assign_with_embeddings(self, df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """Assign skills using embedding similarity"""
        if self.skill_embeddings is None or self.family_embeddings is None:
            return df
        
        indices = df[mask].index.tolist()
        to_be_reranked = []
        for idx in tqdm(indices, desc="Embedding similarity assignment"):
            # Get skill embedding
            position = df.index.get_loc(idx)
            skill_emb = self.skill_embeddings[position].reshape(1, -1)
            
            # Calculate similarity to all families
            similarities = self.embedding_interface.similarity(skill_emb, self.family_embeddings)[0]

            # Get top-K candidates
            top_k = self.rerank_top_k if self.use_llm_reranking else 1
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            top_similarities = similarities[top_indices]
            
            # Default: use best embedding match
            best_idx = top_indices[0]
            best_similarity = top_similarities[0]
            
            # If LLM re-ranking is enabled and we have multiple candidates above threshold
            if self.use_llm_reranking and len(top_indices) > 1 and top_similarities[0] >= self.rerank_similarity_threshold and best_similarity < self.embedding_threshold:
                # Get skill info
                skill_name = df.loc[idx, 'name']
                skill_desc = df.loc[idx, 'description'] if 'description' in df.columns else ''
                
                # Get top-K family candidates
                candidates = []
                for i, fam_idx in enumerate(top_indices):
                    if top_similarities[i] >= self.rerank_similarity_threshold:
                        family_key = self.family_keys[fam_idx]
                        candidates.append({
                            'key': family_key,
                            'name': self.families[family_key].get('name', family_key),
                            'description': self.families[family_key].get('description', ''),
                            'similarity': float(top_similarities[i])
                        })
                
                # Re-rank with LLM if we have multiple candidates
                if len(candidates) > 1:
                    best_family, confidence = self._rerank_with_llm(skill_name, skill_desc, candidates)
                    if best_family and confidence >= self.rerank_similarity_threshold:
                        df.loc[idx, 'assigned_family'] = best_family
                        df.loc[idx, 'assigned_family_name'] = self.family_names[best_family]
                        df.loc[idx, 'family_assignment_method'] = 'embedding+llm_rerank'
                        df.loc[idx, 'family_assignment_confidence'] = confidence
                        self.assignment_stats['embedding+llm_rerank'] += 1
                    else:
                        # Fallback to best embedding match
                        family_key = self.family_keys[best_idx]
                        df.loc[idx, 'assigned_family'] = None
                        df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                        df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                        df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                        self.assignment_stats['Not assigned'] += 1
                else:
                        # Fallback to best embedding match
                        family_key = self.family_keys[best_idx]
                        df.loc[idx, 'assigned_family'] = None
                        df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                        df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                        df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                        self.assignment_stats['Not assigned'] += 1
            
            elif best_similarity >= self.embedding_threshold:
                family_key = self.family_keys[best_idx]
                df.loc[idx, 'assigned_family'] = family_key
                df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                df.loc[idx, 'family_assignment_method'] = 'embedding'
                df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                self.assignment_stats['embedding'] += 1
            else:
                family_key = self.family_keys[best_idx]
                df.loc[idx, 'assigned_family'] = None
                df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                self.assignment_stats['Not assigned'] += 1
        
        return df
    
    def _assign_with_embeddings_batch(self, df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """Assign skills using embedding similarity"""
        if self.skill_embeddings is None or self.family_embeddings is None:
            return df
        
        indices = df[mask].index.tolist()
        to_be_reranked = []
        for idx in tqdm(indices, desc="Embedding similarity assignment"):
            # Get skill embedding
            position = df.index.get_loc(idx)
            skill_emb = self.skill_embeddings[position].reshape(1, -1)
            
            # Calculate similarity to all families
            similarities = self.embedding_interface.similarity(skill_emb, self.family_embeddings)[0]

            # Get top-K candidates
            top_k = self.rerank_top_k if self.use_llm_reranking else 1
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            top_similarities = similarities[top_indices]
            
            # Default: use best embedding match
            best_idx = top_indices[0]
            best_similarity = top_similarities[0]
            
            # If LLM re-ranking is enabled and we have multiple candidates above threshold
            if self.use_llm_reranking and len(top_indices) > 1 and top_similarities[0] >= self.rerank_similarity_threshold and best_similarity < self.embedding_threshold:
                # Get skill info
                skill_name = df.loc[idx, 'name']
                skill_desc = df.loc[idx, 'description'] if 'description' in df.columns else ''
                
                # Get top-K family candidates
                candidates = []
                for i, fam_idx in enumerate(top_indices):
                    if top_similarities[i] >= self.rerank_similarity_threshold:
                        family_key = self.family_keys[fam_idx]
                        candidates.append({
                            'key': family_key,
                            'name': self.families[family_key].get('name', family_key),
                            'description': self.families[family_key].get('description', ''),
                            'similarity': float(top_similarities[i])
                        })
                
                # Re-rank with LLM if we have multiple candidates
                if len(candidates) > 1:
                    to_be_reranked.append((idx, skill_name, skill_desc, candidates))
                else:
                    # Fallback to best embedding match
                    family_key = self.family_keys[best_idx]
                    df.loc[idx, 'assigned_family'] = None
                    df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                    df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                    df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                    self.assignment_stats['Not assigned'] += 1
            
            elif best_similarity >= self.embedding_threshold:
                family_key = self.family_keys[best_idx]
                df.loc[idx, 'assigned_family'] = family_key
                df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                df.loc[idx, 'family_assignment_method'] = 'embedding'
                df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                self.assignment_stats['embedding'] += 1
            else:
                family_key = self.family_keys[best_idx]
                df.loc[idx, 'assigned_family'] = None
                df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                self.assignment_stats['Not assigned'] += 1
        
        if to_be_reranked:
            logger.info(f"Re-ranking {len(to_be_reranked)} skills with LLM...")
            rerank_results = self._rerank_with_llm_batch(to_be_reranked)
            for (idx, _, _, _), (best_family, confidence) in zip(to_be_reranked, rerank_results):
                if best_family and confidence >= self.rerank_similarity_threshold:
                    df.loc[idx, 'assigned_family'] = best_family
                    df.loc[idx, 'assigned_family_name'] = self.family_names[best_family]
                    df.loc[idx, 'family_assignment_method'] = 'embedding+llm_rerank'
                    df.loc[idx, 'family_assignment_confidence'] = confidence
                    self.assignment_stats['embedding+llm_rerank'] += 1
                else:
                    # Fallback to best embedding match
                    position = df.index.get_loc(idx)
                    skill_emb = self.skill_embeddings[position].reshape(1, -1)
                    similarities = self.embedding_interface.similarity(skill_emb, self.family_embeddings)[0]
                    best_idx = np.argmax(similarities)
                    best_similarity = similarities[best_idx]
                    
                    family_key = self.family_keys[best_idx]
                    df.loc[idx, 'assigned_family'] = None
                    df.loc[idx, 'assigned_family_name'] = self.family_names[family_key]
                    df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                    df.loc[idx, 'family_assignment_confidence'] = float(best_similarity)
                    self.assignment_stats['Not assigned'] += 1
        return df
    
    
    def _rerank_with_llm_batch(self, to_be_reranked: List[Tuple[Any, str, str, List[Dict]]]) -> List[Tuple[Optional[str], float]]:
        """Batch re-rank skills with LLM"""
        user_prompts = []
        system_prompt = None
        results = []
        for idx, skill_name, skill_desc, candidates in to_be_reranked:
            system_prompt, user_prompt = self.get_prompt(skill_name, skill_desc, candidates)
            user_prompts.append(user_prompt)
        loop = True
        counter = 5
        while loop:
            loop = False
            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=user_prompts,
                    system_prompt=system_prompt
                )
                
                for response, (idx, skill_name, skill_desc, candidates) in zip(responses, to_be_reranked):
                    response = self.genai_interface._parse_json_response(response)
                    if response and isinstance(response, dict):
                        choice = response['choice']
                        confidence = response['confidence']
                        
                        selected = candidates[choice - 1]
                        final_confidence = (confidence + selected['similarity']) / 2
                        results.append((selected['key'], final_confidence))
                    else:
                        logger.info(f"Response in LLM re-ranking is not a dictionary")
                        logger.info(f"Response: {response}")
                        
                        if counter >= 0:
                            counter -= 1
                            loop = True
                        logger.info(f"Trying {counter} more time ..")
            except Exception as e:
                logger.error(f"LLM batch re-ranking failed: {e}")
                logger.info(f"Response: {response}")
                if counter >= 0:
                    counter -= 1
                    loop = True
                logger.info(f"Trying {counter} more time ..")
                pass
        
        return results
    
    def get_prompt(self, skill_name: str, skill_desc: str, candidates: List[Dict]) -> Tuple[str, str]:
        """
        Generate system and user prompts for LLM re-ranking.
        
        Args:
            skill_name: Name of the skill
            skill_desc: Description of the skill
            candidates: List of candidate families with keys, names, descriptions, and similarities
            """
        system_prompt = """You are an expert in vocational skills classification. Your task is to select the BEST matching skill family for a given skill from a list of candidates.

        Analyze the skill's name and description, then select the single most appropriate family based on:
        1. Domain alignment (e.g., IT skills should match IT families, not finance)
        2. Technical terminology match
        3. Job function alignment

        Respond with JSON only: {"choice": <number>, "confidence": <0.0-1.0>}
        \n\n
        You must respond with valid JSON only. No additional text, explanation, or markdown."""

        # Format candidates
        candidates_text = "\n".join([
            f"{i+1}. {c['name']}: {c['description']}"
            for i, c in enumerate(candidates)
        ])
        
        user_prompt = f"""Select the BEST skill family match for this skill:

        SKILL: {skill_name}
        DESCRIPTION: {skill_desc}

        CANDIDATE FAMILIES:
        {candidates_text}

        Which family (1-{len(candidates)}) is the BEST match? Respond with JSON only: \n\nRespond with valid JSON only:"""
        
        return system_prompt, user_prompt
        
    
    def _rerank_with_llm(self, skill_name: str, skill_desc: str, candidates: List[Dict]) -> Tuple[Optional[str], float]:
        """
        Use LLM to re-rank top-K embedding candidates and select the best match.
        
        Args:
            skill_name: Name of the skill
            skill_desc: Description of the skill
            candidates: List of candidate families with keys, names, descriptions, and similarities
            
        Returns:
            Tuple of (best_family_key, confidence_score) or (None, 0.0) if re-ranking fails
        """
        if not self.genai_interface or not candidates:
            return None, 0.0
        
        system_prompt, user_prompt = self.get_prompt(skill_name, skill_desc, candidates)
        loop = True
        counter = 5
        while loop:
            loop = False
            try:
                response = self.genai_interface.generate_json(
                    prompt=user_prompt,
                    system_prompt=system_prompt,
                    max_tokens=1000,
                    temperature=0.1
                )
                
                if response and isinstance(response, dict):
                    choice = response['choice']
                    confidence = response['confidence']
                    
                    # if 1 <= choice <= len(candidates):
                    selected = candidates[choice - 1]
                    #     # Blend LLM confidence with embedding similarity
                    final_confidence = (confidence + selected['similarity']) / 2
                    return selected['key'], final_confidence
                else:
                    logger.info(f"Response in LLM re-ranking is not a dictionary")
                    logger.info(f"Response: {response}")
                    
                    if counter >= 0:
                        counter -= 1
                        loop = True
                    logger.info(f"Trying {counter} more time ..")
                        
            except Exception as e:
                logger.error(f"LLM re-ranking failed for '{skill_name}': {e}")
                logger.info(f"Response: {response}")
                if counter >= 0:
                    counter -= 1
                    loop = True
                logger.info(f"Trying {counter} more time ..")
                pass
        
        return None, 0.0
    
    def _assign_with_keywords(self, df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """Assign skills using keyword matching"""
        indices = df[mask].index.tolist()
        
        for idx in indices:
            skill_text = str(df.loc[idx, 'name']).lower()
            if 'description' in df.columns:
                skill_text += ' ' + str(df.loc[idx, 'description']).lower()
            
            best_family = None
            best_score = 0
            
            for family_key, family_info in self.families.items():
                keywords = family_info.get('keywords', [])
                score = sum(1 for kw in keywords if kw.lower() in skill_text)
                
                # Also check family name
                family_name = family_info.get('name', '').lower()
                if any(word in skill_text for word in family_name.split()):
                    score += 2
                
                if score > best_score:
                    best_score = score
                    best_family = family_key
            
            if best_family and best_score >= self.keyword_threshold:
                df.loc[idx, 'assigned_family'] = best_family
                df.loc[idx, 'assigned_family_name'] = self.family_names[best_family]
                df.loc[idx, 'family_assignment_method'] = 'keyword'
                df.loc[idx, 'family_assignment_confidence'] = min(0.9, 0.4 + best_score * 0.1)
                self.assignment_stats['keyword'] += 1
            else:
                # Assign to most generic family in the category if we have category info
                if 'category' in df.columns:
                    category = str(df.loc[idx, 'category']).lower()
                    default_family = self._get_default_family_for_category(category)
                    if default_family:
                        df.loc[idx, 'assigned_family'] = None
                        df.loc[idx, 'assigned_family_name'] = None
                        df.loc[idx, 'family_assignment_method'] = 'Not assigned'
                        df.loc[idx, 'family_assignment_confidence'] = 0.0
                        self.assignment_stats['Not assigned'] += 1
        
        return df
    
    def _get_default_family_for_category(self, category: str) -> Optional[str]:
        """Get a default family for a skill category"""
        category_family_map = {
            'technical': 'engineering_mechanical',
            'cognitive': 'business_administration',
            'interpersonal': 'customer_service',
            'domain_knowledge': 'business_administration',
        }
        return category_family_map.get(category)
    
    def _assign_domains(self, df: pd.DataFrame) -> pd.DataFrame:
        """Assign domains based on family assignments"""
        for idx in df.index:
            family_key = df.loc[idx, 'assigned_family']
            if family_key and family_key in self.families:
                domain_key = self.families[family_key].get('domain')
                df.loc[idx, 'assigned_domain'] = domain_key
                df.loc[idx, 'assigned_domain_name'] = self.domain_names.get(domain_key, domain_key)
        
        return df
    
    def _create_cluster_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create cluster IDs from family assignments for compatibility"""
        # Create a mapping from family to cluster ID
        family_to_cluster = {}
        cluster_id = 0
        
        for family_key in self.families.keys():
            family_to_cluster[family_key] = cluster_id
            cluster_id += 1
        
        # Assign cluster IDs
        for idx in df.index:
            family_key = df.loc[idx, 'assigned_family']
            if family_key in family_to_cluster:
                df.loc[idx, 'cluster_id'] = family_to_cluster[family_key]
            else:
                df.loc[idx, 'cluster_id'] = -1  # Unassigned
        
        return df
    
    def _log_assignment_statistics(self, df: pd.DataFrame):
        """Log statistics about family assignments"""
        logger.info("\n" + "=" * 60)
        logger.info("FAMILY ASSIGNMENT STATISTICS")
        logger.info("=" * 60)
        
        total_skills = len(df)
        assigned = df['assigned_family'].notna().sum()
        unassigned = total_skills - assigned
        
        logger.info(f"Total skills: {total_skills}")
        logger.info(f"Assigned: {assigned} ({100*assigned/total_skills:.1f}%)")
        logger.info(f"Unassigned: {unassigned} ({100*unassigned/total_skills:.1f}%)")
        
        logger.info("\nAssignment methods:")
        for method, count in self.assignment_stats.items():
            logger.info(f"  {method}: {count}")
        
        logger.info("\nFamily distribution (top 20):")
        family_dist = df['assigned_family'].value_counts().head(20)
        for family, count in family_dist.items():
            family_name = self.families.get(family, {}).get('name', family)
            logger.info(f"  {family_name}: {count} skills")
        
        logger.info("\nDomain distribution:")
        domain_dist = df['assigned_domain'].value_counts()
        for domain, count in domain_dist.items():
            domain_name = self.domains.get(domain, {}).get('name', domain) if domain else 'Unassigned'
            logger.info(f"  {domain_name}: {count} skills ({100*count/total_skills:.1f}%)")
    
    def get_family_representatives(self, df: pd.DataFrame, embeddings: np.ndarray, 
                                   n_representatives: int = 5) -> Dict[str, List[Dict]]:
        """Get representative skills for each family"""
        representatives = {}
        
        for family_key in self.families.keys():
            family_mask = df['assigned_family'] == family_key
            family_df = df[family_mask]
            
            if len(family_df) == 0:
                continue
            
            # Get family indices
            family_indices = family_df.index.tolist()
            
            if len(family_indices) <= n_representatives:
                # Return all skills if fewer than n_representatives
                reps = family_df.head(n_representatives)
            else:
                # Get skills closest to family centroid
                family_positions = [df.index.get_loc(idx) for idx in family_indices]
                family_embeddings = embeddings[family_positions]
                centroid = np.mean(family_embeddings, axis=0)
                
                # Calculate distances to centroid
                distances = np.linalg.norm(family_embeddings - centroid, axis=1)
                closest_indices = np.argsort(distances)[:n_representatives]
                
                rep_positions = [family_indices[i] for i in closest_indices]
                reps = df.loc[rep_positions]
            
            representatives[family_key] = reps.to_dict('records')
        
        return representatives


# Alias for backwards compatibility
MultiFactorClusterer = SkillFamilyAssigner
