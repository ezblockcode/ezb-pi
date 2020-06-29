from ezblock import IOT
from ezblock import print
from ezblock import delay

__IOT_TOKEN__ = "PjHiavlQWeVFBb3W"
__IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


def forever():
  print("%s" % __IOT__.get("actuators#Slider#1"))
  delay(1000)

while True:
  forever()
