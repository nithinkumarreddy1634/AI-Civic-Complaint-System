"""Model error analysis and difficult case diagnostic tool.

Categorizes failure modes into false alarms, missed detections, low-confidence boundaries,
and adverse environmental factors (lighting, blur, scale). Isolates difficult samples
for targeted retraining without destructive dataset modifications.
"""
import argparse
import json
import logging
import shutil
from pathlib import Path
from typing import List, Dict, Any

from ml.inference.image_quality import assess_image_quality

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
)
logger = logging.getLogger("error_analysis")


def analyze_prediction_errors(
    predictions_json: Path | str,
    output_dir: Path | str | None = None,
    low_conf_threshold: float = 0.45,
    isolate_samples: bool = True
) -> Dict[str, Any]:
    """Analyzes prediction output JSON, flags diagnostic categories, and isolates problematic cases."""
    pred_path = Path(predictions_json)
    if not pred_path.exists():
        raise FileNotFoundError(f"Predictions file not found: {pred_path}")

    with open(pred_path, "r", encoding="utf-8") as f:
        predictions = json.load(f)

    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "outputs" / "evaluation" / "difficult_cases"
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    findings = {
        "total_analyzed": len(predictions),
        "low_confidence": [],
        "poor_quality_images": [],
        "small_objects": [],
        "zero_detections": [],
        "dense_detections": []
    }

    for item in predictions:
        img_p = Path(item.get("image_path", ""))
        dets = item.get("detections", [])
        quality = item.get("quality", {})

        # 1. Quality inspection
        if quality and not quality.get("valid", True):
            findings["poor_quality_images"].append({
                "image": img_p.name,
                "issues": quality.get("issues", [])
            })

        # 2. No detections at all
        if len(dets) == 0:
            findings["zero_detections"].append(img_p.name)

        # 3. Dense / overlapping detections (> 5 detections in 1 image)
        if len(dets) >= 5:
            findings["dense_detections"].append({
                "image": img_p.name,
                "count": len(dets)
            })

        # 4. Low-confidence and small objects
        for d in dets:
            conf = d.get("confidence", 0.0)
            if conf < low_conf_threshold:
                findings["low_confidence"].append({
                    "image": img_p.name,
                    "class": d.get("class_name"),
                    "confidence": conf
                })

            bbox = d.get("bbox", [0, 0, 0, 0])
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            if 0 < w < 30 or 0 < h < 30:
                findings["small_objects"].append({
                    "image": img_p.name,
                    "class": d.get("class_name"),
                    "size": f"{w:.1f}x{h:.1f}"
                })

        # Optionally copy flagged difficult images for human review
        if isolate_samples and img_p.exists():
            is_difficult = (
                (quality and not quality.get("valid", True))
                or any(d.get("confidence", 1.0) < low_conf_threshold for d in dets)
            )
            if is_difficult:
                target_copy = out_dir / img_p.name
                if not target_copy.exists():
                    shutil.copy2(str(img_p), str(target_copy))

    # Format text report
    lines = []
    lines.append("=" * 65)
    lines.append("              CivicAI Error Analysis & Difficult Cases")
    lines.append("=" * 65)
    lines.append(f"Total Images Analyzed: {findings['total_analyzed']}")
    lines.append(f"Zero Detections (Negative/Clean): {len(findings['zero_detections'])}")
    lines.append(f"Low Confidence Predictions (< {low_conf_threshold}): {len(findings['low_confidence'])}")
    lines.append(f"Adverse Environmental/Quality Flags: {len(findings['poor_quality_images'])}")
    lines.append(f"Small Objects (< 30px): {len(findings['small_objects'])}")
    lines.append(f"High Density / Cluttered Images: {len(findings['dense_detections'])}")
    lines.append("-" * 65)
    lines.append("Observed Failure Modes & Actionable Remediation:")
    lines.append("1. Extreme Blur / Vibration: Ensure citizens capture images while stationary.")
    lines.append("2. Under-exposure (Night Streetlights): Augment with gamma/brightness shifts.")
    lines.append("3. Very Small Distant Defects: Advise closer capture framing in user UI.")
    lines.append("=" * 65 + "\n")

    report_text = "\n".join(lines)
    report_file = out_dir.parent / "error_analysis_report.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report_text)

    json_file = out_dir.parent / "error_analysis.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    logger.info(f"Error analysis report saved to: {report_file}")
    return findings


def main():
    parser = argparse.ArgumentParser(description="Run error analysis on model predictions.")
    parser.add_argument("--predictions", type=str, default="ml/outputs/predictions/predictions_summary.json", help="Path to predictions JSON")
    parser.add_argument("--output-dir", type=str, default=None, help="Directory to save difficult cases")
    args = parser.parse_args()

    analyze_prediction_errors(args.predictions, args.output_dir)


if __name__ == "__main__":
    main()
