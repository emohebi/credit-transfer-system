"""
Interface for local GenAI model integration using vLLM with true batch processing
"""
import os
import json
import logging
import re
import shutil
import torch
from typing import List, Dict, Any, Optional
from pathlib import Path
from huggingface_hub import snapshot_download
from config.settings import CONFIG as Config
from vllm import LLM, SamplingParams

logger = logging.getLogger(__name__)


class VLLMGenAIInterface:
    """Interface for local GenAI model integration using vLLM with batch processing"""

    def __init__(self,
                 model_name: str = "meta-llama--Llama-3.1-8B-Instruct",
                 number_gpus: int = 1,
                 max_model_len: int = 8192,
                 batch_size: int = 8,
                 model_cache_dir: str = "/root/.cache/huggingface/hub",
                 external_model_dir: str = "/Volumes/jsa_external_prod/external_vols/scratch/Scratch/Ehsan/Models",
                 gpu_memory_utilization: float = 0.85,
                 gpu_id: int = 0):
        self.MODELS = Config['models']['llm_models']
        self.model_name = model_name
        self.number_gpus = number_gpus
        self.max_model_len = max_model_len
        self.batch_size = batch_size
        self.model_cache_dir = Path(model_cache_dir)
        self.external_model_dir = Path(external_model_dir)
        self.gpu_memory_utilization = gpu_memory_utilization
        self.gpu_id = gpu_id

        # Set environment variable to control GPU visibility for vLLM
        if self.number_gpus == 1:
            os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
            logger.info(f"Set CUDA_VISIBLE_DEVICES={gpu_id} for vLLM batch interface")
        else:
            gpu_list = ",".join(str(gpu_id + i) for i in range(number_gpus))
            os.environ["CUDA_VISIBLE_DEVICES"] = gpu_list
            logger.info(f"Set CUDA_VISIBLE_DEVICES={gpu_list} for vLLM batch interface")

        # Get model configuration
        if model_name not in self.MODELS:
            raise ValueError(f"Unknown model: {model_name}")

        self.model_config = self.MODELS[model_name]
        self.template = self.model_config.get("template", "Mistral")

        # Token budget for batching: leave room for output tokens
        # Use 80% of max_model_len as the per-prompt ceiling
        self._max_prompt_tokens = int(self.max_model_len * 0.80)

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
                max_model_len=self.max_model_len,
                gpu_memory_utilization=self.gpu_memory_utilization
            )
            logger.info(f"Successfully loaded model: {self.model_name} on GPU(s) specified by CUDA_VISIBLE_DEVICES")

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
            return f'''<|start|>system<|message|>{sys_message}\n\nReasoning: medium\n\n# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>user<|message|>{query}<|end|><|start|>assistant'''
        else:  # Default Mistral format
            return f'<s> [INST] {sys_message} [/INST]\nUser: {query}\nAssistant: '

    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token count estimate. Uses ~4 chars per token as a conservative
        heuristic. This avoids needing the actual tokenizer for batching decisions.
        """
        return len(text) // 4 + 1

    def _generate_batch(self, system_prompt: str, user_prompts: List[str], max_tokens: int = 2048) -> List[str]:
        """
        Generate responses for a batch of prompts with token-aware sub-batching.

        If any single formatted prompt exceeds the model's context window,
        it is skipped (returns empty string). If the batch as a whole is too
        large for a single vLLM call, it is split into sub-batches.
        """
        sampling_params = SamplingParams(
            max_tokens=max_tokens,
            temperature=0.0,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            n=1,
            best_of=1
        )

        # Format all prompts and check token counts
        formatted_prompts = []
        prompt_indices = []  # Track which original index each formatted prompt corresponds to
        skipped = set()

        for i, user_prompt in enumerate(user_prompts):
            full_prompt = self._format_instruction(system_prompt, user_prompt)
            estimated_tokens = self._estimate_tokens(full_prompt)

            if estimated_tokens > self._max_prompt_tokens:
                logger.warning(
                    f"Prompt {i} too long (~{estimated_tokens} tokens, "
                    f"max {self._max_prompt_tokens}). Skipping."
                )
                skipped.add(i)
                continue

            formatted_prompts.append(full_prompt)
            prompt_indices.append(i)

        # Generate in sub-batches to avoid overwhelming vLLM
        # Group prompts so each sub-batch stays under a reasonable total token count
        all_outputs = [""] * len(user_prompts)  # Pre-fill with empty strings

        if not formatted_prompts:
            return all_outputs

        sub_batches = self._split_into_subbatches(formatted_prompts, prompt_indices)

        for sub_formatted, sub_indices in sub_batches:
            try:
                outputs = self.llm.generate(sub_formatted, sampling_params=sampling_params, use_tqdm=False)
                for output, orig_idx in zip(outputs, sub_indices):
                    all_outputs[orig_idx] = output.outputs[0].text
            except Exception as e:
                logger.error(f"vLLM generation failed for sub-batch of {len(sub_formatted)}: {e}")
                # Try one-by-one fallback for this sub-batch
                for single_prompt, orig_idx in zip(sub_formatted, sub_indices):
                    try:
                        single_output = self.llm.generate([single_prompt], sampling_params=sampling_params, use_tqdm=False)
                        all_outputs[orig_idx] = single_output[0].outputs[0].text
                    except Exception as single_e:
                        logger.warning(f"Single prompt generation also failed for idx {orig_idx}: {single_e}")

        return all_outputs

    def _split_into_subbatches(
        self,
        formatted_prompts: List[str],
        prompt_indices: List[int],
    ) -> List[tuple]:
        """
        Split formatted prompts into sub-batches where each sub-batch's
        total estimated token count stays reasonable.

        Returns list of (sub_formatted, sub_indices) tuples.
        """
        # Each prompt is processed independently by vLLM, so the constraint
        # is really per-prompt, not total. But very large batches can cause
        # memory issues, so cap at a reasonable batch size.
        max_batch = min(32, len(formatted_prompts))

        sub_batches = []
        for start in range(0, len(formatted_prompts), max_batch):
            end = min(start + max_batch, len(formatted_prompts))
            sub_batches.append((
                formatted_prompts[start:end],
                prompt_indices[start:end],
            ))

        return sub_batches

    def generate_response(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        """Unified method for generating responses"""
        if max_tokens is None:
            max_tokens = 2048
        responses = self._generate_batch(system_prompt, [user_prompt], max_tokens)
        return responses[0] if responses else ""

    def generate_json(self,
                      prompt: str,
                      system_prompt: Optional[str] = None,
                      max_tokens: int = 2048,
                      temperature: float = 0.1,
                      **kwargs) -> Dict:
        """Generate JSON response"""
        json_system = system_prompt or ""
        if json_system:
            json_system += "\n\n"
        json_system += "You must respond with valid JSON only. No additional text, explanation, or markdown."

        json_prompt = prompt + "\n\nRespond with valid JSON only:"

        response = self.generate_response(
            system_prompt=json_system,
            user_prompt=json_prompt,
            max_tokens=max_tokens
        )

        return self._parse_json_response(response)

    def _parse_json_response(self, response: str) -> Dict:
        """
        Parse JSON from model response using the robust shared parser.
        Falls back to legacy parsing if the shared parser is not available.
        """
        if not response:
            return {}

        # Use the robust shared parser
        try:
            from src.utils.json_parser import robust_parse_json
            return robust_parse_json(response)
        except ImportError:
            pass

        # Legacy fallback — kept for backward compatibility
        return self._legacy_parse_json(response)

    def _legacy_parse_json(self, response: str) -> Dict:
        """Legacy JSON parsing — used only if robust parser is unavailable."""
        text = response.strip()

        # Remove markdown code blocks
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

        # Try array
        array_match = re.search(r'\[[\s\S]*\]', text)
        if array_match:
            try:
                return json.loads(array_match.group())
            except json.JSONDecodeError:
                pass

        # Try object
        obj_match = re.search(r'\{[\s\S]*\}', text)
        if obj_match:
            try:
                return json.loads(obj_match.group())
            except json.JSONDecodeError:
                pass

        # Try finding second object (for double-wrapped)
        obj_match = re.findall(r'\{[^{}]*\}', text)
        if obj_match:
            try:
                if len(obj_match) >= 2:
                    return json.loads(obj_match[1])
                return json.loads(obj_match[0])
            except json.JSONDecodeError:
                pass

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.warning(f"Response was: \n{text}")
            return {}


# Alias for backwards compatibility
VLLMGenAIInterfaceBatch = VLLMGenAIInterface