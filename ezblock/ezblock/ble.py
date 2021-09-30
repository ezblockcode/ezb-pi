from serial import Serial as UART
import time
import threading
from .basic import _Basic_class

'''
Test AT command:
AT+BLENAME=ezb-PB01
AT+BLESERUUID=FB349B5F8000008000100000CDAB0000
AT+BLETXUUID=FB349B5F8000008000100000F2FF0000
AT+BLERXUUID=FB349B5F8000008000100000F3FF0000
AT+RST
AT+BLENAME=ezb-TB04
AT+BLESERUUID=0000FFF000001000800000805F9B34FB
AT+BLETXUUID=0000FFF200001000800000805F9B34FB
AT+BLERXUUID=0000FFF300001000800000805F9B34FB
AT+RST
'''


class BLE(_Basic_class):
    DEFAULT_NAME = "ezb-TB04"
    COMMAND_DELAY = 0.1
    MODULE_TYPE = "TB"

    UUID_BASE = "0000{}00001000800000805F9B34FB"
    SERVICE_UUID = UUID_BASE.format("FFF0")
    TX_UUID = UUID_BASE.format("FFF2")
    RX_UUID = UUID_BASE.format("FFF3")

    def __init__(self, port='/dev/serial0', baudrate=115200, debug=False):
        super().__init__()
        self.uart = UART(port, baudrate, timeout=2)
        # self.flush()
        self.is_trans = -1
        self.is_disconnected = True
        value = self.write_command("AT", head="")
        if value != False:
            value = self.write_command("ATE0", head="")
            value = self.get("BLENAME")
            print(value.encode())
            if value != self.DEFAULT_NAME:
                self.set("BLENAME", self.DEFAULT_NAME)
                time.sleep(self.COMMAND_DELAY)
                self.set("BLESERUUID", self.SERVICE_UUID)
                time.sleep(self.COMMAND_DELAY)
                self.set("BLETXUUID", self.TX_UUID)
                time.sleep(self.COMMAND_DELAY)
                self.set("BLERXUUID", self.RX_UUID)
                time.sleep(self.COMMAND_DELAY)
                self.write_command("RST", expect=None)
                time.sleep(1)
                self.flush()
        time.sleep(0.01)

    def flush(self):
        self.readline()

    def _readline(self):
        buf = ""
        while True:
            tmp = self.uart.read()
            buf += tmp.decode()
            if buf.endswith("\n"):
                break
        value = buf.strip()
        return value

    def readline(self):
        tmp = self._readline()
        if self.MODULE_TYPE == "PB" and tmp == 'DISCONNECT OK' or \
           self.MODULE_TYPE == "TB" and tmp == '+BLE_DISCONNECTED':
            self.is_disconnected = True
            self.debug("Bluetooth Disconnected")
            tmp = ""
        elif self.MODULE_TYPE == "PB" and tmp == 'CON OK' or \
             self.MODULE_TYPE == "TB" and tmp == '+BLE_CONNECTED':
            self.is_disconnected = False
            self.debug("Bluetooth Connected")
            tmp = ""
        # if tmp != "":
        #     print(tmp.encode())
        return tmp

    # def readline(self):
        # value = self.uart.readline()
        # print(value)
        # value = value.decode().strip()
        # if value == 'DISCONNECT OK':
        #     self.is_disconnected = True
        #     value = ""
        # elif value == 'CON OK':
        #     self.is_disconnected = False
        #     value = ""
        # return value

    def write(self, data, end="\n"):
        data += end
        print("BLE.write: %s" % data.encode())
        data = data.encode('utf-8')
        self.uart.write(data)

    def write_command(self, data, head="AT+", end="\r\n", expect="OK"):
        print("BLE.write_command: %s" % data)
        buf = ""
        for _ in range(10):
            self.write(head + data, end=end)
            if expect == None:
                return
            for _ in range(3):
                # print("read loop")
                temp = self.readline()
                if temp != "":
                    print("temp: %s" % temp)
                    buf += temp
                    if buf.endswith(expect):
                        return buf.replace(expect, "")
                    else:
                        print("buf not ends with %s"%expect)
            time.sleep(0.1)
        else:
            print("Timeout")
            return False

    def get(self, command):
        result = self.write_command(command+"?")
        for line in result.split("\r\n"):
            if ":" in line:
                value = line.split(":")[1]
                break
        else:
            return False
        value = value.strip()
        return value

    def set(self, command, value):
        return self.write_command(command+"="+value)

    def is_connected(self):
        print("BLE.is_connected")
        result = self.get("BLESTATE")
        return result == "1"

    def reset(self):
        self.write_command("RST", expect=None)
        time.sleep(0.5)
        self.write_command("AT", head="")

    def set_name(self, name):
        print("BLE.set_name: %s" % name)
        current_name = self.get("BLENAME")
        print("current_name: %s" % current_name.encode())
        if current_name != name:
            self.set("BLENAME", name)
            self.reset()

    def exit_trans(self):
        if self.is_trans != False:
            print("BLE.exit_trans")
            self.write_command("+++", head="", end="", expect=None, force=False)
            self.is_trans = False

    def enter_trans(self):
        if self.is_trans != True:
            print("BLE.enter_trans")
            self.write_command("TRANSENTER", expect=None, force=False)
            self.is_trans = True
