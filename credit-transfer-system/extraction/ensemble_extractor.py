"""
Ensemble skill extractor that runs multiple extractions and takes consensus
"""

import logging
from typing import List, Dict, Any, Union
from collections import defaultdict
import numpy as np

from models.base_models import Skill
from models.enums import SkillLevel, SkillContext, SkillCategory

logger = logging.getLogger(__name__)


class EnsembleSkillExtractor:
    """Extract skills using ensemble method for consistency"""
    
    def __init__(self, base_extractor, num_runs: int = 3, embeddings=None, similarity_threshold: float = 0.9):
        """
        Initialize ensemble extractor
        
        Args:
            base_extractor: Base skill extractor to use
            num_runs: Number of extraction runs to perform
            embeddings: Embedding interface for similarity calculation
            similarity_threshold: Threshold for considering skills as same (default 0.9)
        """
        self.base_extractor = base_extractor
        self.num_runs = num_runs
        self.embeddings = embeddings
        self.similarity_threshold = similarity_threshold
        
        # Store skill embeddings to avoid re-computing
        self.skill_embeddings_cache = {}
    
    def _get_skill_embedding(self, skill_name: str):
        """Get embedding for a skill name, using cache"""
        if skill_name not in self.skill_embeddings_cache:
            if self.embeddings:
                # Get embedding - ensure it returns a 1D array
                embeddings = self.embeddings.encode([skill_name])
                # embeddings should be shape (1, embedding_dim), we want just the vector
                if embeddings.ndim == 2:
                    embedding = embeddings[0]  # Get the first (and only) row
                else:
                    embedding = embeddings
                self.skill_embeddings_cache[skill_name] = embedding
            else:
                # Fallback if no embeddings available
                return None
        return self.skill_embeddings_cache[skill_name]
    
    def _find_similar_skill_group(self, skill_name: str, skill_groups: Dict[str, Dict]) -> str:
        """
        Find if a skill belongs to an existing group based on embedding similarity
        
        Args:
            skill_name: Name of the skill to check
            skill_groups: Dictionary of existing skill groups
            
        Returns:
            Key of the matching group, or None if no match found
        """
        if not self.embeddings:
            # Fallback to exact matching if no embeddings
            skill_key = skill_name.lower().strip()
            return skill_key if skill_key in skill_groups else None
        
        # Get embedding for current skill
        skill_embedding = self._get_skill_embedding(skill_name)
        if skill_embedding is None:
            return None
        
        # Check similarity with existing groups
        for group_key, group_info in skill_groups.items():
            # Get representative embedding for the group
            representative_embedding = group_info.get('embedding')
            if representative_embedding is not None:
                # Both embeddings should be 1D arrays at this point
                # Reshape them for similarity calculation
                skill_emb_2d = skill_embedding.reshape(1, -1)
                rep_emb_2d = representative_embedding.reshape(1, -1)
                
                # Calculate cosine similarity
                similarity = self.embeddings.similarity(skill_emb_2d, rep_emb_2d)[0, 0]
                
                if similarity >= self.similarity_threshold:
                    logger.debug(f"Skill '{skill_name}' matched to group '{group_key}' with similarity {similarity:.3f}")
                    return group_key
        
        return None
    
    def extract_with_consensus(self, item, item_type: str = "auto") -> Union[List[Skill], Dict[str, List[Skill]]]:
        """
        Extract skills multiple times and take consensus using embedding similarity
        """
        all_runs = []
        is_dict_result = False
        
        # Perform multiple extraction runs
        for run in range(self.num_runs):
            logger.info(f"Ensemble extraction run {run + 1}/{self.num_runs}")
            
            # Extract skills
            result = self.base_extractor.extract_skills(item, item_type)
            
            # Check if result is a dictionary (multiple items) or list (single item)
            if isinstance(result, dict):
                is_dict_result = True
                all_runs.append(result)
            else:
                # Single item result - should be a list of Skill objects
                all_runs.append(result)
        
        # Clear embedding cache after extraction
        self.skill_embeddings_cache = {}
        
        # Process based on result type
        if is_dict_result:
            # Handle dictionary results (multiple items)
            return self._process_dict_consensus(all_runs)
        else:
            # Handle list results (single item)
            return self._process_list_consensus(all_runs)
    
    def _process_list_consensus(self, all_runs: List[List[Skill]]) -> List[Skill]:
        """Process consensus for list of skills using embedding similarity"""
        
        # Dictionary to store skill groups
        # Each group has: representative_name, embedding, skills, frequency
        skill_groups = {}
        
        # Process each run
        for run_idx, skills_list in enumerate(all_runs):
            for skill in skills_list:
                if not isinstance(skill, Skill):
                    continue
                
                skill_name = skill.name.strip()
                
                # Find if this skill belongs to an existing group
                matching_group_key = self._find_similar_skill_group(skill_name, skill_groups)
                
                if matching_group_key:
                    # Add to existing group
                    skill_groups[matching_group_key]['skills'].append(skill)
                    skill_groups[matching_group_key]['frequency'] += 1
                    skill_groups[matching_group_key]['run_appearances'].add(run_idx)
                    
                    # Update representative if this skill has higher confidence
                    if skill.confidence > skill_groups[matching_group_key]['best_skill'].confidence:
                        skill_groups[matching_group_key]['best_skill'] = skill
                else:
                    # Create new group
                    group_key = skill_name.lower().strip()
                    skill_groups[group_key] = {
                        'representative_name': skill_name,
                        'embedding': self._get_skill_embedding(skill_name) if self.embeddings else None,
                        'skills': [skill],
                        'frequency': 1,
                        'best_skill': skill,
                        'run_appearances': {run_idx}
                    }
        
        # Build consensus skill set
        consensus_skills = []
        threshold = self.num_runs / 2  # Skill group must appear in majority of runs
        
        for group_key, group_info in skill_groups.items():
            # Check if skill appeared in enough runs
            appearances = len(group_info['run_appearances'])
            
            if appearances >= threshold:
                # Use the best skill from the group
                best_skill = group_info['best_skill']
                
                # Adjust confidence based on consensus
                consensus_confidence = appearances / self.num_runs
                best_skill.confidence = min(1.0, best_skill.confidence * consensus_confidence)
                
                consensus_skills.append(best_skill)
                
                logger.debug(f"Skill group '{group_info['representative_name']}' included with {appearances}/{self.num_runs} appearances")
        
        logger.info(f"Consensus extraction: {len(consensus_skills)} skills from {len(skill_groups)} unique groups")
        
        # Sort by confidence and name for consistency
        consensus_skills.sort(key=lambda s: (-s.confidence, s.name.lower()))
        
        return consensus_skills
    
    def _process_dict_consensus(self, all_runs: List[Dict[str, List[Skill]]]) -> Dict[str, List[Skill]]:
        """Process consensus for dictionary of skills using embedding similarity"""
        
        consensus_results = {}
        
        # Get all item codes
        all_codes = set()
        for run_result in all_runs:
            all_codes.update(run_result.keys())
        
        # Process each item code separately
        for code in all_codes:
            # Dictionary to store skill groups for this code
            skill_groups = {}
            
            # Collect skills for this code across all runs
            for run_idx, run_result in enumerate(all_runs):
                if code in run_result:
                    skills_list = run_result[code]
                    
                    for skill in skills_list:
                        if not isinstance(skill, Skill):
                            continue
                        
                        skill_name = skill.name.strip()
                        
                        # Find if this skill belongs to an existing group
                        matching_group_key = self._find_similar_skill_group(skill_name, skill_groups)
                        
                        if matching_group_key:
                            # Add to existing group
                            skill_groups[matching_group_key]['skills'].append(skill)
                            skill_groups[matching_group_key]['frequency'] += 1
                            skill_groups[matching_group_key]['run_appearances'].add(run_idx)
                            
                            # Update representative if this skill has higher confidence
                            if skill.confidence > skill_groups[matching_group_key]['best_skill'].confidence:
                                skill_groups[matching_group_key]['best_skill'] = skill
                        else:
                            # Create new group
                            group_key = skill_name.lower().strip()
                            skill_groups[group_key] = {
                                'representative_name': skill_name,
                                'embedding': self._get_skill_embedding(skill_name) if self.embeddings else None,
                                'skills': [skill],
                                'frequency': 1,
                                'best_skill': skill,
                                'run_appearances': {run_idx}
                            }
            
            # Build consensus for this item
            consensus_skills = []
            threshold = self.num_runs / 2
            
            for group_key, group_info in skill_groups.items():
                appearances = len(group_info['run_appearances'])
                
                if appearances >= threshold:
                    # Use the best skill from the group
                    best_skill = group_info['best_skill']
                    
                    # Adjust confidence based on consensus
                    consensus_confidence = appearances / self.num_runs
                    best_skill.confidence = min(1.0, best_skill.confidence * consensus_confidence)
                    
                    consensus_skills.append(best_skill)
            
            # Sort for consistency
            consensus_skills.sort(key=lambda s: (-s.confidence, s.name.lower()))
            
            consensus_results[code] = consensus_skills
            
            logger.info(f"Consensus for {code}: {len(consensus_skills)} skills from {len(skill_groups)} groups")
        
        return consensus_results
    
    def extract_skills(self, items: Union[List, Any], item_type: str = "auto") -> Union[List[Skill], Dict[str, List[Skill]]]:
        """
        Wrapper method to match the base extractor interface
        """
        return self.extract_with_consensus(items, item_type)