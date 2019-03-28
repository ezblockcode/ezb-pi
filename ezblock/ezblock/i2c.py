from ezblock.basic import _Basic_class
from smbus import SMBus

class I2C(_Basic_class):
    MASTER = 0
    SLAVE  = 1
    RETRY = 5

    def __init__(self, bus=None, baudrate=None):
        super().__init__()
        if bus == None:
            self._bus = 1
        else:
            self._bus = bus
        # self._addr = addr
        self._baudrate = baudrate
        self._smbus = SMBus(self._bus)

    def _i2c_write_byte(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.write_byte(**karg)
                return True
            except:
                pass
        return self._smbus.write_byte(**karg)
    
    def _i2c_write_byte_data(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.write_byte_data(**karg)
                return True
            except:
                pass
        return self._smbus.write_byte_data(**karg)
    
    def _i2c_write_word_data(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.write_word_data(**karg)
                return True
            except:
                pass
        return self._smbus.write_word_data(**karg)
    
    def _i2c_write_i2c_block_data(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.write_i2c_block_data(**karg)
                return True
            except:
                pass
        return self._smbus.write_i2c_block_data(**karg)
    
    def _i2c_read_byte(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.read_byte(**karg)
            except:
                pass
        self._smbus.read_byte(**karg)

    def _i2c_read_i2c_block_data(self, **karg):
        for i in range(self.RETRY):
            try:
                return self._smbus.read_i2c_block_data(**karg)
            except:
                pass
        self._smbus.read_i2c_block_data(**karg)

    def is_ready(self, addr):
        addresses = self.scan()
        if addr in address:
            return True
        else:
            return False

    def scan(self):
        cmd = "i2cdetect -y %s" % self._bus
        output = self.run_command(cmd)
        outputs = output.split('\n')[1:]
        self.debug("outputs")
        addresses = []
        for tmp_addresses in outputs:
            tmp_addresses = tmp_addresses.split(':')[1]
            tmp_addresses = tmp_addresses.strip().split(' ')
            for address in tmp_addresses:
                if address != '--':
                    addresses.append(address)
        self.debug("Conneceted i2c device: %s"%addresses)
        return addresses

    def send(self, send, addr, timeout=0):
        if isinstance(send, bytearray):
            data_all = list(send)
        elif isinstance(send, int):
            data_all = []
            for i in range(0, 100):
                d = send >> (8*i) & 0xFF
                if d == 0:
                    break
                else:
                    data_all.append(d)
            data_all.reverse()
        if len(data_all) == 1:
            data = data_all[0]
            self._i2c_write_byte(addr, data)
        elif len(data_all) == 2:
            reg = data_all[0]
            data = data_all[1]
            self._i2c_write_byte_data(addr, reg, data)
        elif len(data_all) == 3:
            reg = data_all[0]
            data = data_all[1] << 8 + data_all[2]
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
        elif isinstance(data, int):
            data_all = []
            for i in range(0, 100):
                d = data >> (8*i) & 0xFF
                if d == 0:
                    break
                else:
                    data_all.append(d)
            data_all.reverse()
        self._i2c_write_i2c_block_data(addr, memaddr, data_all)
    
    def mem_read(self, data, addr, memaddr, timeout=5000, addr_size=8):
        if isinstance(data, int):
            num = data
        elif isinstance(data, bytearray):
            num = len(data)
        else:
            return False
        result = bytearray(num)
        result = self._i2c_read_i2c_block_data(addr, memaddr, num)
        return result