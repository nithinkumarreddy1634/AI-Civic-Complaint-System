"""Cross-split data leakage detection utility.

Ensures that no exact duplicates (MD5) or visually near-identical frames (pHash)
leak between train, validation, and test splits.
"""
import argparse
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Tuple
from PIL import Image
import imagehash
from tqdm import tqdm

from ml.preprocessing.config import load_config, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("check_leakage")


def compute_md5(file_path: Path) -> str:
    """Computes MD5 checksum of a file."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def compute_phash(file_path: Path, hash_size: int = 16) -> imagehash.ImageHash | None:
    """Computes perceptual hash for visual similarity matching."""
    try:
        with Image.open(file_path) as img:
            return imagehash.phash(img, hash_size=hash_size)
    except Exception as e:
        logger.debug(f"Could not compute pHash for {file_path}: {e}")
        return None


def detect_leakage(dataset_dir: Path, config: DatasetConfig) -> Dict[str, Any]:
    """Scans train, val, and test splits for cross-split duplicates."""
    splits = ["train", "val", "test"]
    split_images: Dict[str, List[Path]] = {}
    exts = set(config.image.supported_extensions)

    for s in splits:
        img_dir = dataset_dir / s / "images"
        if img_dir.exists():
            split_images[s] = [p for p in img_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]
        else:
            split_images[s] = []

    report = {
        "filename_duplicates": [],
        "content_duplicates_md5": [],
        "perceptual_duplicates_phash": [],
        "has_leakage": False
    }

    # 1. Filename overlap
    seen_filenames: Dict[str, str] = {}
    for s, paths in split_images.items():
        for p in paths:
            if p.name in seen_filenames:
                report["filename_duplicates"].append({
                    "filename": p.name,
                    "split1": seen_filenames[p.name],
                    "split2": s
                })
            else:
                seen_filenames[p.name] = s

    # 2. MD5 exact content duplicates
    md5_registry: Dict[str, Tuple[str, Path]] = {}  # md5 -> (split, path)
    for s, paths in split_images.items():
        for p in paths:
            h = compute_md5(p)
            if h in md5_registry:
                orig_split, orig_path = md5_registry[h]
                if orig_split != s:
                    report["content_duplicates_md5"].append({
                        "file1": str(orig_path),
                        "file2": str(p),
                        "split1": orig_split,
                        "split2": s,
                        "md5": h
                    })
            else:
                md5_registry[h] = (s, p)

    # 3. Perceptual hashing across splits
    phash_dict: Dict[str, List[Tuple[Path, imagehash.ImageHash]]] = {s: [] for s in splits}
    total_imgs = sum(len(paths) for paths in split_images.values())

    if total_imgs > 0:
        logger.info(f"Computing perceptual hashes across {total_imgs} images for leakage detection...")
        for s, paths in split_images.items():
            for p in tqdm(paths, desc=f"pHash {s}"):
                h = compute_phash(p, hash_size=config.duplicates.hash_size)
                if h is not None:
                    phash_dict[s].append((p, h))

        thresh = config.duplicates.similarity_threshold
        # Compare train vs val, train vs test, val vs test
        pairs_to_check = [("train", "val"), ("train", "test"), ("val", "test")]
        for s1, s2 in pairs_to_check:
            for p1, h1 in phash_dict[s1]:
                for p2, h2 in phash_dict[s2]:
                    dist = h1 - h2
                    if dist <= thresh:
                        report["perceptual_duplicates_phash"].append({
                            "file1": str(p1),
                            "file2": str(p2),
                            "split1": s1,
                            "split2": s2,
                            "hamming_distance": int(dist)
                        })

    if (
        report["filename_duplicates"]
        or report["content_duplicates_md5"]
        or report["perceptual_duplicates_phash"]
    ):
        report["has_leakage"] = True

    return report


def format_leakage_report(report: Dict[str, Any]) -> str:
    """Formats leakage dictionary into a readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("           CivicAI Cross-Split Data Leakage Report")
    lines.append("=" * 60)

    # Filename duplicates
    f_dups = report["filename_duplicates"]
    lines.append(f"\n[1] Filename Duplicates Across Splits: {len(f_dups)}")
    if f_dups:
        for item in f_dups[:10]:
            lines.append(f"  - '{item['filename']}' exists in both [{item['split1']}] and [{item['split2']}]")
        if len(f_dups) > 10:
            lines.append(f"  ... and {len(f_dups) - 10} more.")
    else:
        lines.append("  [OK] No identical filenames across splits.")

    # MD5 duplicates
    m_dups = report["content_duplicates_md5"]
    lines.append(f"\n[2] Exact Content Duplicates (MD5): {len(m_dups)}")
    if m_dups:
        for item in m_dups[:10]:
            lines.append(f"  - [{item['split1']}] {Path(item['file1']).name} == [{item['split2']}] {Path(item['file2']).name}")
        if len(m_dups) > 10:
            lines.append(f"  ... and {len(m_dups) - 10} more.")
    else:
        lines.append("  [OK] No exact duplicate files detected across splits.")

    # pHash near duplicates
    p_dups = report["perceptual_duplicates_phash"]
    lines.append(f"\n[3] Perceptual Near-Duplicates (pHash): {len(p_dups)}")
    if p_dups:
        for item in p_dups[:10]:
            lines.append(f"  - [{item['split1']}] {Path(item['file1']).name} ~ [{item['split2']}] {Path(item['file2']).name} (dist={item['hamming_distance']})")
        if len(p_dups) > 10:
            lines.append(f"  ... and {len(p_dups) - 10} more.")
    else:
        lines.append("  [OK] No visually near-identical images found across splits.")

    lines.append("\n" + "-" * 60)
    if report["has_leakage"]:
        lines.append("RESULT: [!] POTENTIAL DATA LEAKAGE DETECTED across splits.")
        lines.append("RECOMMENDATION: Remove or quarantine identified pairs to ensure generalization.")
    else:
        lines.append("RESULT: [OK] No data leakage detected between train/val/test splits.")
    lines.append("=" * 60 + "\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check for data leakage between train/val/test splits.")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Datasets directory containing train/val/test.")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else Path(__file__).parent.parent / "datasets"

    report = detect_leakage(dataset_dir, config)
    report_text = format_leakage_report(report)
    print(report_text)


if __name__ == "__main__":
    main()
