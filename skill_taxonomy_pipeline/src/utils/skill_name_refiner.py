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
3. Read the Unit Title to identify the DOMAIN context
4. Apply the DOMAIN ADDITION TEST (below) to decide whether to add domain
5. If domain should be added → add it using language appropriate to the type
6. If domain should NOT be added → keep the skill name generic

────────────────────────────────────────
DOMAIN ADDITION TEST (CRITICAL)
────────────────────────────────────────

Before adding any domain context from the Unit Title, ask:

"Can a person who can do this skill in domain A also do it in domain B
WITHOUT needing to learn new domain-specific knowledge?"

If YES → the skill TRANSFERS across domains → do NOT add domain.
If NO → the domain CHANGES the ability → DO add domain.

EXAMPLES WHERE DOMAIN TRANSFERS (do NOT add domain):
- "Record Keeping" — keeping records is the same process everywhere.
  "Assistance Dog Training Record Keeping" ✗ → "Record Keeping" ✓
- "PPE Selection" — selecting PPE follows the same hazard-based process.
  "Shearing PPE Selection" ✗ → "PPE Selection" ✓
- "Data Analysis" — analytical technique transfers across all domains.
  "Agricultural Data Analysis" ✗ → "Data Analysis" ✓
- "Communication" — communication skill transfers everywhere.
  "Veterinary Drug Dosage Communication" ✗ → "Drug Dosage Communication" ✓
- "Risk Assessment" — the risk assessment PROCESS is the same everywhere.
  "Alpaca Hazard Risk Assessment" ✗ → "Hazard Risk Assessment" ✓
- "Scheduling" — scheduling is scheduling regardless of domain.
  "Shearing Team Scheduling" ✗ → "Team Scheduling" ✓
- "Cost Calculation" — maths transfers.
  "Wool Premium Percentage Calculation" ✗ → "Percentage Calculation" ✓
- "Compliance Checking" — compliance process transfers.
  "Bee Transport Permit Compliance" ✗ → "Permit Compliance Checking" ✓
- "Budget Monitoring" — budgeting transfers.
  "Companion Animal Campaign Budget Monitoring" ✗ → "Campaign Budget Monitoring" ✓

EXAMPLES WHERE DOMAIN CHANGES THE ABILITY (DO add domain):
- "Stress Prevention" — animal stress is completely different from human stress.
  "Stress Prevention" ✗ → "Animal Stress Prevention" ✓
- "Behaviour Modification" — modifying animal behaviour ≠ modifying human behaviour.
  "Behaviour Modification" ✗ → "Animal Behaviour Modification" ✓
- "Infection Control" — animal infection control ≠ hospital infection control.
  "Infection Control" ✗ → "Animal Infection Control" ✓
- "Health Assessment" — assessing animal health ≠ assessing human health.
  "Health Assessment" ✗ → "Animal Health Assessment" ✓
- "Wound Dressing" — animal wounds differ from human wounds.
  "Wound Dressing" ✗ → "Animal Wound Dressing" ✓
- "Nutrition Planning" — animal nutrition ≠ human nutrition.
  "Nutrition Planning" ✗ → "Animal Nutrition Planning" ✓
- "Habitat Assessment" — specific to ecosystem/species.
  "Habitat Assessment" ✗ → "Marine Habitat Assessment" ✓
- "Pruning" — pruning technique depends on plant species.
  "Pruning" ✗ → "Amenity Tree Pruning" ✓

────────────────────────────────────────
QUICK REFERENCE — GENERIC SKILLS (never add domain)
────────────────────────────────────────

These skills are ALWAYS transferable. NEVER add domain qualifiers:
Record Keeping, Data Entry, Filing, Documentation, Reporting,
Communication, Briefing, Presentation, Active Listening,
Scheduling, Time Management, Prioritisation,
PPE Selection, Manual Handling, Hazard Identification,
Risk Assessment, Compliance Checking, Audit,
Cost Calculation, Budget Monitoring, Numeracy,
Teamwork, Supervision, Coordination, Delegation,
Problem Solving, Decision Making, Research,
Quality Checking, Inspection, Verification

────────────────────────────────────────
QUICK REFERENCE — DOMAIN-SPECIFIC SKILLS (always add domain)
────────────────────────────────────────

