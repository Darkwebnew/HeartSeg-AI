# config.py — move secrets out of app.py
import os
SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')