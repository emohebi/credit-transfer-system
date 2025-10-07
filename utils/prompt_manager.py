"""
Enhanced Prompt Manager using Chain-of-Thought for Human Capability Extraction
"""

from typing import Dict, List, Optional, Tuple, Any
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
  * "Excel" → "spreadsheet analysis"
  * "Python" → "Python programming"
  * "AutoCAD" → "technical drawing"
  * "SAP" → "ERP implementation"
- Add specific context to generic skills:
  * "communication" → "technical writing" or "client consultation"
  * "teamwork" → "cross-functional collaboration" or "agile coordination"
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

### CRITICAL Skill Naming Convention:
- **Use NATURAL, PROFESSIONAL terminology with sufficient context**
- **MUST BE 2-4 WORDS MAXIMUM**
- **Match existing taxonomies**: ESCO, O*NET, SFIA, job postings
- **Remove unnecessary qualifiers and redundant descriptors**
- Follow the pattern: [Action/Process] + [Domain/Context] + [Object/Outcome]
- **Optimal length is 2-4 words**: Provide enough context while maintaining clarity

Examples of PROPER skill naming (2-4 words):
- "financial data analysis" (NOT "comprehensive financial data analysis and modeling")
- "stakeholder engagement management" (NOT "multi-stakeholder engagement and communication management")
- "business process optimization" (NOT "enterprise-wide business process optimization and improvement")
- "enterprise risk assessment" (NOT "comprehensive enterprise risk identification and assessment")
- "project management" (NOT "end-to-end project lifecycle management")
- "database design" (NOT "relational database design and modeling")
"""

        # Skill categories with human capability focus
        skill_categories = """
## Skill Categories (Human Capabilities):

### COGNITIVE/ANALYTICAL CAPABILITIES:
Pattern: [Analytical Process] + [Domain] (2-4 words optimal)
- "quantitative data analysis"
- "pattern recognition"

### TECHNICAL CAPABILITIES:
Pattern: [Technical Action] + [Technology Context] (2-4 words optimal)
- "AI algorithm development"
- "API design integration"

### COMMUNICATION CAPABILITIES:
Pattern: [Communication Type] + [Purpose] (2-4 words optimal)
- "cross-cultural business communication"
- "scientific report writing"

### MANAGEMENT CAPABILITIES:
Pattern: [Management Function] + [Domain] (2-4 words optimal)
- "project management"
- "vendor relationship management"

### CREATIVE/DESIGN CAPABILITIES:
Pattern: [Creative Process] + [Output] (2-4 words optimal)
- "user experience design"
- "innovative solution design"
"""

        # Translation examples
        translation_examples = """
## Translation Examples (KEEP NAMES 2-4 WORDS):

WHEN TEXT SAYS → EXTRACT AS (2-4 words):

"Use Excel for financial reports"
→ "spreadsheet financial analysis"

"Work in teams on projects"
→ "cross-functional team collaboration"

"Communicate with stakeholders"
→ "stakeholder expectation alignment"

"Manage customer relationships"
→ "customer relationship management"

"Implement software solutions"
→ "software solution architecture"

"Analyze business processes"
→ "business process analysis"

