import websockets
import asyncio
from multiprocessing import Process, Manager, Value
import threading
from configparser import ConfigParser
import json
import time
import sys,os
import RPi.GPIO as GPIO
from .utils import delay, getIP, run_command, log
from .ble import BLE
from ezblock import Pin, PWM, Servo, I2C, ADC, VERSION
from .user_info import USER, USER_HOME

log(f"user:{USER}")
log(f"userhome:{USER_HOME}")

# port = 8765  # version == 1.0.x
port = 7852    # SiTianJiChuang, version >= 1.1.x

def _log(msg:str, location='websokcets', end='\n', flush=False, timestamp=True, color=''):
    log(msg, location, end='\n', flush=False, timestamp=True, color=color)

# select LED lights foe websockets status
# according to the Robot-Hat expansion board
check_io = Pin('D13')
check_io.mode(check_io.IN)
if check_io.value() == 1:  # old board
    ws_status_led = Pin("LED")
    # close external bluetooth
    ble_reset = Pin("D20")
    tx = Pin(14);rx = Pin(15)
    tx.off();rx.off()
    ble_reset.off()
    # _log('old robot_hat')
else: # new board
    ws_status_led = Pin("LED")
    # _log('new robot_hat')
 
# tools
def music_by_system(path:str, is_background=False):
    def mp(path:str):
        try:
           run_command('sudo mplayer %s'%path)
        except Exception as e:
            _log(e, location='Sound effect')
    
    if is_background == True:
        t =  threading.Thread(target=mp, args=(path,))
        t.setDaemon(True)
        t.start()
    else:
        mp(path)

# detect_i2c
detect_i2c = I2C()
i2c_adress_list = list(map(hex, detect_i2c.scan()))

