"""Dataset versioning and metadata management utility.

Maintains immutable version records with integrity checksums, class distributions,
and preprocessing hyperparameters to guarantee experiment reproducibility.
"""
import argparse
import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

from ml.preprocessing.config import load_config, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("dataset_version")


def compute_dataset_checksum(dataset_dir: Path, exts: set) -> str:
    """Computes a composite MD5 checksum across all images and labels."""
    hasher = hashlib.md5()
    all_files: List[Path] = []
    for split in ["train", "val", "test"]:
        split_dir = dataset_dir / split
        if split_dir.exists():
            for p in split_dir.rglob("*"):
                if p.is_file() and (p.suffix.lower() in exts or p.suffix.lower() == ".txt"):
                    all_files.append(p)

    # Sort to ensure deterministic hashing
    all_files.sort(key=lambda p: str(p.relative_to(dataset_dir)))
    for fpath in all_files:
        hasher.update(fpath.name.encode("utf-8"))
        with open(fpath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                hasher.update(chunk)

    return hasher.hexdigest()


def count_split_images(split_dir: Path, exts: set) -> int:
    """Counts valid images in a split directory."""
    img_dir = split_dir / "images"
    if not img_dir.exists():
        return 0
    return sum(1 for p in img_dir.iterdir() if p.is_file() and p.suffix.lower() in exts)


def create_version_metadata(
    dataset_dir: Path,
    version: str,
    description: str,
    config: DatasetConfig
) -> Path:
    """Generates and writes a version metadata JSON file."""
    versions_dir = dataset_dir / "versions"
    versions_dir.mkdir(parents=True, exist_ok=True)
    version_file = versions_dir / f"dataset_{version}.json"

    if version_file.exists():
        raise FileExistsError(f"Dataset version '{version}' already exists at {version_file}. Please use a new version identifier.")

    exts = set(config.image.supported_extensions)
    train_count = count_split_images(dataset_dir / "train", exts)
    val_count = count_split_images(dataset_dir / "val", exts)
    test_count = count_split_images(dataset_dir / "test", exts)
    total_images = train_count + val_count + test_count

    logger.info("Computing dataset checksum for version verification...")
    checksum = compute_dataset_checksum(dataset_dir, exts)

    metadata: Dict[str, Any] = {
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "description": description,
        "total_images": total_images,
        "train_images": train_count,
        "val_images": val_count,
        "test_images": test_count,
        "classes": {str(k): v for k, v in config.classes.items()},
        "num_classes": config.num_classes,
        "split_ratios": {
            "train": config.split.train,
            "val": config.split.val,
            "test": config.split.test
        },
        "random_seed": config.split.random_seed,
        "preprocessing": {
            "target_size": config.image.target_size,
            "letterbox": config.image.letterbox,
            "augmentation_enabled": config.augmentation.enabled,
            "augmented_per_image": config.augmentation.per_image
        },
        "sources": [s.get("name", "Unknown") for s in config.sources],
        "md5_checksum": checksum
    }

    with open(version_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    logger.info(f"Dataset version metadata successfully saved: {version_file}")
    return version_file


def list_versions(dataset_dir: Path):
    """Lists all saved dataset versions."""
    versions_dir = dataset_dir / "versions"
    if not versions_dir.exists():
        print("No versions directory found.")
        return

    version_files = sorted(versions_dir.glob("dataset_*.json"))
    if not version_files:
        print("No dataset versions found.")
        return

    print("=" * 65)
    print("                     CivicAI Dataset Versions")
    print("=" * 65)
    for vf in version_files:
        try:
            with open(vf, "r", encoding="utf-8") as f:
                meta = json.load(f)
            v = meta.get("version", "N/A")
            dt = meta.get("created_at", "N/A")[:10]
            imgs = meta.get("total_images", 0)
            desc = meta.get("description", "")
            chk = meta.get("md5_checksum", "")[:8]
            print(f"[{v:<6}] Date: {dt} | Total Images: {imgs:>6} | MD5: {chk}.. | {desc}")
        except Exception as e:
            print(f"Error reading {vf.name}: {e}")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="Manage CivicAI dataset versions.")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Root datasets directory")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    parser.add_argument("--version", type=str, default=None, help="Version tag, e.g. 'v1'")
    parser.add_argument("--description", type=str, default="Dataset release version", help="Description of changes")
    parser.add_argument("--list", action="store_true", help="List existing dataset versions")
    args = parser.parse_args()

    config = load_config(args.config)
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else Path(__file__).parent.parent / "datasets"

    if args.list:
        list_versions(dataset_dir)
        return

    if not args.version:
        parser.error("--version is required when creating a new dataset version metadata file.")

    create_version_metadata(dataset_dir, args.version, args.description, config)


if __name__ == "__main__":
    main()
