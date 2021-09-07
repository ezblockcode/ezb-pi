# #!/usr/bin/env python3
# from raspberrypi import DHT11
# from raspberrypi import Pin
# import time
# while(True):
#     # print(DHT11(Pin(17)).read.result[0,1])
#     # time.sleep(1)

#     # value = DHT11(Pin(17)).read()
#     # if value:
#     #     print(value[0])
#     # time.sleep(1)

#     dht11 = DHT11(Pin(27))
#     value = dht11.read()
#     if value:
#         print(value[0])
#     else:

#         print(value)
#     time.sleep(1)
# # print(Ultrasonicranging(Pin(17), Pin(18)).value())




# # sensorkit(pin1, pin2).ultrasonicranging_value()
# #  sensorkit(pin1).ds18b20_value()
# # sensorkit(pin1).dht11_read.result[0,1]




# #!/usr/bin/env pythno3
# from raspberrypi import Pin
# from raspberrypi import ADC
# import time

# class Button(object):
#     pass

#     def __init__(self, pin_in, pin_out):
#         self.pin_in = pin_in
#         self.pin_out = pin_out

#         # pin_in.value(1)


# def test():
#     print("hello1")
#     pin_in = Pin(17)
#     pin_out= ADC(0)
#     print("hello2")
#     button = Button(pin_in, pin_out)
#     print("hello3")
#     # print(button.pin_out.read())
#     while(True):
#         print(button.pin_out.read())
#         time.sleep(1)
    

# test()


#!/usr/bin/env pythno3
from raspberrypi import DHT11
from raspberrypi import Pin
import time

dht11 = DHT11(17)
while(True):

    dht11.read()
    time.sleep(0.5)