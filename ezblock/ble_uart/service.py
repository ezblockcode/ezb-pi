import asyncio
import websockets
import json
import time
from ezblock import getIP

# print(websockets.__version__)


ip = getIP()

class Websocket():
    recv_dict = {
        'A_region':None,
        'B_region':None,
        'C_region':None,
        'D_region':None, 
        'E_region':None,
        'F_region':None,
        'G_region':None,
        'H_region':None,
        'I_region':None,
        'J_region':None,
        'K_region':None,
        'L_region':None,
        'M_region':None,
        'N_region':None,
        'O_region':None,
        'P_region':None,
        'Q_region':None,
    }
    
    send_dict = {
        'Name':'Pitank-2',
        'Type':'Pitank',
        'Check':'SunFounder Controller',
        'A_region':0,
        'B_region':0,
        'C_region':0,
        'D_region':0,
        'E_region':0,
        'F_region':0,
        'G_region':0,
        'H_region':0,
        'I_region':0,
        'J_region':0,
        'L_region':0,
        'M_region':0,
        'O_region':0,
        'P_region':0,
        'Q_region':0,
        'AD':'http://' + ip + ':9000/mjpg',
        
    }
    
    def __init__(self):
        self.a_value = 0
        self.b_value = 0
        self.c_value = 0
        self.d_value = 0
        self.e_value = 0
        self.f_value = 0
        self.g_value = 0
        self.h_value = 0
        self.i_value = 0
        self.j_value = 0
        self.l_value = 0
        self.m_value = 0
        self.o_value = 0
        self.p_value = 0
        self.n_value = 0

    def main_loop(self):
        pass

    async def main_loop_frame(self):
        while 1:
            self.main_loop()
            await asyncio.sleep(0.01)
    
    async def recv_server_func(self, websocket):
        tmp = await websocket.recv()
        # print(type(tmp))
        # print(tmp)
        # websocket.send(json.dumps(self.send_dict))
        # print(tmp[1])
        tmp = json.loads(tmp)
        print("recv_dict: %s"%self.recv_dict)
        if self.recv_dict['A_region'] != None and self.recv_dict['A_region'] != tmp['A_region']:
            self.on_a_change(tmp['A_region'])
        if self.recv_dict['B_region'] != None and self.recv_dict['B_region'] != tmp['B_region']:
            self.on_b_change(tmp['B_region'])
        if self.recv_dict['C_region'] != None and self.recv_dict['C_region'] != tmp['C_region']:
            self.on_c_change(tmp['C_region'])
        if self.recv_dict['D_region'] != None and self.recv_dict['D_region'] != tmp['D_region']:
            self.on_d_change(tmp['D_region'])
        if self.recv_dict['E_region'] != None and self.recv_dict['E_region'] != tmp['E_region']:
            self.on_e_change(tmp['E_region'])
        if self.recv_dict['F_region'] != None and self.recv_dict['F_region'] != tmp['F_region']:
            self.on_f_change(tmp['F_region'])
        if self.recv_dict['G_region'] != None and self.recv_dict['G_region'] != tmp['G_region']:
            self.on_g_change(tmp['G_region'])
        if self.recv_dict['H_region'] != None and self.recv_dict['H_region'] != tmp['H_region']:
            self.on_h_change(tmp['H_region'])
        if self.recv_dict['I_region'] != None and self.recv_dict['I_region'] != tmp['I_region']:
            self.on_i_change(tmp['I_region'])
        if self.recv_dict['J_region'] != None and self.recv_dict['J_region'] != tmp['J_region']:
            self.on_j_change(tmp['J_region'])
        if self.recv_dict['K_region'] != None and self.recv_dict['K_region'] != tmp['K_region']:
            self.on_k_change(tmp['K_region'])
        if self.recv_dict['L_region'] != None and self.recv_dict['L_region'] != tmp['L_region']:
            self.on_l_change(tmp['L_region'])
        if self.recv_dict['M_region'] != None and self.recv_dict['M_region'] != tmp['M_region']:
            self.on_m_change(tmp['M_region'])
        if self.recv_dict['N_region'] != None and self.recv_dict['N_region'] != tmp['N_region']:
            self.on_n_change(tmp['N_region'])
        if self.recv_dict['O_region'] != None and self.recv_dict['O_region'] != tmp['O_region']:
            self.on_o_change(tmp['O_region'])
        if self.recv_dict['P_region'] != None and self.recv_dict['P_region'] != tmp['P_region']:
            self.on_p_change(tmp['P_region'])
        if self.recv_dict['Q_region'] != None and self.recv_dict['Q_region'] != tmp['Q_region']:
            self.on_q_change(tmp['Q_region'])
        for key in tmp:
            self.recv_dict[key] = tmp[key]
        
        await asyncio.sleep(0.01)

    
    def on_a_change(self, value):
        pass
    
    def on_b_change(self, value):
        pass
    
    def on_c_change(self, value):
        pass

    def on_d_change(self, value):
        pass
    
    def on_e_change(self, value):
        pass 
    
    def on_f_change(self, value):
        pass

    def on_g_change(self, value):
        pass
    
    def on_h_change(self, value):
        pass
    
    def on_i_change(self, value):
        pass
    
    def on_j_change(self, value):
        pass
    
    def on_k_change(self, value):
        pass
    
    def on_l_change(self, value):
        pass
    
    def on_m_change(self, value):
        pass
    
    def on_n_change(self, value):
        pass
    
    def on_o_change(self, value):
        pass
    
    def on_p_change(self, value):
        pass
    
    def on_q_change(self, value):
        pass
    
    async def send_server_func(self, websocket):
        self.send_dict['A_region'] = 80
        self.send_dict['B_region'] = self.b_value
        self.send_dict['C_region'] = self.c_value
        self.send_dict['D_region'] = self.d_value
        self.send_dict['E_region'] = self.e_value
        self.send_dict['F_region'] = self.f_value
        self.send_dict['G_region'] = self.g_value
        self.send_dict['H_region'] = self.h_value
        self.send_dict['I_region'] = self.i_value
        self.send_dict['J_region'] = self.j_value
        self.send_dict['L_region'] = self.l_value
        self.send_dict['M_region'] = self.m_value
        self.send_dict['O_region'] = self.o_value
        self.send_dict['P_region'] = self.p_value
        self.send_dict['N_region'] = self.n_value
        
        await websocket.send(json.dumps(self.send_dict))
        # await websocket.send(self.send_dict)
        await asyncio.sleep(0.01)

    async def main_logic_1(self, websocket, path):
        while 1:
            await self.send_server_func(websocket)
            await self.recv_server_func(websocket)
            

    # async def main_logic_2(self, websocket, path):
    #     while 1:
    #         await self.send_server_func(websocket)
            
    def start_loop(self): 
        try:
            for _ in range(10):
                ip = getIP()
                # ip = '192.168.18.27'
                if ip:
                    print("IP Address: "+ ip)
                    # start_http_server()
                    break
                time.sleep(1)
            # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            # localhost_pem = pathlib.Path(__file__).with_name("server.pem")
            # ssl_context.load_cert_chain(localho st_pem)
            start_server_1 = websockets.serve(self.main_logic_1, ip, 8765)
            # start_server_2 = websockets.serve(self.main_logic_2, ip, 8766)
            print('Start!')
            tasks = [self.main_loop_frame(), start_server_1]
            asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
            asyncio.get_event_loop().run_forever()
 
        finally:
            print("Finished")
            
            
if __name__ == "__main__":
    ws = Websocket()
    ws.start_loop()
            