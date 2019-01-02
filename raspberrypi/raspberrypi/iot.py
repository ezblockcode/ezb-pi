from urllib import request
from urllib import parse
from urllib.request import urlopen
import json

class IOT(object):
    headers = {'Content-Type': 'application/json'}

    url = "https://www.ezblock.sunfounder.com/api/web/v1/"
    def __init__(self, iot_token, device):
        self.iot_token = iot_token
        self.device = device

    def _upload(self, url, data):
        url = self.url+url
        _data = parse.urlencode(data).encode('utf-8')
        req = request.Request(url, _data)
        response = urlopen(req)
        result = response.read().decode()
        result = json.loads(result)
        if result["status"]:
            return result["value"]
        else:
            print(result["errorMsg"])

    def post(self, sensorname, value):
        data = {
            "iotToken": self.iot_token,
            "deviceId": self.device,
            "sensorname": sensorname,
            "value": value,
        }
        # print(data)
        return self._upload("iots/info", data)

    def get(self, sensorname):
        data = {
            "iotToken": self.iot_token,
            "deviceId": self.device,
            "sensorname": sensorname,
        }
        print(data)
        value = self._upload("iots/iotget", data)
        value = int(value)
        return value


def test():
    import time
    # print("set to: (epuubHMC3Bj5b0fb, raspberrypi, temperature), value: 25")
    # IOT('3qNtOfNL07v5Uj59', 'raspberrypi').post('actuators#Switch#1', 20)
    a = IOT('3qNtOfNL07v5Uj59', 'raspberrypi').get('actuators#Switch#1')
    # print("get from: (epuubHMC3Bj5b0fb, raspberrypi, temperature), value: %s"%a)
    print(a)
    time.sleep(2)


if __name__ == '__main__':
    while True:
        test()
