from serial import Serial

class UART(object):
    def __init__(self):
        self._port = '/dev/serial0'

    def init(self, baudrate):
        self._baudrate = baudrate
        self.ser = Serial(self._port, self._baudrate, timeout=1)

    def deinit(self):
        pass

    def read(self, num):
        buf = self.ser.read(num)
        # buf = buf.decode('utf-8')
        return buf

    def readinto(self, buf):
        #buf = self.ser.read(num)
        pass

    def readline(self):
        pass

    def write(self, buf):
        # buf = buf.encode('utf-8')
        self.ser.write(buf)

    def writechar(self, buf):
        # buf = buf.encode('utf-8')
        self.ser.write(buf)
