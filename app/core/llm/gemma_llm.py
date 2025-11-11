"""Google Gemma model via HuggingFace Inference API."""
from typing import Optional, Dict, Any
import requests
import json

from app.config import settings
from app.utils.logger import app_logger as logger
from app.core.llm.orchestrator import BaseLLM


class GemmaLLM(BaseLLM):
    """
    Google Gemma model via HuggingFace Inference API.
    
    Gemma is a family of lightweight, state-of-the-art open models from Google,
    built from the same research and technology used to create Gemini models.
    
    Features:
    - Lightweight and fast
    - Can run on limited resources
    - Good for question answering, summarization, reasoning
    - Free tier available with HuggingFace API
    
    Models available:
    - google/gemma-2-2b-it (2B parameters, instruction-tuned)
    - google/gemma-2-9b-it (9B parameters, instruction-tuned)
    - google/gemma-1.1-7b-it (7B parameters)
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize Gemma LLM.
        
        Args:
            api_key: HuggingFace API token
            model: Model name (default: gemma-2-2b-it)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or settings.huggingface_api_key
        
        if not self.api_key:
            raise ValueError(
                "HuggingFace API key required for Gemma model.\n"
                "Get free key from: https://huggingface.co/settings/tokens\n"
                "Add to .env: HUGGINGFACE_API_KEY=your_token_here"
            )
        
        # Default to the lightweight 2B model
        self.model = model or settings.gemma_model or "google/gemma-2-2b-it:nebius"
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens
        
        # HuggingFace chat completions endpoint
        self.api_url = "https://router.huggingface.co/v1/chat/completions"
        
        logger.info(f"Initialized Gemma LLM with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate response using Gemma model via HuggingFace API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        try:
            # Prepare request payload (OpenAI-compatible format)
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "stream": False
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            logger.info(f"Calling Gemma API: {self.model}")
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract response from OpenAI-compatible format
                if "choices" in result and len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        text = choice["message"]["content"]
                        logger.info(f"Gemma response: {len(text)} chars")
                        return text.strip()
                
                logger.warning(f"Unexpected response format: {result}")
                return "Error: Unexpected response format from Gemma API"
            
            elif response.status_code == 401:
                logger.error("Invalid HuggingFace API key")
                return "⚠️ Invalid HuggingFace API key. Please check your token."
            
            elif response.status_code == 429:
                logger.warning("Rate limit reached")
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            
            elif response.status_code == 503:
                logger.warning("Model is loading")
                return "⏳ Model is loading. Please try again in a moment."
            
            else:
                error_text = response.text
                logger.error(f"Gemma API error {response.status_code}: {error_text}")
                return f"Error: API returned status {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Gemma API request timed out")
            return "Error: Request timed out. Please try again."
        
        except Exception as e:
            logger.error(f"Error calling Gemma API: {str(e)}")
            return f"Error: {str(e)}"
    
    def stream_generate(self, prompt: str, max_tokens: int = None, temperature: float = None):
        """
        Stream generation from Gemma model.
        
        Yields text chunks as they're generated.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Yields:
            Text chunks as they arrive
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "stream": True  # Enable streaming
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                stream=True,
                timeout=30
            )
            
            if response.status_code == 200:
                full_text = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                chunk_data = json.loads(data)
                                if "choices" in chunk_data:
                                    choice = chunk_data["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        content = choice["delta"]["content"]
                                        full_text += content
                                        yield content
                            except json.JSONDecodeError:
                                continue
                
                if full_text:
                    logger.info(f"Streamed {len(full_text)} chars from Gemma")
                    return
            
            # Fallback to non-streaming
            logger.warning("Streaming failed, falling back to regular generation")
            result = self.generate(prompt, max_tokens, temperature)
            yield result
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            result = self.generate(prompt, max_tokens, temperature)
            yield result


def get_gemma_llm() -> BaseLLM:
    """
    Get Gemma LLM instance.
    
    Returns:
        Gemma LLM instance
        
    Raises:
        ValueError: If HuggingFace API key not configured
    """
    try:
        return GemmaLLM()
    except ValueError as e:
        logger.error(f"Cannot initialize Gemma LLM: {e}")
        raise
