from raspberrypi import delay

from raspberrypi import IOT
__IOT_TOKEN__ = "EKoOgvfrILGoSCn5"
__IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


def forever():
  print("%s" % __IOT__.get("actuators#Button#1"))

while True:
    forever()
