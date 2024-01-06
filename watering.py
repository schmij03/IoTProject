# -*- coding: utf-8 -*-

import spidev
import time
import RPi.GPIO as GPIO
from pymongo import MongoClient, server_api
import requests

# GPIO setup
pump_pin = 23  # GPIO Nummer auf dem Raspberry PI.
GPIO.setmode(GPIO.BCM)  # oder GPIO.BOARD für physische Pin-Nummerierung
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

def send_telegram_message(message):
    """Sendet eine Nachricht ueber den Telegram Bot."""
    send_text = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()
    
try:
    while True:
        # Read the moisture sensor data
        moisture_level = ReadChannel(sensor_channel)
        
        # Print out results
        print(f"Moisture Level: {moisture_level}")
        
        # Store the value in MongoDB
        post = {"moisture_level": moisture_level, "timestamp": time.time()}
        post_id = collection.insert_one(post).inserted_id
        
        # Check if moisture level is below threshold
        if moisture_level < threshold:
            print("Water your plant!")
            water_count += 1
            GPIO.output(pump_pin, GPIO.HIGH)  # Schaltet die Pumpe ein
            
            # Halte die Pumpe fuer 5 Sekunden an
            time.sleep(5)
            
            GPIO.output(pump_pin, GPIO.LOW)  # Schaltet die Pumpe aus
        else:
            GPIO.output(pump_pin, GPIO.LOW)  # Stellt sicher, dass die Pumpe aus ist
        
        if water_count >= 10:
            print("Bitte Flasche fuellen!")
            # Send message via Telegram
            send_telegram_message("Bitte Flasche fuellen!")
            water_count = 0  # Zuruecksetzen des Zaehlers nach der Aufforderung
        
        # Wait before repeating loop
        time.sleep(10)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()  # Setzt alle Pins zurueck
