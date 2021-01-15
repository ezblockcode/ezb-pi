import asyncio
import websockets
import json
import time
from .utils import getIP
import os

recv_dict = {
    'JS':[0, 0], #remote
    'SL':0,
    'DP':"up",
    'BT':0,
    'SW':0,
}

send_dict = {
    'debug':'hello',  #print message
} 

__WS_STARTED__ = False

def __start_ws__():
    global __WS_STARTED__
    if __WS_STARTED__:
        return
    from multiprocessing import Process
    ws = WS()
    service = Process(name='websocket service',target=ws.start_loop)
    service.start()
    __WS_STARTED__ = True

def ws_print(msg, end='\n', tag='[DEBUG]'):
    global send_dict
    __start_ws__()
    _msg = "Ezblock [{}] [DEBUG] {}".format(time.asctime(), msg)
    os.system("echo {} >> /opt/ezblock/log".format(_msg))
    msg = '%s %s %s' % (tag, msg, tag)
    print(msg, end=end)
    # ble.write(msg)
    send_dict['debug'] = msg

class Remote():
    
    def __init__(self):
        __start_ws__()
    
    def read(self): # deprecated 
        pass
    
    def get_joystick_value(self, coord):
        global recv_dict
        if coord == 'X':
            return int(recv_dict['JS'][0])
        elif coord == 'Y':
            return int(recv_dict['JS'][1])
        else:
            return 0
    
    def get_slider_value(self):
        global recv_dict
        _value = int(recv_dict['SL'])
        return _value
    
    def get_dpad_value(self, id, direction):
        global recv_dict
        _value = int(recv_dict['DP'])
        return _value
        
    def get_button_value(self, id):
        global recv_dict
        _value = int(recv_dict['BT'])
        return _value
    
    def get_switch_value(self, id):
        global recv_dict
        _value = int(recv_dict['SW'])
        return _value
        
    def set_segment_value(self, value):
        global send_dict
        if not (isinstance(value, (int, float, str))):
            raise ValueError("segment value must be number, int or float")
        send_dict['SG'] = value
    
    def set_light_bolb_value(self, value):
        global send_dict
        if not (value in [0, 1] or isinstance(value, bool)):
            raise ValueError("light bolb value must be 0/1 or True/False")
        send_dict['LB'] = value
    
    def set_meter_value(self, value):
        global send_dict
        if not (isinstance(value, int) or isinstance(value, float)):
            raise ValueError("meter value must be number, int or float")
        send_dict["MT"] = value
    
    def set_line_chart_value(self, value):
        global send_dict
        if not isinstance(value, list):
            raise ValueError("line chart value must be list of name value pair, not %s"%type(value))
        send_dict["LC"] = value
    
    def set_pie_chart_value(self, id, value):
        global send_dict
        if not isinstance(value, list):
            raise ValueError("pie chart value must be list of name value pair not %s"%type(value))
        send_dict["PC"] = value
    
    def set_bar_chart_value(self, id, value):
        global send_dict
        if not isinstance(value, list):
            raise ValueError("bar_chart value must be list of numbers, int or float")
        send_dict["BC"] = value

        
class WS():
    
    def __init__(self):
        pass
              
    async def main_loop_frame(self):
        global recv_dict, send_dict
        while 1:
            pass
            await asyncio.sleep(0.01)
            

    async def main_logic(self, websocket, path):
        global recv_dict,send_dict
        while 1:
            try:
                tmp = await asyncio.wait_for(websocket.recv(), timeout=0.001)
                # print(tmp)
                tmp = json.loads(tmp)
                for key in tmp:
                    recv_dict[key] = tmp[key]
            except:
                pass
            await websocket.send(json.dumps(send_dict))
            send_dict = {}
            # await asyncio.sleep(0.01)

            
    def start_loop(self): 
        try:
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

        finally:
            print("Finished")

if __name__ == '__main__':
    web = WS()