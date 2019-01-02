from raspberrypi import BLE
from time import sleep

__PRINT__ = print

def print(msg, end='\n', tag='[DEBUG]'):
	ble = BLE()
	msg = '%s %s' % (tag, msg)
	__PRINT__(msg, end=end)
	msg = msg+end
	ble.write(msg)

# airprint = print

def delay(ms):
	sleep(ms/1000)


def mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
