import paho.mqtt.client as mqtt 
import json
import time
import os
import re
from .utils import log

def getIP(ifaces=['wlan0', 'eth0']):
    if isinstance(ifaces, str):
        ifaces = [ifaces]
    for iface in list(ifaces):
        search_str = 'ip addr show {}'.format(iface)
        result = os.popen(search_str).read()
        com = re.compile(r'(?<=inet )(.*)(?=\/)', re.M)
        ipv4 = re.search(com, result)
        if ipv4:
            ipv4 = ipv4.groups()[0]
            return ipv4
    return False

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result


class IOT():
    
    MQTT_BROKER_HOST = '' 
    MQTT_BROKER_PORT = 1883
    MQTT_KEEP_ALIVE_INTERVAL = 60
    
    def __init__(self, iot_token, mqtt_host):
        # try:
        time_count = 0
        while getIP() == False and time_count < 15:
            time_count += 1
            time.sleep(1)
        self.iot_token = iot_token
        self.MQTT_BROKER_HOST = mqtt_host

        log(self.MQTT_BROKER_HOST,'IOT')

        self.client = mqtt.Client("Sunfounder test")
        self.client.username_pw_set(username="admin",password="gkjsPS2aoQIvR4bt")
        a_flag = self.client.connect(self.MQTT_BROKER_HOST, self.MQTT_BROKER_PORT, self.MQTT_KEEP_ALIVE_INTERVAL)
        print("a_flag:",a_flag)
        self.recv_date = {}
        
    def post(self, topic, value):
        sensorname = topic.split("_")[-1]
        data = {
            "name":sensorname,
            "iotToken":self.iot_token,
            "value":value,
        }
        log(str(topic))
        log(data)
        self.client.subscribe(topic)
        self.client.publish(topic, json.dumps(data))
    
    def on_message(self, client, userdata, msg):
        date = msg.payload.decode()
        print("Message Recieved. ", date)
        date = json.loads(date)
        # if date['name'] not in list(self.recv_date.keys()):
        self.recv_date[str(date['name'])] = date["value"]

        
    def get(self, topic):
        ip = getIP()
        log('t %s'%(topic))
        if ip:
            self.client.subscribe(topic)
            self.client.on_message=self.on_message 
            self.client.loop_start()
            if topic in list(self.recv_date.keys()):
                return self.recv_date[topic]
            return None
        else:
            run_command("sudo touch /home/pi/noip")


def test():
    import time
    __IOT_TOKEN__ = "16227124370004660887403726913706840856139"
    __IOT__ = IOT(__IOT_TOKEN__)


    while True:
        print("%s"%(__IOT__.get("com/iot/actuators_Button_1_a")))
        print("%s"%('abc'))
        time.sleep(1)
        print("%s"%(__IOT__.get("com/iot/actuators_Slider_1_b")))
        time.sleep(1)


    
if __name__ == "__main__":
    test()


        
        