# Import necessary libraries
import spidev
import time
import RPi.GPIO as GPIO
from pymongo import MongoClient, server_api
import requests
import logging

# Set up GPIO pin for the water pump
pump_pin = 23  
GPIO.setmode(GPIO.BCM)  
GPIO.setup(pump_pin, GPIO.OUT)

# Initialize a variable to keep track of water count
water_count = 0

# MongoDB URIs for two databases
uri = "mongodb+srv://janosi:1234@cluster.lp4msmq.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"

# Create MongoClient instances for the two databases
client = MongoClient(uri, server_api=server_api.ServerApi('1'))


# Check if MongoDB connections are successful
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    print("Failed to connect to MongoDB:", e)

# Select the specific databases and collections
db = client["IoT"]
collection = db["Cluster"]
collection1 = db["message"]

# Set up SPI for analog sensor communication
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

# Function to read data from an analog sensor channel
def ReadChannel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Analog sensor channel to read from
sensor_channel = 0

# Moisture level threshold for watering
threshold = 600

# Telegram configuration
telegram_bot_token = '6611630847:AAEyTRdb8zn_G2cHA33covbTtZ7luOE6JoA'
chat_id = '6432517199'

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to send a message via Telegram
def send_telegram_message(message):
    send_text = f'https://api.telegram.org/bot{telegram_bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}'
    response = requests.get(send_text)
    return response.json()

# Function to water the plant
def giesse_pflanze():
    print('Pflanze wird gegossen!')
    GPIO.output(pump_pin, GPIO.HIGH)  
    time.sleep(5)  
    GPIO.output(pump_pin, GPIO.LOW)  
    print('Giessen abgeschlossen!')
    if moisture_level > threshold:
        send_telegram_message("Hallo\nDeine Pflanze hatte einen Feuchtigskeitslevel von:",moisture_level,"\nDeine Pflanze wurde aus diesem Grund soeben gegossen.")
    
    send_telegram_message('Pflanze wurde gegossen!')

# Main loop to continuously monitor and water the plant
try:
    while True:
        # Read moisture level from the analog sensor
        moisture_level = ReadChannel(sensor_channel)
        print(f"Moisture Level: {moisture_level}")
        
        # Store the moisture level and timestamp in the MongoDB collection
        post = {"moisture_level": moisture_level, "timestamp": time.time()}
        post_id = collection.insert_one(post).inserted_id
        
        # Check if moisture level is above the threshold
        if moisture_level > threshold:
            print("Water your plant!")
           
            # Call the function to water the plant
            giesse_pflanze()  
            water_count += 1

            # Store the timestamp of watering in the second MongoDB collection
            post1 = {"timestamp": time.time()}
            post_id1 = collection1.insert_one(post1).inserted_id

        # Check if the water count has reached a limit
        if water_count >= 10:
            print("Bitte Flasche fuellen!")
            send_telegram_message("Bitte Flasche fuellen!")
            water_count = 0  

        # Wait for a set period before checking again (7200 seconds = 2 hours)
        time.sleep(7200)

except KeyboardInterrupt:
    # Close SPI and clean up GPIO pins on program exit
    spi.close()
    GPIO.cleanup()
