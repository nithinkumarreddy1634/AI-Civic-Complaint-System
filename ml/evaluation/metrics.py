"""Evaluation metrics calculation module for object detection.

Computes Precision, Recall, F1 score, IoU, and mean Average Precision.
"""
from typing import List, Dict, Any, Tuple
import numpy as np


def compute_iou(box1: List[float], box2: List[float]) -> float:
    """Computes Intersection over Union (IoU) between two [x1, y1, x2, y2] boxes."""
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0.0, x2 - x1) * max(0.0, y2 - y1)
    area1 = max(0.0, box1[2] - box1[0]) * max(0.0, box1[3] - box1[1])
    area2 = max(0.0, box2[2] - box2[0]) * max(0.0, box2[3] - box2[1])
    union = area1 + area2 - intersection

    if union <= 0:
        return 0.0
    return intersection / union


def calculate_f1_score(precision: float, recall: float) -> float:
    """Computes harmonic mean F1 score."""
    if precision + recall <= 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


def summarize_metrics(metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Formats raw validation/test metrics into a clean summary table."""
    p = metrics_dict.get("precision", 0.0)
    r = metrics_dict.get("recall", 0.0)
    map50 = metrics_dict.get("map50", 0.0)
    map50_95 = metrics_dict.get("map50_95", 0.0)
    f1 = calculate_f1_score(p, r)

    return {
        "precision": round(p, 4),
        "recall": round(r, 4),
        "f1_score": round(f1, 4),
        "map50": round(map50, 4),
        "map50_95": round(map50_95, 4)
    }
