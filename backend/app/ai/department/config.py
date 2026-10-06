"""Department Configuration loader and category mapping definitions."""
import os
import yaml
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DepartmentMeta:
    code: str
    name: str
    description: str
    contact_email: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    priority_order: int = 1


@dataclass
class FallbackDepartment:
    code: str = "manual_review"
    name: str = "Manual Review / Triage Team"
    description: str = "Queue for unclassified or ambiguous civic complaints"
    contact_email: Optional[str] = None


@dataclass
class DepartmentConfig:
    version: str = "v1.0.0"
    departments: Dict[str, DepartmentMeta] = field(default_factory=dict)
    fallback: FallbackDepartment = field(default_factory=FallbackDepartment)

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> "DepartmentConfig":
        """Load department configuration from YAML file or return defaults."""
        if config_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            config_path = os.path.join(base_dir, "config", "departments.yaml")

        if not os.path.exists(config_path):
            return cls._default_fallback()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            depts_data = data.get("departments", {})
            fb_data = data.get("fallback", {})

            parsed_depts: Dict[str, DepartmentMeta] = {}
            for code, d in depts_data.items():
                parsed_depts[code] = DepartmentMeta(
                    code=code,
                    name=d.get("name", code.replace("_", " ").title()),
                    description=d.get("description", ""),
                    contact_email=d.get("contact_email"),
                    categories=d.get("categories", []),
                    priority_order=int(d.get("priority_order", 1)),
                )

            fallback = FallbackDepartment(
                code=fb_data.get("code", "manual_review"),
                name=fb_data.get("name", "Manual Review / Triage Team"),
                description=fb_data.get("description", "Queue for unclassified or ambiguous civic complaints"),
                contact_email=fb_data.get("contact_email"),
            )

            return cls(
                version=data.get("version", "v1.0.0"),
                departments=parsed_depts,
                fallback=fallback,
            )
        except Exception:
            return cls._default_fallback()

    @classmethod
    def _default_fallback(cls) -> "DepartmentConfig":
        return cls(
            departments={
                "roads": DepartmentMeta(
                    code="roads",
                    name="Roads / Public Works Department",
                    description="Roads, sidewalks, potholes, manholes",
                    categories=["pothole", "damaged_road", "damaged_sidewalk", "open_manhole"],
                ),
                "sanitation": DepartmentMeta(
                    code="sanitation",
                    name="Sanitation Department",
                    description="Garbage and illegal dumping",
                    categories=["garbage", "garbage_accumulation", "illegal_dumping"],
                ),
                "electrical": DepartmentMeta(
                    code="electrical",
                    name="Electrical / Street Lighting Department",
                    description="Street lighting and electrical hazards",
                    categories=["broken_streetlight"],
                ),
                "water": DepartmentMeta(
                    code="water",
                    name="Water Supply & Sewerage Department",
                    description="Water leakages and pipe bursts",
                    categories=["water_leakage"],
                ),
                "horticulture": DepartmentMeta(
                    code="horticulture",
                    name="Horticulture / Municipal Parks Department",
                    description="Fallen trees and greenery",
                    categories=["fallen_tree"],
                ),
            },
            fallback=FallbackDepartment(),
        )


department_config = DepartmentConfig.load()
