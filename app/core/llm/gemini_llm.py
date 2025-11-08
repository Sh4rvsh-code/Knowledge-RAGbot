"""Google Gemini API wrapper - FREE tier with generous limits!"""
from typing import Optional
import requests
import json

from app.config import settings
from app.utils.logger import app_logger as logger
from app.core.llm.orchestrator import BaseLLM


class GeminiLLM(BaseLLM):
    """
    Google Gemini API wrapper - FREE!
    
    Free tier includes:
    - 15 requests per minute
    - 1 million tokens per minute
    - 1500 requests per day
    
    Models:
    - gemini-pro (text generation)
    - gemini-pro-vision (image + text)
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500
    ):
        """
        Initialize Gemini LLM.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-pro)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or settings.gemini_api_key
        # Try different model names - Gemini API keeps changing
        self.model = model or settings.gemini_model or "gemini-1.5-flash-latest"
        self.default_temperature = temperature
        self.default_max_tokens = max_tokens
        
        if not self.api_key:
            raise ValueError("Gemini API key not provided")
        
        # Use v1 API endpoint (more stable than v1beta)
        self.api_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"
        
        logger.info(f"Initialized Gemini LLM with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate response using Gemini API with fallback models.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature or self.default_temperature
        
        # Try multiple model names as fallback
        model_names_to_try = [
            self.model,
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-1.0-pro"
        ]
        
        last_error = None
        
        for model_name in model_names_to_try:
            try:
                return self._attempt_generate(prompt, max_tokens, temperature, model_name)
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_name} failed, trying next...")
                continue
        
        # If all models failed
        logger.error(f"All Gemini models failed. Last error: {last_error}")
        return f"Error: All models failed. Please check your API key and try again."
    
    def _attempt_generate(
        self,
        prompt: str,
        max_tokens: int,
        temperature: float,
        model_name: str
    ) -> str:
        """Attempt to generate with a specific model."""
        try:
            # Build API URL for this model
            api_url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent"
            # Gemini API request format
            payload = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                    "topP": 0.95,
                    "topK": 40
                }
            }
            
            # Add API key as query parameter
            url_with_key = f"{api_url}?key={self.api_key}"
            
            response = requests.post(
                url_with_key,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract generated text from Gemini response
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate:
                        content = candidate["content"]
                        if "parts" in content and len(content["parts"]) > 0:
                            text = content["parts"][0].get("text", "")
                            logger.info(f"Successfully generated response with model: {model_name}")
                            return text
                
                logger.warning(f"Unexpected Gemini response format: {result}")
                raise Exception("Unexpected response format")
            
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Bad request")
                logger.error(f"Gemini API error 400 with {model_name}: {error_msg}")
                raise Exception(f"400: {error_msg}")
            
            elif response.status_code == 404:
                logger.warning(f"Model {model_name} not found (404)")
                raise Exception(f"Model {model_name} not found")
            
            elif response.status_code == 429:
                logger.warning("Gemini API rate limit reached")
                return "⚠️ Rate limit reached. Please wait a moment and try again."
            
            elif response.status_code == 403:
                logger.error("Gemini API key invalid or forbidden")
                raise Exception("Invalid API key or access forbidden")
            
            else:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise Exception(f"Status {response.status_code}")
                
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out")
            return "Error: Request timed out. Please try again."
        
        except Exception as e:
            logger.error(f"Error calling Gemini API: {str(e)}")
            return f"Error: {str(e)}"
    
    def stream_generate(self, prompt: str, max_tokens: int = None) -> str:
        """
        Stream generation (not yet implemented for Gemini).
        Falls back to regular generation.
        """
        return self.generate(prompt, max_tokens)
