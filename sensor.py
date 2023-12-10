import RPi.GPIO as GPIO

MOISTURE_SENSOR_PIN = 17  # Change to your GPIO pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_PIN, GPIO.IN)

def read_soil_moisture():
    return GPIO.input(MOISTURE_SENSOR_PIN)
