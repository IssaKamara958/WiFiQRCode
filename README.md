# WiFi QR Code Scanner

Une application web Flask moderne pour scanner les QR codes Wi-Fi et se connecter automatiquement aux réseaux sans fil.

## 🚀 Fonctionnalités

- **Scan d'images** : Uploadez une image contenant un QR code Wi-Fi
- **Interface glisser-déposer** : Interface intuitive avec drag-and-drop
- **Scan webcam** : Scan en temps réel via webcam (local uniquement)
- **Connexion automatique** : Connexion automatique au Wi-Fi sur Windows
- **Interface moderne** : Design responsive avec Bootstrap 5
- **Notifications en temps réel** : Feedback instantané avec des toasts
- **Support multi-formats** : PNG, JPG, JPEG, GIF, BMP, WebP

## 📋 Prérequis

- Python 3.11+
- Système d'exploitation : Linux/Windows/macOS
- Pour la connexion automatique : Windows uniquement

## 🛠️ Installation

### Sur Replit (Recommandé pour le développement)

1. Clonez ce projet dans Replit
2. Les dépendances s'installent automatiquement
3. Lancez l'application avec le bouton "Run"

### Installation locale

1. Clonez le repository :
```bash
git clone <votre-repo>
cd wifi-qr-scanner
```

2. Installez les dépendances Python :
```bash
pip install flask opencv-python zxing-cpp werkzeug
```

3. Pour Windows, assurez-vous d'avoir les droits administrateur pour la connexion Wi-Fi.

## 🚀 Utilisation

### Démarrage de l'application

```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

### Utilisation de l'interface web

1. **Upload d'image** :
   - Glissez-déposez une image contenant un QR code Wi-Fi
   - Ou cliquez sur la zone de upload pour sélectionner un fichier
   - L'application analysera automatiquement le QR code

2. **Scan webcam** (local uniquement) :
   - Cliquez sur "Scan with Webcam"
   - Présentez le QR code devant la caméra
   - La détection se fait automatiquement

3. **Connexion Wi-Fi** :
   - Une fois le QR code scanné, les informations du réseau s'affichent
   - Sur Windows, cliquez sur "Connect Now" pour se connecter automatiquement
   - Les informations incluent : SSID, mot de passe, type de sécurité

## 📱 Format des QR Codes Wi-Fi

L'application supporte le format standard des QR codes Wi-Fi :

```
WIFI:T:[type de sécurité];S:[nom du réseau];P:[mot de passe];;
```

### Exemples :
- **WPA/WPA2** : `WIFI:T:WPA;S:MonReseau;P:MotDePasse123;;`
- **Réseau ouvert** : `WIFI:T:nopass;S:ReseauOuvert;P:;;`
- **WEP** : `WIFI:T:WEP;S:ReseauWEP;P:MotDePasse;;`

### Générateurs de QR codes Wi-Fi recommandés :
- [QR Code Generator](https://www.qr-code-generator.com/)
- [WiFi QR Code Generator](https://qifi.org/)

## 🏗️ Architecture Technique

### Backend (Flask)
- **app.py** : Serveur principal Flask avec routes API
- **wifi_scanner.py** : Classe de traitement des QR codes et connexion Wi-Fi
- **Endpoints** :
  - `GET /` : Page principale
  - `POST /upload` : Upload et analyse d'images
  - `POST /scan_webcam` : Scan webcam (local)
  - `POST /connect` : Connexion Wi-Fi Windows
  - `GET /health` : Vérification de santé

### Frontend (JavaScript/Bootstrap)
- **Interface responsive** : Bootstrap 5 avec design moderne
- **Gestion des fichiers** : Drag-and-drop natif
- **Notifications** : Système de toasts Bootstrap
- **État en temps réel** : Feedback visuel des opérations

### Traitement des QR Codes
- **Bibliothèque** : zxing-cpp (plus fiable que pyzbar)
- **Formats supportés** : Tous les formats d'images standards
- **Parsing** : Analyse complète du format WIFI: avec gestion des caractères échappés

### Connexion Wi-Fi (Windows)
- **Méthode** : Commandes netsh via subprocess
- **Profils XML** : Génération automatique de profils Windows
- **Types de sécurité** : WPA/WPA2/WPA3, WEP, Open/None

## 📁 Structure du Projet

```
wifi-qr-scanner/
├── app.py                  # Application Flask principale
├── wifi_scanner.py         # Classe de scanner QR Wi-Fi
├── templates/
│   └── index.html         # Interface utilisateur HTML
├── static/
│   ├── style.css          # Styles CSS personnalisés
│   └── script.js          # Logique JavaScript frontend
├── uploads/               # Dossier temporaire pour les uploads
├── replit.md             # Documentation du projet
└── README.md             # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement

