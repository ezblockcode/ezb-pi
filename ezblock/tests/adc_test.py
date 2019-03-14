from raspberrypi import ADC
import time

A0=ADC("A7")
A0.debug="debug"
while True:
    A0.read()
    time.sleep(1)
