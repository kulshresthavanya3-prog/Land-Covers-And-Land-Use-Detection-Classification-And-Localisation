<div align="center">

# 🎨 Shillong LULC — VIA-Labeled Annotation Set

**Manually labeled polygons (VGG Image Annotator) for 16-class Land Use / Land Cover mapping — Shillong, Meghalaya, India, with standardized color-coded class legend.**

![Tool](https://img.shields.io/badge/Annotation%20Tool-VIA%20%2B%20QGIS-589632)
![Images](https://img.shields.io/badge/Manually%20Labeled-25%20images-blue)
![Instances](https://img.shields.io/badge/Instances-83-orange)
![Classes](https://img.shields.io/badge/Classes-16-9cf)
![Format](https://img.shields.io/badge/Export-COCO%20JSON-yellow)

</div>

---

## 📌 Overview

This dataset contains the **manually annotated ground-truth polygons** for the Shillong LULC pipeline, labeled using the **VGG Image Annotator (VIA)** and cross-checked in **QGIS**. Polygons were drawn over CLAHE-enhanced 256×256 satellite patches and exported in **COCO JSON** format.

Each class below is paired with a **standard cartographic color** used for visualizing the labeled masks — consistent with conventional LULC map styling (greens for vegetation, blues for water, warm tones for built-up/bare land). Use these swatches when styling exported masks in QGIS, matplotlib, or any COCO-viewer.

---

## 🖍️ Land Cover Class Color Legend

| Swatch | Class | Hex | RGB |
|:---:|---|---|---|
| ![#DAA520](https://placehold.co/40x20/DAA520/DAA520.png) | Cropland | `#DAA520` | (218, 165, 32) |
| ![#F0E68C](https://placehold.co/40x20/F0E68C/F0E68C.png) | Fallow | `#F0E68C` | (240, 230, 140) |
| ![#808000](https://placehold.co/40x20/808000/808000.png) | Plantation | `#808000` | (128, 128, 0) |
| ![#F4A460](https://placehold.co/40x20/F4A460/F4A460.png) | Sandy_area | `#F4A460` | (244, 164, 96) |
| ![#9ACD32](https://placehold.co/40x20/9ACD32/9ACD32.png) | Scrub_land | `#9ACD32` | (154, 205, 50) |
| ![#8B4513](https://placehold.co/40x20/8B4513/8B4513.png) | Mining | `#8B4513` | (139, 69, 19) |
| ![#DEB887](https://placehold.co/40x20/DEB887/DEB887.png) | Rural | `#DEB887` | (222, 184, 135) |
| ![#FF0000](https://placehold.co/40x20/FF0000/FF0000.png) | Urban | `#FF0000` | (255, 0, 0) |
| ![#228B22](https://placehold.co/40x20/228B22/228B22.png) | Deciduous | `#228B22` | (34, 139, 34) |
| ![#006400](https://placehold.co/40x20/006400/006400.png) | Evergreen | `#006400` | (0, 100, 0) |
| ![#3CB371](https://placehold.co/40x20/3CB371/3CB371.png) | Forest_plantation | `#3CB371` | (60, 179, 113) |
| ![#90EE90](https://placehold.co/40x20/90EE90/90EE90.png) | Grass_grazing | `#90EE90` | (144, 238, 144) |
| ![#20B2AA](https://placehold.co/40x20/20B2AA/20B2AA.png) | Inland_wetland | `#20B2AA` | (32, 178, 170) |
| ![#1E90FF](https://placehold.co/40x20/1E90FF/1E90FF.png) | Riverstream_canals | `#1E90FF` | (30, 144, 255) |
| ![#00008B](https://placehold.co/40x20/00008B/00008B.png) | Water_bodies | `#00008B` | (0, 0, 139) |
| ![#D3D3D3](https://placehold.co/40x20/D3D3D3/D3D3D3.png) | Cloud_NoData | `#D3D3D3` | (211, 211, 211) |

> 🎨 **Color logic:** warm earth tones (yellow → brown) for agricultural/bare-land classes, greens (light → dark) for vegetation density, blue tones for hydrology, red for built-up areas, and neutral grey for the no-data/cloud class — matching common LULC cartographic convention (e.g. NLCD-style palettes).

---

## 🏷️ Annotation Details

| Field | Value |
|---|---|
| Annotation tool | VGG Image Annotator (VIA) |
| Cross-verification | QGIS |
| Images manually labeled | 25 |
| Total manual instances | 83 |
| Export format | VIA JSON → converted to COCO instance-segmentation JSON |
| Annotation type | Polygon (instance segmentation masks) |

### Manual Annotation Counts per Class

| ID | Class | Color | Instances |
|---|---|---|---|
| 1 | Cropland | 🟨 `#DAA520` | 6 |
| 2 | Fallow | 🟡 `#F0E68C` | 2 |
| 3 | Plantation | 🫒 `#808000` | 0 |
| 4 | Sandy_area | 🟧 `#F4A460` | 2 |
| 5 | Scrub_land | 🟢 `#9ACD32` | 9 |
| 6 | Mining | 🟤 `#8B4513` | 3 |
| 7 | Rural | 🟫 `#DEB887` | 0 |
| 8 | Urban | 🔴 `#FF0000` | 3 |
| 9 | Deciduous | 🟩 `#228B22` | 22 |
| 10 | Evergreen | 🟢 `#006400` | 4 |
| 11 | Forest_plantation | 🟢 `#3CB371` | 2 |
| 12 | Grass_grazing | 🟩 `#90EE90` | 3 |
| 13 | Inland_wetland | 🔵 `#20B2AA` | 1 |
| 14 | Riverstream_canals | 🔵 `#1E90FF` | 16 |
| 15 | Water_bodies | 🔵 `#00008B` | 10 |
| 16 | Cloud_NoData | ⚪ `#D3D3D3` | *(added post-hoc)* |

> `Deciduous` (🟩) is the most heavily labeled class (22 of 83 instances, ~27%); `Rural` and `Plantation` have zero manual instances — see [Known Limitations](#️-known-limitations).

---

## 🗂️ Directory Structure

```
.
├── via_project/
│   ├── via_annotations.json           # Raw VIA project export
│   └── images/                        # 25 manually annotated 256×256 patches
├── outputs/
│   └── coco_dataset/
│       └── annotations_coco.json      # Converted COCO instance-segmentation JSON
├── legend/
│   └── lulc_color_map.json            # Class → hex color mapping (see below)
└── README.md
```

### `lulc_color_map.json`

```json
{
  "Cropland":            "#DAA520",
  "Fallow":              "#F0E68C",
  "Plantation":          "#808000",
  "Sandy_area":          "#F4A460",
  "Scrub_land":          "#9ACD32",
  "Mining":              "#8B4513",
  "Rural":               "#DEB887",
  "Urban":               "#FF0000",
  "Deciduous":           "#228B22",
  "Evergreen":           "#006400",
  "Forest_plantation":   "#3CB371",
  "Grass_grazing":       "#90EE90",
  "Inland_wetland":      "#20B2AA",
  "Riverstream_canals":  "#1E90FF",
  "Water_bodies":        "#00008B",
  "Cloud_NoData":        "#D3D3D3"
}
```

---

---
## ⚠️ Known Limitations

- **Class imbalance in manual labels** — `Deciduous` is over-represented (22/83 instances); `Rural` and `Plantation` have no manual annotations at all.
- **Small manually labeled set** — only 25 images (83 instances) were hand-annotated; the rest of the training annotations come from semi-supervised pseudo-labeling, which was not independently color-verified against this legend.
- **Color legend is a cartographic convention, not sensor-derived** — these hex values are assigned for visualization/consistency purposes and do not encode spectral reflectance values from the source imagery.
- **`Cloud_NoData`** was introduced after the initial VIA labeling pass, so it does not appear in the original 25-image manual set — it was added at the WITH_CLOUD dataset stage.

---

## 👤 Maintainer

**Vanya Kulshrestha** — annotation coordination and color-legend standardization.


---



</div>
