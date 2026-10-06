"""Data augmentation pipeline using Albumentations.

Augments civic infrastructure images with bounding boxes in YOLO format.
Ensures realistic domain transformations (e.g. no vertical flips for gravity-sensitive
infrastructure like falling trees, potholes, water leaks).
"""
import argparse
import logging
from pathlib import Path
from typing import List, Tuple
import cv2
import albumentations as A
from tqdm import tqdm

from ml.preprocessing.config import load_config, validate_yolo_label, DatasetConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("augment_dataset")


def build_augmentation_pipeline(config: DatasetConfig) -> A.Compose:
    """Builds Albumentations Compose pipeline honoring dataset_config constraints."""
    aug_cfg = config.augmentation
    transforms = [
        A.HorizontalFlip(p=aug_cfg.horizontal_flip),
        A.RandomBrightnessContrast(
            brightness_limit=aug_cfg.brightness_limit,
            contrast_limit=aug_cfg.contrast_limit,
            p=0.5
        ),
        A.Rotate(
            limit=aug_cfg.rotation_limit,
            border_mode=cv2.BORDER_CONSTANT,
            value=config.image.letterbox_color,
            p=0.5
        ),
        A.RandomScale(scale_limit=aug_cfg.scale_limit, p=0.4),
        A.GaussianBlur(blur_limit=(3, max(3, aug_cfg.blur_limit)), p=0.3),
        A.GaussNoise(var_limit=(10.0, max(10.0, float(aug_cfg.noise_var_limit))), p=0.3),
        A.Perspective(scale=(0.01, aug_cfg.perspective_limit), p=0.3),
    ]

    return A.Compose(
        transforms,
        bbox_params=A.BboxParams(
            format="yolo",
            label_fields=["class_labels"],
            min_visibility=0.2,
            check_each_transform=False
        )
    )


def load_yolo_labels(label_file: Path) -> Tuple[List[List[float]], List[int]]:
    """Loads YOLO format bboxes and class labels."""
    bboxes = []
    class_labels = []

    if not label_file.exists():
        return bboxes, class_labels

    with open(label_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 5:
                cls_id = int(parts[0])
                coords = [float(p) for p in parts[1:]]
                # Clamp coordinates slightly if small numerical inaccuracy
                x, y, w, h = coords
                x = min(max(x, 0.0), 1.0)
                y = min(max(y, 0.0), 1.0)
                w = min(max(w, 0.001), 1.0)
                h = min(max(h, 0.001), 1.0)
                bboxes.append([x, y, w, h])
                class_labels.append(cls_id)

    return bboxes, class_labels


def save_yolo_labels(label_file: Path, bboxes: List[List[float]], class_labels: List[int], num_classes: int) -> int:
    """Saves YOLO labels and validates each line before writing."""
    valid_count = 0
    lines = []
    for cls_id, bbox in zip(class_labels, bboxes):
        x, y, w, h = bbox
        line = f"{cls_id} {x:.6f} {y:.6f} {w:.6f} {h:.6f}"
        is_valid, msg = validate_yolo_label(line, num_classes)
        if is_valid:
            lines.append(line)
            valid_count += 1
        else:
            logger.debug(f"Skipping invalid augmented bbox: {msg}")

    with open(label_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))

    return valid_count


def augment_directory(
    images_dir: Path,
    labels_dir: Path,
    out_images_dir: Path,
    out_labels_dir: Path,
    config: DatasetConfig,
    num_augmented: int | None = None
) -> Tuple[int, int]:
    """Augments all images in images_dir and saves outputs to target directories."""
    out_images_dir.mkdir(parents=True, exist_ok=True)
    out_labels_dir.mkdir(parents=True, exist_ok=True)

    pipeline = build_augmentation_pipeline(config)
    copies_per_image = num_augmented if num_augmented is not None else config.augmentation.per_image

    exts = set(config.image.supported_extensions)
    image_files = [p for p in images_dir.iterdir() if p.is_file() and p.suffix.lower() in exts]

    total_generated = 0
    total_skipped = 0

    logger.info(f"Augmenting {len(image_files)} images ({copies_per_image} variants per image)...")

    for img_path in tqdm(image_files, desc="Augmenting"):
        img = cv2.imread(str(img_path))
        if img is None:
            total_skipped += 1
            continue

        lbl_path = labels_dir / f"{img_path.stem}.txt"
        bboxes, class_labels = load_yolo_labels(lbl_path)

        for i in range(1, copies_per_image + 1):
            out_stem = f"{img_path.stem}_aug_{i:03d}"
            out_img_path = out_images_dir / f"{out_stem}{img_path.suffix}"
            out_lbl_path = out_labels_dir / f"{out_stem}.txt"

            try:
                transformed = pipeline(image=img, bboxes=bboxes, class_labels=class_labels)
                aug_img = transformed["image"]
                aug_bboxes = transformed["bboxes"]
                aug_classes = transformed["class_labels"]

                cv2.imwrite(str(out_img_path), aug_img)
                save_yolo_labels(out_lbl_path, aug_bboxes, aug_classes, len(config.classes))
                total_generated += 1
            except Exception as e:
                logger.debug(f"Augmentation failed for {img_path.name} variant {i}: {e}")
                total_skipped += 1

    logger.info(f"Augmentation completed: {total_generated} generated, {total_skipped} skipped/failed.")
    return total_generated, total_skipped


def main():
    parser = argparse.ArgumentParser(description="Augment civic infrastructure dataset using Albumentations.")
    parser.add_argument("--input-dir", type=str, required=True, help="Input images directory")
    parser.add_argument("--labels-dir", type=str, required=True, help="Input labels directory")
    parser.add_argument("--output-dir", type=str, required=True, help="Output images directory")
    parser.add_argument("--output-labels-dir", type=str, required=True, help="Output labels directory")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    parser.add_argument("--num-augmented", type=int, default=None, help="Number of augmented copies per image")
    args = parser.parse_args()

    config = load_config(args.config)
    augment_directory(
        Path(args.input_dir),
        Path(args.labels_dir),
        Path(args.output_dir),
        Path(args.output_labels_dir),
        config,
        args.num_augmented
    )


if __name__ == "__main__":
    main()
