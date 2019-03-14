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
from time import sleep
from ezblock.sensorkit import DHT11, Ultrasonicranging, DS18B20
from ezblock.taskmgr import Taskmgr
# from ezblock.camera import Camera

ble = BLE()

ble.write('NAME+ezb-RPi')
# ble.write('ADVP+') # 0~F

# from ezblock.uart import UART
SCRIPT_NAME = 'ezblock'
# is_print_init = False
def reset():
    from os import system as run
    import os
    # Kill restart program

    # run("sudo kill `ps aux | grep '%s' | awk '{print $2}'`" % (
    #     SCRIPT_NAME))
    # # # Rerun new program
    # run("%s > /dev/null 2>&1 &" % SCRIPT_NAME)

    run("sudo kill `ps aux | grep '%s' | awk '{print $2}'` && %s > /dev/null 2>&1 &" % (
        SCRIPT_NAME, SCRIPT_NAME))
    # # Rerun new program

    # run('sudo service ezblock restart')
    # run('sudo service ezblock restart')
    # quit()
    # os.execl("ezblock", "")

def main():
    from ezblock import _boot

__PRINT__ = print

# def print_init():
#     global ble, is_print_init
#     if not is_print_init:
#         ble = BLE()
#         is_print_init = True

def print(msg, end='\n', tag='[DEBUG]'):
#     print_init()
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