"""Image quality audit gate executed prior to model inference.

Evaluates readability, image resolution, darkness/underexposure, and motion/focus blur.
Returns an explainable quality score (0-100) and actionable diagnosis list.
"""
from pathlib import Path
from typing import Dict, Any, List
import cv2
import numpy as np
from PIL import Image


def assess_image_quality(
    image_path: Path | str | np.ndarray,
    min_dimension: int = 100,
    blur_threshold: float = 30.0,
    darkness_threshold: float = 35.0,
    brightness_threshold: float = 230.0
) -> Dict[str, Any]:
    """Inspects an input image and computes a quality score and issue list.

    Args:
        image_path: Path to image file or numpy BGR array.
        min_dimension: Minimum allowed width or height in pixels.
        blur_threshold: Laplacian variance cutoff below which image is blurry.
        darkness_threshold: Mean grayscale pixel intensity below which image is too dark.
        brightness_threshold: Mean grayscale pixel intensity above which image is washed out.

    Returns:
        Dict with keys: valid (bool), quality_score (int 0-100), issues (list[str]), metrics (dict)
    """
    issues: List[str] = []
    quality_score = 100

    # 1. Existence and loading
    if isinstance(image_path, (str, Path)):
        p = Path(image_path)
        if not p.exists():
            return {
                "valid": False,
                "quality_score": 0,
                "issues": [f"File not found: {p}"],
                "metrics": {}
            }

        ext = p.suffix.lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            return {
                "valid": False,
                "quality_score": 0,
                "issues": [f"Unsupported format '{ext}'. Allowed: .jpg, .jpeg, .png, .webp"],
                "metrics": {}
            }

        # PIL integrity check
        try:
            with Image.open(p) as img:
                img.verify()
        except Exception as e:
            return {
                "valid": False,
                "quality_score": 0,
                "issues": [f"Corrupt image file: {e}"],
                "metrics": {}
            }

        img_bgr = cv2.imread(str(p))
    else:
        img_bgr = image_path

    if img_bgr is None or img_bgr.size == 0:
        return {
            "valid": False,
            "quality_score": 0,
            "issues": ["Unreadable image data (cv2 decoded None)."],
            "metrics": {}
        }

    h, w = img_bgr.shape[:2]

    # 2. Dimension constraints
    if w < min_dimension or h < min_dimension:
        issues.append(f"Resolution too small: {w}x{h} px (minimum is {min_dimension}x{min_dimension}).")
        quality_score -= 40

    # Convert to grayscale for illumination and focus analysis
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 3. Illumination / Darkness test
    mean_intensity = float(np.mean(gray))
    if mean_intensity < darkness_threshold:
        issues.append(f"Image is underexposed/too dark (mean brightness: {mean_intensity:.1f}/255).")
        quality_score -= 30
    elif mean_intensity > brightness_threshold:
        issues.append(f"Image is overexposed/washed out (mean brightness: {mean_intensity:.1f}/255).")
        quality_score -= 25

    # 4. Blur / Sharpness test (Laplacian variance)
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    if laplacian_var < blur_threshold:
        issues.append(f"Image is significantly blurred (Laplacian variance: {laplacian_var:.1f}).")
        quality_score -= 35

    quality_score = max(0, min(100, quality_score))
    # Consider valid if quality score >= 40 and resolution is not fatally small
    is_valid = (quality_score >= 40) and (w >= min_dimension and h >= min_dimension)

    return {
        "valid": is_valid,
        "quality_score": quality_score,
        "issues": issues,
        "metrics": {
            "width": w,
            "height": h,
            "mean_intensity": round(mean_intensity, 2),
            "laplacian_variance": round(laplacian_var, 2)
        }
    }
