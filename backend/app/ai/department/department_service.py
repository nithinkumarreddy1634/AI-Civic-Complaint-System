"""Department Recommendation Service for civic complaint triage."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.ai.department.config import DepartmentConfig, department_config


class DepartmentRecommendationService:
    """Recommends responsible municipal departments from verified AI evidence.

    Supports:
    - Single-category direct and affinity mapping
    - Multi-issue detection aggregation (e.g. Pothole + Garbage)
    - Fallback to MANUAL_REVIEW for unknown or ambiguous issues
    - Calibrated recommendation_confidence calculation
    """

    def __init__(self, config: DepartmentConfig = None):
        self.config = config or department_config

    def recommend(
        self,
        category: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        detections: Optional[List[Dict[str, Any]]] = None,
        detection_confidence: float = 0.85,
        verification_status: str = "VERIFIED",
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Compute explainable department recommendation."""
        # 1. Identify all candidate categories
        categories_to_evaluate: List[str] = []

        if category:
            cat_norm = category.strip().lower()
            if cat_norm not in ("other", "unknown", "unrecognized", "none", ""):
                categories_to_evaluate.append(cat_norm)

        if detections:
            for det in detections:
                det_cls = det.get("class_name") or det.get("label") or det.get("category")
                if det_cls:
                    det_norm = str(det_cls).strip().lower()
                    if det_norm not in ("other", "unknown", "unrecognized", "normal") and det_norm not in categories_to_evaluate:
                        categories_to_evaluate.append(det_norm)

        # 2. Check for Unknown / Unrecognized Fallback
        if not categories_to_evaluate:
            fb = self.config.fallback
            return {
                "department_id": fb.code,
                "department_name": fb.name,
                "recommendation_confidence": 0.50,
                "is_manual_review": True,
                "reason": (
                    "The issue category is unclassified, ambiguous, or marked as 'other'. "
                    "Routed to the Manual Review / Triage Team for administrative inspection."
                ),
                "departments": [
                    {
                        "department_id": fb.code,
                        "department_name": fb.name,
                        "category": category or "unclassified",
                        "confidence": 0.50,
                        "is_primary": True,
                    }
                ],
            }

        # 3. Map categories to departments
        matched_departments: List[Dict[str, Any]] = []
        seen_depts = set()

        for cat in categories_to_evaluate:
            dept_meta = self._find_department_for_category(cat, db=db)
            if dept_meta and dept_meta["code"] not in seen_depts:
                seen_depts.add(dept_meta["code"])
                # Compute category-specific recommendation confidence
                cat_conf = self._compute_confidence(
                    detection_confidence=detection_confidence,
                    verification_status=verification_status,
                    has_description=bool(description and len(description.strip()) > 5),
                    has_location=bool(location and location.get("latitude")),
                    priority_order=dept_meta.get("priority_order", 1),
                )
                matched_departments.append({
                    "department_id": dept_meta["code"],
                    "department_name": dept_meta["name"],
                    "category": cat,
                    "confidence": cat_conf,
                    "priority_order": dept_meta.get("priority_order", 1),
                })

        # If none of the categories matched known departments
        if not matched_departments:
            fb = self.config.fallback
            return {
                "department_id": fb.code,
                "department_name": fb.name,
                "recommendation_confidence": 0.40,
                "is_manual_review": True,
                "reason": (
                    f"Category '{category}' does not map to any recognized municipal department. "
                    "Assigned to Manual Review / Triage Team to avoid incorrect dispatch."
                ),
                "departments": [
                    {
                        "department_id": fb.code,
                        "department_name": fb.name,
                        "category": category or "unknown",
                        "confidence": 0.40,
                        "is_primary": True,
                    }
                ],
            }

        # Sort departments by priority_order ascending (1 is highest), then confidence descending
        matched_departments.sort(key=lambda x: (x["priority_order"], -x["confidence"]))

        primary = matched_departments[0]
        primary["is_primary"] = True
        for d in matched_departments[1:]:
            d["is_primary"] = False

        # Build transparent explanation
        if len(matched_departments) > 1:
            dept_names = ", ".join(f"{d['department_name']} ({d['category']})" for d in matched_departments)
            reason = (
                f"Multi-issue complaint detected involving multiple functional jurisdictions: {dept_names}. "
                f"Primary recommendation is {primary['department_name']} based on priority order and detection evidence."
            )
        else:
            reason = (
                f"The detected issue is classified as '{primary['category']}', "
                f"which falls under the jurisdiction of the {primary['department_name']}."
            )

        return {
            "department_id": primary["department_id"],
            "department_name": primary["department_name"],
            "recommendation_confidence": primary["confidence"],
            "is_manual_review": False,
            "reason": reason,
            "departments": matched_departments,
        }

    def _find_department_for_category(
        self,
        category: str,
        db: Optional[Session] = None,
    ) -> Optional[Dict[str, Any]]:
        """Find department matching category from database or YAML config."""
        # 1. Try DB lookup first if session provided
        if db is not None:
            try:
                from app.models.department import Department, DepartmentCategoryMapping
                mapping = (
                    db.query(DepartmentCategoryMapping)
                    .join(Department, Department.id == DepartmentCategoryMapping.department_id)
                    .filter(DepartmentCategoryMapping.category == category)
                    .filter(Department.is_active == True)
                    .order_by(DepartmentCategoryMapping.priority_order.asc())
                    .first()
                )
                if mapping and mapping.department:
                    dept = mapping.department
                    code = getattr(dept, "code", None) or dept.name.lower().split()[0]
                    return {
                        "code": code,
                        "name": dept.name,
                        "description": dept.description,
                        "priority_order": mapping.priority_order,
                    }
            except Exception:
                pass

        # 2. YAML config lookup
        for code, dept in self.config.departments.items():
            if category in dept.categories:
                return {
                    "code": dept.code,
                    "name": dept.name,
                    "description": dept.description,
                    "priority_order": dept.priority_order,
                }

        # Normalize common synonyms (e.g. garbage -> garbage_accumulation)
        synonyms = {
            "garbage": "garbage_accumulation",
            "potholes": "pothole",
            "manhole": "open_manhole",
            "road_damage": "damaged_road",
            "leakage": "water_leakage",
            "tree": "fallen_tree",
            "dumping": "illegal_dumping",
            "sidewalk": "damaged_sidewalk",
            "streetlight": "broken_streetlight",
        }
        mapped_synonym = synonyms.get(category)
        if mapped_synonym and mapped_synonym != category:
            return self._find_department_for_category(mapped_synonym, db=db)

        return None

    def _compute_confidence(
        self,
        detection_confidence: float,
        verification_status: str,
        has_description: bool,
        has_location: bool,
        priority_order: int,
    ) -> float:
        """Calibrate recommendation confidence score between 0.0 and 1.0."""
        # Base confidence anchored to vision detection confidence
        conf = max(0.50, min(0.95, float(detection_confidence)))

        # Verification boost or penalty
        if verification_status == "VERIFIED":
            conf += 0.05
        elif verification_status == "NEEDS_REVIEW":
            conf -= 0.10

        # Description and location confirmation boosts
        if has_description:
            conf += 0.03
        if has_location:
            conf += 0.02

        # Priority alignment
        if priority_order == 1:
            conf += 0.02

        # Clamp between 0.0 and 0.99 (never claim 100% certainty)
        return round(max(0.10, min(0.99, conf)), 2)


department_recommendation_service = DepartmentRecommendationService()
