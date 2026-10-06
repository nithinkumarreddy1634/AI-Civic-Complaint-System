"""Multi-modal evidence fusion and duplicate decision engine."""
from typing import Dict, Any, Optional
from .config import duplicate_config


def calculate_category_similarity(
    category_a: Optional[str],
    category_b: Optional[str],
) -> float:
    """
    Compute similarity between two civic issue categories.
    1.0 = exact match
    0.7 = category affinity group (e.g. pothole <-> damaged_road)
    0.0 = conflict (e.g. streetlight <-> garbage)
    """
    if not category_a or not category_b:
        return 0.5  # Neutral baseline if either is missing

    cat_a = category_a.lower().strip()
    cat_b = category_b.lower().strip()

    if cat_a == cat_b:
        return 1.0

    affinities = {
        "pothole": {"damaged_road", "damaged_sidewalk"},
        "damaged_road": {"pothole", "damaged_sidewalk"},
        "garbage": {"garbage_accumulation", "illegal_dumping"},
        "garbage_accumulation": {"garbage", "illegal_dumping"},
        "illegal_dumping": {"garbage", "garbage_accumulation"},
        "open_manhole": {"damaged_road"},
        "damaged_sidewalk": {"damaged_road", "pothole"},
        "water_leakage": {"damaged_road"},
        "fallen_tree": {"damaged_road"},
    }

    if cat_b in affinities.get(cat_a, set()):
        return 0.70

    return 0.0


def compute_duplicate_score(
    location_sim: Optional[float],
    image_sim: float,
    text_sim: float,
    category_sim: float,
    distance_meters: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute weighted composite duplicate score (0–100) and assign decision.

    Safety veto overrides:
    - If distance > 1000m, capped as NEW.
    - If category similarity is 0.0 (conflicting civic issues), capped as NEW.
    - Distance alone without visual or text confirmation never results in LIKELY_DUPLICATE.
    """
    cfg = duplicate_config
    has_location = location_sim is not None

    if has_location:
        w = cfg.weights
        composite = (
            w.location * location_sim
            + w.image * image_sim
            + w.text * text_sim
            + w.category * category_sim
        )
    else:
        w_no = cfg.no_location_weights
        composite = (
            w_no.image * image_sim
            + w_no.text * text_sim
            + w_no.category * category_sim
        )

    score = round(max(0.0, min(100.0, composite * 100.0)), 1)

    # Apply Safety Overrides
    reasons = []

    # Veto 1: Categorical conflict
    if category_sim == 0.0:
        score = min(score, 45.0)
        reasons.append("Categories conflict; cannot be duplicate.")

    # Veto 2: Excessive geographic separation
    if distance_meters is not None and distance_meters > cfg.geographic.max_duplicate_distance_meters:
        score = min(score, 30.0)
        reasons.append(f"Separation exceeds {cfg.geographic.max_duplicate_distance_meters}m limit.")

    # Veto 3: Low visual similarity with high distance
    if image_sim < 0.40 and (distance_meters is not None and distance_meters > 50.0):
        score = min(score, 55.0)
        reasons.append("Visual evidence indicates distinct scene.")

    # Map to Decision
    thresh = cfg.thresholds
    if score >= thresh.likely_duplicate:
        decision = "LIKELY_DUPLICATE"
    elif score >= thresh.possible_duplicate:
        decision = "POSSIBLE_DUPLICATE"
    else:
        decision = "NEW"

    return {
        "duplicate_score": score,
        "decision": decision,
        "location_similarity": location_sim,
        "image_similarity": image_sim,
        "text_similarity": text_sim,
        "category_similarity": category_sim,
        "distance_meters": distance_meters,
        "safety_reasons": reasons,
    }
