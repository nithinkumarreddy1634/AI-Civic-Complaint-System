"""Text-based severity signal extraction from complaint descriptions."""
import re
from typing import Dict, Any, List, Optional

# Severity modifier patterns and their weights
HIGH_SEVERITY_KEYWORDS = {
    r"\b(danger(ous)?|hazardous|unsafe|perilous)\b": 85.0,
    r"\b(blocked|impassable|unpassable|obstruct(ed|ing)?)\b": 80.0,
    r"\b(huge|massive|giant|colossal|enormous|deep)\b": 75.0,
    r"\b(sever(e|ely)|critical|acute|emergency)\b": 85.0,
    r"\b(collapse(d)?|cave[- ]?in|caved in|sinkhole)\b": 90.0,
    r"\b(broken completely|completely damaged|destroyed)\b": 80.0,
    r"\b(multiple|several|numerous|cluster|many)\b": 65.0,
    r"\b(flood(ed|ing)?|overflow(ing)?|burst)\b": 75.0,
}

LOW_SEVERITY_KEYWORDS = {
    r"\b(small|minor|slight|tiny|hairline)\b": 25.0,
    r"\b(starting to|forming|early stage)\b": 35.0,
    r"\b(shallow|little)\b": 30.0,
}


def extract_text_severity_signal(description: Optional[str]) -> Dict[str, Any]:
    """
    Extract a normalized severity signal (0–100) from the citizen's text description.

    Returns:
        Dict with:
            - text_severity_score: float (0.0 to 100.0)
            - high_severity_cues: List[str]
            - low_severity_cues: List[str]
            - explanation: str
    """
    if not description or not description.strip():
        return {
            "text_severity_score": 50.0,  # Neutral baseline
            "high_severity_cues": [],
            "low_severity_cues": [],
            "explanation": "No text description provided; neutral severity assumption."
        }

    text_lower = description.lower()
    high_matches = []
    low_matches = []
    high_scores = []
    low_scores = []

    for pattern, score in HIGH_SEVERITY_KEYWORDS.items():
        found = re.findall(pattern, text_lower)
        if found:
            high_scores.append(score)
            match_word = found[0][0] if isinstance(found[0], tuple) else found[0]
            high_matches.append(match_word)

    for pattern, score in LOW_SEVERITY_KEYWORDS.items():
        found = re.findall(pattern, text_lower)
        if found:
            low_scores.append(score)
            match_word = found[0][0] if isinstance(found[0], tuple) else found[0]
            low_matches.append(match_word)

    if high_scores and not low_scores:
        final_score = min(100.0, max(high_scores) + (len(high_scores) - 1) * 5.0)
        explanation = f"Text contains elevated urgency terms: {', '.join(high_matches[:3])}."
    elif low_scores and not high_scores:
        final_score = max(15.0, min(low_scores))
        explanation = f"Text indicates minor/early stage condition: {', '.join(low_matches[:3])}."
    elif high_scores and low_scores:
        # Mixed signals
        avg_score = (max(high_scores) + min(low_scores)) / 2.0
        final_score = avg_score
        explanation = f"Text contains mixed severity cues ({', '.join(high_matches[:2])} vs {', '.join(low_matches[:2])})."
    else:
        final_score = 50.0
        explanation = "Neutral problem description without explicit urgency markers."

    return {
        "text_severity_score": round(final_score, 1),
        "high_severity_cues": high_matches,
        "low_severity_cues": low_matches,
        "explanation": explanation
    }
