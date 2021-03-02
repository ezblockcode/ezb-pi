import asyncio
import websockets
import json
import time
from .utils import getIP, run_command
import os
from multiprocessing import Process, Manager, Queue
from .ble import BLE
from configparser import ConfigParser
from .adc import ADC
import sys
# sys.path.append(r'/home/pi/ezb-pi/workspace')
sys.path.append(r'/opt/ezblock')
import picarx as car
from ezb_update import Ezbupdate



ble = BLE()
config = ConfigParser()
ezb = Ezbupdate()

TAIL = """\
if __name__ == "__main__":
  try:
    while True:
      forever()
  except KeyboardInterrupt:
    from ezblock import print
    print("Program stops")
  except Exception as e:
    from ezblock import print
    print(e, tag="[ERROR]")
"""

def read(key):
    _, command_result = run_command("ls /opt/ezblock/ezb-info.ini")
    if _ != 0:
        run_command("sudo touch /opt/ezblock/ezb-info.ini")
        config['DEFAULT'] ={'version':"1.10",
                            'name':"null",
                            'type':"null",
                            'mac':"null"}
        config['message'] ={'version':"1.10"}
        with open("/opt/ezblock/ezb-info.ini", 'w') as f:
            config.write(f)
    config.read("/opt/ezblock/ezb-info.ini")
    temp = config["message"][key]
    return temp

def write(key, value):
    config["message"][key] = value
    with open("/opt/ezblock/ezb-info.ini", "w") as f:
        config.write(f)

class WS():
    
    def __init__(self):
        self.recv_dict = {}   
        self.send_dict = {}
        self.recv_queue = Queue()
        self.send_queue = Queue()
        self.user_service_pid = 0
        self.service_status = True
    
    def main_process(self):
        try:
            from main import forever
            while True:
                forever()
                time.sleep(0.01)
        except Exception as e:
            # for _ in range(3):
            self.print("Error :%s"%e)
            # self.user_service.join()
    
    def user_service_start(self):
        self.user_service = Process(name='user service',target=self.main_process)
        self.user_service.start()
        self.user_service_pid = self.user_service.pid
        # print("user_service_start: %s"%self.user_service_pid)
        
    def flash(self, name):
        file_dir = '/opt/ezblock/'
        dir = "%s/%s.py"%(file_dir, name)
        with open(dir, 'w') as f:
            f.write(self.recv_dict["DA"] + TAIL)
            
    def send_data(self):
        if "RE" in self.recv_dict.keys():
            if self.recv_dict['RE'] == "all":
                self.send_dict['name'] = read("name")
                self.send_dict['type'] = read("type")
                self.send_dict['version'] = read("version")
                temp = read("mac")
                if temp == "null":
                    addr = run_command("hciconfig hci0")
                    addr = addr[1].split("BD Address: ")[1].split(" ")[0].strip()
                    write("mac", addr)
                self.send_dict['mac'] = read("mac")
                self.send_dict['battery'] = round(ADC('A4').read() / 4096.0 * 3.3 * 3,2)
                self.send_dict['ip'] = getIP()
                self.send_dict['update'] = ezb.get_status()
            elif self.recv_dict['RE'] == "name":
                self.send_dict['name'] = read("name")
            elif self.recv_dict['RE'] == "type":
                self.send_dict['type'] = read("type")
            elif self.recv_dict['RE'] == "version":
                self.send_dict['version'] = read("version")
            elif self.recv_dict['RE'] == "battery":
                self.send_dict['battery'] = round(ADC('A4').read() / 4096.0 * 3.3 * 3,2)
            elif self.recv_dict['RE'] == "offset":
                self.send_dict['offset'] = [car.dir_cal_value, car.cam_cal_value_1, car.cam_cal_value_2]
            # self.send_queue.put(self.send_dict, block=False)
        if "NA" in self.recv_dict.keys():
            name_temp = self.recv_dict["NA"]
            write("name", name_temp)
            self.send_dict["name"] = name_temp
            # self.send_queue.put(self.send_dict, block=False)
        if "Type" in self.recv_dict.keys():
            type_temp = self.recv_dict["Type"]
            write("type", type_temp)
            self.send_dict["type"] = type_temp
            # self.send_queue.put(self.send_dict, block=False)
        if "UD" in self.recv_dict.keys():
            if self.recv_dict["UD"]:
                ezb.update()
        if "OF" in self.recv_dict.keys():
            if read("type") == "PiCarMini":
                if "DO" in self.recv_dict["OF"].keys():
                    if self.recv_dict["OF"]["DO"] == "test":
                        car.set_dir_servo_angle(-30)
                        time.sleep(0.2)
                        car.set_dir_servo_angle(30)
                        time.sleep(0.4)
                        car.set_dir_servo_angle(0)
                    else:
                        car.dir_servo_angle_calibration(int(self.recv_dict["OF"]["DO"]))
                elif "PO" in self.recv_dict["OF"].keys():
                    car.camera_servo1_angle_calibration(int(self.recv_dict["OF"]["PO"]))
                elif "TO" in self.recv_dict["OF"].keys():
                    car.camera_servo2_angle_calibration(int(self.recv_dict["OF"]["TO"]))
       
    async def main_loop_frame(self):
        while 1:
            if "FL" in self.recv_dict.keys():
                if self.recv_dict['FL']:
                    # print(self.user_service_pid)
                    run_command("sudo kill {}".format(self.user_service_pid))
                    self.flash("main")
                    self.user_service_start()
                    for _ in range(10): 
                        self.send_dict["CD"] = True
                        # self.send_queue.put(self.send_dict, block=False)
                    self.recv_dict['FL'] = False
            # self.main_loop()
            await asyncio.sleep(0.001)
            

    async def main_logic(self, websocket, path):
        while 1:
            # print("main_logic_loop")
            try:
                tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                tmp = json.loads(tmp)
                print("recv_data_load:%s"%tmp)
                self.recv_dict = tmp
                self.send_data()
                self.recv_queue.put(tmp, block=False)
            except:
                pass
           
            try:
                if self.send_dict:
                    data = self.send_dict
                else:
                    data = self.send_queue.get(block=True, timeout=0.001)
                print("send_data:%s"%data)
                await websocket.send(json.dumps(data))
                self.send_dict = {} 
            except:
                pass
            # self.send_dict = {}
            # await asyncio.sleep(0.01)

            
    def start_loop(self, ip): 
        start_server_1 = websockets.serve(self.main_logic, ip, 8765)
        print('Websockets Start!')
        tasks = [self.main_loop_frame(), start_server_1]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
        asyncio.get_event_loop().run_forever()

    def print(self, msg, end='\n', tag='[DEBUG]'):
        _msg = "Ezblock [{}] [DEBUG] {}".format(time.asctime(), msg)
        os.system("echo {} >> /opt/ezblock/log".format(_msg))
        self.send_dict['debug'] = msg
        self.send_queue.put(self.send_dict, block=False)
        print("ws_print_send_dict: %s" % self.send_dict)
        # self.send_dict = {}
    
    
    def __start_ws__(self):
        while True:
            ip = getIP()
            if ip:
                if self.service_status:
                    service = Process(name='websocket service',target=self.start_loop,args=(ip,))
                    service.start()
                    self.service_status = False
            value = ""
            raw_data = ble.read(1).decode()
            if raw_data != "":
                while True:
                    value = value + raw_data
                    raw_data = ble.read(1).decode()
                    if raw_data == "\n":
                        break
            if value == "":
                continue
            print("value: "+value)
            if value == "get":
                if ip:
                    ble.write(ip)
                else:
                    ble.write("No IP")
            elif value:
                temp_index = value.index("#*#")
                country = value[:temp_index]
                temp_data = value[(temp_index+3):]
                index = temp_data.index("#*#")
                ssid = temp_data[:index]
                password = temp_data[(index+3):]
                from .wifi import WiFi
                wifi = WiFi()
                wifi.write(country, ssid, password)
                for _ in range(3):
                    ip = getIP()
                    if ip:
                        print("IP Address: "+ ip)
                        break
                    time.sleep(1)
                if ip:
                    ble.write(ip)
                    # break
                else:
                    ble.write("Connect Failed!")
        

