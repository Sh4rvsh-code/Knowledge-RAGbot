"""Local LLM wrapper using Hugging Face transformers."""
from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

from app.config import settings
from app.utils.logger import app_logger as logger
from app.core.llm.orchestrator import BaseLLM


class LocalLLM(BaseLLM):
    """
    Local LLM using Hugging Face transformers.
    
    Supports various open-source models for on-premise deployment.
    """
    
    def __init__(
        self,
        model_name: str = None,
        max_length: int = None,
        device: str = None
    ):
        """
        Initialize local LLM.
        
        Args:
            model_name: Hugging Face model name
            max_length: Maximum generation length
            device: Device to use ('cuda', 'cpu', 'mps')
        """
        self.model_name = model_name or settings.local_model_name
        self.max_length = max_length or settings.local_model_max_length
        
        # Determine device
        if device:
            self.device = device
        elif torch.cuda.is_available():
            self.device = "cuda"
        elif torch.backends.mps.is_available():
            self.device = "mps"
        else:
            self.device = "cpu"
        
        logger.info(f"Loading local model: {self.model_name} on {self.device}")
        
        # Load tokenizer and model
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16 if self.device != "cpu" else torch.float32,
                device_map="auto" if self.device == "cuda" else None
            )
            
            if self.device != "cuda":
                self.model = self.model.to(self.device)
            
            # Create generation pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=self.device if self.device != "mps" else -1
            )
            
            logger.info(f"Local model loaded successfully on {self.device}")
            
        except Exception as e:
            logger.error(f"Failed to load local model: {e}")
            raise RuntimeError(f"Failed to initialize local LLM: {e}")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Generate text using local model.
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Generated text
        """
        try:
            # Generate
            outputs = self.pipeline(
                prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                return_full_text=False
            )
            
            # Extract generated text
            generated_text = outputs[0]["generated_text"]
            
            # Clean up response
            response = self._clean_response(generated_text, prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return "I apologize, but I encountered an error generating a response."
    
    def _clean_response(self, generated: str, prompt: str) -> str:
        """Clean and extract response from generated text."""
        # Remove prompt if present
        if generated.startswith(prompt):
            generated = generated[len(prompt):].strip()
        
        # Remove common artifacts
        generated = generated.strip()
        
        # Truncate at first occurrence of stop sequences
        stop_sequences = ["\n\nQuestion:", "\n\nContext:", "###", "---"]
        for stop in stop_sequences:
            if stop in generated:
                generated = generated.split(stop)[0].strip()
        
        return generated


def get_local_llm() -> LocalLLM:
    """Get or create local LLM instance."""
    global _local_llm_instance
    
    if '_local_llm_instance' not in globals():
        globals()['_local_llm_instance'] = LocalLLM()
    
    return globals()['_local_llm_instance']