## Optimal Length Examples:
- "strategic business planning" (3 words) ✓
- "financial data analysis" (3 words) ✓
- "cross-functional team collaboration" (3 words) ✓
- "comprehensive risk assessment" → "risk assessment planning" (3 words) ✓
- "budget compliance monitoring" (3 words) ✓
"""

        # Level calibration based on Bloom's taxonomy
        if study_level:
            study_enum = StudyLevel.from_string(study_level)
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
            
            level_rules = f"""
        ## SFIA Level Assignment:
            For each skill, assign a SFIA level (1-7) based on the following attributes, make sure to think twice before assigning a level:
        ### SFIA Level Definitions:
        - **Level 1 (Follow)**: Works under close supervision, follows instructions, performs routine tasks
        - **Level 2 (Assist)**: Provides assistance, works under routine supervision, uses limited discretion  
        - **Level 3 (Apply)**: Performs varied tasks, works under general direction, exercises discretion
        - **Level 4 (Enable)**: Performs diverse complex activities, guides others, works autonomously
        - **Level 5 (Ensure/Advise)**: Provides authoritative guidance, accountable for significant outcomes
        - **Level 6 (Initiate/Influence)**: Has significant organizational influence, makes high-level decisions
        - **Level 7 (Set Strategy)**: Operates at highest level, determines vision and strategy

        ### Level Assessment Examples (with 2-4 word skill names):

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

        ### For {study_level} study level:
        - Expected Target SFIA levels: {expected_min}-{expected_max}
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
5. **CRITICAL: Keep skill names to 2-4 words for optimal context but make sure the skill names are aligned with other existing taxonomies**
6. Ensure each skill follows the naming convention: [Action/Process] + [Domain/Context] + [Object/Outcome]
7. Validate that each skill represents a transferable human capability

## OUTPUT REQUIREMENTS:
Output maximum 15 high quality distinct skills or human capabilities in JSON format.

Each skill must:
- Represent a human ability (not a tool or task)
- Include specific context
- **BE 2-4 WORDS OPTIMAL** (provide sufficient context)
- Follow the naming convention if possible
- Be transferable across roles
- Align with educational taxonomies is a MUST
- Make sure to assign an appropriate SFIA level (1-7) based on the provided guidelines, do not output levels outside the expected range for the given study level
"""+"""
JSON FORMAT:
[
  {
    "name": "financial data analysis",  // Human capability with context (2-4 WORDS OPTIMAL)
    "category": "analytical",  // cognitive/technical/communication/management/creative
    "level": """+f"""{int((expected_min + expected_max) / 2) if study_level else 3}"""+""",  // SFIA level (1-7)
    "context": "practical",  // theoretical/practical/hybrid
    "confidence": 0.7,  // Extraction confidence
    "evidence": "...",  // The exact unmodified text in the input showing this capability (max 200 chars)
    "translation_rationale": "Excel reports → financial data analysis capability"  // How you derived this
  }
]

Remember: Focus on HUMAN CAPABILITIES, not tools or generic terms! Keep names at 2-4 words for optimal context!

Return ONLY the JSON array:"""

        return system_prompt, user_prompt
    
    @staticmethod
    def get_skill_keywords_prompt(
        skills_with_evidence: List[Dict[str, Any]],
        context_type: str = "VET",
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Generate relevant keywords for skills based on their evidence and context
        """
        
        system_prompt = """You are an expert at identifying relevant keywords for professional skills and capabilities.
        Your task is to generate 3-5 highly relevant keywords for each skill based on the skill name, evidence, and context.

        Keywords should:
        - Be specific and relevant to the skill
        - Include related tools, technologies, methods, and concepts
        - Help with searching and matching similar skills
        - Not be redundant with the skill name itself
        - Include both specific terms and broader domain terms

        Categories of keywords to consider:
        1. Domain terms (e.g., finance, healthcare, engineering)
        2. Tools/technologies (e.g., Excel, Python, AutoCAD)
        3. Methods/approaches (e.g., analysis, optimization, agile)
        4. Industry terms (e.g., compliance, governance, audit)
        5. Related concepts (e.g., for "data analysis": statistics, visualization, reporting)"""

        user_prompt = f"""Generate relevant keywords for these {context_type} skills based on their evidence and context.

        ## Skills to Generate Keywords For:
        """
            
        for idx, skill in enumerate(skills_with_evidence[:50]):  # Limit to 50 for token efficiency
            skill_name = skill.get('name', '')
            evidence = skill.get('evidence', '')
            category = skill.get('category', '')
            level = skill.get('level', 3)
            context = skill.get('context', 'practical')
            
            user_prompt += f"""
            ### Skill {idx + 1}:
            - Name: {skill_name}
            - Category: {category}
            - Level: {level}
            - Context: {context}
            - Evidence: {evidence[:150]}
            """

        user_prompt += """

        ## Keyword Generation Guidelines:
        1. Extract key terms from the evidence that relate to the skill
        2. Add domain-specific terminology
        3. Include tools or technologies mentioned or implied
        4. Add broader category terms for better matching
        5. Include both specific and general terms

        ## Examples:
        - "financial data analysis" → ["finance", "accounting", "spreadsheet", "Excel", "reporting", "budgeting", "quantitative", "metrics", "dashboard"]
        - "project lifecycle management" → ["project", "planning", "agile", "scrum", "timeline", "milestones", "resources", "coordination", "delivery"]
        - "database design optimization" → ["SQL", "database", "schema", "performance", "indexing", "queries", "normalization", "data modeling", "optimization"]

        ## Output Format:
        Return a JSON array with keywords for each skill:
        [
        {
            "skill_index": 0,
            "name": "skill name",
            "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
        }
        ]

        Return ONLY the JSON array with 3-5 keywords per skill:"""

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
   - "financial analysis" = "financial analytics"
   - "project management" = "project lifecycle management"

