"""Single image and CLI prediction runner for CivicAI YOLO models.

Performs quality validation, executes model inference, and returns structured JSON.
Optionally generates visual overlays in ml/outputs/predictions/.
"""
import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List

from ml.inference.image_quality import assess_image_quality
from ml.inference.visualize_prediction import save_annotated_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("civic_predict")


def predict_single_image(
    image_path: Path | str,
    model_path: Path | str,
    conf_threshold: float = 0.40,
    iou_threshold: float = 0.50,
    device: str = "auto",
    save_vis: bool = False,
    vis_output_dir: Path | str | None = None
) -> Dict[str, Any]:
    """Runs quality check and object detection on a single image file."""
    from ultralytics import YOLO
    from ml.training.train import detect_device

    p = Path(image_path)
    if not p.exists():
        return {
            "image_path": str(p),
            "status": "error",
            "error": "File not found.",
            "detections": []
        }

    # 1. Pre-inference image quality audit
    quality_result = assess_image_quality(p)
    if not quality_result["valid"]:
        logger.warning(f"Image {p.name} failed quality audit: {quality_result['issues']}")
        return {
            "image_path": str(p),
            "status": "rejected_quality",
            "quality": quality_result,
            "detections": [],
            "inference_time_ms": 0.0
        }

    # 2. Run model prediction
    model_p = Path(model_path)
    if not model_p.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {model_p}")

    device = detect_device(device)
    model = YOLO(str(model_p))

    t0 = time.perf_counter()
    results = model.predict(
        source=str(p),
        conf=conf_threshold,
        iou=iou_threshold,
        device=device,
        verbose=False
    )
    inference_time_ms = (time.perf_counter() - t0) * 1000.0

    detections: List[Dict[str, Any]] = []
    if len(results) > 0:
        res = results[0]
        boxes = res.boxes
        class_names = res.names

        for i in range(len(boxes)):
            cls_id = int(boxes.cls[i].item())
            cls_name = class_names.get(cls_id, f"class_{cls_id}")
            score = float(boxes.conf[i].item())
            xyxy = [round(float(v), 1) for v in boxes.xyxy[i].tolist()]

            detections.append({
                "class_id": cls_id,
                "class_name": cls_name,
                "confidence": round(score, 4),
                "bbox": xyxy  # [x1, y1, x2, y2]
            })

    output: Dict[str, Any] = {
        "image_path": str(p),
        "status": "success",
        "image_width": quality_result["metrics"]["width"],
        "image_height": quality_result["metrics"]["height"],
        "quality": quality_result,
        "detection_count": len(detections),
        "detections": detections,
        "inference_time_ms": round(inference_time_ms, 2)
    }

    # 3. Optional visual output
    if save_vis:
        if vis_output_dir is None:
            vis_output_dir = Path(__file__).parent.parent / "outputs" / "predictions"
        vis_path = Path(vis_output_dir) / f"pred_{p.name}"
        saved_file = save_annotated_image(p, detections, vis_path)
        output["visualization_path"] = str(saved_file)

    return output


def main():
    parser = argparse.ArgumentParser(description="Predict civic infrastructure complaints in images.")
    parser.add_argument("--source", type=str, required=True, help="Path to input image file")
    parser.add_argument("--model", type=str, default="ml/models/trained/civic_yolo_best.pt", help="Path to trained YOLO weights")
    parser.add_argument("--conf", type=float, default=0.40, help="Confidence threshold (0.0 - 1.0)")
    parser.add_argument("--iou", type=float, default=0.50, help="NMS IoU threshold")
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, 0")
    parser.add_argument("--save-vis", action="store_true", help="Save annotated visualization image")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save visualizations")
    args = parser.parse_args()

    res = predict_single_image(
        image_path=args.source,
        model_path=args.model,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        device=args.device,
        save_vis=args.save_vis,
        vis_output_dir=args.output_dir
    )

    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
