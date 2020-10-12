from .pin import Pin
from .led import LED
from .pwm import PWM
from .servo import Servo
from .signal import Signal
from .spi import SPI
from .switch import Switch
from .uart import UART
from .i2c import I2C
from .adc import ADC
from .ble import BLE
from .ble import Remote
from .music import Music
from .color import Color
from .camera import Camera
from .iot import IOT
from .tts import TTS
from .irq import IRQ
from .wifi import WiFi
from .utils import *
from .taskmgr import Taskmgr
from .modules import *
from .send_email import SendMail
from .info import Info
from .rgb_matrix import RGB_Matrix
from .oled import SSD1306_128_64 as SSD1306
from .lcd1602_i2c import LCD
from .serial_sound import Serial_Sound
from .nrf24 import NRF24
from .filedb import fileDB

def __reset_mcu__():
    mcurst = Pin("MCURST")
    mcurst.off()
    delay(1)
    mcurst.on()

def __main__():
    import sys
    from .utils import __PRINT__

    usage = '''
Usage:
    ezblock [option]

Options:
    reset-mcu   Reset MCU on Ezblock
    -h          Show this help text and exit
'''
    option = ""
    if len(sys.argv) <= 1:
        __PRINT__(usage)
        quit()
    elif len(sys.argv) > 1:
        option = sys.argv[1]

    if "-h" == option:
        __PRINT__(usage)
        quit()
    elif option == "reset-mcu":
        __PRINT__("MCU Reset.")
        __reset_mcu__()
    else:
        __PRINT__(usage)
        quit()
    