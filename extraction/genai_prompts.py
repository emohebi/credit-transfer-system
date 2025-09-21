"""
Centralized Gen AI prompts for skill extraction and analysis
All prompts designed for consistent, deterministic output with temperature=0
"""

class GenAIPrompts:
    """Collection of structured prompts for Gen AI-based extraction"""
    
    @staticmethod
    def skill_extraction_prompt():
        """Main skill extraction prompt"""
        return """You are an expert in educational course analysis and skill extraction. Analyze the provided text and extract ALL identifiable skills.

IMPORTANT INSTRUCTIONS:
1. Extract skills as generalizable human capabilities, not task descriptions
2. If a tool/technology is mentioned, extract the human ability (e.g., "Excel" → "spreadsheet data analysis")
3. Be comprehensive - extract explicit AND implicit skills
4. Maintain consistency - similar skills should be named identically
5. Return ONLY valid JSON, no additional text

For each skill provide:
- name: Concise skill name (3-50 characters)
- category: One of [technical, cognitive, practical, foundational, professional]
- level: One of [novice, beginner, competent, proficient, expert]
- context: One of [theoretical, practical, hybrid]
- keywords: List of 3-10 relevant keywords
- confidence: Score 0.0-1.0
- evidence: Brief text showing where skill was found

OUTPUT FORMAT (strict JSON):
{
  "skills": [
    {
      "name": "skill name",
      "category": "category",
      "level": "level",
      "context": "context", 
      "keywords": ["keyword1", "keyword2"],
      "confidence": 0.8,
      "evidence": "text excerpt"
    }
  ]
}"""

    @staticmethod
    def study_level_identification_prompt():
        """Identify study level from course description"""
        return """Analyze the course description and determine its study level based on complexity, prerequisites, and learning outcomes.

Study levels (choose exactly one):
- introductory: Foundational concepts, no prerequisites, basic understanding
- intermediate: Building on basics, some prerequisites, developing proficiency  
- advanced: Complex topics, multiple prerequisites, deep understanding
- specialized: Niche/specific focus, extensive prerequisites, expert-level
- postgraduate: Research-oriented, assumes undergraduate completion

Analyze these factors:
1. Complexity of topics
2. Prerequisites mentioned
3. Depth of learning outcomes
4. Expected prior knowledge
5. Assessment complexity

OUTPUT FORMAT (strict JSON):
{
  "study_level": "level_name",
  "confidence": 0.9,
  "indicators": ["indicator1", "indicator2"],
  "reasoning": "brief explanation"
}"""

    @staticmethod
    def skill_deduplication_prompt():
        """Deduplicate and merge similar skills"""
        return """Analyze the list of skills and identify duplicates or highly similar skills that should be merged.

RULES:
1. Skills with same meaning but different wording should be merged
2. Keep the most descriptive/accurate name
3. Combine keywords and evidence
4. Use highest confidence score
5. Consider context - "Python programming" and "Python scripting" are similar enough to merge

For each group of similar skills:
- Identify which skills are duplicates
- Suggest the best merged name
- Combine relevant properties

OUTPUT FORMAT (strict JSON):
{
  "skill_groups": [
    {
      "similar_skills": ["skill1", "skill2"],
      "merged_name": "best name",
      "merged_category": "category",
      "merged_level": "highest_level",
      "merged_keywords": ["all", "unique", "keywords"],
      "merge_confidence": 0.9
    }
  ],
  "unique_skills": ["skill3", "skill4"]
}"""

    @staticmethod
    def implicit_skill_identification_prompt():
        """Identify implicit/hidden skills"""
        return """Based on the course content and explicit skills already identified, determine what implicit skills would be required but aren't explicitly stated.

Consider:
1. Foundational skills assumed but not mentioned
2. Supporting skills needed for main skills
3. Soft skills implied by activities
4. Tool/technology skills referenced indirectly
5. Process skills required for assessments

OUTPUT FORMAT (strict JSON):
{
  "implicit_skills": [
    {
      "name": "skill name",
      "category": "category",
      "reasoning": "why this skill is implied",
      "confidence": 0.7,
      "supporting_evidence": "text that implies this"
    }
  ]
}"""

    @staticmethod
    def composite_skill_decomposition_prompt():
        """Decompose composite skills into components"""
        return """Analyze each skill and determine if it's a composite skill that should be broken down into component skills.

Composite skills are broad capabilities that encompass multiple specific skills.
Examples:
- "project management" → planning, execution, monitoring, stakeholder communication
- "web development" → HTML, CSS, JavaScript, responsive design
- "data analysis" → collection, cleaning, visualization, interpretation

For each composite skill, provide component skills with VALID categories.

VALID CATEGORIES (use ONLY these):
- technical: Programming, software, tools, technologies
- cognitive: Analysis, problem-solving, critical thinking
- practical: Hands-on implementation, operation, maintenance
- foundational: Basic principles, theories, core concepts
- professional: Communication, teamwork, leadership

OUTPUT FORMAT (strict JSON):
{
  "composite_skills": [
    {
      "original_skill": "composite skill name",
      "is_composite": true,
      "components": [
        {"name": "component skill name", "category": "technical"},
        {"name": "another component", "category": "professional"}
      ],
      "keep_original": true
    }
  ]
}

IMPORTANT: The "category" field must be one of: technical, cognitive, practical, foundational, professional"""

    @staticmethod
    def skill_level_adjustment_prompt():
        """Adjust skill levels based on context"""
        return """Analyze the skill and its context to determine the appropriate proficiency level.

Consider:
1. Study level of the course
2. Prerequisites mentioned
3. Depth of coverage indicated
4. Assessment requirements
5. Learning outcome complexity

Levels (from lowest to highest):
- novice: Basic awareness, theoretical understanding
- beginner: Can perform with guidance, learning fundamentals
- competent: Can perform independently, solid understanding
- proficient: Advanced application, can handle complex scenarios
- expert: Master level, can teach/innovate

OUTPUT FORMAT (strict JSON):
{
  "adjusted_skills": [
    {
      "skill_name": "skill",
      "original_level": "competent",
      "adjusted_level": "proficient",
      "adjustment_reason": "advanced course requires higher proficiency"
    }
  ]
}"""

    @staticmethod
    def context_determination_prompt():
        """Determine theoretical vs practical context"""
        return """Analyze the text and determine whether skills are applied in theoretical, practical, or hybrid contexts.

Theoretical indicators: concepts, principles, models, analysis, research, examination
Practical indicators: hands-on, laboratory, workshop, implementation, real-world, project
Hybrid: combination of both

OUTPUT FORMAT (strict JSON):
{
  "context_analysis": {
    "primary_context": "practical",
    "theoretical_percentage": 30,
    "practical_percentage": 70,
    "evidence": {
      "theoretical": ["found these theoretical indicators"],
      "practical": ["found these practical indicators"]
    }
  }
}"""

    @staticmethod
    def technology_version_extraction_prompt():
        """Extract technology versions and assess currency"""
        return """Identify all technologies mentioned with their versions and assess if they are current or outdated.

Look for:
1. Programming languages with versions (Python 2/3, Java 8/11/17)
2. Frameworks and their versions
3. Software tools and versions
4. Methodologies (waterfall vs agile)

Assess currency based on 2024 standards.

OUTPUT FORMAT (strict JSON):
{
  "technologies": [
    {
      "name": "Python",
      "version": "3.11",
      "is_current": true,
      "recommended_version": "3.11+",
      "update_priority": "none"
    },
    {
      "name": "Java",
      "version": "8",
      "is_current": false,
      "recommended_version": "17 or 21",
      "update_priority": "medium"
    }
  ],
  "overall_currency": "mostly_current",
  "update_effort": "low"
}"""

    @staticmethod
    def prerequisite_analysis_prompt():
        """Analyze prerequisites and dependencies"""
        return """Analyze the prerequisites mentioned and determine what foundational skills they imply.

For each prerequisite:
1. Identify the implied skills
2. Determine the minimum proficiency level needed
3. Assess criticality for the course

OUTPUT FORMAT (strict JSON):
{
  "prerequisites": [
    {
      "prerequisite": "COMP1500",
      "implied_skills": [
        {"name": "basic programming", "level": "competent"},
        {"name": "algorithm design", "level": "beginner"}
      ],
      "criticality": "essential"
    }
  ],
  "missing_prerequisite_risk": "low"
}"""

    @staticmethod
    def skill_similarity_prompt():
        """Assess similarity between two skills"""
        return """Compare these two skills and determine their similarity.

Consider:
1. Semantic meaning similarity
2. Required knowledge overlap
3. Application context similarity
4. Transferability between skills

Provide a similarity score from 0.0 (completely different) to 1.0 (identical).

OUTPUT FORMAT (strict JSON):
{
  "similarity_score": 0.85,
  "similar_aspects": ["both involve programming", "similar complexity"],
  "different_aspects": ["different languages", "different domains"],
  "transferability": "high"
}"""

    @staticmethod
    def edge_case_detection_prompt():
        """Detect edge cases in credit mapping"""
        return """Analyze the VET and University course mapping for potential edge cases and special considerations.

Look for:
1. Significant context imbalance (practical vs theoretical)
2. Technology version mismatches
3. Composite skills that need decomposition
4. Missing prerequisites
5. Credit hour mismatches
6. Multiple units mapping to single course
7. Outdated content requiring updates

OUTPUT FORMAT (strict JSON):
{
  "edge_cases": [
    {
      "type": "context_imbalance",
      "severity": "medium",
      "description": "VET is 80% practical, Uni course is 70% theoretical",
      "recommendation": "Add theoretical bridging content"
    }
  ],
  "overall_risk": "low",
  "requires_manual_review": false
}"""

    @staticmethod
    def keyword_extraction_prompt():
        """Extract relevant keywords for a skill"""
        return """Extract 5-10 highly relevant keywords for the given skill based on the context provided.

Keywords should be:
1. Specific and relevant to the skill
2. Include related tools, technologies, concepts
3. Useful for searching and matching
4. Not redundant with the skill name itself

OUTPUT FORMAT (strict JSON):
{
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "primary_domain": "software development"
}"""

    @staticmethod
    def assessment_type_analysis_prompt():
        """Analyze assessment methods to understand skill context"""
        return """Analyze the assessment description to understand how skills are evaluated.

Identify:
1. Assessment types (exam, project, practical, presentation)
2. Skill application context (theoretical vs practical)
3. Complexity level indicated by assessment
4. Skills emphasized by assessment method

OUTPUT FORMAT (strict JSON):
{
  "assessment_types": [
    {
      "type": "project",
      "weight": "40%",
      "context": "practical",
      "skills_assessed": ["implementation", "design", "testing"]
    }
  ],
  "primary_assessment_context": "practical",
  "complexity_indicator": "advanced"
}"""
    
    @staticmethod
    def skill_categorization_prompt():
        """Categorize a skill into appropriate category"""
        return """Categorize the given skill into the most appropriate category.

Categories:
- technical: Programming, software, tools, technologies, engineering
- cognitive: Analysis, problem-solving, critical thinking, evaluation
- practical: Hands-on implementation, operation, maintenance
- foundational: Basic principles, theories, core concepts
- professional: Communication, teamwork, leadership, project management

Consider the skill's primary nature and application.

OUTPUT FORMAT (strict JSON):
{
  "skill_name": "skill",
  "category": "technical",
  "confidence": 0.9,
  "reasoning": "involves programming and software development"
}"""