sys.path.append(r'/opt/ezblock')
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
                            'mac':"null",
                            'auto-run':"False",}
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
        mcu_reset.off()
        time.sleep(0.001)
        mcu_reset.on()
        time.sleep(0.2)

    @staticmethod
    def reset_servo():
        Ezb_Service.reset_mcu_func()
        ws.type = read_info("type")
        log('Products type: %s'%ws.type, location='reset_servo')
        try:
            # delete i2c
            for _ in range(3):
                i2c_adress_list = list(map(hex, detect_i2c.scan()))
                log('i2c_adress_list: %s'%i2c_adress_list, location='reset_servo')
                if '0x14' in i2c_adress_list:
                    break
                time.sleep(0.2)
            else:
                log("I2C 0x14 not found", location='reset_servo', color='31')
                return False
            # Products init
            if ws.type == "SpiderForPi":
                log("spider init", location='reset_servo')
                from spider import Spider
                ws.sp = Spider([10,11,12,4,5,6,1,2,3,7,8,9])
                ws.sp.servo_positions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            elif ws.type == "SlothForPi":
                log("sloth init", location='reset_servo')
                from sloth import Sloth
                ws.sloth = Sloth([1,2,3,4])
            elif ws.type in ["PiCarMini","PaKe"]:
                log("picarx init", location='reset_servo')
                from picarx import PiCarX
                ws.px = PiCarX()
            return True
        except Exception as e:
            _log('reset_servo error for %s:%s'%(ws.type, e), location='reset_servo', color='31')
            Ezb_Service.set_share_val('debug', [str(e), True])
            return False


    @staticmethod
    def ezb_service_start():
        _log("Ezb_Service.ezb_service_start")
        # Service startup Sound
        music_by_system(f'{USER_HOME}/Music/startup.mp3')
        # whether auto-run main.py
        if read_info("auto-run") in ["True", "true", "TRUE", "1", "on", "ON"]:
            _log("WS.user_service_start auto-run")
            ws.user_service_start()
        else:
            _log("WS.user_service_start does not auto-run")
        worker_2 = Process(name='worker 2',target=ws.__start_ws__)
        worker_2.start()
        _log("[Process] __start_ws__: %s" % worker_2.pid)
        # this loop is necessary
        while True:
            time.sleep(1)


    @staticmethod
    def start_service():
        _log("Ezb_Service.start_service")
        Ezb_Service.reset_mcu_func()
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
        self.user_service_status = False
        self.type = None
        self.app_version = None
        self.sp = None
        self.sloth = None
        self.px = None
        self.user_service_process = None
        self.voltage = Value('d',0.0)
        self.battery = Value('d',0)
        self.ws_battery_process = None
        self.ws_battery_status = False
        self.is_client_connected = Value('i',0)
        self.connect_num = 0
        self.ble = None


    @staticmethod
    def get_battery(voltage,battery):
        voltage.value = round(ADC('A4').read() / 4095.0 * 3.3 * 3,2)
        battery.value = round(min(max((voltage.value - 7.0) / 1.4, 0) * 100,100),2)


    @staticmethod
    def get_battery_thread(voltage,battery,id='user'):
        def fuc():
            while True:
                voltage.value = round(ADC('A4').read() / 4095.0 * 3.3 * 3,2)
                battery.value = round(min(max((voltage.value - 7.0) / 1.4, 0) * 100,100),2)
                time.sleep(2)

        _log('start getting battery thread by %s process'%id)
        t = threading.Thread(target=fuc)
        t.setDaemon(True)
        t.start()

    # battery
    def ws_battery_process_start(self):
        self.ws_battery_process = Process(name='ws battery',target=self.get_battery_thread,args=(self.voltage, self.battery, 'websocket'))
        self.ws_battery_process.start()
        _log("[Process] ws_battery_process_start: %s" % self.ws_battery_process.pid)
        self.ws_battery_status = True

    def ws_battery_process_close(self):
        if self.ws_battery_status == True:
            _log("[Process] ws_battery_process_close: %s" % self.ws_battery_process.pid)
            self.ws_battery_process.terminate()
            self.ws_battery_status = False

    def main_process(self, voltage, battery):
        try:
            from main import forever
            start_time = time.time()
            while True:
                if (time.time() - start_time) > 5:
                    self.get_battery(voltage, battery)
                    start_time = time.time()
                forever()
                time.sleep(0.01)
        except Exception as e:
            Ezb_Service.reset_servo()
            self.user_service_status = False
            self.print("Error :%s"%e, color='31')
            return False


    def user_service_start(self):
        self.user_service_close()
        if self.ws_battery_status == True:
            self.ws_battery_process_close()
        self.user_service_process = Process(name='user service',target=self.main_process,args=(ws.voltage,ws.battery))
        self.user_service_process.start()
        _log("[Process] user_service_start: %s" % self.user_service_process.pid)
        self.user_service_status = True


    def user_service_close(self):
        if self.user_service_status == True:
            self.user_service_process.terminate()
            self.user_service_status = False

    def flash(self, name):
        file_dir = '/opt/ezblock/'
        dir = "%s/%s.py"%(file_dir, name)
        with open(dir, 'w') as f:
            f.write(self.recv_dict["DA"])

    def have_update(self):
        def fuc():
            if self.app_version == None:
                self.send_dict['update'] = False
            else:
                self.send_dict['update'] = ezb_update.get_status(self.app_version)
        t = threading.Thread(target=fuc)
        t.setDaemon(True)
        t.start()

    def str_limit(self,string:str):
        import re
        # remove the first space and line break, maximum length: 64 characters
        string = string.strip()[0:64]
        # only keep the English letters (a-z,A-Z) and numbers (0-9) and '-'
        compile = re.compile('[^A-Z^a-z^0-9^\-]')
        return compile.sub('', string)


    def data_process(self):
        global i2c_adress_list
        try:
            # Read data
            if "APP" in self.recv_dict.keys():
                self.app_version = self.recv_dict["APP"]
            if "RE" in self.recv_dict.keys():
                # info
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
                    self.send_dict['auto-run'] = read_info("auto-run")
                    self.send_dict['ip'] = getIP()
                    self.have_update()  # have_update thread
                    self.send_dict['voltage'] = '%.2f'%self.voltage.value
                    self.send_dict['battery'] = self.battery.value
                elif self.recv_dict['RE'] == "name":
                    self.send_dict['name'] = read_info("name")
                elif self.recv_dict['RE'] == "type":
                    self.type = read_info("type")
                    self.send_dict['type'] = self.type
                elif self.recv_dict['RE'] == "version":
                    self.send_dict['version'] = read_info("version")
                elif self.recv_dict['RE'] == "battery":
                    self.send_dict['voltage'] = '%.2f'%self.voltage.value
                    self.send_dict['battery'] = self.battery.value
                elif self.recv_dict['RE'] == "offset":
                    self.user_service_close()
                    self.ws_battery_process_close()
                    if self.type in ["PiCarMini","PaKe"]:
                        self.px.set_steering_angle(0)
                        self.px.set_camera_pan_angle(0)
                        self.px.set_camera_tilt_angle(0)
                        self.send_dict['offset'] = [self.px.dir_cali_value, self.px.cam_cali_value_1, self.px.cam_cali_value_2]
                    elif self.type in ["SpiderForPi"]:
                        # _init_coord = [ [a+b for a,b in zip(self.sp.default_coord[i],self.sp.cali_coord[i])] for i in range(4)]
                        _init_coord = list.copy(self.sp.cali_default_coord)
                        self.sp.do_step(_init_coord, 80)
                        self.send_dict['coord_offset'] = list(self.sp.coord_offset)
                    elif self.type in ["SlothForPi"]:
                        self.sloth.servo_move([0, 0, 0, 0])
                        self.send_dict['offset'] = list(self.sloth.offset)
            # set name
            elif "NA" in self.recv_dict.keys():
                try:
                    _,hostname = run_command("sudo hostname")
                    name_temp = self.recv_dict["NA"]
                    name_temp = self.str_limit(name_temp)
                    write_info("name", name_temp)
                    run_command('sudo hostnamectl set-hostname %s'%name_temp)
                    _log("change name to : %s"%name_temp)
                    self.send_dict["name"] = name_temp
                except Exception as e:
                    _log('set-hostname failed: %s'%e)
            # set device type
            elif "Type" in self.recv_dict.keys():
                self.type = self.recv_dict["Type"]
                write_info("type", self.type)
                self.send_dict["type"] = self.type
                Ezb_Service.reset_servo()
            # set user block auto-run
            elif "Auto-run" in self.recv_dict.keys():
                reslut = self.recv_dict["Type"]
                write_info("auto-run", reslut)
                self.send_dict["auto-run"] = reslut
                Ezb_Service.reset_servo()
            # reboot
            elif "RB" in self.recv_dict.keys():
                if self.recv_dict["RB"]:
                    _log('RB==True, rebooting...')
                    run_command("sudo reboot")
            # calibration
            elif "OF" in self.recv_dict.keys():
                # self.user_service_close()
                # self.ws_battery_process_close()
                if self.type in ["PiCarMini","PaKe"]:
                    if "DO" in self.recv_dict["OF"].keys():
                        if self.recv_dict["OF"]["DO"] == "test":
                            self.px.set_steering_angle(-30)
                            time.sleep(0.5)
                            self.px.set_steering_angle(30)
                            time.sleep(0.5)
                            self.px.set_steering_angle(0)
                            time.sleep(0.5)
                        else:
                            self.px.dir_servo_angle_calibration(int(self.recv_dict["OF"]["DO"]))
                    elif "PO" in self.recv_dict["OF"].keys():
                        self.px.camera_servo1_angle_calibration(int(self.recv_dict["OF"]["PO"]))
                    elif "TO" in self.recv_dict["OF"].keys():
                        self.px.camera_servo2_angle_calibration(int(self.recv_dict["OF"]["TO"]))
                    elif "enter" in self.recv_dict["OF"].keys():
                        self.px.save_calibration()
                elif self.type == "SpiderForPi":
                    if isinstance(self.recv_dict["OF"], dict) and "enter" in self.recv_dict["OF"].keys():
                        self.sp.cali_helper_web(0, 0, 1)
                    elif isinstance(self.recv_dict["OF"], list) and len(self.recv_dict["OF"]) == 3 and int(self.recv_dict["OF"][2]) == 0:
                        self.sp.cali_helper_web(int(self.recv_dict['OF'][0]), self.recv_dict['OF'][1], 0)
                elif self.type == "SlothForPi":
                    if isinstance(self.recv_dict["OF"], dict) and "enter" in self.recv_dict["OF"].keys():
                        self.sloth.save_calibration()
                    elif isinstance(self.recv_dict["OF"], list):
                        self.sloth.cali_temp = [ min(max(x, -20), 20) for x in self.recv_dict["OF"]]
                        self.sloth.angle_list(self.sloth.cali_temp)
                else:
                    _log("Type Error: %s" % self.type, color='31')
                # self.ws_battery_process_start()
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
                self.user_service_close()
                self.ws_battery_process_close()
                Ezb_Service.reset_servo()
                # if '0x14' in i2c_adress_list:
                #     Ezb_Service.reset_servo()
                if '0x74'in i2c_adress_list:
                    GPIO.setmode(GPIO.BCM)
                    GPIO.setup(24, GPIO.OUT)
                    GPIO.output(24,GPIO.LOW)
                    GPIO.cleanup(24)
                self.user_service_status = False
                self.send_dict["ST"] = True
                self.ws_battery_process_start()
            # Run user service
            elif "RU" in self.recv_dict.keys() and self.recv_dict["RU"]:
                try:
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
                except Exception as e:
                    _log('RU : %s'%e)
            # Update Ezblock
            if "UE" in self.recv_dict.keys():
                if self.recv_dict["UE"] and Ezb_Service.update_work == False:
                    Ezb_Service.update_work = True

            if Ezb_Service.update_work == True:
                # _log('Ezb_Service.update_flag.value: %s'% Ezb_Service.update_flag.value)
                if Ezb_Service.update_flag.value == 0: # 0:none 1:ING 2:OK 3:Failed
                    _log('Updating ...')
                    self.update_process = Process(name='update_process',target=self.update_ezblock,args=(Ezb_Service.update_flag,))
                    self.update_process.start()
                    _log('update_process start, pid = %s'% self.update_process.pid)
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

            # Processing completed, clear recv_dict
            self.recv_dict = {}

        except OSError as e:
            _log(e, location='data_process')
            Ezb_Service.reset_mcu_func()
            time.sleep(1)
        except Exception as e:
            _log(e, location='data_process', color='31')


    async def main_logic(self, websocket,path):
        # check connection
        # only one connection is allowed at the same time
        # self.connect_num += 1
        # if self.connect_num  > 1:
        #     await websocket.close(code=4000, reason='Connection is occupied')
        #     _log('Connection is occupied')
        #     return
            
        # connected flag
        self.is_client_connected.value = True
        self.recv_dict = {}
        self.send_dict = {}
        music_by_system(f'{USER_HOME}/Music/connected.mp3')
        _log('client connected')

        # close BLE Advertisement
        # self.ble.uart.stop_advertising()

        # battery
        if self.user_service_status == False and self.ws_battery_status == False:
            self.ws_battery_process_start()

        tmp = {}
        while True:
            self.is_client_connected.value = True
            try: #  to catch websockets.exceptions.ConnectionClosed
                # recv
                try:
                    tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                    tmp = json.loads(str(tmp))
                    self.recv_dict = dict.copy(tmp)
                    if 'PF' in dict(tmp).keys():
                        tmp.pop('PF')
                    if tmp != {}:
                        _log("recv_data_load:%s"%tmp,'websockets')
                except asyncio.TimeoutError as e:
                    # _log('asyncio.TimeoutError : %s'%e)
                    pass
                except json.JSONDecodeError as e:
                    _log('recv data JSONDecodeError: %s'%tmp, color='31')

                # data processing
                try:
                    # heartbeat
                    if 'PF' in self.recv_dict.keys():
                        data = {}
                        data['PF'] = 'pong'
                        data['voltage'] = '%.2f'%self.voltage.value
                        data['battery'] = self.battery.value
                        # print('send heartbeat: %s'%data)
                        # send heartbeat, voltage，battery
                        await websocket.send(json.dumps(data))
                        data = {}

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
                    _log('process data error: %s'%e, color='31')

                # send
                try:
                    # write send buff
                    if self.send_dict != {}:
                        data = dict(self.send_dict)
                    else:
                        data = dict(Ezb_Service.return_share_val())
                        if 'debug' in data.keys() :
                            if data['debug'][1] == False:
                                data = {}
                            else:
                                # Ezb_Service.clear_val()
                                Ezb_Service.set_share_val('debug',[data['debug'][0], False])
                        else:
                            data = {}

                    # updating no log (print)
                    if 'UE' in data and data['UE'] == "ING":
                        _UE_data = {'UE': data['UE']}
                        data.pop('UE')
                        await websocket.send(json.dumps(_UE_data))

                    # websocket.send
                    if data != {} :
                        _log('send data: %s'% data)
                        await websocket.send(json.dumps(data))
                    # TODO Unknown
                    try:
                        if 'LC' in data.keys():
                            LC_list = list(data['LC'].keys())
                            if  LC_list != []:
                                for i in LC_list:
                                    if data['LC'][i][-1] == True:
                                        data['LC'][i][-1] = False
                                        Ezb_Service.set_share_val('LC',data['LC'])
                    except Exception as e:
                        _log('send data error: %s'%e)

                    # clear send buff
                    if self.send_dict != {} and data == self.send_dict:
                        self.send_dict = {}
                except KeyboardInterrupt:
                    pass

            # disconnected exception
            except websockets.exceptions.ConnectionClosed as connection_code:
                _log('disconnected:%s'%connection_code)
                break
            await asyncio.sleep(0.01)

        # end while processing
        # self.ble.uart.start_advertising()   # start BLE Advertisement
        self.is_client_connected.value = False
        # self.connect_num = 0
        self.recv_dict = {}
        self.send_dict = {}
        Ezb_Service.clear_val()
        music_by_system(f'{USER_HOME}/Music/disconnected.mp3')
        _log('client disconnected')
        _log('---------------------------------------------')
      
    def print(self, msg, end='\n', tag='[DEBUG]', color=''):
        _log(msg, color=color)
        Ezb_Service.set_share_val('debug', [str(msg), True])
        time.sleep(0.02)
        while Ezb_Service.return_share_val()['debug'][1] == True:
            time.sleep(0.1)

    def close_tcp_port(self,port=port):
        # check port
        results = os.popen("sudo lsof -i:%s|grep %s|awk '{print $2}'"%(port,port)).readlines()
        if results == []:
            _log('no process occupies port %s'%port)
        else:
            # close related processes
            _log('port %s is already occupied,try to close related processes ...'%port)
            for pid in results:
                _log('kill %s .... '%pid.replace('\n',''),end='')
                status = os.system('sudo kill %s'%pid)
                if status == 0:
                    _log('succeed',timestamp=False)
                else:
                    _log('failed',timestamp=False)
                    return False
        return True

    def start_loop(self, ip):
        # check port
        while not self.close_tcp_port(port):
            time.sleep(0.01)
        # start websockets
        _log('open websockets server')
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
        _log("[Process] websocket_service_process: %s" % self.websocket_service_pid)

    def __start_ws__(self):
        _log("WS.__start_ws__")

        run_command('sudo rfkill unblock bluetooth')
        if read_info("name") != 'null':
            self.ble = BLE(read_info("name"))
            _log("BLE start: %s"%read_info("name"))
        else:
            self.ble = BLE('ezb-Raspberry')
            _log("BLE start: ezb-Raspberry")
        # Service status LED
        ws_led_t = threading.Thread(name='bl_led',target=self._ws_status_led,args=())
        ws_led_t.setDaemon(True)
        ws_led_t.start()

        while True:
            try:
                ip = getIP()
                # start websocket_service once
                # _log("get ip: %s" % ip)
                if ip and self.ws_process == None:
                    _log("got ip: %s " % ip)
                    self.websocket_service_process()

                # wait app connect the bluetooth
                value = ""
                value = self.ble.readline()
                if value == "":
                    time.sleep(0.05)
                    continue
                # send ip to app so that the app can connect to the WebSocket
                if value == "get":
                    if ip:
                        self.ble.write(ip)
                    else:
                        self.ble.write("No IP")
                # reconfigure wifi
                elif value and "#*#" in value:
                    if self.ws_process != None:
                        self.ws_process.terminate()
                        _log("ws_process.terminate(), kill pid: %s"%self.ws_process.pid)
                        delay(500)
                        
                    _log("Connecting to wifi")
                    data_list = value.split("#*#")
                    from .wifi import WiFi
                    wifi = WiFi()
                    wifi.write(*data_list)
                    # Retry 3 times
                    for _ in range(3):
                        ip = getIP()
                        if ip:
                            _log("IP Address: %s" % ip)
                            # start websocket_service
                            self.websocket_service_process()
                            _log("self.websocket_service_process()")
                            self.ble.write(ip)
                            break
                        time.sleep(1)
                    else:
                        self.ble.write("Connect Failed!")

            except Exception as e:
                _log("WS.__start_ws__ failed: %s" %e, color='31')
   

    def update_ezblock(self, update_flag):
        update_flag.value = 1  # 1:ING
        flag = ezb_update.update(self.app_version)
        if flag == True:
            update_flag.value = 2 # 2:OK
        else:
            update_flag.value = 3 # 3:Failed

    def _ws_status_led(self):
        _log("bluetooth_status_led thread start")
        while True:
            # _log(self.is_client_connected.value)
            if self.is_client_connected.value == True:
                ws_status_led.value(1)
                time.sleep(2)
            else:
                ws_status_led.value(1)
                time.sleep(1)
                ws_status_led.value(0)
                time.sleep(1)
                
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
