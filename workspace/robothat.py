from ezblock import PWM,Pin
import time

PERIOD = 4095
PRESCALER = 10
TIMEOUT = 0.02

motor1_pwm_pin = PWM("P13")
motor2_pwm_pin = PWM("P12")
if motor1_pwm_pin.ADDR == 0x15:
    motor1_pwm_pin = PWM("P4")
    motor2_pwm_pin = PWM("P5")
motor1_dir_pin = Pin("D4")
motor2_dir_pin = Pin("D5")

motor_direction_pins = [motor1_dir_pin, motor2_dir_pin]
motor_speed_pins = [motor1_pwm_pin, motor2_pwm_pin]
cali_dir_value = [1, -1]
cali_speed_value = [0, 0]

for pin in motor_speed_pins:
    pin.period(PERIOD)
    pin.prescaler(PRESCALER)

def set_motor_speed(motor, speed):
    global cali_speed_value,cali_dir_value
    motor -= 1
    if speed >= 0:
        direction = 1 * cali_dir_value[motor]
    elif speed < 0:
        direction = -1 * cali_dir_value[motor]
    speed = abs(speed)
    if speed != 0:
        speed = int(speed /2 ) + 30
    speed = speed - cali_speed_value[motor]
    if direction > 0:
        motor_direction_pins[motor].high()
        motor_speed_pins[motor].pulse_width_percent(speed)
    else:
        motor_direction_pins[motor].low()
        motor_speed_pins[motor].pulse_width_percent(speed)

def motor_speed_calibration(value):
    global cali_speed_value
    if value < 0:
        cali_speed_value[0] = 0
        cali_speed_value[1] = abs(value)
    else:
        cali_speed_value[0] = abs(value)
        cali_speed_value[1] = 0

def motor_direction_calibration(motor, value):
    # 0: positive direction
    # 1:negative direction
    global cali_dir_value
    motor -= 1
    if value == 1:
        cali_dir_value[motor] = -cali_dir_value[motor]

     
# from ezblock import *
def test():
    set_motor_speed(1, 100)
    pin_D0=Pin("D0",)

    pin_D1=Pin("D1",)


    while True:
        print("%s"%(Ultrasonic(pin_D0, pin_D1).read()))
        delay(500)

if __name__ == "__main__":
    test()
