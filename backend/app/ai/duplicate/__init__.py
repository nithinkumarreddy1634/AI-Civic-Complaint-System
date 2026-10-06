"""AI Duplicate Detection package."""
from .config import duplicate_config, DuplicateConfig
from .embedding_service import EmbeddingService
from .geospatial_similarity import calculate_haversine_distance, calculate_location_similarity
from .image_similarity import calculate_image_similarity, DISCLAIMER_IMAGE_SIMILARITY
from .text_similarity import calculate_text_similarity
from .scoring import calculate_category_similarity, compute_duplicate_score
from .candidate_search import find_duplicate_candidates
from .explainer import generate_duplicate_explanation
from .duplicate_service import DuplicateDetectionService

__all__ = [
    "duplicate_config",
    "DuplicateConfig",
    "EmbeddingService",
    "calculate_haversine_distance",
    "calculate_location_similarity",
    "calculate_image_similarity",
    "DISCLAIMER_IMAGE_SIMILARITY",
    "calculate_text_similarity",
    "calculate_category_similarity",
    "compute_duplicate_score",
    "find_duplicate_candidates",
    "generate_duplicate_explanation",
    "DuplicateDetectionService",
]
