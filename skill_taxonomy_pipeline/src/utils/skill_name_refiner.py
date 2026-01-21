"""
Skill Name Refinement Tool

This module refines skill names based on their descriptions to create more
accurate, context-aware skill names that better represent the actual capability.

Example:
    Original: "Behaviour Analysis"
    Description: "Observes dogs' posture, facial cues, body language, stress signals, and energy to assess behavior."
    Refined: "Canine Body Language Reading"

Uses vLLM batch processing with one prompt per skill for efficient large-scale refinement.
"""

import logging
import json
import re
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from tqdm import tqdm
from datetime import datetime

logger = logging.getLogger(__name__)


# System prompt used for all refinement requests
REFINEMENT_SYSTEM_PROMPT = """You are an expert skill taxonomist specializing in vocational education and training (VET).
Your task is to refine a skill name to make it clearer and more specific based on what the skill actually refers to in context.

## Your Expertise:
- Deep knowledge of Australian VET sector terminology and Training Packages
- Understanding of industry-specific jargon and professional terminology
- Expertise in creating clear, searchable, standardized skill names
- Knowledge of ESCO, O*NET, SFIA, and other skills frameworks

## CRITICAL: Using Unit Title for CLARITY (Not Domain Prefixing)

The VET Unit Title helps you understand WHAT the skill actually refers to. Use it to clarify the skill name, NOT to add industry prefixes.

### The Goal:
- Understand what vague terms like "equipment", "procedures", "communication" actually mean in this specific context
- Create a skill name that clearly describes what the person is actually doing
- Make the skill name self-explanatory without needing the unit context

### Examples of GOOD vs BAD refinements:

| Original Skill | Unit Title | BAD (Domain Prefix) | GOOD (Clarified Meaning) |
|----------------|------------|---------------------|--------------------------|
| Equipment Cleaning Procedure | Carry out food preparation and service on an aircraft | Aircraft Equipment Cleaning ❌ | Galley Equipment Sanitisation ✓ |
| Communication Skills | Provide responsible service of alcohol | RSA Communication ❌ | Intoxication Refusal Communication ✓ |
| Safety Checks | Work safely at heights | Heights Safety Checks ❌ | Harness and Anchor Point Inspection ✓ |
| Data Entry | Process financial transactions | Financial Data Entry ❌ | Transaction Record Entry ✓ |
| Behaviour Analysis | Handle companion animals | Animal Behaviour Analysis ❌ | Pet Stress Signal Recognition ✓ |
| Risk Assessment | Conduct underground mining operations | Mining Risk Assessment ❌ | Ground Stability Assessment ✓ |
| Documentation | Prepare legal documents | Legal Documentation ❌ | Contract Drafting ✓ |

### Key Principle:
Ask yourself: "In this unit, WHAT is the equipment? WHAT is being communicated? WHAT procedures?"
Then name the skill based on that specific thing, not the industry.

## Refinement Principles:

### 1. CLARIFY THE VAGUE TERM
Use the unit context to understand what generic words actually mean:
- "Equipment" in aircraft catering = galley equipment, trolleys, ovens
- "Communication" in RSA = refusing service, explaining limits
- "Procedures" in aged care = medication rounds, hygiene protocols
- "Assessment" in mining = ground stability, ventilation, gas levels

### 2. NAME THE ACTUAL ACTIVITY
The refined name should describe what the person is actually doing:
- Not "Aircraft Communication" → but "Passenger Meal Service Coordination"
- Not "Mining Safety" → but "Ventilation System Monitoring"
- Not "Healthcare Documentation" → but "Patient Observation Recording"

### 3. OPTIMAL LENGTH: 2-5 WORDS
Keep it concise but specific enough to be self-explanatory.

### 4. WHEN TO KEEP ORIGINAL
Keep the original name if:
- It's already specific and clear
- The unit context doesn't add clarity
- The original accurately describes what the person does

## Critical Rules:
1. DO NOT just add industry/domain prefixes
2. DO clarify what vague terms actually refer to
3. The refined name should be understandable WITHOUT knowing the unit
4. Focus on WHAT is being done, not WHERE it's being done
5. Use terminology that describes the actual objects, actions, or outcomes

You MUST respond with valid JSON only. No additional text or explanation."""


