"""Image visual similarity comparison using vector cosine distance."""
from typing import List, Dict, Any
import numpy as np


DISCLAIMER_IMAGE_SIMILARITY = (
    "Image similarity measures visual resemblance in color, texture, and spatial composition. "
    "Distinct defects belonging to the same category may share visual similarity; "
    "visual similarity must be evaluated alongside location and category."
)


def calculate_image_similarity(
    embedding_a: List[float],
    embedding_b: List[float],
) -> Dict[str, Any]:
    """
    Compute cosine similarity between two normalized image embeddings.

    Args:
        embedding_a: Float vector representing image A.
        embedding_b: Float vector representing image B.

    Returns:
        Dict with:
            - image_similarity: float (0.0 to 1.0)
            - is_high_visual_match: bool (>= 0.85)
            - disclaimer: str
    """
    if not embedding_a or not embedding_b or len(embedding_a) != len(embedding_b):
        return {
            "image_similarity": 0.0,
            "is_high_visual_match": False,
            "disclaimer": DISCLAIMER_IMAGE_SIMILARITY,
        }

    vec_a = np.array(embedding_a, dtype=np.float32)
    vec_b = np.array(embedding_b, dtype=np.float32)

    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)

    if norm_a < 1e-12 or norm_b < 1e-12:
        return {
            "image_similarity": 0.0,
            "is_high_visual_match": False,
            "disclaimer": DISCLAIMER_IMAGE_SIMILARITY,
        }

    cos_sim = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    # Clamp negative cosine values to 0.0
    normalized_sim = round(max(0.0, min(1.0, cos_sim)), 4)
    is_high = normalized_sim >= 0.85

    return {
        "image_similarity": normalized_sim,
        "is_high_visual_match": is_high,
        "disclaimer": DISCLAIMER_IMAGE_SIMILARITY,
    }
