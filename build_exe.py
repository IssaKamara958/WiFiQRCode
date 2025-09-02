#!/usr/bin/env python3
"""
Script de compilation pour créer un exécutable Windows (.exe) 
du scanner de QR code Wi-Fi.

Usage:
    python build_exe.py

Prérequis:
    pip install pyinstaller flask opencv-python zxing-cpp werkzeug

Le fichier .exe sera créé dans le dossier dist/
"""

import subprocess
import sys
import os
import shutil

def install_pyinstaller():
    """Installe PyInstaller si nécessaire"""
    try:
        import PyInstaller
        print("✓ PyInstaller déjà installé")
    except ImportError:
        print("📦 Installation de PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller installé avec succès")

def clean_build_folders():
    """Nettoie les dossiers de build précédents"""
    folders_to_clean = ['build', 'dist', '__pycache__']
    for folder in folders_to_clean:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"🧹 Dossier {folder} nettoyé")

def build_executable():
    """Compile l'application en exécutable"""
    print("🔨 Compilation de l'exécutable...")
    
    # Commande PyInstaller
    cmd = [
        "pyinstaller",
        "--onefile",                    # Un seul fichier exe
        "--windowed",                   # Pas de console (pour interface graphique)
        "--name=WiFiQRScanner",        # Nom de l'exécutable
        "--add-data=templates;templates",  # Inclure templates
        "--add-data=static;static",        # Inclure static
        "--add-data=uploads;uploads",      # Inclure uploads
        "--icon=static/favicon.ico",       # Icône (optionnel)
        "--clean",                         # Nettoyer avant build
        "app.py"                          # Fichier principal
    ]
    
    # Retirer l'icône si elle n'existe pas
    if not os.path.exists("static/favicon.ico"):
        cmd = [c for c in cmd if not c.startswith("--icon")]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Compilation réussie !")
        print(f"📁 Exécutable créé : dist/WiFiQRScanner.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur de compilation :")
        print(f"Stdout: {e.stdout}")
        print(f"Stderr: {e.stderr}")
        return False

def create_launcher_script():
    """Crée un script de lancement simplifié"""
    launcher_content = '''#!/usr/bin/env python3
"""
Lanceur simple pour le scanner QR Wi-Fi
Usage direct sans serveur web
"""

import sys
import os
import tempfile
from wifi_scanner import WiFiQRScanner

def main():
    print("=== WiFi QR Code Scanner ===")
    print("1. Scan depuis un fichier image")
    print("2. Scan depuis la webcam")
    
    choice = input("Choisissez une option (1 ou 2): ").strip()
    
    scanner = WiFiQRScanner()
    
    if choice == "1":
        # Scan depuis fichier
        image_path = input("Chemin vers l'image QR: ").strip()
        if not os.path.exists(image_path):
            print(f"❌ Fichier non trouvé: {image_path}")
            return
        
        result = scanner.scan_qr_from_image(image_path)
        
    elif choice == "2":
        # Scan webcam
        print("📷 Démarrage de la webcam... Présentez le QR code")
        result = scanner.scan_qr_from_webcam(timeout=10)
        
    else:
        print("❌ Option invalide")
        return
    
    # Afficher résultats
    if result['success']:
        print("\\n✅ QR Code Wi-Fi détecté !")
        print(f"📶 SSID: {result['ssid']}")
        print(f"🔐 Mot de passe: {result['password'] or 'Aucun'}")
        print(f"🛡️ Sécurité: {result['security']}")
        
        # Demander connexion
        if scanner.is_windows:
            connect = input("\\nSe connecter maintenant ? (o/n): ").strip().lower()
            if connect in ['o', 'oui', 'y', 'yes']:
                conn_result = scanner.connect_to_wifi(
                    result['ssid'], 
                    result['password'], 
                    result['security']
                )
                if conn_result['success']:
                    print(f"✅ {conn_result['message']}")
                else:
                    print(f"❌ {conn_result['error']}")
        else:
            print("ℹ️ Connexion automatique disponible sur Windows uniquement")
    else:
        print(f"❌ Erreur: {result['error']}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    
    input("\\nAppuyez sur Entrée pour fermer...")
'''
    
    with open("launcher.py", "w", encoding="utf-8") as f:
        f.write(launcher_content)
    
    print("📄 Script launcher.py créé")

def main():
    """Fonction principale de compilation"""
    print("🚀 Préparation de la compilation pour exécutable...")
    
    # Vérifier que nous sommes dans le bon dossier
    required_files = ["app.py", "wifi_scanner.py", "templates", "static"]
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Fichiers manquants: {missing_files}")
        print("Assurez-vous d'être dans le dossier du projet")
        return False
    
    # Nettoyer
    clean_build_folders()
    
    # Installer PyInstaller
    install_pyinstaller()
    
    # Créer le launcher
    create_launcher_script()
    
    # Compiler
    success = build_executable()
    
    if success:
        print("\n🎉 Compilation terminée avec succès !")
        print("\n📋 Instructions pour l'utilisation :")
        print("1. Copiez le dossier 'dist' sur votre PC Windows")
        print("2. Exécutez WiFiQRScanner.exe en tant qu'administrateur")
        print("3. Uploadez des images QR ou utilisez la webcam")
        print("\n💡 Alternative : Utilisez 'python launcher.py' pour une version console simple")
    else:
        print("\n❌ Échec de la compilation")
        print("Vérifiez les erreurs ci-dessus et réessayez")
    
    return success

if __name__ == "__main__":
    main()