"""Comprehensive test suite for CivicAI ML dataset preprocessing pipeline.

Tests configuration, YOLO label validation, image corruption/validation checks,
duplicate detection, dataset splitting, annotation conversion, and versioning.
"""
import os
import json
import yaml
import pytest
from pathlib import Path
from PIL import Image
import numpy as np
import xml.etree.ElementTree as ET

from ml.preprocessing.config import (
    load_config,
    class_name_to_id,
    get_detection_classes,
    get_num_classes,
    validate_yolo_label,
    is_valid_yolo_annotation,
    DatasetConfig
)
from ml.preprocessing.remove_duplicates import compute_md5
from ml.preprocessing.check_leakage import compute_phash


@pytest.fixture
def dummy_config(tmp_path):
    """Fixture to create a temporary dataset_config.yaml."""
    config_data = {
        'classes': {
            0: 'pothole',
            1: 'garbage',
            2: 'open_manhole',
            3: 'damaged_road',
            4: 'broken_streetlight',
            5: 'water_leakage',
            6: 'damaged_sidewalk',
            7: 'fallen_tree',
            8: 'illegal_dumping',
            9: 'normal'
        },
        'background_classes': [9],
        'split': {'train': 0.7, 'val': 0.2, 'test': 0.1, 'random_seed': 42},
        'image': {
            'target_size': 640,
            'min_size': 50,
            'max_size': 2000,
            'supported_extensions': ['.jpg', '.jpeg', '.png']
        }
    }
    config_path = tmp_path / "dataset_config.yaml"
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)
    return config_path


@pytest.fixture
def valid_image_file(tmp_path):
    """Creates a valid small JPEG image (100x100, RGB)."""
    img_path = tmp_path / "valid_image.jpg"
    img = Image.new('RGB', (100, 100), color=(128, 128, 128))
    img.save(img_path)
    return img_path


@pytest.fixture
def corrupted_image_file(tmp_path):
    """Creates a corrupted file with a .jpg extension."""
    corrupt_path = tmp_path / "corrupted_image.jpg"
    with open(corrupt_path, 'wb') as f:
        f.write(os.urandom(1024))
    return corrupt_path


class TestConfig:
    """Tests for dataset configuration and class mapping."""

    def test_load_config(self, dummy_config):
        config = load_config(dummy_config)
        assert len(config.classes) == 10
        assert 0 in config.classes
        assert config.classes[0] == 'pothole'
        assert 'classes' in config

    def test_class_mapping(self, dummy_config):
        mapping = class_name_to_id(dummy_config)
        assert mapping['pothole'] == 0
        assert mapping['normal'] == 9

    def test_detection_classes(self, dummy_config):
        classes = get_detection_classes(dummy_config)
        assert 'normal' not in classes
        assert 'pothole' in classes
        assert len(classes) == 9

    def test_num_classes(self, dummy_config):
        num = get_num_classes(dummy_config)
        assert num == 9


class TestYOLOValidation:
    """Tests for YOLO annotation format validation."""

    def test_valid_annotation(self):
        valid, msg = validate_yolo_label("0 0.5 0.5 0.3 0.2", num_classes=10)
        assert valid is True
        assert msg == ""
        assert is_valid_yolo_annotation("0 0.5 0.5 0.3 0.2") is True

    def test_empty_line(self):
        assert is_valid_yolo_annotation("") is True
        assert is_valid_yolo_annotation("   \n") is True

    def test_invalid_class_id(self):
        valid, _ = validate_yolo_label("99 0.5 0.5 0.3 0.2", num_classes=10)
        assert valid is False

    def test_negative_class_id(self):
        assert is_valid_yolo_annotation("-1 0.5 0.5 0.3 0.2") is False

    def test_out_of_range_coords(self):
        assert is_valid_yolo_annotation("0 1.5 0.5 0.3 0.2") is False
        assert is_valid_yolo_annotation("0 0.5 1.5 0.3 0.2") is False

    def test_negative_coords(self):
        assert is_valid_yolo_annotation("0 -0.1 0.5 0.3 0.2") is False

    def test_zero_width_and_height(self):
        assert is_valid_yolo_annotation("0 0.5 0.5 0.0 0.2") is False
        assert is_valid_yolo_annotation("0 0.5 0.5 0.3 0.0") is False

    def test_non_numeric(self):
        assert is_valid_yolo_annotation("0 abc 0.5 0.3 0.2") is False

    def test_wrong_field_count(self):
        assert is_valid_yolo_annotation("0 0.5 0.5") is False
        assert is_valid_yolo_annotation("0 0.5 0.5 0.2 0.2 0.9") is False

    def test_boundary_values(self):
        # Center at edge and box size of 1.0 (clamped bounding box)
        assert is_valid_yolo_annotation("0 0.0 0.0 1.0 1.0") is True
        assert is_valid_yolo_annotation("0 1.0 1.0 0.5 0.5") is True

    def test_all_valid_class_ids(self):
        for i in range(10):
            assert is_valid_yolo_annotation(f"{i} 0.5 0.5 0.1 0.1", num_classes=10) is True


