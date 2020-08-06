from smbus2 import SMBusWrapper
from sgp30 import Sgp30
import time
with SMBusWrapper(1) as bus:
    sgp = Sgp30(bus, baseline_filename="/tmp/mySGP30_baseline")  # things thing with the baselinefile is dumb and will be changed in the future
    print("resetting all i2c devices")
    sgp.i2c_geral_call()  # WARNING: Will reset any device on teh i2cbus that listens for general call
    print(sgp.read_features())
    print(sgp.read_serial())
    sgp.init_sgp()
    print(sgp.read_measurements())
    print("the SGP30 takes at least 15 seconds to warm up, 12 hours before the readigs become really stable")
    for i in range(20):
        time.sleep(1)
        print(".", end="")
    print()
    print(sgp.read_measurements())