These skills CHANGE based on domain. ALWAYS add domain qualifiers:
Health Assessment, Infection Control, Wound Care, Medication,
Behaviour Modification, Stress Management, Nutrition Planning,
Species Identification, Habitat Assessment, Breeding,
Diagnosis, Treatment, Rehabilitation, Therapy,
Propagation, Pruning technique, Grafting, Pollination,
Welding technique, Machining technique, Cooking technique

────────────────────────────────────────
NAMING CONSTRAINTS
────────────────────────────────────────

- Keep to 2-5 words
- Use noun-headed phrases (the last word should be a noun or gerund noun)
- Preferred structure: [Domain/Object] + [Action-as-Noun]
  Examples: "Sheep Shearing", "Concrete Placing", "IV Cannulation", "Forklift Operation"
- For generic transferable skills, keep short: "Record Keeping", "PPE Selection", "Risk Assessment"
- For domain-specific skills: "Animal Health Assessment", "Marine Habitat Survey", "Tree Pruning"
- Use Australian VET terminology where appropriate

────────────────────────────────────────
MORE EXAMPLES
────────────────────────────────────────

| Description | Unit Title | Refined Name | Why |
|------------|------------|--------------|-----|
| Operates excavator to dig trenches | Conduct excavator operations | Trench Excavation | domain-specific technique |
| Mixes concrete to specified ratios | Carry out concreting | Concrete Mix Preparation | domain-specific technique |
| Applies wound dressing to patient | Provide wound care | Wound Dressing Application | domain-specific (human vs animal wounds differ) |
| Monitors sheep for signs of illness | Handle livestock | Sheep Health Monitoring | domain-specific (animal health ≠ human health) |
| Reviews compliance with food safety law | Manage food safety program | Compliance Review | generic process — transfers across all compliance |
| Identifies hazards in shearing shed | Work safely in shearing | Hazard Identification | generic process — same process everywhere |
| Selects correct welding rod for joint | Perform MMAW welding | Welding Rod Selection | domain-specific (welding knowledge needed) |
| Records animal feeding data in logbook | Maintain animal records | Record Keeping | generic process — recording data transfers |
| Prunes branches using chainsaw | Perform tree pruning | Chainsaw Pruning | domain-specific technique |
| Supervises junior staff during harvest | Coordinate harvest operations | Team Supervision | generic process — supervision transfers |
| Selects PPE for task | Work safely around animals | PPE Selection | generic process — PPE selection process is same |
| Plans rations for sheep flock | Provide livestock nutrition | Sheep Nutrition Planning | domain-specific (animal nutrition ≠ human nutrition) |
| Analyses soil test data | Manage soil health | Data Analysis | generic process — analytical method transfers |
| Modifies dog behaviour using conditioning | Train assistance dogs | Canine Behaviour Modification | domain-specific (animal ≠ human behaviour) |

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
    
    # ═══════════════════════════════════════════════════════════════
    #  POST-PROCESSING: Strip domain from generic transferable skills
    # ═══════════════════════════════════════════════════════════════

    # Generic skill suffixes that transfer across ALL domains.
    # If a refined name ends with one of these, the domain prefix is unnecessary.
    GENERIC_TRANSFERABLE_SUFFIXES = [
        # Record keeping & documentation
        'record keeping', 'data entry', 'data recording', 'documentation',
        'form completion', 'filing', 'record management', 'log keeping',
        'record maintenance', 'data collation', 'data collection',
        'record updating', 'document preparation', 'data management',
        # Communication
        'communication', 'briefing', 'active listening', 'presentation',
        'oral communication', 'written communication', 'reporting',
        'feedback provision', 'debriefing', 'instruction delivery',
        'instruction following', 'information delivery', 'explanation',
        # Safety & PPE
        'ppe selection', 'ppe usage', 'ppe fitting', 'ppe utilization',
        'ppe use', 'ppe compliance', 'hazard identification',
        'risk assessment', 'safety compliance', 'manual handling',
        'safe work practices', 'safe work practice implementation',
        # Planning & scheduling
        'scheduling', 'time management', 'prioritisation', 'planning',
        'task scheduling', 'work scheduling', 'deadline management',
        # Financial
        'cost calculation', 'cost estimation', 'budget monitoring',
        'budget management', 'cost analysis', 'percentage calculation',
        'payroll maintenance', 'wage calculation', 'invoice processing',
        # Quality & compliance
        'compliance checking', 'compliance verification', 'compliance review',
        'quality checking', 'quality inspection', 'audit', 'auditing',
        'compliance monitoring', 'verification',
        # Supervision & coordination
        'team supervision', 'team coordination', 'staff coordination',
        'work coordination', 'team briefing', 'team communication',
        'delegation', 'task allocation',
        # Research & analysis
        'data analysis', 'research', 'literature review',
        'information retrieval', 'information gathering',
        # Other generic processes
        'problem solving', 'decision making', 'conflict resolution',
        'negotiation', 'consultation', 'stakeholder engagement',
        'customer service', 'client communication',
        'inspection', 'testing', 'calibration', 'measurement',
        'housekeeping', 'work area cleaning', 'site cleaning',
        'procurement', 'ordering', 'inventory management',
        'stock management', 'storage', 'transport',
    ]

    # Domain words that should be stripped when preceding a generic suffix
    DOMAIN_PREFIXES_TO_STRIP = [
        # Multi-word domains (check these FIRST — longer matches take priority)
        'companion animal', 'assistance dog', 'marine wildlife',
        'native animal', 'native mammal', 'stingless bee', 'honey bee',
        'large animal', 'small animal', 'young animal',
        'wool room', 'shearing shed', 'woolshed', 'shearing team',
        'compost site', 'compost plant', 'mushroom substrate',
        'grain storage', 'nursery plant', 'indoor plant',
        'poultry shed', 'production shed',
        # Animals
        'animal', 'canine', 'feline', 'equine', 'bovine', 'ovine',
        'avian', 'porcine', 'alpaca', 'sheep', 'cattle', 'horse',
        'mare', 'dog', 'cat', 'poultry', 'pig', 'bee', 'fish',
        'livestock', 'aquatic', 'marine', 'amphibian', 'reptile',
        'bird', 'mammal', 'wildlife', 'zoological', 'veterinary',
        # Plants & agriculture
        'plant', 'crop', 'seed', 'soil', 'horticultural', 'nursery',
        'garden', 'turf', 'tree', 'vineyard', 'mushroom', 'cannabis',
        'agricultural', 'organic', 'compost', 'broadacre', 'pastoral',
        'grain', 'harvest', 'wool', 'fleece', 'shearing',
        # Industry contexts
        'construction', 'mining', 'maritime', 'aviation', 'automotive',
        'electrical', 'plumbing', 'welding', 'catering', 'hospitality',
        'retail', 'warehouse', 'laboratory', 'clinical', 'dental',
        'pharmaceutical', 'correctional', 'custodial',
        # Specific contexts
        'apiary', 'hive', 'incubation', 'carcass', 'carcase',
        'abattoir', 'stockyard',
    ]

    def _strip_unnecessary_domain(self, refined_name: str) -> str:
        """
        Strip domain qualifiers from generic transferable skills.
        
        If the skill ends with a generic transferable suffix (like "Record Keeping"),
        remove any domain prefix (like "Animal") because the skill transfers
        across all domains.
        
        Args:
            refined_name: The LLM-refined skill name
            
        Returns:
            Cleaned skill name with unnecessary domain stripped
        """
        name_lower = refined_name.lower().strip()
        
        # Check if the name ends with any generic transferable suffix
        matched_suffix = None
        for suffix in sorted(self.GENERIC_TRANSFERABLE_SUFFIXES, key=len, reverse=True):
            if name_lower.endswith(suffix):
                matched_suffix = suffix
                break
        
        if not matched_suffix:
            return refined_name
        
        # Extract the prefix (everything before the generic suffix)
        suffix_start = name_lower.rfind(matched_suffix)
        prefix = name_lower[:suffix_start].strip()
        
        if not prefix:
            return refined_name  # No prefix to strip
        
        # Iteratively strip domain words from the prefix (right to left)
        # This handles multi-layer prefixes like "Assistance Dog Training"
        # where "assistance dog" is a domain and "training" is context
        remaining_prefix = prefix
        stripped_any = False
        
        max_iterations = 5  # Safety limit
        for _ in range(max_iterations):
            found = False
            for domain in sorted(self.DOMAIN_PREFIXES_TO_STRIP, key=len, reverse=True):
                domain_lower = domain.lower()
                if remaining_prefix.endswith(domain_lower):
                    remaining_prefix = remaining_prefix[:remaining_prefix.rfind(domain_lower)].strip()
                    stripped_any = True
                    found = True
                    break
            
            if not found:
                # Check if remaining prefix is a generic context word that should also be stripped
                context_words = ['training', 'work', 'operations', 'service', 'services',
                                'facility', 'site', 'area', 'room', 'shed', 'field',
                                'workplace', 'worksite', 'industry', 'sector', 'program',
                                'project', 'production', 'processing', 'practice']
                remaining_words = remaining_prefix.split()
                if remaining_words and remaining_words[-1] in context_words:
                    remaining_prefix = ' '.join(remaining_words[:-1]).strip()
                    stripped_any = True
                else:
                    break
            
            if not remaining_prefix:
                break
        
        if not stripped_any:
            return refined_name
        
        # Reconstruct the name
        suffix_part = refined_name[suffix_start:].strip()
        if remaining_prefix:
            # Keep the remaining non-domain prefix with proper casing
            return remaining_prefix.title() + ' ' + suffix_part
        else:
            return suffix_part

    # ═══════════════════════════════════════════════════════════════
    #  STAGE 2: LLM VALIDATION for domain qualifiers
    #  Catches domain words not in the deterministic list
    # ═══════════════════════════════════════════════════════════════

    DOMAIN_VALIDATION_SYSTEM_PROMPT = """You determine whether a domain qualifier in a skill name is necessary or should be removed.

RULE: If the core skill transfers to ANY domain without needing new knowledge, remove the domain qualifier. If the domain changes HOW the skill is performed, keep it.

TRANSFERS (remove domain):
- "Brood Frame Record Keeping" → "Record Keeping" (recording data is the same everywhere)
- "Singe Carcase Issue Reporting" → "Issue Reporting" (reporting issues is the same process)
- "Gambrel Safety Inspection" → "Safety Inspection" (inspecting for safety is the same process)
- "Vermiculture Data Entry" → "Data Entry" (entering data is the same everywhere)
- "Aquaponics Budget Monitoring" → "Budget Monitoring" (budgeting transfers)
- "Silviculture Team Briefing" → "Team Briefing" (briefing a team transfers)
- "Apiculture PPE Selection" → "PPE Selection" (selecting PPE transfers)
- "Feedlot Compliance Checking" → "Compliance Checking" (compliance process transfers)

DOES NOT TRANSFER (keep domain):
- "Animal Behaviour Modification" → KEEP (animal behaviour ≠ human behaviour)
- "Tree Crown Reduction" → KEEP (domain-specific pruning technique)
- "Marine Species Identification" → KEEP (needs marine biology knowledge)
- "Equine Lameness Assessment" → KEEP (needs veterinary knowledge)
- "Soil pH Testing" → KEEP (needs soil science knowledge)

Output ONLY valid JSON: {"cleaned_name": "...", "domain_removed": true/false}
No explanations."""

    def _validate_domain_batch(self, skills_to_validate: List[Dict]) -> List[Dict]:
        """
        Stage 2: Use LLM to check if domain qualifiers should be stripped
        from skills that the deterministic list didn't catch.
        
        Args:
            skills_to_validate: List of dicts with 'index', 'refined_name', 'description'
            
        Returns:
            List of dicts with 'index' and 'cleaned_name'
        """
        if not self.genai_interface or not skills_to_validate:
            return skills_to_validate
        
        logger.info(f"Stage 2: LLM domain validation for {len(skills_to_validate)} skills")
        
        results = []
        
        # Process in batches
        for batch_start in range(0, len(skills_to_validate), self.batch_size):
            batch = skills_to_validate[batch_start:batch_start + self.batch_size]
            
            prompts = []
            for item in batch:
                prompt = (
                    f"Skill name: \"{item['refined_name']}\"\n"
                    f"Description: {item.get('description', '')[:200]}\n\n"
                    f"Does the domain qualifier transfer or should it be removed?\n"
                    f"{{\"cleaned_name\":"
                )
                prompts.append(prompt)
            
            try:
                responses = self.genai_interface._generate_batch(
                    user_prompts=prompts,
                    system_prompt=self.DOMAIN_VALIDATION_SYSTEM_PROMPT
                )
                
                for item, response in zip(batch, responses or []):
                    cleaned = item['refined_name']  # default: keep as-is
                    
                    if response:
                        text = response.strip()
                        # Prepend the partial JSON we sent
                        text = '{"cleaned_name":' + text
                        
                        # Clean up markdown
                        text = text.replace('```json', '').replace('```', '').strip()
                        
                        try:
                            parsed = json.loads(text)
                            if isinstance(parsed, dict) and 'cleaned_name' in parsed:
                                candidate = parsed['cleaned_name'].strip()
                                if candidate and len(candidate) >= 3:
                                    if parsed.get('domain_removed', False) or candidate != item['refined_name']:
                                        logger.debug(
                                            f"LLM domain strip: '{item['refined_name']}' → '{candidate}'"
                                        )
                                    cleaned = candidate
                        except (json.JSONDecodeError, KeyError):
                            # Try regex extraction
                            match = re.search(r'"cleaned_name"\s*:\s*"([^"]+)"', text)
                            if match:
                                candidate = match.group(1).strip()
                                if candidate and len(candidate) >= 3:
                                    cleaned = candidate
                    
                    results.append({
                        'index': item['index'],
                        'cleaned_name': cleaned,
                        'original_refined': item['refined_name'],
                    })
                    
            except Exception as e:
                logger.warning(f"LLM domain validation batch failed: {e}")
                for item in batch:
                    results.append({
                        'index': item['index'],
                        'cleaned_name': item['refined_name'],
                        'original_refined': item['refined_name'],
                    })
        
        stripped_count = sum(1 for r in results if r['cleaned_name'] != r['original_refined'])
        logger.info(f"Stage 2: LLM stripped domain from {stripped_count}/{len(results)} skills")
        
        return results

    def _needs_llm_domain_check(self, refined_name: str) -> bool:
        """
        Determine if a refined name should go through LLM domain validation.
        
        Returns True if the name has 3+ words AND wasn't already stripped by Stage 1,
        meaning it might have domain qualifiers the deterministic list missed.
        """
        words = refined_name.split()
        if len(words) < 3:
            return False  # Short names like "PPE Selection" are already fine
        
        # Check if the name ends with a generic suffix — if it does and still
        # has a prefix, it means Stage 1 didn't strip it, so the prefix might
        # be a domain word we missed
        name_lower = refined_name.lower()
        for suffix in self.GENERIC_TRANSFERABLE_SUFFIXES:
            if name_lower.endswith(suffix):
                prefix_part = name_lower[:name_lower.rfind(suffix)].strip()
                if prefix_part:
                    return True  # Has prefix + generic suffix → needs LLM check
        
        return False

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
2. Apply the DOMAIN ADDITION TEST: "Can a person who can do this skill in one domain also do it in another domain WITHOUT new domain knowledge?"
   - If YES (skill transfers) → do NOT add domain. Keep the name generic. Examples: Record Keeping, Data Entry, PPE Selection, Risk Assessment, Communication, Scheduling, Cost Calculation, Compliance Checking, Hazard Identification.
   - If NO (domain changes the ability) → DO add domain. Examples: Animal Health Assessment, Canine Behaviour Modification, Marine Habitat Survey, Tree Pruning.
