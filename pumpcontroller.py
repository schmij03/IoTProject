import RPi.GPIO as GPIO
import time

# GPIO-Modus einstellen (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# GPIO-Pin als Ausgang festlegen
GPIO.setup(23, GPIO.OUT)

# Pumpe einschalten
GPIO.output(23, GPIO.HIGH)  # Bei PNP Transistor, GPIO.HIGH schaltet ab, da es GND an den Pin bringt.
print("Pumpe eingeschaltet")
time.sleep(5)  # 5 Sekunden warten

# Pumpe ausschalten
GPIO.output(23, GPIO.LOW)  # Bei PNP Transistor, GPIO.LOW aktiviert den Transistor.
print("Pumpe ausgeschaltet")

# GPIO-Einstellungen zurücksetzen
GPIO.cleanup()
