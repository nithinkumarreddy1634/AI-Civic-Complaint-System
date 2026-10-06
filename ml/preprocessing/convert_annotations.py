"""
Annotation format converter for the dataset pipeline.
Converts Pascal VOC (XML) and COCO (JSON) formats to YOLO (TXT) format.
Can also validate and remap existing YOLO labels.
"""

import argparse
import json
import logging
from pathlib import Path
import xml.etree.ElementTree as ET

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs): return iterable

try:
    from ml.config import get_dataset_config
except ImportError:
    def get_dataset_config(path=None): return {}

def setup_logger() -> logging.Logger:
    logger = logging.getLogger("convert_annotations")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())
    return logger

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert dataset annotations to YOLO format.")
    parser.add_argument("--input-dir", type=str, required=True, help="Input annotations directory.")
    parser.add_argument("--output-dir", type=str, required=True, help="Output YOLO labels directory.")
    parser.add_argument("--format", type=str, choices=["pascal_voc", "coco_json", "yolo"], required=True, help="Input format.")
    parser.add_argument("--class-mapping", type=str, help="JSON file or inline dict mapping class names to IDs.")
    parser.add_argument("--config", type=str, help="Path to dataset config.")
    return parser.parse_args()

def validate_yolo_label(class_id: int, x: float, y: float, w: float, h: float) -> bool:
    """Validate YOLO coordinate ranges."""
    if not isinstance(class_id, int): return False
    return all(0.0 <= val <= 1.0 for val in [x, y, w, h])

def parse_class_mapping(mapping_str: str | None, config_dict: dict) -> dict:
    if mapping_str:
        try:
            if Path(mapping_str).exists():
                with open(mapping_str, 'r') as f:
                    return json.load(f)
            return json.loads(mapping_str)
        except Exception:
            pass
    return config_dict.get("class_mapping", {})

def convert_pascal_voc(input_dir: Path, output_dir: Path, mapping: dict, logger: logging.Logger):
    success, skipped, errors = 0, 0, 0
    
    for xml_file in tqdm(list(input_dir.glob("*.xml")), desc="Converting VOC XML"):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            size = root.find("size")
            if size is None:
                logger.warning(f"No size in {xml_file.name}")
                errors += 1
                continue
                
            width = float(size.find("width").text)
            height = float(size.find("height").text)
            
            yolo_annotations = []
            for obj in root.findall("object"):
                name = obj.find("name").text
                if name not in mapping:
                    logger.warning(f"Skipping unknown class '{name}' in {xml_file.name}")
                    skipped += 1
                    continue
                    
                cls_id = mapping[name]
                bndbox = obj.find("bndbox")
                xmin = float(bndbox.find("xmin").text)
                ymin = float(bndbox.find("ymin").text)
                xmax = float(bndbox.find("xmax").text)
                ymax = float(bndbox.find("ymax").text)
                
                x_center = ((xmin + xmax) / 2) / width
                y_center = ((ymin + ymax) / 2) / height
                w = (xmax - xmin) / width
                h = (ymax - ymin) / height
                
                if validate_yolo_label(cls_id, x_center, y_center, w, h):
                    yolo_annotations.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
                else:
                    logger.error(f"Invalid YOLO coordinates derived in {xml_file.name}")
                    errors += 1
                    
            if yolo_annotations:
                out_path = output_dir / f"{xml_file.stem}.txt"
                with open(out_path, 'w') as f:
                    f.write("\n".join(yolo_annotations) + "\n")
                success += 1
                
        except Exception as e:
            logger.error(f"Error processing {xml_file.name}: {e}")
            errors += 1
            
    return success, skipped, errors

def convert_coco_json(input_dir: Path, output_dir: Path, mapping: dict, logger: logging.Logger):
    success, skipped, errors = 0, 0, 0
    
    for json_file in tqdm(list(input_dir.glob("*.json")), desc="Converting COCO JSON"):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                
            categories = {cat['id']: cat['name'] for cat in data.get('categories', [])}
            images = {img['id']: img for img in data.get('images', [])}
            annotations_by_img = {}
            
            for ann in data.get('annotations', []):
                img_id = ann['image_id']
                if img_id not in annotations_by_img:
                    annotations_by_img[img_id] = []
                annotations_by_img[img_id].append(ann)
                
            for img_id, anns in annotations_by_img.items():
                img = images.get(img_id)
                if not img:
                    errors += 1
                    continue
                    
                img_width = img['width']
                img_height = img['height']
                img_name = Path(img['file_name']).stem
                
                yolo_annotations = []
                for ann in anns:
                    cat_name = categories.get(ann['category_id'])
                    if cat_name not in mapping:
                        logger.warning(f"Skipping unknown class '{cat_name}'")
                        skipped += 1
                        continue
                        
                    cls_id = mapping[cat_name]
                    x, y, width, height = ann['bbox']
                    
                    x_center = (x + width / 2) / img_width
                    y_center = (y + height / 2) / img_height
                    w = width / img_width
                    h = height / img_height
                    
                    if validate_yolo_label(cls_id, x_center, y_center, w, h):
                        yolo_annotations.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")
                    else:
                        errors += 1
                        
                if yolo_annotations:
                    out_path = output_dir / f"{img_name}.txt"
                    with open(out_path, 'w') as f:
                        f.write("\n".join(yolo_annotations) + "\n")
                    success += 1
                    
        except Exception as e:
            logger.error(f"Error processing {json_file.name}: {e}")
            errors += 1
            
    return success, skipped, errors

def main():
    args = parse_args()
    logger = setup_logger()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    config = get_dataset_config(args.config)
    class_mapping = parse_class_mapping(args.class_mapping, config)
    
    logger.info(f"Starting conversion from {args.format}")
    
    if args.format == "pascal_voc":
        success, skipped, errors = convert_pascal_voc(input_dir, output_dir, class_mapping, logger)
    elif args.format == "coco_json":
        success, skipped, errors = convert_coco_json(input_dir, output_dir, class_mapping, logger)
    else:
        logger.error("YOLO to YOLO validation not fully implemented in this stub.")
        success, skipped, errors = 0, 0, 0
        
    logger.info(f"Conversion complete. Success: {success}, Skipped annotations: {skipped}, Errors: {errors}")

if __name__ == '__main__':
    main()
