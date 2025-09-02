class WiFiQRScanner {
    constructor() {
        this.initializeElements();
        this.bindEvents();
        this.currentData = null;
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadProgress = document.getElementById('uploadProgress');
        this.webcamBtn = document.getElementById('webcamBtn');
        this.resultsCard = document.getElementById('resultsCard');
        this.resultsContent = document.getElementById('resultsContent');
        this.clearResults = document.getElementById('clearResults');
        this.toastElement = document.getElementById('alertToast');
        this.toast = new bootstrap.Toast(this.toastElement);
    }

    bindEvents() {
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));
        
        // File input change
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        
        // Webcam button
        this.webcamBtn.addEventListener('click', this.scanWithWebcam.bind(this));
        
        // Clear results
        this.clearResults.addEventListener('click', this.clearResultsHandler.bind(this));
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const file = e.target.files[0];
        if (file) {
            this.processFile(file);
        }
    }

    processFile(file) {
        // Validate file
        const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/bmp', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
            this.showToast('error', 'Invalid File Type', 'Please select a valid image file.');
            return;
        }

        if (file.size > 16 * 1024 * 1024) { // 16MB
            this.showToast('error', 'File Too Large', 'Maximum file size is 16MB.');
            return;
        }

        // Show progress
        this.showProgress();

        // Create FormData
        const formData = new FormData();
        formData.append('file', file);

        // Upload and scan
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            this.hideProgress();
            this.handleScanResult(data);
        })
        .catch(error => {
            this.hideProgress();
            this.showToast('error', 'Upload Failed', `Error: ${error.message}`);
        });
    }

    async scanWithWebcam() {
        const originalHtml = this.webcamBtn.innerHTML;
        this.webcamBtn.innerHTML = '<div class="spinner"></div><span class="loading-text">Scanning...</span>';
        this.webcamBtn.disabled = true;

        try {
            const response = await fetch('/scan_webcam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            this.handleScanResult(data);
            
        } catch (error) {
            this.showToast('error', 'Webcam Error', `Failed to scan: ${error.message}`);
        } finally {
            this.webcamBtn.innerHTML = originalHtml;
            this.webcamBtn.disabled = false;
        }
    }

    handleScanResult(data) {
        if (data.success) {
            this.currentData = data;
            this.displayResults(data);
            this.showToast('success', 'QR Code Found', `WiFi network "${data.ssid}" detected!`);
        } else {
            this.showToast('error', 'Scan Failed', data.error || 'Could not read QR code');
        }
    }

    displayResults(data) {
        const html = `
            <div class="wifi-info fade-in">
                <h4><i class="fas fa-wifi me-2"></i>${data.ssid}</h4>
                
                <div class="info-item">
                    <span class="info-label"><i class="fas fa-network-wired me-2"></i>Network Name:</span>
                    <span class="info-value">${data.ssid}</span>
                </div>
                
                <div class="info-item">
                    <span class="info-label"><i class="fas fa-key me-2"></i>Password:</span>
                    <span class="info-value">
                        <span id="passwordDisplay">${data.password ? '••••••••••••' : 'None'}</span>
                        ${data.password ? '<i class="fas fa-eye password-toggle ms-2" id="passwordToggle" title="Show/Hide Password"></i>' : ''}
                    </span>
                </div>
                
                <div class="info-item">
                    <span class="info-label"><i class="fas fa-shield-alt me-2"></i>Security:</span>
                    <span class="security-badge security-${data.security.toLowerCase()}">${data.security}</span>
                </div>
                
                <div class="info-item">
                    <span class="info-label"><i class="fas fa-search me-2"></i>Scan Method:</span>
                    <span class="info-value">${data.method || 'image'}</span>
                </div>
                
                ${data.hidden ? '<div class="info-item"><span class="info-label"><i class="fas fa-eye-slash me-2"></i>Hidden Network:</span><span class="status-badge status-info">Yes</span></div>' : ''}
            </div>
            
            <div class="connect-section">
                <h5><i class="fas fa-plug me-2"></i>Connect to Network</h5>
                <p class="text-muted mb-3">Click below to automatically connect to this WiFi network (Windows only)</p>
                <button id="connectBtn" class="btn btn-connect btn-lg">
                    <i class="fas fa-wifi me-2"></i>Connect Now
                </button>
                <div id="connectionStatus"></div>
            </div>
            
            <div class="qr-details">
                <h6><i class="fas fa-info-circle me-2"></i>QR Code Details</h6>
                <div class="raw-data">
                    <small>${data.raw_data || 'N/A'}</small>
                </div>
            </div>
        `;

        this.resultsContent.innerHTML = html;
        this.resultsCard.classList.remove('d-none');

        // Bind password toggle
        const passwordToggle = document.getElementById('passwordToggle');
        if (passwordToggle) {
            passwordToggle.addEventListener('click', this.togglePassword.bind(this));
        }

        // Bind connect button
        const connectBtn = document.getElementById('connectBtn');
        if (connectBtn) {
            connectBtn.addEventListener('click', this.connectToWiFi.bind(this));
        }
    }

    togglePassword() {
        const passwordDisplay = document.getElementById('passwordDisplay');
        const passwordToggle = document.getElementById('passwordToggle');
        
        if (passwordDisplay.textContent === '••••••••••••') {
            passwordDisplay.textContent = this.currentData.password;
            passwordToggle.className = 'fas fa-eye-slash password-toggle ms-2';
            passwordToggle.title = 'Hide Password';
        } else {
            passwordDisplay.textContent = '••••••••••••';
            passwordToggle.className = 'fas fa-eye password-toggle ms-2';
            passwordToggle.title = 'Show Password';
        }
    }

    async connectToWiFi() {
        if (!this.currentData) return;

        const connectBtn = document.getElementById('connectBtn');
        const connectionStatus = document.getElementById('connectionStatus');
        
        const originalHtml = connectBtn.innerHTML;
        connectBtn.innerHTML = '<div class="spinner"></div><span class="loading-text">Connecting...</span>';
        connectBtn.disabled = true;

        try {
            const response = await fetch('/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ssid: this.currentData.ssid,
                    password: this.currentData.password,
                    security: this.currentData.security
                })
            });

            const result = await response.json();
            
            if (result.success) {
                connectionStatus.innerHTML = `
                    <div class="connection-status connection-success">
                        <i class="fas fa-check-circle me-2"></i>
                        <strong>Connected Successfully!</strong><br>
                        <small>${result.message}</small>
                    </div>
                `;
                this.showToast('success', 'Connected', `Successfully connected to ${this.currentData.ssid}`);
            } else {
                connectionStatus.innerHTML = `
                    <div class="connection-status connection-error">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Connection Failed</strong><br>
                        <small>${result.error}</small>
                    </div>
                `;
                this.showToast('error', 'Connection Failed', result.error);
            }

        } catch (error) {
            connectionStatus.innerHTML = `
                <div class="connection-status connection-error">
                    <i class="fas fa-times-circle me-2"></i>
                    <strong>Connection Error</strong><br>
                    <small>${error.message}</small>
                </div>
            `;
            this.showToast('error', 'Error', `Connection error: ${error.message}`);
        } finally {
            connectBtn.innerHTML = originalHtml;
            connectBtn.disabled = false;
        }
    }

    clearResultsHandler() {
        this.resultsCard.classList.add('d-none');
        this.currentData = null;
        this.fileInput.value = '';
    }

    showProgress() {
        this.uploadProgress.classList.remove('d-none');
        const progressBar = this.uploadProgress.querySelector('.progress-bar');
        progressBar.style.width = '100%';
    }

    hideProgress() {
        this.uploadProgress.classList.add('d-none');
        const progressBar = this.uploadProgress.querySelector('.progress-bar');
        progressBar.style.width = '0%';
    }

    showToast(type, title, message) {
        const toastIcon = document.getElementById('toastIcon');
        const toastTitle = document.getElementById('toastTitle');
        const toastMessage = document.getElementById('toastMessage');

        // Set icon and styling based on type
        const iconMap = {
            'success': 'fas fa-check-circle text-success',
            'error': 'fas fa-exclamation-circle text-danger',
            'warning': 'fas fa-exclamation-triangle text-warning',
            'info': 'fas fa-info-circle text-info'
        };

        toastIcon.className = iconMap[type] || iconMap.info;
        toastTitle.textContent = title;
        toastMessage.textContent = message;

        this.toast.show();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new WiFiQRScanner();
});
