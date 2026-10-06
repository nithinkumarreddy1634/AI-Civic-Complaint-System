"""Sample visualization utility.

Draws bounding boxes, class names, and IDs on images to inspect annotation
quality visually. Generates sample directories per class and an overall montage.
"""
import argparse
import logging
import random
from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import numpy as np
import matplotlib.pyplot as plt

from ml.preprocessing.config import load_config, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("visualize_samples")

# High-contrast color palette in BGR for cv2
COLOR_PALETTE = [
    (0, 0, 255),      # 0: pothole - Red
    (0, 165, 255),    # 1: garbage - Orange
    (0, 255, 255),    # 2: open_manhole - Yellow
    (0, 255, 0),      # 3: damaged_road - Green
    (255, 255, 0),    # 4: broken_streetlight - Cyan
    (255, 0, 0),      # 5: water_leakage - Blue
    (255, 0, 255),    # 6: damaged_sidewalk - Magenta
    (128, 0, 128),    # 7: fallen_tree - Purple
    (0, 128, 255),    # 8: illegal_dumping - Light Orange
    (128, 128, 128),  # 9: normal - Gray
]


def get_color(cls_id: int) -> Tuple[int, int, int]:
    """Returns consistent BGR color tuple for a class ID."""
    return COLOR_PALETTE[cls_id % len(COLOR_PALETTE)]


def draw_bounding_boxes(
    image: np.ndarray,
    labels: List[Tuple[int, float, float, float, float]],
    config: DatasetConfig
) -> np.ndarray:
    """Draws YOLO normalized bounding boxes on an image with labels."""
    h, w = image.shape[:2]
    annotated = image.copy()

    for cls_id, x_c, y_c, bw, bh in labels:
        # Convert normalized YOLO format (center_x, center_y, w, h) to pixel corners
        xmin = int((x_c - bw / 2.0) * w)
        ymin = int((y_c - bh / 2.0) * h)
        xmax = int((x_c + bw / 2.0) * w)
        ymax = int((y_c + bh / 2.0) * h)

        xmin = max(0, xmin)
        ymin = max(0, ymin)
        xmax = min(w - 1, xmax)
        ymax = min(h - 1, ymax)

        color = get_color(cls_id)
        cv2.rectangle(annotated, (xmin, ymin), (xmax, ymax), color, 2)

        cls_name = config.classes.get(cls_id, f"class_{cls_id}")
        label_text = f"{cls_id}: {cls_name}"

        # Draw label background box
        (tw, th), baseline = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        bg_ymin = max(0, ymin - th - 6)
        cv2.rectangle(annotated, (xmin, bg_ymin), (xmin + tw + 4, bg_ymin + th + 6), color, -1)
        # Draw label text in white or black
        cv2.putText(
            annotated,
            label_text,
            (xmin + 2, bg_ymin + th + 2),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1,
            cv2.LINE_AA
        )

    return annotated


def find_class_images(images_dir: Path, labels_dir: Path, exts: set) -> Dict[int, List[Path]]:
    """Maps class_id -> list of image paths that contain that class."""
    class_map: Dict[int, List[Path]] = {}
    if not images_dir.exists() or not labels_dir.exists():
        return class_map

    for img_path in images_dir.iterdir():
        if not (img_path.is_file() and img_path.suffix.lower() in exts):
            continue

        lbl_path = labels_dir / f"{img_path.stem}.txt"
        if not lbl_path.exists():
            continue

        with open(lbl_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 5:
                    try:
                        cls_id = int(parts[0])
                        class_map.setdefault(cls_id, []).append(img_path)
                    except ValueError:
                        continue
    return class_map


def create_montage(
    sample_images: Dict[str, np.ndarray],
    output_path: Path,
    title: str = "CivicAI Dataset Class Samples"
):
    """Creates and saves a grid montage of class samples using matplotlib."""
    if not sample_images:
        return

    n_classes = len(sample_images)
    cols = min(3, n_classes)
    rows = (n_classes + cols - 1) // cols

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 5, rows * 4))
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = np.array([axes])
    elif cols == 1:
        axes = np.array([[ax] for ax in axes])

    items = list(sample_images.items())
    for idx, ax in enumerate(axes.flat):
        if idx < len(items):
            cls_name, img_bgr = items[idx]
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            ax.imshow(img_rgb)
            ax.set_title(cls_name, fontsize=12, fontweight="bold")
            ax.axis("off")
        else:
            ax.axis("off")

    plt.suptitle(title, fontsize=16, fontweight="bold")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(output_path), dpi=150, bbox_inches="tight")
    plt.close()
    logger.info(f"Montage saved to: {output_path}")


def visualize_dataset(
    dataset_dir: Path,
    output_dir: Path,
    config: DatasetConfig,
    num_samples_per_class: int = 5,
    split: str = "train"
):
    """Generates visual annotations for samples of each class in the chosen split."""
    images_dir = dataset_dir / split / "images"
    labels_dir = dataset_dir / split / "labels"
    exts = set(config.image.supported_extensions)

    class_images = find_class_images(images_dir, labels_dir, exts)
    montage_samples: Dict[str, np.ndarray] = {}

    for cls_id, cls_name in config.classes.items():
        img_paths = list(set(class_images.get(cls_id, [])))
        if not img_paths:
            logger.info(f"No sample images found for class {cls_id} ({cls_name}) in split '{split}'.")
            continue

        selected = random.sample(img_paths, min(len(img_paths), num_samples_per_class))
        cls_out_dir = output_dir / cls_name
        cls_out_dir.mkdir(parents=True, exist_ok=True)

        for i, img_path in enumerate(selected):
            img = cv2.imread(str(img_path))
            if img is None:
                continue

            lbl_path = labels_dir / f"{img_path.stem}.txt"
            labels = []
            if lbl_path.exists():
                with open(lbl_path, "r", encoding="utf-8") as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) == 5:
                            labels.append((
                                int(parts[0]),
                                float(parts[1]),
                                float(parts[2]),
                                float(parts[3]),
                                float(parts[4])
                            ))

            annotated = draw_bounding_boxes(img, labels, config)
            out_img_path = cls_out_dir / f"sample_{i+1:02d}_{img_path.name}"
            cv2.imwrite(str(out_img_path), annotated)

            if cls_name not in montage_samples:
                montage_samples[cls_name] = annotated

    # Generate overview montage
    montage_path = output_dir / "class_samples_montage.png"
    create_montage(montage_samples, montage_path)


def main():
    parser = argparse.ArgumentParser(description="Visualize annotated civic infrastructure dataset samples.")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Root datasets directory")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for visualizations")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    parser.add_argument("--num-samples", type=int, default=5, help="Number of samples per class")
    parser.add_argument("--split", type=str, default="train", choices=["train", "val", "test"], help="Split to sample from")
    args = parser.parse_args()

    config = load_config(args.config)
    dataset_dir = Path(args.dataset_dir) if args.dataset_dir else Path(__file__).parent.parent / "datasets"
    output_dir = Path(args.output_dir) if args.output_dir else dataset_dir / "processed" / "visualizations"

    logger.info(f"Generating visualizations from '{args.split}' split to '{output_dir}'...")
    visualize_dataset(dataset_dir, output_dir, config, args.num_samples, args.split)
    logger.info("Visualizations complete.")


if __name__ == "__main__":
    main()
