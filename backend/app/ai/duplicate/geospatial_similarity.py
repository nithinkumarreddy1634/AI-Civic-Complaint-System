"""Geospatial distance and location similarity calculations using the Haversine formula."""
import math
from typing import Dict, Any, Optional, Tuple
from .config import duplicate_config

# Earth's mean radius in meters
EARTH_RADIUS_METERS = 6371000.0


def calculate_haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Calculate the great-circle distance between two geographic points on Earth in meters.

    Formula:
        a = sin^2(dlat/2) + cos(lat1)*cos(lat2)*sin^2(dlon/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        d = R * c
    """
    # Convert degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    # Clamp for numerical stability
    a = min(1.0, max(0.0, a))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = EARTH_RADIUS_METERS * c

    return round(distance, 2)


def calculate_location_similarity(
    lat1: Optional[float],
    lon1: Optional[float],
    lat2: Optional[float],
    lon2: Optional[float],
) -> Dict[str, Any]:
    """
    Calculate geographic distance and normalized location similarity score (0.0 to 1.0).

    Mapping curve:
        - distance <= high_similarity_radius (50m):
            similarity drops gently from 1.00 down to 0.90
        - high_similarity_radius < distance <= candidate_radius (500m):
            similarity decays smoothly from 0.90 down to 0.00
        - distance > candidate_radius:
            similarity = 0.00

    Args:
        lat1, lon1: Coordinates of complaint A.
        lat2, lon2: Coordinates of complaint B.

    Returns:
        Dict with:
            - has_location: bool
            - distance_meters: Optional[float]
            - location_similarity: Optional[float] (0.0 to 1.0)
            - is_close_proximity: bool (< 50m)
            - notes: str
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return {
            "has_location": False,
            "distance_meters": None,
            "location_similarity": None,
            "is_close_proximity": False,
            "notes": "One or both complaints lack GPS coordinates.",
        }

    # Validate coordinate boundaries
    if not (-90.0 <= lat1 <= 90.0 and -180.0 <= lon1 <= 180.0 and
            -90.0 <= lat2 <= 90.0 and -180.0 <= lon2 <= 180.0):
        return {
            "has_location": False,
            "distance_meters": None,
            "location_similarity": None,
            "is_close_proximity": False,
            "notes": "Coordinates are outside valid latitude/longitude ranges.",
        }

    dist = calculate_haversine_distance(lat1, lon1, lat2, lon2)
    geo_cfg = duplicate_config.geographic
    high_rad = geo_cfg.high_similarity_radius_meters
    cand_rad = geo_cfg.candidate_radius_meters

    if dist <= high_rad:
        # 0m -> 1.0, 50m -> 0.90
        sim = 1.0 - 0.10 * (dist / high_rad if high_rad > 0 else 0)
    elif dist <= cand_rad:
        # 50m -> 0.90, 500m -> 0.00
        span = cand_rad - high_rad
        ratio = (dist - high_rad) / span if span > 0 else 1.0
        # Cosine half-wave decay for smooth gradient
        sim = 0.90 * (0.5 * (1.0 + math.cos(math.pi * ratio)))
    else:
        sim = 0.0

    sim = round(max(0.0, min(1.0, sim)), 4)
    is_close = dist <= high_rad

    return {
        "has_location": True,
        "distance_meters": dist,
        "location_similarity": sim,
        "is_close_proximity": is_close,
        "notes": f"Geographic separation: {dist:.1f} meters.",
    }


def get_bounding_box_for_radius(
    lat: float,
    lon: float,
    radius_meters: float,
) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box [min_lat, min_lon, max_lat, max_lon] for candidate database query.
    1 degree latitude ~ 111,320 meters.
    1 degree longitude ~ 111,320 * cos(lat) meters.
    """
    delta_lat = radius_meters / 111320.0
    lat_rad = math.radians(lat)
    cos_lat = math.cos(lat_rad)
    delta_lon = radius_meters / (111320.0 * cos_lat) if abs(cos_lat) > 1e-6 else radius_meters / 111320.0

    return (
        max(-90.0, lat - delta_lat),
        max(-180.0, lon - delta_lon),
        min(90.0, lat + delta_lat),
        min(180.0, lon + delta_lon),
    )
