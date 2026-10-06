"""
Dataset splitting script.
Splits images and labels into train/val/test directories based on group splitting
to prevent data leakage between similar frames in sequence.
"""

import argparse
import logging
import random
import re
import shutil
from collections import defaultdict
from pathlib import Path

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs): return iterable

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("split_dataset")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Split dataset into train/val/test.")
    parser.add_argument("--input-dir", type=str, required=True, help="Input images dir.")
    parser.add_argument("--labels-dir", type=str, required=True, help="Input labels dir.")
    parser.add_argument("--output-dir", type=str, required=True, help="Output dataset root.")
    parser.add_argument("--config", type=str, help="Dataset config path.")
    parser.add_argument("--train", type=float, default=0.7, help="Train split ratio.")
    parser.add_argument("--val", type=float, default=0.2, help="Validation split ratio.")
    parser.add_argument("--test", type=float, default=0.1, help="Test split ratio.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")
    return parser.parse_args()

def get_group_id(filename: str) -> str:
    """Extract a group ID by taking the prefix before the last numeric segment."""
    match = re.match(r"(.*?)_?\d+\.[a-zA-Z]+$", filename)
    if match:
        return match.group(1)
    return Path(filename).stem # Fallback

def main():
    args = parse_args()
    logger = setup_logger()
    
    # Validate ratios
    total_ratio = args.train + args.val + args.test
    if not (0.99 <= total_ratio <= 1.01):
        logger.error(f"Split ratios must sum to 1.0, got {total_ratio}")
        return
        
    random.seed(args.seed)
    
    input_dir = Path(args.input_dir)
    labels_dir = Path(args.labels_dir)
    output_dir = Path(args.output_dir)
    
    images = list(input_dir.rglob("*.jpg")) + list(input_dir.rglob("*.png")) + list(input_dir.rglob("*.jpeg"))
    
    # Group images
    groups = defaultdict(list)
    for img in images:
        group_id = get_group_id(img.name)
        groups[group_id].append(img)
        
    group_keys = list(groups.keys())
    random.shuffle(group_keys)
    
    total_groups = len(group_keys)
    train_idx = int(total_groups * args.train)
    val_idx = train_idx + int(total_groups * args.val)
    
    splits = {
        "train": group_keys[:train_idx],
        "val": group_keys[train_idx:val_idx],
        "test": group_keys[val_idx:]
    }
    
    counts = {"train": 0, "val": 0, "test": 0}
    class_dist = {"train": defaultdict(int), "val": defaultdict(int), "test": defaultdict(int)}
    
    for split_name, g_keys in splits.items():
        img_out = output_dir / "images" / split_name
        lbl_out = output_dir / "labels" / split_name
        img_out.mkdir(parents=True, exist_ok=True)
        lbl_out.mkdir(parents=True, exist_ok=True)
        
        for g_key in g_keys:
            for img_path in groups[g_key]:
                # Copy image
                shutil.copy2(img_path, img_out / img_path.name)
                counts[split_name] += 1
                
                # Copy and analyze label
                label_path = labels_dir / img_path.with_suffix(".txt").name
                if label_path.exists():
                    shutil.copy2(label_path, lbl_out / label_path.name)
                    
                    with open(label_path, 'r') as f:
                        for line in f:
                            parts = line.strip().split()
                            if parts:
                                cls_id = parts[0]
                                class_dist[split_name][cls_id] += 1
                                
    total_images = sum(counts.values())
    
    report = f"""
=== Dataset Split Report ===
Random seed: {args.seed}
Total images: {total_images}
Total groups: {total_groups}

Training set: {counts['train']} images ({counts['train']/total_images*100:.1f}%)
Validation set: {counts['val']} images ({counts['val']/total_images*100:.1f}%)
Test set: {counts['test']} images ({counts['test']/total_images*100:.1f}%)

Class distribution per split:
Class      | Train | Val  | Test
"""
    
    all_classes = set()
    for s in class_dist.values():
        all_classes.update(s.keys())
        
    for cls in sorted(all_classes):
        tr = class_dist['train'].get(cls, 0)
        vl = class_dist['val'].get(cls, 0)
        te = class_dist['test'].get(cls, 0)
        report += f"{cls:<10} | {tr:<5} | {vl:<4} | {te:<4}\n"
        
    logger.info(report)
    
    with open(output_dir / "split_report.txt", "w") as f:
        f.write(report)

if __name__ == '__main__':
    main()
