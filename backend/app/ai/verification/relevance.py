"""Civic relevance determination module.

Checks whether object detections belong to the verified municipal infrastructure
problem taxonomy and computes an overall relevance score.
"""
from typing import List, Dict, Any, Set
from .config import SUPPORTED_CIVIC_CATEGORIES


def check_civic_relevance(detections: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyzes a list of vision detections and assesses municipal infrastructure relevance.

    Args:
        detections: List of detection dicts containing 'class_name' and 'confidence'.

    Returns:
        Dict with:
            is_relevant: bool
            relevance_score: float (0.0 to 100.0)
            detected_issues: list[str] (names of valid civic defect classes detected)
            irrelevant_detections: list[str]
            explanation: str
    """
    if not detections:
        return {
            "is_relevant": False,
            "relevance_score": 0.0,
            "detected_issues": [],
            "irrelevant_detections": [],
            "explanation": "No objects or infrastructure defects were detected in the image."
        }

    detected_civic_issues: List[Dict[str, Any]] = []
    irrelevant_detections: List[str] = []

    for d in detections:
        cls_name = str(d.get("class_name", "")).lower().strip()
        conf = float(d.get("confidence", 0.0))

        if cls_name in SUPPORTED_CIVIC_CATEGORIES:
            detected_civic_issues.append({"class": cls_name, "conf": conf})
        else:
            irrelevant_detections.append(cls_name)

    if not detected_civic_issues:
        return {
            "is_relevant": False,
            "relevance_score": 0.0,
            "detected_issues": [],
            "irrelevant_detections": irrelevant_detections,
            "explanation": f"Detected objects ({', '.join(irrelevant_detections) or 'unrecognized'}) do not represent municipal infrastructure defects."
        }

    # Compute relevance score weighted by the highest detection confidence
    max_conf = max(item["conf"] for item in detected_civic_issues)
    distinct_civic_classes = sorted(list(set(item["class"] for item in detected_civic_issues)))

    # Bonus for multiple corroborating detections
    multi_issue_bonus = min(10.0, (len(detected_civic_issues) - 1) * 3.0)
    relevance_score = min(100.0, (max_conf * 90.0) + multi_issue_bonus)

    # Penalty if dominated by irrelevant objects
    if irrelevant_detections and len(irrelevant_detections) > len(detected_civic_issues):
        relevance_score *= 0.85

    return {
        "is_relevant": True,
        "relevance_score": round(relevance_score, 2),
        "detected_issues": distinct_civic_classes,
        "irrelevant_detections": irrelevant_detections,
        "explanation": f"Detected valid civic infrastructure issue(s): {', '.join(distinct_civic_classes)} (confidence: {max_conf*100:.1f}%)."
    }
