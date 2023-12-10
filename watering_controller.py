from sensor import read_soil_moisture
from pump import pump_on, pump_off

MOISTURE_THRESHOLD = 0.3  # Define your threshold

def check_and_water():
    if read_soil_moisture() < MOISTURE_THRESHOLD:
        pump_on()
    else:
        pump_off()
