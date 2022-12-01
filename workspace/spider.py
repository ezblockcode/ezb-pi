from robot import Robot
import math
from ezblock import fileDB
import copy

class Spider(Robot):
    A = 48
    B = 78
    C = 33
    config_file='/opt/ezblock/.config'
    
    def __init__(self, pin_list):
        
        # self.current_coord = self.step_list['stand']
        # init_angles = [-40, 55, 0]*4
        # self.coord_temp = init_angles

        super().__init__(pin_list, group=3,init_angles=None)
        self.move_list = self.MoveList()
        self.move_list_add = {
            'my action': None
        }
        self.stand_position = 0
        self.direction = [
            1,1,-1,
            1,1,1,
            1,1,-1,
            1,1,1,
        ]

        # ------ record current coordinates ------
        self.current_coord = [[0]*3]*4
        self.coord_temp = [[0]*3]*4

        # ------ calibration related ------
        # angle_offset
        self.angle_offset = self.offset # Robot Class built-in

        # coord_offset
        self.db = fileDB(db=self.config_file)
        temp = self.db.get("spider_coord_offset", default_value=str([[0]*3]*4))
        temp = [ a.replace("[",'').replace("]",'').replace(" ",'').split(',') for a in temp.split('],')]
        temp = [[ float(x) for x in temp[i] ] for i in range(len(temp))]
        if len(temp) == 4:
            self.coord_offset = temp
        else:
            print('\033[35m Incorrect number of elements in offset list \033[0m')
            self.coord_offset = [[0]*3]*4

        # coord_offset_temp
        self.coord_offset_temp = copy.deepcopy(self.coord_offset) #Pay attention to the copying of two-dimensional arrays in python

        # Calibrated original coordinates
        self.cali_default_coord = [[60, 0, -30], [60, 0, -30], [60, 0, -30], [60, 0, -30]]

        self.cali_default_angle = []
        for coord in self.cali_default_coord: # each servo motion
            alpha, beta, gamma = self.coord2polar(coord)
            self.cali_default_angle += [beta, alpha, gamma]
        
    def coord2polar(self, coord):
        x,y,z = coord
        
        L = math.sqrt(x**2+y**2+z**2)
        if L == 0:
            L = 0.1
        if L < self.C:
            temp = self.C/L
            x = temp * x
            y = temp * y
            z = temp * z
        elif L > (self.A+self.B+self.C):
            temp = (self.A+self.B+self.C)/L
            x = temp * x
            y = temp * y
            z = temp * z

        self.coord_temp.append([x,y,z])

        w = math.sqrt(math.pow(x,2) + math.pow(y,2))
        v = w - self.C
        u = math.sqrt(math.pow(z,2) + math.pow(v,2))
        u = max(30, min(91.58, u))
        cos_angle1 = (self.B**2 + self.A**2 - u**2) / (2 * self.B * self.A)
        beta = math.acos(cos_angle1)

        angle1 = math.atan2(z, v)
        angle2 = math.acos((self.A**2 + u**2 - self.B**2)/(2*self.A*u))
        alpha = angle2 + angle1

        gamma = math.atan2(y, x)

        alpha = 90 - alpha / math.pi * 180
        beta = beta / math.pi * 180 - 90
        gamma = -(gamma / math.pi * 180 - 45)

        return round(alpha,4), round(beta,4), round(gamma,4)

    def polar2coord(self, angles):
        alpha, beta, gamma = angles

        L1 = math.sqrt(self.A**2+self.B**2-2*self.A*self.B*math.cos((90+alpha)/180*math.pi))
        angle = math.acos((self.A**2+L1**2-self.B**2)/(2*self.A*L1))*180/math.pi
        angle = 90 - beta - angle
        L = L1*math.cos(angle*math.pi/180) + self.C

        x = L*math.sin((45+gamma)*math.pi/180)
        y = L*math.cos((45+gamma)*math.pi/180)
        z = L1*math.sin(angle*math.pi/180)
    
        return [round(x,4),round(y,4),round(z,4)]

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
        temp = self.limit(-90,90,alpha)
        if temp != alpha:
            alpha = temp
            limit_flag = True
        ## beta
        temp = self.limit(-10,90,beta)
        if temp != beta:
            beta = temp
            limit_flag = True
        ## gamma
        temp = self.limit(-60,60,gamma)
        if temp != gamma:
            gamma = temp
            limit_flag = True
        # return
        return limit_flag,[alpha,beta,gamma]

    def do_action(self, motion_name, step=1, speed=50):
        try:
            for _ in range(step): # times
                self.move_list.stand_position = self.stand_position
                if motion_name in ["forward", "backward", "turn left", "turn right", "turn left angle", "turn right angle"]:
                    self.stand_position = self.stand_position + 1 & 1
                action = self.move_list[motion_name]
                for _step in action: # spyder motion
                    self.do_step(_step, speed=speed)
        except AttributeError:
            try:
                for _ in range(step):
                    action_add = self.move_list_add[motion_name]
                    for _step in action_add:
                        self.do_step(_step, speed=speed)
            except KeyError:
                print("No such action")

    def set_angle(self, angles_list,speed=50,israise=False):
        translate_list = []
        results = []
        for angles in angles_list:
            result, angles = self.limit_angle(angles)
            translate_list += angles
            results.append(result)
        if True in results:
            if israise == True:
                raise ValueError('\033[1;35mCoordinates out of controllable range.\033[0m')
            else:
                print('\033[1;35mCoordinates out of controllable range.\033[0m', end='\r', flush=True)
                coords = []
                # Calculate coordinates
                for i in range(4):
                    coords.append(self.polar2coord([translate_list[i*3],translate_list[i*3+1],translate_list[i*3+2]]))
                self.current_coord = list.copy(coords)
        else:
            self.current_coord = list.copy(self.coord_temp)

        self.servo_move(translate_list, speed)
        return list.copy(translate_list)


    def do_step(self, _step, speed=50,israise=False):
        step_temp = []
        if isinstance(_step,str):
            if _step in self.step_list.keys():
                step_temp  = list.copy(self.step_list[_step])
            else:
                print("The name of gait is not in the default gait dictionary")
        elif isinstance(_step,list):
            step_temp = _step
        else:
            print("The \"_step\" parameter is wrong.")
            return

        angles_temp = []
        self.coord_temp = [] # do not use list.clear()
        for coord in step_temp: # each servo motion
            alpha, beta, gamma = self.coord2polar(coord)
            angles_temp.append([beta, alpha, gamma])

        return list.copy(self.set_angle(angles_temp,speed,israise))

    
    def current_step_all_leg_angle(self):
        return list.copy(self.servo_positions)

    def add_action(self,action_name, action_list):
        self.move_list_add[action_name] = action_list
        
    def cali_helper_web(self, leg, pos, enter):
        step=0.2

        positive_list = [
            [1, -1, -1, 1, 1, -1],
            [1, -1, -1, 1, 1, -1],
            [1, -1, -1, 1, 1, -1],
            [1, -1, -1, 1, 1, -1],
        ]

        leg = leg - 1
        def adjust_coord(coord_index, positive_index):
            self.coord_offset_temp[leg][coord_index] += step * positive_list[leg][positive_index]
            if self.coord_offset_temp[leg][coord_index] > 20:
                self.coord_offset_temp[leg][coord_index] = 20
            elif self.coord_offset_temp[leg][coord_index] < -20:
                self.coord_offset_temp[leg][coord_index] = -20
            self.current_coord[leg][coord_index] = self.cali_default_coord[leg][coord_index] - self.coord_offset[leg][coord_index] + self.coord_offset_temp[leg][coord_index]

        if pos == 'up':
            adjust_coord(1, 0)
        elif pos == 'down':
            adjust_coord(1, 1)
        elif pos == 'left':
            adjust_coord(0, 2)
        elif pos == 'right':
            adjust_coord(0, 3)
        elif pos == 'high':
            adjust_coord(2, 4)
        elif pos == 'low':
            adjust_coord(2, 5)
        
        for coord in self.current_coord:
            coord[0] = max(40, min(80, coord[0]))
            coord[1] = max(-20, min(20, coord[1]))
            coord[2] = max(-50, min(-10, coord[2]))

        self.do_step(self.current_coord, speed=100)

        if enter == 1:
            self.angle_offset = self.offset
            current_angle = self.servo_positions

            # offset[leg*3:(leg + 1)*3] = tmp[leg*3:(leg + 1)*3]
            tmp = [current_angle[i] - self.cali_default_angle[i] + self.angle_offset[i] for i in range(12)]
            self.angle_offset = list.copy(tmp)
            self.set_offset(self.angle_offset)

            self.coord_offset = copy.deepcopy(self.coord_offset_temp)
            self.db.set("spider_coord_offset", self.coord_offset_temp)
            print("set_angle_offset: %s"%self.angle_offset)
            print("set_coord_offset: %s"%self.coord_offset_temp)
            self.do_step(self.cali_default_coord, speed=100)

    class MoveList(dict):
        
        LENGTH_SIDE = 77
        X_DEFAULT = 45
        X_TURN = 70
        X_START = 0
        Y_DEFAULT = 45
        Y_TURN = 130
        Y_WAVE =120
        Y_START = 0
        Z_DEFAULT = -50
        Z_UP = -30
        Z_WAVE = 60
        Z_TURN = -40
        Z_PUSH = -76
         
        # temp length
        TEMP_A = math.sqrt(pow(2 * X_DEFAULT + LENGTH_SIDE, 2) + pow(Y_DEFAULT, 2))
        TEMP_B = 2 * (Y_START + Y_DEFAULT) + LENGTH_SIDE
        TEMP_C = math.sqrt(pow(2 * X_DEFAULT + LENGTH_SIDE, 2) + pow(2 * Y_START + Y_DEFAULT + LENGTH_SIDE, 2))
        TEMP_ALPHA = math.acos((pow(TEMP_A, 2) + pow(TEMP_B, 2) - pow(TEMP_C, 2)) / 2 / TEMP_A / TEMP_B)
        # site for turn
        TURN_X1 = (TEMP_A - LENGTH_SIDE) / 2
        TURN_Y1 = Y_START + Y_DEFAULT / 2
        TURN_X0 = TURN_X1 - TEMP_B * math.cos(TEMP_ALPHA)
        TURN_Y0 = TEMP_B * math.sin(TEMP_ALPHA) - TURN_Y1 - LENGTH_SIDE

        def __init__(self, *args, **kwargs):
            dict.__init__(self, *args, **kwargs)
            self.z_current = self.Z_UP
            self.stand_position = 0
            self.recovery_step = []
            self.ready_state = 0
            self.angle = 30
   

        def __getitem__(self, item):
            return eval("self.%s"%item.replace(" ", "_"))
        
        def turn_angle_coord(self, angle):
            a = math.atan(self.Y_DEFAULT/(self.X_DEFAULT+self.LENGTH_SIDE/2))
            angle1 = a/math.pi*180
            r1 = math.sqrt(pow(self.Y_DEFAULT,2)+ pow(self.X_DEFAULT+ self.LENGTH_SIDE/2, 2))
            x1 = r1* math.cos((angle1-angle)* math.pi/180)- self.LENGTH_SIDE/2
            y1 = r1* math.sin((angle1-angle)* math.pi/180)
            
            x2 = (self.X_DEFAULT+ self.LENGTH_SIDE/2)* math.cos(angle*math.pi/180)- self.LENGTH_SIDE/2
            y2 = (self.X_DEFAULT+ self.LENGTH_SIDE/2)* math.sin(angle*math.pi/180)
            
            b = math.atan((self.X_DEFAULT+self.LENGTH_SIDE/2)/(self.Y_DEFAULT+ self.LENGTH_SIDE))
            angle2 = b/math.pi*180
            r2 = math.sqrt(pow(self.X_DEFAULT+ self.LENGTH_SIDE/2, 2)+ pow(self.Y_DEFAULT+ self.LENGTH_SIDE,2))
            x3 = r2*math.sin((angle2-angle)* math.pi/180) - self.LENGTH_SIDE/2
            y3 = r2*math.cos((angle2-angle)*math.pi/180)- self.LENGTH_SIDE

            x3 += 10
            return [x1,y1,x2,y2,x3,y3]
        
        # 装饰器封装函数,判断是否站立
        def check_stand(func):
            def wrapper(self):
                _action = []
                if not self.is_stand():
                    _action += self.stand
                _action += func(self)
                return _action
            return wrapper
        
        # 装饰器封装函数，装饰器简化步态的0，1两种状态转化，状态0为2，3脚y轴为0，状态1为1，4脚y轴为0 mode为2种转化方式，mode0为1，2交换3，4交换，mode1为1，3交换2，4交换
        def normal_action(mode):
            def wrapper1(func):
                def wrapper2(self):
                    _action = []
                    if self.stand_position == 0:
                        _action += func(self)
                    else:
                        temp = func(self)
                        new_step = []
                        for step in temp:
                            if mode == 0:
                                new_step = [step[1], step[0], step[3], step[2]]
                            elif mode == 1:
                                new_step = [step[2], step[3], step[0], step[1]]
                            _action += [new_step]
                    return _action
                return wrapper2
            return wrapper1
        
        @property
        @normal_action(0)
        def sit(self):
            self.z_current = self.Z_UP
            return [[
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
                [self.X_TURN,self.Y_START,self.z_current],
                [self.X_TURN,self.Y_START,self.z_current],
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
            ]]
            

        @property
        @normal_action(0)
        def stand(self):
            _stand = []
            if self.ready_state ==  0:
                _stand += self.ready
            self.z_current = self.Z_DEFAULT
            _stand += [[
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
                [self.X_DEFAULT,self.Y_START,self.z_current],
                [self.X_DEFAULT,self.Y_START,self.z_current],
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
            ]]
            return _stand
           
        
        @property
        def ready(self):
            _ready = [[
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
                [self.X_TURN,self.Y_START,self.z_current],
                [self.X_TURN,self.Y_START,self.z_current],
                [self.X_DEFAULT,self.Y_DEFAULT,self.z_current],
            ]]
            self.ready_state = 1
            return _ready
          

        def is_sit(self):
            return self.z_current == self.Z_UP
            
        def is_stand(self):
            tmp = self.z_current == self.Z_DEFAULT
            return tmp
        
        @property
        @check_stand
        @normal_action(0)
        def forward(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2,self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2, self.z_current]],
                
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2, self.Z_UP]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START, self.Z_UP]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
            ]
        
        @property
        @check_stand
        @normal_action(0)
        def backward(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT*2, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT*2, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT*2, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
                [[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT,self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
            ]
        
       
        @property
        @check_stand
        @normal_action(1)
        def turn_left(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X0, self.TURN_Y0, self.Z_UP],[self.TURN_X0, self.TURN_Y0, self.z_current]],
                [[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X0, self.TURN_Y0, self.z_current]],
                
                [[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X0, self.TURN_Y0, self.Z_UP]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START, self.Z_UP]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
            ]

        @property
        @check_stand
        @normal_action(1)
        def turn_right(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X0, self.TURN_Y0, self.Z_UP],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_X1, self.z_current]],
                [[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_X1, self.z_current]],
                [[self.TURN_X0, self.TURN_Y0, self.Z_UP],[self.TURN_X0, self.TURN_Y0, self.z_current],[self.TURN_X1, self.TURN_Y1, self.z_current],[self.TURN_X1, self.TURN_X1, self.z_current]],
                [[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
                [[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]],
                
            ]
        
        @property
        def push_up(self):
            _push_up = []
            if not self.is_sit():
                _push_up += self.sit
            _push_up += [
                [[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_TURN, self.Y_START, self.Z_PUSH],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
                [[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_TURN, self.Y_START, self.Z_TURN],[self.X_START, self.Y_TURN, self.Z_TURN],[self.X_START, self.Y_TURN,self.Z_TURN]],
            ]
            if self.stand_position == 0:
                _push_up.append([[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.z_current],[self.X_TURN, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]])
            else:
                _push_up.append([[self.X_TURN, self.Y_START,self.z_current], [self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START, self.z_current]])
            return _push_up
        
        @property
        @check_stand
        @normal_action(0)
        def wave(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_WAVE],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_START, self.Y_WAVE,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            ]
        
        @property
        @check_stand
        @normal_action(1)
        def look_left(self):
            li = self.turn_angle_coord(self.angle)
            temp_x1 = li[0:2]
            temp_x1.append(self.z_current)
            temp_x2 = li[2:4]
            temp_x2.append(self.z_current)
            temp_x3 = li[4:6]
            temp_x3.append(self.z_current)
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [temp_x1, temp_x2,[self.X_TURN, self.Y_START, self.Z_UP],temp_x3]
            ]
            
        @property
        @check_stand
        @normal_action(1)
        def look_right(self):
            li = self.turn_angle_coord(self.angle)
            temp_x1 = li[0:2]
            temp_x1.append(self.z_current)
            temp_x2 = li[2:4]
            temp_x2.append(self.z_current)
            temp_x3 = li[4:6]
            temp_x3.append(self.z_current)
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [temp_x3, [self.X_TURN, self.Y_START, self.Z_UP], temp_x2, temp_x1]
            ]
        
        @property
        @check_stand
        @normal_action(1)
        def turn_left_angle(self):
            li = self.turn_angle_coord(self.angle)
            temp_x1 = li[0]
            temp_y1 = li[1]
            temp_x2 = li[2]
            temp_y2 = li[3]
            temp_x3 = li[4]
            temp_y3 = li[5]
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START,self.z_current],[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[temp_x1, temp_y1, self.z_current], [temp_x2, temp_y2, self.z_current],[self.X_TURN, self.Y_START, self.Z_UP],[temp_x3, temp_y3, self.z_current]],
                [[temp_x1, temp_y1, self.z_current], [temp_x2, temp_y2, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[temp_x3, temp_y3, self.z_current]],
                [[temp_x1, temp_y1, self.z_current], [temp_x2, temp_y2, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[temp_x3, temp_y3, self.Z_UP]],
                [[temp_x1, temp_y1, self.z_current], [temp_x2, temp_y2, self.z_current],[self.X_TURN, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START, self.Z_UP]],
                [[temp_x1, temp_y1, self.z_current], [temp_x2, temp_y2, self.z_current],[self.X_TURN, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_START, self.z_current]]
            ]
            
        @property
        @check_stand
        @normal_action(1)
        def turn_right_angle(self):
            li = self.turn_angle_coord(self.angle)
            temp_x1 = li[0]
            temp_y1 = li[1]
            temp_x2 = li[2]
            temp_y2 = li[3]
            temp_x3 = li[4]
            temp_y3 = li[5]
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
                [[temp_x3,temp_y3, self.z_current], [self.X_TURN, self.Y_START, self.Z_UP], [temp_x2, temp_y2, self.z_current], [temp_x1, temp_y1, self.z_current]],
                [[temp_x3,temp_y3, self.z_current], [self.X_DEFAULT, self.Y_DEFAULT, self.z_current], [temp_x2, temp_y2, self.z_current], [temp_x1, temp_y1, self.z_current]],
                [[temp_x3,temp_y3, self.Z_UP], [self.X_DEFAULT, self.Y_DEFAULT, self.z_current], [temp_x2, temp_y2, self.z_current], [temp_x1, temp_y1, self.z_current]],
                [[self.X_TURN, self.Y_START, self.Z_UP], [self.X_DEFAULT, self.Y_DEFAULT, self.z_current], [temp_x2, temp_y2, self.z_current], [temp_x1, temp_y1, self.z_current]],
                [[self.X_DEFAULT, self.Y_START, self.z_current], [self.X_DEFAULT, self.Y_DEFAULT, self.z_current], [temp_x2, temp_y2, self.z_current], [temp_x1, temp_y1, self.z_current]],
            ]
            
        
        @property
        @check_stand
        @normal_action(0)
        def look_up(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.Z_DEFAULT],[self.X_DEFAULT, self.Y_START,self.Z_DEFAULT],[self.X_TURN, self.Y_START, self.Z_UP],[self.X_DEFAULT, self.Y_DEFAULT, self.Z_UP]],
            ]
            
        @property
        @check_stand
        @normal_action(0)
        def look_down(self):
            return [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.Z_UP],[self.X_TURN, self.Y_START,self.Z_UP],[self.X_DEFAULT, self.Y_START, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            ]
        
        def rotate_body_absolute_x(self, degree_x):
            degree_x = degree_x * math.pi / 180
            dz = (self.LENGTH_SIDE / 2 + self.Y_DEFAULT) * math.sin(degree_x)
            dy = (self.LENGTH_SIDE / 2 + self.Y_DEFAULT) * (1 - math.cos(degree_x))
            return [[self.X_DEFAULT, self.Y_DEFAULT - dy, self.Z_DEFAULT + dz],[self.X_DEFAULT, self.Y_DEFAULT - dy, self.Z_DEFAULT - dz],[self.X_DEFAULT, self.Y_DEFAULT - dy, self.Z_DEFAULT - dz],[self.X_DEFAULT, self.Y_DEFAULT - dy, self.Z_DEFAULT + dz]]
        
        
        def rotate_body_absolute_y(self, degree_y):
            degree_y = degree_y * math.pi / 180
            dz = (self.LENGTH_SIDE / 2 + self.X_DEFAULT) * math.sin(degree_y)
            dx = (self.LENGTH_SIDE / 2 + self.X_DEFAULT) * (1 - math.cos(degree_y))
            return [[self.X_DEFAULT- dx, self.Y_DEFAULT, self.Z_DEFAULT + dz], [self.X_DEFAULT- dx, self.Y_DEFAULT, self.Z_DEFAULT + dz],[self.X_DEFAULT- dx, self.Y_DEFAULT, self.Z_DEFAULT - dz],[self.X_DEFAULT- dx, self.Y_DEFAULT, self.Z_DEFAULT - dz]]
        
        
        def  move_body_absolute(self, x, y, z):
            return [[self.X_DEFAULT - x,self.Y_DEFAULT - y,self.Z_TURN - z],[self.X_DEFAULT + x,self.Y_DEFAULT - y,self.Z_TURN - z],[self.X_DEFAULT + x,self.Y_DEFAULT + y,self.Z_TURN - z],[self.X_DEFAULT - x,self.Y_DEFAULT + y,self.Z_TURN - z]]
        
        
        def to_rad(self, deg):
            return deg * math.pi / 180
        
        @property
        def twist(self):
            _dance = []
            if not self.is_sit():
                _dance += self.sit
            _dance += [
                [[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current],[self.X_DEFAULT, self.Y_DEFAULT, self.z_current]],
            ]
            for i in range(0, 360, 5):
                _dance.append(self.move_body_absolute(40 * math.sin(self.to_rad(i)), 40 * math.cos(self.to_rad(i)), 0))
            for i in range(360, 0, -5):
                _dance.append(self.move_body_absolute(40 * math.sin(self.to_rad(i)), 40 * math.cos(self.to_rad(i)), 0))
            _dance.append(self.rotate_body_absolute_x(-20))
            _dance.append(self.rotate_body_absolute_x(20))
            _dance.append(self.move_body_absolute(0, 0, 0))
            _dance.append(self.rotate_body_absolute_y(-20))
            _dance.append(self.rotate_body_absolute_y(20))
            for j in range(0, 3):
                for i in range(0, 360, 3):
                    _dance.append(self.move_body_absolute(40 * math.sin(self.to_rad(i)), 40 * math.cos(self.to_rad(i)), (i / 360.0 + j) * 15))
            for j in range(3, 0, -1):
                for i in range(0, 360, 3):
                    _dance.append(self.move_body_absolute(40 * math.sin(self.to_rad(i)), 40 * math.cos(self.to_rad(i)), ((360 - i) / 360.0 + j - 1) * 15))
            _dance.append(self.move_body_absolute(0, 0, 0))
            return _dance


    step_list = {

        "stand":[
            [45, 45, -50],
            [45, 45, -50],
            [45, 45, -50],
            [45, 45, -50]
        ],
        "sit":[
            [45, 45, -30],
            [45, 45, -30],
            [45, 45, -30],
            [45, 45, -30]
        ],
              
    }


    def do_single_leg(self,leg,coodinate=[50,50,-33],speed=50):
        leg_num = 0
        if isinstance(leg,str):
            if leg == 'left_front':
                leg_num = 1
            elif leg == 'right_front':
                leg_num = 0
            elif leg == 'left_rear':
                leg_num = 2
            elif leg == 'right_rear':
                leg_num = 3
            else:
                print('no this leg')
                return
        elif isinstance(leg,int):
            leg_num = leg
        else:
            print('parameter type error')
            return

        target_coord = self.current_step_all_leg_value()
        target_coord[leg_num] = coodinate
        self.do_step(target_coord,speed)
 

    def current_step_leg_value(self,leg):
        leg_num = 0
        if isinstance(leg,str):
            if leg == 'left_front':
                leg_num = 1
            if leg == 'right_front':
                leg_num = 0
            if leg == 'left_rear':
                leg_num = 2
            if leg == 'right_rear':
                leg_num = 3
        elif isinstance(leg,int):
            leg_num = leg
        return self.current_coord[leg_num]


    def current_step_all_leg_value(self):
        return list(self.current_coord)


    def mix_step(self,basic_step,leg,coodinate=[50,50,-33]):
        # Pay attention to adding list(), otherwise the address pointer is returned
        new_step = list(basic_step)
        new_step[leg] = coodinate
        return list(new_step)

