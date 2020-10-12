import requests
import json

class IOT(object):
    headers = {'Content-Type': 'application/json'}      # Header

    # url = "https://www.ezblock.sunfounder.com/api/web/v1/"  # API Url
    url =  'https://test2.ezblock.com.cn:11000/api/web/v2/ezblock/'
    def __init__(self, iot_token):
        self.iot_token = iot_token

    def _upload(self, url, data):
        url = self.url+url
        headers={'Content-Type': 'application/json'}
        r = requests.post(url, json=data, headers=headers)
        result = r.content.decode('utf-8')
        print(result)
        result = json.loads(result)
        if result["code"] == 200:
            data = result["data"]
            value = data["value"]
            print(data)
            return value
        else:
            print("Error[%s]"%result["code"])
            if result["code"] == 10302:
                return None

    def post(self, sensorname, value):
        data = {
            "name":sensorname,
            "iotToken":self.iot_token,
            "value":value,
        }
        return self._upload("iot/upload", data)

    def get(self, sensorname):
        data = {
            "name": sensorname,
            "iotToken": self.iot_token,
        }
        value = self._upload("iot/get", data)
        print(value)
        try:
            value = int(value)
        except:
            pass
        return value

# def test():
#     from ezblock import print
#     import random
    
#     __IOT_TOKEN__ = "6a31ef81850642d980fceb14a974e087XX1600395165796"
#     __IOT__ = IOT(__IOT_TOKEN__, "raspberrypi")
  
#     print("%s"%(__IOT__.get("actuators#Switch#1")))
#     __IOT__.post("actuators#Switch#1", (random.randint(1, 100)))

# if __name__ == "__main__":
#     test()