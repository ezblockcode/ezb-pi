from robot import Robot



def mapping(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min



class Sloth(Robot):
  move_list = {
    "forward":[
      [0, 40, 0, 15],
      [-30, 40, -30, 15],
      [-30, 0, -30, 0],

      [0, -15, 0, -40],
      [30, -15, 30, -40],
      [30, 0, 30, 0],
      ],

    "turn right":[
      [0, -20, 0, -40],
      [-20, -20, 0, -40],
      [-20, 0, 0, 0],

      [0, 40, 0, 20],
      [20, 40, 0, 20],
      [20, 0, 0, 0],
      ],

    "turn left":[
      [0, 40, 0, 20],
      [0, 40, 20, 20],
      [0, 0, 20, 0],

      [0, -20, 0, -40],
      [0, -20, -20, -40],
      [0, 0, -20, 0],
      ],
    "backward":[
      [0, 40, 0, 15],
      [30, 40, 30, 15],
      [30, 0, 30, 0],

      [0, -15, 0, -40],
      [-30, -15, -30, -40],
      [-30, 0, -30, 0],
      ],

    "stop":[
      [0,0,0,0],
      ],

    "moon walk left": [
      [0, 0, 0, -30],
      [0, 30, 0, -60],
      [0, 60, 0, -30],
      [0, 30, 0, 0],
      [0, 0, 0, 0]
    ],
    "moon walk right": [
      [0, 30, 0, 0],
      [0, 60, 0, -30],
      [0, 30, 0, -60],
      [0, 0, 0, -30],
      [0, 0, 0, 0]
    ],

    "shake left": [
      [-40, 70, -40, 30],
      [-40, 30, -40, 30],

      [-10, 30, -40, 30],
      [-40, 30, -40, 30],
      [-10, 30, -40, 30],
      [-40, 30, -40, 30],

      [-40, 70, -40, 30],
      [0, 0, 0, 0],
    ],

    "shake right": [
      [40, -30, 40, -70],
      [40, -30, 40, -30],

      [40, -30, 10, -30],
      [40, -30, 40, -30],
      [40, -30, 10, -30],
      [40, -30, 40, -30],

      [40, -30, 40, -70],
      [0, 0, 0, 0],
    ],

    "go up and down": [
      [0, 50, 0, -50],
      [0, 0, 0, 0],
    ],

    "swing": [
      [0, -40, 0, 40],
      [0, 0, 0, 0],
    ],

    "walk boldly": [
      [-15, -15, 15, -40],
      [10, -30, 40, -40],
      [10, 0, 40, 0],

      [-15, 40, 15, 15],
      [-40, 40, -10, 30],
      [-40, 0, -10, 0],
    ],

    "walk backward boldly": [
      [-15, -15, 15, -40],
      [-40, -30, -10, -40],
      [-40, 0, -10, 0],

      [-15, 40, 15, 15],
      [10, 40, 40, 30],
      [10, 0, 40, 0],
    ],

    "walk shyly": [
      [10, -15, -10, -40],
      [25, -30, -5, -40],
      [25, 0, -5, 0],

      [10, 40, -10, 15],
      [5, 40, -25, 30],
      [5, 0, -25, 0],
    ],

    "walk backward shyly": [
      [10, -15, -10, -40],
      [5, -30, -25, -40],
      [5, 0, -25, 0],

      [10, 40, -10, 15],
      [25, 40, -5, 30],
      [25, 0, -5, 0],
    ],

    "big swing": [
      [0, -90, 0, 90],
      [0, 0, 0, 0],
    ],

  }




  def do_action(self,motion_name, step=1, speed=50):
    speed = mapping(speed, 0, 100, 0, 80)
    for _ in range(step):
        for motion in self.move_list[motion_name]:
            self.servo_move(motion, speed)

  def add_action(self,action_name,action_list):
    if action_name not in self.move_list.keys():
      self.move_list[action_name] = action_list

if __name__=="__main__":
	a = Sloth([1,2,3,4])
	while 1:
		for i in a.move_list:
			a.do_action(i,step=2,speed=100)
	# a.do_action("turn right",step=2,speed=100)
#   new_list_test = [
#       [0, -90, 0, 90],
#       [0, 0, 0, 0]
#     ]
#   a.add_action("test",new_list_test)
#   while 1:
#       a.do_action("test",speed=100)