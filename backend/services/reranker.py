"""
Snippet Reranker using Cross-Encoder for semantic similarity scoring.

This module provides a reranking layer for RAG (Retrieval Augmented Generation)
that filters snippets by semantic relevance before sending to the LLM.

Author: Louis Inference System
Date: 05/Out/2025
"""

import logging
from typing import List, Tuple
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


class SnippetReranker:
    """
    Reranks text snippets by semantic relevance to a query using a cross-encoder model.

    Uses lazy loading pattern to avoid loading the model until first use,
    reducing memory footprint and startup time.

    Attributes:
        model_name (str): Name of the cross-encoder model from HuggingFace
        _model (CrossEncoder): Lazy-loaded cross-encoder instance

    Example:
        >>> reranker = SnippetReranker()
        >>> snippets = ["text1", "text2", "text3"]
        >>> query = "clinical query"
        >>> top_snippets = reranker.rerank_simple(query, snippets, top_k=2)
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initialize reranker with specified cross-encoder model.

        Args:
            model_name: HuggingFace model identifier for cross-encoder.
                       Default: ms-marco-MiniLM-L-6-v2 (22MB, CPU-friendly)

        Note:
            Model is NOT loaded during __init__ (lazy loading).
            First call to rerank() will trigger model loading.
        """
        self.model_name = model_name
        self._model = None
        logger.info(f"SnippetReranker initialized with model={model_name} (lazy loading)")

    @property
    def model(self) -> CrossEncoder:
        """
        Lazy-load the cross-encoder model on first access.

        Returns:
            CrossEncoder: Loaded cross-encoder model instance

        Raises:
            Exception: If model loading fails (network, disk, etc)
        """
        if self._model is None:
            logger.info(f"Loading cross-encoder model: {self.model_name}")
            try:
                self._model = CrossEncoder(self.model_name)
                logger.info(f"Model loaded successfully: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
        return self._model

    def rerank(
        self,
        query: str,
        snippets: List[str],
        top_k: int = 5
    ) -> Tuple[List[str], List[float]]:
        """
        Rerank snippets by semantic relevance to query, return top-k with scores.

        Args:
            query: Clinical text or search query
            snippets: List of text snippets to rerank
            top_k: Number of top snippets to return (default: 5)

        Returns:
            Tuple containing:
                - List of top-k snippets (most relevant first)
                - List of corresponding scores (float, higher = more relevant)

        Raises:
            ValueError: If snippets list is empty
            Exception: If model prediction fails

        Example:
            >>> top_snippets, scores = reranker.rerank(query, snippets, top_k=3)
            >>> for snippet, score in zip(top_snippets, scores):
            ...     print(f"Score: {score:.4f} - {snippet[:50]}...")
        """
        if not snippets:
            logger.warning("rerank() called with empty snippets list")
            return [], []

        # If requesting more than available, return all
        if top_k >= len(snippets):
            logger.info(f"top_k={top_k} >= len(snippets)={len(snippets)}, returning all")
            return snippets, [1.0] * len(snippets)

        try:
            # Create query-snippet pairs for cross-encoder
            pairs = [[query, snippet] for snippet in snippets]

            # Score all pairs (returns list of floats)
            logger.info(f"Scoring {len(pairs)} query-snippet pairs")
            scores = self.model.predict(pairs)

            # Sort by score descending (highest first)
            scored_snippets = list(zip(snippets, scores))
            scored_snippets.sort(key=lambda x: x[1], reverse=True)

            # Extract top-k snippets and scores
            top_snippets = [snippet for snippet, _ in scored_snippets[:top_k]]
            top_scores = [score for _, score in scored_snippets[:top_k]]

            logger.info(
                f"Reranking complete: {len(snippets)} → {len(top_snippets)} snippets "
                f"(score range: {min(top_scores):.4f} to {max(top_scores):.4f})"
            )

            return top_snippets, top_scores

        except Exception as e:
            logger.error(f"Reranking failed: {e}", exc_info=True)
            # Fallback: return first top_k snippets without reranking
            logger.warning(f"Fallback: returning first {top_k} snippets without reranking")
            return snippets[:top_k], [0.0] * top_k

    def rerank_simple(
        self,
        query: str,
        snippets: List[str],
        top_k: int = 5
    ) -> List[str]:
        """
        Rerank snippets and return only top-k (without scores).

        Convenience method for cases where scores are not needed.

        Args:
            query: Clinical text or search query
            snippets: List of text snippets to rerank
            top_k: Number of top snippets to return (default: 5)

        Returns:
            List of top-k snippets (most relevant first)

        Example:
            >>> top_snippets = reranker.rerank_simple(query, snippets, top_k=5)
            >>> context = '\n\n'.join(top_snippets)
        """
        top_snippets, _ = self.rerank(query, snippets, top_k)
        return top_snippets


# Global singleton instance (lazy-loaded)
# Import this in inference_service.py: from backend.services.reranker import reranker
reranker = SnippetReranker()


if __name__ == "__main__":
    # Quick test when running directly
    logging.basicConfig(level=logging.INFO)

    test_query = "Paciente com hemiparesia esquerda"
    test_snippets = [
        "A síndrome de circulação anterior total envolve hemiparesia contralateral.",
        "A cefaleia em salvas causa dor periorbital unilateral intensa.",
        "O acidente vascular cerebral isquêmico pode causar déficits motores súbitos.",
        "A enxaqueca com aura pode apresentar sintomas visuais transitórios.",
        "A síndrome de Wallenberg afeta o bulbo e causa múltiplos sintomas.",
    ]

    reranker_test = SnippetReranker()
    top_snippets, scores = reranker_test.rerank(test_query, test_snippets, top_k=2)

    print("\n=== Reranking Test Results ===")
    print(f"Query: {test_query}\n")
    print(f"Top {len(top_snippets)} snippets:")
    for i, (snippet, score) in enumerate(zip(top_snippets, scores), 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   {snippet}\n")
