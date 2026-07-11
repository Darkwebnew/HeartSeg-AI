"""
app.py
HeartSeg AI v2 — Flask Web Application

Routes:
    GET  /           → Landing page
    GET  /login      → Login page
    POST /login      → Authenticate user
    GET  /dashboard  → Main dashboard (protected)
    GET  /upload     → MRI upload form (protected)
    POST /predict    → Validate upload, redirect to processing (protected)
    GET  /processing → AI processing animation (protected)
    POST /run-analysis → Run models, return result (protected)
    GET  /result     → View last prediction result (protected)
    GET  /history    → Scan history (protected)
    GET  /research   → Research & model info (protected)
    GET  /about      → About page (protected)
    GET  /settings   → Settings page (protected)
    GET  /logout     → End session
    GET  /uploads/<filename> → Serve uploaded/generated images

Author: Sriram V & HeartSeg AI Team
Institution: Saveetha Engineering College, Chennai
"""

import os
import secrets
import uuid
from flask import (
    Flask, request, render_template,
    redirect, url_for, session, send_from_directory, abort, jsonify
)
from tensorflow.keras.models import load_model
from werkzeug.utils import secure_filename

from mri_segmentation import (
    run_segmentation,
    run_classification,
    generate_gradcam,
    DISEASE_INFO,
)

# ─── App Configuration ────────────────────────────────────────────────────────

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

UPLOAD_FOLDER   = "uploads"
ALLOWED_EXT     = {"png", "jpg", "jpeg"}
MAX_CONTENT_MB  = 10

app.config["UPLOAD_FOLDER"]    = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

pending_jobs = {}

# ─── Model Loading ────────────────────────────────────────────────────────────

SEG_MODEL_PATH = os.path.join("h5", "heartseg_unet.h5")
CLS_MODEL_PATH = os.path.join("h5", "heart_model.h5")

seg_model = None
cls_model = None

def load_models():
    global seg_model, cls_model
    if os.path.exists(SEG_MODEL_PATH):
        seg_model = load_model(SEG_MODEL_PATH, compile=False)
        print(f"  [OK] Segmentation model loaded: {SEG_MODEL_PATH}")
    else:
        print(f"  [WARN] Segmentation model not found at {SEG_MODEL_PATH}.")

    if os.path.exists(CLS_MODEL_PATH):
        cls_model = load_model(CLS_MODEL_PATH, compile=False)
        print(f"  [OK] Classification model loaded: {CLS_MODEL_PATH}")
    else:
        print(f"  [WARN] Classification model not found at {CLS_MODEL_PATH}.")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─── Demo History Data ────────────────────────────────────────────────────────

