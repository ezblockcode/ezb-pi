# file: rfcomm-server.py
# auth: Dino Horvat <dxh3401@rit.edu>
# desc: sending the server IP to the client over rfcomm 
from bluetooth import *
import socket
import subprocess
import time

# Subprocess has to be run after bluetoothservice is up, therefore the sleep is there
time.sleep(5)
cmd = 'hciconfig hci0 piscan'
subprocess.check_output(cmd, shell = True )

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def client_connect():
    client_sock, client_info = server_sock.accept()
    print("Accepted connection from ", client_info)
    client_sock.send(get_ip())
    try:
       while True:
           data = client_sock.recv(1024)
           if len(data) == 0: break
           print("received [%s]" % data)
           client_sock.send(get_ip())
    except IOError:
       pass

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
# uuid = "fff0"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
serveron = True
while(serveron==True):
    print("Waiting for connection on RFCOMM channel %d" % port)
    client_connect()
    print("disconnected")
    client_sock.close()
    server_sock.close()