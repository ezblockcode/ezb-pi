from .basic import _Basic_class
from .uart import UART
from time import sleep
import json

class BLE(_Basic_class):
    def __init__(self, port='/dev/serial0', baudrate=115200, debug=False):
        super().__init__()
        self.uart = UART(port, baudrate)
        self.is_trans = False

    def read_raw(self, num=None):
        buf = b""
        if num == None:
            while self.uart.inWaiting():
                buf = buf + super().read(self.uart.inWaiting())
        else:
            result = self.uart.read(num)
        return result

    def read(self, num=None):
        return self.read_raw(num).decode()

    def write_raw(self, data):
        data = data.encode('utf-8')
        self.uart.write(data)

    def write(self, data):
        self.write_data(data)
    
    def write_data(self, data):
        self.enter_trans()
        data += "\r\n"
        self.write_raw(data)

    def write_command(self, command):
        self.exit_trans()
        data += "\r\n"
        self.write_raw(data)
        self.read(data)

    def is_connected(self):
        self.write_command("AT+BLESTATE?")
        self.read()

    def set_name(self, name):

    def exit_trans(self):
        if self.is_trans:
            self.write_raw("+++")
            self.is_trans = False

    def enter_trans(self):
        if not self.is_trans:
            self.write_raw("AT+TRANSENTER\r\n")
            self.is_trans = True
