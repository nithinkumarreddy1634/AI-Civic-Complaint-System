"""Dataset configuration loader.

Provides a single source of truth for all dataset settings by loading
from dataset_config.yaml. All other scripts import from here.
"""
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "datasets" / "dataset_config.yaml"


@dataclass
class ImageConfig:
    target_size: int = 640
    min_size: int = 100
    max_size: int = 10000
    supported_extensions: list[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png"])
    letterbox: bool = True
    letterbox_color: list[int] = field(default_factory=lambda: [114, 114, 114])


@dataclass
class SplitConfig:
    train: float = 0.70
    val: float = 0.20
    test: float = 0.10
    random_seed: int = 42


@dataclass
class DuplicateConfig:
    hash_size: int = 16
    similarity_threshold: int = 5


@dataclass
class AugmentationConfig:
    enabled: bool = True
    per_image: int = 2
    horizontal_flip: float = 0.5
    vertical_flip: float = 0.0
    brightness_limit: float = 0.2
    contrast_limit: float = 0.2
    rotation_limit: int = 10
    scale_limit: float = 0.15
    blur_limit: int = 3
    noise_var_limit: int = 10
    perspective_limit: float = 0.05


@dataclass
class DatasetConfig:
    classes: dict[int, str] = field(default_factory=dict)
    background_classes: list[int] = field(default_factory=list)
    image: ImageConfig = field(default_factory=ImageConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    duplicates: DuplicateConfig = field(default_factory=DuplicateConfig)
    augmentation: AugmentationConfig = field(default_factory=AugmentationConfig)
    paths: dict[str, str] = field(default_factory=dict)
    sources: list[dict[str, Any]] = field(default_factory=list)

    @property
    def num_classes(self) -> int:
        """Number of detection classes (excluding background)."""
        return len(self.classes) - len(self.background_classes)

    @property
    def detection_classes(self) -> dict[int, str]:
        """Classes that have bounding boxes (excluding background)."""
        return {k: v for k, v in self.classes.items() if k not in self.background_classes}

    @property
    def class_name_to_id(self) -> dict[str, int]:
        """Reverse mapping: class name -> class ID."""
        return {v: k for k, v in self.classes.items()}

    def get_path(self, key: str, base_dir: Path | None = None) -> Path:
        """Get a resolved path from the paths config."""
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        return base_dir / self.paths.get(key, key)

    def __contains__(self, item: str) -> bool:
        return hasattr(self, item) or item in ["split_ratios", "supported_formats"]

    def __getitem__(self, item: str) -> Any:
        if item == "split_ratios":
            return {"train": self.split.train, "val": self.split.val, "test": self.split.test}
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)


def load_config(config_path: Path | str | None = None) -> DatasetConfig:
    """Load dataset configuration from YAML file."""
    if config_path is None:
        config_path = DEFAULT_CONFIG_PATH
    config_path = Path(config_path)

    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}. Using defaults.")
        return DatasetConfig()

    with open(config_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    split_data = raw.get("split", {})
    if "split_ratios" in raw and not split_data:
        split_data = raw.get("split_ratios", {})

    cfg = DatasetConfig(
        classes={int(k): v for k, v in raw.get("classes", {}).items()},
        background_classes=raw.get("background_classes", []),
        image=ImageConfig(**raw.get("image", {})),
        split=SplitConfig(**split_data),
        duplicates=DuplicateConfig(**raw.get("duplicates", {})),
        augmentation=AugmentationConfig(**raw.get("augmentation", {})),
        paths=raw.get("paths", {}),
        sources=raw.get("sources", []),
    )
    return cfg


def class_name_to_id(config: DatasetConfig | Path | str | None = None) -> dict[str, int]:
    """Helper returning class name to id dict."""
    if not isinstance(config, DatasetConfig):
        config = load_config(config)
    return config.class_name_to_id


def get_detection_classes(config: DatasetConfig | Path | str | None = None) -> list[str]:
    """Helper returning list of detection class names (excluding background)."""
    if not isinstance(config, DatasetConfig):
        config = load_config(config)
    return list(config.detection_classes.values())


def get_num_classes(config: DatasetConfig | Path | str | None = None) -> int:
    """Helper returning count of detection classes."""
    if not isinstance(config, DatasetConfig):
        config = load_config(config)
    return config.num_classes


def validate_yolo_label(line: str, num_classes: int = 10) -> tuple[bool, str]:
    """Validate a single YOLO annotation line.
    
    Expected format: class_id x_center y_center width height
    Coordinates normalized to [0, 1].
    """
    line = line.strip()
    if not line:
        return True, ""

    parts = line.split()
    if len(parts) != 5:
        return False, f"Expected 5 values, got {len(parts)}: '{line}'"

    try:
        class_id = int(parts[0])
        x_center = float(parts[1])
        y_center = float(parts[2])
        width = float(parts[3])
        height = float(parts[4])
    except ValueError:
        return False, f"Non-numeric values in: '{line}'"

    if class_id < 0 or class_id >= num_classes:
        return False, f"Invalid class ID {class_id} (valid: 0-{num_classes - 1})"

    for name, val in [("x_center", x_center), ("y_center", y_center),
                      ("width", width), ("height", height)]:
        if val < 0.0 or val > 1.0:
            return False, f"{name}={val} out of range [0, 1]"

    if width <= 0:
        return False, f"width must be > 0, got {width}"
    if height <= 0:
        return False, f"height must be > 0, got {height}"

    return True, ""


def is_valid_yolo_annotation(line: str, num_classes: int = 10) -> bool:
    """Boolean helper for YOLO annotation validation."""
    valid, _ = validate_yolo_label(line, num_classes=num_classes)
    return valid
