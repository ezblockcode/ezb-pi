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

    BOARD_TYPE_PIN = 12

    pin_dict = {
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
        "USR": 25,
        "LED": 26,
        "BOARD_TYPE": 12,
        "RST": 16,
        "D13": 13,
        "D20": 20, # BLE_reset
        "MCURST":  5, # Changed
    }

    def __init__(self, *value):
        super().__init__()

        self._dict = self.pin_dict
 
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
                self._pin = self.pin_dict[pin]
            except Exception as e:
                print(e)
                self._error('Pin should be in %s, not %s' % (self.pin_dict.keys(), pin))
        elif isinstance(pin, int):
            self._pin = pin
        else:
            self._error('Pin should be in %s, not %s' % (self.pin_dict.keys(), pin))
        # setup
        self._value = 0
        self.gpio = None

        self.init(mode, pull=setup)

        self._info("Pin init finished.")
        
    @staticmethod
    def check_board_type():
        _type_pin = gpiozero.InputDevice(Pin.pin_dict['BOARD_TYPE'], pull_up=False)
        _board_type = _type_pin.value
        _type_pin.close()
        # _type_pin.pin_factory.close()
        return _board_type

    def close(self):
        self.gpio.close()

    def init(self, mode, pull=PULL_NONE, bouncetime=None):
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
        # check bouncetime
        if bouncetime is None:
            self._bouncetime = bouncetime
        elif isinstance(bouncetime, float) or isinstance(bouncetime, int):
            self._bouncetime = bouncetime
            bouncetime = self._bouncetime / 1000.0
        else:
          raise ValueError(
                f'bouncetime param error, should be None, float, or int (unit:)')
              
        if self.gpio != None:
            if self.gpio.pin != None:
                self.gpio.close()

        if mode in [None, self.OUT]:
            self.gpio = gpiozero.OutputDevice(self._pin)

        else:
            if pull in [None, self.PULL_UP]:
                # self.gpio = gpiozero.InputDevice(self._pin, pull_up=True, bounce_time=bouncetime)
                self.gpio = gpiozero.InputDevice(self._pin, pull_up=True)
            else:
                # self.gpio = gpiozero.InputDevice(self._pin, pull_up=False, bounce_time=bouncetime)
                self.gpio = gpiozero.InputDevice(self._pin, pull_up=False)


    def __call__(self, value):
        return self.value(value)

    def value(self, value=None):
        if value == None:
            if self._mode in [None, self.OUT]:
                self.init(self.IN)
            result = 0 if self.gpio.value else 1 # reverse
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
        pressed_handler = None
        released_handler = None

        if bouncetime != self._bouncetime:
            if self.gpio is not None and self._mode == self.IN:
                pressed_handler = self.gpio.when_pressed
                released_handler = self.gpio.when_released
            self.init(self.IN, pull, bouncetime)
        #
        if trigger in [None, self.IRQ_FALLING]:
            pressed_handler = handler
        elif trigger in [self.IRQ_RISING]:
            released_handler = handler
        elif trigger in [self.IRQ_RISING_FALLING]:
            pressed_handler = handler
            released_handler = handler
        #
        if pressed_handler is not None:
            self.gpio.when_pressed = pressed_handler
        if released_handler is not None:
            self.gpio.when_released = released_handler

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
