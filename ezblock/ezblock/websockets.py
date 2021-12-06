import asyncio
from asyncio.tasks import sleep
import websockets

import threading
from multiprocessing import Process, Manager, Value

import sys,os
import time
import json

import RPi.GPIO as GPIO
from ezblock import Pin,Servo,PWM
from .utils import delay,getIP, run_command, log
from .ble import BLE
from configparser import ConfigParser
from .adc import ADC
from .i2c import I2C
from .version import VERSION

detect_i2c = I2C()
i2c_adress_list = list(map(hex, detect_i2c.scan()))

sys.path.append('/opt/ezblock')
from ezb_update import Ezbupdate

mcu_reset = Pin("MCURST")
db_local ='/opt/ezblock/.uspid_init_config'

config = ConfigParser()
ezb_update = Ezbupdate()

message = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1 """

def read_info(key):
    try:
        config.read("/opt/ezblock/ezb-info.ini")
        temp = config["message"][key]
        return temp
    except:
        run_command("sudo touch /opt/ezblock/ezb-info.ini")
        config['DEFAULT'] ={'version':VERSION,
                            'name':"null",
                            'type':"null",
                            'mac':"null"}
        config['message'] ={'version':VERSION}
        with open("/opt/ezblock/ezb-info.ini", 'w') as f:
            config.write(f)
        return None

def write_info(key, value):
    config["message"][key] = value
    with open("/opt/ezblock/ezb-info.ini", "w") as f:
        config.write(f)


class Ezb_Service(object):
    update_flag = Value('d',0) # 0:none 1:ING 2:OK 3:Failed
    update_work = False 
    share_dict = Manager().dict()
    share_dict['debug'] = [None,False]

    @staticmethod
    def reset_mcu_func():
        log('reset_mcu')
        mcu_reset.off()
        time.sleep(0.001)
        mcu_reset.on() 
        time.sleep(0.01)  

    @staticmethod
    def reset_servo():
        Ezb_Service.reset_mcu_func()
        ws.type = read_info("type")
        if ws.type == "SpiderForPi":
            from spider import Spider
            ws.sp = Spider([10,11,12,4,5,6,1,2,3,7,8,9])
            ws.sp.servo_positions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif ws.type == "SlothForPi":
            from sloth import Sloth
            ws.sloth = Sloth([1,2,3,4])
        elif ws.type in ["PiCarMini","PaKe"]:
            from picarx import Picarx
            ws.px = Picarx()       


    @staticmethod
    def ezb_service_start():
        log("Ezb_Service.ezb_service_start")
        ws.user_service_start()
        worker_2 = Process(name='worker 2',target=ws.__start_ws__)
        worker_2.start()
        log("[Process] __start_ws__: %s" % worker_2.pid)
        # this loop is necessary
        while True:
            time.sleep(1)


    @staticmethod
    def start_service():
        log("Ezb_Service.start_service")
        global i2c_adress_list
        Ezb_Service.reset_mcu_func()
        detect_i2c = I2C()
        i2c_adress_list = list(map(hex,detect_i2c.scan()))
        if '0x14' in i2c_adress_list:
            Ezb_Service.reset_servo()
        Ezb_Service.ezb_service_start()

    @staticmethod
    def return_share_val():
        return Ezb_Service.share_dict

    @staticmethod
    def clear_val():
        # Using [ Ezb_Service.share_dict ={} ] is wrong, it will change the address of the object
        Ezb_Service.share_dict.clear()

    @staticmethod
    def set_share_val(item,value):
        item = str(item)
        if item in ["SS", "LB", "MT", "LC", "PC","BC"]:
            if item in list(ws.remote_dict.keys()): # Determines whether the control exists
                if item == 'LC' and value == {}:
                    pass
                else:
                    ws.remote_dict[item][list(value.keys())[0]] = value[list(value.keys())[0]]
                    Ezb_Service.share_dict[item] = ws.remote_dict[item]
            else:
                ws.remote_dict[item] = value
                Ezb_Service.share_dict[item] = value
        else:
            Ezb_Service.share_dict[item] = value

    
class WS():

    def __init__(self):
        self.recv_dict = {}   
        self.send_dict = {}
        self.remote_dict = {}
        self.output_module_dict = {}
        self.user_service_pid = None
        self.websocket_service_pid = None
        self.ws_process = None    
        self.type = None
        self.sp = None
        self.sloth = None
        self.px = None
        self.user_service_process = None
        self.user_service_status = False
        self.voltage = Value('d',0.0)
        self.battery = Value('d',0)
        self.ws_battery_process = None
        self.ws_battery_status = False
        self.is_client_conneted = Value('i',0)

    @staticmethod
    def get_battery(voltage,battery,id='user'):
        def fuc():
            while True:
                voltage.value = min(round(ADC('A4').read() / 4096.0 * 3.3 * 3,2), 8.40)
                battery.value = round(max((voltage.value - 7.0) / 1.4, 0) * 100, 2)
                time.sleep(1)

        log('start getting battery thread by %s process'%id)
        t = threading.Thread(target=fuc)
        t.setDaemon(True)
        t.start()

    # battery
    def ws_battery_process_start(self):
        self.ws_battery_process = Process(name='ws battery',target=self.get_battery,args=(ws.voltage,ws.battery,'websocket'))
        self.ws_battery_process.start()
        self.ws_battery_status = True

    def ws_battery_process_close(self):
        if self.ws_battery_status == True:
            log("[Process] ws_battery_process_close: %s" % self.ws_battery_process.pid)
            self.ws_battery_process.terminate()
            self.ws_battery_status = False

    def main_process(self,voltage,battery):
        # battery    
        self.get_battery(voltage,battery,'user')
        #   
        try:
            from main import forever
            while True:
                forever()
                time.sleep(0.01)
        except Exception as e:
            self.print("Error :%s"%e)
            return False

    def user_service_start(self):
        log("WS.user_service_start")
        if self.ws_battery_status == True:
            self.ws_battery_process_close()
        self.user_service_process = Process(name='user service',target=self.main_process,args=(ws.voltage,ws.battery))
        self.user_service_process.start()
        log("[Process] user_service_start: %s" % self.user_service_process.pid)
        self.user_service_status = True

    def user_service_close(self):
        self.user_service_process.terminate()
        self.user_service_status = False

    def flash(self, name):
        file_dir = '/opt/ezblock/'
        dir = "%s/%s.py"%(file_dir, name)
        with open(dir, 'w') as f:
            f.write(self.recv_dict["DA"])

    def have_update(self):
        def fuc():
            self.send_dict['update'] = ezb_update.get_status()
        t = threading.Thread(target=fuc)
        t.setDaemon(True)
        t.start()

    def data_process(self):
        global i2c_adress_list
        try:  
            # Read data
            if "RE" in self.recv_dict.keys():
                if self.recv_dict['RE'] == "all":               
                    self.send_dict['name'] = read_info("name")
                    self.type = read_info("type")
                    self.send_dict['type'] = self.type
                    self.send_dict['version'] = read_info("version")
                    temp = read_info("mac")
                    if temp == "null":
                        addr = run_command("hciconfig hci0")
                        addr = addr[1].split("BD Address: ")[1].split(" ")[0].strip()
                        write_info("mac", addr)
                    self.send_dict['mac'] = read_info("mac")
                    self.send_dict['ip'] = getIP()
                    self.have_update()
                    self.send_dict['voltage'] = self.voltage.value
                    self.send_dict['battery'] = self.battery.value
                elif self.recv_dict['RE'] == "name":
                    self.send_dict['name'] = read_info("name")
                elif self.recv_dict['RE'] == "type":
                    self.type = read_info("type")
                    self.send_dict['type'] = self.type
                elif self.recv_dict['RE'] == "version":
                    self.send_dict['version'] = read_info("version")
                elif self.recv_dict['RE'] == "battery":
                    self.send_dict['voltage'] = self.voltage.value
                    self.send_dict['battery'] = self.battery.value
                elif self.recv_dict['RE'] == "offset":
                    if read_info("type") in ["PiCarMini","PaKe"]:
                        self.send_dict['offset'] = [dir_cal_value, cam_cal_value_1, cam_cal_value_2]
                self.recv_dict = {}
            # set name
            elif "NA" in self.recv_dict.keys():
                name_temp = self.recv_dict["NA"]
                write_info("name", name_temp)
                self.send_dict["name"] = name_temp
            # set device type
            elif "Type" in self.recv_dict.keys():
                self.type = self.recv_dict["Type"]
                write_info("type", self.type)
                self.send_dict["type"] = self.type
            # reboot       
            elif "RB" in self.recv_dict.keys():
                if self.recv_dict["RB"]:
                    run_command("sudo reboot")  
            # robot calibration 
            elif "OF" in self.recv_dict.keys():
                self.user_service_close()
                self.ws_battery_process_close()
                if self.type in ["PiCarMini","PaKe"]:
                    dir_servo_pin = Servo(PWM('P2'))
                    camera_servo_pin1 = Servo(PWM('P0'))
                    camera_servo_pin2 = Servo(PWM('P1'))
                    if "DO" in self.recv_dict["OF"].keys():
                        if self.recv_dict["OF"]["DO"] == "test":
                            self.px.set_dir_servo_angle(-30)
                            time.sleep(0.5)
                            self.px.set_dir_servo_angle(30)
                            time.sleep(0.5)
                            self.px.set_dir_servo_angle(0)
                            time.sleep(0.5)
                        else:
                            self.px.dir_servo_angle_calibration(int(self.recv_dict["OF"]["DO"]))
                    elif "PO" in self.recv_dict["OF"].keys():
                        self.px.camera_servo1_angle_calibration(int(self.recv_dict["OF"]["PO"]))
                    elif "TO" in self.recv_dict["OF"].keys():
                        self.px.camera_servo2_angle_calibration(int(self.recv_dict["OF"]["TO"]))
                elif self.type == "SpiderForPi":
                    self.sp.cali_helper_web(int(self.recv_dict['OF'][0]), self.recv_dict['OF'][1], int(self.recv_dict['OF'][2]))
                elif self.type == "SlothForPi":
                    self.sloth.set_offset(self.recv_dict['OF'])
                    self.sloth.calibration()
                else:
                    log("Type Error: %s" % self.type)
                self.ws_battery_process_start()   
            # Download code
            elif "FL" in self.recv_dict.keys() and self.recv_dict['FL']:
                # Stop User service
                self.user_service_close()
                self.ws_battery_process_close()

                Ezb_Service.share_dict['SS'] = {}
                Ezb_Service.share_dict['LB'] = {}
                Ezb_Service.share_dict['MT'] = {}
                Ezb_Service.share_dict['LC'] = {}
                Ezb_Service.share_dict['PC'] = {}
                Ezb_Service.share_dict['BC'] = {}
                Ezb_Service.share_dict['SL'] = {}

                if '0x14' in i2c_adress_list:
                    Ezb_Service.reset_mcu_func()
                    self.type = read_info("type")
                    if self.type == "SpiderForPi":
                        pass
                elif '0x74'in i2c_adress_list:
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(24, GPIO.OUT)
                    GPIO.output(24,GPIO.LOW)
                    GPIO.cleanup(24)
                self.flash("main")
                self.user_service_start()
                for _ in range(10): 
                    self.send_dict["CD"] = True
                self.recv_dict['FL'] = False
            # Stop user service
            elif "ST" in self.recv_dict.keys() and self.recv_dict["ST"]:
                # Stop User service
                self.user_service_close()
                if '0x14' in i2c_adress_list:
                    Ezb_Service.reset_servo()
                elif '0x74'in i2c_adress_list:
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(24, GPIO.OUT)
                    GPIO.output(24,GPIO.LOW)
                    GPIO.cleanup(24)
                self.user_service_status = False
                self.send_dict["ST"] = True
                self.recv_dict = {}
                self.ws_battery_process_start()
            # Run user service
            elif "RU" in self.recv_dict.keys() and self.recv_dict["RU"]:
                # Stop User service
                self.user_service_close()

                if not self.user_service_status:
                    if '0x14' in i2c_adress_list:
                        Ezb_Service.reset_mcu_func()
                    elif '0x74'in i2c_adress_list:
                        GPIO.setmode(GPIO.BCM)
                        GPIO.setup(24, GPIO.OUT)
                        GPIO.output(24,GPIO.LOW)
                        GPIO.cleanup(24)
                    self.user_service_start()
                    self.user_service_status = True
                    self.send_dict["RU"] = True
                    self.recv_dict = {}
        #---            
            # heartbeat
            if 'PF' in self.recv_dict.keys() and self.recv_dict['PF']:
                self.send_dict['PF'] = 'pong'  
                self.recv_dict = {} 
            # Update Ezblock
            if "UE" in self.recv_dict.keys():
                if self.recv_dict["UE"] and Ezb_Service.update_work == False:
                    Ezb_Service.update_work = True 
                else:
                    self.send_dict["UE"] = 'Failed'
            if Ezb_Service.update_work == True:
                log('Updating ...')
                log('Ezb_Service.update_flag.value: %s'% Ezb_Service.update_flag.value)
                if Ezb_Service.update_flag.value == 0: # 0:none 1:ING 2:OK 3:Failed
                    self.update_process = Process(name='update_process',target=self.update_ezblock,args=(Ezb_Service.update_flag,))
                    self.update_process.start()
                    log('update_process start, pid = %s'% self.update_process.pid)
                    Ezb_Service.update_flag.value = 1
                elif Ezb_Service.update_flag.value == 1: #  1:ING 
                    self.send_dict["UE"] = 'ING'
                elif Ezb_Service.update_flag.value == 2: #  2:OK   
                    self.send_dict["UE"] = 'OK'
                    Ezb_Service.update_work = False
                    self.update_process.terminate()
                    self.send_dict['version'] = read_info("version")
                    Ezb_Service.update_flag.value = 0
                elif Ezb_Service.update_flag.value == 3: #  3:Failed
                    self.send_dict["UE"] = 'Failed'
                    Ezb_Service.update_work = False
                    self.update_process.terminate()
                    Ezb_Service.update_flag.value = 0
        except OSError as e:
            log(e,level='ERROR')
            Ezb_Service.reset_mcu_func()
            time.sleep(1)
        except Exception as e:
            log(e,level='ERROR')   

            
    async def main_logic(self, websocket,path):
        log('client conneted')
        self.is_client_conneted.value = True
        # battery 
        if self.user_service_status == False and self.ws_battery_status == False:
            self.ws_battery_process_start()

        while True:
            try: #  to catch websockets.exceptions.ConnectionClosed 
                # recv
                try:
                    tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                except asyncio.TimeoutError as e:
                    # log('asyncio.TimeoutError : %s'%e)
                    pass

                # Received and data processing
                try:   
                    tmp = json.loads(str(tmp))                    
                    self.recv_dict = tmp
                    log("recv_data_load:%s"%tmp,'websockets')

                    # heartbeat
                    if 'PF' in tmp.keys() and tmp['PF']:
                        self.send_dict['PF'] = 'pong'  

                    # data processing
                    self.data_process()              
                    for key in tmp.keys():
                        if key in ["JS", "SL", "DP", "BT", "SW"]:
                            if key in list(self.remote_dict.keys()): # Determines whether the control exists
                                self.remote_dict[key][list(tmp[key].keys())[0]] = tmp[key][list(tmp[key].keys())[0]]
                                Ezb_Service.set_share_val(key,self.remote_dict[key])
                            else:
                                self.remote_dict[key] = tmp[key]
                                Ezb_Service.set_share_val(key,self.remote_dict[key])
                except Exception as e:
                    # log(e)
                    pass

                # send           
                try:
                    if self.send_dict != {}:
                        data = self.send_dict
                        log('send data: %s'% data)
                    else:
                        data = Ezb_Service.return_share_val()

                    data = dict(data)
                    await websocket.send(json.dumps(data))

                    if 'debug' in data.keys():
                        if data['debug'][1] == True:
                            Ezb_Service.set_share_val('debug',[data['debug'][0],False])
                    if 'LC' in data.keys():
                        LC_list = list(data['LC'].keys())
                        if  LC_list != []:
                            for i in LC_list:
                                if data['LC'][i][-1] == True:
                                    data['LC'][i][-1] = False
                                    Ezb_Service.set_share_val('LC',data['LC'])
                    if self.send_dict != {} and data == self.send_dict:
                        self.send_dict = {} 
                except KeyboardInterrupt:
                    pass
            # disconneted exception
            except websockets.exceptions.ConnectionClosed as connection_code:
                log(connection_code)
                self.is_client_conneted.value = False
                log('client disconneted')
                Ezb_Service.clear_val()
                break   
            await asyncio.sleep(0.01)

    def print(self, msg, end='\n', tag='[DEBUG]'):
        log(msg)
        Ezb_Service.set_share_val('debug',[str(msg),True])
        while Ezb_Service.return_share_val()['debug'][1] == True:
            time.sleep(0.01)

    def close_tcp_port(self,port=8765):
        # check port
        results = os.popen("sudo lsof -i:%s|grep %s|awk '{print $2}'"%(port,port)).readlines()
        if results == []:
            log('no process occupies port %s'%port)
        else:
            # close related processes
            log('port 8765 is already occupied,try to close related processes ...')
            for pid in results:
                log('kill %s .... '%pid.replace('\n',''),end='')
                status = os.system('sudo kill %s'%pid)
                if status == 0:
                    log('succeed',timestamp=False)
                else:
                    log('failed',timestamp=False)
                    return False
        return True


    def start_loop(self, ip):
        port = 8765
        # check port
        while not self.close_tcp_port(port):
            time.sleep(0.01)
        # start websockets
        log('open websockets server')
        start_server_1 = websockets.serve(self.main_logic, ip, port)
        tasks = [start_server_1]
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(asyncio.wait(tasks))
        self.loop.run_forever()


    # start websocket_service_process
    def websocket_service_process(self):
        if self.ws_battery_status == True:
            self.ws_battery_process_close()
        Ezb_Service.reset_mcu_func()
        self.ws_process = Process(name='websocket service',target=self.start_loop,args=('0.0.0.0', )) # args=(ip, ) ：This is a tuple, the ',' is necessary !!!
        self.ws_process.start()
        self.websocket_service_pid = self.ws_process.pid
        log("[Process] websocket_service_process: %s" % self.websocket_service_pid)

    def __start_ws__(self):
        log("WS.__start_ws__")
        while True:
            try :
                ip = getIP()
                if ip and self.ws_process == None:
                    log("got ip: %s " % ip)
                    self.websocket_service_process()

                value = ""
                raw_data = ble.read(1).decode()
                if raw_data != "":
                    while True:
                        value = value + raw_data
                        raw_data = ble.read(1).decode()
                        if raw_data == "\n":
                            break
                if value == "":
                    time.sleep(0.05)
                    continue

                log("ble read value: %s" % value)
                if value == "get":
                    if ip:
                        log("ble write value: %s" % ip)
                        ble.write(ip)
                    else:
                        log("ble write value: No IP")
                        ble.write("No IP")
                elif value:
                    try:
                        if self.ws_process != None:
                            self.ws_process.terminate()

                        data_list = value.split("#*#")
                        from .wifi import WiFi
                        wifi = WiFi()
                        # Connect the wifi
                        if wifi.write(*data_list) == True:
                            # start websocket_service
                            for _ in range(3):
                                ip = getIP()
                                if ip:
                                    log("IP Address: %s" % ip)
                                    self.websocket_service_process()
                                    log("ble write value:%s"%ip)
                                    ble.write(ip)
                                    break
                                time.sleep(1)
                            else:
                                log("ble write value:Connect Failed!")
                                ble.write("Connect Failed!")
                        else:
                            log("ble write value:Connect Failed!")
                            ble.write("Connect Failed!")
                    except Exception as e:
                        log("WS.__start_ws__ failed: %s" % e)
            except Exception as e:
                # ble.write("Connect Failed!")
                log("WS.__start_ws__ failed: %s" % e)
        
    def update_ezblock(self,update_flag):
        update_flag.value = 1  # 1:ING
        flag = ezb_update.update()
        if flag == True:
            update_flag.value = 2 # 2:OK
        else:
            update_flag.value = 3 # 3:Failed

ws = WS()
ble = BLE()

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
        temp = {}
        temp = Ezb_Service.return_share_val()
        
        self.recv_dict = temp

        if self.recv_dict != None:
            data = self.recv_dict.get(name,None)
            if data == None:
                return None
            value = data.get(id,None)
            return value
        else:
            return 0
        
    
    def get_joystick_value(self, id, coord):
        _value = self.get_data("JS", id)
        if _value != None:
            if coord == 'X':
                return int(_value[0])
            elif coord == 'Y':
                return int(_value[1])
            else:
                return 0
        else:
            return 0
    
    def get_slider_value(self, id):
        _value = self.get_data("SL", id)
        if _value == None:
            return 0
        _value = int(_value)
        return _value
    
    def get_dpad_value(self, id, direction):
        _value = self.get_data("DP", id)
        if _value != None:
            if direction == _value:
                return 1
            else:
                return 0
        else:
            return None
        
    def get_button_value(self, id):
        _value = self.get_data("BT", id)
        if _value == None:
            return None
        _value = int(_value)
        return _value
    
    def get_switch_value(self, id):
        _value = self.get_data("SW", id)
        if _value == None:
            return None
        _value = int(_value)
        return _value
        
    def set_segment_value(self, id, value):
        if not (isinstance(value, (int, float, str))):
            raise ValueError("segment value must be number, int or float")
        ws.send_dict['SS'] = {"%s"%id: value}
        Ezb_Service.set_share_val('SS',ws.send_dict['SS'])
    
    def set_light_bolb_value(self, id, value):
        if not (value in [0, 1] or isinstance(value, bool)):
            raise ValueError("light bolb value must be 0/1 or True/False")
        ws.send_dict['LB'] = {"%s"%id: value}
        Ezb_Service.set_share_val('LB',ws.send_dict['LB'])
    
    def set_meter_value(self, id, value):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("meter value must be number, int or float")
        ws.send_dict["MT"] = {"%s"%id: value}
        Ezb_Service.set_share_val("MT",ws.send_dict["MT"])
    
    def set_line_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("line chart value must be list of name value pair, not %s"%type(value))
        ws.send_dict["LC"] = {"%s"%id: [value,True]}
        Ezb_Service.set_share_val("LC",ws.send_dict["LC"])

        if Ezb_Service.return_share_val()['LC'] != {}:
            LC_keys_list = list(Ezb_Service.return_share_val()['LC'].keys())
            while LC_keys_list[0][-1] == True:
                time.sleep(0.001)
            time.sleep(0.15)
    
    def set_pie_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("pie chart value must be list of name value pair not %s"%type(value))
        ws.send_dict["PC"] = {"%s"%id: value}
        Ezb_Service.set_share_val("PC",ws.send_dict["PC"])
    
    def set_bar_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("bar_chart value must be list of numbers, int or float")
        ws.send_dict["BC"] = {"%s"%id: value}
        Ezb_Service.set_share_val("BC",ws.send_dict["BC"])
