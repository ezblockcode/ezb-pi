from ezblock.pwm import PWM
import time


class Servo(PWM):
    MAX_PW = 2500
    MIN_PW = 500
    _freq = 50
    def __init__(self, channel):
        super().__init__(channel)
        self.period(4095)
        prescaler = int(float(self.CLOCK) /self._freq/self._arr)
        self.prescaler(prescaler)
        self.angle(90)

    # angle ranges -90 to 90 degrees
    def angle(self, angle):
        try:
            angle = int(angle)
        except:
            raise ValueError("Angle value should be int value, not %s"%angle)
        if angle < -90:
            angle = -90
        if angle > 90:
            angle = 90
        High_level_time = self.map(angle, -90, 90, self.MIN_PW, self.MAX_PW)
        self._debug("High_level_time: %f" % High_level_time)
        pwr =  High_level_time / 20000
        self._debug("pulse width rate: %f" % pwr)
        value = int(pwr*4095)
        self._debug("pulse width value: %f" % value)
        self.pulse_width(value)

def test():
    print("Test")
    s0 = Servo(0)
    s0.debug = "debug"
    s0.angle(90)
    
if __name__ == "__main__":
    test()