"""
Interface for Azure OpenAI integration
Provides unified generate() and generate_json() methods for LLM tasks
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI

logger = logging.getLogger(__name__)


class GenAIInterface:
    """Interface for Azure OpenAI integration"""
    
    def __init__(self, 
                 endpoint: Optional[str] = None,
                 deployment: Optional[str] = None,
                 api_key: Optional[str] = None,
                 api_version: str = "2025-01-01-preview",
                 timeout: int = 60,
                 max_tokens: int = 4000,
                 temperature: float = 0.0):
        """
        Initialize Azure OpenAI interface
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment: Deployment name (model)
            api_key: Azure OpenAI API key
            api_version: API version
            timeout: Request timeout in seconds
            max_tokens: Maximum tokens for responses
            temperature: Sampling temperature (0.0 for deterministic)
        """
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY", "")
        self.api_version = api_version
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        self.client = None
        self._initialized = False
        
        if self.is_available():
            self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Azure OpenAI client"""
        try:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
                timeout=self.timeout
            )
            self._initialized = True
            logger.info(f"Azure OpenAI client initialized: {self.endpoint} / {self.deployment}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            self._initialized = False
    
    def is_available(self) -> bool:
        """Check if the interface is properly configured"""
        return bool(
            self.api_key and 
            self.api_key != "REPLACE_WITH_YOUR_KEY_VALUE_HERE" and
            self.endpoint and
            self.deployment
        )
    
    def generate(self, 
                 prompt: str,
                 system_prompt: Optional[str] = None,
                 max_tokens: Optional[int] = None,
                 temperature: Optional[float] = None,
                 top_p: float = 1.0,
                 **kwargs) -> str:
        """
        Generate text completion
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
        """
        if not self._initialized:
            if not self.is_available():
                raise RuntimeError("Azure OpenAI is not configured")
            self._initialize_client()
        
        messages = []
        if system_prompt:
            messages.append({
                "role": "system",
                "content": [{"type": "text", "text": system_prompt}]
            })
        
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": prompt}]
        })
        
        try:
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                top_p=top_p,
                max_tokens=max_tokens or self.max_tokens,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False,
                seed=42
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API request failed: {e}")
            raise
    
    def generate_response(self, 
                          system_prompt: str, 
                          user_prompt: str, 
                          max_tokens: Optional[int] = None,
                          temperature: float = 0.0,
                          top_p: float = 1.0) -> str:
        """
        Generate response (legacy method for compatibility)
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            top_p: Top-p sampling
            
        Returns:
            Generated text
        """
        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p
        )
    
    def generate_json(self,
                      prompt: str,
                      system_prompt: Optional[str] = None,
                      max_tokens: Optional[int] = None,
                      temperature: float = 0.1,
                      **kwargs) -> Dict:
        """
        Generate JSON response
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower for JSON)
            **kwargs: Additional parameters
            
        Returns:
            Parsed JSON dictionary
        """
        # Add JSON instruction to system prompt
        json_system = system_prompt or ""
        if json_system:
            json_system += "\n\n"
        json_system += "You must respond with valid JSON only. No additional text or explanation."
        
        response = self.generate(
            prompt=prompt,
            system_prompt=json_system,
            max_tokens=max_tokens,
            temperature=temperature,
            **kwargs
        )
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        if not response:
            return {}
        
        text = response.strip()
        
        # Remove markdown code blocks
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        
        if text.endswith('```'):
            text = text[:-3]
        
        text = text.strip()
        
        # Try to find JSON array or object
        import re
        
        # Try array first
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
        
        # Try parsing the whole text
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response was: {text[:500]}...")
            return {}
