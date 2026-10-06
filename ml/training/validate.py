"""Validation script for CivicAI YOLO models.

Evaluates a trained model checkpoint against the validation split, extracting
and formatting overall and per-class metrics (Precision, Recall, mAP50, mAP50-95).
"""
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("civic_validate")


def run_validation(
    model_path: Path | str,
    data_yaml: Path | str | None = None,
    imgsz: int = 640,
    batch: int = 16,
    conf: float = 0.25,
    iou: float = 0.60,
    device: str = "auto"
) -> Dict[str, Any]:
    """Runs model validation and returns structured metrics."""
    from ultralytics import YOLO
    from ml.training.train import detect_device

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    if data_yaml is None:
        data_yaml = Path(__file__).parent.parent / "datasets" / "data.yaml"
    data_yaml = Path(data_yaml)

    device = detect_device(device)
    logger.info(f"Loading model for validation: {model_path}")
    model = YOLO(str(model_path))

    logger.info(f"Running validation on {data_yaml} at imgsz={imgsz}, conf={conf}...")
    val_results = model.val(
        data=str(data_yaml),
        imgsz=imgsz,
        batch=batch,
        conf=conf,
        iou=iou,
        device=device,
        split="val",
    )

    box = val_results.box
    precision = float(box.mp)
    recall = float(box.mr)
    map50 = float(box.map50)
    map50_95 = float(box.map)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    class_names = list(model.names.values()) if hasattr(model, "names") else []
    per_class_metrics = []

    # Extract per-class breakdown if available
    if hasattr(box, "p") and len(box.p) > 0:
        for idx in range(len(box.p)):
            cls_name = class_names[idx] if idx < len(class_names) else f"class_{idx}"
            p_cls = float(box.p[idx])
            r_cls = float(box.r[idx])
            map50_cls = float(box.all_ap[idx][0]) if hasattr(box, "all_ap") and len(box.all_ap) > idx else 0.0
            map_cls = float(box.maps[idx]) if hasattr(box, "maps") and len(box.maps) > idx else 0.0

            per_class_metrics.append({
                "class_id": idx,
                "class_name": cls_name,
                "precision": round(p_cls, 4),
                "recall": round(r_cls, 4),
                "map50": round(map50_cls, 4),
                "map50_95": round(map_cls, 4),
            })

    report = {
        "model_path": str(model_path),
        "split": "val",
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "map50": round(map50, 4),
            "map50_95": round(map50_95, 4),
            "f1_score": round(f1, 4),
        },
        "per_class": per_class_metrics,
        "speed_ms": {
            "preprocess": round(float(val_results.speed.get("preprocess", 0.0)), 2),
            "inference": round(float(val_results.speed.get("inference", 0.0)), 2),
            "loss": round(float(val_results.speed.get("loss", 0.0)), 2),
            "postprocess": round(float(val_results.speed.get("postprocess", 0.0)), 2),
        }
    }

    # Print human-readable report
    print("\n" + "=" * 65)
    print("              CivicAI Validation Evaluation Report")
    print("=" * 65)
    print(f"Model: {model_path.name}")
    print(f"Split: Validation")
    print("-" * 65)
    print(f"Overall Metrics:")
    print(f"  Precision:   {precision:.4f}")
    print(f"  Recall:      {recall:.4f}")
    print(f"  mAP@50:      {map50:.4f}")
    print(f"  mAP@50-95:   {map50_95:.4f}")
    print(f"  F1 Score:    {f1:.4f}")
    print("-" * 65)
    print(f"Inference Latency: {report['speed_ms']['inference']:.2f} ms/image")
    print("-" * 65)

    if per_class_metrics:
        print(f"{'Class':<22} | {'Precision':>10} | {'Recall':>10} | {'mAP50':>10} | {'mAP50-95':>10}")
        print("-" * 65)
        for c in per_class_metrics:
            print(f"{c['class_name']:<22} | {c['precision']:>10.4f} | {c['recall']:>10.4f} | {c['map50']:>10.4f} | {c['map50_95']:>10.4f}")
    print("=" * 65 + "\n")

    # Save to outputs/evaluation/val_metrics.json
    out_dir = Path(__file__).parent.parent / "outputs" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = out_dir / "val_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Validation metrics written to: {metrics_file}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Validate trained CivicAI YOLO model on validation split.")
    parser.add_argument("--model", type=str, default="ml/models/trained/civic_yolo_best.pt", help="Path to model weights (.pt)")
    parser.add_argument("--data", type=str, default=None, help="Path to data.yaml")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.60, help="NMS IoU threshold")
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, 0")
    args = parser.parse_args()

    run_validation(
        model_path=args.model,
        data_yaml=args.data,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        device=args.device
    )


if __name__ == "__main__":
    main()
