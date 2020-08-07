""" Example for using the SGP30 with CircuitPython and the Adafruit library"""

import os
import time
import busio
import adafruit_sgp30
from board import SCL, SDA
from Adafruit_IO import Client, Feed, RequestError

# Fetch the key for the IO service
aio_key = None
if os.path.exists('aio.txt'):
    aio_key = str(open('aio.txt', 'r').read()).strip()
else:
    print('No token set for adafruitio')

# Setup the gas sensor
i2c = busio.I2C(SCL, SDA)

# Create library object on our I2C port
sgp30 = adafruit_sgp30.Adafruit_SGP30(i2c)

print("SGP30 serial #", [hex(i) for i in sgp30.serial])

sgp30.iaq_init()
# sgp30.set_iaq_baseline(0x8eb4, 0x912b)

# Setup the io data feeds
aio = Client('ArthurGuy', aio_key)
tvoc_feed = aio.feeds('study.tvoc')
eCO2_feed = aio.feeds('study.eco2')

elapsed_sec = 0


def capture_sensor_readings():
    try:
        print("eCO2 = %d ppm \t TVOC = %d ppb" % (sgp30.eCO2, sgp30.TVOC))
        time.sleep(1)
        aio.send(eCO2_feed.key, sgp30.eCO2)
        aio.send(tvoc_feed.key, sgp30.TVOC)
        return True
    except:
        return False


def capture_sensor_baseline_readings():
    print("**** Baseline values: eCO2 = 0x%x, TVOC = 0x%x" % (sgp30.baseline_eCO2, sgp30.baseline_TVOC))


while True:
    status = capture_sensor_readings()
    if status is False:
        print("Error reading sensor")
    time.sleep(10)
    elapsed_sec += 1
    if elapsed_sec > 6:
        elapsed_sec = 0
        capture_sensor_baseline_readings()
