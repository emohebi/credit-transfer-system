"""
Enhanced Prompt Manager using Chain-of-Thought for Human Capability Extraction
"""

from typing import Dict, List, Optional, Tuple
from models.enums import StudyLevel, SkillLevel
import json


class PromptManager:
    """Manages prompts for extracting human capabilities from competency descriptions"""
    
    @staticmethod
    def get_skill_extraction_prompt(
        text: str,
        item_type: str,
        study_level: Optional[str] = None,
        backend_type: str = "standard",
        max_text_length: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Get chain-of-thought skill extraction prompt for human capabilities
        """
        
        if max_text_length is None:
            max_text_length = 2000 if backend_type == "vllm" else 3000
        
        # System prompt establishing the expert role
        system_prompt = """You are a skill extraction expert specializing in identifying human capabilities implied in unit of competency (UOC) descriptions. Your task is to analyze the given unit of competency description and extract skills that represent human abilities rather than just keywords or tools.

Your expertise includes understanding educational taxonomies (Bloom's, Australian Qualifications Framework, European Qualifications Framework) and translating competency statements into standardized human capabilities."""

        # Chain of thought process
        chain_of_thought = """
## Chain of Thought Process:

1. **Read and Analyze**: Carefully read the entire UOC/course description
2. **Identify Context**: Look for tasks, responsibilities, and requirements that imply human abilities
3. **Tool-to-Skill Translation**: Convert tool/technology mentions into the underlying human skills required
4. **Contextualize Generic Terms**: Add specific context to broad terms
5. **Standardize Language**: Ensure skills align with established VET and Higher Education taxonomies
6. **Create Variations**: Consider both specific and broader versions for comprehensive coverage

## Extraction Guidelines:

### DO Extract:
- Skills that represent **human abilities** and **cognitive processes**
- Convert tools/technologies to underlying skills:
  * "Excel" → "spreadsheet data analysis and modeling"
  * "Python" → "algorithmic problem solving using Python"
  * "AutoCAD" → "technical drawing and 3D modeling"
  * "SAP" → "enterprise resource planning implementation"
- Add specific context to generic skills:
  * "communication" → "technical report writing" or "client consultation facilitation"
  * "teamwork" → "cross-functional project collaboration" or "agile team coordination"
  * "problem-solving" → "root cause analysis" or "systems troubleshooting"
- Use standardized terminology from educational frameworks:
  * Bloom's cognitive domains: analyzing, evaluating, creating
  * AQF descriptors: application, analysis, synthesis
- Focus on transferable skills applicable across roles
- Include both technical and soft skills with proper context

### DON'T Extract:
- Bare tool names without skill context (just "Excel" or "Python")
- Vague, uncontextualized skills ("communication," "teamwork")
- Company-specific processes that aren't transferable
- Personality traits or attitudes ("motivated," "enthusiastic")
- Task descriptions ("complete reports," "attend meetings")

### Skill Naming Convention:
Follow the pattern: [Action/Process] + [Domain/Context] + [Object/Outcome]

Examples of PROPER skill naming:
- "financial data analysis" (action + domain + object)
- "cross-functional team coordination" (context + object + action)
- "regulatory compliance assessment" (domain + object + action)
- "statistical model development" (domain + object + action)
- "stakeholder requirements elicitation" (context + object + action)
- "quality assurance process design" (domain + process + action)
"""

        # Skill categories with human capability focus
        skill_categories = """
## Skill Categories (Human Capabilities):

### COGNITIVE/ANALYTICAL CAPABILITIES:
Pattern: [Analytical Process] + [Domain]
- "quantitative data analysis"
- "systems thinking and analysis"
- "critical evaluation of evidence"
- "pattern recognition and interpretation"
- "strategic problem decomposition"
- "conceptual model development"
- "hypothesis testing and validation"

### TECHNICAL CAPABILITIES:
Pattern: [Technical Action] + [Technology Context] + [Purpose]
- "database design and optimization"
- "algorithm development and implementation"
- "software architecture planning"
- "network infrastructure configuration"
- "automated testing framework development"
- "data pipeline engineering"
- "API design and integration"

### COMMUNICATION CAPABILITIES:
Pattern: [Communication Type] + [Audience/Purpose]
- "technical documentation authoring"
- "stakeholder presentation delivery"
- "cross-cultural business communication"
- "scientific report writing"
- "executive briefing preparation"
- "instructional content development"
- "conflict mediation and resolution"

### MANAGEMENT CAPABILITIES:
Pattern: [Management Function] + [Scope/Domain]
- "project lifecycle management"
- "resource allocation optimization"
- "risk identification and mitigation"
- "performance metrics development"
- "change management facilitation"
- "strategic planning and execution"
- "vendor relationship management"

### CREATIVE/DESIGN CAPABILITIES:
Pattern: [Creative Process] + [Domain/Output]
- "user experience research and design"
- "visual communication design"
- "innovative solution generation"
- "prototype development and testing"
- "creative problem formulation"
- "design thinking facilitation"
"""

        # Translation examples
        translation_examples = """
## Translation Examples:

WHEN TEXT SAYS → EXTRACT AS:

"Use Excel for financial reports"
→ "spreadsheet-based financial analysis"
→ "financial data visualization"
→ "financial reporting automation"

"Work in teams on projects"
→ "collaborative project execution"
→ "cross-functional team coordination"
→ "team-based problem solving"

"Communicate with stakeholders"
→ "stakeholder engagement management"
→ "business requirements communication"
→ "stakeholder expectation alignment"

"Manage customer relationships"
→ "customer relationship cultivation"
→ "client needs assessment"
→ "customer satisfaction optimization"

"Implement software solutions"
→ "software solution architecture"
→ "technical implementation planning"
→ "systems integration management"

"Analyze business processes"
→ "business process optimization"
→ "operational efficiency analysis"
→ "workflow improvement identification"
"""

        # Level calibration based on Bloom's taxonomy
        if study_level:
            study_enum = StudyLevel.from_string(study_level)
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
            
            level_rules = f"""
        ## SFIA Level Assignment:

        ### SFIA Level Definitions:
        - **Level 1 (Follow)**: Works under close supervision, follows instructions, performs routine tasks
        - **Level 2 (Assist)**: Provides assistance, works under routine supervision, uses limited discretion  
        - **Level 3 (Apply)**: Performs varied tasks, works under general direction, exercises discretion
        - **Level 4 (Enable)**: Performs diverse complex activities, guides others, works autonomously
        - **Level 5 (Ensure/Advise)**: Provides authoritative guidance, accountable for significant outcomes
        - **Level 6 (Initiate/Influence)**: Has significant organizational influence, makes high-level decisions
        - **Level 7 (Set Strategy)**: Operates at highest level, determines vision and strategy

        Use these five attributes to determine the appropriate SFIA level for each skill:

        #### 1. AUTONOMY (Independence and Accountability)
        - **Level 1-2**: Works under close/routine supervision, seeks guidance frequently
        - **Level 3-4**: Works under general direction, exercises discretion, escalates appropriately  
        - **Level 5-6**: Works under broad direction, substantial responsibility and authority
        - **Level 7**: Full authority for significant areas, policy formation

        #### 2. INFLUENCE (Reach and Impact)
        - **Level 1-2**: Minimal influence, interacts with immediate colleagues
        - **Level 3-4**: Influences colleagues and team members, some customer contact
        - **Level 5-6**: Influences at account/senior management level, cross-functional impact
        - **Level 7**: Influences industry leaders, shapes organizational strategy

        #### 3. COMPLEXITY (Range and Intricacy)
        - **Level 1-2**: Routine tasks, simple problems with standard solutions
        - **Level 3-4**: Complex and non-routine work, moderately complex problem-solving
        - **Level 5-6**: Highly complex activities covering technical, financial, quality aspects
        - **Level 7**: Strategic complexity, formulation and implementation of strategy

        #### 4. BUSINESS SKILLS/BEHAVIOURAL FACTORS
        Assess these capabilities at each level:

        **Communication**:
        - Level 1-2: Basic information exchange
        - Level 3-4: Effective team communication, some stakeholder interaction
        - Level 5-6: Authoritative communication, influences decision-making
        - Level 7: Strategic communication, shapes organizational narrative

        **Leadership**:
        - Level 1-2: Follows direction, learns from others
        - Level 3-4: Guides individuals, supports team objectives
        - Level 5-6: Leads teams/projects, develops others
        - Level 7: Organizational leadership, inspires transformation

        **Planning**:
        - Level 1-2: Plans own immediate work
        - Level 3-4: Plans work sequences, coordinates with others
        - Level 5-6: Strategic planning, resource allocation
        - Level 7: Organizational planning, long-term strategy

        **Problem-solving**:
        - Level 1-2: Solves routine problems with guidance
        - Level 3-4: Solves complex problems independently
        - Level 5-6: Solves multifaceted problems, develops new approaches
        - Level 7: Addresses strategic challenges, creates frameworks

        #### 5. KNOWLEDGE (Depth and Breadth)
        - **Level 1-2**: Basic role-specific knowledge, learning fundamentals
        - **Level 3-4**: Working knowledge with methodical approach
        - **Level 5-6**: Deep expertise in specialization, broad business understanding
        - **Level 7**: Strategic business knowledge, industry expertise

        ### SFIA Level Determination Process:
        For each extracted skill, assess ALL FIVE generic attributes:

        1. **Analyze the capability description** for indicators of autonomy, influence, complexity, business skills, and knowledge
        2. **Map each attribute** to the appropriate SFIA level (1-7)
        3. **Determine the predominant level** across all five attributes
        4. **Validate consistency** across the skill set

        ### Level Assessment Examples:

        **"financial data analysis"**:
        - Autonomy: Level 3 (works under general direction)
        - Influence: Level 3 (influences team decisions)  
        - Complexity: Level 4 (complex analytical work)
        - Business Skills: Level 3 (effective communication of findings)
        - Knowledge: Level 4 (deep analytical knowledge)
        → **Result: Level 3-4**

        **"strategic business planning"**:
        - Autonomy: Level 6 (works under broad direction)
        - Influence: Level 6 (influences senior management)
        - Complexity: Level 6 (highly complex strategic work)
        - Business Skills: Level 6 (leadership and strategic communication)
        - Knowledge: Level 6 (broad business and strategic knowledge)
        → **Result: Level 6**

        **"routine data entry"**:
        - Autonomy: Level 1 (works under close supervision)
        - Influence: Level 1 (minimal influence)
        - Complexity: Level 1 (routine tasks)
        - Business Skills: Level 1 (basic communication)
        - Knowledge: Level 1 (basic role-specific knowledge)
        → **Result: Level 1**

        
        """

        # Final prompt construction
        user_prompt = f"""Analyze this {item_type} description and extract human capabilities using the chain-of-thought process.

{chain_of_thought}

{skill_categories}

{translation_examples}

{level_rules}

## TEXT TO ANALYZE:
{text}

## EXTRACTION STEPS:
1. Read the text and identify all mentions of tasks, tools, and responsibilities
2. For each identified element, determine the underlying human capability required
3. Translate tools/technologies into human skills
4. Add specific context to generic abilities
5. Ensure each skill follows the naming convention: [Action/Process] + [Domain/Context] + [Object/Outcome]
6. Validate that each skill represents a transferable human capability

## OUTPUT REQUIREMENTS:
Provide human capabilities in JSON format.

Each skill must:
- Represent a human ability (not a tool or task)
- Include specific context
- Follow the naming convention
- Be transferable across roles
- Align with educational taxonomies
"""+"""
JSON FORMAT:
[
  {
    "name": "financial data analysis",  // Human capability with context
    "category": "analytical",  // cognitive/technical/communication/management/creative
    "level": """+f"""{int((expected_min + expected_max) / 2) if study_level else 3}"""+""",  // SFIA level (1-7)
    "context": "practical",  // theoretical/practical/hybrid
    "confidence": 0.7,  // Extraction confidence
    "evidence": "...",  // Text excerpt showing this capability (max 100 chars)
    "translation_rationale": "Excel reports → financial data analysis capability",  // How you derived this
    "sfia_autonomy": "general_direction",  // SFIA autonomy level
    "sfia_influence": "team_level"  // SFIA influence scope
  }
]

Remember: Focus on HUMAN CAPABILITIES, not tools or generic terms!

Return ONLY the JSON array:"""

        return system_prompt, user_prompt

    @staticmethod
    def get_skill_comparison_prompt(
        vet_skills: List[str],
        uni_skills: List[str],
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Compare human capabilities between VET and University programs
        """
        
        system_prompt = """You are comparing human capabilities between educational programs.
Focus on whether the same underlying human abilities are present, considering different contexts and applications."""

        user_prompt = f"""Compare these sets of HUMAN CAPABILITIES.

VET CAPABILITIES ({len(vet_skills)} total):
{chr(10).join(f'- {skill}' for skill in vet_skills[:30])}

UNIVERSITY CAPABILITIES ({len(uni_skills)} total):
{chr(10).join(f'- {skill}' for skill in uni_skills[:30])}

## MATCHING METHODOLOGY:

1. **Identical Capabilities (1.0)**:
   - Same human ability, possibly different wording
   - "financial data analysis" = "financial analytics"
   - "project lifecycle management" = "project management"

2. **Overlapping Capabilities (0.7)**:
   - Related abilities with shared competencies
   - "spreadsheet data analysis" overlaps with "quantitative analysis"
   - "technical documentation writing" overlaps with "technical communication"

3. **Related Domain (0.4)**:
   - Same domain, different specific abilities
   - "financial modeling" related to "financial analysis"
   - "database design" related to "data management"

4. **Different Capabilities (0.0)**:
   - Unrelated human abilities

## CALCULATION:
For each university capability:
1. Find best match in VET capabilities
2. Assign score based on matching level
3. Sum all scores
4. Divide by total university capabilities

Return ONLY the final score (0.0-1.0):"""

        return system_prompt, user_prompt

    @staticmethod
    def get_batch_extraction_prompt(
        texts: List[str],
        item_type: str,
        study_levels: List[Optional[str]] = None,
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Batch extraction of human capabilities from multiple texts
        """
        
        system_prompt = """You are a skill extraction expert identifying human capabilities from multiple competency descriptions.
Apply the chain-of-thought process consistently across all texts."""
        
        user_prompt = f"""Extract HUMAN CAPABILITIES from {len(texts)} competency descriptions.

## Quick Reference:
- Extract human abilities, not tools or tasks
- Add context to generic terms
- Use pattern: [Action/Process] + [Domain/Context] + [Object/Outcome]
- Focus on transferable capabilities

## Key Translations:
- Tools → Underlying human skills
- Tasks → Required capabilities
- Generic terms → Contextualized abilities

For each text, extract 5-20 human capabilities with:
- name: Contextualized human capability
- category: cognitive/technical/communication/management/creative
- level: Based on Bloom's taxonomy (1-5)
- context: theoretical/practical/hybrid
- confidence: 0.7-1.0
- evidence: Supporting text excerpt
- translation_rationale: Brief explanation of derivation

## TEXTS TO ANALYZE:
"""
        
        for idx, text in enumerate(texts):
            study_level = study_levels[idx] if study_levels and idx < len(study_levels) else None
            level_info = f" [Study Level: {study_level}]" if study_level else ""
            
            user_prompt += f"""
=== Text {idx}{level_info} ===
{text[:1500 if backend_type == "vllm" else 2000]}
"""
        
        user_prompt += """

## OUTPUT:
Return JSON array with one object per text:
[{"text_index": 0, "skills": [...]}, {"text_index": 1, "skills": [...]}]

Apply the chain-of-thought process to each text to extract true HUMAN CAPABILITIES!"""
        
        return system_prompt, user_prompt

    @staticmethod
    def get_study_level_inference_prompt(
        text: str,
        item_type: str,
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Infer study level based on cognitive complexity of required capabilities
        """
        
        system_prompt = """You are an educational taxonomy expert who classifies study levels based on the cognitive complexity of required human capabilities."""
        
        user_prompt = f"""Analyze the cognitive complexity of capabilities in this {item_type}.

## TEXT TO ANALYZE:
{text}

## CLASSIFICATION BASED ON BLOOM'S TAXONOMY:

**INTRODUCTORY** - Lower-order cognitive capabilities:
- Remember/Understand level verbs: identify, describe, explain, list, define
- Basic application: follow procedures, apply simple rules
- Foundational knowledge: basic concepts, terminology
- Limited complexity: straightforward problems, guided tasks

**INTERMEDIATE** - Mid-level cognitive capabilities:
- Apply/Analyze level verbs: implement, examine, compare, differentiate
- Independent application: solve standard problems, analyze relationships
- Integrated knowledge: connect concepts, apply theories
- Moderate complexity: multi-step problems, some ambiguity

**ADVANCED** - Higher-order cognitive capabilities:
- Evaluate/Create level verbs: design, critique, synthesize, innovate
- Complex application: novel problems, original solutions
- Deep knowledge: critique theories, develop new approaches
- High complexity: ill-defined problems, research, innovation

## DECISION:
Based on the predominant level of cognitive capabilities required, classify as:
Introductory, Intermediate, or Advanced

Return ONLY ONE WORD:"""
        
        return system_prompt, user_prompt