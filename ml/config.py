"""Convenience alias pointing to ml.preprocessing.config."""
from ml.preprocessing.config import (
    load_config,
    validate_yolo_label,
    DatasetConfig,
    ImageConfig,
    SplitConfig,
    DuplicateConfig,
    AugmentationConfig,
    DEFAULT_CONFIG_PATH,
)

def get_dataset_config(path=None):
    """Returns dataset config as a dict or DatasetConfig."""
    cfg = load_config(path)
    return {
        "classes": cfg.classes,
        "background_classes": cfg.background_classes,
        "image_size": {"min": cfg.image.min_size, "max": cfg.image.max_size},
        "target_size": cfg.image.target_size,
        "supported_formats": cfg.image.supported_extensions,
        "letterbox": cfg.image.letterbox,
        "letterbox_color": cfg.image.letterbox_color,
        "split_ratios": {"train": cfg.split.train, "val": cfg.split.val, "test": cfg.split.test},
        "random_seed": cfg.split.random_seed,
    }
