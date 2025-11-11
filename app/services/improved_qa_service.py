"""
Improved RAG pipeline with reranker and grounded prompts.
Implements all high-ROI fixes from the checklist.
"""

from typing import List, Dict, Any, Optional
import time

from app.core.retrieval.retriever import SemanticRetriever
from app.core.retrieval.reranker import get_reranker
from app.core.llm.remote_llm import get_llm
from app.core.llm.orchestrator import LLMOrchestrator
from app.utils.logger import app_logger as logger


def build_grounded_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    """
    Build a grounded prompt that forces LLM to only use provided context.
    
    Args:
        question: User question
        chunks: Retrieved and reranked chunks with metadata
        
    Returns:
        Formatted prompt with strict grounding instructions
    """
    # Build context block with clear source citations
    ctx_parts = []
    for i, chunk in enumerate(chunks, start=1):
        source = chunk.get('filename', 'Unknown')
        chunk_id = chunk.get('chunk_id', 'N/A')
        doc_id = chunk.get('doc_id', 'N/A')
        text = chunk.get('chunk_text', '')
        
        ctx_parts.append(
            f"[DOCUMENT {i}]\n"
            f"Source: {source}\n"
            f"ID: doc={doc_id}, chunk={chunk_id}\n"
            f"Content:\n{text}\n"
        )
    
    context_block = "\n".join(ctx_parts)
    
    # Strict system instruction
    system = """You are a helpful assistant that MUST ONLY use the CONTEXT documents provided below to answer questions.

CRITICAL RULES:
1. ONLY use information from the CONTEXT - do not use external knowledge
2. If the answer is not in the CONTEXT, respond EXACTLY: "I don't know from the provided documents."
3. Be specific and cite which document(s) you used
4. Quote relevant parts when possible
5. If partially answered, say what you know and what's missing

FORMAT:
Answer: [Your answer based on context]
Sources: [List document numbers used, e.g., "Documents 1, 3"]"""
    
    # Assemble full prompt
    prompt = f"""{system}

CONTEXT:
{context_block}

QUESTION: {question}

Answer:"""
    
    return prompt


