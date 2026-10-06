"""
Image validation script for the ML dataset pipeline.
Validates images for corruption, correct dimensions, format, duplicate filenames,
and missing labels. Quarantines invalid files.
"""

import argparse
import logging
import shutil
from pathlib import Path
from collections import Counter
from PIL import Image

try:
    from ml.config import get_dataset_config
except ImportError:
    # Fallback/stub if config is not available yet
    def get_dataset_config(config_path: Path | str | None = None) -> dict:
        return {
            "image_size": {"min": 10, "max": 4096},
            "supported_formats": [".jpg", ".jpeg", ".png"]
        }

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("validate_images")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate dataset images.")
    parser.add_argument("--input-dir", type=str, required=True, help="Directory containing input images.")
    parser.add_argument("--quarantine-dir", type=str, required=True, help="Directory to move invalid images.")
    parser.add_argument("--config", type=str, default=None, help="Path to dataset_config.yaml")
    return parser.parse_args()

def find_label_file(image_path: Path) -> Path | None:
    """Check for corresponding label file in same dir or siblings/labels."""
    # Check same directory
    same_dir_label = image_path.with_suffix('.txt')
    if same_dir_label.exists():
        return same_dir_label
    
    # Check sibling labels directory
    sibling_label = image_path.parent.parent / "labels" / image_path.name
    sibling_label = sibling_label.with_suffix('.txt')
    if sibling_label.exists():
        return sibling_label
        
    return None

def main():
    args = parse_args()
    logger = setup_logger()
    
    input_dir = Path(args.input_dir)
    quarantine_dir = Path(args.quarantine_dir)
    quarantine_dir.mkdir(parents=True, exist_ok=True)
    
    config = get_dataset_config(args.config)
    supported_formats = [ext.lower() for ext in config.get("supported_formats", [".jpg", ".jpeg", ".png"])]
    min_size = config.get("image_size", {}).get("min", 10)
    max_size = config.get("image_size", {}).get("max", 8192)
    
    stats = Counter({
        "total": 0,
        "valid": 0,
        "corrupted": 0,
        "invalid_dimensions": 0,
        "unsupported_format": 0,
        "duplicate_filenames": 0,
        "missing_labels": 0,
        "valid_labels": 0,
        "grayscale_warnings": 0,
        "quarantined": 0
    })
    
    seen_filenames = set()
    
    logger.info(f"Scanning directory: {input_dir}")
    
    for file_path in input_dir.rglob("*"):
        if not file_path.is_file():
            continue
            
        ext = file_path.suffix.lower()
        if ext not in supported_formats:
            continue
            
        stats["total"] += 1
        filename = file_path.name
        
        # Check duplicate filename
        if filename in seen_filenames:
            stats["duplicate_filenames"] += 1
            shutil.move(str(file_path), str(quarantine_dir / f"dup_{filename}"))
            stats["quarantined"] += 1
            continue
        seen_filenames.add(filename)
        
        is_valid = True
        
        # Check corruption and image properties
        try:
            with Image.open(file_path) as img:
                img.verify()
                
            # Need to reopen to check mode and size after verify
            with Image.open(file_path) as img:
                width, height = img.size
                if width < min_size or height < min_size or width > max_size or height > max_size:
                    stats["invalid_dimensions"] += 1
                    is_valid = False
                    
                if img.mode != "RGB":
                    stats["grayscale_warnings"] += 1
                    logger.warning(f"Image {filename} is not RGB (mode: {img.mode})")
        except Exception as e:
            logger.error(f"Image {filename} is corrupted: {e}")
            stats["corrupted"] += 1
            is_valid = False
            
        if not is_valid:
            shutil.move(str(file_path), str(quarantine_dir / filename))
            stats["quarantined"] += 1
            continue
            
        # Check for labels
        label_file = find_label_file(file_path)
        if label_file:
            stats["valid_labels"] += 1
            stats["valid"] += 1
        else:
            stats["missing_labels"] += 1
            shutil.move(str(file_path), str(quarantine_dir / filename))
            stats["quarantined"] += 1
            
    report = f'''
=== Image Validation Report ===
Total files scanned: {stats['total']}
Valid images: {stats['valid']}
Corrupted images: {stats['corrupted']}
Invalid dimensions: {stats['invalid_dimensions']}
Unsupported format: {stats['unsupported_format']}
Duplicate filenames: {stats['duplicate_filenames']}
Missing labels: {stats['missing_labels']}
Valid labels: {stats['valid_labels']}  
Grayscale warnings: {stats['grayscale_warnings']}
Quarantined files: {stats['quarantined']}
'''
    logger.info(report)
    
    report_file = quarantine_dir / "validation_report.txt"
    with open(report_file, "w") as f:
        f.write(report)
        
    logger.info(f"Report saved to {report_file}")

if __name__ == '__main__':
    main()
