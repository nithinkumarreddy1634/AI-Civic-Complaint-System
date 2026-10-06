"""Master pipeline orchestrator for CivicAI dataset preparation.

Executes the entire workflow in sequence:
1. Validation & Quarantine
2. Exact & Perceptual Duplicate Removal
3. Annotation Conversion (VOC / COCO -> YOLO)
4. Aspect-ratio Preserving Resizing & Bounding Box Coordinate Mapping
5. Reproducible Train / Validation / Test Splitting
6. Cross-split Data Leakage Auditing
7. Dataset Statistics & Quality Reporting
8. Sample Bounding Box Visualizations
9. Version Metadata Archival
"""
import argparse
import logging
import sys
import subprocess
from pathlib import Path
from typing import List, Dict

from ml.preprocessing.config import load_config, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("run_pipeline")


def run_python_step(module_name: str, args: List[str]) -> bool:
    """Runs a pipeline step as a Python module subprocess."""
    cmd = [sys.executable, "-m", f"ml.preprocessing.{module_name}"] + args
    logger.info(f"Executing step [{module_name}] with: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        logger.error(f"Step [{module_name}] failed with returncode {result.returncode}")
        return False
    return True


def execute_pipeline(config_path: Path | None, skip_steps: List[str], version_tag: str, dry_run: bool = False):
    """Executes all preprocessing steps in orderly sequence."""
    config = load_config(config_path)
    ml_dir = Path(__file__).parent.parent
    datasets_dir = ml_dir / "datasets"

    raw_dir = datasets_dir / "raw"
    quarantine_dir = datasets_dir / "quarantine"
    processed_dir = datasets_dir / "processed"
    cfg_arg = ["--config", str(config_path)] if config_path else []

    status_summary: Dict[str, str] = {}

    pipeline_steps = [
        ("validate", "validate_images", [
            "--input-dir", str(raw_dir),
            "--quarantine-dir", str(quarantine_dir)
        ] + cfg_arg),
        ("dedup", "remove_duplicates", [
            "--input-dir", str(raw_dir),
            "--quarantine-dir", str(quarantine_dir),
            "--method", "both"
        ] + (["--dry-run"] if dry_run else []) + cfg_arg),
        ("resize", "resize_images", [
            "--input-dir", str(raw_dir),
            "--output-dir", str(processed_dir / "images"),
            "--labels-dir", str(raw_dir),
            "--output-labels-dir", str(processed_dir / "labels")
        ] + cfg_arg),
        ("split", "split_dataset", [
            "--input-dir", str(processed_dir / "images"),
            "--labels-dir", str(processed_dir / "labels"),
            "--output-dir", str(datasets_dir)
        ] + cfg_arg),
        ("leakage", "check_leakage", [
            "--dataset-dir", str(datasets_dir)
        ] + cfg_arg),
        ("stats", "dataset_statistics", [
            "--dataset-dir", str(datasets_dir)
        ] + cfg_arg),
        ("visualize", "visualize_samples", [
            "--dataset-dir", str(datasets_dir),
            "--output-dir", str(datasets_dir / "processed" / "visualizations"),
            "--num-samples", "3"
        ] + cfg_arg),
        ("version", "dataset_version", [
            "--dataset-dir", str(datasets_dir),
            "--version", version_tag,
            "--description", "Automated pipeline run dataset snapshot"
        ] + cfg_arg)
    ]

    print("\n" + "=" * 65)
    print("        Starting CivicAI Dataset Preprocessing Pipeline")
    print("=" * 65 + "\n")

    for step_id, module_name, step_args in pipeline_steps:
        if step_id in skip_steps:
            logger.info(f"Skipping step [{step_id}] per user request.")
            status_summary[step_id] = "SKIPPED"
            continue

        if dry_run and step_id in ["resize", "split", "version"]:
            logger.info(f"Dry-run enabled: skipping file-modifying step [{step_id}].")
            status_summary[step_id] = "DRY-RUN (SKIPPED)"
            continue

        success = run_python_step(module_name, step_args)
        status_summary[step_id] = "SUCCESS" if success else "FAILED"
        if not success and step_id in ["validate", "split"]:
            logger.error(f"Critical step [{step_id}] failed. Halting pipeline execution.")
            break

    print("\n" + "=" * 65)
    print("                   Pipeline Execution Summary")
    print("=" * 65)
    for step_id, status in status_summary.items():
        print(f"  - Step: {step_id:<14} Result: {status}")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Run complete CivicAI dataset preprocessing pipeline.")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    parser.add_argument("--skip", nargs="*", default=[], help="Step IDs to skip (e.g. dedup visualize)")
    parser.add_argument("--version", type=str, default="v1", help="Version identifier tag (default: v1)")
    parser.add_argument("--dry-run", action="store_true", help="Audit dataset without making destructive file changes")
    args = parser.parse_args()

    cfg_p = Path(args.config) if args.config else None
    execute_pipeline(cfg_p, args.skip, args.version, args.dry_run)


if __name__ == "__main__":
    main()
