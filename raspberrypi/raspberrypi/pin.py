from raspberrypi.basic import _Basic_class
import RPi.GPIO as GPIO

class Pin(_Basic_class):
    OUT = GPIO.OUT
    IN = GPIO.IN
    IRQ_FALLING = GPIO.FALLING
    IRQ_RISING = GPIO.RISING
    PULL_UP = GPIO.PUD_UP
    PULL_DOWN = GPIO.PUD_DOWN
    _dict = {
        "D0":  17,
        "D1":  18,
        "D2":  27,
        "D3":  22,
        "D4":  23,
        "D5":  24,
        "D6":  25,
        "D7":  4,
        "D8":  5,
        "D9":  6,
        "D10": 12,
        "D11": 13,
        "D12": 19,
        "D13": 16,
        "D14": 26,
        "D15": 20,
        "D16": 21,
        "SW":  19,
        "LED": 26,
        "PWR": 12,
        "RST": 16,
        "BLEINT": 13,
    }

    def __init__(self, pin):
        super().__init__()
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        if isinstance(pin, str):
            try:
                self._bname = pin
                self._pin = self.dict()[pin]
            except Exception as e:
                print(e)
                self._error('Pin should be in %s, not %s' % (self._dict, pin))
        elif isinstance(pin, int):
            self._pin = pin
        else:
            self._error('Pin should be in %s, not %s' % (self._dict, pin))
        self._value = 0
        self._pull = self.PULL_UP
        self._mode = None
        self._info("Pin init finished.")
        
    def dict(self, *_dict):
        if len(_dict) == 0:
            return self._dict
        else:
            if isinstance(_dict, dict):
                self._dict = _dict
            else:
                self._error(
                    'argument should be a pin dictionary like {"my pin": raspberrypi.Pin.cpu.GPIO17}, not %s' % _dict)

    def __call__(self, value):
        return self.value(value)

    def value(self, *value):
        if len(value) == 0:
            self.mode(self.IN)
            result = GPIO.input(self._pin)
            self._debug("read pin %s: %s" % (self._pin, result))
            return result
        else:
            value = value[0]
            self.mode(self.OUT)
            GPIO.output(self._pin, value)
            return value

    def on(self):
        return self.value(1)

    def off(self):
        return self.value(0)

    def high(self):
        return self.on()

    def low(self):
        return self.off()

    def mode(self, *value):
        if len(value) == 0:
            return self._mode
        else:
            value = value[0]
            if value != self._mode:
                self._mode = value
                GPIO.setup(self._pin, self._mode)
                return self._mode

    def pull(self, *value):
        if len(value) == 0:
            return self._pull
        else:
            value = value[0]
            self._pull = value
            self._mode = self.IN
            GPIO.setup(self._pin, self._mode, pull_up_down=value)

    def irq(self, handler=None, trigger=None):
        self.mode(self.IN)
        GPIO.add_event_detect(self._pin, trigger, callback=handler)

    def name(self):
        return "GPIO%s"%self._pin

    def names(self):
        return [self.name, self._bname]

    class cpu(object):
        GPIO17 = 17
        GPIO18 = 18
        GPIO27 = 27
        GPIO22 = 22
        GPIO23 = 23
        GPIO24 = 24
        GPIO25 = 25
        GPIO26 = 26
        GPIO4  = 4
        GPIO5  = 5
        GPIO6  = 6
        GPIO12 = 12
        GPIO13 = 13
        GPIO19 = 19
        GPIO16 = 16
        GPIO26 = 26
        GPIO20 = 20
        GPIO21 = 21

        def __init__(self):
            pass
