"""
Interface for Azure OpenAI integration
Modified to use Gen AI for all pattern matching and extraction tasks
"""

import json
import logging
import re
import os
from typing import List, Dict, Any, Optional
from openai import AzureOpenAI
from src.utils.converters import JSONExtraction

logger = logging.getLogger(__name__)


class GenAIInterface:
    """Interface for Azure OpenAI integration - Full Gen AI approach"""
    
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
        # Use environment variables as fallback
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "https://ehsaninstance1.openai.azure.com/")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4o")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        
        if not self.api_key or self.api_key == "REPLACE_WITH_YOUR_KEY_VALUE_HERE":
            raise ValueError("Azure OpenAI API key is required. Set AZURE_OPENAI_API_KEY environment variable.")
        
        self.api_version = api_version
        self.timeout = timeout
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize Azure OpenAI client
        try:
            self.client = AzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
                timeout=self.timeout
            )
            logger.info(f"Azure OpenAI client initialized with endpoint: {self.endpoint}")
        except Exception as e:
            logger.error(f"Failed to initialize Azure OpenAI client: {e}")
            raise
    
    def _call_openai_api(self, system_prompt: str, user_prompt: str, max_tokens: Optional[int] = None, temperature: float = 0.0, top_p=1.0) -> str:
        """
        Make API call to Azure OpenAI
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Override max tokens for this call
            temperature: Temperature for sampling (default 0.0 for deterministic)
            
        Returns:
            Model response as string
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
                        }
                    ]
                },
                {
                    "role": "user", 
                    "content": [
                        {
                            "type": "text",
                            "text": user_prompt
                        }
                    ]
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                temperature=temperature,  # Use passed temperature
                top_p=top_p,  # Deterministic
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False,
                seed=42  # Add seed for additional determinism if supported
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI API request failed: {e}")
            raise
    
    def _parse_json_response(self, response: str) -> Dict:
        """Parse JSON from model response"""
        try:
            # Try to extract JSON from response
            json_match = JSONExtraction.extract_json_from_text(response)
            if json_match:
                return json.loads(json_match)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
        return {}
    