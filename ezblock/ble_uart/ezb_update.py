import requests
import json
# from ezblock import run_command
from configparser import ConfigParser

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

class Ezbupdate(object):
    headers = {'Content-Type': 'application/json'}      # Header

    def __init__(self,url = 'https://test2.ezblock.com.cn:11000/api/web/v2/ezblock/get/last/version'):
        # self.iot_token = iot_token
        # self.url = url + "ezblock/"
        # self.iot_token = iot_token
        self.cfg = ConfigParser()
        self.file_address = "/opt/ezblock/ezb-info.ini"
        self.url = url

    def _upload(self, data):
        # url = self.url+url
        url = self.url
        headers={'Content-Type': 'application/json'}
        r = requests.post(url, json=data, headers=headers)
        # print(r)
        result = r.content.decode('utf-8')
        # print("st")
        # print("result:",result)
        self.result = json.loads(result)
        # print(type(result["data"]["version"]))
        # print("Create workspace")
        _, command_result = run_command("ls /opt/ezblock/ezb-info.ini")
        if _ != 0:
            run_command("sudo touch /opt/ezblock/ezb-info.ini")
            self.cfg['message'] ={'version':"1.10"}
            with open(self.file_address, 'w') as f:
                self.cfg.write(f)

        self.cfg.read(self.file_address)
        version_message = dict(self.cfg.items("message"))
        # print("local: ",version_message['version'])
        # print(version_message['version'])
        # print(result['data']['version'])
        if float(version_message['version']) == float(self.result['data']['version']):
            print("pass")
            return False
        else:
            print("update")
            return True
    
    def update(self):
        download_command = "sudo wget " + self.result['data']['url'] + " -O /opt/ezblock/" + self.result['data']['description'] + ".zip"
        # print(download_command)
        run_command(download_command)
        unzip_command = "sudo unzip -o /opt/ezblock/" + self.result['data']['description'] + '.zip' + " -d /opt/ezblock/"
        # print(unzip_command)
        run_command(unzip_command)
        # print("sudo unzip -o /opt/ezblock/" + self.result['data']['description'] + '.zip' + " -d /opt/ezblock/")
        # print("sudo python3 /opt/ezblock/" + self.result['data']['description'] + "/" + self.result['data']['description'] + ".py")
        update_conmmand = "sudo python3 /opt/ezblock/" + self.result['data']['description'] + "/" + self.result['data']['description'] + ".py"
        # update_conmmand = "sudo python3 /opt/ezblock/" + self.result['data']['description'] + "/" + "update_test" + ".py"
        # print(update_conmmand)
        run_command(update_conmmand)
        self.cfg.set('message', 'version', self.result['data']['version'])
        with open(self.file_address, 'w') as self.file_address:
            self.cfg.write(self.file_address)
            
    def get_status(self):
        data = {
             "value": 200,
             "message": "success",
             "data": {
            "id": 8,
            "version": "1.5",
            "url": "https://test2.ezblock.com.cn/version/4.rar",
            "description": "hello",
            "creattime": "17"
                }
            }
        status = self._upload(data)
        return status

if __name__ == "__main__":
    a_iot = Ezbupdate()
    status = a_iot.get_status()
    print(status)
    # print(b["url"])
    # print("ok")
