"""Image-Text Cross-Modal Consistency & Category Matching Engine.

Measures semantic alignment between Computer Vision detections, NLP text extraction,
and citizen-selected category.
"""
from typing import List, Dict, Any, Optional, Set
from .config import CATEGORY_AFFINITY_GROUPS


def are_categories_affiliated(cat1: str, cat2: str) -> bool:
    """Checks whether two categories belong to the same conceptual affinity group."""
    if cat1 == cat2:
        return True
    for group in CATEGORY_AFFINITY_GROUPS:
        if cat1 in group and cat2 in group:
            return True
    return False


def evaluate_consistency(
    vision_detections: List[Dict[str, Any]],
    text_categories: List[Dict[str, Any]],
    user_selected_category: Optional[str] = None
) -> Dict[str, Any]:
    """Computes cross-modal consistency score and category agreement flags.

    Args:
        vision_detections: List of vision detection dicts with 'class_name' and 'confidence'.
        text_categories: List of text category dicts with 'category' and 'confidence'.
        user_selected_category: Optional category selected by citizen in submission form.

    Returns:
        Dict with consistency_score, matched, vision_category, text_category,
        category_match, and explainable description.
    """
    vision_classes = [d.get("class_name", "").lower() for d in vision_detections if d.get("class_name")]
    primary_vision_class = vision_classes[0] if vision_classes else None

    text_classes = [t.get("category", "").lower() for t in text_categories if t.get("category")]
    primary_text_class = text_classes[0] if text_classes else None

    user_cat = user_selected_category.lower().strip() if user_selected_category else None

    # Case 1: No vision detections
    if not primary_vision_class:
        return {
            "consistency_score": 20.0 if primary_text_class else 0.0,
            "matched": False,
            "vision_category": None,
            "text_category": primary_text_class,
            "selected_category": user_cat,
            "category_match": False,
            "explanation": "No visual defect was detected to compare with the text description."
        }

    # Case 2: Vision detected, but no text description provided
    if not primary_text_class:
        # Check against user selected category if present
        if user_cat:
            match_selected = (user_cat == primary_vision_class)
            affiliated_selected = are_categories_affiliated(user_cat, primary_vision_class)
            score = 85.0 if match_selected else (65.0 if affiliated_selected else 35.0)
            return {
                "consistency_score": score,
                "matched": match_selected or affiliated_selected,
                "vision_category": primary_vision_class,
                "text_category": None,
                "selected_category": user_cat,
                "category_match": match_selected,
                "explanation": f"No text description provided; visual detection ({primary_vision_class}) {'matches' if match_selected else 'differs from'} selected category ({user_cat})."
            }
        else:
            # Default neutral consistency when text is omitted
            return {
                "consistency_score": 70.0,
                "matched": True,
                "vision_category": primary_vision_class,
                "text_category": None,
                "selected_category": None,
                "category_match": True,
                "explanation": "No text description provided; relying solely on visual detection."
            }

    # Case 3: Both vision and text categories present
    exact_match = (primary_vision_class in text_classes) or (primary_text_class in vision_classes)
    affinity_match = any(are_categories_affiliated(v, t) for v in vision_classes for t in text_classes)

    if exact_match:
        consistency_score = 95.0
        matched = True
        explanation = f"Detected {primary_vision_class} is directly confirmed by the citizen description."
    elif affinity_match:
        consistency_score = 75.0
        matched = True
        explanation = f"Detected {primary_vision_class} is related to issues described in the text ({primary_text_class})."
    else:
        # Conflict
        consistency_score = 25.0
        matched = False
        explanation = f"Visual detection ({primary_vision_class}) conflicts with citizen description ({primary_text_class})."

    # Evaluate user-selected category agreement against detected vision issue
    category_match = True
    if user_cat:
        agreement = (user_cat == primary_vision_class) or are_categories_affiliated(user_cat, primary_vision_class)
        if agreement:
            consistency_score = min(100.0, consistency_score + 5.0)
            category_match = True
        else:
            category_match = False
            consistency_score = max(10.0, consistency_score - 15.0)
            explanation += f" Note: Citizen selected category was '{user_cat}'."

    return {
        "consistency_score": round(consistency_score, 1),
        "matched": matched,
        "vision_category": primary_vision_class,
        "text_category": primary_text_class,
        "selected_category": user_cat,
        "category_match": category_match,
        "explanation": explanation
    }
