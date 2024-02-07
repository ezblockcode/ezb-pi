from .basic import _Basic_class
import gpiozero # https://gpiozero.readthedocs.io/en/latest/installing.html

class Pin(_Basic_class):
    """Pin manipulation class"""

    OUT = 0x01
    """Pin mode output"""
    IN = 0x02
    """Pin mode input"""

    PULL_UP = 0x11
    """Pin internal pull up"""
    PULL_DOWN = 0x12
    """Pin internal pull down"""
    PULL_NONE = None
    """Pin internal pull none"""

    IRQ_FALLING = 0x21
    """Pin interrupt falling"""
    IRQ_RISING = 0x22
    """Pin interrupt falling"""
    IRQ_RISING_FALLING = 0x23
    """Pin interrupt both rising and falling"""

    _dict = {
        "BOARD_TYPE": 12,
    }

    _dict_1 = {
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
        "USR":  19,
        "LED": 26,
        "BOARD_TYPE": 12,
        "RST": 16,
        "D13": 13,
        "D20": 20, # BLE_reset
        "MCURST": 21,
    }

    _dict_2 = {
        "D0":  17,
        "D1":   4, # Changed
        "D2":  27,
        "D3":  22,
        "D4":  23,
        "D5":  24,
        "D6":  25, # Removed
        "D7":   4, # Removed
        "D8":   5, # Removed
        "D9":   6,
        "D10": 12,
        "D11": 13,
        "D12": 19,
        "D13": 16,
        "D14": 26,
        "D15": 20,
        "D16": 21,
        "SW":  25, # Changed
        "USR":  19,
        "LED": 26,
        "BOARD_TYPE": 12,
        "RST": 16,
        "D13": 13,
        "D20": 20, # BLE_reset
        "MCURST":  5, # Changed
    }

    def __init__(self, *value):
        super().__init__()

        self.check_board_type()

        if len(value) > 0:
            pin = value[0]
        if len(value) > 1:
            mode = value[1]
        else:
            mode = None
        if len(value) > 2:
            setup = value[2]
        else:
            setup = None
        if isinstance(pin, str):
            try:
                self._board_name = pin
                self._pin = self.dict()[pin]
            except Exception as e:
                print(e)
                self._error('Pin should be in %s, not %s' % (self._dict.keys(), pin))
        elif isinstance(pin, int):
            self._pin = pin
        else:
            self._error('Pin should be in %s, not %s' % (self._dict.keys(), pin))
        # setup
        self._value = 0
        self.gpio = None
        self.init(mode, pull=setup)
        self._info("Pin init finished.")
        
    def check_board_type(self):
        type_pin = self.dict()["BOARD_TYPE"]
        _pin = gpiozero.Button(type_pin, pull_up=True)
        if _pin.value == 0:
            self._dict = self._dict_1
        else:
            self._dict = self._dict_2
        _pin.close()

    def close(self):
        self.gpio.close()

    def init(self, mode, pull=PULL_NONE):
        # check mode
        if mode in [None, self.OUT, self.IN]:
            self._mode = mode
        else:
            raise ValueError(
                f'mode param error, should be None, Pin.OUT, Pin.IN')
        # check pull
        if pull in [self.PULL_NONE, self.PULL_DOWN, self.PULL_UP]:
            self._pull = pull
        else:
            raise ValueError(
                f'pull param error, should be None, Pin.PULL_NONE, Pin.PULL_DOWN, Pin.PULL_UP')

        self._pull = pull
        self._mode = mode

        if self.gpio != None:
            if self.gpio.pin != None:
                self.gpio.close()

        if mode in [None, self.OUT]:
            self.gpio = gpiozero.OutputDevice(self._pin)
        else:
            if pull in [None, self.PULL_UP]:
                self.gpio = gpiozero.Button(self._pin, pull_up=True)
            else:
                self.gpio = gpiozero.Button(self._pin, pull_up=False)


    def dict(self, *_dict):
        if len(_dict) == 0:
            return self._dict
        else:
            if isinstance(_dict, dict):
                self._dict = _dict
            else:
                self._error(
                    'argument should be a pin dictionary like {"my pin": ezblock.Pin.cpu.GPIO17}, not %s' % _dict)

    def __call__(self, value):
        return self.value(value)

    def value(self, *value):
        if value == None:
            if self._mode in [None, self.OUT]:
                self.init(self.IN)
            result = self.gpio.value
            self._debug(f"read pin {self.gpio.pin}: {result}")
            return result
        else:
            if self._mode in [None, self.IN]:
                self.init(self.OUT)
            if bool(value):
                value = 1
                self.gpio.on()
            else:
                value = 0
                self.gpio.off()
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
            mode = value[0]
            self._mode = mode
            self.init(mode)

    def pull(self, *value):
        return self._pull

    def irq(self, handler=None, trigger=None, bouncetime=200, pull=None):
        # check trigger
        if trigger not in [None, self.IRQ_FALLING, self.IRQ_RISING, self.IRQ_RISING_FALLING]:
            raise ValueError(
                f'trigger param error, should be None, Pin.IRQ_FALLING, Pin.IRQ_RISING, Pin.IRQ_RISING_FALLING')
        #
        self.init(self.IN, pull, bouncetime)
        #
        if trigger in [None, self.IRQ_FALLING]:
            self.gpio.when_pressed = handler
        elif trigger in [self.IRQ_RISING]:
            self.gpio.when_released = handler
        elif trigger in [self.IRQ_RISING_FALLING]:
            self.gpio.when_pressed = handler
            self.gpio.when_released = handler

    def name(self):
        return "GPIO%s"%self._pin

    def names(self):
        return [self.name, self._board_name]

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
