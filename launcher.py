#!/usr/bin/env python3
"""
Lanceur simple pour le scanner QR Wi-Fi
Version console standalone
"""

import sys
import os
import tempfile
from wifi_scanner import WiFiQRScanner

def main():
    print("=== WiFi QR Code Scanner ===")
    print("1. Scan depuis un fichier image")
    print("2. Scan depuis la webcam")
    print("3. Lancer le serveur web")
    
    choice = input("Choisissez une option (1, 2 ou 3): ").strip()
    
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
        print("Appuyez sur Ctrl+C pour arrêter")
        result = scanner.scan_qr_from_webcam(timeout=30)
        
    elif choice == "3":
        # Lancer le serveur web
        print("🌐 Démarrage du serveur web...")
        print("Ouvrez http://localhost:5000 dans votre navigateur")
        os.system("python app.py")
        return
        
    else:
        print("❌ Option invalide")
        return
    
    # Afficher résultats
    if result['success']:
        print("\n✅ QR Code Wi-Fi détecté !")
        print(f"📶 SSID: {result['ssid']}")
        print(f"🔐 Mot de passe: {result['password'] or 'Aucun'}")
        print(f"🛡️ Sécurité: {result['security']}")
        
        # Demander connexion
        if scanner.is_windows:
            connect = input("\nSe connecter maintenant ? (o/n): ").strip().lower()
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
        print("\n👋 Au revoir !")
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
    
    input("\nAppuyez sur Entrée pour fermer...")