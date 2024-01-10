import logging
import time
import spidev
import RPi.GPIO as GPIO
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# GPIO und SPI setup für die Pumpe und den Sensor
pump_pin = 23  # Passen Sie die Nummer an Ihren GPIO-Pin an
GPIO.setmode(GPIO.BCM)
GPIO.setup(pump_pin, GPIO.OUT)

# SPI Device öffnen
spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

# Funktion zum Auslesen des Feuchtigkeitssensors
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

# Definieren Sie den Sensor Kanal und den Schwellenwert
sensor_channel = 0
threshold = 200

# Telegram Bot Token und Chat-ID
telegram_bot_token = '6611630847:AAEyTRdb8zn_G2cHA33covbTtZ7luOE6JoA'
chat_id = '6432517199'

# Logging konfigurieren (optional)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Command handler Funktionen
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hallo! Ich werde dich informieren, wenn ich die Pflanze gieße.')

def giessen_command(update: Update, context: CallbackContext) -> None:
    """Manuelles Gießen über den Telegram-Befehl"""
    update.message.reply_text('Pflanze wird gegossen!')
    giesse_pflanze()
    update.message.reply_text('Giessen abgeschlossen!')

def giesse_pflanze():
    """Aktiviert die Pumpe für eine festgelegte Zeit"""
    print('Pflanze wird gegossen!')
    GPIO.output(pump_pin, GPIO.HIGH)  # Schaltet die Pumpe ein
    time.sleep(5)  # Pumpe für 5 Sekunden laufen lassen
    GPIO.output(pump_pin, GPIO.LOW)  # Schaltet die Pumpe aus
    print('Giessen abgeschlossen!')

def main() -> None:
    # Erstellt den Updater und übergibt ihn Ihr Bot-Token.
    updater = Updater(telegram_bot_token)

    # Erhalten den Dispatcher, um handlers zu registrieren
    dp = updater.dispatcher

    # Verschiedene command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("giessen", giessen_command))  # Fügt einen Handler für /giessen hinzu
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, giessen_command))  # Reagiert auf Nachrichten

    # Startet den Bot
    updater.start_polling()

    # Überwachen des Feuchtigkeitssensors und automatisches Gießen, wenn erforderlich
    try:
        while True:
            # Feuchtigkeit lesen
            moisture_level = ReadChannel(sensor_channel)
            print(f"Aktuelles Feuchtigkeitsniveau: {moisture_level}")

            # Überprüfen, ob das Feuchtigkeitsniveau unter dem Schwellenwert liegt
            if moisture_level < threshold:
                print("Feuchtigkeit unter Schwellenwert, Pflanze wird automatisch gegossen.")
                giesse_pflanze()

            # Wartezeit, bevor die Schleife wiederholt wird
            time.sleep(10)
    except KeyboardInterrupt:
        spi.close()
        GPIO.cleanup()  # Setzt alle Pins zurück

if __name__ == '__main__':
    main()
