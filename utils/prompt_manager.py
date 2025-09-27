"""
Centralized prompt management for consistent prompts across all backends
"""

from typing import Dict, List, Optional, Tuple
from models.enums import StudyLevel


class PromptManager:
    """Manages all prompts for the system to ensure consistency across backends"""
    
    @staticmethod
    def get_skill_extraction_prompt(
        text: str,
        item_type: str,
        study_level: Optional[str] = None,
        backend_type: str = "standard",
        max_text_length: Optional[int] = None
    ) -> Tuple[str, str]:
        """
        Get skill extraction prompt
        
        Args:
            text: Text to analyze
            item_type: Type of item (vet/uni)
            study_level: Study level if known
            backend_type: Backend type for optimization (not for different prompts!)
            max_text_length: Maximum text length to include
            
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        
        # Determine text length based on backend (for performance only)
        if max_text_length is None:
            max_text_length = 2000 if backend_type == "vllm" else 3000
        
        # System prompt - SAME for all backends
        system_prompt = """You are an expert skill extractor specializing in educational competency analysis. 
Extract skills accurately, comprehensively, and calibrated to the appropriate study level.
Always return valid JSON arrays."""
        
        # Build study level guidance if provided
        level_guidance = ""
        if study_level:
            study_enum = StudyLevel.from_string(study_level)
            expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
            
            level_guidance = f"""
            Study Level Context:
            - This is a {study_level} level {item_type}
            - Expected skill levels: {expected_min}-{expected_max}
            - Level definitions:
            * Level 1: Novice (basic awareness, requires supervision)
            * Level 2: Advanced Beginner (limited experience, occasional supervision)
            * Level 3: Competent (can perform independently)
            * Level 4: Proficient (advanced application, can supervise others)
            * Level 5: Expert (mastery, can teach/innovate)
            """
        
        # User prompt - SAME for all backends
        user_prompt = f"""Analyze this {item_type} text and extract ALL skills.
            {level_guidance}
            Task Requirements:
            1. Extract both explicit skills (directly stated) and implicit skills (required but not stated)
            2. Decompose composite skills into component skills
            3. Remove duplicate or redundant skills
            4. Consider prerequisites and assessment methods

            For EACH skill, provide these fields:
            - name: Clear, concise skill name (3-50 characters)
            - category: One of [technical, cognitive, practical, foundational, professional]
            - level: Integer 1-5 (calibrated to study level if provided)
            - context: One of [theoretical, practical, hybrid]
            - confidence: Float 0.0-1.0 (your confidence in this extraction)
            - is_explicit: Boolean (true if directly stated, false if inferred)
            - keywords: Array of 3-5 relevant keywords

            Output Format: Return ONLY a valid JSON array of skill objects, no additional text.
            """+"""
            Example Output:
            [
            {
                "name": "Database Design",
                "category": "technical",
                "level": 3,
                "context": "hybrid",
                "confidence": 0.9,
                "is_explicit": true,
                "keywords": ["SQL", "normalization", "ERD", "schemas"]
            }
            ]
            """+f"""
            Text to Analyze:
            {text}

            Return JSON array:"""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def get_batch_extraction_prompt(
        texts: List[str],
        item_type: str,
        study_levels: List[Optional[str]] = None,
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Get batch extraction prompt
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        
        # System prompt - SAME for all backends
        system_prompt = """You are an expert skill extractor specializing in educational competency analysis.
Process multiple texts and extract skills from each, maintaining consistency across all extractions.
Always return valid JSON."""
        
        # Build batch prompt
        batch_items = []
        for idx, text in enumerate(texts):
            study_level = study_levels[idx] if study_levels and idx < len(study_levels) else None
            
            # Add study level info if available
            level_info = ""
            if study_level:
                study_enum = StudyLevel.from_string(study_level)
                expected_min, expected_max = StudyLevel.get_expected_skill_level_range(study_enum)
                level_info = f"Study Level: {study_level} (expect skill levels {expected_min}-{expected_max})\n"
            
            # Limit text length for batch processing
            max_length = 1500 if backend_type == "vllm" else 2000
            
            batch_items.append(f"""
