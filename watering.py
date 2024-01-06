# -*- coding: utf-8 -*-

import spidev
import time
from pymongo import MongoClient, server_api

# Correct your URI with appropriate username and password
uri = "mongodb+srv://janosi:1234@cluster.lp4msmq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=server_api.ServerApi('1'))

# Attempt to connect and confirm connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

# Define your database and collection here
db = client["IoT"]  # Change "wateringSystem" to your actual database name
collection = db["Cluster"]  # Change "moistureReadings" to your actual collection name

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
        
        # Wait before repeating loop
        time.sleep(10)

except KeyboardInterrupt:
    spi.close()


