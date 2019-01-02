from raspberrypi.pin import Pin
import time
import os
ds18b20 = ''

class DHT11(Pin):
    MAX_UNCHANGE_COUNT = 100

    STATE_INIT_PULL_DOWN = 1
    STATE_INIT_PULL_UP = 2
    STATE_DATA_FIRST_PULL_DOWN = 3
    STATE_DATA_PULL_UP = 4
    STATE_DATA_PULL_DOWN = 5

    def __init__(self, pin):
        # super().__init__()
        self.pin = pin
        

    def read_dht11(self):
        self.pin.high()
        time.sleep(0.05)
        self.pin.low()
        time.sleep(0.02)

        unchanged_count = 0
        last = -1
        data = []
        while True:
            current = self.pin.value()
            data.append(current)
            if last != current:
                unchanged_count = 0
                last = current
            else:
                unchanged_count += 1
                if unchanged_count > self.MAX_UNCHANGE_COUNT:
                    break

        state = self.STATE_INIT_PULL_DOWN

        lengths = []
        current_length = 0

        for current in data:
            current_length += 1

            if state == self.STATE_INIT_PULL_DOWN:
                if current == 0:
                    state = self.STATE_INIT_PULL_UP
                else:
                    continue
            if state == self.STATE_INIT_PULL_UP:
                if current == 1:
                    state = self.STATE_DATA_FIRST_PULL_DOWN
                else:
                    continue
            if state == self.STATE_DATA_FIRST_PULL_DOWN:
                if current == 0:
                    state = self.STATE_DATA_PULL_UP
                else:
                    continue
            if state == self.STATE_DATA_PULL_UP:
                if current == 1:
                    current_length = 0
                    state = self.STATE_DATA_PULL_DOWN
                else:
                    continue
            if state == self.STATE_DATA_PULL_DOWN:
                if current == 0:
                    lengths.append(current_length)
                    state = self.STATE_DATA_PULL_UP
                else:
                    continue
        if len(lengths) != 40:
            return False

        shortest_pull_up = min(lengths)
        longest_pull_up = max(lengths)
        halfway = (longest_pull_up + shortest_pull_up) / 2
        bits = []
        the_bytes = []
        byte = 0

        for length in lengths:
            bit = 0
            if length > halfway:
                bit = 1
            bits.append(bit)
        #print "bits: %s, length: %d" % (bits, len(bits))
        for i in range(0, len(bits)):
            byte = byte << 1
            if (bits[i]):
                byte = byte | 1
            else:
                byte = byte | 0
            if ((i + 1) % 8 == 0):
                the_bytes.append(byte)
                byte = 0
        #print the_bytes
        checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
        if the_bytes[4] != checksum:
            return False

        return the_bytes[0], the_bytes[2]

    def read(self, max_times=30):
        for i in range(max_times):
            result = self.read_dht11()
            if result:
                return result
        return False






class Ultrasonicranging(object):

    def __init__(self, trig, echo, timeout=0.02):
        self.trig = trig
        self.echo = echo
        self.timeout = timeout

    def value(self):
        self.trig.low()
        time.sleep(0.5)
        self.trig.high()
        time.sleep(0.00001)
        self.trig.low()
        pulse_end = 0

        timeout_start = time.time()
        while self.echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while self.echo.value()==1:
            pulse_end = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1

        during = pulse_end - pulse_start
        return during * 340 / 2 * 100




class DS18B20(Pin):
    F = 0
    C = 1

    def __init__(self):
        for i in os.listdir('/sys/bus/w1/devices'):
            if i.startswith('28-'):
                self.ds18b20 = i

    def value(self, unit=1):
        self.unit = unit
        location = '/sys/bus/w1/devices/' + self.ds18b20 + '/w1_slave'
        with open(location) as f:
            text = f.read()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        if self.unit == 1:
            pass
        else:
            temperature = 32 + temperature*1.8
        return temperature