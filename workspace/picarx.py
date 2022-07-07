from ezblock import Servo,PWM,fileDB,Pin,ADC
import time

class Picarx(object):
    PERIOD = 4095
    PRESCALER = 10
    TIMEOUT = 0.02
    config_flie = fileDB('/opt/ezblock/.config')

    def __init__(self):
        self.dir_servo_pin = Servo(PWM('P2'))
        self.camera_servo_pin1 = Servo(PWM('P0'))
        self.camera_servo_pin2 = Servo(PWM('P1'))
        self.dir_cali_value = int(self.config_flie.get("picarx_dir_servo", default_value=0))
        self.cam_cali_value_1 = int(self.config_flie.get("picarx_cam1_servo", default_value=0))
        self.cam_cali_value_2 = int(self.config_flie.get("picarx_cam2_servo", default_value=0))
        self.dir_servo_pin.angle(self.dir_cali_value)
        self.camera_servo_pin1.angle(self.cam_cali_value_1)
        self.camera_servo_pin2.angle(self.cam_cali_value_2)

        self.left_rear_pwm_pin = PWM("P13")
        self.right_rear_pwm_pin = PWM("P12")
        self.left_rear_dir_pin = Pin("D4")
        self.right_rear_dir_pin = Pin("D5")

        self.S0 = ADC('A0')
        self.S1 = ADC('A1')
        self.S2 = ADC('A2')

        self.motor_direction_pins = [self.left_rear_dir_pin, self.right_rear_dir_pin]
        self.motor_speed_pins = [self.left_rear_pwm_pin, self.right_rear_pwm_pin]
        self.motor_cali_value = self.config_flie.get("picarx_dir_motor", default_value="[1,1]")
        self.motor_cali_value = [int(i.strip()) for i in self.motor_cali_value.strip("[]").split(",")]
        self.cali_speed_value = [0, 0]
        self.dir_current_angle = 0
        # PWM pin init
        for pin in self.motor_speed_pins:
            pin.period(self.PERIOD)
            pin.prescaler(self.PRESCALER)

        # Calibration cache variables
        self.dir_cali_temp = self.dir_cali_value
        self.cam_cali_temp_1 = self.cam_cali_value_1
        self.cam_cali_temp_2 = self.cam_cali_value_2
        self.motor_cali_temp = self.motor_cali_value

    def set_motor_speed(self,motor,speed):
        motor -= 1
        if speed >= 0:
            direction = 1 * self.motor_cali_value[motor]
        elif speed < 0:
            direction = -1 * self.motor_cali_value[motor]
        speed = abs(speed)
        if speed != 0:
            speed = int(speed /2 ) + 50
        speed = speed - self.cali_speed_value[motor]
        if direction < 0:
            self.motor_direction_pins[motor].high()
            self.motor_speed_pins[motor].pulse_width_percent(speed)
        else:
            self.motor_direction_pins[motor].low()
            self.motor_speed_pins[motor].pulse_width_percent(speed)

    def motor_speed_calibration(self,value):
        self.cali_speed_value = value
        if value < 0:
            self.cali_speed_value[0] = 0
            self.cali_speed_value[1] = abs(self.cali_speed_value)
        else:
            self.cali_speed_value[0] = abs(self.cali_speed_value)
            self.cali_speed_value[1] = 0

    def motor_direction_calibration(self,motor, value):
        # 0: positive direction
        # 1:negative direction
        # global motor_cali_value
        motor -= 1
        if value == 1:
            self.motor_cali_value[motor] = -1 * self.motor_cali_value[motor]
        self.config_flie.set("picarx_dir_motor", self.motor_cali_value)


    def dir_servo_angle_calibration(self,value):
        self.dir_cali_temp = value
        self.dir_servo_pin.angle(value)

    def camera_servo1_angle_calibration(self,value):
        self.cam_cali_temp_1 = value
        self.camera_servo_pin1.angle(value)

    def camera_servo2_angle_calibration(self,value):
        self.cam_cali_temp_2 = value
        self.camera_servo_pin2.angle(value)

    def save_calibration(self):
        self.config_flie.set("picarx_dir_motor", self.motor_cali_value)
        self.config_flie.set("picarx_dir_servo", self.dir_cali_temp)
        self.config_flie.set("picarx_cam1_servo", self.cam_cali_temp_1)
        self.config_flie.set("picarx_cam2_servo", self.cam_cali_temp_2)

    def set_dir_servo_angle(self,value):
        self.dir_current_angle = value
        angle_value  = value + self.dir_cali_value
        self.dir_servo_pin.angle(angle_value)

    def set_camera_servo1_angle(self,value):
        self.camera_servo_pin1.angle(-1*(value + -1*self.cam_cali_value_1))

    def set_camera_servo2_angle(self,value):
        self.camera_servo_pin2.angle(-1*(value + -1*self.cam_cali_value_2))

    def get_adc_value(self):
        adc_value_list = []
        adc_value_list.append(self.S0.read())
        adc_value_list.append(self.S1.read())
        adc_value_list.append(self.S2.read())
        return adc_value_list

    def set_power(self,speed):
        self.set_motor_speed(1, speed)
        self.set_motor_speed(2, speed) 

    def backward(self,speed):
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
                self.set_motor_speed(2, speed )
        else:
            self.set_motor_speed(1, -1*speed)
            self.set_motor_speed(2, speed)  

    def forward(self,speed):
        current_angle = self.dir_current_angle
        if current_angle != 0:
            abs_current_angle = abs(current_angle)
            if abs_current_angle > 40:
                abs_current_angle = 40
            power_scale = (100 - abs_current_angle) / 100.0 
            if (current_angle / abs_current_angle) > 0:
                self.set_motor_speed(1, speed)
                self.set_motor_speed(2, -1*speed * power_scale)
            else:
                self.set_motor_speed(1, speed * power_scale)
                self.set_motor_speed(2, -1*speed )
        else:
            self.set_motor_speed(1, speed)
            self.set_motor_speed(2, -1*speed)                  

    def stop(self):
        self.set_motor_speed(1, 0)
        self.set_motor_speed(2, 0)


    def Get_distance(self):
        timeout=0.01
        trig = Pin('D8')
        echo = Pin('D9')

        trig.low()
        time.sleep(0.01)
        trig.high()
        time.sleep(0.000015)
        trig.low()
        pulse_end = 0
        pulse_start = 0
        timeout_start = time.time()
        while echo.value()==0:
            pulse_start = time.time()
            if pulse_start - timeout_start > timeout:
                return -1
        while echo.value()==1:
            pulse_end = time.time()
            if pulse_end - timeout_start > timeout:
                return -2
        during = pulse_end - pulse_start
        cm = round(during * 340 / 2 * 100, 2)
        return cm


if __name__ == "__main__":
    px = Picarx()
    px.forward(50)
    time.sleep(1)
    px.stop()
