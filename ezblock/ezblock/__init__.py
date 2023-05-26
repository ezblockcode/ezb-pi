#!/usr/bin/env python3
import sys
from .version import VERSION
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


def __reset_mcu__():
    mcurst = Pin("MCURST")
    mcurst.off()
    delay(1)
    mcurst.on()


def __main__():
   
    _print('ezblock version: %s'%VERSION)

    usage = '''
Usage:
    ezblock [option]

Options:
    reset-mcu   Reset MCU on Ezblock
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
        __reset_mcu__()
    else:
        _print(usage)
        quit()


