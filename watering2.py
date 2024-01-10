# -*- coding: utf-8 -*-

import logging
import spidev
import time
import RPi.GPIO as GPIO
from pymongo import MongoClient, server_api
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# GPIO setup
pump_pin = 23  # GPIO Nummer auf dem Raspberry PI.
GPIO.setmode(GPIO.BCM)  # oder GPIO.BOARD fuer physische Pin-Nummerierung
GPIO.setup(pump_pin, GPIO.OUT)

# Counter for "Water your plant!"
water_count = 0

uri = "mongodb+srv://janosi:1234@cluster.lp4msmq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=server_api.ServerApi('1'))

# Attempt to connect and confirm connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

db = client["IoT"]
collection = db["Cluster"]

# Open SPI bus
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Define sensor channel (e.g. 0)
sensor_channel = 0

# Define the threshold below which "water your plant" is printed
threshold = 200

# Telegram configuration
telegram_bot_token = '6611630847:AAEyTRdb8zn_G2cHA33covbTtZ7luOE6JoA'
chat_id = '6432517199'

# Logging configuration (optional)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def send_telegram_message(message):
    """Sendet eine Nachricht via Telegram Bot."""
    send_text = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

# Command handler functions
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hallo! Ich werde dich informieren, wenn ich die Pflanze giesse.')

def giessen_command(update: Update, context: CallbackContext) -> None:
    """Manuelles Giessen ueber den Telegram-Befehl"""
    update.message.reply_text('Pflanze wird gegossen!')
    giesse_pflanze()
    update.message.reply_text('Giessen abgeschlossen!')

def giesse_pflanze():
    """Aktiviert die Pumpe fuer eine festgelegte Zeit"""
    print('Pflanze wird gegossen!')
    GPIO.output(pump_pin, GPIO.HIGH)  # Schaltet die Pumpe ein
    time.sleep(5)  # Pumpe fuer 5 Sekunden laufen lassen
    GPIO.output(pump_pin, GPIO.LOW)  # Schaltet die Pumpe aus
    print('Giessen abgeschlossen!')

def main() -> None:
    # Erstellt den Updater und uebergibt ihn Ihr Bot-Token.
    updater = Updater(telegram_bot_token)

    # Erhalten den Dispatcher, um handlers zu registrieren
    dp = updater.dispatcher

    # Verschiedene command handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("giessen", giessen_command))  # Fuegt einen Handler fuer /giessen hinzu
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, giessen_command))  # Reagiert auf Nachrichten

    # Startet den Bot
    updater.start_polling()

    # ueberwachen des Feuchtigkeitssensors und automatisches Gießen, wenn erforderlich
    try:
        while True:
            # Feuchtigkeit lesen
            moisture_level = ReadChannel(sensor_channel)
            print(f"Aktuelles Feuchtigkeitsniveau: {moisture_level}")

            # ueberpruefen, ob das Feuchtigkeitsniveau unter dem Schwellenwert liegt
            if moisture_level < threshold:
                print("Feuchtigkeit unter Schwellenwert, Pflanze wird automatisch gegossen.")
                giesse_pflanze()

            # Store the value in MongoDB
            post = {"moisture_level": moisture_level, "timestamp": time.time()}
            post_id = collection.insert_one(post).inserted_id

            if water_count >= 10:
                print("Bitte Flasche fuellen!")
                # Send message via Telegram
                send_telegram_message("Bitte Flasche fuellen!")
                water_count = 0  # Zuruecksetzen des Zaehlers nach der Aufforderung

            # Wartezeit, bevor die Schleife wiederholt wird
            time.sleep(10)

    except KeyboardInterrupt:
        spi.close()
        GPIO.cleanup()  # Setzt alle Pins zurueck

if __name__ == '__main__':
    main()
