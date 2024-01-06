import spidev
import time

# Konfiguration des MCP3008 ADC
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Gerät 0
spi.max_speed_hz = 1000000  # 1 MHz (kann je nach Sensor variieren)

def read_adc(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data

# Anpassen Sie den Kanal entsprechend Ihrer Verkabelung
moisture_channel = 0

try:
    while True:
        moisture_level = read_adc(moisture_channel)
        print('Moisture Level:', moisture_level)
        time.sleep(1)

except KeyboardInterrupt:
    spi.close()

