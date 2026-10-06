"""
AI Model Evaluation Script — Phase 10.

Evaluates the YOLO model on the held-out test split using Ultralytics val().

Usage:
    python ml/evaluation/evaluate_model.py

Outputs:
    ml/reports/model_metrics.json
    ml/reports/per_class_metrics.json
    ml/reports/evaluation_summary.md
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Project root
ROOT = Path(__file__).resolve().parent.parent.parent
ML_ROOT = ROOT / "ml"
REPORTS_DIR = ML_ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = ML_ROOT / "models" / "best.pt"
DATA_CONFIG = ML_ROOT / "datasets" / "data.yaml"
RESULTS_SPLIT = "test"

CLASS_NAMES = [
    "pothole", "garbage", "open_manhole", "damaged_road",
    "broken_streetlight", "water_leakage", "damaged_sidewalk",
    "fallen_tree", "illegal_dumping"
]


def not_evaluated_report(reason: str) -> dict:
    return {
        "evaluation_status": "NOT_EVALUATED",
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat(),
        "model_path": str(MODEL_PATH),
        "note": (
            "The model has not been evaluated because a prerequisite is missing. "
            "This is not a fabricated result — see 'reason' for details."
        )
    }


def evaluate_with_ultralytics():
    """Run Ultralytics YOLO validation on the test split."""
    from ultralytics import YOLO

    print(f"Loading model from: {MODEL_PATH}")
    model = YOLO(str(MODEL_PATH))

    print(f"Running validation on split: {RESULTS_SPLIT}")
    results = model.val(
        data=str(DATA_CONFIG),
        split=RESULTS_SPLIT,
        verbose=True,
        save_json=False,
    )

    # Overall metrics
    overall = {
        "evaluation_status": "EVALUATED",
        "timestamp": datetime.utcnow().isoformat(),
        "model_path": str(MODEL_PATH),
        "data_config": str(DATA_CONFIG),
        "split": RESULTS_SPLIT,
        "metrics": {
            "precision": float(results.box.mp),
            "recall": float(results.box.mr),
            "mAP_50": float(results.box.map50),
            "mAP_50_95": float(results.box.map),
            "f1": float(2 * results.box.mp * results.box.mr / max(results.box.mp + results.box.mr, 1e-8)),
        }
    }

    # Per-class metrics
    per_class = {}
    if hasattr(results.box, "ap_class_index"):
        ap_per_class = results.box.ap_class_index.tolist() if hasattr(results.box.ap_class_index, "tolist") else []
        p_per_class = results.box.p.tolist() if hasattr(results.box, "p") else []
        r_per_class = results.box.r.tolist() if hasattr(results.box, "r") else []
        ap50_per_class = results.box.ap50.tolist() if hasattr(results.box, "ap50") else []
        ap_per_class_vals = results.box.ap.tolist() if hasattr(results.box, "ap") else []

        for i, class_idx in enumerate(results.box.ap_class_index.tolist()):
            class_name = model.names.get(int(class_idx), f"class_{class_idx}")
            f1 = 0.0
            p = p_per_class[i] if i < len(p_per_class) else 0.0
            r = r_per_class[i] if i < len(r_per_class) else 0.0
            if p + r > 0:
                f1 = 2 * p * r / (p + r)
            per_class[class_name] = {
                "precision": p,
                "recall": r,
                "mAP_50": ap50_per_class[i] if i < len(ap50_per_class) else 0.0,
                "mAP_50_95": ap_per_class_vals[i] if i < len(ap_per_class_vals) else 0.0,
                "f1": f1,
            }

    return overall, per_class


def main():
    print("=" * 60)
    print("CivicAI — YOLO Model Evaluation")
    print("=" * 60)

    # Check prerequisites
    if not MODEL_PATH.exists():
        reason = (
            f"Model file not found at {MODEL_PATH}. "
            "The .pt model file is excluded from version control (gitignored) "
            "and must be trained or downloaded separately. "
            "Run Phase 3 training to generate the model."
        )
        print(f"[SKIP] {reason}")
        overall = not_evaluated_report(reason)
        per_class = {}
    elif not DATA_CONFIG.exists():
        reason = f"Dataset config not found at {DATA_CONFIG}. Run Phase 2 dataset preparation first."
        print(f"[SKIP] {reason}")
        overall = not_evaluated_report(reason)
        per_class = {}
    else:
        try:
            overall, per_class = evaluate_with_ultralytics()
        except ImportError:
            reason = "ultralytics package not installed in this environment."
            overall = not_evaluated_report(reason)
            per_class = {}
        except Exception as e:
            reason = f"Evaluation failed with error: {type(e).__name__}: {e}"
            print(f"[ERROR] {reason}")
            overall = not_evaluated_report(reason)
            per_class = {}

    # Save results
    metrics_path = REPORTS_DIR / "model_metrics.json"
    per_class_path = REPORTS_DIR / "per_class_metrics.json"

    with open(metrics_path, "w") as f:
        json.dump(overall, f, indent=2)
    print(f"[SAVED] {metrics_path}")

    with open(per_class_path, "w") as f:
        json.dump(per_class, f, indent=2)
    print(f"[SAVED] {per_class_path}")

    # Generate markdown summary
    summary_path = REPORTS_DIR / "evaluation_summary.md"
    write_evaluation_summary(summary_path, overall, per_class)
    print(f"[SAVED] {summary_path}")

    print("\nEvaluation complete.")
    return overall


def write_evaluation_summary(path: Path, overall: dict, per_class: dict):
    lines = [
        "# CivicAI — Model Evaluation Summary",
        "",
        f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"**Model Path:** `{overall.get('model_path', 'N/A')}`  ",
        f"**Split:** `{overall.get('split', 'N/A')}`",
        "",
    ]

    status = overall.get("evaluation_status", "UNKNOWN")
    if status == "NOT_EVALUATED":
        lines += [
            "## Status: NOT EVALUATED",
            "",
            f"> **Reason:** {overall.get('reason', 'Unknown')}",
            "",
            "> [!NOTE]",
            "> This is an honest report. Metrics were not fabricated.",
            "> To generate real metrics, ensure the model file and test dataset are available,",
            "> then re-run `python ml/evaluation/evaluate_model.py`.",
            "",
        ]
    else:
        m = overall.get("metrics", {})
        lines += [
            "## Overall Metrics",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Precision (mP) | {m.get('precision', 0):.4f} |",
            f"| Recall (mR) | {m.get('recall', 0):.4f} |",
            f"| mAP@0.5 | {m.get('mAP_50', 0):.4f} |",
            f"| mAP@0.5:0.95 | {m.get('mAP_50_95', 0):.4f} |",
            f"| F1 Score | {m.get('f1', 0):.4f} |",
            "",
        ]
        if per_class:
            lines += [
                "## Per-Class Metrics",
                "",
                "| Class | Precision | Recall | mAP@0.5 | mAP@0.5:0.95 | F1 |",
                "|-------|-----------|--------|---------|-------------|-----|",
            ]
            for cls, vals in sorted(per_class.items()):
                lines.append(
                    f"| {cls} | {vals.get('precision', 0):.3f} | {vals.get('recall', 0):.3f} | "
                    f"{vals.get('mAP_50', 0):.3f} | {vals.get('mAP_50_95', 0):.3f} | {vals.get('f1', 0):.3f} |"
                )
            lines.append("")

    lines += [
        "## Known Limitations",
        "",
        "- Model trained on a relatively small synthetic/scraped dataset.",
        "- Performance may degrade on unseen geographic regions or lighting conditions.",
        "- Some classes (e.g., `open_manhole`, `fallen_tree`) may have fewer training examples,",
        "  leading to lower recall.",
        "- Evaluation is on the held-out test split from Phase 2. Real-world performance may differ.",
        "- Bounding box quality (localization) is not separately reported here.",
        "",
    ]

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


if __name__ == "__main__":
    main()
