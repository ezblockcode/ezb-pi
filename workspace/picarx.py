from ezblock import Servo, PWM, fileDB, Pin, ADC
from ezblock.user_info import USER, USER_HOME
from ezblock.utils import constrain


class PiCarX(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02
    config_file='/opt/ezblock/.config'

    DIR_MIN = -45
    DIR_MAX = 45
    CAM_PAN_MIN = -90
    CAM_PAN_MAX = 90
    CAM_TILT_MIN = -35
    CAM_TILT_MAX = 65

    def __init__(self):

        # get calibration value
        self.db = fileDB(db=self.config_file)
        self.dir_cal_value = int(self.db.get(
            "picarx_dir_servo", default_value=0))
        self.cam_cal_value_1 = int(self.db.get(
            "picarx_cam1_servo", default_value=0))
        self.cam_cal_value_2 = int(self.db.get(
            "picarx_cam2_servo", default_value=0))
        self.cali_dir_value = self.db.get(
            "picarx_dir_motor", default_value="[1, 1]")
        self.cali_dir_value = [int(i.strip())
                               for i in self.cali_dir_value.strip("[]").split(",")]
      
        # init servos
        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))

        self.set_steering_angle(0)
        self.set_camera_pan_angle(0)
        self.set_camera_tilt_angle(0)

        # init motors
        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0

        self.motor_direction_pins = [
            self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [
            self.left_rear_pwm_pin, self.right_rear_pwm_pin]

        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        self.stop()

        # init grayscale
        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

    def set_motor_speed(self, motor, speed):
        motor -= 1
        if speed >= 0:
            direction = 1 * self.cali_dir_value[motor]
        elif speed < 0:
            direction = -1 * self.cali_dir_value[motor]
        speed = abs(speed)
        if speed != 0:
            speed = int(speed / 2) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self, value):
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(value)
        else:
            self.cali_speed_value[0] = abs(value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self, motor, value):
        # 0: positive direction
        # 1: negative direction
        motor -= 1
        if value == 1:
            self.cali_dir_value[motor] = -1 * self.cali_dir_value[motor]
        self.db.set("picarx_dir_motor", self.cali_dir_value)

    def dir_servo_angle_calibration(self, value):
        self.dir_cal_value = value
        self.db.set("picarx_dir_servo", "%s" % value)
        self.dir_servo_pin.angle(value)

    def set_steering_angle(self, value):
        value = constrain(value, self.DIR_MIN, self.DIR_MAX)
        self.dir_current_angle = value
        angle_value = value + self.dir_cal_value
        self.dir_servo_pin.angle(angle_value)

    def camera_servo1_angle_calibration(self, value):
        self.cam_cal_value_1 = value
        self.db.set("picarx_cam1_servo", "%s" % value)
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self, value):
        self.cam_cal_value_2 = value
        self.db.set("picarx_cam2_servo", "%s" % value)
        self.camera_servo_pin2.angle(value)

    def set_camera_pan_angle(self, value):
        value = constrain(value, self.CAM_PAN_MIN, self.CAM_PAN_MAX)
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cal_value_1))

    def set_camera_tilt_angle(self, value):
        value = value = constrain(value, self.CAM_TILT_MIN, self.CAM_TILT_MAX)
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cal_value_2))

    def set_power(self, speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed)

    def backward(self, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, -1*speed)
                self.set_motor_speed(2, speed * power_scale)
            else:
                self.set_motor_speed(1, -1*speed * power_scale)
                self.set_motor_speed(2, speed)
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)

    def forward(self, speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            if abs_current_angle > 40:
                abs_current_angle = 30
            power_scale = (100 - abs_current_angle) / 100.0
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1*speed * power_scale)
            else:
                self.set_motor_speed(1, speed * power_scale)
                self.set_motor_speed(2, -1*speed)
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)
