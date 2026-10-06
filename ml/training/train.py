"""YOLOv8 Training Runner for Civic Infrastructure Complaint Detection.

Handles pre-flight dataset verification, automatic hardware detection (CUDA/CPU),
experiment directory management, training execution, checkpoint copying,
and comprehensive experiment metadata logging.
"""
import argparse
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Tuple
import yaml

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("civic_train")


def detect_device(preferred: str = "auto") -> str:
    """Detects available computing hardware (CUDA GPU or CPU fallback)."""
    if preferred.lower() == "cpu":
        logger.info("Using CPU per explicit configuration.")
        return "cpu"

    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            logger.info(f"CUDA GPU detected: {device_name}. Training will use GPU acceleration.")
            return "0"
        else:
            logger.info("CUDA not available. Falling back to CPU.")
            return "cpu"
    except ImportError:
        logger.warning("PyTorch not imported yet. Defaulting device to cpu.")
        return "cpu"


def verify_dataset(data_yaml_path: Path) -> Tuple[bool, str, Dict[str, Any]]:
    """Strictly validates dataset structure, image counts, and class alignment before training."""
    if not data_yaml_path.exists():
        return False, f"Dataset configuration file not found at: {data_yaml_path}", {}

    try:
        with open(data_yaml_path, "r", encoding="utf-8") as f:
            data_cfg = yaml.safe_load(f) or {}
    except Exception as e:
        return False, f"Failed to parse YAML from {data_yaml_path}: {e}", {}

    base_dir = data_yaml_path.parent
    train_rel = data_cfg.get("train")
    val_rel = data_cfg.get("val")
    nc = data_cfg.get("nc", 0)
    names = data_cfg.get("names", {})

    if not train_rel or not val_rel:
        return False, "data.yaml must define both 'train' and 'val' split paths.", {}

    train_dir = (base_dir / train_rel).resolve()
    val_dir = (base_dir / val_rel).resolve()

    if not train_dir.exists():
        return False, f"Training images directory does not exist: {train_dir}", {}
    if not val_dir.exists():
        return False, f"Validation images directory does not exist: {val_dir}", {}

    exts = {".jpg", ".jpeg", ".png"}
    train_imgs = [p for p in train_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
    val_imgs = [p for p in val_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]

    # Verify corresponding labels directories
    train_labels_dir = train_dir.parent / "labels"
    val_labels_dir = val_dir.parent / "labels"

    train_lbl_count = sum(1 for p in train_labels_dir.glob("*.txt")) if train_labels_dir.exists() else 0
    val_lbl_count = sum(1 for p in val_labels_dir.glob("*.txt")) if val_labels_dir.exists() else 0

    summary = {
        "train_images": len(train_imgs),
        "val_images": len(val_imgs),
        "train_labels": train_lbl_count,
        "val_labels": val_lbl_count,
        "nc": nc,
        "classes": names,
        "train_path": str(train_dir),
        "val_path": str(val_dir),
    }

    if len(train_imgs) == 0:
        return False, f"Training directory is empty ({train_dir}). Please run dataset preprocessing before training.", summary

    if len(val_imgs) == 0:
        return False, f"Validation directory is empty ({val_dir}).", summary

    logger.info(f"Dataset pre-flight verified: {len(train_imgs)} train images, {len(val_imgs)} val images, {nc} classes.")
    return True, "Dataset configuration valid.", summary


def get_next_experiment_dir(base_output_dir: Path) -> Tuple[Path, str]:
    """Finds next unique experiment folder without overwriting existing experiments."""
    base_output_dir.mkdir(parents=True, exist_ok=True)
    exp_idx = 1
    while True:
        exp_name = f"experiment_{exp_idx:03d}"
        exp_dir = base_output_dir / exp_name
        if not exp_dir.exists():
            exp_dir.mkdir(parents=True, exist_ok=True)
            return exp_dir, exp_name
        exp_idx += 1


def train_model(config_path: Path | str | None = None, overrides: Dict[str, Any] | None = None) -> Path:
    """Executes YOLO model training workflow."""
    from ultralytics import YOLO

    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    config_path = Path(config_path)

    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    # Apply command-line overrides
    if overrides:
        for k, v in overrides.items():
            if v is not None:
                if k in cfg["training"]:
                    cfg["training"][k] = v
                elif k in cfg["model"]:
                    cfg["model"][k] = v

    data_yaml_path = (Path(__file__).parent.parent / cfg["data"]["yaml_path"].replace("ml/", "")).resolve()
    if not data_yaml_path.exists():
        data_yaml_path = Path(cfg["data"]["yaml_path"]).resolve()

    # Pre-flight dataset verification
    is_valid, err_msg, dataset_summary = verify_dataset(data_yaml_path)
    if not is_valid:
        logger.error(f"Pre-flight verification failed: {err_msg}")
        raise RuntimeError(f"Cannot proceed with training: {err_msg}")

    device = detect_device(cfg["training"].get("device", "auto"))
    output_base = Path(__file__).parent.parent / "outputs" / "training"
    exp_dir, exp_name = get_next_experiment_dir(output_base)

    model_variant = cfg["model"]["variant"]
    logger.info(f"Initializing YOLO model: {model_variant}")
    model = YOLO(model_variant)

    start_time = datetime.now(timezone.utc)
    logger.info(f"Starting training run [{exp_name}] at {start_time.isoformat()} on device [{device}]...")

    results = model.train(
        data=str(data_yaml_path),
        imgsz=cfg["training"]["imgsz"],
        epochs=cfg["training"]["epochs"],
        batch=cfg["training"]["batch"],
        patience=cfg["training"]["patience"],
        optimizer=cfg["training"]["optimizer"],
        lr0=cfg["training"]["lr0"],
        seed=cfg["training"]["seed"],
        device=device,
        workers=cfg["training"]["workers"],
        project=str(exp_dir.parent),
        name=exp_name,
        exist_ok=True,
    )

    finish_time = datetime.now(timezone.utc)
    duration_sec = (finish_time - start_time).total_seconds()
    logger.info(f"Training completed in {duration_sec:.1f}s.")

    # Locate generated best.pt
    trained_best = exp_dir / "weights" / "best.pt"
    if not trained_best.exists():
        trained_best = exp_dir / "best.pt"

    trained_models_dir = Path(__file__).parent.parent / "models" / "trained"
    trained_models_dir.mkdir(parents=True, exist_ok=True)
    final_model_target = trained_models_dir / "civic_yolo_best.pt"

    if trained_best.exists():
        shutil.copy2(str(trained_best), str(final_model_target))
        logger.info(f"Best model copied to: {final_model_target}")

    # Extract metrics safely from results object
    metrics_summary = {}
    try:
        if hasattr(results, "results_dict"):
            metrics_summary = results.results_dict
        elif hasattr(results, "maps"):
            metrics_summary = {"mAP50": float(results.maps[0]) if len(results.maps) > 0 else 0.0}
    except Exception as e:
        logger.debug(f"Could not parse results_dict: {e}")

    # Log experiment metadata
    meta = {
        "experiment_name": exp_name,
        "model_variant": model_variant,
        "created_at": start_time.isoformat(),
        "finished_at": finish_time.isoformat(),
        "duration_seconds": duration_sec,
        "device": device,
        "hyperparameters": cfg["training"],
        "dataset_summary": dataset_summary,
        "best_model_path": str(trained_best) if trained_best.exists() else None,
        "production_model_copy": str(final_model_target) if final_model_target.exists() else None,
        "metrics": metrics_summary,
    }

    metadata_file = exp_dir / "experiment_metadata.json"
    with open(metadata_file, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    logger.info(f"Experiment metadata recorded to: {metadata_file}")
    return exp_dir


def main():
    parser = argparse.ArgumentParser(description="Train YOLOv8 on CivicAI infrastructure complaint dataset.")
    parser.add_argument("--config", type=str, default=None, help="Path to training config.yaml")
    parser.add_argument("--epochs", type=int, default=None, help="Override number of epochs")
    parser.add_argument("--batch", type=int, default=None, help="Override batch size")
    parser.add_argument("--imgsz", type=int, default=None, help="Override image resolution")
    parser.add_argument("--device", type=str, default=None, help="Override device: auto, cpu, 0")
    args = parser.parse_args()

    overrides = {
        "epochs": args.epochs,
        "batch": args.batch,
        "imgsz": args.imgsz,
        "device": args.device,
    }

    train_model(args.config, overrides)


if __name__ == "__main__":
    main()
