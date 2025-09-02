#!/usr/bin/env python3
"""
Version standalone du scanner WiFi QR Code
Peut être compilée en .exe avec PyInstaller
"""

import cv2
import os
import sys
import platform
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zxingcpp
import re
import json
from typing import Dict, Any, Optional, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading

class WiFiQRScannerGUI:
    def __init__(self):
        self.scanner = WiFiQRScanner()
        self.setup_gui()
        
    def setup_gui(self):
        """Configure l'interface graphique"""
        self.root = tk.Tk()
        self.root.title("WiFi QR Code Scanner")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titre
        title_label = ttk.Label(main_frame, text="WiFi QR Code Scanner", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Boutons de scan
        scan_frame = ttk.LabelFrame(main_frame, text="Scanner", padding="10")
        scan_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(scan_frame, text="📁 Scan depuis fichier", 
                  command=self.scan_from_file).grid(row=0, column=0, padx=5)
        ttk.Button(scan_frame, text="📷 Scan webcam", 
                  command=self.scan_from_webcam).grid(row=0, column=1, padx=5)
        
        # Zone de résultats
        results_frame = ttk.LabelFrame(main_frame, text="Résultats", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        self.results_text = ScrolledText(results_frame, height=15, width=70)
        self.results_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bouton de connexion
        self.connect_btn = ttk.Button(main_frame, text="🔗 Connecter au WiFi", 
                                     command=self.connect_wifi, state='disabled')
        self.connect_btn.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Status bar
        self.status_var = tk.StringVar(value="Prêt")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Configuration des poids pour redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.current_wifi_data = None
        
    def scan_from_file(self):
        """Scan QR code depuis un fichier"""
        file_path = filedialog.askopenfilename(
            title="Sélectionner une image QR",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Tous", "*.*")
            ]
        )
        
        if file_path:
            self.status_var.set("Scan en cours...")
            self.root.update()
            
            result = self.scanner.scan_qr_from_image(file_path)
            self.display_result(result)
            
    def scan_from_webcam(self):
        """Scan QR code depuis la webcam"""
        self.status_var.set("Démarrage webcam...")
        self.root.update()
        
        # Lancer le scan webcam dans un thread séparé
        def webcam_thread():
            result = self.scanner.scan_qr_from_webcam(timeout=15)
            self.root.after(0, lambda: self.display_result(result))
            
        threading.Thread(target=webcam_thread, daemon=True).start()
        
    def display_result(self, result):
        """Affiche les résultats du scan"""
        self.results_text.delete(1.0, tk.END)
        
        if result['success']:
            self.current_wifi_data = result
            self.connect_btn.config(state='normal')
            
            output = f"✅ QR Code WiFi détecté !\n\n"
            output += f"📶 SSID: {result['ssid']}\n"
            output += f"🔐 Mot de passe: {result['password'] or 'Aucun'}\n"
            output += f"🛡️ Sécurité: {result['security']}\n"
            
            if result.get('hidden'):
                output += f"👁️ Réseau caché: Oui\n"
                
            output += f"📱 Méthode: {result.get('method', 'image')}\n"
            output += f"\n📋 Données brutes:\n{result.get('raw_data', 'N/A')}\n"
            
            self.status_var.set("QR Code détecté avec succès")
            
        else:
            self.current_wifi_data = None
            self.connect_btn.config(state='disabled')
            
            output = f"❌ Erreur de scan\n\n"
            output += f"Détails: {result.get('error', 'Erreur inconnue')}\n"
            
            if 'raw_data' in result:
                output += f"\n📋 Données détectées:\n{result['raw_data']}\n"
                
            self.status_var.set("Échec du scan")
            
        self.results_text.insert(tk.END, output)
        
    def connect_wifi(self):
        """Connecte au réseau WiFi"""
        if not self.current_wifi_data:
            return
            
        if not self.scanner.is_windows:
            messagebox.showwarning("Platform non supportée", 
                                 "La connexion automatique n'est disponible que sur Windows")
            return
            
        # Confirmation
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
        """Lance l'interface graphique"""
        self.root.mainloop()

class WiFiQRScanner:
    """WiFi QR Code Scanner avec intégration Windows netsh"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        
    def parse_wifi_qr(self, qr_data: str) -> Dict[str, Any]:
        """Parse les données QR WiFi"""
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
    
    def generate_wifi_profile_xml(self, ssid: str, password: str, security: str) -> str:
        """Génère le profil XML Windows WiFi"""
        root = ET.Element("WLANProfile")
        root.set("xmlns", "http://www.microsoft.com/networking/WLAN/profile/v1")
        
        name = ET.SubElement(root, "name")
        name.text = ssid
        
        ssid_config = ET.SubElement(root, "SSIDConfig")
        ssid_elem = ET.SubElement(ssid_config, "SSID")
        hex_elem = ET.SubElement(ssid_elem, "hex")
        hex_elem.text = ssid.encode('utf-8').hex().upper()
        name_elem = ET.SubElement(ssid_elem, "name")
        name_elem.text = ssid
        
        connection_type = ET.SubElement(root, "connectionType")
        connection_type.text = "ESS"
        
        connection_mode = ET.SubElement(root, "connectionMode")
        connection_mode.text = "auto"
        
        msm = ET.SubElement(root, "MSM")
        security_elem = ET.SubElement(msm, "security")
        
        if security.upper() == 'NOPASS':
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            authentication = ET.SubElement(auth_encryption, "authentication")
            authentication.text = "open"
            encryption = ET.SubElement(auth_encryption, "encryption")
            encryption.text = "none"
            use_one_x = ET.SubElement(auth_encryption, "useOneX")
            use_one_x.text = "false"
            
        elif security.upper() == 'WEP':
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            authentication = ET.SubElement(auth_encryption, "authentication")
            authentication.text = "open"
            encryption = ET.SubElement(auth_encryption, "encryption")
            encryption.text = "WEP"
            use_one_x = ET.SubElement(auth_encryption, "useOneX")
            use_one_x.text = "false"
            
            shared_key = ET.SubElement(security_elem, "sharedKey")
            key_type = ET.SubElement(shared_key, "keyType")
            key_type.text = "networkKey"
            protected = ET.SubElement(shared_key, "protected")
            protected.text = "false"
            key_material = ET.SubElement(shared_key, "keyMaterial")
            key_material.text = password
            
        else:
            auth_encryption = ET.SubElement(security_elem, "authEncryption")
            authentication = ET.SubElement(auth_encryption, "authentication")
            authentication.text = "WPA2PSK"
            encryption = ET.SubElement(auth_encryption, "encryption")
            encryption.text = "AES"
            use_one_x = ET.SubElement(auth_encryption, "useOneX")
            use_one_x.text = "false"
            
            shared_key = ET.SubElement(security_elem, "sharedKey")
            key_type = ET.SubElement(shared_key, "keyType")
            key_type.text = "passPhrase"
            protected = ET.SubElement(shared_key, "protected")
            protected.text = "false"
            key_material = ET.SubElement(shared_key, "keyMaterial")
            key_material.text = password
        
        ET.indent(root, space="  ")
        return ET.tostring(root, encoding='unicode', xml_declaration=True)
    
    def connect_to_wifi(self, ssid: str, password: str, security: str) -> Dict[str, Any]:
        """Connecte au réseau WiFi (Windows uniquement)"""
        if not self.is_windows:
            return {
                'success': False,
                'error': 'WiFi connection only supported on Windows',
                'platform': platform.system()
            }
        
        try:
            xml_profile = self.generate_wifi_profile_xml(ssid, password, security)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(xml_profile)
                temp_xml_path = temp_file.name
            
            try:
                add_cmd = f'netsh wlan add profile filename="{temp_xml_path}"'
                result = subprocess.run(add_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Failed to add profile: {result.stderr}',
                        'command': add_cmd
                    }
                
                connect_cmd = f'netsh wlan connect name="{ssid}"'
                result = subprocess.run(connect_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'error': f'Failed to connect: {result.stderr}',
                        'command': connect_cmd,
                        'profile_added': True
                    }
                
                return {
                    'success': True,
                    'message': f'Successfully connected to {ssid}',
                    'ssid': ssid,
                    'security': security
                }
                
            finally:
                try:
                    os.unlink(temp_xml_path)
                except:
                    pass
                    
        except Exception as e:
            return {
                'success': False,
                'error': f'Connection failed: {str(e)}'
            }
    
    def scan_qr_from_image(self, image_path: str) -> Dict[str, Any]:
        """Scan QR code depuis une image"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image file")
            
            qr_codes = zxingcpp.read_barcodes(image)
            
            if not qr_codes:
                return {
                    'success': False,
                    'error': 'No QR codes found in image'
                }
            
            qr_data = qr_codes[0].text
            wifi_data = self.parse_wifi_qr(qr_data)
            
            if wifi_data['success']:
                wifi_data['method'] = 'image'
                wifi_data['qr_count'] = len(qr_codes)
            
            return wifi_data
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Image scanning failed: {str(e)}'
            }
    
    def scan_qr_from_webcam(self, timeout: int = 15) -> Dict[str, Any]:
        """Scan QR code depuis la webcam"""
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
                
                qr_codes = zxingcpp.read_barcodes(frame)
                
                if qr_codes:
                    qr_data = qr_codes[0].text
                    cap.release()
                    
                    wifi_data = self.parse_wifi_qr(qr_data)
                    if wifi_data['success']:
                        wifi_data['method'] = 'webcam'
                        wifi_data['frames_processed'] = frame_count
                    
                    return wifi_data
                
                frame_count += 1
            
            cap.release()
            return {
                'success': False,
                'error': f'No QR code found within {timeout} seconds'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Webcam scanning failed: {str(e)}'
            }