3. Refine the name using practical language for Type A or professional language for Type B.
4. Keep to 2-5 words.

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
                
                # Post-process: strip unnecessary domain from generic skills
                if refined_name:
                    cleaned_name = self._strip_unnecessary_domain(refined_name)
                    if cleaned_name != refined_name:
                        logger.debug(f"Domain stripped: '{refined_name}' → '{cleaned_name}'")
                        refined_name = cleaned_name
                
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
        
        # ═══════════════════════════════════════════════════════════
        #  STAGE 2: LLM domain validation
        #  For skills that Stage 1 (deterministic strip) didn't catch,
        #  ask the LLM if the domain qualifier is necessary.
        # ═══════════════════════════════════════════════════════════
        if self.genai_interface:
            skills_for_llm_check = []
            for idx in df_result.index:
                current_name = str(df_result.loc[idx, name_column])
                if self._needs_llm_domain_check(current_name):
                    skills_for_llm_check.append({
                        'index': idx,
                        'refined_name': current_name,
                        'description': str(df_result.loc[idx, description_column]) if description_column in df_result.columns else '',
                    })
            
            if skills_for_llm_check:
                logger.info(f"Stage 2: {len(skills_for_llm_check)} skills need LLM domain validation")
                llm_results = self._validate_domain_batch(skills_for_llm_check)
                
                llm_stripped = 0
                for result in llm_results:
                    idx = result['index']
                    cleaned = result['cleaned_name']
                    original_refined = result['original_refined']
                    
                    if cleaned != original_refined and idx in df_result.index:
                        df_result.loc[idx, name_column] = cleaned
                        llm_stripped += 1
                
                logger.info(f"Stage 2: LLM stripped domain from {llm_stripped} additional skills")
            else:
                logger.info("Stage 2: No skills need LLM domain validation")
        
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