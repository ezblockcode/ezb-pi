from raspberrypi.basic import _Basic_class
from raspberrypi.uart import UART

class BLE(_Basic_class):
    def __init__(self, debug=False):
        super().__init__()
        self.uart = UART()
        self.uart.init(115200)
        #self.uart = UART(1)
        #self.uart.init(9600)
        self.DEBUG = debug

    def debug(self, msg, end='\n'):
        if self.DEBUG:
            print(msg, end=end)

    def read(self, num=None):
        if num == None:
            result = self.uart.read()
        else:
            result = self.uart.read(num)
        return result

    def writechar(self, data):
        self.uart.writechar(data)

    def write(self, data):
        data = data.encode('utf-8')
        self.uart.write(data)