class WiFiQRScanner:
    """Version simplifiée pour import"""
    
    def __init__(self):
        self.is_windows = platform.system() == 'Windows'
        
    def parse_wifi_qr(self, qr_data: str) -> Dict[str, Any]:
        gui_scanner = WiFiQRScannerGUI()
        return gui_scanner.scanner.parse_wifi_qr(qr_data)
        
    def scan_qr_from_image(self, image_path: str) -> Dict[str, Any]:
        gui_scanner = WiFiQRScannerGUI()
        return gui_scanner.scanner.scan_qr_from_image(image_path)
        
    def scan_qr_from_webcam(self, timeout: int = 15) -> Dict[str, Any]:
        gui_scanner = WiFiQRScannerGUI()
        return gui_scanner.scanner.scan_qr_from_webcam(timeout)
        
    def connect_to_wifi(self, ssid: str, password: str, security: str) -> Dict[str, Any]:
        gui_scanner = WiFiQRScannerGUI()
        return gui_scanner.scanner.connect_to_wifi(ssid, password, security)

def main():
    """Fonction principale - lance l'interface graphique"""
    try:
        app = WiFiQRScannerGUI()
        app.run()
    except KeyboardInterrupt:
        print("Application fermée par l'utilisateur")
    except Exception as e:
        print(f"Erreur: {e}")
        input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    main()