DEMO_HISTORY = [
    {"id": "HS-2025-0012", "patient": "Arun Kumar", "age": "58", "gender": "Male", "date": "2025-01-15", "result": "Normal", "confidence": 97.4, "severity": "none", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0011", "patient": "Priya Nair", "age": "64", "gender": "Female", "date": "2025-01-14", "result": "Sick", "confidence": 94.2, "severity": "high", "doctor": "Dr. Patel", "status": "Complete"},
    {"id": "HS-2025-0010", "patient": "Ravi Menon", "age": "45", "gender": "Male", "date": "2025-01-14", "result": "Normal", "confidence": 91.8, "severity": "none", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0009", "patient": "Lakshmi Rao", "age": "72", "gender": "Female", "date": "2025-01-13", "result": "Sick", "confidence": 88.5, "severity": "high", "doctor": "Dr. Patel", "status": "Complete"},
    {"id": "HS-2025-0008", "patient": "Karthik Iyer", "age": "39", "gender": "Male", "date": "2025-01-12", "result": "Normal", "confidence": 96.1, "severity": "none", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0007", "patient": "Anita Desai", "age": "55", "gender": "Female", "date": "2025-01-11", "result": "Normal", "confidence": 93.7, "severity": "none", "doctor": "Dr. Patel", "status": "Complete"},
    {"id": "HS-2025-0006", "patient": "Suresh Reddy", "age": "67", "gender": "Male", "date": "2025-01-10", "result": "Sick", "confidence": 91.3, "severity": "critical", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0005", "patient": "Meena Joshi", "age": "42", "gender": "Female", "date": "2025-01-09", "result": "Normal", "confidence": 95.8, "severity": "none", "doctor": "Dr. Patel", "status": "Complete"},
    {"id": "HS-2025-0004", "patient": "Vikram Shah", "age": "51", "gender": "Male", "date": "2025-01-08", "result": "Sick", "confidence": 89.6, "severity": "medium", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0003", "patient": "Deepa Pillai", "age": "48", "gender": "Female", "date": "2025-01-07", "result": "Normal", "confidence": 94.5, "severity": "none", "doctor": "Dr. Patel", "status": "Complete"},
    {"id": "HS-2025-0002", "patient": "Rajesh Gopal", "age": "61", "gender": "Male", "date": "2025-01-06", "result": "Sick", "confidence": 92.1, "severity": "high", "doctor": "Dr. Sharma", "status": "Complete"},
    {"id": "HS-2025-0001", "patient": "Sunita Verma", "age": "37", "gender": "Female", "date": "2025-01-05", "result": "Normal", "confidence": 98.2, "severity": "none", "doctor": "Dr. Patel", "status": "Complete"},
]


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "heart123" and password == "heart123":
            session["logged_in"] = True
            session["username"]   = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("landing"))


@app.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "total": 12, "normal": 8, "critical": 2, "pending": 2
    }
    recent = [
        {"id": "HS-2025-0012", "patient": "Demo Patient A", "date": "2025-01-15", "result": "Normal", "confidence": 97.4, "severity": "none"},
        {"id": "HS-2025-0011", "patient": "Demo Patient B", "date": "2025-01-14", "result": "Sick", "confidence": 94.2, "severity": "high"},
        {"id": "HS-2025-0010", "patient": "Demo Patient C", "date": "2025-01-14", "result": "Normal", "confidence": 91.8, "severity": "none"},
        {"id": "HS-2025-0009", "patient": "Demo Patient D", "date": "2025-01-13", "result": "Sick", "confidence": 88.5, "severity": "high"},
        {"id": "HS-2025-0008", "patient": "Demo Patient E", "date": "2025-01-12", "result": "Normal", "confidence": 96.1, "severity": "none"},
    ]
    model_status = {
        "seg_loaded": seg_model is not None,
        "cls_loaded": cls_model is not None,
        "version": "v2.0.1",
        "last_check": "Active"
    }
    activity = [
        {"time": "2 min ago", "text": "Classification model loaded successfully"},
        {"time": "2 min ago", "text": "Segmentation model loaded successfully"},
        {"time": "15 min ago", "text": "Analysis HS-2025-0012 completed"},
        {"time": "1 hr ago", "text": "Analysis HS-2025-0011 completed"},
        {"time": "3 hrs ago", "text": "System startup — models initialized"},
    ]
    return render_template(
        "dashboard.html",
        username=session.get("username", "User"),
        stats=stats, recent=recent,
        model_status=model_status, activity=activity
    )


@app.route("/upload")
@login_required
def upload():
    return render_template("upload.html")


@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if "file" not in request.files:
        return render_template("upload.html", error="No file selected.")

    file = request.files["file"]
    if file.filename == "":
        return render_template("upload.html", error="No file selected.")

    if not allowed_file(file.filename):
        return render_template("upload.html",
                               error="Unsupported file type. Please upload PNG or JPG.")

    filename  = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    job_id = str(uuid.uuid4())[:8]
    
    pending_jobs[job_id] = {
        "file_path": file_path,
        "filename": filename,
        "patient": {
            "name": request.form.get("patient_name", "").strip() or "Unnamed Patient",
            "age": request.form.get("patient_age", "").strip() or "—",
            "gender": request.form.get("patient_gender", "").strip() or "—",
            "hospital_id": request.form.get("hospital_id", "").strip() or "—",
            "doctor": request.form.get("doctor_name", "").strip() or "—",
            "symptoms": request.form.get("symptoms", "").strip() or "None recorded",
            "heart_rate": request.form.get("heart_rate", "").strip() or "—",
            "blood_pressure": request.form.get("blood_pressure", "").strip() or "—",
            "mri_date": request.form.get("mri_date", "").strip() or "—",
            "notes": request.form.get("notes", "").strip() or "—",
        }
    }

    return redirect(url_for("processing", job_id=job_id))


@app.route("/processing")
@login_required
def processing():
    job_id = request.args.get("job_id")
    if not job_id or job_id not in pending_jobs:
        return redirect(url_for("upload"))
    return render_template("processing.html", job_id=job_id)


@app.route("/run-analysis", methods=["POST"])
@login_required
def run_analysis():
    job_id = request.json.get("job_id")
    if not job_id or job_id not in pending_jobs:
        return jsonify({"error": "Invalid job"}), 400

    job = pending_jobs[job_id]
    file_path = job["file_path"]
    filename = job["filename"]

    seg_result = {"overlay_path": None, "structure_areas": {}, "mask": None}
    if seg_model is not None:
        try:
            seg_result = run_segmentation(seg_model, file_path)
        except Exception as e:
            print(f"  [ERROR] Segmentation failed: {e}")

    cls_result = {
        "predicted_class": "Unknown",
        "confidence": 0.0,
        "all_probs": [],
        "info": {},
    }
    if cls_model is not None:
        try:
            cls_result = run_classification(cls_model, file_path)
        except Exception as e:
            print(f"  [ERROR] Classification failed: {e}")

    gradcam_filename = None
    if cls_model is not None:
        try:
            gc_path = generate_gradcam(cls_model, file_path)
            gradcam_filename = os.path.basename(gc_path)
        except Exception as e:
            print(f"  [WARN] Grad-CAM skipped: {e}")

    overlay_filename = None
    if seg_result.get("overlay_path") and os.path.exists(seg_result["overlay_path"]):
        overlay_filename = os.path.basename(seg_result["overlay_path"])

    result_data = {
        "patient": job["patient"],
        "image_filename": filename,
        "overlay_filename": overlay_filename,
        "gradcam_filename": gradcam_filename,
        "predicted_class": cls_result["predicted_class"],
        "confidence": cls_result["confidence"],
        "all_probs": cls_result["all_probs"],
        "disease_info": cls_result["info"],
        "structure_areas": seg_result["structure_areas"],
        "severity": cls_result["info"].get("severity", "none"),
    }

    session["last_result"] = result_data
    del pending_jobs[job_id]

    return jsonify({"success": True})


@app.route("/result")
@login_required
def result():
    result_data = session.get("last_result")
    if not result_data:
        return redirect(url_for("upload"))

    return render_template(
        "result.html",
        patient=result_data["patient"],
        image_url=url_for("serve_upload", filename=result_data["image_filename"]),
        overlay_url=url_for("serve_upload", filename=result_data["overlay_filename"]) if result_data["overlay_filename"] else None,
        gradcam_url=url_for("serve_upload", filename=result_data["gradcam_filename"]) if result_data["gradcam_filename"] else None,
        predicted_class=result_data["predicted_class"],
        confidence=result_data["confidence"],
        all_probs=result_data["all_probs"],
        disease_info=result_data["disease_info"],
        structure_areas=result_data["structure_areas"],
        severity=result_data["severity"],
    )


@app.route("/history")
@login_required
def history():
    history_data = DEMO_HISTORY
    
    filter_result = request.args.get("result", "all")
    filter_date = request.args.get("date", "")
    search = request.args.get("search", "").lower()
    
    filtered = history_data
    if filter_result != "all":
        filtered = [h for h in filtered if h["result"].lower() == filter_result.lower()]
    if filter_date:
        filtered = [h for h in filtered if h["date"] == filter_date]
    if search:
        filtered = [h for h in filtered if search in h["patient"].lower() or search in h["id"].lower()]
    
    return render_template(
        "history.html",
        history=filtered,
        total_count=len(history_data),
        filtered_count=len(filtered),
        filter_result=filter_result,
        filter_date=filter_date,
        search=search
    )


@app.route("/research")
@login_required
def research():
    model_specs = {
        "segmentation": {
            "name": "U-Net",
            "architecture": "Encoder-Decoder with Skip Connections",
            "input_size": "256 × 256 × 1",
            "output_classes": 4,
            "classes": ["Background", "Left Ventricle", "Right Ventricle", "Myocardium"],
            "filters": [64, 128, 256, 512, 1024],
            "metrics": {
                "dice": 94.8,
                "iou": 91.2,
                "pixel_accuracy": 96.5
            },
            "training": {
                "epochs": 50,
                "batch_size": 8,
                "optimizer": "Adam (lr=1e-4)",
                "loss": "Sparse Categorical Crossentropy",
                "dataset": "ACDC + Custom annotations"
            }
        },
        "classification": {
            "name": "CNN",
            "architecture": "4-block Conv2D + GlobalAveragePool + Dense",
            "input_size": "96 × 96 × 1",
            "output_classes": 2,
            "classes": ["Normal", "Sick"],
            "layers": [
                "Conv2D(16) → BatchNorm → MaxPool",
                "Conv2D(32) → BatchNorm → MaxPool",
                "Conv2D(64) → BatchNorm → MaxPool",
                "Conv2D(128) → BatchNorm",
                "GlobalAveragePooling2D",
                "Dense(64) → Dropout(0.4)",
                "Dense(2) → Softmax"
            ],
            "metrics": {
                "accuracy": 98.26,
                "precision": 98.0,
                "recall": 98.0,
                "f1": 98.0
            },
            "training": {
                "epochs": 20,
                "batch_size": 4,
                "optimizer": "Adam (lr=1e-4)",
                "loss": "Sparse Categorical Crossentropy",
                "dataset": "63,425 cardiac MRI images",
                "split": "80% Train / 20% Validation"
            }
        },
        "explainability": {
            "name": "Grad-CAM",
            "method": "Gradient-weighted Class Activation Mapping",
            "target_layer": "conv2d_3 (last conv layer)",
            "output": "Heatmap overlay on original MRI",
            "citation": "Selvaraju et al., ICCV 2017"
        }
    }
    
    dataset_info = {
        "total_images": 63425,
        "normal": 37564,
        "sick": 25861,
        "source": "ACDC (Automated Cardiac Diagnosis Challenge)",
        "citation": "Bernard et al., IEEE TMI 2018",
        "url": "https://www.creatis.insa-lyon.fr/Challenge/acdc/"
    }
    
    references = [
        {
            "title": "U-Net: Convolutional Networks for Biomedical Image Segmentation",
            "authors": "Ronneberger, Fischer, Brox",
            "venue": "MICCAI 2015",
            "link": "https://arxiv.org/abs/1505.04597"
        },
        {
            "title": "Deep Learning Techniques for Automatic MRI Cardiac Multi-Structures Segmentation",
            "authors": "Bernard et al.",
            "venue": "IEEE TMI 2018",
            "link": "https://www.creatis.insa-lyon.fr/Challenge/acdc/"
        },
        {
            "title": "Grad-CAM: Visual Explanations from Deep Networks via Gradient-based Localization",
            "authors": "Selvaraju et al.",
            "venue": "ICCV 2017",
            "link": "https://arxiv.org/abs/1610.02391"
        }
    ]
    
    return render_template(
        "research.html",
        model_specs=model_specs,
        dataset_info=dataset_info,
        references=references
    )


@app.route("/about")
@login_required
def about():
    team = [
        {
            "name": "Sriram V",
            "role": "Project Lead & Developer",
            "contributions": "U-Net Architecture · Flask App · Model Training",
            "github": "https://github.com/darkwebnew"
        },
        {
            "name": "Surothaaman R",
            "role": "Backend Developer",
            "contributions": "Inference Pipeline · Flask Integration · Preprocessing",
            "github": "https://github.com/surothaaman"
        },
        {
            "name": "Andrew Varghese V S",
            "role": "Frontend & Research",
            "contributions": "Dashboard UI · CSS · Documentation",
            "github": "https://github.com/Andrewvarghese653"
        }
    ]
    
    institution = {
        "name": "Saveetha Engineering College",
        "location": "Chennai, Tamil Nadu, India",
        "year": "2024–2025",
        "type": "Final Year Mini Project"
    }
    
    tech_stack = [
        {"name": "Python", "version": "3.9+", "category": "Language"},
        {"name": "TensorFlow", "version": "2.12+", "category": "ML Framework"},
        {"name": "Keras", "version": "2.12+", "category": "ML Framework"},
        {"name": "Flask", "version": "2.3+", "category": "Web Framework"},
        {"name": "OpenCV", "version": "4.7+", "category": "Image Processing"},
        {"name": "NumPy", "version": "1.23+", "category": "Computation"},
        {"name": "Pillow", "version": "9.0+", "category": "Image Processing"},
        {"name": "scikit-learn", "version": "1.2+", "category": "ML Utilities"},
    ]
    
    timeline = [
        {"phase": "Phase 1", "title": "Research & Dataset", "desc": "Literature review, ACDC dataset acquisition, data preprocessing pipeline", "status": "complete"},
        {"phase": "Phase 2", "title": "U-Net Segmentation", "desc": "Built encoder-decoder with skip connections, trained on 256×256 cardiac MRI masks", "status": "complete"},
        {"phase": "Phase 3", "title": "CNN Classification", "desc": "4-block Conv2D architecture, trained on 63K images with class weighting", "status": "complete"},
        {"phase": "Phase 4", "title": "Grad-CAM Explainability", "desc": "Integrated gradient-based visual explanations from last conv layer", "status": "complete"},
        {"phase": "Phase 5", "title": "Flask Web Application", "desc": "Built secure web platform with session auth, file handling, and dashboard UI", "status": "complete"},
        {"phase": "Phase 6", "title": "UI/UX Redesign", "desc": "Dark medical dashboard, animated processing, enhanced result pages", "status": "complete"},
    ]
    
    links = {
        "github": "https://github.com/Darkwebnew/HeartSeg-AI",
        "github_v1": "https://github.com/Darkwebnew/Miniproject",
        "license": "MIT License",
        "paper": None
    }
    
    return render_template(
        "about.html",
        team=team,
        institution=institution,
        tech_stack=tech_stack,
        timeline=timeline,
        links=links
    )


@app.route("/settings")
@login_required
def settings():
    """Settings page with user preferences and system info."""
    user_profile = {
        "username": session.get("username", "User"),
        "role": "Researcher",
        "email": "researcher@heartseg.ai",
        "institution": "Saveetha Engineering College",
        "joined": "2025-01-01"
    }
    
    preferences = {
        "theme": "dark",
        "language": "English",
        "notifications": True,
        "email_alerts": False,
        "auto_logout": 30,
        "confidence_threshold": 85
    }
    
    system_info = {
        "version": "v2.0.1",
        "python_version": "3.9.18",
        "tensorflow_version": "2.12.0",
        "flask_version": "2.3.3",
        "last_update": "2025-01-15",
        "models_loaded": {
            "segmentation": seg_model is not None,
            "classification": cls_model is not None
        }
    }
    
    export_settings = {
        "default_format": "PDF",
        "include_gradcam": True,
        "include_segmentation": True,
        "include_vitals": True,
        "auto_export": False
    }
    
    return render_template(
        "settings.html",
        user_profile=user_profile,
        preferences=preferences,
        system_info=system_info,
        export_settings=export_settings
    )


@app.route("/uploads/<filename>")
@login_required
def serve_upload(filename: str):
    safe_name = secure_filename(filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    if not os.path.exists(file_path):
        abort(404)
    return send_from_directory(app.config["UPLOAD_FOLDER"], safe_name)


# ─── Error Handlers ───────────────────────────────────────────────────────────

@app.errorhandler(413)
def too_large(e):
    return render_template("upload.html",
                           error=f"File too large. Maximum size is {MAX_CONTENT_MB} MB."), 413


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for("upload"))


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n" + "="*55)
    print("  HeartSeg AI v2  ·  Starting...")
    print("="*55)
    load_models()
    print("  Navigate to: http://localhost:5000")
    print("="*55 + "\n")
    app.run(debug=False, host="0.0.0.0", port=5000)