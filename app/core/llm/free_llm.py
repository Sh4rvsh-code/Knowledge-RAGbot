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
        
        # Updated to new HF endpoint
        self.api_url = f"https://router.huggingface.co/hf-inference/models/{self.model}"
        self.headers = {"Content-Type": "application/json"}
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
        Generate response using local model with improved quality.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature if temperature is not None else 0.7
        
        try:
            # Generate with improved parameters for better quality
            logger.info(f"Generating with max_tokens={max_tokens}, temperature={temperature}")
            
            result = self.pipeline(
                prompt,
                max_new_tokens=max_tokens,
                do_sample=True,  # Always use sampling for better variety
                temperature=max(temperature, 0.7),  # Higher temp for more detailed responses
                top_p=0.95,  # Increased for more diverse tokens
                top_k=50,  # Add top-k sampling
                num_return_sequences=1,
                repetition_penalty=1.2  # Reduce repetition
            )
            
            if result and len(result) > 0:
                generated_text = result[0]["generated_text"]
                logger.info(f"Generated text length: {len(generated_text)} chars")
                logger.debug(f"Generated text: {generated_text[:200]}...")
                
                # Clean up the response
                cleaned = generated_text.strip()
                
                # If response is empty or too short, provide fallback
                if len(cleaned) < 10:
                    logger.warning("Generated text is too short or empty")
                    return "Based on the documents, I don't have enough information to provide a detailed answer to this specific question."
                
                return cleaned
            else:
                logger.warning("Pipeline returned no results")
                return "I don't have enough information to answer that question based on the provided documents."
                
        except Exception as e:
            logger.error(f"Error generating with local model: {str(e)}")
            return f"I encountered an error while generating the answer. Please try again."


def get_free_llm() -> BaseLLM:
    """
    Get a FREE LLM instance.
    
    Priority:
    1. Local model (completely free, no API needed) 
    2. Hugging Face API (requires free API key)
    
    Returns:
        Free LLM instance
    """
    # Try local model first (no API key needed)
    try:
        logger.info("Initializing local model (completely free, no API needed)")
        return LocalLLM()
    except Exception as e:
        logger.warning(f"Could not initialize local LLM: {e}")
    
    # Fall back to Hugging Face if HF API key is available
    from app.config import settings
    if settings.huggingface_api_key:
        try:
            logger.info("Falling back to Hugging Face API")
            return HuggingFaceLLM()
        except Exception as e:
            logger.warning(f"Could not initialize Hugging Face LLM: {e}")
    
    # If all else fails, provide helpful error
    raise ValueError(
        "No LLM available. Please either:\n"
        "1. Install transformers for local model: pip install transformers torch\n"
        "2. Get a free Gemini API key from https://makersuite.google.com/app/apikey\n"
        "3. Get a free Hugging Face token from https://huggingface.co/settings/tokens\n"
        "4. Use OpenAI/Anthropic API key"
    )
