"""
app.py
HeartSeg AI v2 — Flask Web Application

Routes:
    GET  /           → Login page
    POST /           → Authenticate user
    GET  /upload     → MRI upload form (protected)
    POST /predict    → Run segmentation + classification (protected)
    GET  /result     → View last prediction result (protected)
    GET  /logout     → End session
    GET  /uploads/<filename> → Serve uploaded/generated images

Author: Sriram V & HeartSeg AI Team
Institution: Saveetha Engineering College, Chennai
"""

import os
import secrets
from flask import (
    Flask, request, render_template,
    redirect, url_for, session, send_from_directory, abort
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
app.secret_key = secrets.token_hex(32)   # Cryptographically random session key

UPLOAD_FOLDER   = "uploads"
ALLOWED_EXT     = {"png", "jpg", "jpeg"}
MAX_CONTENT_MB  = 10

app.config["UPLOAD_FOLDER"]    = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_MB * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─── Model Loading ────────────────────────────────────────────────────────────

SEG_MODEL_PATH = os.path.join("h5", "heartseg_unet.h5")
CLS_MODEL_PATH = os.path.join("h5", "heart_model.h5")

seg_model = None
cls_model = None

def load_models():
    """Load both models at startup. Prints a clear error if files are missing."""
    global seg_model, cls_model
    if os.path.exists(SEG_MODEL_PATH):
        seg_model = load_model(SEG_MODEL_PATH, compile=False)
        print(f"  [OK] Segmentation model loaded: {SEG_MODEL_PATH}")
    else:
        print(f"  [WARN] Segmentation model not found at {SEG_MODEL_PATH}.")
        print("         Run: python train.py --mode seg")

    if os.path.exists(CLS_MODEL_PATH):
        cls_model = load_model(CLS_MODEL_PATH, compile=False)
        print(f"  [OK] Classification model loaded: {CLS_MODEL_PATH}")
    else:
        print(f"  [WARN] Classification model not found at {CLS_MODEL_PATH}.")
        print("         Run: python train.py --mode cls")


# ─── Helpers ──────────────────────────────────────────────────────────────────

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


def login_required(f):
    """Decorator to protect routes that need authentication."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("upload"))

    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        # In production: replace with database lookup + hashed passwords
        if username == "heart123" and password == "heart123":
            session["logged_in"] = True
            session["username"]   = username
            return redirect(url_for("upload"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


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

    # ── Segmentation ──
    seg_result = {"overlay_path": None, "structure_areas": {}, "mask": None}
    if seg_model is not None:
        try:
            seg_result = run_segmentation(seg_model, file_path)
        except Exception as e:
            print(f"  [ERROR] Segmentation failed: {e}")

    # ── Classification ──
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

    # ── Grad-CAM ──
    gradcam_url = None
    if cls_model is not None:
        try:
            gc_path = generate_gradcam(cls_model, file_path)
            gradcam_url = url_for("serve_upload", filename=os.path.basename(gc_path))
        except Exception as e:
            print(f"  [WARN] Grad-CAM skipped: {e}")

    # ── Overlay URL ──
    overlay_url = None
    if seg_result.get("overlay_path") and os.path.exists(seg_result["overlay_path"]):
        overlay_url = url_for(
            "serve_upload",
            filename=os.path.basename(seg_result["overlay_path"])
        )

    return render_template(
        "result.html",
        image_url=url_for("serve_upload", filename=filename),
        overlay_url=overlay_url,
        gradcam_url=gradcam_url,
        predicted_class=cls_result["predicted_class"],
        confidence=cls_result["confidence"],
        all_probs=cls_result["all_probs"],
        disease_info=cls_result["info"],
        structure_areas=seg_result["structure_areas"],
        severity=cls_result["info"].get("severity", "none"),
    )


@app.route("/uploads/<filename>")
@login_required
def serve_upload(filename: str):
    """Securely serve uploaded and generated images."""
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
