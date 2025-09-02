from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
import os
import uuid
from werkzeug.utils import secure_filename
from wifi_scanner import WiFiQRScanner
import traceback

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'wifi-qr-scanner-secret-key-2025')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize scanner
scanner = WiFiQRScanner()

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file selected'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        try:
            result = scanner.scan_qr_from_image(filepath)
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify(result)
        except Exception as scan_error:
            try:
                os.remove(filepath)
            except:
                pass
            return jsonify({'error': f'QR scanning failed: {str(scan_error)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Upload failed: {str(e)}'}), 500

@app.route('/connect', methods=['POST'])
def connect_wifi():
    try:
        data = request.get_json()
        if not data or 'ssid' not in data or 'password' not in data or 'security' not in data:
            return jsonify({'error': 'Missing required fields: ssid, password, security'}), 400
        
        ssid = data['ssid']
        password = data['password']
        security = data['security']
        result = scanner.connect_to_wifi(ssid, password, security)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Connection failed: {str(e)}'}), 500

@app.route('/scan_webcam', methods=['POST'])
def scan_webcam():
    try:
        result = scanner.scan_qr_from_webcam()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'Webcam scanning failed: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'scanner': 'ready'})

if __name__ == '__main__':
    print("WiFi QR Scanner starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)
