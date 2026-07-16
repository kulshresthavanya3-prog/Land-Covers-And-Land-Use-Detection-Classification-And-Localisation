

# 🛰️ Shillong LULC Detection Pipeline

**Instance-segmentation-based Land Use / Land Cover mapping for Shillong, Meghalaya**
**using multi-source satellite imagery, GAN-based augmentation, and semi-supervised Mask R-CNN.**




## 📌 Overview

This repository contains the complete pipeline used to produce a 16-class **Land Use / Land Cover (LULC)** instance-segmentation model for the **Shillong / East Khāsi Hills** region of Meghalaya, India, using **LISS-III/IV satellite imagery**.

The pipeline covers everything from raw scene ingestion to a trained, cloud-aware **Mask R-CNN (ResNet-50 FPN)** model:

```
Raw Scenes → Preprocessing → Patch Extraction → GAN Augmentation
→ Manual Annotation → Semi-Supervised Pseudo-Labeling → Weighted Mask R-CNN Training → Evaluation
```

📄 A full write-up is available in [`Shillong_LULC_Technical_Report.docx`](./Shillong_LULC_Technical_Report.docx).

---

## ✨ Key Features

- 🌍 **219 satellite scenes** ingested from RESOURCESAT (LISS-III/IV) and auxiliary sources
- 🧼 3-stage preprocessing: valid-pixel masking → denoising → CLAHE contrast enhancement
- 🧩 **11,479** non-overlapping 256×256 patches, 70/15/15 train/val/test split
- 🎨 **DCGAN-based synthetic augmentation** (1,000 generated patches, 2 refinement rounds)
- ✏️ Manual **QGIS + VIA** polygon annotation across **15 LULC classes**
- 🔁 **Semi-supervised pseudo-labeling** loop expanding annotations from 83 → 1,605 instances
- ☁️ Dedicated **Cloud_NoData (16th) class** for robustness on cloud-obscured imagery
- ⚖️ **Custom weighted Fast R-CNN loss** to counter severe class imbalance
- 📊 Reproducible training log, loss curves, and qualitative detection results

---

## 🗂️ Project Structure

```
.
├── outputs/
│   ├── enhanced/                                 # CLAHE-enhanced images (219 files)
│   ├── masks/                                     # Binary valid-pixel masks (.png + .npy)
│   ├── patches/                                   # 11,479 tiled 256×256 patches
│   ├── dataset/                                   # Train / val / test splits
│   ├── gan_generated/                             # 1,000 GAN synthetic patches
│   ├── dataset_v3_gan_augmented/                  # 9,035 patches (real + GAN)
│   ├── coco_dataset/
│   │   ├── annotations_coco.json                  # Manual COCO annotations (83 instances)
│   │   ├── annotations_coco_SEMISUPERVISED.json   # Semi-supervised annotations (1,605 instances)
│   │   └── annotations_coco_WITH_CLOUD.json       # WITH_CLOUD annotations (1,614 instances, 16 classes)
│   ├── gan_generator_final.pth                    # Saved GAN generator weights
│   ├── maskrcnn_shillong_lulc.pth                 # Initial Mask R-CNN weights
│   └── preprocessing_metadata.json                # Per-image preprocessing stats
├── maskrcnn_FINAL_WITH_CLOUD.pth                  # Final Mask R-CNN weights (16 classes + cloud)
└── README.md
```

---

## 🧬 Dataset

| Source Prefix | Description | Approx. Count |
|---|---|---|
| `RA3xx` | RESOURCESAT-2/2A (LISS-IV / PAN) | ~100 |
| `AA-series` | High-resolution auxiliary acquisition group A | ~50 |
| `qwerty-series` | Auxiliary acquisition group Q | ~40 |
| Numeric (`2`, `165`, …) | Standard grid tiles | ~29 |

**Valid-pixel coverage:** mean 78.2% · min 74.1% · max 84.4% across all 219 images.

### LULC Classes (16 total)

`Cropland` · `Fallow` · `Plantation` · `Sandy_area` · `Scrub_land` · `Mining` · `Rural` · `Urban` · `Deciduous` · `Evergreen` · `Forest_plantation` · `Grass_grazing` · `Inland_wetland` · `Riverstream_canals` · `Water_bodies` · `Cloud_NoData`

---

## ⚙️ Pipeline

