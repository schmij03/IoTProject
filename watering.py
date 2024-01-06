# -*- coding: utf-8 -*-

import spidev
import time
import RPi.GPIO as GPIO
from pymongo import MongoClient, server_api

# GPIO setup
pump_pin = 17  # Ersetzen Sie 17 durch die GPIO-Nummer, die Sie verwenden möchten
GPIO.setmode(GPIO.BCM)  # oder GPIO.BOARD für physische Pin-Nummerierung
GPIO.setup(pump_pin, GPIO.OUT)

# Correct your URI with appropriate username and password
uri = "mongodb+srv://username:password@cluster.lp4msmq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

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
spi.open(0,0)
spi.max_speed_hz=1000000

# Function to read SPI data from MCP3008 chip
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

# Define sensor channel (e.g. 0)
sensor_channel = 0

# Define the threshold below which "water your plant" is printed
threshold = 200

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
            GPIO.output(pump_pin, GPIO.HIGH)  # Schaltet den Transistor (und die Pumpe) ein
        else:
            GPIO.output(pump_pin, GPIO.LOW)  # Schaltet den Transistor (und die Pumpe) aus
        
        # Wait before repeating loop
        time.sleep(10)

except KeyboardInterrupt:
    spi.close()
    GPIO.cleanup()  # Setzt alle Pins zurück
