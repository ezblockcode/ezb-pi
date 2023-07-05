import math
from re import L
from robot import Robot
from ezblock import Servo,PWM
import time
from os import path
import json
import math
from ezblock.utils import log, run_command
import time
from os import path
import json
import math

def debug_2_app(msg):
    from ezblock.websockets import Ezb_Service
    Ezb_Service.set_share_val('debug', [str(msg), True])


class Arm(Robot):
    A = 80
    B = 80
    
    def __init__(self, pin_list,steps_path='/opt/ezblock/steps_record.json'):
        super().__init__(pin_list, group=3)
        # define variables
        self.component = 'none'
        self.speed = 50
        self.current_coord = [0, 80, 80]
        self.coord_temp = [0,0,0]
        self.component_staus = 0
        # checking steps record file
        self.path = steps_path
        self.steps_buff = []
        self.record_data = []
        self.data_index = 0
        self.record_init(self.path)
        
    def record_init(self,_path):
        if not path.exists(_path):
            log('Steps record file does not exist.Create now...')
            try:
                run_command('sudo mkdir -p '+_path.rsplit('/',1)[0])
                run_command('sudo touch '+_path)
                run_command('sudo chmod a+rw '+_path)

                self.record_data.append({'component':'none','values':None})
                self.record_data.append({'component':'bucket','values':None})
                self.record_data.append({'component':'hanging_clip','values':None})
                self.record_data.append({'component':'electromagnet','values':None})
                with open(_path,'w')as f:
                    json.dump(self.record_data,f)
                    time.sleep(0.1)
                    f.close()
            except Exception as e:
                raise(e)

        self.record_buff_clear()
        try:
            with open(_path,'r')as f:
                self.record_data = json.load(f)
                time.sleep(0.1)
                f.close()
        except Exception as e:
            raise(e)

    def set_speed(self, speed):
        self.speed = speed
    
    def bucket_init(self, pin):
        self.bucket = Servo(pin)
        self.bucket_angle = 0
        self.component = 'bucket'
        self.data_index = 1

    def hanging_clip_init(self, pin):
        self.hanging_clip = Servo(pin)
        self.hanging_clip_angle = 0
        self.component = 'hanging_clip'
        self.data_index = 2

    def electromagnet_init(self, pin):
        self.elecma = pin
        self.elecma.pulse_width_percent(0)
        self.component = 'electromagnet'
        self.data_index = 3

    def set_angle(self, angles,israise=False):
        result,angles = self.limit_angle(angles)
        if result == True:
            if israise == True:
                raise ValueError('Coordinates out of controllable range.')
            else:
                print('\033[1;35mCoordinates out of controllable range.\033[0m', end='\r', flush=True)
                # Calculate coordinates
                coord = self.polar2coord(angles)
                self.current_coord = coord
        else:
            self.current_coord = self.coord_temp

        self.servo_move(angles, self.speed)
        
    def coord2polar(self, coord):
        x, y, z = coord
        y = max(0,y)
        u = math.sqrt(math.pow(z,2) + math.pow(y,2) + math.pow(x,2))
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
        self.coord_temp = [x,y,z]

        angle1 = math.acos((self.A**2 + u**2 - self.B**2) / (2 * self.A * u))
        angle2 = math.asin(z / u)
        angle3 = math.acos((self.A**2 + self.B**2 - u**2) / (2 * self.A * self.B))
        angle4 = math.atan2(x, y)
        alpha = 90 - (angle1 + angle2) / math.pi * 180
        beta = -180 + (angle1 + angle2 + angle3) / math.pi * 180
        gamma = - angle4 / math.pi * 180

        # alpha = round(alpha,2)
        # beta = round(beta,2)
        # gamma = round(gamma,2)
                    
        return [alpha, beta, gamma]

    def polar2coord(self, angles):
        alpha, beta, gamma = angles

        a1 = 90 + alpha + beta
        a2 = (180 - a1)/2
        a3 = 90-alpha-a2
        # a^2 = sqrt(b^2 + C^2 - 2bc*cosA)   ,  A = 90 + alpha + beta
        L = math.sqrt((self.A**2 + self.B**2 - 2 * self.A * self.B*math.cos(a1/180*math.pi)))
        L2 = L*math.cos(a3/180*math.pi)

        x = L2*math.sin(-gamma/180*math.pi)
        if gamma < 0:
            y = L2*math.cos(-gamma/180*math.pi)
        elif gamma >= 0:
            y = L2*math.cos(gamma/180*math.pi)
        z = L*math.sin(a3/180*math.pi)

        return [round(x),round(y),round(z)]

    def limit(self,min,max,x):
        if x > max:
            return max
        elif x < min:
            return min
        else:
            return x

    def limit_angle(self,angles):
        alpha, beta, gamma = angles
        # limit
        limit_flag = False
        ## alpha
        temp = self.limit(-30,60,alpha)
        if temp != alpha:
            alpha = temp
            limit_flag = True
        ## beta
        else:
            # relative to alpha: (-alpha - 90 + 30),(-alpha - 90 + 120)  ,
            # 30 and 120 are the minimum and maximum angles of the quadrilateral structure
            temp = self.limit((-alpha-60),(-alpha+30),beta)
            if temp != beta:
                beta = temp
                limit_flag = True
            else:
                # relative to own structure:
                temp = self.limit(-90,40,beta)
                if temp != beta:
                    beta = temp
                    limit_flag = True
        ## gamma
        temp = self.limit(-90,90,gamma)
        if temp != gamma:
            gamma = temp
            limit_flag = True
        # return
        return limit_flag,[alpha,beta,gamma]

    def do_by_coord(self, coord,israise=False):
        temp = self.coord2polar(coord)
        self.set_angle(temp)
    
    def set_bucket(self, angle):
        angle = self.limit(-50,90,angle)
        self.bucket.angle(angle)
        self.component_staus = angle
    
    def set_hanging_clip(self, angle):
        # angle = self.limit(-50,90,angle)
        self.hanging_clip.angle(angle)
        self.component_staus = angle
    
    def set_electromagnet(self, status):
        if status == "on":
            self.elecma.pulse_width_percent(100)
        else:
            self.elecma.pulse_width_percent(0)
        self.component_staus = status