### 1. Preprocessing
- **Valid-pixel masking** — binary mask via grayscale threshold at intensity 8
- **Denoising** — `cv2.fastNlMeansDenoisingColored` (h=5, hColor=5, templateWindowSize=7, searchWindowSize=21)
- **CLAHE** — LAB L-channel, clipLimit=2.0, tileGrid=8×8 (masked to preserve black borders)

### 2. Patch Extraction
- 256×256 patches, stride 256 (non-overlapping), ≥70% valid-pixel threshold
- **11,479** total patches → **8,035 / 1,722 / 1,722** train/val/test

### 3. GAN Augmentation (DCGAN)
| Parameter | Value |
|---|---|
| Latent dimension | 100 |
| Training resolution | 128 × 128 px |
| Batch size | 32 |
| Epochs (final run) | 20 |
| Training subset | 500 real patches |
| Optimizer | Adam (β₁=0.5, β₂=0.999) |
| Synthetic patches generated | 1,000 |

Round-2 refinements: `ConvTranspose2d → Upsample+Conv2d` (no checkerboarding), label smoothing (0.9), 2× generator steps per discriminator step, lower discriminator LR (1e-4 vs. 2e-4).

### 4. Annotation & Semi-Supervised Expansion
| Dataset Version | Images | Annotations |
|---|---|---|
| Manual (QGIS + VIA) | 25 | 83 |
| Semi-supervised (pseudo-labels) | 633 | 1,605 |
| **WITH_CLOUD (final)** | **642** | **1,614** |

### 5. Model Training

**Architecture:** Mask R-CNN, ResNet-50 + FPN backbone, ImageNet/COCO-pretrained, rebuilt with 17 output nodes (16 classes + background) for the cloud-aware retrain.

**Weighted loss** — class weights inversely proportional to annotation frequency, clipped at 15.0:

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

Loss = weighted cross-entropy (classification) + Smooth-L1 (box regression, β=1/9, `reduction='sum'`, normalized by label count).

| Parameter | Value |
|---|---|
| Epochs | 10 |
| Device | CUDA (GPU) |
| Optimizer | SGD (torchvision default) |
| Final training loss | **0.4335** (from 0.9853 at epoch 1) |
| Total training time | ~21 minutes (1,259 s) |

---

## 📈 Results

- Model correctly localizes **river/stream networks, forest types, scrub land, water bodies, and cloud cover** on the held-out validation set (96 images).
- Multi-class patches (3–5 simultaneous LULC classes per 256×256 tile) are handled correctly.
- `Cloud_NoData` reliably flagged on white/hazy regions (confidence ≥ 0.60); fully opaque cloud patches correctly return **no detections**.
- `Deciduous` / `Evergreen` separated at moderate confidence (0.57–0.79); `Riverstream_canals` detected with high recall on linear features.

**Known limitations:** over-prediction of `Deciduous` due to class imbalance in the manual annotation set; several minority classes (`Rural`, `Plantation`) remain under-represented and would benefit from additional manual labeling.

---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| Modeling | PyTorch, torchvision (Mask R-CNN, ResNet-50 FPN) |
| Image processing | OpenCV, CLAHE, DCGAN |
| Annotation | QGIS, VGG Image Annotator (VIA), COCO format |
| Environment | Google Colab (T4 GPU), Kiro IDE |
| Data source | Bhoonidhi (ISRO) — LISS-III/IV scenes |

---

## 🚀 Getting Started

```bash
# clone the repository
git clone https://github.com/<your-username>/shillong-lulc-pipeline.git
cd shillong-lulc-pipeline

# install dependencies
pip install torch torchvision opencv-python pycocotools numpy matplotlib

# run inference with the final trained model
python detect.py --weights maskrcnn_FINAL_WITH_CLOUD.pth --input path/to/patch.png
```

> Training scripts, the DCGAN augmentation notebook, and the full preprocessing pipeline are provided under `notebooks/` (Colab-ready).

---

## 📄 Documentation

For the complete methodology, dataset statistics, per-class weighting rationale, and validation figures, see the full technical report:

📘 **[Shillong_LULC_Technical_Report.docx](./Shillong_LULC_Technical_Report.docx)**

---

## 👤 Author

**Vanya Kulshrestha** — Project lead, pipeline design & implementation


---



</div>
