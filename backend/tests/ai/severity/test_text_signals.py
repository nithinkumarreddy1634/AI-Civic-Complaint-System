"""Unit tests for textual severity signal extraction."""
import pytest
from app.ai.severity.text_signals import extract_text_severity_signal


def test_high_severity_description():
    desc = "Huge dangerous pothole completely blocking the road! Urgent emergency."
    res = extract_text_severity_signal(desc)
    assert res["text_severity_score"] >= 75.0
    assert len(res["high_severity_cues"]) >= 2
    assert len(res["low_severity_cues"]) == 0


def test_low_severity_description():
    desc = "Small minor hairline crack starting to form on the sidewalk."
    res = extract_text_severity_signal(desc)
    assert res["text_severity_score"] <= 40.0
    assert len(res["low_severity_cues"]) >= 1


def test_mixed_severity_description():
    desc = "Small pothole but dangerous for high speed bikes."
    res = extract_text_severity_signal(desc)
    assert 40.0 <= res["text_severity_score"] <= 75.0


def test_empty_description_neutral():
    res = extract_text_severity_signal("")
    assert res["text_severity_score"] == 50.0
    res_none = extract_text_severity_signal(None)
    assert res_none["text_severity_score"] == 50.0
