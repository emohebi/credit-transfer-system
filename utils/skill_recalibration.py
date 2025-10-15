"""
Skill Recalibration Tool
Re-categorizes and/or re-levels existing cached skills without re-extraction
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import argparse
from tqdm import tqdm
import numpy as np

from models.base_models import (
    VETQualification, UniQualification, 
    UnitOfCompetency, UniCourse, Skill
)
from models.enums import SkillLevel, SkillCategory, SkillContext, StudyLevel
from extraction.unified_extractor import UnifiedSkillExtractor
from reporting.skill_export import SkillExportManager
from interfaces.model_factory import ModelFactory
from config_profiles import ConfigProfiles
from utils.prompt_manager import PromptManager

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class SkillRecalibrationTool:
    """Tool for recalibrating cached skills with updated category/level definitions"""
    
    def __init__(self, genai=None, config=None):
        """
        Initialize recalibration tool
        
        Args:
            genai: GenAI interface for AI-based recalibration
            config: Configuration dictionary
        """
        self.genai = genai
        self.config = config or {}
        self.prompt_manager = PromptManager()
        self.skill_export = SkillExportManager(output_dir="output/skills")
        
        # Detect backend type
        self.backend_type = self._detect_backend_type()
        
        # Track changes for reporting
        self.changes_made = {
            'category_changes': 0,
            'level_changes': 0,
            'total_skills_processed': 0,
            'units_processed': 0,
            'courses_processed': 0
        }
        
        logger.info(f"Initialized SkillRecalibrationTool with backend: {self.backend_type}")
    
    def _detect_backend_type(self) -> str:
        """Detect the backend type from genai interface"""
        if not self.genai:
            return "none"
        
        class_name = self.genai.__class__.__name__
        
        if "OpenAI" in class_name or hasattr(self.genai, 'client'):
            return "openai"
        elif "VLLM" in class_name or hasattr(self.genai, 'llm'):
            return "vllm"
        else:
            return "unknown"
    
    def recalibrate_vet_skills(self, 
                              filepath: str,
                              recalibrate_categories: bool = True,
                              recalibrate_levels: bool = True,
                              batch_size: int = 50,
                              backup: bool = True) -> str:
        """
        Recalibrate VET qualification skills from cached file
        
        Args:
            filepath: Path to cached VET skills JSON file
            recalibrate_categories: Whether to update categories
            recalibrate_levels: Whether to update levels
            batch_size: Number of skills to process in each AI batch
            backup: Whether to create backup before overwriting
            
        Returns:
            Path to updated file
        """
        logger.info(f"Loading VET skills from {filepath}")
        
        # Create backup if requested
        if backup:
            backup_path = self._create_backup(filepath)
            logger.info(f"Created backup at {backup_path}")
        
        # Load the qualification
        vet_qual = self.skill_export.import_vet_skills(filepath)
        
        # Process each unit
        for unit in tqdm(vet_qual.units, desc="Processing VET units"):
            if unit.extracted_skills:
                logger.info(f"Recalibrating {len(unit.extracted_skills)} skills for unit {unit.code}")
                
                # Recalibrate skills
                recalibrated_skills = self._recalibrate_skills(
                    skills=unit.extracted_skills,
                    context_text=unit.get_full_text(),
                    item_type="VET Unit",
                    item_code=unit.code,
                    study_level=None,  # VET doesn't have explicit study levels
                    recalibrate_categories=recalibrate_categories,
                    recalibrate_levels=recalibrate_levels,
                    batch_size=batch_size
                )
                
                # Update the skills
                unit.extracted_skills = recalibrated_skills
                self.changes_made['units_processed'] += 1
        
        # Save the updated qualification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(filepath).parent / f"{vet_qual.code}_skills_recalibrated_{timestamp}.json"
        
        # Export using the skill export manager's method
        self._export_vet_with_metadata(vet_qual, output_path)
        
        # Print summary
        self._print_summary()
        
        logger.info(f"Recalibrated VET skills saved to {output_path}")
        return str(output_path)
    
    def recalibrate_uni_skills(self, 
                              filepath: str,
                              recalibrate_categories: bool = True,
                              recalibrate_levels: bool = True,
                              batch_size: int = 50,
                              backup: bool = True) -> str:
        """
        Recalibrate University qualification skills from cached file
        
        Args:
            filepath: Path to cached University skills JSON file
            recalibrate_categories: Whether to update categories
            recalibrate_levels: Whether to update levels
            batch_size: Number of skills to process in each AI batch
            backup: Whether to create backup before overwriting
            
        Returns:
            Path to updated file
        """
        logger.info(f"Loading University skills from {filepath}")
        
        # Create backup if requested
        if backup:
            backup_path = self._create_backup(filepath)
            logger.info(f"Created backup at {backup_path}")
        
        # Load the qualification
        uni_qual = self.skill_export.import_uni_skills(filepath)
        
        # Process each course
        for course in tqdm(uni_qual.courses, desc="Processing University courses"):
            if course.extracted_skills:
                logger.info(f"Recalibrating {len(course.extracted_skills)} skills for course {course.code}")
                
                # Recalibrate skills
                recalibrated_skills = self._recalibrate_skills(
                    skills=course.extracted_skills,
                    context_text=course.get_full_text(),
                    item_type="University Course",
                    item_code=course.code,
                    study_level=course.study_level,
                    recalibrate_categories=recalibrate_categories,
                    recalibrate_levels=recalibrate_levels,
                    batch_size=batch_size
                )
                
                # Update the skills
                course.extracted_skills = recalibrated_skills
                self.changes_made['courses_processed'] += 1
        
        # Save the updated qualification
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(filepath).parent / f"{uni_qual.code}_skills_recalibrated_{timestamp}.json"
        
        # Export using the skill export manager's method
        self._export_uni_with_metadata(uni_qual, output_path)
        
        # Print summary
        self._print_summary()
        
        logger.info(f"Recalibrated University skills saved to {output_path}")
        return str(output_path)
    
    def _recalibrate_skills(self,
                           skills: List[Skill],
                           context_text: str,
                           item_type: str,
                           item_code: str,
                           study_level: Optional[str],
                           recalibrate_categories: bool,
                           recalibrate_levels: bool,
                           batch_size: int) -> List[Skill]:
        """
        Recalibrate a list of skills
        
        Args:
            skills: List of skills to recalibrate
            context_text: Original text for context
            item_type: Type of item (VET/University)
            item_code: Code of the unit/course
            study_level: Study level if known
            recalibrate_categories: Whether to update categories
            recalibrate_levels: Whether to update levels
            batch_size: Batch size for AI processing
            
        Returns:
            List of recalibrated skills
        """
        if not self.genai:
            logger.warning("No GenAI interface available, returning skills unchanged")
            return skills
        
        self.changes_made['total_skills_processed'] += len(skills)
        
        # Store original values for comparison
        original_values = {
            skill.name: {
                'category': skill.category,
                'level': skill.level
            }
            for skill in skills
        }
        
        # Process in batches
        for i in range(0, len(skills), batch_size):
            batch = skills[i:i + batch_size]
            
            # Recalibrate categories if requested
            if recalibrate_categories:
                logger.debug(f"Recalibrating categories for batch {i//batch_size + 1}")
                self._recalibrate_categories_batch(batch, context_text, item_type)
            
            # Recalibrate levels if requested
            if recalibrate_levels:
                logger.debug(f"Recalibrating levels for batch {i//batch_size + 1}")
                self._recalibrate_levels_batch(batch, context_text, item_type, study_level)
        
        # Count changes
        for skill in skills:
            original = original_values[skill.name]
            if skill.category != original['category']:
                self.changes_made['category_changes'] += 1
                logger.debug(f"Category changed for '{skill.name}': "
                           f"{original['category'].value} → {skill.category.value}")
            
            if skill.level != original['level']:
                self.changes_made['level_changes'] += 1
                logger.debug(f"Level changed for '{skill.name}': "
                           f"{original['level'].value} → {skill.level.value}")
        
        return skills
    
    def _recalibrate_categories_batch(self, 
                                     skills: List[Skill],
                                     context_text: str,
                                     item_type: str):
        """Recalibrate categories for a batch of skills"""
        
        # Get recategorization prompt
        
        
        # Get AI response
        if self.backend_type == "openai":
            system_prompt, user_prompt = self.prompt_manager.get_skill_recategorization_prompt(
                skills=skills,
                context_text=context_text,
                item_type=item_type,
                backend_type=self.backend_type
            )
            response = self.genai.generate_response(system_prompt, user_prompt, temperature=0.0)
        else:
            user_prompts = []
            for skill in skills:
                system_prompt, user_prompt = self.prompt_manager.get_skill_keywords_prompt(
                    skills_with_evidence=[skill],
                    context_text=context_text,
                    item_type=item_type,
                    backend_type=self.backend_type
                )
                user_prompts.append(user_prompt)
            response = self.genai._generate_batch(system_prompt, user_prompts)
        
        # Parse response
        category_assignments = self._parse_category_response(response)
        
        # Update skills
        for skill in skills:
            if skill.name in category_assignments:
                new_category = category_assignments[skill.name]
                # Add metadata about recalibration
                if 'recalibration_history' not in skill.metadata:
                    skill.metadata['recalibration_history'] = []
                
                skill.metadata['recalibration_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'category',
                    'old_value': skill.category.value,
                    'new_value': new_category
                })
                skill.category = self._map_category(new_category)
    
    def _recalibrate_levels_batch(self, 
                                 skills: List[Skill],
                                 context_text: str,
                                 item_type: str,
                                 study_level: Optional[str]):
        """Recalibrate levels for a batch of skills using ensemble if configured"""
        
        # if self.config.get("ensemble_level_recalibration", True):
        # Use ensemble approach for consistency
        num_runs = self.config.get("level_recalibration_runs", 3)
        level_votes = {skill.name: [] for skill in skills}
        
        for run in range(num_runs):
            # Get level determination prompt
            system_prompt, user_prompt = self.prompt_manager.get_sfia_level_determination_prompt(
                skills=skills,
                context_text=context_text,
                item_type=item_type,
                study_level=study_level,
                backend_type=self.backend_type
            )
            
            # Add slight variation for ensemble
            if self.backend_type == "openai":
                temperature = 0.0
                response = self.genai.generate_response(
                    system_prompt, user_prompt, 
                    temperature=temperature, top_p=1.0
                )
            else:
                user_prompts = []
                for skill in skills:
                    system_prompt, user_prompt = self.prompt_manager.get_sfia_level_determination_prompt(
                        skills=[skill],
                        context_text=context_text,
                        item_type=item_type,
                        study_level=study_level,
                        backend_type=self.backend_type
                    )
                    user_prompts.append(user_prompt)
                response = self.genai._generate_batch(system_prompt, user_prompts)
            
            # Parse response
            level_assignments = self._parse_level_response(response)
            
            # Store votes
            for skill_name, level in level_assignments.items():
                if skill_name in level_votes:
                    level_votes[skill_name].append(level)
        
        # Calculate consensus
        for skill in skills:
            if skill.name in level_votes and level_votes[skill.name]:
                from collections import Counter
                votes = level_votes[skill.name]
                level_counts = Counter(votes)
                consensus_level = level_counts.most_common(1)[0][0]
                
                # Update skill level
                old_level = skill.level
                skill.level = SkillLevel(consensus_level)
                
                # Add metadata
                if 'recalibration_history' not in skill.metadata:
                    skill.metadata['recalibration_history'] = []
                
                skill.metadata['recalibration_history'].append({
                    'timestamp': datetime.now().isoformat(),
                    'type': 'level',
                    'old_value': old_level.value,
                    'new_value': consensus_level,
                    'votes': votes,
                        'consensus_confidence': level_counts[consensus_level] / len(votes)
                    })
        # else:
        #     # Single run approach
        #     system_prompt, user_prompt = self.prompt_manager.get_sfia_level_determination_prompt(
        #         skills=skills,
        #         context_text=context_text,
        #         item_type=item_type,
        #         study_level=study_level,
        #         backend_type=self.backend_type
        #     )
            
        #     response = self.genai.generate_response(system_prompt, user_prompt)
        #     level_assignments = self._parse_level_response(response)
            
        #     # Update skills
        #     for skill in skills:
        #         if skill.name in level_assignments:
        #             old_level = skill.level
        #             skill.level = SkillLevel(level_assignments[skill.name])
                    
        #             # Add metadata
        #             if 'recalibration_history' not in skill.metadata:
        #                 skill.metadata['recalibration_history'] = []
                    
        #             skill.metadata['recalibration_history'].append({
        #                 'timestamp': datetime.now().isoformat(),
        #                 'type': 'level',
        #                 'old_value': old_level.value,
        #                 'new_value': level_assignments[skill.name]
        #             })
    
    def _parse_category_response(self, response: Any) -> Dict[str, str]:
        """Parse category recalibration response"""
        if isinstance(response, list):
            # Batch responses
            category_assignments = {}
            for resp in response:
                parsed = self._parse_single_category_response(resp)
                category_assignments.update(parsed)
            return category_assignments
        elif isinstance(response, str):
            # Single response
            return self._parse_single_category_response(response)
        else:
            logger.error("Unexpected response format for category recalibration")
            return {}
    
    def _parse_single_category_response(self, response: str) -> Dict[str, str]:
        """Parse category recalibration response"""
        import re
        
        category_assignments = {}
        
        try:
            # Try JSON parsing
            if isinstance(response, str):
                clean_response = response.strip()
                if clean_response.startswith('```json'):
                    clean_response = clean_response[7:]
                if clean_response.startswith('```'):
                    clean_response = clean_response[3:]
                if clean_response.endswith('```'):
                    clean_response = clean_response[:-3]
                
                # Find JSON array
                json_match = re.search(r'(?:assistantfinal.*?)?(\[\s*\{[^}]*\}\s*(?:\s*,\s*\{[^}]*\}\s*)*\])', 
                                     clean_response, re.DOTALL)
                
                if json_match:
                    data = json.loads(json_match.group(1))
                    
                    for item in data:
                        skill_name = item.get('skill_name', '')
                        category = item.get('category', '')
                        if skill_name and category:
                            category_assignments[skill_name] = category
        
        except Exception as e:
            logger.error(f"Failed to parse category response: {e}")
        
        return category_assignments
    
    def _parse_level_response(self, response: str) -> Dict[str, int]:
        """Parse level recalibration response"""
        # Reuse the parsing logic from unified_extractor
        extractor = UnifiedSkillExtractor(self.genai, self.config)
        return extractor._parse_level_assignment_response(response)
    
    def _map_category(self, category_str: str) -> SkillCategory:
        """Map string to SkillCategory enum"""
        extractor = UnifiedSkillExtractor(self.genai, self.config)
        return extractor._map_category(category_str)
    
    def _create_backup(self, filepath: str) -> str:
        """Create backup of the file before modification"""
        import shutil
        
        backup_path = Path(filepath).with_suffix('.backup.json')
        shutil.copy2(filepath, backup_path)
        return str(backup_path)
    
    def _export_vet_with_metadata(self, vet_qual: VETQualification, filepath: Path):
        """Export VET qualification with all metadata"""
        # Use the skill export manager's internal method
        self.skill_export._export_vet_to_json(vet_qual, filepath, include_metadata=True)
    
    def _export_uni_with_metadata(self, uni_qual: UniQualification, filepath: Path):
        """Export University qualification with all metadata"""
        # Use the skill export manager's internal method
        self.skill_export._export_uni_to_json(uni_qual, filepath, include_metadata=True)
    
    def _print_summary(self):
        """Print summary of changes made"""
        print("\n" + "=" * 60)
        print("RECALIBRATION SUMMARY")
        print("=" * 60)
        print(f"Total skills processed: {self.changes_made['total_skills_processed']}")
        print(f"Units processed: {self.changes_made['units_processed']}")
        print(f"Courses processed: {self.changes_made['courses_processed']}")
        print(f"Category changes: {self.changes_made['category_changes']}")
        print(f"Level changes: {self.changes_made['level_changes']}")
        
        if self.changes_made['total_skills_processed'] > 0:
            category_change_rate = (self.changes_made['category_changes'] / 
                                   self.changes_made['total_skills_processed'] * 100)
            level_change_rate = (self.changes_made['level_changes'] / 
                               self.changes_made['total_skills_processed'] * 100)
            print(f"Category change rate: {category_change_rate:.1f}%")
            print(f"Level change rate: {level_change_rate:.1f}%")
        print("=" * 60)


def main():
    """Command-line interface for skill recalibration"""
    parser = argparse.ArgumentParser(
        description="Recalibrate categories and/or levels for cached skills"
    )
    
    parser.add_argument(
        "filepath",
        help="Path to cached skills JSON file"
    )
    
    parser.add_argument(
        "--type",
        choices=["vet", "uni"],
        required=True,
        help="Type of qualification (vet or uni)"
    )
    
    parser.add_argument(
        "--categories",
        action="store_true",
        help="Recalibrate skill categories"
    )
    
    parser.add_argument(
        "--levels",
        action="store_true",
        help="Recalibrate skill levels"
    )
    
    parser.add_argument(
        "--both",
        action="store_true",
        help="Recalibrate both categories and levels"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for AI processing (default: 50)"
    )
    
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Don't create backup before modifying"
    )
    
    parser.add_argument(
        "--profile",
        choices=["fast", "balanced", "thorough", "robust"],
        default="balanced",
        help="Configuration profile (default: balanced)"
    )
    
    parser.add_argument(
        "--backend",
        choices=["openai", "vllm", "auto"],
        default="auto",
        help="AI backend to use"
    )
    
    args = parser.parse_args()
    
    # Determine what to recalibrate
    if args.both:
        recalibrate_categories = True
        recalibrate_levels = True
    else:
        recalibrate_categories = args.categories
        recalibrate_levels = args.levels
    
    if not recalibrate_categories and not recalibrate_levels:
        print("Error: Must specify --categories, --levels, or --both")
        return
    
    # Create configuration
    config = ConfigProfiles.create_config(
        profile_name=args.profile,
        backend=args.backend
    )
    
    # Add recalibration-specific config
    config_dict = config.to_dict()
    config_dict.update({
        'ensemble_level_recalibration': True,
        'level_recalibration_runs': 3
    })
    
    # Initialize GenAI interface
    genai = ModelFactory.create_genai_interface(config)
    
    if not genai:
        print("Error: Could not initialize AI backend")
        return
    
    # Create recalibration tool
    tool = SkillRecalibrationTool(genai=genai, config=config_dict)
    
    # Run recalibration
    try:
        if args.type == "vet":
            output_path = tool.recalibrate_vet_skills(
                filepath=args.filepath,
                recalibrate_categories=recalibrate_categories,
                recalibrate_levels=recalibrate_levels,
                batch_size=args.batch_size,
                backup=not args.no_backup
            )
        else:
            output_path = tool.recalibrate_uni_skills(
                filepath=args.filepath,
                recalibrate_categories=recalibrate_categories,
                recalibrate_levels=recalibrate_levels,
                batch_size=args.batch_size,
                backup=not args.no_backup
            )
        
        print(f"\nRecalibration complete!")
        print(f"Output saved to: {output_path}")
        
    except Exception as e:
        print(f"Error during recalibration: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()