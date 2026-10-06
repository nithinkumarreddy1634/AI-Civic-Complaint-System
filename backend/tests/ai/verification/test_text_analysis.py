"""Tests for NLP description analysis and category extraction."""
from app.ai.verification.text_analysis import analyze_description


def test_pothole_description_extraction():
    text = "There is a huge pothole near the bus stop on main street."
    res = analyze_description(text)
    assert res["has_description"] is True
    categories = [c["category"] for c in res["text_categories"]]
    assert "pothole" in categories
    assert len(res["urgency_markers"]) > 0  # "huge" is detected


def test_multiple_categories_extraction():
    text = "Garbage has been dumped along the road and caused a severe hazard."
    res = analyze_description(text)
    assert res["has_description"] is True
    categories = [c["category"] for c in res["text_categories"]]
    assert "garbage" in categories or "illegal_dumping" in categories
    assert "severe" in res["urgency_markers"] or "hazard" in res["urgency_markers"]


def test_water_leakage_keywords():
    text = "Burst pipe with gushing water near the sidewalk."
    res = analyze_description(text)
    categories = [c["category"] for c in res["text_categories"]]
    assert "water_leakage" in categories


def test_empty_or_none_description():
    res1 = analyze_description("")
    assert res1["has_description"] is False
    assert len(res1["text_categories"]) == 0

    res2 = analyze_description(None)
    assert res2["has_description"] is False
