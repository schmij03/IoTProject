# -*- coding: utf-8 -*-

import spidev
import time
import RPi.GPIO as GPIO
from pymongo import MongoClient, server_api
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
import logging

# GPIO setup
pump_pin = 23  # GPIO Nummer auf dem Raspberry PI.
GPIO.setmode(GPIO.BCM)  # oder GPIO.BOARD für physische Pin-Nummerierung
GPIO.setup(pump_pin, GPIO.OUT)

# Counter for "Water your plant!"
water_count = 0

# MongoDB URIs
uri = "mongodb+srv://janosi:1234@cluster.lp4msmq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
uri2 ="mongodb+srv://janosi:1234@cluster0.4hmu3ww.mongodb.net/?retryWrites=true&w=majority"

# Create new clients and connect to the server
client = MongoClient(uri, server_api=server_api.ServerApi('1'))
client1= MongoClient(uri2, server_api=server_api.ServerApi('1'))

# Attempt to connect and confirm connection
try:
    client.admin.command('ping')
    client1.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

# Database and Collection setup
db = client["IoT"]
db1 = client1["IoT2"]
collection = db["Cluster"]
collection1 = db1["Cluster0"]

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
threshold = 550

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

def giesse_pflanze(update: Update, context: CallbackContext):
    """Aktiviert die Pumpe fuer eine festgelegte Zeit"""
    print('Pflanze wird gegossen!')
    GPIO.output(pump_pin, GPIO.HIGH)  # Schaltet die Pumpe ein
    time.sleep(5)  # Pumpe fuer 5 Sekunden laufen lassen
    GPIO.output(pump_pin, GPIO.LOW)  # Schaltet die Pumpe aus
    print('Giessen abgeschlossen!')
    if update:
        update.message.reply_text('Pflanze wurde gegossen!')

# Funktion zur Verarbeitung eingehender Nachrichten
def message_received(update: Update, context: CallbackContext) -> None:
    # Extrahieren des Texts der eingehenden Nachricht
    message_text = update.message.text

    # Überprüfen, ob das Wort "giessen" im Text enthalten ist
    if "giessen" in message_text.lower():
        giesse_pflanze(update, context)

# Telegram Bot Initialisierung
updater = Updater(telegram_bot_token)

# Erstellen eines Dispatchers
dp = updater.dispatcher

# Hinzufügen eines CommandHandlers für den Befehl '/giessen'
dp.add_handler(CommandHandler("giessen", giesse_pflanze))

# Hinzufügen eines MessageHandlers, der auf alle Nachrichten reagiert
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, message_received))

# Starten des Bots
updater.start_polling()

# Haupt-Loop
try:
    while True:
        # Read the moisture level
        moisture_level = ReadChannel(sensor_channel)
        print(f"Moisture Level: {moisture_level}")
        
        # Store the value in MongoDB
        post = {"moisture_level": moisture_level, "timestamp": time.time()}
        post_id = collection.insert_one(post).inserted_id
        
        # Check if moisture level is below threshold
        if moisture_level > threshold:
            print("Water your plant!")
            send_telegram_message("Ihre Pflanze wurde gegossen.")
            giesse_pflanze(None, None)  # Note: Update and Context are not used in this function
            water_count += 1

            # Store the water event in MongoDB
            post1 = {"timestamp": time.time()}
            post_id1 = collection1.insert_one(post1).inserted_id

        if water_count >= 10:
            print("Bitte Flasche fuellen!")
            send_telegram_message("Bitte Flasche fuellen!")
            water_count = 0  # Reset counter after prompt

        time.sleep(10)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()  # Clean up all GPIO
    updater.stop()  # Stoppen des Telegram Bots
