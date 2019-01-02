from raspberrypi.pwm import PWM
import time


class Servo(PWM):
    MAX_PW = 2500
    MIN_PW = 500
    _freq = 50
    def __init__(self, channel):
        super().__init__(channel)
        self.freq(self._freq)
        self.angle(90)


    def angle(self, angle):
        High_level_time = self.map(angle, 0, 180, self.MIN_PW, self.MAX_PW)
        self._debug("High_level_time: %f" % High_level_time)
        pwr =  High_level_time/self._period
        self._debug("pulse width rate: %f" % pwr)
        value = int(pwr*4095)
        self._debug("pulse width value: %f" % value)
        self.pulse_width(value)


    

