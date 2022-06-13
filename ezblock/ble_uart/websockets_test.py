import asyncio
import websockets
import json
import time
from ezblock import getIP, Pin, run_command, ADC
from filedb import fileDB

recv_dict = {
    'FL':False,  #download status
    'DA':" ",    #recvice code
    'NA': None,
    'TP':None,
    'RE':"null", #request data
}

send_dict = {
    "CD":False,  #finish code
    'name': None,
    'type': None,
    'ip':0,
    'battery':None,
    'mac': None,
    'version': 3.0,
} 
config_flie = fileDB('.config')
ip = getIP()
# power_pin_adc = ADC("A4")


def flash(name):
    global recv_dict
    file_dir = '/opt/ezblock/'
    dir = "%s/%s.py"%(file_dir, name)
    with open(dir, 'w') as f:
       f.write(recv_dict["DA"]) 


def reset():
    mcurst = Pin("MCURST")
    mcurst.off()
    time.sleep(0.001)
    mcurst.on()
    filename = '/opt/ezblock/main.py'
    for _ in range(4):
        run_command("sudo kill $(ps aux | grep -m 1 '%s' | awk '{ print $2 }')" % (filename))

async def recv_server_func(websocket):
    global recv_dict,send_dict
    tmp = await websocket.recv()
    print(tmp)
    tmp = json.loads(tmp)
    for key in tmp:
        recv_dict[key] = tmp[key]
    # print(recv_dict)
    await asyncio.sleep(0.01)
            
async def send_server_func(websocket): 
    global send_dict, recv_dict
    send_dict['name'] = config_flie.get("name")
    if recv_dict['NA']:
        config_flie.set('name','%s'%recv_dict['NA'])
    type_temp = config_flie.get("type")
    send_dict['type'] = type_temp
    if recv_dict['TP']:
        config_flie.set('type','%s'%recv_dict['TP'])
    if type_temp != "Ezblock pi" and type_temp != "None":
        # send_dict['battery'] = round(ADC('A4').read() / 4096.0 * 3.3 * 2,2)
        send_dict['battery'] = 88
    send_dict['ip'] = ip 
    if not config_flie.get("mac"):
        addr = run_command("hciconfig hci0")
        addr = addr[1].split("BD Address: ")[1].split(" ")[0].strip()
        config_flie.set('mac','%s'%addr)
    send_dict['mac'] = config_flie.get('mac')
    send_dict['version'] = config_flie.get('version')
    await websocket.send(json.dumps(send_dict))
    # print(send_dict)
    send_dict ={}
    await asyncio.sleep(0.01)
        
async def main_loop_frame():
    global recv_dict, send_dict
    while 1:
        if recv_dict['FL']:
            reset()
            flash('main')
            run_command("python3 /opt/ezblock/main.py &")
            send_dict["CD"] = True
        await asyncio.sleep(0.01)
        

async def main_logic_1(websocket, path):
    while 1:
        await send_server_func(websocket)
        await recv_server_func(websocket)
        
def start_loop(): 
    try:
        for _ in range(10):
            if ip:
                print("IP Address: "+ ip)
                # start_http_server()
                break
            time.sleep(1)
        start_server_1 = websockets.serve(main_logic_1, ip, 8765)
        print('Start!')
        tasks = [main_loop_frame(), start_server_1]
        asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
        asyncio.get_event_loop().run_forever()

    finally:
        print("Finished")

start_loop()