"""
mri_segmentation.py
HeartSeg AI v2
Compatible with Flask app.py
"""

import os
import cv2
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.models import Model

# =========================================================
# CONFIG
# =========================================================

CLS_INPUT_SIZE = (96, 96)

CLASS_LABELS = [
    "Normal",
    "Sick"
]

DISEASE_INFO = {
    "Normal": {
        "description": "No major cardiac abnormality detected.",
        "severity": "none",
        "recommendation": "Routine annual cardiac checkup recommended.",
        "medications": [],
        "follow_up": "Annual screening"
    },

    "Sick": {
        "description": "Potential cardiac abnormality detected.",
        "severity": "high",
        "recommendation": "Consult a cardiologist for detailed evaluation.",
        "medications": [
            "Further evaluation required"
        ],
        "follow_up": "Immediate cardiology consultation"
    }
}

# =========================================================
# IMAGE PREPROCESSING
# =========================================================

def load_and_preprocess(img_path, target_size=CLS_INPUT_SIZE):

    img = Image.open(img_path).convert("L")

    img = img.resize(target_size)

    img = np.array(img).astype("float32") / 255.0

    img = np.expand_dims(img, axis=-1)

    img = np.expand_dims(img, axis=0)

    return img


# =========================================================
# CLASSIFICATION
# =========================================================

def run_classification(model, img_path):

    arr = load_and_preprocess(img_path)

    preds = model.predict(arr, verbose=0)[0]

    predicted_idx = int(np.argmax(preds))

    predicted_class = CLASS_LABELS[predicted_idx]

    confidence = float(preds[predicted_idx]) * 100

    all_probs = []

    for i, prob in enumerate(preds):

        all_probs.append(
            (
                CLASS_LABELS[i],
                round(float(prob) * 100, 2)
            )
        )

    all_probs.sort(key=lambda x: x[1], reverse=True)

    return {

        "predicted_class": predicted_class,

        "confidence": round(confidence, 2),

        "all_probs": all_probs,

        "info": DISEASE_INFO[predicted_class]
    }


# =========================================================
# DUMMY SEGMENTATION
# =========================================================

def run_segmentation(model, img_path):

    """
    Placeholder segmentation function.
    Keeps Flask app compatible.
    """

    return {

        "mask": None,

        "overlay_path": None,

        "structure_areas": {

            "Left Ventricle": 0,

            "Right Ventricle": 0,

            "Myocardium": 0
        },

        "per_class_dice": None
    }


# =========================================================
# GRADCAM
# =========================================================

def generate_gradcam(
        model,
        img_path,
        last_conv_layer_name="conv2d_3"
):

    arr = load_and_preprocess(img_path)

    try:

        grad_model = Model(
            inputs=model.inputs,
            outputs=[
                model.get_layer(last_conv_layer_name).output,
                model.output
            ]
        )

    except Exception:

        print("GradCAM layer not found.")
        return img_path

    with tf.GradientTape() as tape:

        conv_outputs, predictions = grad_model(arr)

        pred_index = tf.argmax(predictions[0])

        class_channel = predictions[:, pred_index]

    grads = tape.gradient(class_channel, conv_outputs)

    pooled_grads = tf.reduce_mean(
        grads,
        axis=(0, 1, 2)
    )

    conv_outputs = conv_outputs[0]

    heatmap = conv_outputs @ pooled_grads[..., tf.newaxis]

    heatmap = tf.squeeze(heatmap).numpy()

    heatmap = np.maximum(heatmap, 0)

    if np.max(heatmap) != 0:

        heatmap /= np.max(heatmap)

    # =====================================================
    # LOAD ORIGINAL IMAGE
    # =====================================================

    original = cv2.imread(img_path)

    if original is None:

        original = np.array(
            Image.open(img_path).convert("RGB")
        )

        original = cv2.cvtColor(
            original,
            cv2.COLOR_RGB2BGR
        )

    h, w = original.shape[:2]

    heatmap = cv2.resize(
        heatmap,
        (w, h)
    )

    heatmap = np.uint8(255 * heatmap)

    heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    superimposed = cv2.addWeighted(
        original,
        0.6,
        heatmap,
        0.4,
        0
    )

    # =====================================================
    # SAVE OUTPUT
    # =====================================================

    os.makedirs("uploads", exist_ok=True)

    base_name = os.path.splitext(
        os.path.basename(img_path)
    )[0]

    out_path = os.path.join(
        "uploads",
        f"gradcam_{base_name}.png"
    )

    cv2.imwrite(out_path, superimposed)

    return out_path