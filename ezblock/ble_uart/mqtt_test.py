import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

MQTT_BROKER_HOST = '47.92.86.79'
MQTT_BROKER_PORT = 1883
MQTT_KEEP_ALIVE_INTERVAL = 60

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

mqttBroker ="47.92.86.79:1883" 

# client = mqtt.Client("Sunfounder test")
# client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE_INTERVAL) 

# while True:
#     randNumber = uniform(20.0, 21.0)
#     client.publish("TEMPERATURE_test", randNumber)
#     print("Just published " + str(randNumber) + " to topic TEMPERATURE_test")
#     time.sleep(1)

client = mqtt.Client("Sunfounder test")
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, MQTT_KEEP_ALIVE_INTERVAL) 

client.loop_start()

client.subscribe("TEMPERATURE_test")
client.on_message=on_message 

# time.sleep(30)
client.loop_forever()