# Related to 'steps record'
    def record_buff_clear(self):
        self.steps_buff.clear()

    def record(self):
        self.steps_buff.append(list(self.servo_positions)) # list() is necessary
        self.steps_buff.append(self.component_staus)

        msg = {
            'component':self.component,
            'steps':self.steps_buff,
        }
        self.record_data[self.data_index] = msg
 
        try:
            with open(self.path,'w')as f:
                json.dump(self.record_data,f)
                time.sleep(0.1)
                f.close()
        except Exception as e:
            log(e)

    def record_reproduce(self,delay=0.01):
        _data = []
        # read data
        try:
            with open(self.path,'r')as f:
                _data = json.load(f)
                time.sleep(0.1)
                f.close()
        except Exception as e:
            log(e)

        _data = dict(_data[self.data_index])
        if _data['component'] != self.component:
            log('Component mismatch.This record corresponds to the %s component.' %_data[self.data_index]['component'])
        else:
            if 'steps' in  _data.keys() and len(_data['steps']) > 0:
                steps = _data['steps']
                for i in range(0,len(steps),2):
                    angles = steps[i]
                    status = steps[i+1]
                    log('step %s: %s,%s '%(int(i/2),angles,status))
                    self.set_angle(angles)
                    if self.component == 'bucket':
                        self.set_bucket(status)
                    if self.component == 'hanging_clip':
                        self.set_hanging_clip(status)
                    if self.component == 'electromagnet':
                        self.set_electromagnet(status)
                    time.sleep(delay)
            else:
                debug_2_app('steps is null')
                log('steps is null')


if __name__ == "__main__":
    arm = Arm([1,2,3])
    arm.set_offset([0,0,0])
    
    
            
                
            
    
    
        

