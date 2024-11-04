import asyncio
import websockets

from multiprocessing import Process, Manager, Value
import threading
from configparser import ConfigParser
import json
import time
import sys, os
import signal
import psutil


from .utils import *
from .ble import BLE
from .pin import Pin

from .i2c import I2C

from .version import VERSION
from .user_info import USER, USER_HOME

sys.path.append(r'/opt/ezblock')
from ezb_update import Ezbupdate


# variables
# =================================================================
# WS_PORT = 8765  # version == 1.0.x
WS_PORT = 7852    # SiTianJiChuang, version >= 1.1.x

# detect_i2c
detect_i2c = I2C()
i2c_adress_list = list(map(hex, detect_i2c.scan()))

config = ConfigParser()

ezb_update = Ezbupdate()

# utils
# =================================================================
def _log(msg:str, location='websokcets', end='\n', flush=False, timestamp=True, color=''):
    log(msg, location, end=end, flush=flush, timestamp=timestamp, color=color)

DEBUG = False 
def debug(*args, **kwargs):
    if DEBUG:
        print("[DEBUG]", *args, **kwargs)

def music_by_system(path:str, wait=True):
    try:
        run_command('sudo mplayer %s'%path, wait)
    except Exception as e:
        _log(e, location='Sound effect')

def str_limit(string:str, max_len=64):
    import re
    # remove the first space and line break, maximum length: 64 characters
    string = string.strip()[0:max_len]
    # only keep the English letters (a-z,A-Z) and numbers (0-9) and '-'
    compile = re.compile('[^A-Z^a-z^0-9^\-]')
    return compile.sub('', string)

# info
# =================================================================
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


