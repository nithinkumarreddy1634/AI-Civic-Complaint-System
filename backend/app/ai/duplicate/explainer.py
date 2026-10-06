"""Explainability generator for duplicate complaint detection decisions."""
from typing import List, Dict, Any, Optional


def generate_duplicate_explanation(
    decision: str,
    duplicate_score: float,
    best_candidate: Optional[Dict[str, Any]] = None,
) -> List[str]:
    """
    Generate transparent, evidence-based bullet explanations for duplicate decisions.
    """
    if not best_candidate or decision == "NEW":
        return [
            "No existing complaint exhibited sufficiently strong combined visual, textual, and spatial similarity.",
            "Classified as an independent, new infrastructure complaint.",
        ]

    explanations = []
    dist = best_candidate.get("distance_meters")
    img_sim = best_candidate.get("image_similarity", 0.0)
    txt_sim = best_candidate.get("text_similarity", 0.0)
    cat_sim = best_candidate.get("category_similarity", 0.0)
    cat_name = best_candidate.get("category", "civic issue")

    # 1. Geographic observation
    if dist is not None:
        if dist <= 50.0:
            explanations.append(f"The complaints are in close geographic proximity ({dist:.1f} meters apart).")
        else:
            explanations.append(f"The complaints are located {dist:.1f} meters apart within the candidate search radius.")
    else:
        explanations.append("Geographic distance comparison omitted due to missing GPS coordinates.")

    # 2. Visual similarity observation
    if img_sim >= 0.85:
        explanations.append(f"Images exhibit high visual similarity ({img_sim * 100:.1f}% visual match).")
    elif img_sim >= 0.60:
        explanations.append(f"Images show moderate visual resemblance ({img_sim * 100:.1f}% visual match).")
    else:
        explanations.append(f"Low visual similarity between compared photographs ({img_sim * 100:.1f}%).")

    # 3. Category comparison
    if cat_sim == 1.0:
        explanations.append(f"Both reports concern the identical civic defect category ('{cat_name}').")
    elif cat_sim >= 0.70:
        explanations.append(f"Reports concern affiliated defect categories ('{cat_name}').")
    else:
        explanations.append("Reports reference distinct defect types.")

    # 4. Textual semantic description
    if txt_sim >= 0.75:
        explanations.append(f"Citizen descriptions have high semantic overlap ({txt_sim * 100:.1f}% text similarity).")
    elif txt_sim >= 0.50:
        explanations.append(f"Descriptions share moderate contextual problem phrasing ({txt_sim * 100:.1f}%).")

    # 5. Summary conclusion
    if decision == "LIKELY_DUPLICATE":
        explanations.append("High multi-modal evidence supports linking this submission as a duplicate incident.")
    elif decision == "POSSIBLE_DUPLICATE":
        explanations.append("Moderate evidence indicates this complaint may reference the same incident; flagged for review.")

    return explanations
