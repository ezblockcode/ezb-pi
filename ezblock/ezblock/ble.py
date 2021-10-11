
import time
from .filedb import fileDB
from .basic import _Basic_class
from .ble_uart import BLE_UART

class BLE(_Basic_class):
    def __init__(self):
        super().__init__()
        if not self.is_ble_only():
            self.log("Not BLE only, changing config")
            self.run_command("sudo btmgmt power off")
            self.run_command("sudo btmgmt le on")
            self.run_command("sudo btmgmt bredr off")
            self.run_command("sudo btmgmt power on")
            time.sleep(0.5)
            self.is_ble_only()
        else:
            self.reset()

        self.uart = BLE_UART()
    
    def log(self, msg):
        msg = "BLE_UART [{}] [DEBUG] {}".format(time.asctime(), msg)
        self.run_command("echo {} >> /opt/ezblock/log".format(msg))
        print(msg)
    
    def reset(self):
        self.log("reset")
        self.run_command("sudo btmgmt power off")
        time.sleep(0.1)
        self.run_command("sudo btmgmt power on")
        time.sleep(0.1)

    def read(self, num=None):
        if num == None:
            result = self.uart.read_buf
            self.uart.read_buf = ""
        else:
            result = self.uart.read_buf[:num]
            self.uart.read_buf = self.uart.read_buf[num:]
        if result != "":
            print("BLE.read() = %s" % result.encode())
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
        print("BLE.write(%s)" % data)
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
                    self.log(settings)
                    return False
                else:
                    return True

