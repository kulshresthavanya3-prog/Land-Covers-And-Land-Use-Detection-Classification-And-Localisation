
<div align="center">

# 🧪 Shillong LULC — Test Dataset

**Held-out test split used for final evaluation of the 16-class LULC Mask R-CNN model — Shillong, Meghalaya, India**

![Test Patches](https://img.shields.io/badge/Test%20Patches-1%2C722-blue)
![Val Images](https://img.shields.io/badge/Validation%20Images-96-orange)
![Classes](https://img.shields.io/badge/Classes-16-9cf)
![Format](https://img.shields.io/badge/Format-256x256%20PNG-yellow)
![License](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey)

</div>

---

## 📌 Overview

This dataset is the **held-out test split** used to evaluate the final Mask R-CNN (ResNet-50 FPN) model trained on the Shillong LULC pipeline. It was never used during training or hyperparameter tuning and provides the final measure of detection quality across all **16 land-cover classes**, including the `Cloud_NoData` class.

For the training-side dataset (patches, GAN augmentation, manual annotations), see the companion [training dataset README](./README_training_dataset.md).

---

## 🗂️ Split Composition

| Split | Patches | % of Total |
|---|---|---|
| Train | 8,035 | 70% |
| Validation | 1,722 | 15% |
| **Test** | **1,722** | **15%** |
| **Total** | **11,479** | 100% |

The test split is drawn from the same 219 preprocessed LISS-III/IV scenes as the rest of the dataset, tiled into non-overlapping 256×256 patches (stride = 256), with the same ≥70% valid-pixel filter applied.

A separate **96-image validation subset** from the WITH_CLOUD dataset (642 images, 1,614 annotations, 16 classes) was used for the cloud-aware retrain's evaluation pass — this is distinct from the 1,722-patch general test split above.

| WITH_CLOUD Evaluation Set | Value |
|---|---|
| Total images | 642 |
| Train split (85%) | 546 images |
| **Validation split (15%)** | **96 images** |
| Classes evaluated | 16 LULC + background = 17 |

---

## 🖼️ Patch Format

| Property | Value |
|---|---|
| Patch size | 256 × 256 px |
| Format | PNG (RGB, CLAHE-enhanced) |
| Source | Same preprocessing pipeline as train/val (masking → denoising → CLAHE) |
| Annotation | None required for inference; ground truth (where available) in COCO JSON |

Test patches are **not GAN-augmented** — the synthetic DCGAN patches were used only to enrich the training split, so all test-time evaluation reflects real satellite imagery only.

---

## ✅ Evaluation Results (Qualitative)

The trained model was run on the full test set (Step 6 — automatic detection) and on the 96-image WITH_CLOUD validation subset. Observed behavior:

| Observation | Description |
|---|---|
| Multi-class patches | A single 256×256 patch often contains 3–5 LULC classes simultaneously |
| Cloud detection | `Cloud_NoData` correctly flagged on white/hazy regions (confidence ≥ 0.60) |
| Forest types | `Deciduous` and `Evergreen` separated at moderate confidence (0.57–0.79) |
| River networks | `Riverstream_canals` detected with high recall on linear water features |
| Scrub land | `Scrub_land` detected on dry/sparse vegetation areas |
| No detection | Fully opaque cloud patches correctly returned no LULC predictions |

Representative multi-class predictions observed on the validation subset:

- `Riverstream_canals` + `Scrub_land` on high-resolution river-channel imagery
- `Deciduous` + `Cloud_NoData` on partially cloud-covered forest patches
- `Evergreen` + `Deciduous` + `Cloud_NoData` on mixed forest/cloud scenes
- No detections (correctly blank) on fully cloud-obscured patches

> ⚠️ **Note:** these are qualitative observations from the source report, not formal metrics. No mAP, IoU, precision/recall, or confusion matrix values are currently published for this test set — see [Known Limitations](#️-known-limitations) below.

---

## 🗂️ Directory Structure

```
.
├── outputs/
│   └── dataset/
│       └── test/                      # 1,722 held-out 256×256 test patches
├── outputs/
│   └── coco_dataset/
│       └── annotations_coco_WITH_CLOUD.json   # includes the 96-image validation subset
├── final_validation_with_cloud.png    # sample validation-set detections (Colab output)
├── STEP6_final_demonstration.png      # full test-set detection demonstration
└── README.md
```

---


## ⚠️ Known Limitations

- **No formal quantitative metrics published** — this dataset card documents composition and qualitative detection behavior only; mAP/IoU/per-class precision-recall have not been computed or included.
- **Small formally-annotated validation subset** — only 96 images carry ground-truth annotations for the WITH_CLOUD evaluation; the larger 1,722-patch test split is primarily used for qualitative/visual inspection rather than metric-based scoring.
- **Class imbalance carries over from training** — since `Rural` and `Plantation` have no manual training annotations, test-set detections for these classes (if present) should be treated as low-confidence.
- **No train/test spatial-leakage audit** — patches are tiled from whole scenes; adjacency between train and test patches from the same source scene has not been explicitly verified.
- **Cloud-obscured tiles** are expected to yield zero detections by design — this is treated as correct behavior, not a failure case, but it does reduce the number of "active" evaluation tiles.

---

## 📄 Citation / Attribution

> RESOURCESAT-2/2A LISS-III/IV imagery, courtesy of ISRO, distributed via [Bhoonidhi](https://bhoonidhi.nrsc.gov.in/).

---

## 👤 Maintainer

**Vanya Kulshrestha**— dataset curation and evaluation pipeline.


---

## 📜 License

Released under **CC BY 4.0**. Underlying RESOURCESAT imagery remains subject to ISRO's data usage policy — see [Bhoonidhi terms of use](https://bhoonidhi.nrsc.gov.in/).

</div>
