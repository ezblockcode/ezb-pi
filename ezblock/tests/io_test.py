<<<<<<< HEAD:tests/io_test.py
from raspberrypi import IOT, delay
__IOT_TOKEN__ = "W5kRBNyJSNXYyqcZ"
__IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


# def forever():
#   # print("%s"%__IOT__.get("actuators#Button#1"))
#  #  # delay(1000)
# 	__IOT__.post("sensors#Temperature#1", "14")
# 	print("%s"%__IOT__.get("actuators#Button#1"))
# while True:
# 	forever()

# 	from raspberrypi import IOT
# __IOT_TOKEN__ = "6wtOXlxPx9qWfIfo"
# __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


# def forever():
#   __IOT__.post("sensors#Temperature#1", "13")
# rom raspberrypi import IOT
# __IOT_TOKEN__ = "6wtOXlxPx9qWfIfo"
# __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


def forever():
	print("%s"%__IOT__.post("actuators#Button#1", "2"))
	print("%s"%__IOT__.get("actuators#Button#1"))
	print('')
	delay(1000)

if __name__ == '__main__':
	while True:
		forever()
=======
from raspberrypi import IOT, delay
__IOT_TOKEN__ = "epuubHMC3Bj5b0fb"
__IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


def forever():
  # print("%s"%__IOT__.get("actuators#Button#1"))
 #  # delay(1000)
	__IOT__.post("sensors#Temperature#1", "14")
	print("%s"%__IOT__.get("actuators#Button#1"))
while True:
	forever()

# 	from raspberrypi import IOT
# __IOT_TOKEN__ = "6wtOXlxPx9qWfIfo"
# __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


# def forever():
#   __IOT__.post("sensors#Temperature#1", "13")
# rom raspberrypi import IOT
# __IOT_TOKEN__ = "6wtOXlxPx9qWfIfo"
# __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")


# def forever():
#   print("%s"%__IOT__.get("actuators#Button#1"))
>>>>>>> 6b56b9959e1d44c6483ff4828a2a1376ad3fdfa6:python/tests/io_test.py
