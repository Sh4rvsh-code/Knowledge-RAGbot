"""Hugging Face Inference API wrapper - FREE alternative to OpenAI."""
from typing import Optional
import requests
import json

from app.config import settings
from app.utils.logger import app_logger as logger
from app.core.llm.orchestrator import BaseLLM


class HuggingFaceLLM(BaseLLM):
    """
    Hugging Face Inference API wrapper - FREE!
    
    Uses Hugging Face's free inference API with models like:
    - google/flan-t5-xxl (good for Q&A)
    - mistralai/Mistral-7B-Instruct-v0.1
    - meta-llama/Llama-2-7b-chat-hf
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize Hugging Face LLM.
        
        Args:
            api_key: HF API token (free from huggingface.co)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or settings.huggingface_api_key or ""
        self.model = model or settings.huggingface_model or "google/flan-t5-xxl"
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens
        
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model}"
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        logger.info(f"Initialized Hugging Face LLM with model: {self.model}")
        if not self.api_key:
            logger.warning("No HF API key provided - using public inference (rate limited)")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate response using Hugging Face Inference API.
        
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
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Handle different response formats
                if isinstance(result, list) and len(result) > 0:
                    if "generated_text" in result[0]:
                        return result[0]["generated_text"]
                    elif "translation_text" in result[0]:
                        return result[0]["translation_text"]
                    else:
                        return str(result[0])
                elif isinstance(result, dict):
                    if "generated_text" in result:
                        return result["generated_text"]
                    else:
                        return str(result)
                else:
                    return str(result)
            
            elif response.status_code == 503:
                # Model is loading
                error = response.json()
                wait_time = error.get("estimated_time", 20)
                logger.warning(f"Model loading, estimated wait: {wait_time}s")
                return f"⏳ Model is loading (estimated {wait_time}s). Please try again in a moment."
            
            else:
                logger.error(f"HF API error: {response.status_code} - {response.text}")
                return f"Error: Unable to generate response (status {response.status_code})"
                
        except Exception as e:
            logger.error(f"Error calling Hugging Face API: {str(e)}")
            return f"Error: {str(e)}"


class LocalLLM(BaseLLM):
    """
    Simple local LLM using transformers library.
    Works without any API key - completely free!
    """
    
    def __init__(
        self,
        model: str = None,
        max_tokens: int = 256
    ):
        """
        Initialize local LLM.
        
        Args:
            model: Model name (small models work best)
            max_tokens: Maximum tokens
        """
        try:
            from transformers import pipeline
            
            self.model = model or "google/flan-t5-small"
            self.default_max_tokens = max_tokens
            
            logger.info(f"Loading local model: {self.model}")
            
            # Use text generation pipeline
            self.pipeline = pipeline(
                "text2text-generation",
                model=self.model,
                device=-1  # CPU
            )
            
            logger.info(f"Initialized Local LLM with model: {self.model}")
            
        except ImportError:
            raise ImportError(
                "transformers library not installed. "
                "Install with: pip install transformers torch"
            )
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate response using local model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or self.default_max_tokens
        
        try:
            result = self.pipeline(
                prompt,
                max_length=max_tokens,
                do_sample=True,
                temperature=temperature or 0.7
            )
            
            if result and len(result) > 0:
                return result[0]["generated_text"]
            else:
                return "Error: No response generated"
                
        except Exception as e:
            logger.error(f"Error generating with local model: {str(e)}")
            return f"Error: {str(e)}"


def get_free_llm() -> BaseLLM:
    """
    Get a FREE LLM instance.
    
    Priority:
    1. Hugging Face API (free with optional API key)
    2. Local model (completely free, no API needed)
    
    Returns:
        Free LLM instance
    """
    # Try Hugging Face first (better quality, free API)
    try:
        return HuggingFaceLLM()
    except Exception as e:
        logger.warning(f"Could not initialize Hugging Face LLM: {e}")
    
    # Fall back to local model
    try:
        logger.info("Falling back to local model (may be slower)")
        return LocalLLM()
    except Exception as e:
        logger.error(f"Could not initialize local LLM: {e}")
        raise ValueError(
            "No LLM available. Please either:\n"
            "1. Get a free Hugging Face token from huggingface.co\n"
            "2. Install transformers: pip install transformers torch\n"
            "3. Use OpenAI/Anthropic API key"
        )
