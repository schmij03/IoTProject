import RPi.GPIO as GPIO

PUMP_RELAY_PIN = 18  # Change to your GPIO pin

GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_RELAY_PIN, GPIO.OUT)

def pump_on():
    GPIO.output(PUMP_RELAY_PIN, GPIO.HIGH)

def pump_off():
    GPIO.output(PUMP_RELAY_PIN, GPIO.LOW)
