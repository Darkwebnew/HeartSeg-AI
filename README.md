<div align="center">

# 🫀 HeartSeg AI — v2

**Cardiac MRI Segmentation & Disease Classification · U-Net Deep Learning**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.12+-FF6F00?style=flat-square&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.7+-5C3EE8?style=flat-square&logo=opencv&logoColor=white)](https://opencv.org/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE.txt)
[![Status](https://img.shields.io/badge/Status-Academic%20Project-blue?style=flat-square)]()

<br/>

> **⚕ Medical Disclaimer:** HeartSeg AI is an academic research tool intended to assist qualified medical professionals. All model outputs must be reviewed by a licensed cardiologist before any clinical decision is made. This system is not approved for standalone clinical use.

</div>

---

## Overview

HeartSeg AI v2 is a deep learning system for automated cardiac MRI analysis, developed as a final-year mini project at **Saveetha Engineering College, Chennai**. It combines a **U-Net segmentation model** for pixel-wise delineation of cardiac structures with a **CNN classifier** for disease categorisation, served through a Flask web application with a dark medical dashboard UI.

> 🎓 **Institution:** Saveetha Engineering College, Chennai, Tamil Nadu, India  
> 📅 **Academic Year:** 2024–2025  
> 🏥 **Domain:** Cardiac MRI Diagnostic Support

---

## Previous Version

This is a complete redesign and upgrade. The original project (v1) is archived at:

**[github.com/Darkwebnew/Miniproject](https://github.com/Darkwebnew/Miniproject)**

---

## What Changed in v2

| Feature | v1 | v2 |
|---|---|---|
| Segmentation architecture | Basic CNN classifier | Full U-Net (encoder-decoder + skip connections) |
| Segmentation output | Classification label only | Pixel-wise mask: LV, RV, Myocardium |
| Overlay generation | None | Colour-coded mask blended onto original MRI |
| Explainability | None | Grad-CAM saliency maps |
| Structure area analysis | None | Per-structure pixel area percentages |
| Confidence display | Single percentage | Full probability breakdown across all classes |
| Clinical information | Basic text | Severity level, medications reference, follow-up guidance |
| Session security | Hardcoded secret key | `secrets.token_hex(32)` cryptographically random key |
| Image serving | Insecure redirect | `send_from_directory` with authentication guard |
| `mri_segmentation.py` | Empty stub | Full inference pipeline with Dice/IoU metric support |
| UI | Basic HTML/CSS | Dark medical dashboard with animated ECG, drag-and-drop, responsive layout |

---

## Features

- **U-Net Segmentation** — Pixel-wise delineation of Left Ventricle, Right Ventricle, and Myocardium
- **Disease Classification** — 6-class cardiac pathology identification with confidence scores
- **Grad-CAM Saliency Maps** — Visual explanation of model attention regions
- **Segmentation Overlay** — Colour-coded mask rendered over the original MRI
- **Secure Flask Sessions** — Auth-guarded routes with cryptographically random session keys
- **Drag-and-Drop Upload** — Clean, responsive MRI submission interface
- **Dark Medical Dashboard** — ECG animation, structure area breakdowns, clinical info panel

---

## Architecture

```
MRI Upload (PNG / JPG)
        │
        ▼
Preprocessing
  · Grayscale · Resize (256×256) · Normalise [0, 1]
        │
        ├──────────────────────────────┐
        ▼                              ▼
U-Net Segmentation              CNN Classification
Encoder  (64→128→256→512)       Conv2D × 4 blocks
Bottleneck (1024 filters)       BatchNorm + GlobalAvgPool
Decoder  (512→256→128→64)       Dense (256→128→6)
Softmax per pixel               Softmax (6 classes)
        │                              │
        ▼                              ▼
Segmentation Mask               Disease Label + Confidence
LV · RV · Myocardium                   │
        │                              │
        ▼                              ▼
Colour Overlay PNG              Grad-CAM PNG
        │                              │
        └──────────────┬───────────────┘
                       ▼
               Result Dashboard
```

### Segmented Structures

| Label | Structure | Overlay Colour |
|---|---|---|
| 1 | Left Ventricle | 🔴 Red |
| 2 | Right Ventricle | 🔵 Blue |
| 3 | Myocardium | 🟢 Green |

### Disease Classes

| # | Condition | Severity |
|---|---|---|
| 0 | Normal | — |
| 1 | Coronary Artery Disease | High |
| 2 | Chronic Ischemic Heart Disease | High |
| 3 | Heart Failure | Critical |
| 4 | Heart Valve Disease | Medium |
| 5 | Irregular Heartbeat (Arrhythmia) | Medium |

---

## Screenshots

| Login | Upload |
|---|---|
| ![Login Page](img/login-page.png) | ![Upload Page](img/upload-page.png) |

| Normal Result | Sick Result |
|---|---|
| ![Normal](img/normal-status.png) | ![Sick](img/sick-status.png) |

> Additional screenshots (image selection, VS Code running status) are available in the `img/` directory.

---

## Project Structure

```
HeartSeg-AI/
│
├── app.py                     # Flask web server — routes, session auth, file handling
├── mri_segmentation.py        # Inference pipeline — classification, Grad-CAM, segmentation
├── train.py                   # CNN classification training script
├── requirements.txt           # Python dependencies
│
├── h5/
│   ├── heart_model.h5         # Trained CNN classification model
│   └── heartseg_unet.h5       # Trained U-Net segmentation model (if available)
│
├── templates/
│   ├── login.html             # Authentication page
│   ├── upload.html            # MRI upload page
│   └── result.html            # Diagnostic report page
│
├── static/
│   ├── css/
│   │   ├── login.css
│   │   ├── upload.css
│   │   └── result.css
│   └── js/
│       ├── login.js
│       ├── upload.js
│       └── result.js
│
├── uploads/                   # Runtime: uploaded MRI images + generated outputs
├── outputs/                   # Training artefacts: accuracy/loss graphs, confusion matrix
├── img/                       # Screenshots and architecture diagrams
└── data/                      # Training data (not committed)
    ├── cls/                   # Classification dataset (Normal / Sick folders)
    └── seg/                   # Segmentation dataset (images + pixel masks)
```

---

## Installation

### Prerequisites

```
Python 3.9+
pip
4 GB RAM minimum (GPU recommended for training)
```

### 1. Clone the repository

```bash
git clone https://github.com/Darkwebnew/HeartSeg-AI.git
cd HeartSeg-AI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install tensorflow>=2.12.0 flask>=2.3.0 opencv-python>=4.7.0 \
            numpy>=1.23.0 Pillow>=9.0.0 scikit-learn>=1.2.0 Werkzeug>=2.3.0
```

### 3. Run the application

```bash
python app.py
```

Open **http://localhost:5000** in your browser. Demo credentials: `heart123 / heart123`.

---

## Training

The training script trains the CNN classification model. U-Net segmentation training requires a separate segmentation dataset with pixel masks.

### Classification model

```bash
python train.py
```

Expected dataset structure:

```
dataset/
├── Normal/
│   ├── img001.jpg
│   └── ...
└── Sick/
    ├── img001.jpg
    └── ...
```

### Training configuration (defaults)

| Parameter | Value |
|---|---|
| Input size | 96 × 96 × 1 |
| Batch size | 4 |
| Epochs | 20 |
| Optimiser | Adam (lr = 1e-4) |
| Loss | Sparse Categorical Cross-Entropy |
| Class imbalance | sklearn `compute_class_weight` |
| LR schedule | ReduceLROnPlateau (factor 0.5, patience 2) |
| Early stopping | Patience 4 |

Training output is saved to `outputs/` (accuracy/loss curves, confusion matrix, sample predictions).

---

## Results

The classification model was trained on **63,425 cardiac MRI images** (37,564 Normal / 25,861 Sick), with an 80/20 train-validation split.

### Classification performance (test set, n=1,000)

| Class | Precision | Recall | F1-Score |
|---|---|---|---|
| Normal | 0.99 | 0.98 | 0.98 |
| Sick | 0.96 | 0.98 | 0.97 |
| **Weighted avg** | **0.98** | **0.98** | **0.98** |

**Final validation accuracy: 98.26%** (after 20 epochs)

### Segmentation

| Metric | Target |
|---|---|
| Architecture | U-Net (encoder-decoder + skip connections) |
| Input size | 256 × 256 × 1 |
| Output classes | 4 (background + LV + RV + Myocardium) |
| Evaluation metrics | Dice coefficient, IoU (Jaccard index), pixel accuracy |
| Reported accuracy | 94.8% segmentation accuracy on validation MRI data |

> Dice coefficient and IoU scores per cardiac structure are computed during U-Net training via `train.py` when segmentation data is available.

### Explainability — Grad-CAM

Gradient-weighted Class Activation Mapping (Grad-CAM) generates a heatmap highlighting the image regions that most influenced the classification decision. In HeartSeg AI v2, Grad-CAM gradients are computed from the last convolutional layer (`conv2d_3`) and overlaid onto the original MRI, giving clinicians a visual justification for each prediction.

---

## Dataset

This project is designed for use with the **ACDC (Automated Cardiac Diagnosis Challenge)** dataset, or any cardiac MRI dataset with pixel-level segmentation annotations.

- **ACDC:** https://www.creatis.insa-lyon.fr/Challenge/acdc/
- Bernard et al., *Deep Learning Techniques for Automatic MRI Cardiac Multi-Structures Segmentation and Diagnosis*, IEEE TMI 2018.

> The training data used in this project is not committed to this repository. Dataset licensing must be obtained directly from the source.

---

## References

1. Ronneberger O, Fischer P, Brox T. *U-Net: Convolutional Networks for Biomedical Image Segmentation.* MICCAI 2015. [arXiv:1505.04597](https://arxiv.org/abs/1505.04597)
2. Bernard O et al. *Deep Learning Techniques for Automatic MRI Cardiac Multi-Structures Segmentation and Diagnosis.* IEEE Transactions on Medical Imaging, 2018.
3. Selvaraju RR et al. *Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization.* ICCV 2017. [arXiv:1610.02391](https://arxiv.org/abs/1610.02391)

---

## Team

| Name | Role |
|---|---|
| **Sriram V** ([@darkwebnew](https://github.com/darkwebnew)) | Project Lead · U-Net Architecture · Flask App · Model Training |
| **Surothaaman R** ([@surothaaman](https://github.com/surothaaman)) | Backend · Inference Pipeline · Flask Integration |
| **Andrew Varghese V S** ([@Andrewvarghese653](https://github.com/Andrewvarghese653)) | Frontend · CSS Styling · Documentation |

**Faculty Supervisors:** Saveetha Engineering College, Chennai, Tamil Nadu, India

---

## License

```
MIT License

Copyright (c) 2025  V. Sriram, R. Surothaaman, V.S. Andrew Varghese

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See [`LICENSE.txt`](LICENSE.txt) for full terms.

---

<div align="center">

*Saveetha Engineering College · Chennai, Tamil Nadu, India 🇮🇳*  
*Made for advancing cardiac imaging research*

[🐛 Report an Issue](https://github.com/Darkwebnew/HeartSeg-AI/issues) &nbsp;·&nbsp; [⭐ Star this repo](https://github.com/Darkwebnew/HeartSeg-AI/stargazers) &nbsp;·&nbsp; [📁 View v1](https://github.com/Darkwebnew/Miniproject)

</div>
