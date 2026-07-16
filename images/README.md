<div align="center">

# 🛰️ Shillong LULC Training Dataset

**LISS-III/IV satellite imagery + COCO-format annotations for 16-class Land Use / Land Cover instance segmentation — Shillong, Meghalaya, India**

![Scenes](https://img.shields.io/badge/Source%20Scenes-219-blue)
![Patches](https://img.shields.io/badge/Patches-11%2C479-orange)
![Annotations](https://img.shields.io/badge/Final%20Annotations-1%2C614-brightgreen)
![Classes](https://img.shields.io/badge/Classes-16-9cf)
![Format](https://img.shields.io/badge/Format-COCO%20JSON-yellow)
![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)

</div>

---

## 📌 Overview

This dataset provides preprocessed, tiled, and partially annotated satellite imagery of the **Shillong / East Khāsi Hills** region for training LULC instance-segmentation models. It combines raw RESOURCESAT LISS-III/IV scenes, a GAN-augmented synthetic pool, and a manually + semi-supervised annotated subset across **16 land-cover classes**.

---

## 📦 Source Imagery

| Source Prefix | Sensor / Description | Approx. Scenes |
|---|---|---|
| `RA3xx` | RESOURCESAT-2/2A — LISS-IV / PAN | ~100 |
| `AA-series` | High-resolution auxiliary acquisition (Group A) | ~50 |
| `qwerty-series` | Auxiliary acquisition (Group Q) | ~40 |
| Numeric IDs (`2`, `165`, …) | Standard grid tiles | ~29 |
| **Total** | | **219** |

All 219 scenes were successfully preprocessed (0 failures).

### Valid-Pixel Coverage

| Metric | Value |
|---|---|
| Mean | 78.2% |
| Median | 78.2% |
| Min | 74.1% |
| Max | 84.4% |

Scenes below 70% valid coverage were retained at image level, but individual 256×256 tiles derived from them with <70% valid pixels were dropped during patch extraction.

---

## 🧩 Patch-Level Dataset

| Metric | Value |
|---|---|
| Patch size | 256 × 256 px |
| Stride | 256 px (non-overlapping) |
| Min valid ratio per patch | 70% |
| **Total patches extracted** | **11,479** |
| Train split (70%) | 8,035 |
| Validation split (15%) | 1,722 |
| Test split (15%) | 1,722 |

---


---

## 🏷️ Annotated Subset

| Version | Images | Instances | File |
|---|---|---|---|
| Manual (QGIS + VIA) | 25 | 83 | `annotations_coco.json` |
| Semi-supervised (pseudo-labels) | 633 | 1,605 | `annotations_coco_SEMISUPERVISED.json` |
| **Final — WITH_CLOUD (16 classes)** | **642** | **1,614** | `annotations_coco_WITH_CLOUD.json` |

### Manual Annotation Counts by Class

This is where the class imbalance originates — the semi-supervised expansion inherits and amplifies it.

| ID | Class | Manual Count | ID | Class | Manual Count |
|---|---|---|---|---|---|
| 1 | Cropland | 6 | 9 | Deciduous | **22** |
| 2 | Fallow | 2 | 10 | Evergreen | 4 |
| 3 | Plantation | **0** | 11 | Forest_plantation | 2 |
| 4 | Sandy_area | 2 | 12 | Grass_grazing | 3 |
| 5 | Scrub_land | 9 | 13 | Inland_wetland | 1 |
| 6 | Mining | 3 | 14 | Riverstream_canals | 16 |
| 7 | Rural | **0** | 15 | Water_bodies | 10 |
| 8 | Urban | 3 | 16 | Cloud_NoData | *(added later)* |

> `Deciduous` accounts for ~27% of all manual annotations, while `Rural` and `Plantation` have **zero** manual examples. This directly motivates the weighted loss used at training time (see below) and explains the model's tendency to over-predict `Deciduous`.

### Per-Class Loss Weights (applied at training, inverse to annotation frequency, clipped at 15.0)

| Class | Weight | Class | Weight |
|---|---|---|---|
| Cropland | 15.000 | Grass_grazing | 15.000 |
| Fallow | 15.000 | Inland_wetland | 15.000 |
| Plantation | 1.000 | Riverstream_canals | 0.454 |
| Sandy_area | 15.000 | Water_bodies | 0.300 |
| Scrub_land | 0.842 | Cloud_NoData | 12.810 |
| Mining | 15.000 | Urban | 15.000 |
| Rural | 1.000 | Deciduous | 0.300 |
| Evergreen | 15.000 | Forest_plantation | 15.000 |

---

## 🗂️ Directory Structure

```
.
├── raw/                                            # Original 219 LISS-III/IV scenes
├── outputs/
│   ├── enhanced/                                   # CLAHE-enhanced scenes (219 files)
│   ├── masks/                                      # Binary valid-pixel masks (.png + .npy)
│   ├── patches/                                    # 11,479 tiled 256×256 patches
│   ├── dataset/                                    # train/ val/ test/ splits
│   ├── gan_generated/                              # 1,000 synthetic GAN patches
│   ├── dataset_v3_gan_augmented/                   # 9,035 patches (real + GAN)
│   ├── coco_dataset/
│   │   ├── annotations_coco.json                   # Manual annotations (83 instances)
│   │   ├── annotations_coco_SEMISUPERVISED.json    # Pseudo-labeled annotations (1,605 instances)
│   │   └── annotations_coco_WITH_CLOUD.json        # Final annotations (1,614 instances, 16 classes)
│   └── preprocessing_metadata.json                 # Per-image preprocessing statistics
└── README.md
```

---


## ⚠️ Known Limitations

- **Severe class imbalance** — `Deciduous` is heavily over-represented; `Rural` and `Plantation` have no manual ground truth at all, relying entirely on pseudo-labels.
- **Instance count ≠ area** — annotation counts are reported per-polygon; no per-class pixel/area statistics are currently included, so it's unclear whether Deciduous dominates by count, area, or both.
- **No documented acquisition dates** — seasonal metadata for the RA3xx vs. AA/qwerty series scenes isn't tracked, which may affect consistency of `Cropland`/`Fallow` labels across scenes captured in different seasons.
- **Patch-level train/test independence not verified** — patches are tiled from whole scenes; spatial adjacency between train and test patches from the same scene has not been explicitly checked for leakage.
- **No quantitative accuracy metrics included** — this dataset card documents composition, not model performance; see the companion technical report for qualitative detection results.
- Tiles with <70% valid pixels are excluded, which may under-represent scene edges and heavily shadowed terrain.

---

## 📄 Citation / Attribution

> RESOURCESAT-2/2A LISS-III/IV imagery, courtesy of ISRO, distributed via [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/).

If you use this dataset in published work, please cite the imagery source above and link back to this repository.

---

## 👤 Maintainer

**Vanya Kulshrestha** — dataset curation, preprocessing pipeline, annotation coordination.


---

## 📜 License

Derived/processed dataset released under **CC BY 4.0**. Underlying RESOURCESAT imagery remains subject to ISRO's data usage policy — see [Bhoonidhi terms of use](https://bhoonidhi.nrsc.gov.in/).

</div>
