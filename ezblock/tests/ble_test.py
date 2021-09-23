from serial import Serial as UART
import time
import threading

SERVICE_UUID = "55e405d2af9fa98fe54a7dfe43535355"
TX_UUID      = "16962447c62361bad94b4d1e43535349"
RX_UUID      = "16962447c62361bad94b4d1e43535349"

SERVICE_UUID = "55535343fe7d4ae58fa99fafd205e455"
TX_UUID      = "495353431e4d4bd9ba6123c647249616"
RX_UUID      = "495353431e4d4bd9ba6123c647249616"

class BLE():
    def __init__(self, port='/dev/cu.usbserial-14320', baudrate=115200, debug=False):
        super().__init__()
        self.uart = UART(port, baudrate)
        self.uart.flush()
        self.is_trans = -1

    def read(self, timeout=1):
        buf = b""
        start = time.time()
        while time.time()-start < timeout:
            while self.uart.inWaiting():
                buf = buf + self.uart.read(self.uart.inWaiting())
            if buf != b"":
                return buf.decode()
        return False

    def write(self, data, end="\r\n", force=True):
        print("BLE.write: %s" % data)
        if force:
            self.enter_trans()
        data += end
        data = data.encode('utf-8')
        self.uart.write(data)

    def write_command(self, data, head="AT+", end="\r\n", expect="OK\r\n", force=True):
        print("BLE.write_command: %s" % data)
        if force:
            self.exit_trans()
        buf = ""
        for _ in range(10):
            self.write(head + data, end=end, force=False)
            if expect == None:
                return
            else:
                for _ in range(3):
                    print("read loop")
                    temp = self.read()
                    if temp != False:
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

print("Start!")

ble = BLE()

ble.set_name("ezb-Test")
print(ble.is_connected())
# while True:
#     a = ble.read()
#     if a != "":
#         ble.write(a)
print("finished")