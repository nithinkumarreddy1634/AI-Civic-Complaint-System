from abc import ABC, abstractmethod
from pydantic import BaseModel

class DetectionResult(BaseModel):
    detected_class: str
    confidence: float
    bounding_box: list[float]

class BaseDetector(ABC):
    """
    Abstract interface for object detection in civic issue images.
    """
    @abstractmethod
    async def detect(self, image_path: str) -> DetectionResult:
        pass

class YOLODetector(BaseDetector):
    """
    YOLO based object detector for civic issues.
    Will use ultralytics YOLO, load model from model_path, run inference,
    return detected class, confidence, and bounding box.
    """
    def __init__(self, model_path: str, confidence_threshold: float):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold

    async def detect(self, image_path: str) -> DetectionResult:
        raise NotImplementedError("YOLO detection will be implemented in Phase 3 after model training.")