class ImprovedRAGPipeline:
    """
    Enhanced RAG pipeline with cross-encoder reranking and grounded generation.
    """
    
    def __init__(
        self,
        use_reranker: bool = True,
        top_k_retrieval: int = 50,
        top_k_final: int = 4,
        similarity_threshold: float = 0.10
    ):
        """
        Initialize improved pipeline.
        
        Args:
            use_reranker: Whether to use cross-encoder reranking
            top_k_retrieval: Initial retrieval count (bi-encoder)
            top_k_final: Final count after reranking
            similarity_threshold: Minimum similarity for bi-encoder
        """
        self.use_reranker = use_reranker
        self.top_k_retrieval = top_k_retrieval
        self.top_k_final = top_k_final
        self.similarity_threshold = similarity_threshold
        
        # Initialize components
        self.retriever = SemanticRetriever(
            top_k=top_k_retrieval,
            similarity_threshold=similarity_threshold
        )
        
        if use_reranker:
            self.reranker = get_reranker()
            logger.info("Initialized pipeline WITH cross-encoder reranker")
        else:
            self.reranker = None
            logger.info("Initialized pipeline WITHOUT reranker")
        
        self.llm = get_llm()
        self.orchestrator = LLMOrchestrator(self.llm)
    
    def answer_question(
        self,
        question: str,
        temperature: float = 0.0,
        max_tokens: int = 512,
        log_prompt: bool = True
    ) -> Dict[str, Any]:
        """
        Answer question using improved pipeline.
        
        Args:
            question: User question
            temperature: LLM temperature (0 = deterministic)
            max_tokens: Maximum response tokens
            log_prompt: Whether to log full prompt (for debugging)
            
        Returns:
            Dict with answer, sources, chunks, and metadata
        """
        start_time = time.time()
        
        # Step 1: Bi-encoder retrieval
        logger.info(f"Step 1: Retrieving top-{self.top_k_retrieval} candidates")
        candidates = self.retriever.search(
            question,
            top_k=self.top_k_retrieval,
            min_score=self.similarity_threshold
        )
        
        if not candidates:
            logger.warning(f"No candidates found with threshold {self.similarity_threshold}")
            return {
                'success': False,
                'answer': "No relevant documents found. Try lowering the similarity threshold.",
                'sources': [],
                'chunks': [],
                'retrieval_count': 0,
                'processing_time': time.time() - start_time
            }
        
        retrieval_time = time.time() - start_time
        logger.info(
            f"Retrieved {len(candidates)} candidates "
            f"(scores: {candidates[0]['score']:.3f} to {candidates[-1]['score']:.3f})"
        )
        
        # Step 2: Rerank with cross-encoder (if enabled)
        if self.use_reranker and self.reranker:
            rerank_start = time.time()
            logger.info(f"Step 2: Reranking top-{self.top_k_final} with cross-encoder")
            
            top_chunks = self.reranker.rerank(
                question,
                candidates,
                top_k=self.top_k_final
            )
            
            rerank_time = time.time() - rerank_start
            logger.info(
                f"Reranked to {len(top_chunks)} chunks "
                f"(rerank scores: {top_chunks[0]['rerank_score']:.3f} to {top_chunks[-1]['rerank_score']:.3f})"
            )
        else:
            top_chunks = candidates[:self.top_k_final]
            rerank_time = 0
            logger.info(f"Step 2: Skipped reranking, using top-{self.top_k_final} from retrieval")
        
        # Step 3: Build grounded prompt
        logger.info("Step 3: Building grounded prompt")
        prompt = build_grounded_prompt(question, top_chunks)
        
        if log_prompt:
            logger.info(f"Full prompt ({len(prompt)} chars):")
            logger.info("="*80)
            logger.info(prompt[:1000] + ("..." if len(prompt) > 1000 else ""))
            logger.info("="*80)
        
        # Step 4: Generate answer with LLM
        llm_start = time.time()
        logger.info(f"Step 4: Generating answer (temperature={temperature})")
        
        # Use the prompt directly - bypass orchestrator's prompt building
        answer = self.llm.generate(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        llm_time = time.time() - llm_start
        
        total_time = time.time() - start_time
        
        logger.info(
            f"Answer generated: {len(answer)} chars "
            f"(retrieval: {retrieval_time:.2f}s, rerank: {rerank_time:.2f}s, llm: {llm_time:.2f}s, total: {total_time:.2f}s)"
        )
        
        # Extract sources
        sources = [
            {
                'document': chunk['filename'],
                'doc_id': chunk['doc_id'],
                'chunk_id': chunk['chunk_id'],
                'score': chunk.get('rerank_score', chunk.get('score', 0))
            }
            for chunk in top_chunks
        ]
        
        return {
            'success': True,
            'answer': answer.strip(),
            'sources': sources,
            'chunks': top_chunks,
            'retrieval_count': len(candidates),
            'final_count': len(top_chunks),
            'processing_time': total_time,
            'timing': {
                'retrieval': retrieval_time,
                'rerank': rerank_time,
                'llm': llm_time,
                'total': total_time
            }
        }
    
    def verify_answer(
        self,
        answer: str,
        question: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Verify that answer is grounded in provided chunks.
        
        This is a simple implementation - can be enhanced with NER and claim extraction.
        
        Args:
            answer: Generated answer
            question: Original question
            chunks: Chunks that were provided to LLM
            
        Returns:
            Dict with verification results
        """
        # Check if answer says "I don't know"
        if "don't know" in answer.lower() or "not in" in answer.lower():
            return {
                'verified': True,
                'reason': 'LLM correctly stated information not available',
                'confidence': 1.0
            }
        
        # Simple verification: check if answer words appear in chunks
        answer_words = set(answer.lower().split())
        chunk_text = " ".join([c['chunk_text'] for c in chunks]).lower()
        chunk_words = set(chunk_text.split())
        
        overlap = answer_words.intersection(chunk_words)
        coverage = len(overlap) / len(answer_words) if answer_words else 0
        
        verified = coverage > 0.5  # At least 50% of answer words in context
        
        return {
            'verified': verified,
            'coverage': coverage,
            'reason': f'{coverage*100:.1f}% of answer words found in context',
            'confidence': coverage
        }


def get_improved_pipeline(use_reranker: bool = True) -> ImprovedRAGPipeline:
    """Get improved pipeline instance."""
    return ImprovedRAGPipeline(use_reranker=use_reranker)

