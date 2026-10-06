"""Candidate complaint retrieval engine for scalable duplicate search."""
import uuid
from typing import List, Optional, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.complaint import Complaint, ComplaintStatus
from .config import duplicate_config
from .geospatial_similarity import get_bounding_box_for_radius

# Statuses eligible for duplicate matching
ACTIVE_DUPLICATE_STATUSES = {
    ComplaintStatus.SUBMITTED,
    ComplaintStatus.VERIFIED,
    ComplaintStatus.NEEDS_REVIEW,
    ComplaintStatus.ASSIGNED,
    ComplaintStatus.IN_PROGRESS,
    ComplaintStatus.RESOLVED,  # Included because resolved infrastructure problems may recur
}

# Category affinity mapping for cross-category candidate consideration
CATEGORY_AFFINITIES = {
    "pothole": {"pothole", "damaged_road", "damaged_sidewalk"},
    "damaged_road": {"damaged_road", "pothole", "damaged_sidewalk"},
    "garbage": {"garbage", "garbage_accumulation", "illegal_dumping"},
    "garbage_accumulation": {"garbage", "garbage_accumulation", "illegal_dumping"},
    "illegal_dumping": {"illegal_dumping", "garbage", "garbage_accumulation"},
    "open_manhole": {"open_manhole", "damaged_road", "damaged_sidewalk"},
    "damaged_sidewalk": {"damaged_sidewalk", "damaged_road", "pothole"},
    "broken_streetlight": {"broken_streetlight"},
    "water_leakage": {"water_leakage", "damaged_road"},
    "fallen_tree": {"fallen_tree", "damaged_road", "damaged_sidewalk"},
}


def get_compatible_categories(category: Optional[str]) -> Set[str]:
    """Return set of categories that could semantically match the input category."""
    if not category:
        return set()
    norm = category.lower().strip()
    return CATEGORY_AFFINITIES.get(norm, {norm})


def find_duplicate_candidates(
    db: Session,
    current_complaint_id: Optional[uuid.UUID],
    category: Optional[str],
    latitude: Optional[float],
    longitude: Optional[float],
    max_candidates: Optional[int] = None,
) -> List[Complaint]:
    """
    Retrieve candidate complaints using spatial bounding-box and category filtering.

    Avoids full database table scans by filtering first on indexed latitude/longitude
    bounds and compatible category tags.

    Args:
        db: SQLAlchemy database session.
        current_complaint_id: ID of the complaint being evaluated (to exclude self).
        category: AI-verified or user-selected category.
        latitude: GPS latitude.
        longitude: GPS longitude.
        max_candidates: Maximum candidates to retrieve.

    Returns:
        List of Candidate Complaint objects.
    """
    limit = max_candidates or duplicate_config.max_candidates_to_compare
    compatible_cats = get_compatible_categories(category)

    query = db.query(Complaint).filter(
        Complaint.status.in_(ACTIVE_DUPLICATE_STATUSES)
    )

    if current_complaint_id:
        query = query.filter(Complaint.id != current_complaint_id)

    # Branch 1: GPS coordinates are available -> Spatial bounding box query
    if latitude is not None and longitude is not None:
        radius_m = duplicate_config.geographic.candidate_radius_meters
        min_lat, min_lon, max_lat, max_lon = get_bounding_box_for_radius(latitude, longitude, radius_m)

        query = query.filter(
            and_(
                Complaint.latitude.isnot(None),
                Complaint.longitude.isnot(None),
                Complaint.latitude >= min_lat,
                Complaint.latitude <= max_lat,
                Complaint.longitude >= min_lon,
                Complaint.longitude <= max_lon,
            )
        )
        if compatible_cats:
            query = query.filter(Complaint.category.in_(compatible_cats))

        candidates = query.order_by(Complaint.created_at.desc()).limit(limit).all()
        return candidates

    # Branch 2: GPS coordinates are missing -> Fall back to category-based candidate search
    if compatible_cats:
        query = query.filter(Complaint.category.in_(compatible_cats))

    candidates = query.order_by(Complaint.created_at.desc()).limit(limit).all()
    return candidates
