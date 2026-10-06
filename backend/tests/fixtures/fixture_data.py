"""
Test fixtures and controlled test data for CivicAI Phase 10 testing.

Provides realistic complaint data dictionaries, valid civic and non-civic images,
and edge-case files (corrupted, oversized, invalid extension, path traversal).
"""
import io
import os
from PIL import Image, ImageDraw


def generate_test_image(
    width: int = 400,
    height: int = 400,
    color: str = "gray",
    pattern: str = "circle",
    fmt: str = "JPEG",
) -> bytes:
    """Dynamically generate a synthetic test image with realistic patterns."""
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)

    if pattern == "circle":
        # Simulate a pothole or manhole circular defect
        draw.ellipse([width // 4, height // 4, 3 * width // 4, 3 * height // 4], fill="black", outline="darkgray")
    elif pattern == "garbage":
        # Simulate debris / waste accumulation
        for i in range(10, width - 20, 30):
            draw.rectangle([i, height // 2, i + 20, height // 2 + 30], fill="green")
            draw.rectangle([i + 5, height // 2 - 20, i + 25, height // 2], fill="brown")
    elif pattern == "pole":
        # Simulate a streetlight pole
        draw.rectangle([width // 2 - 10, 20, width // 2 + 10, height - 20], fill="silver")
        draw.ellipse([width // 2 - 25, 20, width // 2 + 25, 60], fill="yellow")
    elif pattern == "water":
        # Simulate water puddle / leakage
        draw.ellipse([50, height // 2, width - 50, height - 30], fill="blue")
    elif pattern == "food":
        # Non-civic: plate with food
        draw.ellipse([50, 50, width - 50, height - 50], fill="white", outline="gold")
        draw.ellipse([100, 100, width - 100, height - 100], fill="orange")
    elif pattern == "blank":
        pass  # Just solid color

    buf = io.BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


# Standard civic complaint fixtures
SAMPLE_POTHOLE = {
    "category": "pothole",
    "description": "Large dangerous pothole near road intersection creating traffic hazard",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "MG Road Intersection, Central Zone",
    "image_pattern": "circle",
}

SAMPLE_GARBAGE = {
    "category": "garbage_accumulation",
    "description": "Severe garbage accumulation dumped near residential apartments blocking footpath",
    "latitude": 12.9720,
    "longitude": 77.5950,
    "address": "4th Cross, Indiranagar, East Zone",
    "image_pattern": "garbage",
}

SAMPLE_STREETLIGHT = {
    "category": "broken_streetlight",
    "description": "Streetlight pole damaged and not functioning causing extreme darkness at night",
    "latitude": 12.9750,
    "longitude": 77.5980,
    "address": "Ring Road Sector 2",
    "image_pattern": "pole",
}

SAMPLE_WATER_LEAKAGE = {
    "category": "water_leakage",
    "description": "Major drinking water pipeline leakage visible on roadside flooding the pavement",
    "latitude": 12.9690,
    "longitude": 77.5910,
    "address": "Water Tank Road, South Ward",
    "image_pattern": "water",
}

# Non-civic complaint fixture
SAMPLE_NON_CIVIC = {
    "category": "other",
    "description": "Photo of a meal served at a local cafeteria restaurant",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "address": "Food Court",
    "image_pattern": "food",
}

# Corrupted and edge case file bytes
CORRUPTED_IMAGE_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * 30 + b"INVALID_GARBAGE_PAYLOAD"
EMPTY_FILE_BYTES = b""
TEXT_AS_JPG_BYTES = b"This is just plain text content renamed as a jpg image file."
OVERSIZED_IMAGE_BYTES = b"\xff\xd8\xff\xe0" + b"\x00" * (11 * 1024 * 1024)  # 11MB
