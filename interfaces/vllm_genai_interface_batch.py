"""
Interface for local GenAI model integration using vLLM with true batch processing
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


class VLLMGenAIInterfaceBatch:
    """Interface for local GenAI model integration using vLLM with batch processing"""
    
    def __init__(self, 
                 model_name: str = "meta-llama--Llama-3.1-8B-Instruct",
                 number_gpus: int = 1,
                 max_model_len: int = 8192,
                 batch_size: int = 8,
                 model_cache_dir: str = "/root/.cache/huggingface/hub",
                 external_model_dir: str = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models"):
        """
        Initialize vLLM GenAI interface with batch processing
        
        Args:
            model_name: Name of the model to use
            number_gpus: Number of GPUs for tensor parallelism
            max_model_len: Maximum model context length
            batch_size: Default batch size for processing
            model_cache_dir: Directory for HuggingFace cache
            external_model_dir: Directory containing pre-downloaded models
        """
        self.MODELS = Config.MODELS
        self.model_name = model_name
        self.number_gpus = number_gpus
        self.max_model_len = max_model_len
        self.batch_size = batch_size
        self.model_cache_dir = Path(model_cache_dir)
        self.external_model_dir = Path(external_model_dir)
        
        # Get model configuration
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}")
        
        self.model_config = self.MODELS[model_name]
        self.template = self.model_config.get("template", "Mistral")
        
        # Import prompts
        from extraction.genai_prompts import GenAIPrompts
        self.prompts = GenAIPrompts()
        
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
            external_path = self.external_model_dir / f"models--{self.model_name}"
            cache_path = self.model_cache_dir / f"models--{self.model_name}"
            
            if copy_model and external_path.exists():
                try:
                    shutil.copytree(str(external_path), str(cache_path))
                    logger.info(f"Copied model from {external_path} to {cache_path}")
                except FileExistsError:
                    logger.info(f"Model already exists in cache: {cache_path}")
            
            snapshot_location = snapshot_download(
                repo_id=model_id,
                revision=revision,
                cache_dir=str(self.model_cache_dir)
            )
        else:
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
    
    def _generate_batch(self, system_prompt: str, user_prompts: List[str], max_tokens: int = 2048) -> List[str]:
        """Generate responses for a batch of prompts"""
        full_prompts = [
            self._format_instruction(system_prompt, user_prompt) 
            for user_prompt in user_prompts
        ]
        
        sampling_params = SamplingParams(
            max_tokens=max_tokens,
            temperature=0.0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
            best_of=1
        )
        
        outputs = self.llm.generate(full_prompts, sampling_params=sampling_params)
        return [output.outputs[0].text for output in outputs]
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        try:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        return {}
    
    # Batch extraction methods
    
    def extract_skills_batch(self, texts: List[str], contexts: List[str] = None) -> List[List[Dict]]:
        """
        Extract skills from multiple texts in batch
        
        Args:
            texts: List of texts to extract skills from
            contexts: List of context types (optional)
            
        Returns:
            List of extracted skills for each text
        """
        if contexts is None:
            contexts = ["course"] * len(texts)
        
        system_prompt = self.prompts.skill_extraction_prompt()
        user_prompts = [
            f"Context: {context}\n\nText to analyze:\n{text[:3000]}"
            for text, context in zip(texts, contexts)
        ]
        
        # Process in batches if needed
        all_results = []
        for i in range(0, len(user_prompts), self.batch_size):
            batch = user_prompts[i:i + self.batch_size]
            responses = self._generate_batch(system_prompt, batch)
            
            for response in responses:
                result = self._parse_json_response(response)
                all_results.append(result.get("skills", []))
        
        return all_results
    
    def identify_study_levels_batch(self, course_texts: List[str]) -> List[Dict]:
        """Identify study levels for multiple courses"""
        system_prompt = self.prompts.study_level_identification_prompt()
        user_prompts = [
            f"Course description:\n{text[:2000]}" 
            for text in course_texts
        ]
        
        all_results = []
        for i in range(0, len(user_prompts), self.batch_size):
            batch = user_prompts[i:i + self.batch_size]
            responses = self._generate_batch(system_prompt, batch, max_tokens=512)
            
            for response in responses:
                all_results.append(self._parse_json_response(response))
        
        return all_results
    
    def identify_implicit_skills_batch(self, texts: List[str], explicit_skills_lists: List[List[str]]) -> List[List[Dict]]:
        """Identify implicit skills for multiple texts"""
        system_prompt = self.prompts.implicit_skill_identification_prompt()
        user_prompts = [
            f"Course content: {text[:1500]}\n\nExplicit skills already identified: {', '.join(skills[:20])}"
            for text, skills in zip(texts, explicit_skills_lists)
        ]
        
        all_results = []
        for i in range(0, len(user_prompts), self.batch_size):
            batch = user_prompts[i:i + self.batch_size]
            responses = self._generate_batch(system_prompt, batch)
            
            for response in responses:
                result = self._parse_json_response(response)
                all_results.append(result.get("implicit_skills", []))
        
        return all_results
    
    def determine_contexts_batch(self, texts: List[str]) -> List[Dict]:
        """Determine theoretical vs practical context for multiple texts"""
        system_prompt = self.prompts.context_determination_prompt()
        user_prompts = [f"Text to analyze:\n{text[:2000]}" for text in texts]
        
        all_results = []
        for i in range(0, len(user_prompts), self.batch_size):
            batch = user_prompts[i:i + self.batch_size]
            responses = self._generate_batch(system_prompt, batch, max_tokens=512)
            
            for response in responses:
                all_results.append(self._parse_json_response(response))
        
        return all_results
    
    def analyze_skill_similarities_batch(self, skill_pairs: List[tuple]) -> List[float]:
        """Analyze similarity for multiple skill pairs"""
        system_prompt = self.prompts.skill_similarity_prompt()
        user_prompts = [
            f"Skill 1: {skill1}\nSkill 2: {skill2}"
            for skill1, skill2 in skill_pairs
        ]
        
        all_scores = []
        for i in range(0, len(user_prompts), self.batch_size):
            batch = user_prompts[i:i + self.batch_size]
            responses = self._generate_batch(system_prompt, batch, max_tokens=256)
            
            for response in responses:
                result = self._parse_json_response(response)
                all_scores.append(result.get("similarity_score", 0.5))
        
        return all_scores
    
    # Single-item methods that delegate to batch methods
    
    def extract_skills_prompt(self, text: str, context: str = "course") -> List[Dict]:
        """Extract skills from a single text (delegates to batch)"""
        results = self.extract_skills_batch([text], [context])
        return results[0] if results else []
    
    def identify_study_level(self, course_text: str) -> Dict:
        """Identify study level from single course (delegates to batch)"""
        results = self.identify_study_levels_batch([course_text])
        return results[0] if results else {}
    
    def identify_implicit_skills(self, text: str, explicit_skills: List[str]) -> List[Dict]:
        """Identify implicit skills for single text (delegates to batch)"""
        results = self.identify_implicit_skills_batch([text], [explicit_skills])
        return results[0] if results else []
    
    def determine_context(self, text: str) -> Dict:
        """Determine context for single text (delegates to batch)"""
        results = self.determine_contexts_batch([text])
        return results[0] if results else {}
    
    def analyze_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Analyze similarity between two skills (delegates to batch)"""
        results = self.analyze_skill_similarities_batch([(skill1, skill2)])
        return results[0] if results else 0.5
    
    # Methods that remain single-processing (less common operations)
    
    def deduplicate_skills(self, skills: List[Dict]) -> Dict:
        """Deduplicate and merge similar skills"""
        system_prompt = self.prompts.skill_deduplication_prompt()
        skills_json = json.dumps(skills[:50], indent=2)
        user_prompt = f"Skills to analyze:\n{skills_json}"
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def decompose_composite_skills(self, skills: List[str]) -> Dict:
        """Decompose composite skills into components"""
        system_prompt = self.prompts.composite_skill_decomposition_prompt()
        user_prompt = f"Skills to analyze:\n{json.dumps(skills[:30], indent=2)}"
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def adjust_skill_levels(self, skills: List[Dict], study_level: str, course_text: str) -> Dict:
        """Adjust skill levels based on context"""
        system_prompt = self.prompts.skill_level_adjustment_prompt()
        user_prompt = f"""Study level: {study_level}
Course context: {course_text[:1000]}
Skills to adjust: {json.dumps(skills[:30], indent=2)}"""
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def extract_technology_versions(self, text: str) -> Dict:
        """Extract technology versions and assess currency"""
        system_prompt = self.prompts.technology_version_extraction_prompt()
        user_prompt = f"Text to analyze:\n{text[:2000]}"
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def analyze_prerequisites(self, prerequisites: List[str], course_text: str) -> Dict:
        """Analyze prerequisites and dependencies"""
        system_prompt = self.prompts.prerequisite_analysis_prompt()
        user_prompt = f"""Prerequisites: {', '.join(prerequisites)}
Course context: {course_text[:1000]}"""
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def detect_edge_cases(self, vet_text: str, uni_text: str, mapping_info: Dict) -> Dict:
        """Detect edge cases in credit mapping"""
        system_prompt = self.prompts.edge_case_detection_prompt()
        user_prompt = f"""VET content: {vet_text[:1000]}
University content: {uni_text[:1000]}
Mapping summary: {json.dumps(mapping_info, indent=2)}"""
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def extract_keywords(self, skill_name: str, context_text: str) -> List[str]:
        """Extract relevant keywords for a skill"""
        system_prompt = self.prompts.keyword_extraction_prompt()
        user_prompt = f"Skill: {skill_name}\nContext: {context_text[:500]}"
        
        response = self._generate_batch(system_prompt, [user_prompt], max_tokens=256)[0]
        result = self._parse_json_response(response)
        return result.get("keywords", [])
    
    def analyze_assessment(self, assessment_text: str) -> Dict:
        """Analyze assessment methods"""
        system_prompt = self.prompts.assessment_type_analysis_prompt()
        user_prompt = f"Assessment description:\n{assessment_text[:1500]}"
        
        response = self._generate_batch(system_prompt, [user_prompt])[0]
        return self._parse_json_response(response)
    
    def categorize_skill(self, skill_name: str, context: str = "") -> str:
        """Categorize a skill"""
        system_prompt = self.prompts.skill_categorization_prompt()
        user_prompt = f"Skill to categorize: {skill_name}\nContext: {context[:200]}"
        
        response = self._generate_batch(system_prompt, [user_prompt], max_tokens=256)[0]
        result = self._parse_json_response(response)
        return result.get("category", "technical")