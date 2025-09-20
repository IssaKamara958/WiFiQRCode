import os
import uuid
import io
import qrcode
from flask import Flask, request, jsonify, render_template, send_file
from werkzeug.utils import secure_filename
from wifi_scanner import WiFiQRScanner

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'wifi-qr-scanner-secret-key-2025')

# Configuration upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

scanner = WiFiQRScanner()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')  # ton template avec <img src="{{ url_for('wifi_qr') }}">

@app.route("/wifi_qr")
def wifi_qr():
    ssid = "MonWiFi"
    password = "MonMotDePasse"
    wifi_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(wifi_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file selected'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    result = scanner.scan_qr_from_image(filepath)
    os.remove(filepath)
    return jsonify(result)

# ... ajoute ici tes autres routes comme /connect, /scan_webcam ...

# --- Main ---
if __name__ == "__main__":
    print("WiFi QR Scanner starting...")
    app.run(host='0.0.0.0', port=5000, debug=True)
