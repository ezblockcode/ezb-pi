from ezblock.ble import BLE
import time
import os

ble = BLE()

ble.write('NAME+ezb-RPi')
# ble.write('ADVP+') # 0~F

__PRINT__ = print

def print(msg, end='\n', tag='[DEBUG]'):
    _msg = "EZblock [{}] [DEBUG] {}".format(time.asctime(), msg)
    os.system("echo {} >> /opt/ezblock/log".format(_msg))
    msg = '%s %s %s' % (tag, msg, tag)
    __PRINT__(msg, end=end)
    ble.write(msg)

def delay(ms):
    time.sleep(ms/1000)

def mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
