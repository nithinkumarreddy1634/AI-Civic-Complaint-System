"""Dataset statistics and quality report generator.

Scans train, validation, and test directories to analyze class distributions,
bounding box metrics, image/label integrity, and highlights potential issues.
"""
import argparse
import logging
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any, List

from ml.preprocessing.config import load_config, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("dataset_statistics")


def analyze_split(split_name: str, images_dir: Path, labels_dir: Path, config: DatasetConfig) -> Dict[str, Any]:
    """Analyzes a specific dataset split (train/val/test)."""
    stats: Dict[str, Any] = {
        "split": split_name,
        "total_images": 0,
        "images_with_labels": 0,
        "background_images": 0,
        "missing_labels": 0,
        "total_annotations": 0,
        "class_images": defaultdict(int),
        "class_annotations": defaultdict(int),
        "class_bbox_sizes": defaultdict(list),
        "invalid_labels": 0,
    }

    if not images_dir.exists():
        logger.warning(f"Images directory not found for {split_name}: {images_dir}")
        return stats

    image_extensions = set(config.image.supported_extensions)
    image_files = [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in image_extensions]
    stats["total_images"] = len(image_files)

    for img_path in image_files:
        label_path = labels_dir / f"{img_path.stem}.txt"
        if not label_path.exists():
            stats["missing_labels"] += 1
            continue

        stats["images_with_labels"] += 1
        with open(label_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            stats["background_images"] += 1
            continue

        seen_classes_in_img = set()
        for line in lines:
            parts = line.split()
            if len(parts) != 5:
                stats["invalid_labels"] += 1
                continue
            try:
                cls_id = int(parts[0])
                w = float(parts[3])
                h = float(parts[4])
            except ValueError:
                stats["invalid_labels"] += 1
                continue

            cls_name = config.classes.get(cls_id, f"unknown_{cls_id}")
            seen_classes_in_img.add(cls_name)
            stats["class_annotations"][cls_name] += 1
            stats["total_annotations"] += 1
            stats["class_bbox_sizes"][cls_name].append(w * h)

        for cls_name in seen_classes_in_img:
            stats["class_images"][cls_name] += 1

    return stats


def generate_report(split_stats_list: List[Dict[str, Any]], config: DatasetConfig, output_path: Path | None = None) -> str:
    """Combines stats and generates a human-readable quality report."""
    total_imgs = sum(s["total_images"] for s in split_stats_list)
    total_annos = sum(s["total_annotations"] for s in split_stats_list)
    total_bg = sum(s["background_images"] for s in split_stats_list)
    total_missing = sum(s["missing_labels"] for s in split_stats_list)
    total_invalid = sum(s["invalid_labels"] for s in split_stats_list)

    combined_class_images: Dict[str, int] = defaultdict(int)
    combined_class_annos: Dict[str, int] = defaultdict(int)
    combined_class_sizes: Dict[str, List[float]] = defaultdict(list)

    for s in split_stats_list:
        for c, count in s["class_images"].items():
            combined_class_images[c] += count
        for c, count in s["class_annotations"].items():
            combined_class_annos[c] += count
        for c, sizes in s["class_bbox_sizes"].items():
            combined_class_sizes[c].extend(sizes)

    lines: List[str] = []
    lines.append("=" * 60)
    lines.append("         CivicAI Dataset Quality & Statistics Report")
    lines.append("=" * 60)
    lines.append("\n[Dataset Summary]")
    lines.append(f"  Total Images:        {total_imgs}")
    for s in split_stats_list:
        pct = (s['total_images'] / total_imgs * 100) if total_imgs > 0 else 0.0
        lines.append(f"  - {s['split'].capitalize():<16} {s['total_images']:>6} images ({pct:>5.1f}%)")
    lines.append(f"  Background Images:   {total_bg}")
    lines.append(f"  Total Annotations:   {total_annos}")

    lines.append("\n[Class Distribution]")
    lines.append(f"  {'Class':<22} | {'Images':>8} | {'Annotations':>12} | {'% of Anno':>10}")
    lines.append("  " + "-" * 58)

    detection_classes = list(config.detection_classes.values())
    for cls_name in detection_classes:
        imgs = combined_class_images.get(cls_name, 0)
        annos = combined_class_annos.get(cls_name, 0)
        pct = (annos / total_annos * 100) if total_annos > 0 else 0.0
        lines.append(f"  {cls_name:<22} | {imgs:>8} | {annos:>12} | {pct:>9.1f}%")

    lines.append("\n[Bounding Box Geometry (Normalized Area = w * h)]")
    lines.append(f"  {'Class':<22} | {'Avg Area':>10} | {'Min Area':>10} | {'Max Area':>10}")
    lines.append("  " + "-" * 58)
    for cls_name in detection_classes:
        sizes = combined_class_sizes.get(cls_name, [])
        if sizes:
            avg_sz = sum(sizes) / len(sizes)
            min_sz = min(sizes)
            max_sz = max(sizes)
            lines.append(f"  {cls_name:<22} | {avg_sz:>10.4f} | {min_sz:>10.4f} | {max_sz:>10.4f}")
        else:
            lines.append(f"  {cls_name:<22} | {'N/A':>10} | {'N/A':>10} | {'N/A':>10}")

    lines.append("\n[Annotation Integrity]")
    lines.append(f"  Valid Labels:        {sum(s['images_with_labels'] for s in split_stats_list) - total_invalid}")
    lines.append(f"  Invalid Labels:      {total_invalid}")
    lines.append(f"  Missing Labels:      {total_missing}")

    lines.append("\n[Potential Issues & Recommendations]")
    issues_found = False
    for cls_name in detection_classes:
        cnt = combined_class_images.get(cls_name, 0)
        if cnt < 50:
            lines.append(f"  [!] Severe class imbalance: '{cls_name}' has only {cnt} sample images (recommended >= 100).")
            issues_found = True

    if total_missing > 0:
        lines.append(f"  [!] Missing label files detected ({total_missing} images lack matching .txt).")
        issues_found = True

    if total_invalid > 0:
        lines.append(f"  [!] Invalid annotation lines found ({total_invalid}). Check formatting.")
        issues_found = True

    if not issues_found:
        lines.append("  [OK] No major dataset anomalies or severe imbalance detected.")

    lines.append("=" * 60 + "\n")
    report_text = "\n".join(lines)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        logger.info(f"Statistics report saved to: {output_path}")

    return report_text


def main():
    parser = argparse.ArgumentParser(description="Generate CivicAI dataset statistics and quality report.")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Root datasets dir containing train/val/test.")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    parser.add_argument("--output", type=str, default=None, help="Output path for report file.")
    args = parser.parse_args()

    config = load_config(args.config)
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else Path(__file__).parent.parent / "datasets"

    splits = ["train", "val", "test"]
    split_stats_list = []
    for s in splits:
        img_dir = dataset_dir / s / "images"
        lbl_dir = dataset_dir / s / "labels"
        split_stats_list.append(analyze_split(s, img_dir, lbl_dir, config))

    out_path = Path(args.output) if args.output else dataset_dir / "processed" / "dataset_quality_report.txt"
    report = generate_report(split_stats_list, config, out_path)
    print(report)


if __name__ == "__main__":
    main()
