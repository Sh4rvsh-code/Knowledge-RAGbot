"""LLM orchestrator for question answering with context."""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from app.utils.logger import app_logger as logger


class BaseLLM(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """Generate response from prompt."""
        pass


class LLMOrchestrator:
    """
    Orchestrate LLM-based question answering with retrieved context.
    
    Manages prompt construction, context integration, and response generation.
    """
    
    def __init__(self, llm_provider: BaseLLM):
        """
        Initialize orchestrator.
        
        Args:
            llm_provider: LLM provider instance (local or remote)
        """
        self.llm = llm_provider
        logger.info(f"Initialized LLMOrchestrator with provider: {type(llm_provider).__name__}")
    
    def answer_question(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Answer question using retrieved context.
        
        Args:
            query: User question
            context_chunks: Retrieved document chunks with metadata
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            
        Returns:
            Generated answer
        """
        # Build context from chunks
        context = self._build_context(context_chunks)
        
        # Build prompt
        prompt = self._build_prompt(query, context)
        
        logger.info(f"Generating answer for query: '{query[:50]}...'")
        logger.debug(f"Prompt length: {len(prompt)} chars")
        
        # Generate answer
        answer = self.llm.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        logger.info(f"Generated answer: {len(answer)} chars")
        return answer
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Build context string from retrieved chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, chunk in enumerate(chunks):
            filename = chunk.get("filename", "Unknown")
            chunk_text = chunk.get("chunk_text", "")
            page = chunk.get("page", "")
            
            # Format with source citation
            page_info = f", Page {page}" if page else ""
            source_info = f"[Source {i+1}: {filename}{page_info}]"
            
            context_parts.append(f"{source_info}\n{chunk_text}")
        
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build prompt for LLM.
        
        Args:
            query: User question
            context: Retrieved context
            
        Returns:
            Formatted prompt
        """
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context.

Context:
{context}

Question: {query}

Instructions:
- Answer the question using ONLY the information from the provided context
- If the context doesn't contain enough information to answer the question, say so
- Be concise and accurate
- Cite sources by referring to [Source X] when appropriate
- Do not make up information not present in the context

Answer:"""
        
        return prompt
    
    def summarize_context(
        self,
        context_chunks: List[Dict[str, Any]],
        max_tokens: int = 300
    ) -> str:
        """
        Generate a summary of the retrieved context.
        
        Args:
            context_chunks: Retrieved chunks
            max_tokens: Maximum summary tokens
            
        Returns:
            Summary text
        """
        context = self._build_context(context_chunks)
        
        prompt = f"""Summarize the following information concisely:

{context}

Summary:"""
        
        summary = self.llm.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.5
        )
        
        return summary
