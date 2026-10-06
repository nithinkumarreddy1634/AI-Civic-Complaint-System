"""
Duplicate image detection script.
Finds exact duplicates using MD5 and near-duplicates using perceptual hashes.
Moves duplicates to a quarantine directory.
"""

import argparse
import hashlib
import logging
import shutil
from pathlib import Path
from collections import defaultdict

try:
    from tqdm import tqdm
except ImportError:
    # Fallback to simple generator if tqdm is missing
    def tqdm(iterable, *args, **kwargs): return iterable

try:
    from PIL import Image
    import imagehash
except ImportError:
    imagehash = None

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("remove_duplicates")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Remove duplicate images.")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing images.")
    parser.add_argument("--quarantine-dir", type=str, required=True, help="Directory for duplicates.")
    parser.add_argument("--config", type=str, default=None, help="Path to config")
    parser.add_argument("--method", type=str, choices=["md5", "phash", "both"], default="both", help="Deduplication method")
    parser.add_argument("--dry-run", action="store_true", help="Report duplicates without moving them")
    return parser.parse_args()

def compute_md5(file_path: Path) -> str:
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_phash(file_path: Path) -> str | None:
    if imagehash is None:
        return None
    try:
        with Image.open(file_path) as img:
            return str(imagehash.phash(img))
    except Exception:
        return None

def main():
    args = parse_args()
    logger = setup_logger()
    
    input_dir = Path(args.input_dir)
    quarantine_dir = Path(args.quarantine_dir)
    if not args.dry_run:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        
    image_files = list(input_dir.rglob("*.jpg")) + list(input_dir.rglob("*.jpeg")) + list(input_dir.rglob("*.png"))
    
    hash_groups = defaultdict(list)
    exact_duplicates = 0
    near_duplicates = 0
    
    logger.info(f"Scanning {len(image_files)} images using method: {args.method}")
    
    for img_path in tqdm(image_files, desc="Hashing images"):
        file_hash = ""
        if args.method in ["md5", "both"]:
            file_hash += compute_md5(img_path) + "_"
        if args.method in ["phash", "both"]:
            ph = compute_phash(img_path)
            if ph:
                file_hash += ph
                
        hash_groups[file_hash].append(img_path)

    duplicate_groups = []
    
    for f_hash, paths in hash_groups.items():
        if len(paths) > 1:
            # Sort to keep the first alphabetically
            paths.sort(key=lambda p: p.name)
            keep = paths[0]
            dupes = paths[1:]
            
            group_report = {"keep": keep.name, "duplicates": [d.name for d in dupes]}
            duplicate_groups.append(group_report)
            
            # Simple heuristic to classify duplicate type for report
            if args.method == "both":
                exact_duplicates += len(dupes) # Simplify: treating all as exact in this pass
            elif args.method == "md5":
                exact_duplicates += len(dupes)
            else:
                near_duplicates += len(dupes)
                
            if not args.dry_run:
                for dupe in dupes:
                    try:
                        shutil.move(str(dupe), str(quarantine_dir / dupe.name))
                    except Exception as e:
                        logger.error(f"Failed to move {dupe.name}: {e}")

    unique_count = len(image_files) - exact_duplicates - near_duplicates
    
    report_lines = [
        "=== Duplicate Detection Report ===",
        f"Method: {args.method}",
        f"Total images scanned: {len(image_files)}",
        f"Exact duplicates found: {exact_duplicates}",
        f"Near-duplicates found: {near_duplicates}",
        f"Unique images: {unique_count}",
        "\nDuplicate Groups:"
    ]
    
    for i, group in enumerate(duplicate_groups, 1):
        report_lines.append(f"Group {i}:")
        report_lines.append(f"  - KEEP: {group['keep']}")
        for d in group['duplicates']:
            report_lines.append(f"  - DUPLICATE: {d}")
            
    report_text = "\n".join(report_lines)
    logger.info(report_text)
    
    if not args.dry_run:
        with open(quarantine_dir / "duplicate_report.txt", "w") as f:
            f.write(report_text)

if __name__ == '__main__':
    main()
