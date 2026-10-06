"""
Image resizing script for the dataset pipeline.
Resizes images using standard resizing or letterboxing (padding).
Adjusts YOLO bounding box labels to match the new image dimensions.
"""

import argparse
import logging
from pathlib import Path
import numpy as np
import cv2

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs): return iterable

try:
    from ml.config import get_dataset_config
except ImportError:
    def get_dataset_config(path=None):
        return {"target_size": 640, "letterbox": True, "letterbox_color": [114, 114, 114]}

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("resize_images")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Resize images and adjust YOLO annotations.")
    parser.add_argument("--input-dir", type=str, required=True, help="Input images dir.")
    parser.add_argument("--output-dir", type=str, required=True, help="Output images dir.")
    parser.add_argument("--labels-dir", type=str, required=True, help="Output labels dir.")
    parser.add_argument("--config", type=str, help="Dataset config path.")
    parser.add_argument("--size", type=int, help="Target size (overrides config).")
    return parser.parse_args()

def letterbox(im, new_shape=(640, 640), color=(114, 114, 114)):
    """Resize and pad image while meeting stride-multiple constraints."""
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
    
    return im, r, (dw, dh)

def adjust_bbox(bbox, ratio, pad_w, pad_h, img_w, img_h, new_size):
    """Adjust YOLO normalized bbox after letterboxing."""
    class_id, x, y, w, h = bbox
    
    # Unnormalize based on old size
    abs_x = x * img_w
    abs_y = y * img_h
    abs_w = w * img_w
    abs_h = h * img_h
    
    # Scale and pad
    new_abs_x = abs_x * ratio + pad_w
    new_abs_y = abs_y * ratio + pad_h
    new_abs_w = abs_w * ratio
    new_abs_h = abs_h * ratio
    
    # Renormalize based on new size
    new_x = max(0.0, min(1.0, new_abs_x / new_size))
    new_y = max(0.0, min(1.0, new_abs_y / new_size))
    new_w = max(0.0, min(1.0, new_abs_w / new_size))
    new_h = max(0.0, min(1.0, new_abs_h / new_size))
    
    return [class_id, new_x, new_y, new_w, new_h]

def main():
    args = parse_args()
    logger = setup_logger()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    labels_dir = Path(args.labels_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    labels_dir.mkdir(parents=True, exist_ok=True)
    
    config = get_dataset_config(args.config)
    target_size = args.size if args.size else config.get("target_size", 640)
    use_letterbox = config.get("letterbox", True)
    letterbox_color = config.get("letterbox_color", [114, 114, 114])
    
    images = list(input_dir.rglob("*.jpg")) + list(input_dir.rglob("*.png")) + list(input_dir.rglob("*.jpeg"))
    
    processed = 0
    errors = 0
    
    for img_path in tqdm(images, desc="Resizing images"):
        try:
            im = cv2.imread(str(img_path))
            if im is None:
                errors += 1
                continue
                
            orig_h, orig_w = im.shape[:2]
            
            if use_letterbox:
                im_resized, ratio, (pad_w, pad_h) = letterbox(im, target_size, letterbox_color)
            else:
                im_resized = cv2.resize(im, (target_size, target_size))
                ratio = target_size / max(orig_w, orig_h) # approximate
                pad_w, pad_h = 0, 0
                
            cv2.imwrite(str(output_dir / img_path.name), im_resized)
            
            # Find and process label
            label_path = input_dir.parent / "labels" / img_path.with_suffix(".txt").name
            if not label_path.exists():
                label_path = img_path.with_suffix(".txt")
                
            if label_path.exists():
                new_bboxes = []
                with open(label_path, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) >= 5:
                            cls_id = int(parts[0])
                            coords = [float(x) for x in parts[1:5]]
                            
                            if use_letterbox:
                                new_box = adjust_bbox([cls_id] + coords, ratio, pad_w, pad_h, orig_w, orig_h, target_size)
                            else:
                                new_box = [cls_id] + coords # No aspect ratio correction for raw resize (will distort)
                                
                            new_bboxes.append(new_box)
                            
                with open(labels_dir / label_path.name, 'w') as f:
                    for box in new_bboxes:
                        f.write(f"{int(box[0])} {box[1]:.6f} {box[2]:.6f} {box[3]:.6f} {box[4]:.6f}\n")
                        
            processed += 1
            
        except Exception as e:
            logger.error(f"Error processing {img_path.name}: {e}")
            errors += 1
            
    logger.info(f"=== Resize Summary ===")
    logger.info(f"Total processed: {processed}")
    logger.info(f"Errors: {errors}")
    logger.info(f"Output size: {target_size}x{target_size}")

if __name__ == '__main__':
    main()
