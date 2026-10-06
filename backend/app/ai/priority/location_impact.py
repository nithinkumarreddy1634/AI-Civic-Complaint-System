"""Location impact evaluation service for civic complaints."""
from typing import Optional, Dict, Any, NamedTuple
from app.ai.priority.config import LocationImpactConfig, priority_config


class LocationImpactAssessment(NamedTuple):
    is_available: bool
    score: Optional[float]
    metadata: Dict[str, Any]


class LocationImpactService:
    """Evaluates location-based impact without fabricating unverified POIs.

    In production municipal environments, this service queries verified GIS spatial layers
    (e.g., proximity to schools, trauma centers, arterial transit corridors).
    When no external GIS layers are attached, it reports a neutral baseline if GPS is present,
    or flags data as unavailable so the prioritization engine can mathematically redistribute
    the location weight rather than penalizing or guessing.
    """

    def __init__(self, config: LocationImpactConfig = None):
        self.config = config or priority_config.location_impact

    def assess_location(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
        zone_type: Optional[str] = None,
        is_arterial_road: Optional[bool] = None,
        is_school_zone: Optional[bool] = None,
        is_hospital_zone: Optional[bool] = None,
    ) -> LocationImpactAssessment:
        """Assess location impact score given coordinates and optional verified municipal GIS tags."""
        if latitude is None or longitude is None:
            return LocationImpactAssessment(
                is_available=False,
                score=None,
                metadata={
                    "status": "unavailable",
                    "reason": "GPS coordinates not provided with complaint submission",
                    "has_coordinates": False,
                },
            )

        # Baseline location score when GPS is verified
        score = self.config.default_score
        applied_factors = ["valid_gps_coordinates"]

        # If verified external GIS flags are explicitly passed (extensible hook)
        if is_school_zone:
            score += 25.0
            applied_factors.append("verified_school_zone (+25)")
        if is_hospital_zone:
            score += 30.0
            applied_factors.append("verified_hospital_zone (+30)")
        if is_arterial_road:
            score += 20.0
            applied_factors.append("arterial_traffic_corridor (+20)")

        if zone_type:
            applied_factors.append(f"zone_classification:{zone_type}")

        # Clamp score to [0.0, 100.0]
        final_score = max(0.0, min(100.0, score))

        return LocationImpactAssessment(
            is_available=True,
            score=round(final_score, 2),
            metadata={
                "status": "available",
                "latitude": latitude,
                "longitude": longitude,
                "applied_factors": applied_factors,
                "has_coordinates": True,
            },
        )


location_impact_service = LocationImpactService()
