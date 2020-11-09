import math
from robot import Robot
from ezblock import Servo
import time

class Arm(Robot):
    A = 80
    B = 80
    
    def __init__(self, pin_list):
        super().__init__(pin_list, group=3)
        self.speed = 50
        
    
    def set_speed(self, speed):
        self.speed = speed 
    
    def bucket_init(self, pin):
        self.bucket = Servo(pin)

    def hanging_clip_init(self, pin):
        self.hanging_clip = Servo(pin)
    
    def electromagnet_init(self, pin):
        self.elecma = pin
    
    def set_angle(self, angle):
        self.servo_move(angle, self.speed)
    
    def coord2polar(self, coord):
        x, y, z = coord
        y = max(0,y)
        u = math.sqrt(math.pow(z,2) + math.pow(y,2) + math.pow(x,2))
        # print(u)
        if u == 0:
            u = 0.1
        #u = min(160, u)
        if u > 160:  # 坐标超出范围，等比换算成最大球面位置
            temp = 160 / u
            x = temp * x
            y = temp * y
            z = temp * z
            u = 160
        if u < 30:  # 坐标超出范围，等比换算成最大球面位置
            temp = 30 / u
            x = temp * x
            y = temp * y
            z = temp * z
            u = 30
        angle1 = math.acos((self.A**2 + u**2 - self.B**2) / (2 * self.A * u))
        angle2 = math.asin(z / u)
        angle3 = math.acos((self.A**2 + self.B**2 - u**2) / (2 * self.A * self.B))
        angle4 = math.atan2(x, y)
        alpha = 90 - (angle1 + angle2) / math.pi * 180
        beta = -180 + (angle1 + angle2 + angle3) / math.pi * 180
        gamma = - angle4 / math.pi * 180
        # print(alpha, beta, gamma)
        # self.set_angle([alpha, beta, gamma], speed)
        return [alpha, beta, gamma]
    
    def do_by_coord(self, coord):
        temp = self.coord2polar(coord)
        # self.set_speed(speed)
        self.set_angle(temp)
    
    def set_bucket(self, angle):
        self.bucket.angle(angle)
    
    def set_hanging_clip(self, angle):
        self.hanging_clip.angle(angle)
    
    def set_electromagnet(self, status):
        if status == "on":
            self.elecma.pulse_width_percent(100)
        else:
            self.elecma.pulse_width_percent(0)


if __name__ == "__main__":
    arm = Arm([1,2,3])
    arm.set_offset([0,0,0])
    
    
            
                
            
    
    
        

