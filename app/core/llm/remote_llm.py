"""Remote LLM wrappers for OpenAI and Anthropic."""
from typing import Optional
import openai
from anthropic import Anthropic

from app.config import settings
from app.utils.logger import app_logger as logger
from app.core.llm.orchestrator import BaseLLM


class OpenAILLM(BaseLLM):
    """
    OpenAI API wrapper for GPT models.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        temperature: float = None,
        max_tokens: int = None
    ):
        """
        Initialize OpenAI LLM.
        
        Args:
            api_key: OpenAI API key
            model: Model name (e.g., gpt-3.5-turbo, gpt-4)
            temperature: Default temperature
            max_tokens: Default max tokens
        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.default_temperature = temperature or settings.openai_temperature
        self.default_max_tokens = max_tokens or settings.openai_max_tokens
        
        if not self.api_key:
            raise ValueError("OpenAI API key not provided")
        
        # Set API key
        openai.api_key = self.api_key
        
        logger.info(f"Initialized OpenAI LLM with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        max_tokens = max_tokens or self.default_max_tokens
        temperature = temperature if temperature is not None else self.default_temperature
        
        try:
            logger.info(f"Calling OpenAI API with model: {self.model}")
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            answer = response.choices[0].message.content.strip()
            
            logger.info(f"OpenAI response received: {len(answer)} chars")
            return answer
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"


class AnthropicLLM(BaseLLM):
    """
    Anthropic Claude API wrapper.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None
    ):
        """
        Initialize Anthropic LLM.
        
        Args:
            api_key: Anthropic API key
            model: Model name (e.g., claude-3-sonnet-20240229)
        """
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.anthropic_model
        
        if not self.api_key:
            raise ValueError("Anthropic API key not provided")
        
        self.client = Anthropic(api_key=self.api_key)
        
        logger.info(f"Initialized Anthropic LLM with model: {self.model}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated response
        """
        try:
            logger.info(f"Calling Anthropic API with model: {self.model}")
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            answer = message.content[0].text.strip()
            
            logger.info(f"Anthropic response received: {len(answer)} chars")
            return answer
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}"


def get_remote_llm(provider: str = "openai") -> BaseLLM:
    """
    Get remote LLM instance.
    
    Args:
        provider: Provider name ('openai' or 'anthropic')
        
    Returns:
        LLM instance
    """
    if provider.lower() == "openai":
        return OpenAILLM()
    elif provider.lower() == "anthropic":
        return AnthropicLLM()
    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_llm() -> BaseLLM:
    """
    Get LLM instance based on configuration.
    
    Returns:
        LLM instance (local or remote)
    """
    if settings.llm_provider == "local":
        from app.core.llm.local_llm import get_local_llm
        return get_local_llm()
    else:
        # Default to OpenAI for remote
        return get_remote_llm("openai")
