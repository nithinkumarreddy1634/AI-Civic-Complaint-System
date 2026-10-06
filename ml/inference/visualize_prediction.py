"""Visualization utility for drawing detected bounding boxes and confidence tags."""
from pathlib import Path
from typing import List, Dict, Any, Tuple
import cv2
import numpy as np

# High-contrast color palette in BGR
COLOR_PALETTE = [
    (0, 0, 255),      # 0: pothole - Red
    (0, 165, 255),    # 1: garbage - Orange
    (0, 255, 255),    # 2: open_manhole - Yellow
    (0, 255, 0),      # 3: damaged_road - Green
    (255, 255, 0),    # 4: broken_streetlight - Cyan
    (255, 0, 0),      # 5: water_leakage - Blue
    (255, 0, 255),    # 6: damaged_sidewalk - Magenta
    (128, 0, 128),    # 7: fallen_tree - Purple
    (0, 128, 255),    # 8: illegal_dumping - Light Orange
    (128, 128, 128),  # 9: normal - Gray
]


def render_detections(
    image: np.ndarray,
    detections: List[Dict[str, Any]],
    line_thickness: int = 2
) -> np.ndarray:
    """Draws bounding boxes, class names, and confidence scores onto an image array."""
    annotated = image.copy()
    h, w = annotated.shape[:2]

    for det in detections:
        cls_id = int(det.get("class_id", 0))
        cls_name = det.get("class_name", f"class_{cls_id}")
        conf = float(det.get("confidence", 0.0))
        bbox = det.get("bbox", [])

        if len(bbox) != 4:
            continue

        x1, y1, x2, y2 = [int(v) for v in bbox]
        x1 = max(0, min(w - 1, x1))
        y1 = max(0, min(h - 1, y1))
        x2 = max(0, min(w - 1, x2))
        y2 = max(0, min(h - 1, y2))

        color = COLOR_PALETTE[cls_id % len(COLOR_PALETTE)]

        # Draw main rectangle
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, line_thickness)

        # Draw label banner
        label_text = f"{cls_name} {int(conf * 100)}%"
        (tw, th), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        bg_y1 = max(0, y1 - th - 6)
        bg_y2 = y1
        bg_x2 = min(w - 1, x1 + tw + 6)

        cv2.rectangle(annotated, (x1, bg_y1), (bg_x2, bg_y2), color, -1)
        cv2.putText(
            annotated,
            label_text,
            (x1 + 3, y1 - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    return annotated


def save_annotated_image(
    image_path: Path | str,
    detections: List[Dict[str, Any]],
    output_path: Path | str
) -> Path:
    """Loads image, renders detections, and saves annotated image to output_path."""
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Could not read image for visualization: {image_path}")

    rendered = render_detections(img, detections)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out), rendered)
    return out
