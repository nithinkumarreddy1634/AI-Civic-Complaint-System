"""Location context service for spatial and environmental factor analysis."""
from typing import Dict, Any, Optional


class LocationContextService:
    """
    Extensible service for analyzing geographic and environmental context.

    In Phase 5, provides validated coordinate metadata without making unverified
    assumptions regarding nearby schools, hospitals, or traffic density.
    Subsequent phases can integrate GIS layers and spatial queries.
    """

    def analyze(
        self,
        latitude: Optional[float],
        longitude: Optional[float],
    ) -> Dict[str, Any]:
        """
        Analyze location context if coordinates are available.

        Args:
            latitude: GPS latitude in decimal degrees.
            longitude: GPS longitude in decimal degrees.

        Returns:
            Dict with location metadata, validity flag, and context factors.
        """
        if latitude is None or longitude is None:
            return {
                "has_location": False,
                "latitude": None,
                "longitude": None,
                "is_valid_coordinates": False,
                "location_factor_multiplier": 1.0,
                "notes": "No geographic coordinates supplied."
            }

        # Validate coordinate bounds
        is_valid = (-90.0 <= latitude <= 90.0) and (-180.0 <= longitude <= 180.0)
        if not is_valid:
            return {
                "has_location": True,
                "latitude": latitude,
                "longitude": longitude,
                "is_valid_coordinates": False,
                "location_factor_multiplier": 1.0,
                "notes": "Supplied coordinates are out of valid geographic range."
            }

        return {
            "has_location": True,
            "latitude": round(latitude, 6),
            "longitude": round(longitude, 6),
            "is_valid_coordinates": True,
            "location_factor_multiplier": 1.0,
            "notes": "Coordinates recorded for spatial indexing; no unverified POI assumed."
        }
