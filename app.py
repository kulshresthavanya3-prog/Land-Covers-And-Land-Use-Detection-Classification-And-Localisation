"""
LULC Web Application - Shillong Land Use / Land Cover Detection
Flask backend serving Mask R-CNN predictions
"""

import os
import io
import base64
import json
import numpy as np
import cv2
import torch
import torchvision
from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageDraw, ImageFont
from torchvision.models.detection import maskrcnn_resnet50_fpn
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.models.detection.mask_rcnn import MaskRCNNPredictor

# ── Config ─────────────────────────────────────────────────────────────────────
MODEL_PATH = "outputs/maskrcnn_FINAL_WITH_CLOUD.pth"  # ← change to whichever .pth you downloaded
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CONFIDENCE_THRESHOLD = 0.5

# NUM_CLASSES must match what the model was trained with:
# - maskrcnn_FINAL_WITH_CLOUD.pth  → 17  (16 LULC + background)
# - maskrcnn_shillong_lulc.pth     → 16  (15 LULC + background)
NUM_CLASSES = 17

# ── Class definitions ──────────────────────────────────────────────────────────
CLASS_NAMES = [
    "__background__",
    "Cropland",
    "Fallow",
    "Plantation",
    "Sandy_area",
    "Scrub_land",
    "Mining",
    "Rural",
    "Urban",
    "Deciduous",
    "Evergreen",
    "Forest_plantation",
    "Grass_grazing",
    "Inland_wetland",
    "Riverstream_canals",
    "Water_bodies",
    "Cloud_NoData",   # only present in WITH_CLOUD model; remove if using 16-class model
]

# Distinct colors per class (RGB)
CLASS_COLORS = {
    "Cropland":           (255, 215,   0),
    "Fallow":             (210, 180, 140),
    "Plantation":         ( 34, 139,  34),
    "Sandy_area":         (244, 164,  96),
    "Scrub_land":         (154, 205,  50),
    "Mining":             (128, 128, 128),
    "Rural":              (255, 140,   0),
    "Urban":              (220,  20,  60),
    "Deciduous":          (  0, 128,   0),
    "Evergreen":          (  0, 100,   0),
    "Forest_plantation":  ( 85, 107,  47),
    "Grass_grazing":      (144, 238, 144),
    "Inland_wetland":     ( 64, 224, 208),
    "Riverstream_canals": ( 30, 144, 255),
    "Water_bodies":       (  0,   0, 205),
    "Cloud_NoData":       (200, 200, 220),  # remove if using 16-class model
}

# ── Preprocessing (mirrors notebook pipeline) ──────────────────────────────────
def preprocess_image(img_array):
    """Apply the same CLAHE + denoise pipeline used during training."""
    # Denoise
    denoised = cv2.fastNlMeansDenoisingColored(img_array, None, 5, 5, 7, 21)
    # CLAHE on L channel
    lab = cv2.cvtColor(denoised, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l)
    lab_enhanced = cv2.merge([l_enhanced, a, b])
    enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)
    # Valid pixel mask
    gray = cv2.cvtColor(enhanced, cv2.COLOR_RGB2GRAY)
    mask = (gray > 8).astype(np.uint8)
    mask_3ch = np.stack([mask, mask, mask], axis=-1)
    return (enhanced * mask_3ch).astype(np.uint8)


# ── Model loading ──────────────────────────────────────────────────────────────
def load_model():
    model = maskrcnn_resnet50_fpn(weights=None)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, NUM_CLASSES)
    in_features_mask = model.roi_heads.mask_predictor.conv5_mask.in_channels
    model.roi_heads.mask_predictor = MaskRCNNPredictor(in_features_mask, 256, NUM_CLASSES)

    if os.path.exists(MODEL_PATH):
        state = torch.load(MODEL_PATH, map_location=DEVICE)
        model.load_state_dict(state, strict=False)
        print(f"✅ Model loaded from {MODEL_PATH}")
    else:
        print(f"⚠️  Model file not found at {MODEL_PATH} — using untrained model")

    model.to(DEVICE)
    model.eval()
    return model


