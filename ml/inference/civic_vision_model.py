"""Clean Python service interface for Phase 4 backend integration.

Wraps model loading, pre-inference image quality audit, YOLO inference,
and structured prediction formatting for the FastAPI application.
"""
from pathlib import Path
from typing import Dict, Any, List, Union
import io
import time
import cv2
import numpy as np
from PIL import Image

from ml.inference.image_quality import assess_image_quality


class CivicVisionModel:
    """Service wrapper for CivicAI Computer Vision inference."""

    def __init__(
        self,
        model_path: Union[Path, str, None] = None,
        conf_threshold: float = 0.40,
        iou_threshold: float = 0.50,
        device: str = "auto"
    ):
        if model_path is None:
            # Default to production model or fallback to pretrained
            trained_p = Path(__file__).parent.parent / "models" / "trained" / "civic_yolo_best.pt"
            if trained_p.exists():
                model_path = trained_p
            else:
                model_path = Path(__file__).parent.parent / "models" / "pretrained" / "yolov8n.pt"
                if not model_path.exists():
                    model_path = "yolov8n.pt"

        self.model_path = str(model_path)
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self._model = None

    def load_model(self):
        """Loads and initializes the Ultralytics YOLO model."""
        if self._model is None:
            from ultralytics import YOLO
            self._model = YOLO(self.model_path)
        return self._model

    def _convert_input_to_bgr(self, image_input: Union[Path, str, bytes, np.ndarray]) -> np.ndarray:
        """Converts diverse image input types (path, raw bytes, numpy array) into BGR array."""
        if isinstance(image_input, np.ndarray):
            return image_input
        elif isinstance(image_input, (str, Path)):
            img = cv2.imread(str(image_input))
            if img is None:
                raise ValueError(f"Could not decode image from path: {image_input}")
            return img
        elif isinstance(image_input, (bytes, bytearray)):
            nparr = np.frombuffer(image_input, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                raise ValueError("Could not decode image from byte buffer.")
            return img
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def validate_image(self, image_input: Union[Path, str, bytes, np.ndarray]) -> Dict[str, Any]:
        """Runs image quality and corruption inspection."""
        try:
            img_bgr = self._convert_input_to_bgr(image_input)
            return assess_image_quality(img_bgr)
        except Exception as e:
            return {
                "valid": False,
                "quality_score": 0,
                "issues": [str(e)],
                "metrics": {}
            }

    def predict(self, image_input: Union[Path, str, bytes, np.ndarray]) -> Dict[str, Any]:
        """Main inference method returning complete structured diagnosis."""
        # 1. Quality check
        quality = self.validate_image(image_input)
        if not quality["valid"]:
            return {
                "image_valid": False,
                "quality_score": quality["quality_score"],
                "issues": quality["issues"],
                "detections": [],
                "inference_time_ms": 0.0
            }

        img_bgr = self._convert_input_to_bgr(image_input)
        model = self.load_model()

        # 2. Run prediction
        t0 = time.perf_counter()
        results = model.predict(
            source=img_bgr,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device if self.device != "auto" else "",
            verbose=False
        )
        inference_time_ms = (time.perf_counter() - t0) * 1000.0

        detections: List[Dict[str, Any]] = []
        if len(results) > 0:
            res = results[0]
            boxes = res.boxes
            class_names = res.names

            for i in range(len(boxes)):
                cls_id = int(boxes.cls[i].item())
                cls_name = class_names.get(cls_id, f"class_{cls_id}")
                conf = float(boxes.conf[i].item())
                xyxy = boxes.xyxy[i].tolist()

                detections.append({
                    "class_id": cls_id,
                    "class_name": cls_name,
                    "confidence": round(conf, 4),
                    "bbox": {
                        "x1": round(float(xyxy[0]), 1),
                        "y1": round(float(xyxy[1]), 1),
                        "x2": round(float(xyxy[2]), 1),
                        "y2": round(float(xyxy[3]), 1),
                    }
                })

        return {
            "image_valid": True,
            "quality_score": quality["quality_score"],
            "issues": quality["issues"],
            "detection_count": len(detections),
            "detections": detections,
            "inference_time_ms": round(inference_time_ms, 2)
        }

    def get_detections(self, image_input: Union[Path, str, bytes, np.ndarray]) -> List[Dict[str, Any]]:
        """Convenience helper returning just detection items."""
        result = self.predict(image_input)
        return result.get("detections", [])
