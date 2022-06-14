
from os import name
import time

from .filedb import fileDB
from .basic import _Basic_class
from .ble_uart import BLE_UART, LOCAL_NAME
from .utils import  log

def _log(msg:str, location='BLE', end='\n', flush=False, timestamp=True):
    log(msg, location, end='\n', flush=False, timestamp=True)


class BLE(_Basic_class):
    def __init__(self,name=LOCAL_NAME):
        super().__init__()
        if not self.is_ble_only():
            _log("Not BLE only, changing config")
            self.run_command("sudo btmgmt power off")
            self.run_command("sudo btmgmt le on")
            self.run_command("sudo btmgmt bredr off")
            self.run_command("sudo btmgmt power on")
            time.sleep(0.5)
            self.is_ble_only()

        self.uart = BLE_UART(name)
    

    def reset(self):
        _log("BLE: reset")
        self.run_command("sudo btmgmt power off")
        time.sleep(0.5)
        self.run_command("sudo btmgmt power on")
        time.sleep(0.5)

    def read(self, num=None):
        if num == None:
            result = self.uart.read_buf
            self.uart.read_buf = ""
        else:
            result = self.uart.read_buf[:num]
            self.uart.read_buf = self.uart.read_buf[num:]
        if result != "":
            _log("BLE: read: %s" % result.encode())
        return result

    def readline(self):
        result = ""
        for _ in range(10):
            result += self.read()
            if result.endswith("\n"):
                return result.strip("\n")
        return result

    def flush(self):
        self.uart.read_buf = ""

    def writechar(self, data):
        self.uart.send_tx(data)

    # def write(self, data, end="\n"):
    #     data += end
    def write(self, data):
        _log("BLE: write: %s" % data)
        self.uart.send_tx(data)

    def inWaiting(self):
        return len(self.uart.read_buf)

    def is_ble_only(self):
        settings = []
        _, result = self.run_command("sudo btmgmt info")
        for line in result.split("\n"):
            line = line.strip()
            if line.startswith("current settings: "):
                settings = line.replace("current settings: ", "").split(" ")
                if "br/edr" in settings or "le" not in settings:
                    _log('BLE: settings: %s'%settings)
                    return False
                else:
                    return True
