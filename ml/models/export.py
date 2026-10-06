"""Model export utility for CivicAI YOLO models.

Exports trained PyTorch (.pt) weights to ONNX format for efficient CPU/edge inference.
"""
import argparse
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("model_export")


def export_model_to_onnx(
    model_path: Path | str,
    imgsz: int = 640,
    dynamic: bool = False,
    simplify: bool = True
) -> Path:
    """Exports a trained YOLO model to ONNX format."""
    from ultralytics import YOLO

    p = Path(model_path)
    if not p.exists():
        raise FileNotFoundError(f"Model file not found: {p}")

    logger.info(f"Loading model for export: {p}")
    model = YOLO(str(p))

    logger.info(f"Exporting to ONNX format (imgsz={imgsz}, dynamic={dynamic}, simplify={simplify})...")
    exported_path = model.export(
        format="onnx",
        imgsz=imgsz,
        dynamic=dynamic,
        simplify=simplify
    )

    out_p = Path(exported_path)
    logger.info(f"Model successfully exported to: {out_p} ({out_p.stat().st_size / (1024*1024):.2f} MB)")
    return out_p


def main():
    parser = argparse.ArgumentParser(description="Export CivicAI YOLO model to ONNX format.")
    parser.add_argument("--model", type=str, default="ml/models/trained/civic_yolo_best.pt", help="Path to .pt model")
    parser.add_argument("--imgsz", type=int, default=640, help="Input resolution")
    parser.add_argument("--dynamic", action="store_true", help="Enable dynamic input shape")
    args = parser.parse_args()

    export_model_to_onnx(args.model, args.imgsz, args.dynamic)


if __name__ == "__main__":
    main()
