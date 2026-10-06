"""Test set evaluation script for CivicAI YOLO models.

Evaluates the final selected model on the unseen TEST split.
Measures generalization performance, latency (ms), throughput (FPS), and model size.
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
logger = logging.getLogger("civic_evaluate")


def run_test_evaluation(
    model_path: Path | str,
    data_yaml: Path | str | None = None,
    imgsz: int = 640,
    conf: float = 0.25,
    iou: float = 0.60,
    device: str = "auto"
) -> Dict[str, Any]:
    """Evaluates model strictly on unseen test data."""
    from ultralytics import YOLO
    from ml.training.train import detect_device

    model_path = Path(model_path)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    if data_yaml is None:
        data_yaml = Path(__file__).parent.parent / "datasets" / "data.yaml"
    data_yaml = Path(data_yaml)

    device = detect_device(device)
    model_size_mb = model_path.stat().st_size / (1024 * 1024)

    logger.info(f"Loading final model for test evaluation: {model_path} ({model_size_mb:.2f} MB)")
    model = YOLO(str(model_path))

    logger.info(f"Evaluating strictly on TEST split ({data_yaml}) with conf={conf}...")
    test_results = model.val(
        data=str(data_yaml),
        imgsz=imgsz,
        conf=conf,
        iou=iou,
        device=device,
        split="test",
    )

    box = test_results.box
    precision = float(box.mp)
    recall = float(box.mr)
    map50 = float(box.map50)
    map50_95 = float(box.map)
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0

    inference_ms = float(test_results.speed.get("inference", 0.0))
    preprocess_ms = float(test_results.speed.get("preprocess", 0.0))
    postprocess_ms = float(test_results.speed.get("postprocess", 0.0))
    total_ms = inference_ms + preprocess_ms + postprocess_ms
    fps = (1000.0 / total_ms) if total_ms > 0 else 0.0

    class_names = list(model.names.values()) if hasattr(model, "names") else []
    per_class_metrics = []

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
        "split": "TEST (Unseen)",
        "model_size_mb": round(model_size_mb, 2),
        "overall": {
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "map50": round(map50, 4),
            "map50_95": round(map50_95, 4),
            "f1_score": round(f1, 4),
        },
        "per_class": per_class_metrics,
        "performance": {
            "inference_ms": round(inference_ms, 2),
            "preprocess_ms": round(preprocess_ms, 2),
            "postprocess_ms": round(postprocess_ms, 2),
            "total_latency_ms": round(total_ms, 2),
            "throughput_fps": round(fps, 1),
            "device": device,
        }
    }

    # Print clean benchmark report
    print("\n" + "=" * 65)
    print("           CivicAI Final TEST Set Evaluation Report")
    print("=" * 65)
    print(f"Model:           {model_path.name}")
    print(f"Model File Size: {model_size_mb:.2f} MB")
    print(f"Evaluation Mode: Strictly Unseen TEST Split")
    print(f"Device:          {device.upper()}")
    print("-" * 65)
    print(f"Generalization Accuracy:")
    print(f"  Precision:     {precision:.4f}")
    print(f"  Recall:        {recall:.4f}")
    print(f"  mAP@50:        {map50:.4f}")
    print(f"  mAP@50-95:     {map50_95:.4f}")
    print(f"  F1 Score:      {f1:.4f}")
    print("-" * 65)
    print(f"Speed & Throughput Benchmarks:")
    print(f"  Inference Latency: {inference_ms:.2f} ms")
    print(f"  Total Pipeline:    {total_ms:.2f} ms")
    print(f"  Throughput:        {fps:.1f} frames/second")
    print("-" * 65)

    if per_class_metrics:
        print(f"{'Class':<22} | {'Precision':>10} | {'Recall':>10} | {'mAP50':>10} | {'mAP50-95':>10}")
        print("-" * 65)
        for c in per_class_metrics:
            print(f"{c['class_name']:<22} | {c['precision']:>10.4f} | {c['recall']:>10.4f} | {c['map50']:>10.4f} | {c['map50_95']:>10.4f}")
    print("=" * 65 + "\n")

    out_dir = Path(__file__).parent.parent / "outputs" / "evaluation"
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = out_dir / "test_metrics.json"
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    logger.info(f"Test evaluation results saved to: {metrics_file}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Evaluate CivicAI model on the test split.")
    parser.add_argument("--model", type=str, default="ml/models/trained/civic_yolo_best.pt", help="Path to model weights (.pt)")
    parser.add_argument("--data", type=str, default=None, help="Path to data.yaml")
    parser.add_argument("--imgsz", type=int, default=640, help="Image resolution")
    parser.add_argument("--conf", type=float, default=0.25, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.60, help="NMS IoU threshold")
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, 0")
    args = parser.parse_args()

    run_test_evaluation(
        model_path=args.model,
        data_yaml=args.data,
        imgsz=args.imgsz,
        conf=args.conf,
        iou=args.iou,
        device=args.device
    )


if __name__ == "__main__":
    main()
