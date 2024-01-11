# ReadMe für PlantPiDrizzle - IoT Pflanzenbewässerungssystem

## Projektübersicht
PlantPiDrizzle ist ein innovatives IoT (Internet der Dinge) Projekt, das darauf abzielt, das Problem der regelmäßigen und effizienten Pflanzenbewässerung zu lösen. Unter Verwendung eines Raspberry Pi, eines Feuchtigkeitssensors und einer Wasserpumpe, ermöglicht dieses System die automatisierte Bewässerung Ihrer Pflanze, basierend auf dem gemessenen Feuchtigkeitsgehalt des Bodens.

## Zielsetzung
Das Hauptziel von PlantPiDrizzle ist es, eine zuverlässige und benutzerfreundliche Lösung für die Pflanzenpflege zu bieten, insbesondere für Menschen, die oft unterwegs sind oder die regelmäßige Bewässerung vergessen. Mit der Integration in ein IoT-Ökosystem bietet das Projekt eine smarte und vernetzte Lösung, die ferngesteuerte Überwachung und Bewässerung ermöglicht.

## Voraussetzungen
- Raspberry Pi (mit Raspbian OS)
- Python 3
- MongoDB-Konto
- Telegram-Bot-Token und Chat-ID
- Bibliotheken: Spidev, RPi.GPIO, Pymongo, Requests, Logging

## Einrichtung einer virtuellen Umgebung (venv)
Um Konflikte mit anderen Python-Projekten zu vermeiden, ist es empfehlenswert, PlantPiDrizzle in einer virtuellen Umgebung (venv) zu betreiben:

1. **Virtuelle Umgebung erstellen:**
   Navigieren Sie im Terminal zu Ihrem Projektverzeichnis und erstellen Sie eine neue virtuelle Umgebung mit:
   ```bash
   python3 -m venv plantpidrizzle_venv
   ```

2. **Virtuelle Umgebung aktivieren:**
   Aktivieren Sie die virtuelle Umgebung mit:
   ```bash
   source plantpidrizzle_venv/bin/activate
   ```

3. **Installation der erforderlichen Pakete:**
   Installieren Sie die benötigten Pakete innerhalb der virtuellen Umgebung:
   ```bash
   pip3 install spidev RPi.GPIO pymongo requests
   ```

### PlantPiDrizzle im venv ausführen
Nachdem die virtuelle Umgebung eingerichtet und aktiviert ist, führen Sie das PlantPiDrizzle-Skript in dieser Umgebung aus:
```bash
python3 plantpidrizzle_script.py
```

## Hardware-Setup
- Schließen Sie den Feuchtigkeitssensor an den SPI-Port des Raspberry Pi an.
- Verbinden Sie die Wasserpumpe mit dem GPIO-Pin 23 des Raspberry Pi.

## Konfiguration
- Ersetzen Sie `YOUR_BOT_TOKEN_HERE` und `YOUR_CHAT_ID_HERE` im Skript durch Ihre Telegram-Bot-Token und Chat-ID.
- Konfigurieren Sie die MongoDB URIs gemäß Ihren Zugangsdaten.

## Hauptfunktionen
- Kontinuierliche Überwachung des Feuchtigkeitsgehalts.
- Automatische Aktivierung der Bewässerung bei niedrigem Feuchtigkeitsgehalt.
- Datenspeicherung der Feuchtigkeitswerte und Bewässerungszeiten in MongoDB.
- Benachrichtigungen über den Bewässerungsstatus via Telegram.

## Fehlerbehandlung und Sicherheit
- Fehlerbehandlung für MongoDB-Verbindungen.
- Sichere Steuerung der Wasserpumpe zur Vermeidung von elektrischen Risiken.
- Graceful Shutdown bei Programmabbruch zur Vermeidung von Hardwareproblemen.

## Wartung und Anpassungen
- Regelmäßige Überprüfung der Wasserversorgung und des Sensorzustands.
- Anpassbarer Feuchtigkeitsschwellenwert für unterschiedliche Pflanzentypen.

Mit PlantPiDrizzle erhalten Sie eine smarte, zuverlässige und benutzerfreundliche Lösung für die automatisierte Pflanzenpflege, die Ihren Alltag erleichtert und Ihre Pflanzen glücklich macht.

## Hinweis
Hier geht es noch zum dazugehörigen Dashboard, worüber die letze Bewässerung und der Feuchtigkeitsstand eingesehen werden kann: https://github.com/noahstammm/IoT_PlantPiDrizzle
