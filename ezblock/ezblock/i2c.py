from .basic import _Basic_class
from smbus2 import SMBus
from .utils import run_command
import time


def _retry_wrapper(func):

    def wrapper(self, *arg, **kwargs):
        for _ in range(self.RETRY):
            try:
                return func(self, *arg, **kwargs)
            except OSError:
                self._debug(f"OSError: {func.__name__}")
                continue
        else:
            return False

    return wrapper


def log(msg):
    msg = "I2C [{}] [DEBUG] {}".format(time.asctime(), msg)
    run_command("echo {} >> /opt/ezblock/log".format(msg))
    print(msg)

class I2C(_Basic_class):

    RETRY = 5

    def __init__(self, *args, **kargs): 
        super().__init__()

        self._bus = 1
        self._smbus = SMBus(self._bus)

        
    def _i2c_write_byte(self, addr, data):
        self._debug("_i2c_write_byte: [0x{:02X}] [0x{:02X}]".format(addr, data))
        return self._smbus.write_byte(addr, data)
    
    def _i2c_write_byte_data(self, addr, reg, data):
        self._debug("_i2c_write_byte_data: [0x{:02X}] [0x{:02X}] [0x{:02X}]".format(addr, reg, data))
        return self._smbus.write_byte_data(addr, reg, data)
    
    def _i2c_write_word_data(self, addr, reg, data):
        self._debug("_i2c_write_word_data: [0x{:02X}] [0x{:02X}] [0x{:04X}]".format(addr, reg, data))
        return self._smbus.write_word_data(addr, reg, data)
    
    def _i2c_write_i2c_block_data(self, addr, reg, data):
        self._debug("_i2c_write_i2c_block_data: [0x{:02X}] [0x{:02X}] {}".format(addr, reg, data))
        return self._smbus.write_i2c_block_data(addr, reg, data)
    
    def _i2c_read_byte(self, addr):
        self._debug("_i2c_read_byte: [0x{:02X}]".format(addr))
        return self._smbus.read_byte(addr)

    def _i2c_read_word_data(self, addr, reg):
        self._debug("_i2c_read_word_data: [0x{:02X}] [0x{:02X}]".format(addr, reg))
        return self._smbus.read_word_data(addr, reg)
    
    def _i2c_read_i2c_block_data(self, addr, reg, num):
        self._debug("_i2c_read_i2c_block_data: [0x{:02X}] [0x{:02X}] [{}]".format(addr, reg, num))
        return self._smbus.read_i2c_block_data(addr, reg, num)

    def is_ready(self, addr):
        addresses = self.scan()
        if addr in addresses:
            return True
        else:
            return False

    def scan(self):                            
        cmd = "i2cdetect -y %s" % self._bus
        _, output = run_command(cmd)         
        
        outputs = output.split('\n')[1:]       
        self._debug("outputs")
        addresses = []
        for tmp_addresses in outputs:
            if tmp_addresses == "":
                continue
            tmp_addresses = tmp_addresses.split(':')[1]
            tmp_addresses = tmp_addresses.strip().split(' ')    
            for address in tmp_addresses:
                if address != '--':
                    addresses.append(int(address, 16))
        self._debug("Conneceted i2c device: %s"%addresses)                 
        return addresses

    def send(self, send, addr, timeout=0):                     

        if isinstance(send, bytearray):
            data_all = list(send)
        elif isinstance(send, int):
            data_all = []
            d = "{:X}".format(send)
            d = "{}{}".format("0" if len(d)%2 == 1 else "", d) 
            # print(d)
            for i in range(len(d)-2, -1, -2):
                tmp = int(d[i:i+2], 16)
                # print(tmp)
                data_all.append(tmp) 
            data_all.reverse()
        elif isinstance(send, list):
            data_all = send
        else:
            raise ValueError("send data must be int, list, or bytearray, not {}".format(type(send)))

        if len(data_all) == 1:
            data = data_all[0]
            self._i2c_write_byte(addr, data)
        elif len(data_all) == 2:
            reg = data_all[0]
            data = data_all[1]
            self._i2c_write_byte_data(addr, reg, data)
        elif len(data_all) == 3:
            reg = data_all[0]
            data = (data_all[2] << 8) + data_all[1]
            self._i2c_write_word_data(addr, reg, data)
        else:
            reg = data_all[0]
            data = list(data_all[1:])
            self._i2c_write_i2c_block_data(addr, reg, data)

    def recv(self, recv, addr=0x00, timeout=0):

        if isinstance(recv, int):
            result = bytearray(recv)
        elif isinstance(recv, bytearray):
            result = recv
        else:
            return False
        for i in range(len(result)):
            result[i] = self._i2c_read_byte(addr)

        return result

    def mem_write(self, data, addr, memaddr, timeout=5000, addr_size=8): #memaddr match to chn
        if isinstance(data, bytearray):
            data_all = list(data)
        elif isinstance(data, list):
            data_all = data
        elif isinstance(data, int):
            data_all = []
            data = "%x"%data
            if len(data) % 2 == 1:
                data = "0" + data
            # print(data)
            for i in range(0, len(data), 2):
                # print(data[i:i+2])
                data_all.append(int(data[i:i+2], 16))
        else:
            raise ValueError("memery write require arguement of bytearray, list, int less than 0xFF")
        # print(data_all)
        self._i2c_write_i2c_block_data(addr, memaddr, data_all)
    
    def mem_read(self, data, addr, memaddr, timeout=5000, addr_size=8):     # 读取数据
        if isinstance(data, int):
            num = data
        elif isinstance(data, bytearray):
            num = len(data)
        else:
            return False
        result = bytearray(self._i2c_read_i2c_block_data(addr, memaddr, num))
        return result
    
    def readfrom_mem_into(self, addr, memaddr, buf):
        buf = self.mem_read(len(buf), addr, memaddr)
        return buf
    
    def writeto_mem(self, addr, memaddr, data):
        self.mem_write(data, addr, memaddr)

