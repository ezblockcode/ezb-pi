from ezblock.ble import BLE
import time
import os
import re

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

def getIP(ifaces=['wlan0', 'eth0']):
    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = 'ip addr show {}'.format(iface)
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?=\/)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return False