2. **Overlapping Capabilities (0.7)**:
   - Related abilities with shared competencies
   - "spreadsheet analysis" overlaps with "quantitative analysis"
   - "technical writing" overlaps with "technical communication"

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
- **KEEP SKILL NAMES TO 3-4 WORDS OPTIMAL**
- Use pattern: [Action/Process] + [Domain/Context] + [Object/Outcome]
- Focus on transferable capabilities

## Key Translations (3-4 WORD NAMES):
- Tools → Underlying human skills (3-4 words)
- Tasks → Required capabilities (3-4 words)
- Generic terms → Contextualized abilities (3-4 words)

Examples of PROPER naming:
- "comprehensive risk assessment" (3 words)
- "quantitative data analysis" (3 words) 
- "project lifecycle management" (3 words)

For each text, extract 5-20 human capabilities with:
- name: Contextualized human capability (3-4 WORDS OPTIMAL)
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

Apply the chain-of-thought process to each text to extract true HUMAN CAPABILITIES with optimal names (3-4 words)!"""
        
        return system_prompt, user_prompt

    @staticmethod
    def get_study_level_inference_prompt(
        text: str,
        item_type: str,
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Infer study level based on cognitive complexity with better calibration
        """
        
        system_prompt = """You are an educational taxonomy expert who classifies study levels based on cognitive complexity and prerequisite assumptions. You must be conservative and precise in your classification, avoiding bias toward higher levels."""
        
        user_prompt = f"""Analyze the cognitive complexity and prerequisite assumptions in this {item_type}.

    ## TEXT TO ANALYZE:
    {text}

    ## CLASSIFICATION CRITERIA (MUST meet majority of indicators):

    **INTRODUCTORY** (DEFAULT if uncertain) - Foundation level:
    STRONG INDICATORS:
    - Words: "introduction", "basic", "fundamental", "overview", "foundation", "elementary", "beginning"
    - Verbs: identify, define, list, describe, explain, summarize, recall, recognize
    - Phrases: "no prerequisites", "assumes no prior knowledge", "first exposure", "getting started"
    - Content: Basic concepts, terminology, simple procedures, guided practice
    - Assessment: Multiple choice, definitions, simple calculations, guided exercises
    - Course codes: 100-level, 1000-level, first-year, entry-level

    DISQUALIFIERS for Introductory:
    - Any mention of "advanced", "complex analysis", "critical evaluation"
    - Prerequisites beyond basic math/English
    - Research or independent project requirements

    **INTERMEDIATE** - Building competence:
    STRONG INDICATORS:
    - Words: "develop", "apply", "analyze", "examine", "integrate"  
    - Verbs: apply, analyze, compare, differentiate, organize, relate, compute
    - Phrases: "builds on introductory", "some experience required", "working knowledge"
    - Content: Application of theories, standard problem-solving, case studies
    - Assessment: Problem sets, reports, group projects, practical applications
    - Course codes: 200-300 level, 2000-3000 level, second/third year

    DISQUALIFIERS for Intermediate:
    - Words like "mastery", "expertise", "research", "thesis"
    - Highly specialized or niche topics
    - Assumption of professional experience

    **ADVANCED** - High expertise (ONLY if clear evidence):
    STRONG INDICATORS:
    - Words: "advanced", "complex", "critical", "research", "specialized", "expert"
    - Verbs: evaluate, create, design, critique, synthesize, theorize, innovate
    - Phrases: "extensive prerequisites", "assumes strong background", "professional level"
    - Content: Original research, complex synthesis, cutting-edge topics, independent work
    - Assessment: Thesis, dissertation, original projects, peer review, publication
    - Course codes: 400+ level, 4000+ level, graduate, postgraduate, final year

    REQUIRED for Advanced:
    - MUST have at least 3 strong indicators
    - MUST mention complex prerequisites or assumed knowledge
    - MUST involve creation/evaluation level work

    ## DECISION RULES:
    1. Count indicators for each level
    2. If unclear or mixed signals → choose INTERMEDIATE
    3. If basic/introductory indicators ≥ advanced indicators → choose INTRODUCTORY
    4. Only choose ADVANCED if overwhelming evidence (>60% advanced indicators)
    5. When in doubt, choose the LOWER level

    ## Based on the evidence, classify as:
    - If mostly basic concepts and foundational skills → Introductory
    - If building on basics with application focus → Intermediate  
    - If ONLY if clear research/expert focus → Advanced

    Return ONLY ONE WORD (Introductory/Intermediate/Advanced):"""
        
        return system_prompt, user_prompt
        
    @staticmethod
    def get_skill_description_prompt(
        skills_with_evidence: List[Dict[str, Any]],
        context_type: str = "VET",
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Generate detailed descriptions for skills based on their evidence and context
        """
        
        system_prompt = """You are an expert at creating concise, context-aware descriptions for professional skills and capabilities. 
    Your task is to generate clear, actionable descriptions that explain HOW each skill is applied in practice, based on the evidence provided.

    Each description should:
    - Be 1 sentences (max 10-15 words)
    - Explain the practical application of the skill
    - Connect to the specific context shown in the evidence
    - Use active voice and professional language
    - Avoid generic or vague descriptions"""

        user_prompt = f"""Generate practical descriptions for these {context_type} skills based on their evidence.

    ## Skills to Describe:
    """
        
        for idx, skill in enumerate(skills_with_evidence):  # Limit to 20 for token efficiency
            skill_name = skill.get('name', '')
            evidence = skill.get('evidence', '')
            category = skill.get('category', '')
            level = skill.get('level', 3)
            context = skill.get('context', 'practical')
            
            user_prompt += f"""
            ### Skill {idx + 1}:
            - Name: {skill_name}
            - Category: {category}
            - Level: {level}
            - Context: {context}
            - Evidence: {evidence[:150]}
            """

        user_prompt += """

        ## Description Guidelines:
        1. Focus on WHAT the person does and HOW they apply this skill
        2. Reference the specific context from the evidence
        3. Match the complexity to the skill level
        4. Make it actionable and measurable where possible

        ## Examples:
        - "financial data analysis" with evidence about Excel reports → "Analyzes financial datasets using spreadsheet tools to identify trends and create reports for business decision-making"
        - "stakeholder communication" with evidence about meetings → "Facilitates clear communication with internal and external stakeholders through presentations, meetings, and written updates"
        - "project planning" with evidence about timelines → "Develops and maintains project schedules, milestones, and resource allocations to ensure timely delivery"

        ## Output Format:
        Return a JSON array with descriptions for each skill:
        [
        {
            "skill_index": 0,
            "name": "skill name",
            "description": "Practical description of how this skill is applied..."
        }
        ]

        Return ONLY the JSON array:"""

        return system_prompt, user_prompt
