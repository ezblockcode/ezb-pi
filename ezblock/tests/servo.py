from raspberrypi import Servo
import time

S7 = Servo("P7")
S0 = Servo("P0")

while True:
    S7.angle(90)
    S0.angle(90)
    time.sleep(1)
    S7.angle(180)
    S0.angle(180)
    time.sleep(1)