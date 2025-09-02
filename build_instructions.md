# Instructions de Compilation en Exécutable

## Pour Windows (.exe)

### Prérequis sur votre PC Windows :
1. Python 3.8+ installé
2. Droits administrateur

### Étapes de compilation :

1. **Téléchargez le projet depuis Replit :**
   - Cliquez sur "Download as ZIP" dans Replit
   - Extraire sur votre PC Windows

2. **Installez les dépendances :**
   ```cmd
   pip install flask opencv-python zxing-cpp werkzeug pyinstaller
   ```

3. **Compilez l'exécutable :**
   ```cmd
   python build_exe.py
   ```

4. **Résultat :**
   - L'exécutable `WiFiQRScanner.exe` sera dans le dossier `dist/`
   - Exécutez-le en tant qu'administrateur pour la connexion Wi-Fi

### Options d'utilisation :

**Option 1 : Interface Web (recommandée)**
- Double-cliquez sur `WiFiQRScanner.exe`
- Ouvrez http://localhost:5000 dans votre navigateur

**Option 2 : Version Console**
- Exécutez `launcher.py` pour une interface console simple
- Choix entre fichier image ou webcam

### Dépannage :

- **Erreur "Module not found"** : Réinstallez les dépendances
- **Erreur webcam** : Vérifiez les permissions caméra Windows
- **Erreur netsh** : Exécutez en tant qu'administrateur
- **QR non détecté** : Vérifiez que l'image est nette et au bon format

### Test avant compilation :
```cmd
python launcher.py
```
Testez avec l'image `test_qr.png` fournie.