"""Damage extent analysis using 2D Computer Vision bounding box geometry."""
import math
from typing import Dict, Any, List, Union, Tuple, Optional
from .config import severity_config


DISCLAIMER_DAMAGE_EXTENT = (
    "Damage extent is an algorithmic approximation based on 2D bounding box surface coverage. "
    "It does not represent physical depth, volume, or structural load capacity."
)


def calculate_damage_extent(
    bbox: Union[List[float], Tuple[float, float, float, float]],
    image_width: int,
    image_height: int,
    max_reference_ratio: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate the relative damage extent score from a 2D bounding box and image dimensions.

    Formula:
        damage_area_ratio = bounding_box_area / image_area

    The raw ratio is mapped to a normalized 0–100 score using square-root scaling
    anchored at `max_reference_ratio` (default 0.15, meaning 15% surface coverage
    corresponds to maximum visual disruption).

    Args:
        bbox: Bounding box coordinates [x_min, y_min, x_max, y_max] in pixels.
        image_width: Image width in pixels.
        image_height: Image height in pixels.
        max_reference_ratio: Coverage ratio that saturates to 100.0 score.

    Returns:
        Dict containing:
            - damage_extent_score: float (0.0 to 100.0)
            - damage_area_ratio: float (0.0 to 1.0)
            - bbox_area: float (pixels^2)
            - image_area: float (pixels^2)
            - is_significant: bool
            - disclaimer: str
    """
    cfg = severity_config.damage_extent
    ref_ratio = max_reference_ratio if max_reference_ratio is not None else cfg.max_reference_ratio

    # Validate image dimensions
    if not image_width or not image_height or image_width <= 0 or image_height <= 0:
        return {
            "damage_extent_score": cfg.min_score,
            "damage_area_ratio": 0.0,
            "bbox_area": 0.0,
            "image_area": 0.0,
            "is_significant": False,
            "disclaimer": DISCLAIMER_DAMAGE_EXTENT,
        }

    image_area = float(image_width * image_height)

    # Validate bounding box
    if not bbox or len(bbox) < 4:
        return {
            "damage_extent_score": cfg.min_score,
            "damage_area_ratio": 0.0,
            "bbox_area": 0.0,
            "image_area": image_area,
            "is_significant": False,
            "disclaimer": DISCLAIMER_DAMAGE_EXTENT,
        }

    x_min, y_min, x_max, y_max = [float(c) for c in bbox[:4]]

    # Ensure min <= max
    if x_min > x_max:
        x_min, x_max = x_max, x_min
    if y_min > y_max:
        y_min, y_max = y_max, y_min

    # Clamp coordinates to image boundaries
    x_min = max(0.0, min(x_min, float(image_width)))
    x_max = max(0.0, min(x_max, float(image_width)))
    y_min = max(0.0, min(y_min, float(image_height)))
    y_max = max(0.0, min(y_max, float(image_height)))

    bbox_width = x_max - x_min
    bbox_height = y_max - y_min
    bbox_area = bbox_width * bbox_height

    if bbox_area <= 0.0:
        return {
            "damage_extent_score": cfg.min_score,
            "damage_area_ratio": 0.0,
            "bbox_area": 0.0,
            "image_area": image_area,
            "is_significant": False,
            "disclaimer": DISCLAIMER_DAMAGE_EXTENT,
        }

    ratio = bbox_area / image_area
    ratio = min(1.0, max(0.0, ratio))

    # Square-root perceptual normalization:
    # A damage ratio of 1% (0.01) -> ~25 score
    # A damage ratio of 5% (0.05) -> ~57 score
    # A damage ratio of 15% (0.15) -> 100 score
    if ref_ratio > 0.0:
        normalized_ratio = min(1.0, ratio / ref_ratio)
        score = math.sqrt(normalized_ratio) * 100.0
    else:
        score = ratio * 100.0

    score = round(max(cfg.min_score, min(cfg.max_score, score)), 1)
    is_significant = score >= 50.0

    return {
        "damage_extent_score": score,
        "damage_area_ratio": round(ratio, 4),
        "bbox_area": round(bbox_area, 1),
        "image_area": round(image_area, 1),
        "is_significant": is_significant,
        "disclaimer": DISCLAIMER_DAMAGE_EXTENT,
    }
