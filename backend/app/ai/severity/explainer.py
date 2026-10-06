"""Explainability generator for severity assessment decisions."""
from typing import List, Dict, Any


AI_DECISION_SUPPORT_NOTICE = (
    "Note: Severity score is an AI-assisted decision-support assessment based on visual and textual "
    "evidence. It does not constitute a certified structural, civil engineering, or safety inspection."
)


def generate_severity_explanation(
    category: str,
    severity_level: str,
    severity_score: float,
    damage_extent_score: float,
    detection_confidence: float,
    safety_risk_score: float,
    infrastructure_impact_score: float,
    public_impact_score: float,
    detection_count: int = 1,
    text_cues: List[str] = None,
    disclaimer: str = "",
) -> List[str]:
    """
    Generate clear, defensible, human-readable explanation bullet points.

    Adheres to ethical guidelines:
    - Never predicts guaranteed accidents or structural collapses.
    - Accurately cites observable 2D surface coverage proxies.
    - Incorporates detection confidence and user text confirmation.
    """
    explanations = []

    # 1. Detection summary
    conf_pct = round(detection_confidence * 100.0, 1)
    if detection_count > 1:
        explanations.append(
            f"Detected {detection_count} {category} issue regions with primary model confidence of {conf_pct}%."
        )
    else:
        explanations.append(
            f"Detected primary issue '{category}' with model confidence of {conf_pct}%."
        )

    # 2. Damage extent explanation
    if damage_extent_score >= 70.0:
        explanations.append(
            "Visible damage occupies a substantial portion of the captured frame, indicating extensive surface disruption."
        )
    elif damage_extent_score >= 40.0:
        explanations.append(
            "Visible defect covers a moderate portion of the infrastructure surface area."
        )
    else:
        explanations.append(
            "Visual damage is localized to a small portion of the captured frame."
        )

    # 3. Safety & Impact observations
    if safety_risk_score >= 75.0:
        explanations.append(
            f"Potential safety risk is elevated ({safety_risk_score}/100) based on observed defect category and extent."
        )
    elif safety_risk_score >= 45.0:
        explanations.append(
            f"Moderate safety concern ({safety_risk_score}/100) under standard transit conditions."
        )

    if infrastructure_impact_score >= 70.0:
        explanations.append(
            f"Infrastructure impact is elevated ({infrastructure_impact_score}/100), reflecting significant degradation."
        )

    # 4. Text cues corroboration
    if text_cues:
        explanations.append(
            f"Citizen description corroborates urgency with terms: {', '.join(text_cues[:3])}."
        )

    # 5. Category-specific disclaimer if available
    if disclaimer:
        explanations.append(f"Technical note: {disclaimer}")

    # 6. Overall decision support notice
    explanations.append(AI_DECISION_SUPPORT_NOTICE)

    return explanations
