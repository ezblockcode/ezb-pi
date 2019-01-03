from raspberrypi.basic import _Basic_class
from raspberrypi.uart import UART
from raspberrypi import delay

class BLE(_Basic_class):
    # Delay between every 20 Byte
    SEND_DELAY = 100
    # Length of every package bluetooth sent
    DATA_LENGTH = 20
    def __init__(self, debug=False):
        super().__init__()
        self.uart = UART()
        self.uart.init(115200)
        #self.uart = UART(1)
        #self.uart.init(9600)

    def read(self, num):
        result = self.uart.read(num)
        return result

    def writechar(self, data):
        self.uart.writechar(data)

    def write(self, data):
        data = data.encode('utf-8')
        for i in range(0, len(data), self.DATA_LENGTH):
            temp = data[i:i+self.DATA_LENGTH]
            delay(self.SEND_DELAY)
            self.uart.write(temp)

    def verify(self, raw_data):
        self._debug("Flash.verify")
        import re
        self._debug("raw_data: %s" % raw_data)
        data_type = None
        data = None
        data_head = re.search('[*][$][A-Z]+[#][H][#]\d+[$][*]', raw_data)
        data_tail = re.search('[*][$][A-Z]+[#][T][#]\d+[$][*]', raw_data)
        ble = BLE()
        if data_head and data_tail:
            self._debug("Tansfer finished!")
            data_head = data_head.group(0)
            data_tail = data_tail.group(0)
            data_head_info = data_head.strip('*').strip('$').split('#')
            data_head_type = data_head_info[0]
            data_tail_info = data_tail.strip('*').strip('$').split('#')
            data_tail_type = data_tail_info[0]
            if data_head_type == data_tail_type:
                data_type = data_head_type
                self._debug("Tranfer type: %s" % data_type)
                expect_data_length = int(data_head_info[2])
                data = raw_data.split(data_head)[1].split(data_tail)[0]
                data_length = len(data)
                if expect_data_length == data_length:
                    self._debug("Verified!")
                    ble.write("1")
                    return [data_type, data, True]
                else:
                    self._debug("Verified error, expecting %s, received %s" %
                        (expect_data_length, data_length))
                    ble.write("0")
            else:
                self._debug("Verified error, data head type is %s, while data tail type is %s" % (
                    data_head_type, data_tail_type))
        else:
            self._debug("Verified error, head or tail not found")
        return [None, None, False]