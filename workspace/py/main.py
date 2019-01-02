from raspberrypi import *

led = Pin("LED")
def forever():
    led.on()
    delay(500)
    led.off()
    delay(500)

while True:
    forever()