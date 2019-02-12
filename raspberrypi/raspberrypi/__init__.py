from raspberrypi.pin import Pin
from raspberrypi.led import LED
from raspberrypi.pwm import PWM
from raspberrypi.servo import Servo
from raspberrypi.signal import Signal
from raspberrypi.spi import SPI
from raspberrypi.switch import Switch
from raspberrypi.uart import UART
from raspberrypi.i2c import I2C
from raspberrypi.adc import ADC
from raspberrypi.ble import BLE
from raspberrypi.ble import Remote
from raspberrypi.iot import IOT
from time import sleep
from raspberrypi.sensorkit import DHT11, Ultrasonicranging, DS18B20
from raspberrypi.taskmgr import Taskmgr
# from raspberrypi.camera import Camera

# from raspberrypi.uart import UART
SCRIPT_NAME = 'raspberrypi'
is_print_init = False
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

    # run('sudo service raspberrypi restart')
    # run('sudo service raspberrypi restart')
    # quit()
    # os.execl("raspberrypi", "")



def main():
    from raspberrypi import _boot


__PRINT__ = print

def print_init():
    global ble, is_print_init
    if not is_print_init:
        ble = BLE()
        is_print_init = True

def print(msg, end='\n', tag='[DEBUG]'):
    print_init()
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