=== Text {idx} ===
{level_info}Type: {item_type}
Content: {text[:max_length]}
""")
        
        # User prompt - SAME for all backends
        user_prompt = f"""Analyze these {len(texts)} texts and extract skills from EACH one.

        Requirements for EACH text:
        1. Extract explicit and implicit skills
        2. Decompose composite skills
        3. Remove duplicates within each text
        4. Calibrate skill levels to the study level if provided

        For EACH skill: name, category (technical/cognitive/practical/foundational/professional), 
        level (1-5), context (theoretical/practical/hybrid), confidence (0-1), 
        is_explicit (true/false), keywords (3-5 words).
        """+"""
        Output Format: JSON array with one object per text, each containing a "skills" array:
        [
        {{"text_index": 0, "skills": [...]}}, 
        {{"text_index": 1, "skills": [...]}}
        ]

        Texts to Analyze:
        {"".join(batch_items)}

        Return JSON array:"""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def get_study_level_inference_prompt(
        text: str,
        item_type: str,
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Get prompt for inferring study level
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        
        # System prompt - SAME for all backends
        system_prompt = """You are an expert education level classifier.
            Analyze educational content and accurately determine its study level.
            Be precise and consider complexity, prerequisites, and learning outcomes."""
                    
                    # Text length based on backend
        max_length = 1000 if backend_type == "vllm" else 1500
        
        # User prompt - SAME for all backends
        user_prompt = f"""Analyze this {item_type.upper()} Course text and determine the study level.

            Classification Criteria:
            - Introductory: Basic concepts, foundational knowledge, beginner-friendly, no prerequisites
            - Intermediate: Standard complexity, some prerequisites, builds on basics, practical application
            - Advanced: Complex topics, significant prerequisites, specialized knowledge, research/innovation

            Key Indicators to Consider:
            1. Complexity of concepts
            2. Prerequisites mentioned
            3. Learning outcomes level
            4. Assessment methods
            5. Target audience
            6. Depth of coverage

            Text to Analyze:
            {text}

            Respond with ONLY ONE WORD: Introductory, Intermediate, or Advanced"""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def get_skill_comparison_prompt(
        vet_skills: List[str],
        uni_skills: List[str],
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Get prompt for comparing skills (used in refinement)
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        
        # System prompt - SAME for all backends
        system_prompt = """You are an expert at skill comparison and alignment assessment.
Evaluate skill alignments accurately considering coverage, level appropriateness, and practical relevance."""
        
        # Limit skills for prompt
        max_skills = 50 if backend_type == "vllm" else 50
        
        # User prompt - SAME for all backends  
        user_prompt = f"""Compare these skill sets and rate their alignment.

        VET Skills:
        {', '.join(vet_skills[:max_skills])}

        University Skills:
        {', '.join(uni_skills[:max_skills])}

        Evaluation Criteria:
        1. Coverage: What percentage of university skills are covered by VET skills?
        2. Level Match: Are the skill levels appropriate?
        3. Practical Relevance: Do VET skills provide practical foundation for university requirements?

        Provide alignment score as a single decimal number between 0.0 and 1.0.
        Consider: 0.8+ = excellent alignment, 0.6-0.8 = good alignment, 0.4-0.6 = partial alignment, <0.4 = poor alignment

        Return ONLY the decimal number (e.g., 0.75):"""
        
        return system_prompt, user_prompt
    
    @staticmethod
    def get_composite_skill_decomposition_prompt(
        skill_name: str,
        context: str = "",
        backend_type: str = "standard"
    ) -> Tuple[str, str]:
        """
        Get prompt for decomposing composite skills
        
        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        
        # System prompt - SAME for all backends
        system_prompt = """You are an expert at skill decomposition and competency analysis.
Break down complex skills into their constituent components accurately."""
        
        # User prompt - SAME for all backends
        user_prompt = f"""Decompose this composite skill into component skills.

        Composite Skill: {skill_name}
        Context: {context if context else "General educational context"}
        """+"""
        Requirements:
        1. Identify 3-7 component skills that make up this composite skill
        2. Each component should be a distinct, assessable skill
        3. Components should collectively cover the composite skill

        For each component skill provide:
        - name: Clear component skill name
        - category: technical/cognitive/practical/foundational/professional
        - importance: high/medium/low (relative to the composite skill)

        Return as JSON array:
        [
        {{"name": "...", "category": "...", "importance": "..."}}
        ]

        Return JSON array:"""
        
        return system_prompt, user_prompt