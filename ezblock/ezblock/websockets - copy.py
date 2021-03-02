import asyncio
import websockets
import json
import time
from .utils import getIP
import os
from multiprocessing import Process, Manager, Queue


class WS():
    
    def __init__(self):
        self.recv_dict = {}   
        self.send_dict = {}
        self.recv_queue = Queue()
        self.send_queue = Queue()
        self.__WS_STARTED__ = False
              
    async def main_loop_frame(self):
        while 1:
            pass
            await asyncio.sleep(0.001)
            

    async def main_logic(self, websocket, path):
        while 1:
            # print("main_logic_loop")
            try:
                tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                # print(tmp)
                tmp = json.loads(tmp)
                # print("recv_data_load:%s"%tmp)
                self.recv_queue.put(tmp)
                # for key in tmp:
                #     self.recv_dict[key] = tmp[key]
                # print("self.recv_dict%s"%self.recv_dict)
            except:
                pass
            try:
                data = self.send_queue.get(block=True, timeout=0.001)
                # print("send_data:%s"%data)
                await websocket.send(json.dumps(data))
            except:
                pass
            # self.send_dict = {}
            # await asyncio.sleep(0.01)

            
    def start_loop(self): 
        # try:

        # finally:
        #     print("Finished")
        for _ in range(10):
            ip = getIP()
            if ip:
                print("IP Address: "+ ip)
                # start_http_server()
                break
            time.sleep(1)
        start_server_1 = websockets.serve(self.main_logic, ip, 8766)
        print('Start!')
        tasks = [self.main_loop_frame(), start_server_1]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
        asyncio.get_event_loop().run_forever()
        # while 1:
        #     print("Sub process send_dict: %s"% self.send_dict)
        #     time.sleep(1)

    def start_loop_wrap(self):
        self.start_loop()

    def print(self, msg, end='\n', tag='[DEBUG]'):
        self.__start_ws__()
        _msg = "Ezblock [{}] [DEBUG] {}".format(time.asctime(), msg)
        os.system("echo {} >> /opt/ezblock/log".format(_msg))
        # msg = '%s %s %s' % (tag, msg, tag)
        # print(msg, end=end)
        # ble.write(msg)
        if msg != "None":
            self.send_dict['debug'] = msg
            self.send_queue.put(self.send_dict)
            print("ws_print_send_dict: %s" % self.send_dict)
        # time.sleep(0.01)
    
    
    def __start_ws__(self):
        if self.__WS_STARTED__:
            return
        # import threading
        # ws = WS()
        # service = threading.Thread(name = 'websocket service',target=ws.start_loop)
        # service.start()
        service = Process(name='websocket service',target=self.start_loop_wrap)
        service.start()
        self.__WS_STARTED__ = True

ws = WS()

def ws_print(msg, end='\n', tag='[DEBUG]'):
    ws.print(msg, end, tag)

class Remote():
    
    def __init__(self):
        ws.__start_ws__()
    
    def read(self): # deprecated 
        pass
    
    def get_joystick_value(self, id, coord):
        try:
            ws.recv_dict = ws.recv_queue.get(block=True, timeout=0.001)
        except:
            pass
        if "JS" not in ws.recv_dict.keys():
            return
        if id not in ws.recv_dict["JS"].keys():
            return
        
        value = ws.recv_dict["JS"][id]
        if coord == 'X':
            return int(value[0])
        elif coord == 'Y':
            return int(value[1])
        else:
            return 0
    
    def get_slider_value(self, id):
        try:
            ws.recv_dict = ws.recv_queue.get(block=True, timeout=0.001)
        except:
            pass
        if "SL" not in ws.recv_dict.keys():
            return
        if id not in ws.recv_dict["SL"].keys():
            return
        _value = int(ws.recv_dict['SL'][id])
        return _value
    
    def get_dpad_value(self, id, direction):
        try:
            ws.recv_dict = ws.recv_queue.get(block=True, timeout=0.001)
        except:
            pass
        if "DP" not in ws.recv_dict.keys():
            return
        if id not in ws.recv_dict["DP"].keys():
            return
        _value = int(ws.recv_dict['DP'][id][direction])
        return _value
        
    def get_button_value(self, id):
        try:
            ws.recv_dict = ws.recv_queue.get(block=True, timeout=0.001)
        except:
            pass
        if "BT" not in ws.recv_dict.keys():
            return
        if id not in ws.recv_dict["BT"].keys():
            return
        _value = int(ws.recv_dict['BT'][id])
        return _value
    
    def get_switch_value(self, id):
        try:
            ws.recv_dict = ws.recv_queue.get(block=True, timeout=0.001)
        except:
            pass
        if "SW" not in ws.recv_dict.keys():
            return
        if id not in ws.recv_dict["SW"].keys():
            return
        _value = int(ws.recv_dict['SW'][id])
        return _value
        
    def set_segment_value(self, id, value):
        if not (isinstance(value, (int, float, str))):
            raise ValueError("segment value must be number, int or float")
        ws.send_dict['SG'][id] = value
        ws.send_queue.put(ws.send_dict)
    
    def set_light_bolb_value(self, id, value):
        if not (value in [0, 1] or isinstance(value, bool)):
            raise ValueError("light bolb value must be 0/1 or True/False")
        ws.send_dict['LB'][id] = value
        ws.send_queue.put(ws.send_dict)
    
    def set_meter_value(self, id, value):
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("meter value must be number, int or float")
        ws.send_dict["MT"][id] = value
        ws.send_queue.put(ws.send_dict)
    
    def set_line_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("line chart value must be list of name value pair, not %s"%type(value))
        ws.send_dict["LC"][id] = value
        ws.send_queue.put(ws.send_dict)
    
    def set_pie_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("pie chart value must be list of name value pair not %s"%type(value))
        ws.send_dict["PC"][id] = value
        ws.send_queue.put(ws.send_dict)
    
    def set_bar_chart_value(self, id, value):
        if not isinstance(value, list):
            raise ValueError("bar_chart value must be list of numbers, int or float")
        ws.send_dict["BC"][id] = value
        ws.send_queue.put(ws.send_dict)

# if __name__ == '__main__':
#     web = WS()