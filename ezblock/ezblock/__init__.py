from ezblock.pin import Pin
from ezblock.led import LED
from ezblock.pwm import PWM
from ezblock.servo import Servo
from ezblock.signal import Signal
from ezblock.spi import SPI
from ezblock.switch import Switch
from ezblock.uart import UART
from ezblock.i2c import I2C
from ezblock.adc import ADC
from ezblock.ble import BLE
from ezblock.ble import Remote
from ezblock.iot import IOT
from ezblock.tts import TTS
from ezblock.irq import IRQ
from time import sleep
from ezblock.taskmgr import Taskmgr
from ezblock.modules import *
from ezblock.send_email import SendMail
import time, os

# from ezblock.camera import Camera

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
    sleep(ms/1000)

def mapping(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def wifi_setup(country, ssid, psk):
    import os
    template = 'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=%s\nnetwork={\n\tssid="%s"\n\tpsk="%s"\n}'
    data = template % (country, ssid, psk)
    with open(r"/etc/wpa_supplicant/wpa_supplicant.conf", "w+") as f:
        # old = f.read()
        # f.seek(0)
        f.write(data)
        # f.write(old)
        # print("1")
        # print(self.ssid)
        # echo 'data'>>
    os.system("sudo ifconfig wlan0 down && sudo ifconfig wlan0 up")
