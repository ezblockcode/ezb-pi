# import requests
# import json

# class IOT(object):
#     headers = {'Content-Type': 'application/json'}      # Header

#     def __init__(self, iot_token, url = 'https://www.ezblock.cc:11000/api/web/v2/'):
#         self.iot_token = iot_token
#         self.url = url + "ezblock/"

#     def _upload(self, url, data):
#         url = self.url+url
#         headers={'Content-Type': 'application/json'}
#         r = requests.post(url, json=data, headers=headers)
#         result = r.content.decode('utf-8')
#         print(result)
#         result = json.loads(result)
#         if result["code"] == 200:
#             data = result["data"]
#             value = data["value"]
#             print(data)
#             return value
#         else:
#             print("Error[%s]"%result["code"])
#             if result["code"] == 10302:
#                 return None

#     def post(self, sensorname, value):
#         data = {
#             "name":sensorname,
#             "iotToken":self.iot_token,
#             "value":value,
#         }
#         return self._upload("iot/upload", data)

#     def get(self, sensorname):
#         data = {
#             "name": sensorname,
#             "iotToken": self.iot_token,
#         }
#         value = self._upload("iot/get", data)
#         print(value)
#         try:
#             value = int(value)
#         except:
#             pass
#         return value

# def test():
#     from ezblock import print
#     import random
    
#     __IOT_TOKEN__ = "6a31ef81850642d980fceb14a974e087XX1600395165796"
#     __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")
  
#     print("%s"%(__IOT__.get("actuators#Switch#1")))
#     __IOT__.post("actuators#Switch#1", (random.randint(1, 100)))

# if __name__ == "__main__":
#     test()

import paho.mqtt.client as mqtt 
import json
import time


class IOT():
    
    MQTT_BROKER_HOST = '47.92.86.79'
    MQTT_BROKER_PORT = 1883
    MQTT_KEEP_ALIVE_INTERVAL = 60
    
    def __init__(self, iot_token):
        self.iot_token = iot_token
        self.client = mqtt.Client("Sunfounder test")
        self.client.connect(self.MQTT_BROKER_HOST, self.MQTT_BROKER_PORT, self.MQTT_KEEP_ALIVE_INTERVAL)
        self.recv_date = None
        
    def post(self, topic, value):
        sensorname = topic.split("_")[-1]
        data = {
            "name":sensorname,
            "iotToken":self.iot_token,
            "value":value,
        }
        self.client.subscribe(topic)
        self.client.publish(topic, json.dumps(data))
    
    def on_message(self, client, userdata, msg):
        date = msg.payload.decode()
        print("Message Recieved. ", date)
        date = json.loads(date)
        self.recv_date = date["value"]
        
    def get(self, topic):
        self.client.subscribe(topic)
        self.client.on_message=self.on_message 
        self.client.loop_start()
        return self.recv_date

def test():
    iot = IOT("16128573140003757843323708413916266436285")
    iot.post("com/iot/sensorsHumidity1Drr", 6.6)
    while True:
        
        iot.get("com/iot/sensorsHumidity1Drr")
        
        time.sleep(1)
    
if __name__ == "__main__":
    test()


        
        