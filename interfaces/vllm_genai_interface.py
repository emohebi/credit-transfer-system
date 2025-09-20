"""
Interface for local GenAI model integration using vLLM
"""

import json
import logging
import re
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
from huggingface_hub import snapshot_download
from config import Config
from vllm import LLM, SamplingParams

logger = logging.getLogger(__name__)


class VLLMGenAIInterface:
    """Interface for local GenAI model integration using vLLM"""
    
    
    def __init__(self, 
                 model_name: str = "meta-llama--Llama-3.1-8B-Instruct",
                 number_gpus: int = 1,
                 max_model_len: int = 8192,
                 model_cache_dir: str = "/root/.cache/huggingface/hub",
                 external_model_dir: str = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"):
        """
        Initialize vLLM GenAI interface
        
        Args:
            model_name: Name of the model to use from MODELS dict
            number_gpus: Number of GPUs for tensor parallelism
            max_model_len: Maximum model context length
            model_cache_dir: Directory for HuggingFace cache
            external_model_dir: Directory containing pre-downloaded models
        """
        self.MODELS = Config.MODELS
        self.model_name = model_name
        self.number_gpus = number_gpus
        self.max_model_len = max_model_len
        self.model_cache_dir = Path(model_cache_dir)
        self.external_model_dir = Path(external_model_dir)
        
        # Get model configuration
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}. Available models: {list(self.MODELS.keys())}")
        
        self.model_config = self.MODELS[model_name]
        self.template = self.model_config.get("template", "Mistral")
        
        # Initialize the model
        self.llm = None
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the vLLM model"""
        try:
            snapshot_location = self._get_snapshot_location()
            logger.info(f"Loading model from: {snapshot_location}")
            
            self.llm = LLM(
                model=snapshot_location,
                tensor_parallel_size=self.number_gpus,
                max_model_len=self.max_model_len
            )
            logger.info(f"Successfully loaded model: {self.model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise
    
    def _get_snapshot_location(self, copy_model: bool = False) -> str:
        """Get or download model snapshot location"""
        model_id = self.model_config['model_id']
        revision = self.model_config['revision']
        
        if revision:
            # Copy from external storage if available
            external_path = self.external_model_dir / f"models--{self.model_name}"
            cache_path = self.model_cache_dir / f"models--{self.model_name}"
            
            if copy_model and external_path.exists():
                try:
                    shutil.copytree(str(external_path), str(cache_path))
                    logger.info(f"Copied model from {external_path} to {cache_path}")
                except FileExistsError:
                    logger.info(f"Model already exists in cache: {cache_path}")
            
            # Download from HuggingFace
            snapshot_location = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(self.model_cache_dir)
            )
        else:
            # Local model path
            if copy_model:
                external_path = self.external_model_dir / self.model_name
                cache_path = self.model_cache_dir / self.model_name
                
                if external_path.exists():
                    try:
                        shutil.copytree(str(external_path), str(cache_path))
                        logger.info(f"Copied model from {external_path} to {cache_path}")
                    except FileExistsError:
                        logger.info(f"Model already exists in cache: {cache_path}")
                
                snapshot_location = str(cache_path)
            else:
                snapshot_location = model_id
        
        return snapshot_location
    
    def _format_instruction(self, sys_message: str, query: str) -> str:
        """Format instruction based on model template"""
        if self.template == 'Phi':
            return f'<|system|> {sys_message} <|end|><|user|> {query} <|end|><|assistant|>'
        
        elif self.template == 'Llama':
            return f'''<|begin_of_text|><|start_header_id|>system<|end_header_id|>{sys_message}<|eot_id|><|start_header_id|>user<|end_header_id|>{query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>'''
        
        elif self.template == "GPT":
            return f'''<|start|>system<|message|>{sys_message}\n\nReasoning: low\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>user<|message|>{query}<|end|><|start|>assistant'''
        
        else:  # Default Mistral format
            return f'<s> [INST] {sys_message} [/INST]\nUser: {query}\nAssistant: '
    
    def extract_skills_batch(self, texts: List[str], context: str = "course") -> List[List[Dict]]:
        """
        Extract skills from multiple texts in batch
        
        Args:
            texts: List of texts to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills for each text
        """
        sys_message = self._build_skill_extraction_prompt_system()
        
        # Format prompts for batch processing
        full_prompts = [
            self._format_instruction(
                sys_message,
                f"Now analyze the following {context}: {text}"
            ) for text in texts
        ]
        
        # Set sampling parameters
        sampling_params = SamplingParams(
            max_tokens=2048,
            temperature=0.0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
            best_of=1
        )
        
        # Generate outputs
        outputs = self.llm.generate(full_prompts, sampling_params=sampling_params)
        
        # Parse results
        results = []
        for output in outputs:
            generated_text = output.outputs[0].text
            skills = self._parse_skill_extraction_response(generated_text)
            results.append(skills)
        
        return results
    
    def extract_skills_prompt(self, text: str, context: str = "course") -> List[Dict]:
        """
        Extract skills from a single text
        
        Args:
            text: Text to extract skills from
            context: Context type (e.g., "VET unit", "university course")
            
        Returns:
            List of extracted skills as dictionaries
        """
        results = self.extract_skills_batch([text], context)
        return results[0] if results else []
    
    def _build_skill_extraction_prompt_system(self) -> str:
        """Build system prompt for skill extraction"""
        return """You are an expert in educational course analysis and skill extraction. Given a course or unit description, extract individual skills, making sure they are generalizable capabilities - not task descriptions.

        IMPORTANT: Focus on the underlying skill or ability. If a tool/technology is mentioned, extract the human ability implied by its use (e.g., "Excel" → "spreadsheet data analysis", "Python" → "Python programming").

        For each skill, identify:
        1. Skill name (concise, specific)
        2. Category (technical/cognitive/practical/foundational/professional)
        3. Required proficiency level (novice/beginner/competent/proficient/expert)
        4. Context (theoretical/practical/hybrid)
        5. Related keywords
        6. Confidence score (0-1)

        Return your answer in strict JSON format:
        [
        {
            "name": "skill name",
            "category": "category",
            "level": "proficiency level",
            "context": "context type",
            "keywords": ["keyword1", "keyword2"],
            "confidence": 0.8
        }
        ]

        Note: Only output the JSON, do not generate any extra sentences."""
    
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """
        Analyze similarity between two skills using the LLM
        
        Args:
            skill1: First skill name
            skill2: Second skill name
            
        Returns:
            Similarity score between 0 and 1
        """
        sys_message = """You are an expert in skill analysis. Analyze the similarity between two skills and return a score between 0 and 1.

        Consider:
        1. Semantic similarity
        2. Required knowledge overlap
        3. Application context similarity

        Return ONLY a number between 0 and 1, nothing else."""
        
        query = f"Skill 1: {skill1}\nSkill 2: {skill2}\n\nSimilarity score:"
        
        prompt = self._format_instruction(sys_message, query)
        
        sampling_params = SamplingParams(
            max_tokens=10,
            temperature=0.0,
            top_p=1
        )
        
        output = self.llm.generate([prompt], sampling_params=sampling_params)[0]
        response = output.outputs[0].text.strip()
        
        # Parse similarity score
        try:
            score = float(re.search(r"(\d+\.?\d*)", response).group(1))
            return min(1.0, max(0.0, score))
        except:
            return 0.5  # Default if parsing fails
    
    def identify_implicit_skills(self, text: str, explicit_skills: List[str]) -> List[Dict]:
        """
        Identify implicit skills not explicitly mentioned
        
        Args:
            text: Course/unit description text
            explicit_skills: Already identified explicit skills
            
        Returns:
            List of implicit skills with confidence scores
        """
        sys_message = """You are an expert in skill analysis. Given a course description and explicitly mentioned skills, identify implicit skills that would be required but aren't explicitly stated.

            For each implicit skill, provide:
            1. Skill name
            2. Reason for inference
            3. Confidence level (0-1)

            Return as JSON list:
            [
            {
                "name": "skill name",
                "reason": "why this skill is implied",
                "confidence": 0.6
            }
            ]"""
                    
        query = f"""Course description: {text[:1000]}

            Explicit skills already identified: {', '.join(explicit_skills[:20])}

            Identify implicit skills:"""
        
        prompt = self._format_instruction(sys_message, query)
        
        sampling_params = SamplingParams(
            max_tokens=1024,
            temperature=0.0,
            top_p=1
        )
        
        output = self.llm.generate([prompt], sampling_params=sampling_params)[0]
        response = output.outputs[0].text
        
        return self._parse_implicit_skills_response(response)
    
    def _parse_skill_extraction_response(self, response: str) -> List[Dict]:
        """Parse skill extraction response from LLM"""
        try:
            # Look for content after "assistant" marker
            assistant_pattern = r'(?:assistant|<\|assistant\|>)'
            assistant_match = re.search(assistant_pattern, response, re.IGNORECASE)
            
            if assistant_match:
                # Get content after "assistant"
                response_after_assistant = response[assistant_match.end():]
                
                # Check if there's a "final" marker and extract content after it
                final_match = re.search(r'(?:final|<\|final\|>)', response_after_assistant, re.IGNORECASE)
                
                if final_match:
                    # Extract JSON after "final" marker
                    search_text = response_after_assistant[final_match.end():]
                else:
                    # If no "final" marker, search after "assistant"
                    search_text = response_after_assistant
            else:
                # Fallback to searching the entire response if no "assistant" marker
                search_text = response
            
            # Extract JSON array from the relevant portion
            json_match = re.search(r'\[.*?\]', search_text, re.DOTALL)
            
            if json_match:
                skills_json = json.loads(json_match.group())
                return self._validate_extracted_skills(skills_json)
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse LLM response as JSON: {e}")
        
        # Fallback to empty list
        return []
    
    def _validate_extracted_skills(self, skills: List[Dict]) -> List[Dict]:
        """Validate and clean extracted skills"""
        valid_skills = []
        
        valid_categories = ["technical", "cognitive", "practical", "foundational", "professional"]
        valid_levels = ["novice", "beginner", "competent", "proficient", "expert"]
        valid_contexts = ["theoretical", "practical", "hybrid"]
        
        for skill in skills:
            if "name" in skill and skill["name"]:
                clean_skill = {
                    "name": skill.get("name", "")[:100],
                    "category": skill.get("category", "technical").lower(),
                    "level": skill.get("level", "competent").lower(),
                    "context": skill.get("context", "hybrid").lower(),
                    "keywords": skill.get("keywords", [])[:10],
                    "confidence": min(1.0, max(0.0, float(skill.get("confidence", 0.8))))
                }
                
                # Validate against allowed values
                if clean_skill["category"] not in valid_categories:
                    clean_skill["category"] = "technical"
                if clean_skill["level"] not in valid_levels:
                    clean_skill["level"] = "competent"
                if clean_skill["context"] not in valid_contexts:
                    clean_skill["context"] = "hybrid"
                
                valid_skills.append(clean_skill)
        
        return valid_skills
    
    def _parse_implicit_skills_response(self, response: str) -> List[Dict]:
        """Parse implicit skills response"""
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass
        
        return []
    
    def batch_process_units(self, units: List[Dict], batch_size: int = 8) -> List[List[Dict]]:
        """
        Process multiple units in batches for efficiency
        
        Args:
            units: List of unit dictionaries with 'text' field
            batch_size: Number of units to process in each batch
            
        Returns:
            List of skill lists for each unit
        """
        all_results = []
        
        for i in range(0, len(units), batch_size):
            batch = units[i:i + batch_size]
            texts = [unit.get('text', '') for unit in batch]
            
            # Process batch
            batch_results = self.extract_skills_batch(texts, "VET unit")
            all_results.extend(batch_results)
            
            logger.info(f"Processed batch {i//batch_size + 1}/{(len(units) + batch_size - 1)//batch_size}")
        
        return all_results