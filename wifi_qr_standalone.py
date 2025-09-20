#!/usr/bin/env python3
"""
Scanner et générateur WiFi QR Code
GUI Tkinter + pyzbar pour lecture + qrcode pour génération
Compatible Windows et PyInstaller (.exe)
"""

import os
import platform
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText

from PIL import Image, ImageTk
import qrcode
import cv2
from pyzbar.pyzbar import decode

# --- Récupération SSID et mot de passe ---
def get_wifi_credentials():
    """Récupère le SSID et le mot de passe du WiFi actuel (Windows)."""
    try:
        ssid_result = subprocess.run(
            ['netsh', 'wlan', 'show', 'interfaces'],
            capture_output=True, text=True
        )
        ssid = None
        for line in ssid_result.stdout.split('\n'):
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                break
        if not ssid:
            return None, None

        pw_result = subprocess.run(
            ['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'],
            capture_output=True, text=True
        )
        password = None
        for line in pw_result.stdout.split('\n'):
            if "Key Content" in line:
                password = line.split(":")[1].strip()
                break
        return ssid, password
    except Exception as e:
        print(f"Erreur récupération WiFi : {e}")
        return None, None

# --- Classe Scanner ---
class WiFiQRScanner:
    """Scanner QR Code WiFi avec pyzbar et connexion Windows"""
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'

    def parse_wifi_qr(self, qr_data: str):
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
            return {'success': False, 'error': str(e), 'raw_data': qr_data}

    def scan_qr_from_image(self, image_path: str):
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            image = Image.open(image_path)
            decoded = decode(image)
            if not decoded:
                return {'success': False, 'error': 'No QR codes found in image'}
            qr_data = decoded[0].data.decode('utf-8')
            wifi_data = self.parse_wifi_qr(qr_data)
            if wifi_data['success']:
                wifi_data['method'] = 'image'
            return wifi_data
        except Exception as e:
            return {'success': False, 'error': f'Image scanning failed: {str(e)}'}

    def scan_qr_from_webcam(self, timeout: int = 15):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise RuntimeError("Could not open webcam")
            import time
            start_time = time.time()
            while time.time() - start_time < timeout:
                ret, frame = cap.read()
                if not ret:
                    continue
                decoded = decode(frame)
                if decoded:
                    qr_data = decoded[0].data.decode('utf-8')
                    cap.release()
                    wifi_data = self.parse_wifi_qr(qr_data)
                    if wifi_data['success']:
                        wifi_data['method'] = 'webcam'
                    return wifi_data
            cap.release()
            return {'success': False, 'error': f'No QR code found within {timeout} seconds'}
        except Exception as e:
            return {'success': False, 'error': f'Webcam scanning failed: {str(e)}'}

    def generate_wifi_profile_xml(self, ssid: str, password: str, security: str):
        root = ET.Element("WLANProfile")
        root.set("xmlns", "http://www.microsoft.com/networking/WLAN/profile/v1")
        ET.SubElement(root, "name").text = ssid
        ssid_config = ET.SubElement(root, "SSIDConfig")
        ssid_elem = ET.SubElement(ssid_config, "SSID")
        ET.SubElement(ssid_elem, "hex").text = ssid.encode('utf-8').hex().upper()
        ET.SubElement(ssid_elem, "name").text = ssid
        ET.SubElement(root, "connectionType").text = "ESS"
        ET.SubElement(root, "connectionMode").text = "auto"
        msm = ET.SubElement(root, "MSM")
        security_elem = ET.SubElement(msm, "security")
        if security.lower() == 'nopass':
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            ET.SubElement(auth_encryption, "authentication").text = "open"
            ET.SubElement(auth_encryption, "encryption").text = "none"
            ET.SubElement(auth_encryption, "useOneX").text = "false"
        elif security.upper() == 'WEP':
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            ET.SubElement(auth_encryption, "authentication").text = "open"
            ET.SubElement(auth_encryption, "encryption").text = "WEP"
            ET.SubElement(auth_encryption, "useOneX").text = "false"
            shared_key = ET.SubElement(security_elem, "sharedKey")
            ET.SubElement(shared_key, "keyType").text = "networkKey"
            ET.SubElement(shared_key, "protected").text = "false"
            ET.SubElement(shared_key, "keyMaterial").text = password
        else:
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            ET.SubElement(auth_encryption, "authentication").text = "WPA2PSK"
            ET.SubElement(auth_encryption, "encryption").text = "AES"
            ET.SubElement(auth_encryption, "useOneX").text = "false"
            shared_key = ET.SubElement(security_elem, "sharedKey")
            ET.SubElement(shared_key, "keyType").text = "passPhrase"
            ET.SubElement(shared_key, "protected").text = "false"
            ET.SubElement(shared_key, "keyMaterial").text = password
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding='unicode', xml_declaration=True)

    def connect_to_wifi(self, ssid: str, password: str, security: str):
        if not self.is_windows:
            return {'success': False, 'error': 'Only Windows supported'}
        try:
            xml_profile = self.generate_wifi_profile_xml(ssid, password, security)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(xml_profile)
                temp_xml_path = temp_file.name
            try:
                result = subprocess.run(f'netsh wlan add profile filename="{temp_xml_path}"',
                                        shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {'success': False, 'error': result.stderr}
                result = subprocess.run(f'netsh wlan connect name="{ssid}"',
                                        shell=True, capture_output=True, text=True)
                if result.returncode != 0:
                    return {'success': False, 'error': result.stderr}
                return {'success': True, 'message': f'Connecté à {ssid}', 'ssid': ssid}
            finally:
                os.unlink(temp_xml_path)
        except Exception as e:
            return {'success': False, 'error': str(e)}

# --- Classe GUI ---
class WiFiQRScannerGUI:
    def __init__(self):
        self.scanner = WiFiQRScanner()
        self.qr_image = None
        self.current_wifi_data = None
        self.setup_gui()
        self.generate_qr_code()

    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("WiFi QR Code Scanner")
        self.root.geometry("600x650")
        self.root.resizable(True, True)

        style = ttk.Style()
        style.theme_use('clam')

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        title_label = ttk.Label(main_frame, text="WiFi QR Code Scanner",
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        qr_frame = ttk.LabelFrame(main_frame, text="QR Code de votre WiFi", padding="10")
        qr_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        self.qr_label = ttk.Label(qr_frame)
        self.qr_label.grid(row=0, column=0)

        scan_frame = ttk.LabelFrame(main_frame, text="Scanner", padding="10")
        scan_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        ttk.Button(scan_frame, text="📁 Scan depuis fichier",
                  command=self.scan_from_file).grid(row=0, column=0, padx=5)
        ttk.Button(scan_frame, text="📷 Scan webcam",
                  command=self.scan_from_webcam).grid(row=0, column=1, padx=5)

        results_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="10")
        results_frame.grid(row=3, column=0, columnspan=2,
                           sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.results_text = ScrolledText(results_frame, height=15, width=70)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.connect_btn = ttk.Button(main_frame, text="🔗 Connecter au WiFi",
                                     command=self.connect_wifi, state='disabled')
        self.connect_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                               relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

    def generate_qr_code(self):
        ssid, password = get_wifi_credentials()
        if ssid and password:
            wifi_string = f"WIFI:T:WPA;S:{ssid};P:{password};;"
            qr = qrcode.QRCode(version=1, box_size=10, border=4)
            qr.add_data(wifi_string)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img = img.resize((200, 200))
            self.qr_image = ImageTk.PhotoImage(img)
            self.qr_label.config(image=self.qr_image)
            self.status_var.set(f"QR Code généré pour le réseau {ssid}")
            # Sauvegarde locale
            img.save("wifi_qr.png")
        else:
            self.status_var.set("❌ Impossible de générer le QR (pas de SSID/mot de passe trouvé)")

    def scan_from_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image QR",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp"), ("Tous", "*.*")]
        )
        if file_path:
            self.status_var.set("Scan en cours...")
            self.root.update()
            result = self.scanner.scan_qr_from_image(file_path)
            self.display_result(result)

    def scan_from_webcam(self):
        self.status_var.set("Démarrage webcam...")
        self.root.update()
        def webcam_thread():
            result = self.scanner.scan_qr_from_webcam(timeout=15)
            self.root.after(0, lambda: self.display_result(result))
        threading.Thread(target=webcam_thread, daemon=True).start()

    def display_result(self, result):
        self.results_text.delete(1.0, tk.END)
        if result['success']:
            self.current_wifi_data = result
            self.connect_btn.config(state='normal')
            output = (
                f"✅ QR Code WiFi détecté !\n\n"
                f"📶 SSID: {result['ssid']}\n"
                f"🔐 Mot de passe: {result['password'] or 'Aucun'}\n"
                f"🛡️ Sécurité: {result['security']}\n"
                f"👁️ Réseau caché: {'Oui' if result.get('hidden') else 'Non'}\n"
                f"📱 Méthode: {result.get('method', 'image')}\n"
                f"\n📋 Données brutes:\n{result.get('raw_data', 'N/A')}\n"
            )
            self.status_var.set("QR Code détecté avec succès")
        else:
            self.current_wifi_data = None
            self.connect_btn.config(state='disabled')
            output = f"❌ Erreur de scan\n\nDétails: {result.get('error', 'Erreur inconnue')}\n"
            self.status_var.set("Échec du scan")
        self.results_text.insert(tk.END, output)

    def connect_wifi(self):
        if not self.current_wifi_data:
            return
        if not self.scanner.is_windows:
            messagebox.showwarning("Platform non supportée",
                                   "Connexion auto dispo uniquement sur Windows")
            return
        response = messagebox.askyesno(
            "Connexion WiFi",
            f"Se connecter au réseau '{self.current_wifi_data['ssid']}' ?\n\n"
            f"Mot de passe: {self.current_wifi_data['password'] or 'Aucun'}\n"
            f"Sécurité: {self.current_wifi_data['security']}"
        )
        if response:
            self.status_var.set("Connexion en cours...")
            self.root.update()
            result = self.scanner.connect_to_wifi(
                self.current_wifi_data['ssid'],
                self.current_wifi_data['password'],
                self.current_wifi_data['security']
            )
            if result['success']:
                messagebox.showinfo("Succès", result['message'])
                self.status_var.set("Connecté avec succès")
            else:
                messagebox.showerror("Erreur", f"Connexion échouée:\n{result['error']}")
                self.status_var.set("Échec de la connexion")

    def run(self):
        self.root.mainloop()

# --- Main ---
def main():
    app = WiFiQRScannerGUI()
    app.run()

if __name__ == "__main__":
    main()