# Ezb_Service
# =================================================================
class Ezb_Service(object):
    update_flag = Value('d',0) # 0:none 1:ING 2:OK 3:Failed
    update_work = False
    share_dict = Manager().dict()
    share_dict['debug'] = [None,False]

    @staticmethod
    def reset_servo():
        _log('reset_mcu')
        reset_mcu()
        ws.type = read_info("type")
        _log('Products type: %s'%ws.type)
        try:
            # delete i2c
            for _ in range(3):
                i2c_adress_list = list(map(hex, detect_i2c.scan()))
                _log('i2c_adress_list: %s'%i2c_adress_list)
                if '0x14' in i2c_adress_list:
                    break
                time.sleep(0.2)
            else:
                _log("I2C 0x14 not found", color='31')
                return False
            return True
        except Exception as e:
            _log('reset_servo error for %s:%s'%(ws.type, e), color='31')
            Ezb_Service.set_share_val('debug', [str(e), True])
            return False

    @staticmethod
    def ezb_service_start():
        _log("Ezb_Service.ezb_service_start")

        # Service startup Sound
        music_by_system(f'{USER_HOME}/Music/startup.mp3', wait=False)

        # whether auto-run main.py
        if read_info("auto-run") in ["True", "true", "TRUE", "1", "on", "ON"]:
            _log("ws.user_service_start auto-run")
            ws.calibration_process_close()
            ws.user_service_start()
        else:
            _log("ws.user_service_start does not auto-run")

        # Service status LED thread
        ws_led_t = threading.Thread(name='bl_led', target=ws._ws_status_led)
        ws_led_t.daemon = True
        ws_led_t.start()

        # BLE start
        run_command('sudo rfkill unblock bluetooth')
        if read_info("name") != 'null':
            ws.ble = BLE(read_info("name"))
            _log("BLE start: %s"%read_info("name"))
        else:
            ws.ble = BLE('ezb-Raspberry')
            _log("BLE start: ezb-Raspberry")
        # enable discoverable
        run_command('bluetoothctl discoverable on')

        # loop
        while True:
            try:
                ip = getIP()
                # start websocket_service once
                if ip and ws.ws_process == None:
                    ws.websocket_server_process_start()

                # wait app connect the bluetooth
                value = ""
                value = ws.ble.readline()
                if value == "":
                    time.sleep(0.05)
                    continue

                # send ip to app so that the app can connect to the WebSocket
                if value == "get":
                    if ip:
                        ws.ble.write(ip)
                    else:
                        ws.ble.write("No IP")
                # reconfigure wifi
                elif value and "#*#" in value:
                    ws.websocket_server_process_close()
                    time.sleep(0.5)
                        
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
                            ws.websocket_server_process_start()
                            ws.ble.write(ip)
                            break
                        time.sleep(1)
                    else:
                        ws.ble.write("Connect Failed!")

            except Exception as e:
                _log("ws.__start_ws__ failed: %s" %e, color='31')


    @staticmethod
    def start_service():
        _log("Ezb_Service.start_service")
        _log(f"user:{USER}")
        _log(f"userhome:{USER_HOME}")

        run_command('pinctrl set 20 op dh') # enable speaker
        # run_command('pinctrl pinctrl 21 a0') # PCM_DOUT

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

    recv_dict = Manager().dict()
    send_dict = Manager().dict()
    cali_cmmd_dict = Manager().dict()

    BAT_REFRESH_INTERVAL = 3 # seconds

    def __init__(self):

        self.remote_dict = {}
        self.output_module_dict = {}

        self.ws_process = None
        self.user_service_process = None
        self.ws_battery_process = None
        self.calibration_process = None
        self.update_process = None

        self.type = None
        self.app_version = None

        self.voltage = Value('d',0.0)
        self.battery = Value('d',0)
        self.is_client_connected = Value('i',0)
        self.connect_num = 0
        self.ble = None
        self.client_num = 0
        self.client = {}

    # user_service
    # =================================================================
    def user_service_start(self):
        self.user_service_close()
        self.ws_battery_process_close() # close the battery process, to avoid i2c communication conflicts
        self.user_service_process = Process(name='user service',
                                            target=self.user_main,
                                            args=(ws.voltage, ws.battery)
                                            )
        self.user_service_process.start()
        _log("[Process] user_service_start: %s" % self.user_service_process.pid)

    def user_service_close(self):
        if self.user_service_process != None:
            # ***** 
            # terminate() sometimes the program cannot be terminated. Use kill -9 to force it to close.
            # And sometimes its child process will not be closed, you need to kill the child process manually.
            # *****

            # self.user_service_process.terminate()  
            # self.user_service_process.join()
            parent_pid = self.user_service_process.pid
            children = psutil.Process(parent_pid).children()

            for child in children:
                _log(f"[Process] kill user_service_child_process, pid: {child.pid}")
                os.kill(child.pid, signal.SIGKILL)
            
            _log(f"[Process] kill user_service_main_process, pid: {parent_pid}")
            os.kill(parent_pid, signal.SIGKILL)

            self.user_service_process = None

    def user_main(self, voltage, battery):
        try:
            from main import forever

            _st = time.time()
            while True:

                if (time.time() - _st) > self.BAT_REFRESH_INTERVAL:
                    voltage.value, battery.value = get_battery()
                    _st = time.time()

                forever()
                time.sleep(0.01)
        except Exception as e:
            Ezb_Service.reset_servo()
            _log(f"Error: {e}", location="USER_PROGRAM")
            self.print(f"Error: {e}", color='31')
            return False

    # ws_battery_process
    # =================================================================
    def ws_battery_process_start(self):
        self.ws_battery_process_close()
        self.ws_battery_process = Process(name='ws battery', 
                                          target=self.get_battery_handler, 
                                          args=(self.voltage, self.battery,)
                                          )
        self.ws_battery_process.start()
        _log(f"[Process] start ws_battery_process, pid: {self.ws_battery_process.pid}")
        self.ws_battery_status = True

    def ws_battery_process_close(self):
        if self.ws_battery_process != None:
            _log(f"[Process] kill ws_battery_process, pid: {self.ws_battery_process.pid}")
            # self.ws_battery_process.terminate()
            os.kill(self.ws_battery_process.pid, signal.SIGKILL)
            self.ws_battery_process = None

    def get_battery_handler(self, voltage, battery):
        while True:
            voltage.value, battery.value = get_battery()
            time.sleep(self.BAT_REFRESH_INTERVAL)

    # calibration_process
    # =================================================================
    def calibration_process_start(self):
        self.calibration_process_close()
        self.calibration_process = Process(
                name='calibration_process', 
                target=self.calibration_loop, 
                args=(self.type, self.cali_cmmd_dict, self.send_dict,)
                )
        self.calibration_process.start()
        _log(f"[Process] calibration_process_start: {self.calibration_process.pid}")

    def calibration_process_close(self):
        if self.calibration_process is not None:
            _log(f"[Process] kill calibration_process, pid: {self.calibration_process.pid}")
            # self.calibration_process.terminate()
            os.kill(self.calibration_process.pid, signal.SIGKILL)
            self.calibration_process = None

    def calibration_loop(self, type, cali_cmmd_dict, send_dict):
        _location = "calibration process"

        # ---- Products init ----
        try:
            # --- Spider ---
            if type == "SpiderForPi":
                _log("spider init", location=_location)
                from spider import Spider
                sp = Spider([10,11,12,4,5,6,1,2,3,7,8,9])
                sp.servo_positions = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                #
                _init_coord = list.copy(sp.cali_default_coord)
                sp.do_step(_init_coord, 80)
                #
                send_dict['coord_offset'] = list(sp.coord_offset)
            # --- Sloth ---
            elif type == "SlothForPi":
                _log("sloth init", location=_location)
                from sloth import Sloth
                sloth = Sloth([1,2,3,4])
                #
                sloth.servo_move([0, 0, 0, 0])
                #
                send_dict['offset'] = list(sloth.offset)
            # --- PiCarX ---
            elif type in ["PiCarMini", "PaKe"]:
                _log("picarx init", location=_location)
                from picarx import PiCarX
                px = PiCarX()
                #
                px.set_steering_angle(0)
                px.set_camera_pan_angle(0)
                px.set_camera_tilt_angle(0)
                #
                send_dict['offset'] = [px.dir_cal_value, px.cam_cal_value_1, px.cam_cal_value_2]

        except Exception as e:
            _log(f"{type} init failed: {e}",location=_location)
            Ezb_Service.set_share_val('debug', [str(e), True])

        # --- loop ---
        while True:
            try:
                if cali_cmmd_dict != {}:
                    # --- PicarX ---
                    if type in ["PiCarMini","PaKe"]:
                        if "DO" in cali_cmmd_dict.keys():
                            if cali_cmmd_dict["DO"] == "test":
                                px.set_steering_angle(-30)
                                time.sleep(0.5)
                                px.set_steering_angle(30)
                                time.sleep(0.5)
                                px.set_steering_angle(0)
                                time.sleep(0.5)
                            else:
                                px.dir_servo_angle_calibration(int(cali_cmmd_dict["DO"]))
                        elif "PO" in cali_cmmd_dict.keys():
                            px.camera_servo1_angle_calibration(int(cali_cmmd_dict["PO"]))
                        elif "TO" in cali_cmmd_dict.keys():
                            px.camera_servo2_angle_calibration(int(cali_cmmd_dict["TO"]))
                        elif "enter" in cali_cmmd_dict.keys():
                            # px.save_calibration()
                            pass
                    # --- Spider ---
                    elif type == "SpiderForPi":
                        if "cmd" in cali_cmmd_dict.keys():
                            _cmd = cali_cmmd_dict["cmd"]
                            sp.cali_helper_web(int(_cmd[0]), _cmd[1], 0)
                        elif "enter" in cali_cmmd_dict.keys():
                            sp.cali_helper_web(0, 0, 1)
                    # --- Sloth ---
                    elif type == "SlothForPi":
                        if isinstance(cali_cmmd_dict, dict) and "enter" in cali_cmmd_dict.keys():
                            sloth.save_calibration()
                        elif isinstance(cali_cmmd_dict, list):
                            sloth.cali_temp = [ min(max(x, -20), 20) for x in cali_cmmd_dict]
                            sloth.angle_list(sloth.cali_temp)
                    # --- Type Error ---
                    else:
                        _log(f"Type Error: {type}", location=_location ,color='31')
                        Ezb_Service.set_share_val('debug', [f"Type Error: {type}", True])
            
                    ## clear
                    cali_cmmd_dict.clear()
            
            except Exception as e:
                _log(f"{type} calibration failed: {e}",location=_location)
                Ezb_Service.set_share_val('debug', [str(e), True])

            time.sleep(0.1)

    # update_process
    # =================================================================
    def update_process_start(self):
        self.update_process_close()
        self.update_process = Process(
                name='update_process',
                target=self.update_ezblock,
                args=(Ezb_Service.update_flag,)
                )
        self.update_process.start()
        _log(f"[Process] update_process_start: {self.update_process.pid}")

    def update_process_close(self):
        if self.update_process is not None:
            _log(f"[Process] kill update_process, pid: {self.update_process.pid}")
            # self.update_process.terminate()
            os.kill(self.update_process.pid, signal.SIGKILL)
            self.update_process = None

    def update_ezblock(self, update_flag):
        update_flag.value = 1  # 1:ING
        flag = ezb_update.update(self.app_version)
        if flag == True:
            update_flag.value = 2 # 2:OK
        else:
            update_flag.value = 3 # 3:Failed

    # websocket_server_process
    # =================================================================
    def websocket_server_process_start(self):
        if self.ws_process != None:
            self.websocket_server_process_close()

        reset_mcu()

        self.ws_process = Process(name='websocket service',target=self.start_loop, args=('0.0.0.0', WS_PORT, )) # args=(ip, ) ：This is a tuple, the ',' is necessary !!!
        self.ws_process.start()
        _log(f"[Process] start websocket_service_process: {self.ws_process.pid}")

    def websocket_server_process_close(self):
        if self.ws_process != None:
            _log(f"kill ws_process, pid: {self.ws_process.pid}")
            # self.ws_process.terminate()
            os.kill(self.ws_process.pid, signal.SIGKILL)

    # websocket loop
    # ----------------------------------------------------------------
    def start_loop(self, ip, port):
        # check port
        while not self.close_tcp_port(port):
            time.sleep(0.01)

        # start websockets
        _log('open websockets server')
        asyncio.run(self.websocket_main(ip, port))

    async def websocket_main(self, ip, port):
        self.server = await websockets.serve(self.websocket_loop, ip, port)
        async with self.server:
            await asyncio.Future() # run forever
        _log('websockets server closed')

    async def websocket_loop(self, websocket):
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
        music_by_system(f'{USER_HOME}/Music/connected.mp3', wait=False)
        _log('client connected')

        # close BLE Advertisement
        # self.ble.uart.stop_advertising()

        # battery
        if self.ws_battery_process is None:
            self.ws_battery_process_start()

        tmp = {}
        while True:
            self.is_client_connected.value = True
            try: #  to catch websockets.exceptions.ConnectionClosed
                # recv
                try:
                    tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                    tmp = json.loads(str(tmp))
                    # self.recv_dict = dict.copy(tmp) # this operation will change the id, use dict.update()
                    self.recv_dict.clear()
                    self.recv_dict.update(tmp)

                    if 'PF' in dict(tmp).keys():
                        tmp.pop('PF')
                    if tmp != {}:
                        # _log("recv_data_load:%s"%tmp,'websockets')
                        debug("recv_data_load:%s"%tmp)
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
                        # debug('send heartbeat: %s'%data)
                        # send heartbeat, voltage，battery
                        await websocket.send(json.dumps(data))
                        data = {}

                    # --- data processing ---
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

                    # updating no _log (print)
                    if 'UE' in data and data['UE'] == "ING":
                        _UE_data = {'UE': data['UE']}
                        data.pop('UE')
                        await websocket.send(json.dumps(_UE_data))

                    # websocket.send
                    if data != {} :
                        # _log('send data: %s'% data)
                        debug('send data: %s'% data)
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
        music_by_system(f'{USER_HOME}/Music/disconnected.mp3', wait=False)
        _log('client disconnected')
        _log('---------------------------------------------')

    def data_process(self):
        global i2c_adress_list
        try:
            # Read data
            if "APP" in self.recv_dict.keys():
                _log(f'recv "APP": {self.recv_dict["APP"]}')
                self.app_version = self.recv_dict["APP"]
            if "RE" in self.recv_dict.keys():
                _log(f'recv "RE": {self.recv_dict["RE"]}')
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
                    self.calibration_process_start()
            # calibration cmd
            elif "OF" in self.recv_dict.keys():
                if isinstance(self.recv_dict["OF"], dict):
                    self.cali_cmmd_dict.update(self.recv_dict["OF"])
                else:
                    self.cali_cmmd_dict.update({"cmd": self.recv_dict["OF"]})
            # set name
            elif "NA" in self.recv_dict.keys():
                _log(f'recv "NA": {self.recv_dict["NA"]}')
                try:
                    name_temp = self.recv_dict["NA"]
                    name_temp = str_limit(name_temp)
                    write_info("name", name_temp)
                    run_command('sudo hostnamectl set-hostname %s'%name_temp)
                    _log("change name to : %s"%name_temp)
                    self.send_dict["name"] = name_temp
                except Exception as e:
                    _log('set-hostname failed: %s'%e)
            # set device type
            elif "Type" in self.recv_dict.keys():
                _log(f'recv "Type": {self.recv_dict["Type"]}')
                self.type = self.recv_dict["Type"]
                write_info("type", self.type)
                self.send_dict["type"] = self.type
                Ezb_Service.reset_servo()
            # set user block auto-run
            elif "Auto-run" in self.recv_dict.keys():
                _log(f'recv "Auto-run": {self.recv_dict["Auto-run"]}')
                reslut = self.recv_dict["Auto-run"]
                write_info("auto-run", reslut)
                self.send_dict["auto-run"] = reslut
                Ezb_Service.reset_servo()
            # reboot
            elif "RB" in self.recv_dict.keys():
                _log('recv "RB"')
                if self.recv_dict["RB"]:
                    _log('RB==True, rebooting...')
                    run_command("sudo reboot")
            # Download code
            elif "FL" in self.recv_dict.keys() and self.recv_dict['FL']:
                _log('recv "FL"')
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
                    reset_mcu()
                    self.type = read_info("type")
                    if self.type == "SpiderForPi":
                        pass
                self.flash("main")
                self.calibration_process_close()
                self.user_service_start()
                for _ in range(10):
                    self.send_dict["CD"] = True
                self.recv_dict['FL'] = False
            # Stop user service
            elif "ST" in self.recv_dict.keys() and self.recv_dict["ST"]:
                _log('recv "ST"')
                self.user_service_close()
                self.ws_battery_process_close()
                Ezb_Service.reset_servo()
                self.send_dict["ST"] = True
                self.ws_battery_process_start()
            # Run user service
            elif "RU" in self.recv_dict.keys() and self.recv_dict["RU"]:
                _log('recv "RU"')
                try:
                    self.user_service_close()
                    self.calibration_process_close()
                    reset_mcu()
                    self.user_service_start()
                    self.send_dict["RU"] = True
                except Exception as e:
                    _log('RU : %s'%e)
            # Update Ezblock
            if "UE" in self.recv_dict.keys():
                _log('recv "UE"')
                if self.recv_dict["UE"] and Ezb_Service.update_work == False:
                    Ezb_Service.update_work = True

            if Ezb_Service.update_work == True:
                # _log('Ezb_Service.update_flag.value: %s'% Ezb_Service.update_flag.value)
                if Ezb_Service.update_flag.value == 0: # 0:none 1:ING 2:OK 3:Failed
                    _log('Updating ...')
                    self.update_process_start()
                    Ezb_Service.update_flag.value = 1
                elif Ezb_Service.update_flag.value == 1: #  1:ING
                    self.send_dict["UE"] = 'ING'
                elif Ezb_Service.update_flag.value == 2: #  2:OK
                    self.send_dict["UE"] = 'OK'
                    Ezb_Service.update_work = False
                    self.update_process_close()
                    self.send_dict['version'] = read_info("version")
                    Ezb_Service.update_flag.value = 0
                elif Ezb_Service.update_flag.value == 3: #  3:Failed
                    self.send_dict["UE"] = 'Failed'
                    Ezb_Service.update_work = False
                    self.update_process_close()
                    Ezb_Service.update_flag.value = 0

            # Processing completed, clear recv_dict
            # self.recv_dict = {} # "dict = {}" will change the id
            self.recv_dict.clear() # clear() will keep the id

        except OSError as e:
            _log(e, location='data_process')
            reset_mcu()
            time.sleep(1)
        except Exception as e:
            _log(e, location='data_process', color='31')

    # utils
    # ----------------------------------------------------------------
    def flash(self, name):
        file_dir = '/opt/ezblock/'
        dir = "%s/%s.py"%(file_dir, name)
        with open(dir, 'w') as f:
            f.write(self.recv_dict["DA"])
        _log(f'flash code:\n'
             + f'{"-"*80}\n'
             + f'{self.recv_dict["DA"]}'
             + f'{"-"*80}'
             )

    def have_update(self):
        def fuc():
            if self.app_version == None:
                self.send_dict['update'] = False
            else:
                self.send_dict['update'] = ezb_update.get_status(self.app_version)
        t = threading.Thread(target=fuc)
        t.setDaemon(True)
        t.start()

    def close_tcp_port(self, port):
        # check port
        results = os.popen("sudo lsof -i:%s|grep %s|awk '{print $2}'"%(port, port)).readlines()
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

    def print(self, msg, end='\n', tag='[DEBUG]', color=''):
        # _log(msg, color=color)
        print(f'[user program] {msg}')
        Ezb_Service.set_share_val('debug', [str(msg), True])
        time.sleep(0.02)
        while Ezb_Service.return_share_val()['debug'][1] == True:
            time.sleep(0.1)    # utils

    # ws_status_led thread
    # =================================================================
    def _ws_status_led(self):
        _log("ws_status_led thread start")

        ws_status_led = Pin("LED", Pin.OUT)
        #
        while True:
            if self.is_client_connected.value == True:
                ws_status_led.value(1)
                time.sleep(2)
            else:
                ws_status_led.value(1)
                time.sleep(0.5)
                ws_status_led.value(0)
                time.sleep(0.5)

# init ws
# =================================================================
ws = WS()

def ws_print(msg, end='\n', tag='[DEBUG]'):
    ws.print(msg, end, tag)

# class Remote 
# =================================================================
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
