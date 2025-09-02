import cv2
import os
import sys
import platform
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import re
import json
from typing import Dict, Any

from pyzbar.pyzbar import decode  # Remplace zxingcpp

class WiFiQRScanner:
    """WiFi QR Code Scanner with Windows netsh integration"""

    def __init__(self):
        self.is_windows = platform.system() == 'Windows'

    def parse_wifi_qr(self, qr_data: str) -> Dict[str, Any]:
        """Parse WiFi QR code data in format: WIFI:T:WPA;S:NetworkName;P:Password;;"""
        try:
            if not qr_data.startswith('WIFI:'):
                raise ValueError("Not a WiFi QR code")
            wifi_data = qr_data[5:]
            components = {}
            current_key = None
            current_value = ""
            i = 0
            while i < len(wifi_data):
                char = wifi_data[i]
                if char == ':' and current_key is None:
                    current_key = current_value
                    current_value = ""
                elif char == ';':
                    if current_key:
                        components[current_key] = current_value
                        current_key = None
                        current_value = ""
                elif char == '\\' and i + 1 < len(wifi_data):
                    next_char = wifi_data[i + 1]
                    if next_char in [';', ':', ',', '\\', '"']:
                        current_value += next_char
                        i += 1
                    else:
                        current_value += char
                else:
                    current_value += char
                i += 1
            if current_key and current_value:
                components[current_key] = current_value

            ssid = components.get('S', '').strip()
            password = components.get('P', '').strip()
            security = components.get('T', 'WPA').strip().upper()
            hidden = components.get('H', 'false').strip().lower() == 'true'

            if not ssid:
                raise ValueError("No SSID found in QR code")

            if security in ['WPA', 'WPA2', 'WPA3']:
                security = 'WPA'
            elif security == 'WEP':
                security = 'WEP'
            elif security in ['', 'NONE', 'NOPASS']:
                security = 'nopass'
                password = ''

            return {
                'success': True,
                'ssid': ssid,
                'password': password,
                'security': security,
                'hidden': hidden,
                'raw_data': qr_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to parse WiFi QR code: {str(e)}",
                'raw_data': qr_data
            }

    # Garde les fonctions generate_wifi_profile_xml et connect_to_wifi telles quelles
    # ...

    def scan_qr_from_image(self, image_path: str) -> Dict[str, Any]:
        """Scan QR code from image file"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image file")

            decoded_objects = decode(image)
            if not decoded_objects:
                return {'success': False, 'error': 'No QR codes found in image'}

            qr_data = decoded_objects[0].data.decode('utf-8')
            wifi_data = self.parse_wifi_qr(qr_data)
            if wifi_data['success']:
                wifi_data['method'] = 'image'
                wifi_data['qr_count'] = len(decoded_objects)
            return wifi_data
        except Exception as e:
            return {'success': False, 'error': f'Image scanning failed: {str(e)}'}

    def scan_qr_from_webcam(self, timeout: int = 30) -> Dict[str, Any]:
        """Scan QR code from webcam"""
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("Could not open webcam")
            frame_count = 0
            max_frames = timeout * 10
            while frame_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    continue
                decoded_objects = decode(frame)
                if decoded_objects:
                    qr_data = decoded_objects[0].data.decode('utf-8')
                    cap.release()
                    cv2.destroyAllWindows()
                    wifi_data = self.parse_wifi_qr(qr_data)
                    if wifi_data['success']:
                        wifi_data['method'] = 'webcam'
                        wifi_data['frames_processed'] = frame_count
                    return wifi_data
                frame_count += 1
            cap.release()
            cv2.destroyAllWindows()
            return {'success': False, 'error': f'No QR code found within {timeout} seconds'}
        except Exception as e:
            return {'success': False, 'error': f'Webcam scanning failed: {str(e)}'}
