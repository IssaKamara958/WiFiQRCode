import subprocess
import qrcode

# Récupère le SSID du réseau actuel
ssid_result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], capture_output=True, text=True)
for line in ssid_result.stdout.split('\n'):
    if "SSID" in line and "BSSID" not in line:
        ssid = line.split(":")[1].strip()

# Récupère le mot de passe du réseau actuel
pw_result = subprocess.run(['netsh', 'wlan', 'show', 'profile', ssid, 'key=clear'], capture_output=True, text=True)
for line in pw_result.stdout.split('\n'):
    if "Key Content" in line:
        password = line.split(":")[1].strip()

# Encode WiFi dans le format QR
wifi_qr_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"

# Génère le QR code
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(wifi_qr_data)
qr.make(fit=True)
img = qr.make_image(fill='black', back_color='white')
img.save("wifi_qr.png")
print("QR code généré avec succès !")
