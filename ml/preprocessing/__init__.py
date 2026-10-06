"""CivicAI Dataset Preprocessing Pipeline.

This package provides tools for preparing a YOLO-format dataset
for civic infrastructure complaint detection.

Modules:
    config              - Configuration loading and class mapping
    validate_images     - Image validation and quarantine
    remove_duplicates   - Hash-based duplicate detection
    resize_images       - Aspect-ratio-preserving image resizing
    convert_annotations - VOC/COCO to YOLO annotation conversion
    split_dataset       - Reproducible train/val/test splitting
    dataset_statistics  - Class distribution and quality reporting
    augment_dataset     - Albumentations-based data augmentation
    check_leakage       - Cross-split data leakage detection
    visualize_samples   - Bounding box visualization on images
    dataset_version     - Dataset versioning and metadata
    run_pipeline        - Master pipeline orchestrator
"""