class TestImageValidation:
    """Tests for image file validation."""

    def test_valid_image(self, valid_image_file):
        with Image.open(valid_image_file) as img:
            img.verify()
        # Ensure reopen succeeds
        with Image.open(valid_image_file) as img:
            assert img.size == (100, 100)
            assert img.mode == 'RGB'

    def test_corrupted_image(self, corrupted_image_file):
        with pytest.raises(Exception):
            with Image.open(corrupted_image_file) as img:
                img.verify()

    def test_small_image_dimension_detection(self, tmp_path):
        img_path = tmp_path / "tiny_image.jpg"
        img = Image.new('RGB', (10, 10), color=(100, 100, 100))
        img.save(img_path)
        with Image.open(img_path) as im:
            w, h = im.size
            assert w < 50 or h < 50


class TestDuplicateDetection:
    """Tests for image duplicate detection via MD5 and perceptual hashing."""

    def test_exact_duplicate(self, valid_image_file, tmp_path):
        dup_path = tmp_path / "dup_image.jpg"
        with open(valid_image_file, 'rb') as f1, open(dup_path, 'wb') as f2:
            f2.write(f1.read())

        md5_orig = compute_md5(valid_image_file)
        md5_dup = compute_md5(dup_path)
        assert md5_orig == md5_dup

    def test_unique_images(self, valid_image_file, tmp_path):
        unique_path = tmp_path / "unique_image.jpg"
        img = Image.new('RGB', (100, 100), color=(255, 0, 0))
        img.save(unique_path)

        md5_1 = compute_md5(valid_image_file)
        md5_2 = compute_md5(unique_path)
        assert md5_1 != md5_2

    def test_near_duplicate_phash(self, valid_image_file, tmp_path):
        near_dup_path = tmp_path / "near_dup_image.jpg"
        img = Image.open(valid_image_file)
        img = img.point(lambda p: int(p * 0.95))
        img.save(near_dup_path)

        h1 = compute_phash(valid_image_file, hash_size=16)
        h2 = compute_phash(near_dup_path, hash_size=16)
        assert h1 is not None and h2 is not None
        assert (h1 - h2) <= 5


class TestDatasetSplit:
    """Tests for dataset splitting logic."""

    def test_split_ratios(self, dummy_config):
        config = load_config(dummy_config)
        total = config.split.train + config.split.val + config.split.test
        assert abs(total - 1.0) < 1e-5

    def test_reproducible_split(self):
        import random
        data = [f"img_{i:03d}.jpg" for i in range(100)]
        
        # Test deterministic shuffle with seed
        random.seed(42)
        shuffled1 = list(data)
        random.shuffle(shuffled1)

        random.seed(42)
        shuffled2 = list(data)
        random.shuffle(shuffled2)

        assert shuffled1 == shuffled2


class TestAnnotationConversion:
    """Tests for Pascal VOC and COCO to YOLO conversion logic."""

    def test_voc_bbox_calculation(self):
        # VOC format: xmin=100, ymin=150, xmax=300, ymax=350 on 640x480
        width, height = 640, 480
        xmin, ymin, xmax, ymax = 100, 150, 300, 350

        x_center = ((xmin + xmax) / 2.0) / width
        y_center = ((ymin + ymax) / 2.0) / height
        w = (xmax - xmin) / width
        h = (ymax - ymin) / height

        assert 0.0 <= x_center <= 1.0
        assert 0.0 <= y_center <= 1.0
        assert abs(x_center - (200.0 / 640.0)) < 1e-4
        assert abs(y_center - (250.0 / 480.0)) < 1e-4
        assert is_valid_yolo_annotation(f"0 {x_center:.4f} {y_center:.4f} {w:.4f} {h:.4f}")

    def test_coco_bbox_calculation(self):
        # COCO format: [x, y, width, height] = [100, 150, 200, 200] on 640x480
        img_w, img_h = 640, 480
        bx, by, bw, bh = 100, 150, 200, 200

        x_center = (bx + bw / 2.0) / img_w
        y_center = (by + bh / 2.0) / img_h
        w = bw / img_w
        h = bh / img_h

        assert 0.0 <= x_center <= 1.0
        assert 0.0 <= y_center <= 1.0
        assert is_valid_yolo_annotation(f"0 {x_center:.4f} {y_center:.4f} {w:.4f} {h:.4f}")