ws = WS()

def ws_print(msg, end='\n', tag='[DEBUG]'):
    ws.print(msg, end, tag)

class Remote():
    
    def __init__(self):
        self.recv_dict = {
            "JS":{},
            "SL":{},
            "DP":{},
            "BT":{},
            "SW":{},
        }   
    
    def read(self): # deprecated 
        pass
    
    def get_data(self, name, id):
        try:
            temp = ws.recv_queue.get(block=True, timeout=0.001)
            for key in temp[name]:
                self.recv_dict[name][key] = temp[name][key]
        except:
            pass
        # if name not in temp.keys():
        #     return
        if id not in self.recv_dict[name].keys():
            return
        value = self.recv_dict[name][id]
        return value
    
    def get_joystick_value(self, id, coord):
        value = self.get_data("JS", id)
        if coord == 'X':
            return int(value[0])
        elif coord == 'Y':
            return int(value[1])
        else:
            return 0
    
    def get_slider_value(self, id):
        _value = int(self.get_data("SL", id))
        return _value
    
    def get_dpad_value(self, id, direction):
        _value = self.get_data("DP", id)
        if direction == _value:
            return 1
        else:
            return 0
        
    def get_button_value(self, id):
        _value = int(self.get_data("BT", id))
        return _value
    
    def get_switch_value(self, id):
        _value = int(self.get_data("SW", id))
        return _value
        
    def set_segment_value(self, id, value):
        if not (isinstance(value, (int, float, str))):
            raise ValueError("segment value must be number, int or float")
        ws.send_dict['SS'] = {"%s"%id: value}
        # ws.send_dict['SG'][id] = value
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}
    
    def set_light_bolb_value(self, id, value):
        if not (value in [0, 1] or isinstance(value, bool)):
            raise ValueError("light bolb value must be 0/1 or True/False")
        ws.send_dict['LB'] = {"%s"%id: value}
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}
    
    def set_meter_value(self, id, value):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("meter value must be number, int or float")
        ws.send_dict["MT"] = {"%s"%id: value}
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}
    
    def set_line_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("line chart value must be list of name value pair, not %s"%type(value))
        ws.send_dict["LC"] = {"%s"%id: value}
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}
    
    def set_pie_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("pie chart value must be list of name value pair not %s"%type(value))
        ws.send_dict["PC"] = {"%s"%id: value}
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}
    
    def set_bar_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("bar_chart value must be list of numbers, int or float")
        ws.send_dict["BC"] = {"%s"%id: value}
        ws.send_queue.put(ws.send_dict, block=False)
        # self.send_dict = {}

# if __name__ == '__main__':
#     web = WS()