# ── Inference ──────────────────────────────────────────────────────────────────
def run_inference(model, img_array):
    tensor = torch.tensor(img_array / 255.0, dtype=torch.float32)
    tensor = tensor.permute(2, 0, 1).unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        outputs = model(tensor)

    return outputs[0]


def draw_predictions(img_array, output, threshold=CONFIDENCE_THRESHOLD):
    """Overlay bounding boxes, labels, and semi-transparent masks."""
    img_pil = Image.fromarray(img_array).convert("RGBA")
    overlay = Image.new("RGBA", img_pil.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    boxes   = output["boxes"].cpu().numpy()
    labels  = output["labels"].cpu().numpy()
    scores  = output["scores"].cpu().numpy()
    masks   = output["masks"].cpu().numpy() if "masks" in output else None

    detections = []
    kept = [(b, l, s) for b, l, s in zip(boxes, labels, scores) if s >= threshold]

    for idx, (box, label, score) in enumerate(kept):
        class_name = CLASS_NAMES[label] if label < len(CLASS_NAMES) else f"class_{label}"
        color = CLASS_COLORS.get(class_name, (255, 0, 0))
        x1, y1, x2, y2 = map(int, box)

        # Mask overlay
        if masks is not None and idx < len(masks):
            mask = masks[idx, 0]
            mask_bin = (mask > 0.5).astype(np.uint8)
            mask_color = (*color, 90)
            for py in range(img_array.shape[0]):
                for px in range(img_array.shape[1]):
                    if mask_bin[py, px]:
                        overlay.putpixel((px, py), mask_color)

        # Bounding box
        draw.rectangle([x1, y1, x2, y2], outline=(*color, 255), width=2)

        # Label text
        label_text = f"{class_name} {score:.2f}"
        text_bg = [x1, max(0, y1 - 18), x1 + len(label_text) * 7, y1]
        draw.rectangle(text_bg, fill=(*color, 200))
        draw.text((x1 + 2, max(0, y1 - 16)), label_text, fill=(255, 255, 255, 255))

        detections.append({
            "class": class_name,
            "confidence": round(float(score), 3),
            "bbox": [x1, y1, x2, y2],
            "color": f"rgb({color[0]},{color[1]},{color[2]})",
        })

    result_img = Image.alpha_composite(img_pil, overlay).convert("RGB")
    return result_img, detections


# ── Flask app ──────────────────────────────────────────────────────────────────
app = Flask(__name__)
model = load_model()


@app.route("/")
def index():
    return render_template("index.html", classes=CLASS_NAMES[1:], colors=CLASS_COLORS)


@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        img = Image.open(file.stream).convert("RGB")
        img_array = np.array(img)

        # Preprocess
        processed = preprocess_image(img_array)

        # Run model
        output = run_inference(model, processed)

        # Draw results
        result_img, detections = draw_predictions(processed, output)

        # Encode result image to base64
        buf = io.BytesIO()
        result_img.save(buf, format="PNG")
        img_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # Encode original preprocessed image too
        buf2 = io.BytesIO()
        Image.fromarray(processed).save(buf2, format="PNG")
        orig_b64 = base64.b64encode(buf2.getvalue()).decode("utf-8")

        # Class summary
        class_counts = {}
        for d in detections:
            class_counts[d["class"]] = class_counts.get(d["class"], 0) + 1

        return jsonify({
            "result_image": img_b64,
            "original_image": orig_b64,
            "detections": detections,
            "class_summary": class_counts,
            "total_detections": len(detections),
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/classes")
def get_classes():
    classes = [
        {"name": name, "color": f"rgb({c[0]},{c[1]},{c[2]})"}
        for name, c in CLASS_COLORS.items()
    ]
    return jsonify(classes)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
