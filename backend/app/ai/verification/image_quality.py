"""Image quality verification module for civic complaint submissions.

Maps pre-inference assessment metrics into standardized quality states:
GOOD, ACCEPTABLE, POOR, and INVALID.
"""
from pathlib import Path
from typing import Dict, Any, Union
import cv2
import numpy as np
from PIL import Image


def map_score_to_state(score: int, is_fatal: bool = False) -> str:
    """Maps numerical quality score to categorical health grade."""
    if is_fatal or score < 35:
        return "INVALID"
    elif score < 50:
        return "POOR"
    elif score < 80:
        return "ACCEPTABLE"
    return "GOOD"


def verify_image_quality(
    image_input: Union[Path, str, bytes, np.ndarray],
    min_dimension: int = 100,
    blur_threshold: float = 30.0,
    darkness_threshold: float = 35.0,
    brightness_threshold: float = 230.0
) -> Dict[str, Any]:
    """Inspects image data and returns structured quality state and diagnosis."""
    issues = []
    quality_score = 100
    is_fatal = False

    img_bgr = None

    # 1. Load image and perform format/integrity check
    if isinstance(image_input, (str, Path)):
        p = Path(image_input)
        if not p.exists():
            return {
                "valid": False,
                "status": "INVALID",
                "quality_score": 0,
                "issues": [f"Image file not found: {p}"],
                "metrics": {}
            }
        try:
            with Image.open(p) as pil_img:
                pil_img.verify()
        except Exception as e:
            return {
                "valid": False,
                "status": "INVALID",
                "quality_score": 0,
                "issues": [f"Corrupted or invalid image file: {e}"],
                "metrics": {}
            }
        img_bgr = cv2.imread(str(p))

    elif isinstance(image_input, (bytes, bytearray)):
        if len(image_input) == 0:
            return {
                "valid": False,
                "status": "INVALID",
                "quality_score": 0,
                "issues": ["Empty byte buffer received."],
                "metrics": {}
            }
        nparr = np.frombuffer(image_input, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    elif isinstance(image_input, np.ndarray):
        img_bgr = image_input

    if img_bgr is None or img_bgr.size == 0:
        return {
            "valid": False,
            "status": "INVALID",
            "quality_score": 0,
            "issues": ["Image could not be decoded."],
            "metrics": {}
        }

    h, w = img_bgr.shape[:2]

    # 2. Dimensions check
    if w < min_dimension or h < min_dimension:
        issues.append(f"Image resolution too small: {w}x{h} px (minimum required: {min_dimension}x{min_dimension}).")
        quality_score -= 45
        if w < 50 or h < 50:
            is_fatal = True

    # 3. Grayscale conversion for focus & lighting checks
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    mean_intensity = float(np.mean(gray))
    if mean_intensity < darkness_threshold:
        issues.append(f"Image is underexposed/too dark (brightness: {mean_intensity:.1f}/255).")
        quality_score -= 30
    elif mean_intensity > brightness_threshold:
        issues.append(f"Image is overexposed/washed out (brightness: {mean_intensity:.1f}/255).")
        quality_score -= 25

    # 4. Blur check (Laplacian variance)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < blur_threshold:
        issues.append(f"Image has noticeable blur (sharpness: {laplacian_var:.1f}).")
        quality_score -= 30

    # 5. Low contrast check (standard deviation)
    std_intensity = float(np.std(gray))
    if std_intensity < 15.0:
        issues.append(f"Image has very low contrast (dynamic range: {std_intensity:.1f}).")
        quality_score -= 20

    quality_score = max(0, min(100, quality_score))
    status = map_score_to_state(quality_score, is_fatal=is_fatal)
    is_valid = (status != "INVALID")

    return {
        "valid": is_valid,
        "status": status,
        "quality_score": quality_score,
        "issues": issues,
        "metrics": {
            "width": w,
            "height": h,
            "brightness": round(mean_intensity, 2),
            "sharpness": round(laplacian_var, 2),
            "contrast": round(std_intensity, 2)
        }
    }
