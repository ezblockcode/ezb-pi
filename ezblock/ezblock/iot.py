from urllib import request
from urllib import parse
from urllib.request import urlopen
import json

class IOT(object):
    headers = {'Content-Type': 'application/json'}      # 头文件

    url = "https://www.ezblock.sunfounder.com/api/web/v1/"  # 网址链接
    def __init__(self, iot_token, device):                  # 初始化属性，iot_token由ezblock中生成， device有ezblock中定义
        self.iot_token = iot_token
        self.device = device

    def _upload(self, url, data):                           # 上传数据到服务器
        url = self.url+url
        _data = parse.urlencode(data).encode('utf-8')       # utf-8 编码方式
        req = request.Request(url, _data)                   # 发送请求
        response = urlopen(req)                             # 访问网站内容
        result = response.read().decode()                   # 将网站内容解码
        result = json.loads(result)                         # 读取网站数据
        if result["status"] == "true":
            return result["value"]
        else:
            print(result["errorMsg"])

    def post(self, sensorname, value):                      # 上传数据，调用_upload方法
        data = {
            "iotToken": self.iot_token,
            "deviceId": self.device,
            "sensorname": sensorname,
            "value": value,
        }
        # print(data)
        return self._upload("iots/info", data)

    def get(self, sensorname):                              # 获取服务器内容
        data = {
            "iotToken": self.iot_token,
            "deviceId": self.device,
            "sensorname": sensorname,
        }
        print(data)
        value = self._upload("iots/iotget", data)
        try:
            value = int(value)
        except:
            pass
        return value


def test():
    import time
    # print("set to: (epuubHMC3Bj5b0fb, ezblock, temperature), value: 25")
    # IOT('3qNtOfNL07v5Uj59', 'ezblock').post('actuators#Switch#1', 20)         # 上传数据到服务器
    a = IOT('3qNtOfNL07v5Uj59', 'ezblock').get('actuators#Switch#1')            # 然后从服务器上获取上一行代码上传的数据
    # print("get from: (epuubHMC3Bj5b0fb, ezblock, temperature), value: %s"%a)
    print(a)                                                                    # 打印获取的数据内容
    time.sleep(2)


if __name__ == '__main__':
    while True:
        test()
