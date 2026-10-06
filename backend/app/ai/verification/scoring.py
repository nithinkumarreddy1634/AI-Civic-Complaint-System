"""Verification scoring engine, decision rules, and explainability generator.

Calculates multi-factor verification scores (0-100), applies essential safety
rules, and generates actionable, respectful explanations for citizen complaints.
"""
from typing import List, Dict, Any, Tuple
from .config import VerificationConfig, DEFAULT_VERIFICATION_CONFIG


def calculate_verification_score(
    quality_score: float,
    detection_conf: float,
    relevance_score: float,
    consistency_score: float,
    category_agreement_score: float,
    config: VerificationConfig = DEFAULT_VERIFICATION_CONFIG
) -> float:
    """Computes transparent weighted verification score (0.0 - 100.0)."""
    w = config.weights
    score = (
        (quality_score * w.image_quality) +
        (detection_conf * 100.0 * w.detection_confidence) +
        (relevance_score * w.civic_relevance) +
        (consistency_score * w.text_consistency) +
        (category_agreement_score * w.category_agreement)
    )
    return round(max(0.0, min(100.0, score)), 1)


def make_verification_decision(
    quality_result: Dict[str, Any],
    relevance_result: Dict[str, Any],
    consistency_result: Dict[str, Any],
    detections: List[Dict[str, Any]],
    text_result: Dict[str, Any],
    config: VerificationConfig = DEFAULT_VERIFICATION_CONFIG
) -> Tuple[str, float, List[str]]:
    """Evaluates all component evidence, enforces safety rules, and generates human explanation.

    Returns:
        (status, score, explanations)
        where status is 'VERIFIED', 'NEEDS_REVIEW', or 'REJECTED'.
    """
    quality_score = float(quality_result.get("quality_score", 0.0))
    quality_state = quality_result.get("status", "INVALID")

    relevance_score = float(relevance_result.get("relevance_score", 0.0))
    is_relevant = relevance_result.get("is_relevant", False)

    consistency_score = float(consistency_result.get("consistency_score", 0.0))
    consistency_matched = consistency_result.get("matched", False)

    category_agreement = consistency_result.get("category_match", True)
    category_agreement_score = 100.0 if category_agreement else 30.0

    # Detection confidence (max confidence among civic detections)
    civic_dets = [d for d in detections if d.get("class_name") in relevance_result.get("detected_issues", [])]
    max_conf = max((float(d.get("confidence", 0.0)) for d in civic_dets), default=0.0)

    # 1. Base mathematical verification score
    raw_score = calculate_verification_score(
        quality_score=quality_score,
        detection_conf=max_conf,
        relevance_score=relevance_score,
        consistency_score=consistency_score,
        category_agreement_score=category_agreement_score,
        config=config
    )

    explanations: List[str] = []
    status: str = "NEEDS_REVIEW"

    # =========================================================================
    # SAFETY OVERRIDE RULES & EXPLANATION BUILDER
    # =========================================================================

    # Rule 1: Fatal image corruption / unreadable image
    if quality_state == "INVALID":
        status = "REJECTED"
        raw_score = min(raw_score, 15.0)
        explanations.append("The uploaded image is unreadable, severely degraded, or corrupted.")
        if quality_result.get("issues"):
            explanations.append(f"Image issue details: {'; '.join(quality_result['issues'])}.")
        explanations.append("Please upload a clear photograph showing the infrastructure defect.")
        return status, raw_score, explanations

    # Rule 2: Zero detections
    if not detections or not is_relevant:
        if text_result.get("has_description") and text_result.get("text_categories"):
            status = "NEEDS_REVIEW"
            raw_score = min(raw_score, 55.0)
            explanations.append("No clear civic infrastructure defect was automatically identified in the photo.")
            explanations.append(f"However, your description notes: '{text_result.get('clean_text', '')}'.")
            explanations.append("A municipal officer will review your complaint manually.")
        else:
            status = "REJECTED"
            raw_score = min(raw_score, 25.0)
            explanations.append("No supported civic infrastructure defect was found in the image.")
            explanations.append("The submission lacked corroborating descriptive evidence.")
        return status, raw_score, explanations

    # Build standard positive evidence explanations
    detected_str = ", ".join(relevance_result.get("detected_issues", []))
    explanations.append(f"Detected infrastructure issue(s): {detected_str} (confidence: {max_conf * 100:.1f}%).")
    explanations.append(f"Image quality is assessed as {quality_state.lower()} (score: {int(quality_score)}/100).")

    if text_result.get("has_description"):
        if consistency_matched:
            explanations.append(f"Citizen description aligns with the visual findings ({consistency_result.get('explanation')}).")
        else:
            explanations.append(f"Discrepancy noted: {consistency_result.get('explanation')}.")

    # Rule 3: Image-Text severe conflict
    if text_result.get("has_description") and not consistency_matched and consistency_score < 40.0:
        status = "NEEDS_REVIEW"
        raw_score = min(raw_score, 68.0)
        explanations.append("Verification requires manual confirmation due to the contrast between image and text.")
        return status, raw_score, explanations

    # Rule 4: Borderline low confidence detection (between min veto and 0.45)
    if max_conf < 0.45:
        status = "NEEDS_REVIEW"
        raw_score = min(raw_score, 65.0)
        explanations.append(f"Detection confidence ({max_conf * 100:.1f}%) is borderline. Forwarded for human verification.")
        return status, raw_score, explanations

    # Rule 5: Borderline image quality (POOR state)
    if quality_state == "POOR":
        status = "NEEDS_REVIEW"
        raw_score = min(raw_score, 70.0)
        explanations.append("Image is slightly blurry or poorly lit; officer verification recommended.")
        return status, raw_score, explanations

    # Rule 6: Standard threshold evaluation
    if raw_score >= config.thresholds.verified:
        status = "VERIFIED"
        explanations.append("High confidence visual defect matches municipal criteria. Verified for prioritization.")
    elif raw_score >= config.thresholds.needs_review:
        status = "NEEDS_REVIEW"
        explanations.append("Moderate overall evidence score. Forwarded for supervisory review.")
    else:
        status = "REJECTED"
        explanations.append("Evidence is insufficient to automatically verify this civic infrastructure problem.")

    return status, raw_score, explanations
