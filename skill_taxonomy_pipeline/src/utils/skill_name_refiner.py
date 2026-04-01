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
REFINEMENT_SYSTEM_PROMPT = """
You are an expert skill taxonomist for Australian VET (Vocational Education and Training).

Your task is to refine vague skill names into clear, specific skill labels by adding the missing OBJECT or DOMAIN from the Unit Title.

────────────────────────────────────────
CORE PRINCIPLE — MATCH THE WORK LEVEL
────────────────────────────────────────

The refined skill name MUST reflect what the person ACTUALLY DOES physically or cognitively. Do NOT elevate practical work into management language.

There are TWO types of skills. You must identify which type and name accordingly:

TYPE A — HANDS-ON / PRACTICAL SKILLS
The person uses tools, equipment, materials, or physical techniques.
Use PRACTICAL language: Welding, Cutting, Handling, Cooking, Wiring, Plumbing, Shearing, Grooming, Dressing, Pruning, Drilling, Mixing, Laying, Fitting, Sewing, Painting, Driving, Lifting, Feeding, Planting.

TYPE B — PROFESSIONAL / MANAGEMENT SKILLS  
The person uses judgement, authority, analysis, or coordination from a supervisory or professional position.
Use PROFESSIONAL language: Assessment, Analysis, Management, Compliance, Strategy, Coordination, Planning, Governance, Oversight.

────────────────────────────────────────
CRITICAL RULE — DO NOT ELEVATE TYPE A INTO TYPE B
────────────────────────────────────────

If the description says the person is DOING physical work, the skill name MUST use practical verbs/nouns. Do NOT replace practical words with management abstractions.

WRONG (elevating practical work to management):
- "Cleans bee smoker" → "Bee Smoker Fire Prevention Strategy" ✗
- "Feeds alpacas" → "Animal Feeding Instruction" ✗
- "Ties steel reinforcement" → "Reinforcement Management" ✗
- "Shears sheep" → "Shearing Oversight" ✗
- "Checks carcass quality" → "Carcass QA Correlation" ✗
- "Stacks crop containers" → "Crop Container Stacking Optimisation" ✗

RIGHT (preserving practical language):
- "Cleans bee smoker" → "Bee Smoker Cleaning" ✓
- "Feeds alpacas" → "Alpaca Feeding" ✓
- "Ties steel reinforcement" → "Steel Reinforcement Tying" ✓
- "Shears sheep" → "Sheep Shearing" ✓
- "Checks carcass quality" → "Carcass Quality Checking" ✓
- "Stacks crop containers" → "Crop Container Stacking" ✓

────────────────────────────────────────
BANNED WORDS FOR TYPE A SKILLS
────────────────────────────────────────

When the person is doing PRACTICAL/HANDS-ON work, do NOT use these as the main noun:

BANNED for Type A: Strategy, Governance, Advisory, Oversight, Optimisation, Correlation, Integration, Assurance, Evaluation

These words imply professional/management authority that a hands-on worker does not exercise.

ALLOWED for Type A: the practical verb as a gerund noun:
Welding, Cutting, Handling, Cooking, Wiring, Cleaning, Shearing, Grooming, Dressing, Pruning, Drilling, Mixing, Laying, Fitting, Sewing, Painting, Driving, Lifting, Feeding, Planting, Harvesting, Milling, Grinding, Brazing, Soldering, Tiling, Plastering, Concreting, Bricklaying, Scaffolding, Rigging, Testing, Checking, Measuring, Calibrating, Sampling, Inspecting, Operating, Servicing, Repairing, Installing, Assembling, Fabricating, Joining, Finishing, Coating, Polishing, Pouring, Moulding, Turning, Boring, Threading, Pressing, Stamping, Folding, Rolling, Bending

────────────────────────────────────────
WHEN TO USE MANAGEMENT LANGUAGE (TYPE B ONLY)
────────────────────────────────────────

Use management/professional nouns ONLY when the description explicitly says the person:
- Supervises or directs OTHER people's work
- Makes policy or strategic decisions
- Conducts formal audits or compliance reviews
- Manages budgets, projects, or programs
- Assesses risks using formal frameworks (matrices, registers)
- Writes formal reports, policies, or procedures

Examples of genuine Type B skills:
- "Conducts WHS audit of construction site" → "Construction WHS Auditing" ✓
- "Develops animal welfare compliance policy" → "Animal Welfare Policy Development" ✓
- "Manages shearing team schedule and output" → "Shearing Team Coordination" ✓
- "Assesses fire risk using risk matrix" → "Bushfire Risk Assessment" ✓

────────────────────────────────────────
THE REFINEMENT PROCESS
────────────────────────────────────────

1. Read the Description to understand what the person ACTUALLY DOES
2. Determine if it is Type A (hands-on) or Type B (professional/management)
3. Read the Unit Title to identify the missing OBJECT or DOMAIN
4. If the skill name already contains the object/domain → KEEP unchanged
5. If missing → Add it using language appropriate to the type (A or B)

────────────────────────────────────────
GENERIC CAPABILITY PROTECTION RULE
────────────────────────────────────────

If the original skill is a general human capability (communication, teamwork, planning, coordination, leadership, judgement, analysis, problem-solving), DO NOT add technical or equipment-specific domains from the Unit Title.

Generic soft skills MUST remain generic:
- "Face-to-Face Communication" → keep as is, NOT "Helicopter Communication"
- "Teamwork" → keep as is, NOT "Aviation Teamwork"
- "Problem Solving" → keep as is, NOT "Plumbing Problem Solving"

Domains can ONLY be added when they are INTRINSIC to the capability itself.

────────────────────────────────────────
NAMING CONSTRAINTS
────────────────────────────────────────

- Keep to 2-5 words
- Use noun-headed phrases (the last word should be a noun or gerund noun)
- Preferred structure: [Domain/Object] + [Action-as-Noun]
  Examples: "Sheep Shearing", "Concrete Placing", "IV Cannulation", "Forklift Operation"
- For Type B: [Domain/Object] + [Professional Noun]
  Examples: "Bushfire Risk Assessment", "Carbon Farming Compliance", "WHS Auditing"
- Use Australian VET terminology where appropriate

────────────────────────────────────────
MORE EXAMPLES
────────────────────────────────────────

| Description | Unit Title | Refined Name |
|------------|------------|--------------|
| Operates excavator to dig trenches | Conduct excavator operations | Trench Excavation |
| Mixes concrete to specified ratios | Carry out concreting | Concrete Mix Preparation |
| Applies wound dressing to patient | Provide wound care | Wound Dressing Application |
| Monitors sheep for signs of illness | Handle livestock | Sheep Health Monitoring |
| Reviews compliance with food safety law | Manage food safety program | Food Safety Compliance Review |
| Identifies hazards in shearing shed | Work safely in shearing | Shearing Shed Hazard Identification |
| Selects correct welding rod for joint | Perform MMAW welding | Welding Rod Selection |
| Records animal feeding data in logbook | Maintain animal records | Animal Feeding Record Keeping |
| Prunes branches using chainsaw | Perform tree pruning | Chainsaw Pruning |
| Supervises junior staff during harvest | Coordinate harvest operations | Harvest Team Supervision |

────────────────────────────────────────
OUTPUT
────────────────────────────────────────

Return ONLY valid JSON.
Do NOT include explanations or commentary.

"""


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
        description = skill.get('description', '')
        unit_title = skill.get('unit_title', '')
        
        user_prompt = f"""Refine the following skill name using the rules in the system prompt.

Skill Name: {name}
Description: {description}
Unit Title: {unit_title}

Steps:
1. Read the Description — is this person doing HANDS-ON work (Type A) or PROFESSIONAL/MANAGEMENT work (Type B)?
2. Use the Unit Title to identify any missing object or domain
3. Refine the name using practical language for Type A or professional language for Type B
4. Keep to 2-5 words

Output (JSON only):
{{"original_name": "{name}", "refined_name": "your refined name here", "changed": true/false, "confidence": 0.0-1.0, "type": "A or B"}}"""

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
            result = json.loads(text)
            if isinstance(result, dict):
                result.setdefault('original_name', original_name)
                result.setdefault('refined_name', original_name)
                result.setdefault('changed', False)
                result.setdefault('confidence', 0.0)
                return result
        except json.JSONDecodeError:
            pass
        
        # Try to find JSON object in text
        obj_match = re.search(r'\{[\s\S]*?\}', text)
        if obj_match:
            try:
                result = json.loads(obj_match.group())
                if isinstance(result, dict):
                    result.setdefault('original_name', original_name)
                    result.setdefault('refined_name', original_name)
                    result.setdefault('changed', False)
                    result.setdefault('confidence', 0.0)
                    return result
            except json.JSONDecodeError:
                pass
        
        return None
    
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
            responses = self.genai_interface._generate_batch(
                user_prompts=user_prompts,
                system_prompt=REFINEMENT_SYSTEM_PROMPT
            )
            
            if not responses or len(responses) != len(skills):
                logger.warning(f"Unexpected response count: got {len(responses) if responses else 0}, expected {len(skills)}")
                if responses is None:
                    responses = [''] * len(skills)
                while len(responses) < len(skills):
                    responses.append('')
            
            results = []
            for i, (skill, response) in enumerate(zip(skills, responses)):
                skill_copy = skill.copy()
                retry_count = 5
                loop = True
                
                while loop:
                    try:
                        loop = False
                        refinement = self._parse_single_response(response, skill['name'])
                        if refinement is None and retry_count > 0:
                            retry_count -= 1
                            logger.warning(f"Failed to parse refinement response for '{skill['name']}', {retry_count} retries left")
                            response = self.genai_interface._generate_batch(
                                user_prompts=[self._get_single_skill_prompt(skill)],
                                system_prompt=REFINEMENT_SYSTEM_PROMPT
                            )[0]
                            loop = True
                        elif refinement is None and retry_count == 0:
                            logger.warning(f"All retries exhausted for skill {skill['name']}")
                            refinement = {
                                'original_name': skill['name'],
                                'refined_name': skill['name'],
                                'confidence': 0.0,
                                'changed': False
                            }
                    except Exception as e:
                        if retry_count > 0:
                            retry_count -= 1
                            logger.warning(f"Error for '{skill['name']}', {retry_count} retries left: {e}")
                            try:
                                response = self.genai_interface._generate_batch(
                                    user_prompts=[self._get_single_skill_prompt(skill)],
                                    system_prompt=REFINEMENT_SYSTEM_PROMPT
                                )[0]
                                loop = True
                            except Exception:
                                loop = False
                                refinement = {
                                    'original_name': skill['name'],
                                    'refined_name': skill['name'],
                                    'confidence': 0.0,
                                    'changed': False
                                }
                        else:
                            loop = False
                            refinement = {
                                'original_name': skill['name'],
                                'refined_name': skill['name'],
                                'confidence': 0.0,
                                'changed': False
                            }

                # Apply refinement
                refined_name = refinement.get('refined_name', skill['name'])
                changed = refinement.get('changed', False)
                
                if refined_name and len(refined_name) >= 3:
                    skill_copy['org_name'] = skill['name']
                    skill_copy['name'] = refined_name
                    skill_copy['refinement_confidence'] = refinement.get('confidence', 0.0)
                    skill_copy['name_changed'] = changed and refined_name.lower() != skill['name'].lower()
                    
                    if skill_copy['name_changed']:
                        self.stats['successfully_refined'] += 1
                    else:
                        self.stats['unchanged'] += 1
                else:
                    skill_copy['org_name'] = skill['name']
                    skill_copy['name_changed'] = False
                    skill_copy['refinement_confidence'] = 0.0
                    self.stats['unchanged'] += 1
                
                results.append(skill_copy)
                self.stats['total_processed'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"Error in batch refinement: {e}")
            self.stats['failed'] += len(skills)
            self.stats['errors'].append(str(e))
            
            return [{**s, 'org_name': s['name'], 'name_changed': False, 
                    'refinement_confidence': 0.0} for s in skills]
    
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
        
        has_unit_title = unit_title_column in df.columns
        if has_unit_title:
            logger.info(f"Using unit title column '{unit_title_column}' for domain context")
        else:
            logger.warning(f"No unit title column '{unit_title_column}' found")
        
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
            
            refined_batch = None
            for attempt in range(self.max_retries):
                try:
                    refined_batch = self.refine_skill_names_batch(batch)
                    break
                except Exception as e:
                    logger.warning(f"Batch refinement attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        refined_batch = [{**s, 'org_name': s['name'], 'name_changed': False,
                                         'refinement_confidence': 0.0} for s in batch]
            
            refined_skills.extend(refined_batch)
        
        # Create result DataFrame
        df_result = df.copy()
        df_result['org_name'] = df_result[name_column]
        df_result['name_changed'] = False
        df_result['refinement_confidence'] = 0.0
        
        for refined_skill in refined_skills:
            idx = refined_skill['index']
            if idx in df_result.index:
                df_result.loc[idx, name_column] = refined_skill.get('name', df_result.loc[idx, name_column])
                df_result.loc[idx, 'org_name'] = refined_skill.get('org_name', df_result.loc[idx, 'org_name'])
                df_result.loc[idx, 'name_changed'] = refined_skill.get('name_changed', False)
                df_result.loc[idx, 'refinement_confidence'] = refined_skill.get('refinement_confidence', 0.0)
        
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
    """
    logger.info(f"Loading skills from: {input_file}")
    
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
    
    if genai_interface is None:
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
    
    name_col = 'name' if 'name' in df.columns else 'skill_name'
    desc_col = 'description' if 'description' in df.columns else 'skill_description'
    
    unit_title_col = None
    for col_name in ['unit_title', 'unit_name', 'unit', 'competency_title', 'uoc_title']:
        if col_name in df.columns:
            unit_title_col = col_name
            break
    
    cat_col = 'category' if 'category' in df.columns else None
    
    df_refined = refiner.refine_skills_dataframe(
        df,
        name_column=name_col,
        description_column=desc_col,
        unit_title_column=unit_title_col if unit_title_col else 'unit_title',
        category_column=cat_col if cat_col else 'category'
    )
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.suffix.lower() == '.csv':
        df_refined.to_csv(output_file, index=False)
    else:
        df_refined.to_excel(output_file, index=False)
    
    logger.info(f"Saved refined skills to: {output_file}")
    return df_refined


if __name__ == "__main__":
    import argparse
    import sys
    import os
    
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    parser = argparse.ArgumentParser(
        description="Refine skill names based on descriptions and VET unit context using LLM"
    )
    parser.add_argument("input_file", help="Input Excel/CSV file with skills")
    parser.add_argument("-o", "--output", default=None, help="Output file path")
    parser.add_argument("--batch-size", type=int, default=20, help="Batch size for LLM processing")
    parser.add_argument("--backend", choices=['vllm', 'openai'], default='vllm', help="LLM backend")
    
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    try:
        from config.settings import CONFIG
    except ImportError:
        CONFIG = {}
    
    CONFIG['batch_size'] = args.batch_size
    CONFIG['backend_type'] = args.backend
    
    if args.output:
        output_file = args.output
    else:
        input_path = Path(args.input_file)
        output_file = str(input_path.parent / f"{input_path.stem}_refined.xlsx")
    
    try:
        df_result = run_skill_name_refinement(args.input_file, output_file, config=CONFIG)
        print(f"\nRefinement complete!")
        print(f"Output saved to: {output_file}")
        print(f"Total skills: {len(df_result)}")
        print(f"Names changed: {df_result['name_changed'].sum()}")
    except Exception as e:
        logger.error(f"Refinement failed: {e}")
        sys.exit(1)