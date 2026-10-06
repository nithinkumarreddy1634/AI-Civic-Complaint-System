"""
Unit tests for DepartmentRecommendationService (Section 10).

Covers:
- pothole -> Roads / Public Works
- damaged_road -> Roads / Public Works
- garbage / garbage_accumulation -> Sanitation
- illegal_dumping -> Sanitation
- broken_streetlight -> Electrical
- water_leakage -> Water Supply
- fallen_tree -> Horticulture
- unknown / other -> General Administration / Manual Review
"""
import pytest
from app.ai.department.department_service import DepartmentRecommendationService


@pytest.fixture
def dept_service():
    return DepartmentRecommendationService()


def test_roads_department_recommendations(dept_service):
    """Potholes and damaged roads should route to Roads/Public Works department."""
    res_pothole = dept_service.recommend(
        category="pothole",
        description="Large pothole in road",
    )
    dept_id = res_pothole["department_id"].lower()
    dept_name = res_pothole["department_name"].lower()
    assert "road" in dept_id or "pwd" in dept_id or "road" in dept_name
    assert res_pothole["recommendation_confidence"] > 0.4

    res_road = dept_service.recommend(
        category="damaged_road",
        description="Crumbling asphalt road surface",
    )
    dept_id = res_road["department_id"].lower()
    dept_name = res_road["department_name"].lower()
    assert "road" in dept_id or "pwd" in dept_id or "road" in dept_name


def test_sanitation_department_recommendations(dept_service):
    """Garbage and illegal dumping should route to Sanitation / Solid Waste."""
    res_garbage = dept_service.recommend(
        category="garbage_accumulation",
        description="Piles of plastic waste dumped",
    )
    dept_id = res_garbage["department_id"].lower()
    dept_name = res_garbage["department_name"].lower()
    assert "sanitation" in dept_id or "waste" in dept_id or "sanitation" in dept_name or "waste" in dept_name

    res_dump = dept_service.recommend(
        category="illegal_dumping",
        description="Truck dumping construction debris",
    )
    dept_id = res_dump["department_id"].lower()
    dept_name = res_dump["department_name"].lower()
    assert "sanitation" in dept_id or "waste" in dept_id or "sanitation" in dept_name or "waste" in dept_name


def test_electrical_department_recommendations(dept_service):
    """Broken streetlight should route to Electrical."""
    res = dept_service.recommend(
        category="broken_streetlight",
        description="Streetlight lamp broken and dark",
    )
    dept_id = res["department_id"].lower()
    dept_name = res["department_name"].lower()
    assert "elec" in dept_id or "light" in dept_id or "elec" in dept_name


def test_water_supply_department_recommendations(dept_service):
    """Water leakage should route to Water Supply."""
    res = dept_service.recommend(
        category="water_leakage",
        description="Water main burst leaking all over",
    )
    dept_id = res["department_id"].lower()
    dept_name = res["department_name"].lower()
    assert "water" in dept_id or "water" in dept_name


def test_horticulture_department_recommendations(dept_service):
    """Fallen tree should route to Horticulture / Parks."""
    res = dept_service.recommend(
        category="fallen_tree",
        description="Tree branch fallen over street",
    )
    dept_id = res["department_id"].lower()
    dept_name = res["department_name"].lower()
    assert "hort" in dept_id or "tree" in dept_id or "park" in dept_id or "hort" in dept_name or "tree" in dept_name


def test_unknown_category_fallback(dept_service):
    """Unknown category should fallback gracefully to general admin / manual review."""
    res = dept_service.recommend(
        category="completely_unrecognized_custom_category",
        description="Unclear issue description",
    )
    assert res is not None
    assert "department_name" in res
    assert "department_id" in res
    assert res.get("is_manual_review") is True or res["recommendation_confidence"] <= 0.5
