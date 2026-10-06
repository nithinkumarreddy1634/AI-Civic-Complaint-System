# CivicAI — Machine Learning Subsystem

## Overview
This subsystem provides the complete dataset preprocessing, training, validation, evaluation, and inference pipeline for the **AI-Powered Civic Infrastructure Complaint Verification and Prioritization System Using Computer Vision**.

---

## Architecture & Directory Structure
```
ml/
├── datasets/
│   ├── raw/                          # Raw uploaded/collected images & labels
│   ├── processed/                    # Validated, deduplicated, resized data
│   │   └── visualizations/           # Per-class overlay samples & montage
│   ├── quarantine/                   # Corrupt or invalid images moved here
│   ├── train/                        # 70% Training split (images/ + labels/)
│   ├── val/                          # 20% Validation split (images/ + labels/)
│   ├── test/                         # 10% Test split (images/ + labels/)
│   ├── versions/                     # Dataset version metadata (.json)
│   ├── classes.txt                   # Class list (0: pothole .. 9: normal)
│   ├── data.yaml                     # Ultralytics YOLO dataset configuration
│   └── dataset_config.yaml           # Master configuration (Single Source of Truth)
│
├── models/
│   ├── pretrained/                   # Base model weight cache (e.g. yolov8n.pt)
│   ├── trained/                      # Production model weights (.pt, .onnx)
│   ├── export.py                     # ONNX model export script
│   └── model_metadata.json           # Model registry and metadata specification
│
├── training/
│   ├── config.yaml                   # Training hyperparameters and device settings
│   ├── train.py                      # Training runner with experiment management
│   ├── validate.py                   # Validation runner on val split
│   └── evaluate.py                   # Strict benchmark runner on unseen test split
│
├── inference/
│   ├── image_quality.py              # Pre-inference quality audit (blur, darkness)
│   ├── predict.py                    # Single image prediction CLI & JSON output
│   ├── batch_predict.py              # Directory prediction with CSV/JSON summaries
│   ├── visualize_prediction.py       # Bounding box & label visualization overlay
│   └── civic_vision_model.py         # Python service interface for Phase 4 backend
│
├── evaluation/
│   ├── metrics.py                    # Precision, Recall, mAP50, mAP50-95, F1
│   ├── confusion_matrix.py           # Confusion matrix generation & interpretation
│   ├── precision_recall.py           # Confidence threshold sensitivity analysis
│   └── error_analysis.py             # False positive/negative failure mode categorization
│
├── outputs/
│   ├── training/                     # Unique experiment runs (experiment_001, ...)
│   ├── predictions/                  # Output visualizations and batch CSV reports
│   └── evaluation/                   # Plots, confusion matrices & error reports
│
├── tests/
│   ├── test_preprocessing.py         # 25 unit tests for dataset preprocessing
│   └── test_model_pipeline.py        # Automated tests for model training/inference
│
└── requirements.txt                  # Python dependencies
```

---

## Quick Start & Installation

```powershell
# Activate environment
cd backend
.\venv\Scripts\activate
cd ..

# Install ML requirements
pip install -r ml/requirements.txt
```

---

## Training Pipeline

### 1. Pre-flight Verification & Training
```powershell
# Runs pre-flight dataset check and trains YOLOv8n
python -m ml.training.train --config ml/training/config.yaml

# Command line overrides (optional)
python -m ml.training.train --epochs 30 --batch 16 --device auto
```
* The training script automatically detects CUDA GPU acceleration or defaults to CPU.
* Each run creates an isolated non-destructive experiment folder (e.g. `ml/outputs/training/experiment_001/`).
* Logs complete hyperparameter lineage to `experiment_metadata.json`.
* Copies the top-performing checkpoint to `ml/models/trained/civic_yolo_best.pt`.

### 2. Validation on Validation Split
```powershell
python -m ml.training.validate --model ml/models/trained/civic_yolo_best.pt
```

### 3. Evaluation on Unseen Test Split
```powershell
python -m ml.training.evaluate --model ml/models/trained/civic_yolo_best.pt
```
Outputs latency (ms/image), throughput (FPS), and generalization accuracy without hyperparameter leakage.

---

## Inference & Prediction

### Single Image Prediction (CLI)
```powershell
python -m ml.inference.predict --source path/to/complaint.jpg --conf 0.40 --save-vis
```
Returns structured JSON:
```json
{
  "image_path": "path/to/complaint.jpg",
  "status": "success",
  "quality": { "valid": true, "quality_score": 88 },
  "detection_count": 1,
  "detections": [
    {
      "class_id": 0,
      "class_name": "pothole",
      "confidence": 0.9124,
      "bbox": [120.5, 80.2, 450.0, 310.8]
    }
  ],
  "inference_time_ms": 38.4
}
```

### Batch Directory Prediction
```powershell
python -m ml.inference.batch_predict --source-dir ml/datasets/test/images --conf 0.40
```
Generates `predictions_summary.csv` and `predictions_summary.json` inside `ml/outputs/predictions/`.

---

## Phase 4 Backend Integration Interface

Phase 4 (AI Verification and FastAPI integration) connects directly via `CivicVisionModel`:
```python
from ml.inference.civic_vision_model import CivicVisionModel

# Initialize service
detector = CivicVisionModel(model_path="ml/models/trained/civic_yolo_best.pt", conf_threshold=0.40)

# Pass image file path, raw bytes, or numpy array
result = detector.predict("uploads/complaint_123.jpg")

if result["image_valid"]:
    for det in result["detections"]:
        print(f"Detected {det['class_name']} with {det['confidence']*100:.1f}% confidence")
else:
    print(f"Rejected image: {result['issues']}")
```

---

## Evaluation & Diagnostic Tools

```powershell
# 1. Confusion Matrix Analysis
python -m ml.evaluation.confusion_matrix

# 2. Confidence Threshold Sensitivity (P-R Tradeoff)
python -m ml.evaluation.precision_recall

# 3. Failure Mode & Difficult Cases Diagnosis
python -m ml.evaluation.error_analysis --predictions ml/outputs/predictions/predictions_summary.json
```

---

## Model Export (ONNX)

```powershell
python -m ml.models.export --model ml/models/trained/civic_yolo_best.pt --imgsz 640
```

---

## Automated Unit Testing

```powershell
# Run all Phase 2 and Phase 3 tests
python -m pytest ml/tests -v
```