- `SECRET_KEY` : Clé secrète Flask (optionnelle, valeur par défaut fournie)

### Paramètres modifiables dans app.py

```python
UPLOAD_FOLDER = 'uploads'                    # Dossier d'upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024       # Taille max : 16MB
```

## 🧪 Tests et Développement

### Test de l'analyseur QR

```python
python wifi_scanner.py
```

Cela exécute les tests intégrés avec un QR code d'exemple.

### Test de l'API

```bash
# Test de santé
curl http://localhost:5000/health

# Test d'upload (avec un fichier QR)
curl -X POST -F "file=@test_qr.png" http://localhost:5000/upload
```

## 🔒 Sécurité

### Mesures de sécurité implémentées :

- **Validation des fichiers** : Seuls les formats d'images autorisés
- **Noms de fichiers sécurisés** : werkzeug.secure_filename
- **Identifiants uniques** : UUID pour éviter les conflits
- **Limite de taille** : Maximum 16MB par fichier
- **Nettoyage automatique** : Suppression des fichiers temporaires
- **Validation côté serveur** : Vérification de tous les contenus uploadés

### Recommandations de sécurité :

- Exécutez en mode administrateur sur Windows pour la connexion Wi-Fi
- Ne déployez pas en production sans HTTPS
- Utilisez un serveur WSGI (Gunicorn, uWSGI) pour la production

## 🌐 Déploiement

### Déploiement Replit

L'application est déjà configurée pour Replit. Utilisez simplement le bouton "Deploy" dans l'interface Replit.

### Déploiement local Windows

1. Téléchargez le code depuis Replit
2. Installez Python 3.11+ et les dépendances
3. Exécutez en tant qu'administrateur :
```bash
python app.py
```

### Compilation en .exe (Windows)

Pour créer un exécutable standalone :

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "templates;templates" --add-data "static;static" app.py
```

L'exécutable sera dans le dossier `dist/`.

## 📊 API Documentation

### POST /upload
Analyse un QR code depuis une image uploadée.

**Request :**
```
Content-Type: multipart/form-data
file: [fichier image]
```

**Response :**
```json
{
  "success": true,
  "ssid": "NomDuReseau",
  "password": "MotDePasse",
  "security": "WPA",
  "hidden": false,
  "method": "image",
  "raw_data": "WIFI:T:WPA;S:NomDuReseau;P:MotDePasse;;"
}
```

### POST /connect
Connecte au réseau Wi-Fi (Windows uniquement).

**Request :**
```json
{
  "ssid": "NomDuReseau",
  "password": "MotDePasse",
  "security": "WPA"
}
```

**Response :**
```json
{
  "success": true,
  "message": "Successfully connected to NomDuReseau",
  "ssid": "NomDuReseau",
  "security": "WPA"
}
```

## 🐛 Dépannage

### Problèmes courants

**Erreur "No QR codes found"**
- Vérifiez que l'image est nette et bien cadrée
- Assurez-vous que le QR code est au format WIFI:
- Essayez d'augmenter la taille de l'image

**Erreur de connexion Wi-Fi**
- Vérifiez que vous êtes sur Windows
- Exécutez en tant qu'administrateur
- Vérifiez que le réseau est disponible

**Erreur de webcam**
- La webcam ne fonctionne qu'en local (pas dans Replit)
- Vérifiez les permissions de la caméra
- Assurez-vous qu'aucune autre application n'utilise la webcam

### Logs de débogage

Les logs détaillés sont disponibles dans la console Flask lors de l'exécution.

## 🤝 Contribution

Pour contribuer au projet :

1. Forkez le repository
2. Créez une branche pour votre fonctionnalité
3. Commitez vos changements
4. Poussez vers la branche
5. Ouvrez une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- **OpenCV** : Traitement d'images
- **zxing-cpp** : Décodage QR codes fiable
- **Flask** : Framework web Python
- **Bootstrap** : Framework CSS moderne
- **Font Awesome** : Icônes de qualité

## 📞 Support

Pour toute question ou problème :
- Ouvrez une issue sur GitHub
- Consultez la documentation technique dans `replit.md`
- Vérifiez les logs de la console pour les erreurs détaillées

---

**Développé avec ❤️ et l'aide de l'IA Replit**