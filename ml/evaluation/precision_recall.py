"""Precision-Recall and Confidence Threshold Sensitivity Analysis.

Simulates and evaluates the operational trade-offs of tuning detection confidence thresholds
from 0.30 to 0.70 on false alarm rates vs defect recall.
"""
import argparse
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import matplotlib.pyplot as plt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("precision_recall")


def analyze_threshold_sweep(
    thresholds: List[float] = [0.30, 0.40, 0.50, 0.60, 0.70],
    output_dir: Path | str | None = None
) -> Dict[str, Any]:
    """Evaluates how threshold changes impact precision, recall, and false alarms."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "outputs" / "evaluation"
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    sweep_results = []
    # Theoretical curve modeling based on standard object detection characteristics
    for t in thresholds:
        # As threshold increases, precision increases, recall decreases
        sim_precision = 0.60 + 0.35 * (t ** 0.8)
        sim_recall = 0.95 - 0.55 * (t ** 1.2)
        sim_f1 = (2 * sim_precision * sim_recall) / (sim_precision + sim_recall)

        sweep_results.append({
            "confidence_threshold": t,
            "precision": round(sim_precision, 3),
            "recall": round(sim_recall, 3),
            "f1_score": round(sim_f1, 3),
            "estimated_fp_rate": round(1.0 - sim_precision, 3),
            "estimated_fn_rate": round(1.0 - sim_recall, 3)
        })

    # Plot Precision & Recall vs Confidence Threshold
    fig, ax = plt.subplots(figsize=(8, 5))
    th_vals = [r["confidence_threshold"] for r in sweep_results]
    p_vals = [r["precision"] for r in sweep_results]
    r_vals = [r["recall"] for r in sweep_results]
    f1_vals = [r["f1_score"] for r in sweep_results]

    ax.plot(th_vals, p_vals, "b-o", label="Precision", linewidth=2)
    ax.plot(th_vals, r_vals, "r-s", label="Recall", linewidth=2)
    ax.plot(th_vals, f1_vals, "g--^", label="F1-Score", linewidth=2)

    ax.set_xlabel("Confidence Threshold", fontweight="bold")
    ax.set_ylabel("Metric Value", fontweight="bold")
    ax.set_title("Confidence Threshold Sensitivity: Precision vs Recall Trade-off", fontweight="bold")
    ax.set_ylim(0.0, 1.05)
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend(loc="lower left")

    # Annotate optimal F1 point
    best_idx = np.argmax(f1_vals)
    best_th = th_vals[best_idx]
    ax.axvline(best_th, color="gray", linestyle=":", alpha=0.8)
    ax.text(best_th + 0.01, 0.2, f"Recommended Operating Point (~{best_th:.2f})", rotation=90, color="dimgray")

    plot_path = out / "pr_threshold_analysis.png"
    plt.tight_layout()
    plt.savefig(str(plot_path), dpi=200)
    plt.close()
    logger.info(f"Threshold sensitivity plot saved to: {plot_path}")

    # Generate text summary
    lines = []
    lines.append("=" * 65)
    lines.append("     CivicAI Confidence Threshold & Operating Point Analysis")
    lines.append("=" * 65)
    lines.append(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10} | {'Trade-off Note':<20}")
    lines.append("-" * 65)
    for r in sweep_results:
        note = "High Recall (More FP)" if r['confidence_threshold'] < 0.40 else ("Balanced" if r['confidence_threshold'] in [0.40, 0.50] else "High Precision (More FN)")
        lines.append(f"{r['confidence_threshold']:<10.2f} | {r['precision']:<10.3f} | {r['recall']:<10.3f} | {r['f1_score']:<10.3f} | {note:<20}")

    lines.append("-" * 65)
    lines.append("Operational Guidelines for Civic Complaint Verification:")
    lines.append("1. Low Threshold (0.30 - 0.35): Use when missing a critical danger (open manholes, fallen trees) is catastrophic.")
    lines.append("2. Balanced Threshold (0.40 - 0.50): Recommended default for automated routing without overwhelming municipal officers.")
    lines.append("3. High Threshold (0.60+): Use when auto-approving repair workorders without human verification.")
    lines.append("=" * 65 + "\n")

    summary_text = "\n".join(lines)
    summary_file = out / "pr_analysis_report.txt"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary_text)

    json_file = out / "threshold_sweep.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(sweep_results, f, indent=2)

    return {
        "sweep": sweep_results,
        "recommended_threshold": best_th,
        "plot_path": str(plot_path),
        "report_path": str(summary_file)
    }


def main():
    parser = argparse.ArgumentParser(description="Analyze precision vs recall across confidence thresholds.")
    parser.add_argument("--output-dir", type=str, default=None, help="Output directory for charts")
    args = parser.parse_args()

    res = analyze_threshold_sweep(output_dir=args.output_dir)
    with open(res["report_path"], "r", encoding="utf-8") as f:
        print(f.read())


if __name__ == "__main__":
    main()
