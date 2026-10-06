"""Lightweight NLP description analysis and category extraction module.

Parses citizen complaint descriptions, extracts civic keywords, matches defect taxonomy
synonyms, and computes confidence scores for mentioned categories without external LLM calls.
"""
import re
from typing import List, Dict, Any, Set

# Comprehensive synonym and phrase dictionary mapping to target civic classes
CIVIC_KEYWORD_PATTERNS: Dict[str, List[str]] = {
    "pothole": [
        r"\bpotholes?\b",
        r"\bhole(s)? in (the )?road\b",
        r"\broad crater\b",
        r"\bpit(s)?\b",
        r"\basphalt hole\b",
    ],
    "garbage": [
        r"\bgarbage\b",
        r"\btrash\b",
        r"\blitter\b",
        r"\bwaste\b",
        r"\brubbish\b",
        r"\brefuse\b",
        r"\bdebris\b",
        r"\bdumpster overflow\b",
    ],
    "open_manhole": [
        r"\bopen manhole\b",
        r"\bmissing manhole\b",
        r"\bmanhole cover\b",
        r"\bdrain cover\b",
        r"\buncovered drain\b",
        r"\bopen sewer\b",
        r"\bchamber cover\b",
    ],
    "damaged_road": [
        r"\bdamaged road\b",
        r"\broad crack(s)?\b",
        r"\bbroken road\b",
        r"\basphalt crack(s)?\b",
        r"\bunpaved\b",
        r"\bruts?\b",
        r"\bsurface uneven\b",
        r"\beroded road\b",
    ],
    "broken_streetlight": [
        r"\bbroken streetlight\b",
        r"\bstreet ?light\b",
        r"\blamp ?post\b",
        r"\blight pole\b",
        r"\bdark street\b",
        r"\bno street ?light\b",
        r"\bbulb not working\b",
        r"\bflickering light\b",
    ],
    "water_leakage": [
        r"\bwater leak(age)?\b",
        r"\bburst pipe\b",
        r"\bpipeline leak\b",
        r"\bgushing water\b",
        r"\bwaterlogging\b",
        r"\bflooding\b",
        r"\bbroken pipe\b",
        r"\bstanding water\b",
    ],
    "damaged_sidewalk": [
        r"\bdamaged sidewalk\b",
        r"\bbroken sidewalk\b",
        r"\bfootpath\b",
        r"\bpavement\b",
        r"\bbroken curb\b",
        r"\bwalking path\b",
        r"\bpedestrian path\b",
        r"\bcracked walkway\b",
    ],
    "fallen_tree": [
        r"\bfallen tree\b",
        r"\buprooted tree\b",
        r"\btree branch(es)?\b",
        r"\bdowned tree\b",
        r"\btree fell\b",
        r"\bblocked by tree\b",
    ],
    "illegal_dumping": [
        r"\billegal dump(ing)?\b",
        r"\bdumped\b",
        r"\bconstruction debris\b",
        r"\bconcrete waste\b",
        r"\bcommercial waste\b",
        r"\bhazardous waste\b",
    ],
}

URGENCY_KEYWORDS = [
    r"\bdanger(ous)?\b",
    r"\bhazard(ous)?\b",
    r"\bemergency\b",
    r"\baccident\b",
    r"\bcritical\b",
    r"\bsevere\b",
    r"\bhuge\b",
    r"\brisk\b",
]


def analyze_description(text: str | None) -> Dict[str, Any]:
    """Extracts candidate complaint categories and urgency markers from textual description."""
    if not text or not text.strip():
        return {
            "has_description": False,
            "text_categories": [],
            "keywords_found": [],
            "urgency_markers": [],
            "word_count": 0,
            "clean_text": ""
        }

    clean_text = text.lower().strip()
    words = re.findall(r"\b\w+\b", clean_text)
    word_count = len(words)

    matched_categories: List[Dict[str, Any]] = []
    keywords_found: Set[str] = set()

    for category, patterns in CIVIC_KEYWORD_PATTERNS.items():
        match_count = 0
        strongest_pattern = None

        for pattern in patterns:
            matches = re.findall(pattern, clean_text)
            if matches:
                match_count += len(matches)
                keywords_found.add(pattern.replace(r"\b", "").replace(r"(s)?", "").replace(r"\?", ""))
                if strongest_pattern is None:
                    strongest_pattern = pattern

        if match_count > 0:
            # Confidence formula: Base 0.75 + incremental bonus for multiple matches up to 0.98
            conf = min(0.98, 0.75 + (match_count * 0.08))
            matched_categories.append({
                "category": category,
                "confidence": round(conf, 4),
                "match_count": match_count
            })

    # Sort descending by confidence
    matched_categories.sort(key=lambda x: x["confidence"], reverse=True)

    # Detect urgency markers
    urgency_markers = []
    for pattern in URGENCY_KEYWORDS:
        if re.search(pattern, clean_text):
            urgency_markers.append(pattern.replace(r"\b", "").replace(r"(ous)?", ""))

    return {
        "has_description": True,
        "text_categories": matched_categories,
        "keywords_found": sorted(list(keywords_found)),
        "urgency_markers": sorted(list(set(urgency_markers))),
        "word_count": word_count,
        "clean_text": clean_text
    }
