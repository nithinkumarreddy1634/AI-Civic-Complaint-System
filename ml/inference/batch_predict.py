"""Batch inference processor for directories of civic complaint images.

Processes image directories, exports detections to CSV and JSON reports,
and renders annotated bounding-box prediction visualizations.
"""
import argparse
import csv
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from tqdm import tqdm

from ml.inference.predict import predict_single_image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("batch_predict")


def run_batch_inference(
    source_dir: Path | str,
    model_path: Path | str,
    output_dir: Path | str | None = None,
    conf_threshold: float = 0.40,
    iou_threshold: float = 0.50,
    device: str = "auto",
    save_vis: bool = True
) -> Dict[str, Any]:
    """Runs batch inference across all images in source_dir and writes summary files."""
    src = Path(source_dir)
    if not src.exists() or not src.is_dir():
        raise NotADirectoryError(f"Source directory not found: {src}")

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "outputs" / "predictions"
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exts = {".jpg", ".jpeg", ".png", ".webp"}
    images = [p for p in src.iterdir() if p.is_file() and p.suffix.lower() in exts]

    logger.info(f"Found {len(images)} images in {src}. Running batch inference (conf={conf_threshold})...")

    all_results: List[Dict[str, Any]] = []
    csv_rows: List[List[Any]] = []

    for img_p in tqdm(images, desc="Predicting"):
        res = predict_single_image(
            image_path=img_p,
            model_path=model_path,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            device=device,
            save_vis=save_vis,
            vis_output_dir=out_dir
        )
        all_results.append(res)

        detections = res.get("detections", [])
        if detections:
            for d in detections:
                bbox = d.get("bbox", [0, 0, 0, 0])
                csv_rows.append([
                    img_p.name,
                    d.get("class_name", "unknown"),
                    d.get("confidence", 0.0),
                    bbox[0],
                    bbox[1],
                    bbox[2],
                    bbox[3]
                ])
        else:
            # Background / normal image without defect
            csv_rows.append([
                img_p.name,
                "normal" if res.get("status") == "success" else "rejected",
                1.0 if res.get("status") == "success" else 0.0,
                0, 0, 0, 0
            ])

    # 1. Export JSON summary
    json_path = out_dir / "predictions_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)

    # 2. Export CSV summary
    csv_path = out_dir / "predictions_summary.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Image", "Detected Class", "Confidence", "X1", "Y1", "X2", "Y2"])
        writer.writerows(csv_rows)

    summary = {
        "total_images": len(images),
        "total_detections": sum(len(r.get("detections", [])) for r in all_results),
        "json_report": str(json_path),
        "csv_report": str(csv_path),
        "visualizations_dir": str(out_dir) if save_vis else None
    }

    logger.info(f"Batch prediction completed: {summary['total_detections']} detections across {len(images)} images.")
    logger.info(f"Reports saved to: {csv_path} and {json_path}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Batch inference on directory of civic images.")
    parser.add_argument("--source-dir", type=str, required=True, help="Directory containing images")
    parser.add_argument("--model", type=str, default="ml/models/trained/civic_yolo_best.pt", help="Path to model weights")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for reports & visuals")
    parser.add_argument("--conf", type=float, default=0.40, help="Confidence threshold")
    parser.add_argument("--iou", type=float, default=0.50, help="NMS IoU threshold")
    parser.add_argument("--device", type=str, default="auto", help="Device: auto, cpu, 0")
    parser.add_argument("--no-vis", action="store_true", help="Disable rendering annotated visual images")
    args = parser.parse_args()

    run_batch_inference(
        source_dir=args.source_dir,
        model_path=args.model,
        output_dir=args.output_dir,
        conf_threshold=args.conf,
        iou_threshold=args.iou,
        device=args.device,
        save_vis=not args.no_vis
    )


if __name__ == "__main__":
    main()
