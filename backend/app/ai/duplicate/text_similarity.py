"""Text description semantic similarity comparison."""
from typing import List, Dict, Any
import numpy as np


def calculate_text_similarity(
    embedding_a: List[float],
    embedding_b: List[float],
) -> Dict[str, Any]:
    """
    Compute semantic cosine similarity between two text description embeddings.

    Args:
        embedding_a: Semantic vector for description A.
        embedding_b: Semantic vector for description B.

    Returns:
        Dict with:
            - text_similarity: float (0.0 to 1.0)
            - is_high_semantic_match: bool (>= 0.75)
    """
    if not embedding_a or not embedding_b or len(embedding_a) != len(embedding_b):
        return {
            "text_similarity": 0.0,
            "is_high_semantic_match": False,
        }

    vec_a = np.array(embedding_a, dtype=np.float32)
    vec_b = np.array(embedding_b, dtype=np.float32)

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a < 1e-12 or norm_b < 1e-12:
        return {
            "text_similarity": 0.0,
            "is_high_semantic_match": False,
        }

    cos_sim = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    normalized_sim = round(max(0.0, min(1.0, cos_sim)), 4)
    is_high = normalized_sim >= 0.75

    return {
        "text_similarity": normalized_sim,
        "is_high_semantic_match": is_high,
    }