class SkillNameRefiner:
    """
    Refines skill names based on descriptions using LLM.
    
    The tool analyzes skill descriptions to create more accurate, domain-specific
    skill names that better capture the actual capability being described.
    
    Uses one prompt per skill in batch calls for optimal processing.
    """
    
    def __init__(self, genai_interface=None, config: Optional[Dict] = None):
        """
        Initialize the skill name refiner.
        
        Args:
            genai_interface: GenAI interface (vLLM or Azure OpenAI)
            config: Configuration dictionary
        """
        self.genai_interface = genai_interface
        self.config = config or {}
        
        # Processing settings
        self.batch_size = self.config.get('batch_size', 20)
        self.max_retries = self.config.get('max_retries', 3)
        
        # Statistics
        self.stats = {
            'total_processed': 0,
            'successfully_refined': 0,
            'unchanged': 0,
            'failed': 0,
            'errors': []
        }
        
        logger.info(f"Initialized SkillNameRefiner with batch_size={self.batch_size}")
    
    def _get_single_skill_prompt(self, skill: Dict) -> str:
        """
        Generate a user prompt for a single skill refinement.
        
        Args:
            skill: Dictionary with 'name', 'description', 'unit_title', and optionally 'category'
            
        Returns:
            User prompt string for this skill
        """
        name = skill.get('name', '')
        description = skill.get('description', '')[:500]  # Truncate long descriptions
        unit_title = skill.get('unit_title', '')
        category = skill.get('category', '')
        
        user_prompt = f"""Refine the following skill name to make it clearer and more specific.

## Skill Information:
- Current Skill Name: {name}
- Skill Description: {description}
- VET Unit Title: {unit_title}
- Category: {category}

## Your Task:
1. Use the Unit Title to understand WHAT the vague terms in the skill name actually refer to
2. Ask yourself: "What equipment? What procedures? What communication? What assessment?"
3. Create a skill name that clearly describes the actual activity WITHOUT needing context
4. DO NOT just add industry prefixes - instead clarify what the skill actually involves

## Example of what I want:
- "Equipment Cleaning" in aircraft catering context → "Galley Equipment Sanitisation" (NOT "Aircraft Equipment Cleaning")
- The goal is to clarify WHAT equipment, not just add WHERE

## Output Format:
Return ONLY a JSON object (no markdown, no explanation):
{{"original_name": "{name}", "refined_name": "clarified skill name", "refinement_reason": "Brief explanation of what the vague term actually refers to", "confidence": 0.85, "changed": true}}

Rules for `changed` field:
- true: if the refined name is different from original
- false: if keeping the original name (refined_name should equal original_name)

Return ONLY the JSON object:"""

        return user_prompt
    
    def _parse_single_response(self, response: str, original_name: str) -> Dict:
        """
        Parse LLM response for a single skill refinement.
        
        Args:
            response: Raw LLM response text
            original_name: Original skill name for fallback
            
        Returns:
            Refinement dictionary
        """
        if not response:
            return {
                'original_name': original_name,
                'refined_name': original_name,
                'refinement_reason': 'No response from LLM',
                'confidence': 0.0,
                'changed': False
            }
        
        text = response.strip()
        
        # Remove markdown code blocks if present
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to find JSON object
        try:
            # Try direct parse
            result = json.loads(text)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in text
        obj_match = re.search(r'\{[\s\S]*?\}', text)
        if obj_match:
            try:
                result = json.loads(obj_match.group())
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass
        
        # Fallback
        logger.warning(f"Failed to parse refinement response for '{original_name}'")
        return {
            'original_name': original_name,
            'refined_name': original_name,
            'refinement_reason': 'Failed to parse response',
            'confidence': 0.0,
            'changed': False
        }
    
    def refine_skill_names_batch(self, skills: List[Dict]) -> List[Dict]:
        """
        Refine skill names for a batch of skills using one prompt per skill.
        
        Args:
            skills: List of dictionaries with 'name', 'description', and optionally 'category'
            
        Returns:
            List of refined skill dictionaries
        """
        if not self.genai_interface:
            logger.error("No GenAI interface available for skill name refinement")
            return [{**s, 'org_name': s['name'], 'name_changed': False} for s in skills]
        
        # Generate one prompt per skill
        user_prompts = [self._get_single_skill_prompt(skill) for skill in skills]
        
        try:
            # Use batch generation with one prompt per skill
            responses = self.genai_interface._generate_batch(
                user_prompts=user_prompts,
                system_prompt=REFINEMENT_SYSTEM_PROMPT
            )
            
            if not responses or len(responses) != len(skills):
                logger.warning(f"Unexpected response count: got {len(responses) if responses else 0}, expected {len(skills)}")
                # Pad with empty responses if needed
                if responses is None:
                    responses = [''] * len(skills)
                while len(responses) < len(skills):
                    responses.append('')
            
            # Process each response
            results = []
            for i, (skill, response) in enumerate(zip(skills, responses)):
                skill_copy = skill.copy()
                
                # Parse the response
                refinement = self._parse_single_response(response, skill['name'])
                
                # Apply refinement
                refined_name = refinement.get('refined_name', skill['name'])
                changed = refinement.get('changed', False)
                
                # Validate refinement
                if refined_name and len(refined_name) >= 3:
                    skill_copy['org_name'] = skill['name']
                    skill_copy['name'] = refined_name
                    skill_copy['refinement_reason'] = refinement.get('refinement_reason', '')
                    skill_copy['refinement_confidence'] = refinement.get('confidence', 0.0)
                    skill_copy['name_changed'] = changed and refined_name.lower() != skill['name'].lower()
                    
                    if skill_copy['name_changed']:
                        self.stats['successfully_refined'] += 1
                    else:
                        self.stats['unchanged'] += 1
                else:
                    skill_copy['org_name'] = skill['name']
                    skill_copy['name_changed'] = False
                    skill_copy['refinement_reason'] = ''
                    skill_copy['refinement_confidence'] = 0.0
                    self.stats['unchanged'] += 1
                
                results.append(skill_copy)
                self.stats['total_processed'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch refinement: {e}")
            self.stats['failed'] += len(skills)
            self.stats['errors'].append(str(e))
            
            # Return original skills with org_name
            return [{**s, 'org_name': s['name'], 'name_changed': False, 
                    'refinement_reason': '', 'refinement_confidence': 0.0} for s in skills]
    
    def refine_skills_dataframe(self, 
                                 df: pd.DataFrame,
                                 name_column: str = 'name',
                                 description_column: str = 'description',
                                 unit_title_column: str = 'unit_title',
                                 category_column: str = 'category') -> pd.DataFrame:
        """
        Refine skill names for an entire DataFrame.
        
        Args:
            df: DataFrame containing skills
            name_column: Column name for skill names
            description_column: Column name for descriptions
            unit_title_column: Column name for VET unit titles (provides domain context)
            category_column: Column name for categories
            
        Returns:
            DataFrame with refined names and original names preserved
        """
        logger.info(f"Starting skill name refinement for {len(df)} skills")
        logger.info(f"Batch size: {self.batch_size} (one prompt per skill)")
        
        # Check for unit_title column
        has_unit_title = unit_title_column in df.columns
        if has_unit_title:
            logger.info(f"Using unit title column '{unit_title_column}' for domain context")
        else:
            logger.warning(f"No unit title column '{unit_title_column}' found - refinements may be less context-aware")
        
        # Prepare skills for processing
        all_skills = []
        for idx in df.index:
            skill = {
                'index': idx,
                'name': str(df.loc[idx, name_column]) if name_column in df.columns else '',
                'description': str(df.loc[idx, description_column]) if description_column in df.columns else '',
                'unit_title': str(df.loc[idx, unit_title_column]) if has_unit_title else '',
                'category': str(df.loc[idx, category_column]) if category_column in df.columns else ''
            }
            all_skills.append(skill)
        
        # Process in batches
        refined_skills = []
        
        for batch_start in tqdm(range(0, len(all_skills), self.batch_size), 
                                desc="Refining skill names"):
            batch_end = min(batch_start + self.batch_size, len(all_skills))
            batch = all_skills[batch_start:batch_end]
            
            # Try refinement with retries
            refined_batch = None
            for attempt in range(self.max_retries):
                try:
                    refined_batch = self.refine_skill_names_batch(batch)
                    break
                except Exception as e:
                    logger.warning(f"Batch refinement attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        # Final fallback - keep original names
                        refined_batch = [{**s, 'org_name': s['name'], 'name_changed': False,
                                         'refinement_reason': '', 'refinement_confidence': 0.0} for s in batch]
            
            refined_skills.extend(refined_batch)
        
        # Create result DataFrame
        df_result = df.copy()
        
        # Add new columns
        df_result['org_name'] = df_result[name_column]
        df_result['name_changed'] = False
        df_result['refinement_reason'] = ''
        df_result['refinement_confidence'] = 0.0
        
        # Apply refinements
        for refined_skill in refined_skills:
            idx = refined_skill['index']
            if idx in df_result.index:
                df_result.loc[idx, name_column] = refined_skill.get('name', df_result.loc[idx, name_column])
                df_result.loc[idx, 'org_name'] = refined_skill.get('org_name', df_result.loc[idx, 'org_name'])
                df_result.loc[idx, 'name_changed'] = refined_skill.get('name_changed', False)
                df_result.loc[idx, 'refinement_reason'] = refined_skill.get('refinement_reason', '')
                df_result.loc[idx, 'refinement_confidence'] = refined_skill.get('refinement_confidence', 0.0)
        
        # Log statistics
        self._log_refinement_statistics(df_result)
        
        return df_result
    
    def _log_refinement_statistics(self, df: pd.DataFrame):
        """Log statistics about the refinement process."""
        logger.info("\n" + "=" * 60)
        logger.info("SKILL NAME REFINEMENT STATISTICS")
        logger.info("=" * 60)
        
        total = len(df)
        changed = df['name_changed'].sum() if 'name_changed' in df.columns else 0
        unchanged = total - changed
        
        logger.info(f"Total skills processed: {total}")
        logger.info(f"Names refined: {changed} ({100*changed/total:.1f}%)")
        logger.info(f"Names unchanged: {unchanged} ({100*unchanged/total:.1f}%)")
        
        if 'refinement_confidence' in df.columns:
            changed_df = df[df['name_changed']]
            if len(changed_df) > 0:
                avg_confidence = changed_df['refinement_confidence'].mean()
                logger.info(f"Average refinement confidence: {avg_confidence:.2f}")
        
        logger.info("=" * 60)
    
    def get_statistics(self) -> Dict:
        """Get refinement statistics."""
        return self.stats.copy()


def run_skill_name_refinement(
    input_file: str,
    output_file: str,
    config: Optional[Dict] = None,
    genai_interface=None
) -> pd.DataFrame:
    """
    Main function to run skill name refinement on a file.
    
    Args:
        input_file: Path to input Excel/CSV file
        output_file: Path to output Excel file
        config: Configuration dictionary
        genai_interface: GenAI interface for LLM calls
        
    Returns:
        DataFrame with refined skill names
    """
    logger.info(f"Loading skills from: {input_file}")
    
    # Load input file
    input_path = Path(input_file)
    if input_path.suffix.lower() == '.csv':
        df = pd.read_csv(input_file)
    elif input_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(input_file)
    elif input_path.suffix.lower() == '.parquet':
        df = pd.read_parquet(input_file)
    else:
        raise ValueError(f"Unsupported file format: {input_path.suffix}")
    
    logger.info(f"Loaded {len(df)} skills")
    
    # Initialize refiner
    if genai_interface is None:
        # Try to create genai interface from config
        try:
            from src.interfaces.model_factory import ModelFactory
            genai_interface = ModelFactory.create_genai_interface(config)
        except Exception as e:
            logger.error(f"Failed to create GenAI interface: {e}")
            raise
    
    refiner = SkillNameRefiner(
        genai_interface=genai_interface,
        config=config or {}
    )
    
    # Determine column names
    name_col = 'name' if 'name' in df.columns else 'skill_name'
    desc_col = 'description' if 'description' in df.columns else 'skill_description'
    
    # Try to find unit title column (provides crucial domain context)
    unit_title_col = None
    for col_name in ['unit_title', 'unit_name', 'unit', 'competency_title', 'uoc_title']:
        if col_name in df.columns:
            unit_title_col = col_name
            break
    
    cat_col = 'category' if 'category' in df.columns else None
    
    # Run refinement
    df_refined = refiner.refine_skills_dataframe(
        df,
        name_column=name_col,
        description_column=desc_col,
        unit_title_column=unit_title_col if unit_title_col else 'unit_title',
        category_column=cat_col if cat_col else 'category'
    )
    
    # Save output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.suffix.lower() == '.csv':
        df_refined.to_csv(output_file, index=False)
    else:
        df_refined.to_excel(output_file, index=False)
    
    logger.info(f"Saved refined skills to: {output_file}")
    
    return df_refined


# CLI interface
if __name__ == "__main__":
    import argparse
    import sys
    import os
    
    # Add project root to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    parser = argparse.ArgumentParser(
        description="Refine skill names based on descriptions and VET unit context using LLM"
    )
    
    parser.add_argument(
        "input_file",
        help="Input Excel/CSV file with skills"
    )
    
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output file path (default: input_refined.xlsx)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=20,
        help="Batch size for LLM processing (default: 20)"
    )
    
    parser.add_argument(
        "--unit-title-column",
        default=None,
        help="Column name containing VET unit titles for context (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Process only a sample of N skills"
    )
    
    parser.add_argument(
        "--backend",
        choices=['vllm', 'openai'],
        default='vllm',
        help="LLM backend to use (default: vllm)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load config
    try:
        from config.settings_faceted import CONFIG
    except ImportError:
        CONFIG = {}
    
    CONFIG['batch_size'] = args.batch_size
    CONFIG['backend_type'] = args.backend
    if args.unit_title_column:
        CONFIG['unit_title_column'] = args.unit_title_column
    
    # Determine output file
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_refined.xlsx")
    
    # Run refinement
    try:
        df_result = run_skill_name_refinement(
            args.input_file,
            output_file,
            config=CONFIG
        )
        
        print(f"\nRefinement complete!")
        print(f"Output saved to: {output_file}")
        print(f"Total skills: {len(df_result)}")
        print(f"Names changed: {df_result['name_changed'].sum()}")
        
    except Exception as e:
        logger.error(f"Refinement failed: {e}")
        sys.exit(1)