"""
LLM Integration module for skill taxonomy pipeline
Uses Azure OpenAI models for intelligent naming, validation, and refinement
Modified to support Azure OpenAI instead of standard OpenAI
"""
import openai
from openai import AzureOpenAI  # Changed from OpenAI to AzureOpenAI
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
import logging
import json
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import hashlib
import pickle
import os

logger = logging.getLogger(__name__)


class LLMTaxonomyRefiner:
    """Uses LLM for taxonomy naming, validation, and refinement"""
    
    def __init__(self, config: Dict):
        self.config = config
        
        # Azure OpenAI specific configuration
        self.api_key = config['llm'].get('api_key') or os.environ.get('AZURE_OPENAI_API_KEY')
        self.azure_endpoint = config['llm'].get('azure_endpoint') or os.environ.get('AZURE_OPENAI_ENDPOINT')
        self.api_version = config['llm'].get('api_version', '2024-02-01')  # Default API version
        self.deployment_name = config['llm'].get('deployment_name') or config['llm'].get('model', 'gpt-4')
        
        # Model parameters (same as before)
        self.temperature = config['llm']['temperature']
        self.max_tokens = config['llm']['max_tokens']
        self.batch_size = config['llm']['batch_size']
        
        # Initialize Azure OpenAI client
        if self.api_key and self.azure_endpoint:
            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version=self.api_version,
                azure_endpoint=self.azure_endpoint
            )
        else:
            logger.warning("Azure OpenAI credentials not found. LLM features will be disabled.")
            self.client = None
        
        # Cache for LLM responses
        self.cache_dir = Path(config['paths']['cache_dir']) / "llm_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.response_cache = {}
        
    def generate_cluster_names(self, 
                              cluster_representatives: Dict,
                              cluster_stats: Dict) -> Dict[int, str]:
        """
        Generate meaningful names for clusters using LLM
        
        Args:
            cluster_representatives: Representative skills for each cluster
            cluster_stats: Statistics for each cluster
            
        Returns:
            Dictionary mapping cluster_id to cluster name
        """
        if not self.client:
            logger.warning("Azure OpenAI client not initialized. Using default names.")
            return {cid: f"Cluster {cid}" for cid in cluster_representatives.keys()}
            
        logger.info(f"Generating names for {len(cluster_representatives)} clusters")
        
        cluster_names = {}
        batches = self._create_batches(list(cluster_representatives.keys()), self.batch_size)
        
        for batch in tqdm(batches, desc="Generating cluster names"):
            batch_prompts = []
            
            for cluster_id in batch:
                representatives = cluster_representatives[cluster_id]
                stats = cluster_stats.get(cluster_id, {})
                
                prompt = self._create_cluster_naming_prompt(representatives, stats)
                batch_prompts.append((cluster_id, prompt))
            
            # Process batch
            for cluster_id, prompt in batch_prompts:
                try:
                    name = self._call_llm(prompt, system_prompt=self._get_naming_system_prompt())
                    cluster_names[cluster_id] = name.strip().replace('"', '')
                except Exception as e:
                    logger.error(f"Error generating name for cluster {cluster_id}: {e}")
                    cluster_names[cluster_id] = f"Cluster_{cluster_id}"
            
            # Rate limiting
            time.sleep(0.5)
        
        return cluster_names
    
    def validate_taxonomy_structure(self, taxonomy: Dict) -> Tuple[bool, List[str]]:
        """
        Validate taxonomy structure using LLM
        
        Args:
            taxonomy: Taxonomy structure to validate
            
        Returns:
            Tuple of (is_valid, issues)
        """
        if not self.client:
            logger.warning("Azure OpenAI client not initialized. Skipping validation.")
            return True, []
            
        prompt = self._create_validation_prompt(taxonomy)
        system_prompt = self._get_validation_system_prompt()
        
        try:
            response = self._call_llm(prompt, system_prompt=system_prompt)
            result = json.loads(response)
            
            is_valid = result.get('is_valid', False)
            issues = result.get('issues', [])
            
            return is_valid, issues
            
        except Exception as e:
            logger.error(f"Error validating taxonomy: {e}")
            return False, [str(e)]
    
    def refine_skill_categorization(self, 
                                   df: pd.DataFrame, 
                                   sample_size: int = 100) -> pd.DataFrame:
        """
        Refine skill categorization using LLM
        
        Args:
            df: Dataframe with skills
            sample_size: Number of skills to sample for refinement
            
        Returns:
            Dataframe with refined categories
        """
        if not self.client:
            logger.warning("Azure OpenAI client not initialized. Skipping categorization refinement.")
            return df
            
        logger.info("Refining skill categorization with LLM")
        
        # Sample skills for refinement
        sample_df = df.sample(min(sample_size, len(df)))
        refined_categories = {}
        
        batches = self._create_dataframe_batches(sample_df, batch_size=10)
        
        for batch_df in tqdm(batches, desc="Refining categories"):
            skills_data = batch_df[['name', 'description', 'category', 'keywords']].to_dict('records')
            
            prompt = self._create_categorization_prompt(skills_data)
            system_prompt = self._get_categorization_system_prompt()
            
            try:
                response = self._call_llm(prompt, system_prompt=system_prompt)
                result = json.loads(response)
                
                for skill_result in result.get('skills', []):
                    skill_name = skill_result.get('name')
                    new_category = skill_result.get('suggested_category')
                    confidence = skill_result.get('confidence', 0.5)
                    
                    if confidence > 0.7:  # Only apply high-confidence changes
                        refined_categories[skill_name] = new_category
                        
            except Exception as e:
                logger.error(f"Error refining categories: {e}")
        
        # Apply refinements
        df_refined = df.copy()
        for skill_name, new_category in refined_categories.items():
            mask = df_refined['name'] == skill_name
            df_refined.loc[mask, 'category'] = new_category
            df_refined.loc[mask, 'llm_refined'] = True
        
        return df_refined
    
    def suggest_hierarchy_improvements(self, 
                                      hierarchy: Dict,
                                      cluster_info: Dict) -> List[Dict]:
        """
        Suggest improvements to the taxonomy hierarchy
        
        Args:
            hierarchy: Current hierarchy structure
            cluster_info: Information about clusters
            
        Returns:
            List of improvement suggestions
        """
        if not self.client:
            logger.warning("Azure OpenAI client not initialized. No improvements suggested.")
            return []
            
        prompt = self._create_improvement_prompt(hierarchy, cluster_info)
        system_prompt = self._get_improvement_system_prompt()
        
        try:
            response = self._call_llm(prompt, system_prompt=system_prompt)
            suggestions = json.loads(response)
            
            return suggestions.get('improvements', [])
            
        except Exception as e:
            logger.error(f"Error getting improvement suggestions: {e}")
            return []
    
    def generate_skill_relationships(self, 
                                    skills: List[Dict],
                                    relationship_types: List[str] = None) -> List[Dict]:
        """
        Generate relationships between skills using LLM
        
        Args:
            skills: List of skill dictionaries
            relationship_types: Types of relationships to identify
            
        Returns:
            List of relationships
        """
        if not self.client:
            logger.warning("Azure OpenAI client not initialized. No relationships generated.")
            return []
            
        if relationship_types is None:
            relationship_types = ['prerequisite', 'complementary', 'similar', 'advanced']
        
        relationships = []
        batches = self._create_batches(skills, batch_size=20)
        
        for batch in tqdm(batches, desc="Generating relationships"):
            prompt = self._create_relationship_prompt(batch, relationship_types)
            system_prompt = self._get_relationship_system_prompt()
            
            try:
                response = self._call_llm(prompt, system_prompt=system_prompt)
                result = json.loads(response)
                
                relationships.extend(result.get('relationships', []))
                
            except Exception as e:
                logger.error(f"Error generating relationships: {e}")
        
        return relationships
    
    def _create_cluster_naming_prompt(self, representatives: List[Dict], stats: Dict) -> str:
        """Create prompt for cluster naming"""
        prompt = f"""
        Generate a concise, descriptive name for a skill cluster based on these representative skills:
        
        Representative Skills:
        {json.dumps(representatives[:5], indent=2)}
        
        Cluster Statistics:
        - Size: {stats.get('size', 'unknown')}
        - Top Keywords: {', '.join(stats.get('top_keywords', [])[:10])}
        - Primary Level: {max(stats.get('level_distribution', {'unknown': 1}), key=stats.get('level_distribution', {}).get)}
        - Primary Context: {max(stats.get('context_distribution', {'unknown': 1}), key=stats.get('context_distribution', {}).get)}
        
        Requirements:
        1. Name should be 2-5 words
        2. Should capture the essence of the skill group
        3. Should be specific but not too narrow
        4. Use professional terminology
        5. Avoid generic terms like "General Skills"
        
        Return only the cluster name, nothing else.
        """
        return prompt
    
    def _create_validation_prompt(self, taxonomy: Dict) -> str:
        """Create prompt for taxonomy validation"""
        prompt = f"""
        Validate the following skill taxonomy structure and identify any issues:
        
        Taxonomy Structure:
        {json.dumps(taxonomy, indent=2)}
        
        Check for:
        1. Logical hierarchy and organization
        2. Appropriate grouping of skills
        3. Consistency in naming conventions
        4. Balance in tree structure
        5. Clear differentiation between categories
        6. Missing or misplaced skill groups
        
        Return a JSON object with:
        {{
            "is_valid": boolean,
            "issues": ["list of specific issues found"],
            "severity": "low|medium|high",
            "recommendations": ["list of specific recommendations"]
        }}
        """
        return prompt
    
    def _create_categorization_prompt(self, skills: List[Dict]) -> str:
        """Create prompt for skill categorization"""
        prompt = f"""
        Review and refine the categorization of these skills:
        
        Skills:
        {json.dumps(skills, indent=2)}
        
        Categories available:
        - technical: Technical and hands-on skills
        - cognitive: Thinking and mental processing skills
        - interpersonal: People and communication skills
        - domain knowledge: Specific subject matter expertise
        
        For each skill, suggest the most appropriate category and provide confidence (0-1).
        
        Return a JSON object:
        {{
            "skills": [
                {{
                    "name": "skill name",
                    "current_category": "current",
                    "suggested_category": "suggested",
                    "confidence": 0.95,
                    "reasoning": "brief explanation"
                }}
            ]
        }}
        """
        return prompt
    
    def _create_improvement_prompt(self, hierarchy: Dict, cluster_info: Dict) -> str:
        """Create prompt for hierarchy improvements"""
        prompt = f"""
        Analyze this skill taxonomy hierarchy and suggest improvements:
        
        Current Hierarchy:
        {json.dumps(hierarchy, indent=2)}
        
        Cluster Information:
        {json.dumps(cluster_info, indent=2)}
        
        Suggest improvements for:
        1. Better organization of skill groups
        2. Missing intermediate levels
        3. Skills that should be moved
        4. Groups that should be split or merged
        5. Better naming for categories
        
        Return a JSON object:
        {{
            "improvements": [
                {{
                    "type": "reorganize|split|merge|rename|move",
                    "target": "identifier of target node",
                    "action": "specific action to take",
                    "rationale": "explanation",
                    "priority": "low|medium|high"
                }}
            ]
        }}
        """
        return prompt
    
    def _create_relationship_prompt(self, skills: List[Dict], relationship_types: List[str]) -> str:
        """Create prompt for relationship generation"""
        prompt = f"""
        Identify relationships between these skills:
        
        Skills:
        {json.dumps(skills, indent=2)}
        
        Relationship types to identify:
        {json.dumps(relationship_types, indent=2)}
        
        For each relationship:
        - prerequisite: Skill A is required before learning Skill B
        - complementary: Skills work well together
        - similar: Skills are variants or closely related
        - advanced: Skill B is an advanced version of Skill A
        
        Return a JSON object:
        {{
            "relationships": [
                {{
                    "source": "skill name 1",
                    "target": "skill name 2",
                    "type": "relationship type",
                    "strength": 0.9,
                    "bidirectional": false
                }}
            ]
        }}
        """
        return prompt
    
    def _get_naming_system_prompt(self) -> str:
        """System prompt for naming tasks"""
        return """You are an expert in skill taxonomy and competency frameworks. 
        Your task is to generate clear, professional, and meaningful names for skill clusters.
        Focus on industry-standard terminology and avoid overly generic or specific names."""
    
    def _get_validation_system_prompt(self) -> str:
        """System prompt for validation tasks"""
        return """You are a taxonomy validation expert with deep knowledge of skill frameworks like ESCO, O*NET, and SFIA.
        Analyze taxonomies for structural integrity, logical organization, and usability.
        Provide actionable feedback and specific recommendations."""
    
    def _get_categorization_system_prompt(self) -> str:
        """System prompt for categorization tasks"""
        return """You are an expert in skill classification and competency modeling.
        Accurately categorize skills based on their core nature and primary application.
        Consider the context and keywords when making categorization decisions."""
    
    def _get_improvement_system_prompt(self) -> str:
        """System prompt for improvement suggestions"""
        return """You are a taxonomy design expert specializing in skill hierarchies.
        Analyze existing structures and suggest practical improvements for better organization and usability.
        Focus on creating balanced, intuitive, and comprehensive skill taxonomies."""
    
    def _get_relationship_system_prompt(self) -> str:
        """System prompt for relationship identification"""
        return """You are an expert in skill analysis and competency relationships.
        Identify meaningful relationships between skills based on their descriptions and contexts.
        Focus on relationships that provide value for skill development and career planning."""
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make a call to the Azure OpenAI LLM with caching"""
        if not self.client:
            raise ValueError("Azure OpenAI client not initialized")
            
        # Create cache key
        cache_key = hashlib.md5(f"{system_prompt}_{prompt}".encode()).hexdigest()
        
        # Check cache
        if cache_key in self.response_cache:
            return self.response_cache[cache_key]
        
        cache_file = self.cache_dir / f"{cache_key}.txt"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                response = f.read()
                self.response_cache[cache_key] = response
                return response
        
        # Make API call
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Azure OpenAI API call using deployment name
            completion = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name for Azure
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            response = completion.choices[0].message.content
            
            # Cache response
            self.response_cache[cache_key] = response
            with open(cache_file, 'w') as f:
                f.write(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Azure OpenAI API error: {e}")
            raise
    
    def _create_batches(self, items: List, batch_size: int) -> List[List]:
        """Create batches from a list"""
        return [items[i:i + batch_size] for i in range(0, len(items), batch_size)]
    
    def _create_dataframe_batches(self, df: pd.DataFrame, batch_size: int) -> List[pd.DataFrame]:
        """Create batches from a dataframe"""
        return [df.iloc[i:i + batch_size] for i in range(0, len(df), batch_size)]