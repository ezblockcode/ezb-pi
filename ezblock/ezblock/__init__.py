#!/usr/bin/env python3
import sys
from .version import VERSION, __version__
from .user_info import *
# io operations
from .pin import Pin
from .led import LED
from .pwm import PWM
from .servo import Servo
from .uart import UART
from .i2c import I2C
from .adc import ADC
from .spi import SPI
from .switch import Switch
# block modules
from .modules import *
from .rgb_matrix import RGB_Matrix
from .oled import SSD1306_128_64 as SSD1306
from .lcd1602_i2c import LCD
from .serial_sound import Serial_Sound
from .nrf24 import NRF24
from .music import Music
from .color import Color
from .camera import Camera
from .iot import IOT
from .tts import TTS
from .irq import IRQ
# utility functions
from .send_email import SendMail
from .info import Info
from .filedb import fileDB
from .signal import Signal
from .wifi import WiFi
from .utils import *
from .taskmgr import Taskmgr
# websockets
from .websockets import Remote
from .websockets import ws_print as print
from .websockets import log


def _print(msg:str, end='\n'):
    sys.stdout.write(msg + end)


def get_firmware_version():
    ADDR = [0x14, 0x15]
    VERSSION_REG_ADDR = 0x05
    i2c = I2C(ADDR)
    version = i2c.mem_read(3, 0x14, VERSSION_REG_ADDR)
    _print(f"Robot HAT Firmare version: {version[0]}.{version[1]}.{version[2]}")

def __main__():
   
    _print('ezblock version: %s'%VERSION)

    usage = '''
Usage:
    ezblock [option]

Options:
    reset-mcu   Reset MCU on Ezblock
    version     Get firmware version
    -h          Show this help text and exit
'''
    option = ""
    if len(sys.argv) <= 1:
        _print(usage)
        quit()
    elif len(sys.argv) > 1:
        option = sys.argv[1]

    if "-h" == option:
        _print(usage)
        quit()
    elif option == "reset-mcu":
        _print("MCU Reset.")
        reset_mcu()
    elif sys.argv[1] == "version":
        get_firmware_version()
        quit()
    else:
        _print(usage)
        quit()


