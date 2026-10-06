"""Explainability module for AI civic complaint prioritization."""
from typing import Dict, Any, List
from app.ai.priority.priority_engine import PriorityEngineResult


class PriorityExplainer:
    """Produces clear, transparent, human-readable explanations of prioritization outcomes."""

    DISCLAIMER = (
        "Notice: This AI-generated priority score is an explainable decision-support metric "
        "designed to assist municipal dispatchers and triage teams; it does not replace "
        "professional civil engineering inspection or emergency protocols."
    )

    def generate_explanation(self, result: PriorityEngineResult) -> str:
        """Generate a structured, human-readable explanation from priority calculation results."""
        lines: List[str] = []

        level_str = result.priority_level.value
        score_str = f"{result.priority_score:.1f}/100"

        # Overview summary
        lines.append(f"Complaint assigned {level_str} priority with a composite score of {score_str}.")

        # Find top contributing factors
        active_factors = [
            (name, fc) for name, fc in result.factor_breakdown.items()
            if fc.status == "included" and fc.contribution > 0.0
        ]
        sorted_factors = sorted(active_factors, key=lambda x: x[1].contribution, reverse=True)

        if sorted_factors:
            top_factors = sorted_factors[:2]
            factor_summaries = [
                f"{name.replace('_', ' ').capitalize()} (contributing {fc.contribution:.1f} pts, score {fc.normalized_score:.1f})"
                for name, fc in top_factors
            ]
            lines.append(f"Primary driving factors: {'; '.join(factor_summaries)}.")

        # Duplicate frequency notice
        freq_factor = result.factor_breakdown.get("complaint_frequency")
        if freq_factor and freq_factor.raw_value and int(freq_factor.raw_value) > 1:
            raw_c = int(freq_factor.raw_value)
            lines.append(
                f"Duplicate clustering: Reinforced by {raw_c} citizen reports "
                f"(frequency factor contributes {freq_factor.contribution:.1f} pts via sublinear saturation curve)."
            )

        # Escalation notice
        if result.escalation_boost > 0.0:
            lines.append(
                f"Escalation adjustment: +{result.escalation_boost:.1f} pts aging boost "
                f"applied due to unresolved status."
            )

        # Missing GPS note
        if result.metadata.get("missing_gps_redistributed"):
            lines.append(
                "Geographic notice: GPS coordinates not provided; location weight was "
                "proportionately redistributed across remaining hazard factors without penalty."
            )

        # Append decision-support disclaimer
        lines.append(self.DISCLAIMER)

        return " ".join(lines)


priority_explainer = PriorityExplainer()
