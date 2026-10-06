# Sample Demonstration Dataset

> **NOTICE**: All data, images, coordinates, and complaint texts contained in this directory are **SAMPLE / DEMONSTRATION DATA** curated specifically for testing, system evaluation, viva defense, and feature demonstration. They do NOT represent real citizen submissions or proprietary municipal records.

---

## Directory Organization

```text
demo/
├── README.md               # Dataset overview and demo instructions
├── SAMPLE_DATA.json        # Curated incidents across 5 primary categories
├── pothole/                # Realistic sample road pothole photographs
├── garbage/                # Realistic sample solid waste accumulation photographs
├── streetlight/            # Realistic sample defunct lighting photographs
├── water_leakage/          # Realistic sample potable water pipe rupture photographs
└── damaged_road/           # Realistic sample road subsidence / asphalt cracking photographs
```

---

## Category Specifications & Metadata

| Incident Code | Defect Category | Sample Address | GPS Coordinates | Ground Truth Severity | Expected Dept Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **#CIV-1024** | `pothole` | MG Road, Central Junction, Ward 84 | `12.9716, 77.5946` | **CRITICAL** ($84/100$) | Roads & Highway Authority |
| **#CIV-1023** | `garbage` | 80 Feet Road, Koramangala 4th Block | `12.9352, 77.6245` | **HIGH** ($72/100$) | Solid Waste Management |
| **#CIV-1022** | `streetlight` | 100 Feet Road, Indiranagar | `12.9784, 77.6408` | **MEDIUM** ($54/100$) | Electrical & Lighting Dept |
| **#CIV-1021** | `water_leakage`| 14th Main, HSR Layout Sector 2 | `12.9121, 77.6446` | **CRITICAL** ($89/100$) | Water Supply & Sewerage Board |
| **#CIV-1020** | `damaged_road` | Outer Ring Road, Marathahalli Flyover | `12.9591, 77.6974` | **HIGH** ($68/100$) | Roads & Highway Authority |

---

## Instructions for Live Demo

1. Use the images referenced in `SAMPLE_DATA.json` during the citizen reporting phase.
2. Observe how the YOLOv8 model generates bounding boxes matching the ground truth category.
3. Compare the multi-criteria Priority Score with the expected severity ranking above.
