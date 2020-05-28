import numpy as np
import cv2
import threading

from importlib import import_module
import os
from flask import Flask, render_template, Response
from multiprocessing import Process, Manager
import time
# from utils import cpu_temperature
# import imutils
# from rgb_matrix import RGB_Matrix
import tensorflow as tf 
from pyzbar import pyzbar



traffic_num_list = [i for i in range(4)]
ges_num_list = [i for i in range(3)]
# ges_list = [chr(i) for i in range(97,101)]
# ges_list.remove('j')

traffic_list = ['stop','right','left','ahead']
gesture_list = ["five","two","zero"]

traffic_dict = dict(zip(traffic_num_list,traffic_list))
ges_dict = dict(zip(ges_num_list,gesture_list))


# test_image_dir = './ges_pic/'
traffic_sign_model_path = "/opt/ezblock/tf_150_dr0.2.tflite"
gesture_model_path = "/opt/ezblock/3bak_ges_200_dr0.2.tflite"
# gesture_model_path = "/opt/ezblock/mb1_gesture_200_dr0.2.tflite"



interpreter_1 = tf.lite.Interpreter(model_path=traffic_sign_model_path)
interpreter_1.allocate_tensors()

interpreter_2 = tf.lite.Interpreter(model_path=gesture_model_path)
interpreter_2.allocate_tensors()

# Get input and output tensors.
input_details_1 = interpreter_1.get_input_details()
# print(str(input_details_1))
output_details_1 = interpreter_1.get_output_details()
# print(str(output_details_1))


# Get input and output tensors.
input_details_2 = interpreter_2.get_input_details()
# print(str(input_details_2))
output_details_2 = interpreter_2.get_output_details()
# print(str(output_details_2))


app = Flask(__name__)
@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen():
    """Video streaming generator function."""
    while True:  
        # frame = cv2.imread("123.jpeg")Vilib.q.get()  
        # print("1")
        # if Vilib.conn2.recv()
        # frame = cv2.imencode('.jpg', Vilib.conn2.recv())[1].tobytes() 
        # rt_img = np.ones((320,240),np.uint8)
        # print("2")

        frame = cv2.imencode('.jpg', Vilib.img_array[0])[1].tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        

@app.route('/mjpg')
def video_feed():
    # from camera import Camera
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame') 

def web_camera_start():
    app.run(host='0.0.0.0', port=9000,threaded=True)



class Vilib(object): 
    

    video_flag = False
    # video_path = './video_file/tst.avi'


    # picture_path = './picture_file'
    # video_recorder = cv2.VideoWriter(video_path, fourcc, 20.0, (320, 240))


    face_cascade = cv2.CascadeClassifier('/opt/ezblock/haarcascade_frontalface_default.xml') 
    kernel_5 = np.ones((5,5),np.uint8)#4x4的卷积核
    # color_default = 'blue'
    # color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[166,180]}
    # lower_color = np.array([min(color_dict[detect_obj_parameter['color_default']]), 60, 60])  
    # upper_color = np.array([max(color_dict[detect_obj_parameter['color_default']]), 255, 255])
    # hdf_flag = False 
    # cdf_flag = False
    # stf_flag = False
    video_source = 0
    roi = cv2.imread("/opt/ezblock/cali.jpg")
    roi_hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    obj_roi = cv2.imread("/opt/ezblock/object.jpg")
    h,w = obj_roi.shape[:2]

    obj_hsv = cv2.cvtColor(obj_roi, cv2.COLOR_BGR2HSV)

    track_window = (0, 0, w, h)

    roi_hist = cv2.calcHist([obj_hsv],[0,1],None,[180,256],[0,180,0,256]) #计算直方图
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)

    
    # human_object_counter = 0
    # detect_obj_parameter = np.array([0,0])
    # human_object_size = np.array([0,0]) 

    # color_object_counter = 0
    detect_obj_parameter = Manager().dict()
    img_array = Manager().list(range(2))
#Color_obj_parameter
    detect_obj_parameter['color_default'] = 'red'

    color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[166,180]}
    # lower_color = np.array([min(color_dict[detect_obj_parameter['color_default']]), 60, 60])  
    # upper_color = np.array([max(color_dict[detect_obj_parameter['color_default']]), 255, 255])

    detect_obj_parameter['color_x'] = 160
    detect_obj_parameter['color_y'] = 120
    detect_obj_parameter['color_w'] = 0
    detect_obj_parameter['color_h'] = 0
    detect_obj_parameter['color_n'] = 0
    detect_obj_parameter['lower_color'] = np.array([min(color_dict[detect_obj_parameter['color_default']]), 60, 60]) 
    detect_obj_parameter['upper_color'] = np.array([max(color_dict[detect_obj_parameter['color_default']]), 255, 255])
    

#Human_obj_parameter
    detect_obj_parameter['human_x'] = 160
    detect_obj_parameter['human_y'] = 120
    detect_obj_parameter['human_w'] = 0
    detect_obj_parameter['human_h'] = 0
    detect_obj_parameter['human_n'] = 0

#traffic_sign_obj_parameter
    detect_obj_parameter['traffic_sign_x'] = 160
    detect_obj_parameter['traffic_sign_y'] = 120
    detect_obj_parameter['traffic_sign_w'] = 0
    detect_obj_parameter['traffic_sign_h'] = 0
    detect_obj_parameter['traffic_sign_t'] = 'None'
    detect_obj_parameter['traffic_sign_acc'] = 0

#gesture_obj_parameter
    detect_obj_parameter['gesture_x'] = 160
    detect_obj_parameter['gesture_y'] = 120
    detect_obj_parameter['gesture_w'] = 0
    detect_obj_parameter['gesture_h'] = 0
    detect_obj_parameter['gesture_t'] = 'None'
    detect_obj_parameter['gesture_acc'] = 0
    # detect_obj_parameter['human_n'] = 0


#detect_switch
    detect_obj_parameter['hdf_flag'] = False
    detect_obj_parameter['cdf_flag'] = False
    detect_obj_parameter['ts_flag'] = False
    detect_obj_parameter['gs_flag'] = False
    detect_obj_parameter['calibrate_flag'] = False   
    detect_obj_parameter['object_follow_flag'] = False
    detect_obj_parameter['qr_flag'] = False

#QR_code
    detect_obj_parameter['qr_data'] = 'None'

#video
    # detect_obj_parameter['vi_fps'] = 20
    # detect_obj_parameter['video_flag'] = False
    # detect_obj_parameter['video_path'] = './video_file/1.avi'

    # detect_obj_parameter['new_video'] = False
    # detect_obj_parameter['process_video'] = True

#picture
    detect_obj_parameter['picture_flag'] = False
    detect_obj_parameter['process_picture'] = True
    detect_obj_parameter['picture_path'] = '/home/pi/picture_file/' + time.strftime("%Y-%m-%d-%H-%M-%S")+ '.jpg'
    # detect_obj_parameter['color_default'] = 'red'

    # color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[166,180]}
    # lower_color = np.array([min(color_dict[detect_obj_parameter['color_default']]), 60, 60])  
    # upper_color = np.array([max(color_dict[detect_obj_parameter['color_default']]), 255, 255])


    rt_img = np.ones((320,240),np.uint8)
    front_view_img = np.zeros((240,320,3), np.uint8)
# 使用白色填充图片区域,默认为黑色
    # front_view_img.fill(255)       
    img_array[0] = rt_img
    # img_array = rt_img
    vi_img = np.ones((320,240),np.uint8)  



    @staticmethod
    def color_detect_object(obj_parameter):
        if obj_parameter == 'x':
            # print(Vilib.detect_obj_parameter['x'])          
            return int(Vilib.detect_obj_parameter['color_x']/107.0)-1
        elif obj_parameter == 'y':
            # print(Vilib.detect_obj_parameter['y']) 
            return -1*(int(Vilib.detect_obj_parameter['color_y']/80.1)-1) #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['color_w']   #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['color_h']   #objects_max_height
        elif obj_parameter == 'number':      
            return Vilib.detect_obj_parameter['color_n']   #objects_count
        return None

    @staticmethod
    def human_detect_object(obj_parameter):
        if obj_parameter == 'x':
            # print(Vilib.detect_obj_parameter['x'])          
            return int(Vilib.detect_obj_parameter['human_x']/107.0)-1
        elif obj_parameter == 'y':
            # print(Vilib.detect_obj_parameter['y']) 
            return -1*(int(Vilib.detect_obj_parameter['human_y']/80.1)-1) #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['human_w']   #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['human_h']   #objects_max_height
        elif obj_parameter == 'number':      
            return Vilib.detect_obj_parameter['human_n']   #objects_count
        return None

    @staticmethod
    def traffic_sign_detect_object(obj_parameter):
        if obj_parameter == 'x':
            # print(Vilib.detect_obj_parameter['x'])          
            return int(Vilib.detect_obj_parameter['traffic_sign_x']/107.0)-1
        elif obj_parameter == 'y':
            # print(Vilib.detect_obj_parameter['y']) 
            return -1*(int(Vilib.detect_obj_parameter['traffic_sign_y']/80.1)-1) #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['traffic_sign_w']   #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['traffic_sign_h']   #objects_max_height
        # elif obj_parameter == 'number':      
        #     return Vilib.detect_obj_parameter['traffic_sign_n']   #objects_count
        elif obj_parameter == 'type':      
            return Vilib.detect_obj_parameter['traffic_sign_t']   #objects_type
        elif obj_parameter == 'accuracy':      
            return Vilib.detect_obj_parameter['traffic_sign_acc']   #objects_type
        return None

    @staticmethod
    def gesture_detect_object(obj_parameter):
        if obj_parameter == 'x':
            # print(Vilib.detect_obj_parameter['x'])          
            return int(Vilib.detect_obj_parameter['gesture_x']/107.0)-1
        elif obj_parameter == 'y':
            # print(Vilib.detect_obj_parameter['y']) 
            return -1*(int(Vilib.detect_obj_parameter['gesture_y']/80.1)-1) #max_size_object_coordinate_y
        elif obj_parameter == 'width':
            return Vilib.detect_obj_parameter['gesture_w']   #objects_max_width
        elif obj_parameter == 'height':
            return Vilib.detect_obj_parameter['gesture_h']   #objects_max_height
        elif obj_parameter == 'type':      
            return Vilib.detect_obj_parameter['gesture_t']   #objects_type
        elif obj_parameter == 'accuracy':      
            return Vilib.detect_obj_parameter['gesture_acc']   #objects_type
        return None

    @staticmethod
    def qrcode_detect_object():
        return Vilib.detect_obj_parameter['qr_data']

    @staticmethod
    def detect_color_name(color_name):
        Vilib.detect_obj_parameter['color_default'] = color_name
        Vilib.detect_obj_parameter['lower_color'] = np.array([min(Vilib.color_dict[Vilib.detect_obj_parameter['color_default']]), 60, 60])  
        Vilib.detect_obj_parameter['upper_color'] = np.array([max(Vilib.color_dict[Vilib.detect_obj_parameter['color_default']]), 255, 255])
        # Vilib.detect_obj_parameter['color_x'] = 160
        # Vilib.detect_obj_parameter['color_y'] = 120
        # Vilib.detect_obj_parameter['color_w'] = 0
        # Vilib.detect_obj_parameter['color_h'] = 0
        # Vilib.detect_obj_parameter['color_n'] = 0

    @staticmethod
    def camera_start(web_func = True):
        from multiprocessing import Process
        # Vilib.conn1, Vilib.conn2 = Pipe()
        # Vilib.q = Queue()
        
        
        worker_2 = Process(name='worker 2',target=Vilib.camera_clone)
        if web_func == True:
            worker_1 = Process(name='worker 1',target=web_camera_start)
            worker_1.start()
        worker_2.start()
        # if web_func == True:
        #     print("1")
        #     # from flask_camera import web_camera_start
        #     t2 = threading.Thread(target=web_camera_start)  #Thread是一个类，实例化产生t1对象，这里就是创建了一个线程对象t1
        #     print("2")
        #     t2.start() #线程执行
        # print('cam')
        # t1 = threading.Thread(target=Vilib.camera_clone)  #Thread是一个类，实例化产生t1对象，这里就是创建了一个线程对象t1
        # t1.start() #线程执行
        # print('yes')
    
    @staticmethod
    def human_detect_switch(flag=False):
        Vilib.detect_obj_parameter['hdf_flag'] = flag

    @staticmethod
    def color_detect_switch(flag=False):
        Vilib.detect_obj_parameter['cdf_flag']  = flag

    @staticmethod
    def gesture_detect_switch(flag=False):
        Vilib.detect_obj_parameter['gs_flag']  = flag

    @staticmethod
    def traffic_sign_detect_switch(flag=False):
        Vilib.detect_obj_parameter['ts_flag']  = flag

    @staticmethod
    def gesture_calibrate_switch(flag=False):
        Vilib.detect_obj_parameter['calibrate_flag']  = flag

    @staticmethod
    def object_follow_switch(flag=False):
        Vilib.detect_obj_parameter['object_follow_flag'] = flag

    @staticmethod
    def qrcode_detect_switch(flag=False):
        Vilib.detect_obj_parameter['qr_flag']  = flag

    
    @staticmethod
    def camera_clone():
        Vilib.camera()     

    @staticmethod
    def camera():
        # from PIL import Image
        # rm = RGB_Matrix(0X74)  #RGB
        # k_img = []   
        camera = cv2.VideoCapture(Vilib.video_source)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID')

        camera.set(3,320)
        camera.set(4,240)
        # camera.set(5,80)
        width = int(camera.get(3))
        height = int(camera.get(4))
        # camera.set(cv2.CAP_PROP_FPS,30)
        # M = cv2.getRotationMatrix2D((width / 2, height / 2), 180, 1)
        # print("fps:",camera.get(5))
        camera.set(cv2.CAP_PROP_BUFFERSIZE,1)
        cv2.setUseOptimized(True)
        # fps = camera.get(cv2.CAP_PROP_FPS)

        # pj_img = cv2.imread("javars.png") 
        # pj_img = cv2.resize(pj_img, (320, 240), interpolation=cv2.INTER_LINEAR)
        
        # print(Vilib.front_view_img.shape)
        # front_view_coor_1 = ()
        # front_view_coor_2 = ()
        # video_recorder = cv2.VideoWriter('./video_file/buffer.avi', fourcc, Vilib.detect_obj_parameter['vi_fps'], (320, 240))
        # current_video_path = Vilib.detect_obj_parameter['video_path'] 

        # wait_fp = 0
        while True:
            # start_time = cv2.getTickCount()
            _, img = camera.read()
            # print(fps)

            bak_img = img.copy()
            img = Vilib.gesture_calibrate(img)
            img = Vilib.traffic_detect(img)
            img = Vilib.color_detect_func(img)
            img = Vilib.human_detect_func(img)
            img = Vilib.gesture_recognition(img)
            img = Vilib.qrcode_detect_func(img)
            # img = Vilib.object_follow(img)

            # small_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # red_mask_1 = cv2.inRange(small_hsv,(0,50,20), (4,255,255))           # 3.inRange()：介于lower/upper之间的为白色，其余黑色
            # red_mask_2 = cv2.inRange(small_hsv,(167,50,20), (180,255,255))
            # red_mask_all = cv2.bitwise_or(red_mask_1,red_mask_2)

            # # new_binary = cv2.GaussianBlur(red_mask_all, (5, 5), 0)

            # open_img = cv2.morphologyEx(red_mask_all, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)              #开运算 
            # open_img = cv2.dilate(open_img, Vilib.kernel_5,iterations=5) 
            # # open_img = cv2.morphologyEx(open_img, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)

            # blue_contours, hierarchy = cv2.findContours(open_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          ####在binary中发现轮廓，轮廓按照面积从小到大排列
                                
            # contours_count = len(blue_contours)
            # # print(contours_count)
            # blue_contours = sorted(blue_contours,key = Vilib.cnt_area, reverse=True)
            # if contours_count >=1:
            #     # for cnt in range(contours_count):
            #                     # print("contours:",contours_count)
            #     blue_contours = sorted(blue_contours,key = Vilib.cnt_area, reverse=True)
                                
            #                     # cv2.drawContours(img,contours,0,(0,0,255),3)
            #                     # print(len(blue_contours[0]))
                                
            #     epsilon = 0.02 * cv2.arcLength(blue_contours[0], True)
            #     approx = cv2.approxPolyDP(blue_contours[0], epsilon, True)
            #     cv2.drawContours(img,blue_contours,0,(0,0,255),3)

            #                     #     # 分析几何形状
            #     corners = len(approx)
                                        
            #                         #     # shape_type = ""
            #                         #     cv2.drawContours(img,blue_contours,0,(0,0,255),1)
            #     print(corners)
            # Vilib.video_record(img)

                
            # if Vilib.detect_obj_parameter['video_flag'] == True:
            #     if Vilib.detect_obj_parameter['video_path'] != current_video_path:
            #         current_video_path = Vilib.detect_obj_parameter['video_path']
            #         video_recorder = cv2.VideoWriter(Vilib.detect_obj_parameter['video_path'], fourcc, Vilib.detect_obj_parameter['vi_fps'], (320, 240))
                    
            #     print('start')
            #     # print(Vilib.detect_obj_parameter['video_path'])
            #     print(Vilib.detect_obj_parameter['video_path'])
            #     video_recorder.write(img)

            # Vilib.video_recorder.write(img)
            # img = cv2.warpAffine(img, M, (320, 240))
            # Vilib.front_view_img =img.copy()
            
### main
            # human_img = Vilib.human_detect_func(img)
            # color_img = Vilib.color_detect_func(human_img)
            # img = Vilib.gesture_recognition(img)

            if Vilib.detect_obj_parameter['picture_flag'] == True: 
                if Vilib.detect_obj_parameter['process_picture'] == True: 
                    # print(Vilib.detect_obj_parameter['process_picture'])
                    Vilib.take_photo(img)
                else:
                    # print(Vilib.detect_obj_parameter['process_picture'])
                    Vilib.take_photo(bak_img)


            Vilib.img_array[0] = img
            # end_time = cv2.getTickCount()
            # print(int(1/((end_time - start_time) / cv2.getTickFrequency())))
            # Vilib.refresh_fps(start_time,end_time)

            # img = Vilib.new_color_detect(img)
            # print(Vilib.color_detect_func(img).shape)
            # front_view_coor_1 = (Vilib.detect_obj_parameter['color_x'], Vilib.detect_obj_parameter['color_y'])
            # front_view_coor_2 = (Vilib.detect_obj_parameter['color_x']+40, Vilib.detect_obj_parameter['color_y']+40)
            # cv2.rectangle(Vilib.front_view_img, front_view_coor_1, front_view_coor_2, (255, 144, 30), -1)
            # cv2.rectangle(Vilib.front_view_img, (0,0), (320,20), (46,139,87), -1)
            # cv2.putText(Vilib.front_view_img,"temp: "+str(cpu_temperature()),(0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255),1,cv2.LINE_AA)
            # cv2.putText(Vilib.front_view_img,'hello world!',(160,160), cv2.FONT_HERSHEY_SIMPLEX, 1.5,(255,255,255),2, cv2.LINE_AA)
           # cv2.line(Vilib.front_view_img, (Vilib.detect_obj_parameter['color_x'], Vilib.detect_obj_parameter['color_y']), (120, 200), (255, 144, 30), 5)
            # Vilib.img_array[0] = cv2.addWeighted(img, 0.5, Vilib.front_view_img, 0.5, 0)


### photo picture
            # Vilib.img_array[0] = color_img

            # if Vilib.detect_obj_parameter['video_flag'] == True:
               
            #     if Vilib.detect_obj_parameter['new_video'] == True:
            #         video_recorder = cv2.VideoWriter('./video_file/buffer.avi', fourcc, Vilib.detect_obj_parameter['vi_fps'], (320, 240))
            #     else:
            #         if Vilib.detect_obj_parameter['video_path'] != current_video_path:
            #             # print('init:',Vilib.detect_obj_parameter['vi_fps'])
            #             # print(Vilib.detect_obj_parameter['video_path'])
            #             current_video_path = Vilib.detect_obj_parameter['video_path']
            #             video_recorder = cv2.VideoWriter(Vilib.detect_obj_parameter['video_path'], fourcc,Vilib.detect_obj_parameter['vi_fps'], (320, 240))
            #             wait_fp = 0

            #     if  wait_fp >=4:
            #         Vilib.detect_obj_parameter['new_video'] = False
            #     else:
            #         wait_fp += 1
                
            #     print("process_video:",Vilib.detect_obj_parameter['process_video'])
            #     if Vilib.detect_obj_parameter['process_video'] == True:
            #         video_recorder.write(color_img)
            #     else:
            #         video_recorder.write(bak_img)
            #     # print(Vilib.detect_obj_parameter['vi_fps'])
            #     # if wait_fp >=5:
            #     #     video_recorder.write(img)

            #         # print('fps:',Vilib.detect_obj_parameter['vi_fps'])
            #         # if Vilib.detect_obj_parameter['video_path'] != current_video_path:
            #         #     print(Vilib.detect_obj_parameter['video_path'])
            #         #     current_video_path = Vilib.detect_obj_parameter['video_path']
            #         #     video_recorder = cv2.VideoWriter(Vilib.detect_obj_parameter['video_path'], fourcc,Vilib.detect_obj_parameter['vi_fps'], (320, 240))
            #             # Vilib.detect_obj_parameter['new_video'] = True
            #         # wait_fp = 0

                    
            #     # else:
            #     #     print('fake_fps:',Vilib.detect_obj_parameter['vi_fps'])
            #     #     video_recorder.write(img)

            # # else:
            # #     wait_fp = 0
            #     # Vilib.detect_obj_parameter['last_video_flag'] = False

            # if Vilib.detect_obj_parameter['process_picture'] == True: 
            #     Vilib.take_photo(img)
            #     Vilib.take_photo(color_img)
            # else:
            #     Vilib.take_photo(bak_img)

            # end_time = cv2.getTickCount()
            # Vilib.refresh_fps(start_time,end_time)
            # # cv2.rectangle(Vilib.front_view_img, (0, 0), (320, 240), (255, 144, 30), 40)
            # # k_img = list(Image.fromarray(cv2.cvtColor(Vilib.img_array[0],cv2.COLOR_BGR2RGB)).getdata())#opencv转PIL
            # # rm.image(k_img)

            # # Vilib.img_array[0] = cv2.addWeighted(Vilib.color_detect_func(img), 0.9, pj_img, 0.1, 0)


            # # if w == True:
            # #     q.send(Vilib.vi_img)

### video

    # @staticmethod
    # def refresh_fps(start,end):
    #     Vilib.detect_obj_parameter['vi_fps'] = int(0.5 * int(1/((end - start) / cv2.getTickFrequency())) + 0.5 * Vilib.detect_obj_parameter['vi_fps'] + 0.5)
    #     # print(Vilib.vi_fps)

    # @staticmethod
    # def get_fps():
    #     return Vilib.detect_obj_parameter['vi_fps']


    # @staticmethod
    # def set_video(video_name,process_func = True):
    #     Vilib.detect_obj_parameter['video_path'] = './video_file/' + video_name + '.avi'
        
    #     # print('hhh: ',Vilib.detect_obj_parameter['video_path'])
    #     Vilib.detect_obj_parameter['video_flag'] = True
    #     Vilib.detect_obj_parameter['new_video'] = True
    #     Vilib.detect_obj_parameter['process_video'] = process_func

    # @staticmethod
    # def video_record(flag = False):
    #     Vilib.detect_obj_parameter['video_flag'] = flag

    
    # @staticmethod
    # def video_flag(flag = False):
    #     Vilib.detect_obj_parameter['video_flag'] = flag

    # @staticmethod
    # def video_record(img):
    #     if Vilib.detect_obj_parameter['video_flag'] == True:
    #         # video_path = './video_file/tst.avi'
    #         Vilib.video_recorder.write(img)


    @staticmethod
    def gesture_calibrate(img):
        if Vilib.detect_obj_parameter['calibrate_flag'] == True:
            # cv2.VideoWriter("./video_file/tt.avi", fourcc, 20.0, (640, 480))
                # roi_hsv = roi_hsv
            cv2.imwrite('/opt/ezblock/cali.jpg', img[90:150,130:190])
            # cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            cv2.rectangle(img,(130,90),(190,150),(255,255,255),2)
            # cv2.rectangle(img,(120,80),(80,80),(204,209,72),-1, cv2.LINE_AA)
            # Vilib.detect_obj_parameter['calibrate_flag'] = False

        return img
            # Vilib.detect_obj_parameter['picture_flag'] = False
            # cv2.imwrite(pic_path, Vilib.img_array[0])


    @staticmethod
    def get_picture(process_picture):
        Vilib.detect_obj_parameter['picture_flag'] = True
        Vilib.detect_obj_parameter['process_picture'] = process_picture
        # if Vilib.detect_obj_parameter['picture_flag'] == True:
        # Vilib.detect_obj_parameter['picture_path'] = '/home/pi/picture_file/' + time.strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'
        Vilib.detect_obj_parameter['picture_path'] = '/home/pi/picture_file/' + time.strftime("%Y-%m-%d-%H-%M-%S") + '.jpg'
            # cv2.VideoWriter("./video_file/tt.avi", fourcc, 20.0, (640, 480))
            # cv2.imwrite(pic_path, Vilib.img_array[0])

    @staticmethod
    def take_photo(img):
        if img is not None:
        # if Vilib.detect_obj_parameter['picture_flag'] == True:
            # print(Vilib.detect_obj_parameter['picture_path'])
            cv2.imwrite(Vilib.detect_obj_parameter['picture_path'], img)
            Vilib.detect_obj_parameter['picture_flag'] = False


    @staticmethod
    def cnt_area(cnt):
        x,y,w,h = cv2.boundingRect(cnt)
        return w*h



    @staticmethod
    def traffic_predict(input_img,x,y,w,h):
        # new_x = x
        # new_y = y
        # new_w = w
        # new_h = h
        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h)

        # print(x1,x2,y1,y2)
        new_img = input_img[y1:y2,x1:x2]
        # new_img = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
        # cv2.imwrite(str(x)+str(y)+'.jpg',new_img)
        new_img = (new_img / 255.0)
        # img = img / 255.
        new_img = (new_img - 0.5) * 2.0

        resize_img = cv2.resize(new_img, (96,96), interpolation=cv2.INTER_LINEAR)
        flatten_img = np.reshape(resize_img, (96,96,3))
        im5 = np.expand_dims(flatten_img,axis = 0)

    # Perform the actual detection by running the model with the image as input
        image_np_expanded = im5.astype('float32') # 类型也要满足要求

        interpreter_1.set_tensor(input_details_2[0]['index'],image_np_expanded)
        interpreter_1.invoke()
        output_data_2 = interpreter_1.get_tensor(output_details_2[0]['index'])

    #     # 出来的结果去掉没用的维度   np.where(result==np.max(result)))[0][0]
        result = np.squeeze(output_data_2)
        result_accuracy =  round(np.max(result),2)
        ges_class = np.where(result==np.max(result))[0][0]


        return result_accuracy,ges_class


### detection
    @staticmethod
    def gesture_predict(input_img,x,y,w,h):
        # new_x = x
        # new_y = y
        # new_w = w
        # new_h = h
        x1 = int(x)
        x2 = int(x + w)
        y1 = int(y)
        y2 = int(y + h)

        if x1 <= 0:
            x1 = 0
        elif x2 >= 320:
            x2 = 320
        if y1 <= 0:
            y1 = 0
        elif y2 >= 320:
            y2 = 320

        # print(x1,x2,y1,y2)
        new_img = input_img[y1:y2,x1:x2]
        # new_img = cv2.cvtColor(new_img,cv2.COLOR_BGR2GRAY)
        # cv2.imwrite(str(x)+str(y)+'.jpg',new_img)
        new_img = (new_img / 255.0)
        # img = img / 255.
        new_img = (new_img - 0.5) * 2.0

        resize_img = cv2.resize(new_img, (96,96), interpolation=cv2.INTER_LINEAR)
        flatten_img = np.reshape(resize_img, (96,96,3))
        im5 = np.expand_dims(flatten_img,axis = 0)

    # Perform the actual detection by running the model with the image as input
        image_np_expanded = im5.astype('float32') # 类型也要满足要求

        interpreter_2.set_tensor(input_details_2[0]['index'],image_np_expanded)
        interpreter_2.invoke()
        output_data_2 = interpreter_2.get_tensor(output_details_2[0]['index'])

    #     # 出来的结果去掉没用的维度   np.where(result==np.max(result)))[0][0]
        result = np.squeeze(output_data_2)
        result_accuracy =  round(np.max(result),2)
        ges_class = np.where(result==np.max(result))[0][0]

        # if result_accuracy >= 0.95:
        #     interpreter_1.set_tensor(input_details_1[0]['index'],image_np_expanded)
        #     interpreter_1.invoke()
        #     output_data_1 = interpreter_2.get_tensor(output_details_1[0]['index'])
        #     result_1 = np.squeeze(output_data_1)

        #     result_accuracy_1 =  round(np.max(result_1),2)
        #     ges_class_1 = np.where(result_1==np.max(result_1))[0][0]

        #     if (ges_class_1 == 0 and result_accuracy_1 >= 0.95) or (ges_class_1 == 1 and result_accuracy_1 >= 0.95):
        #         return result_accuracy_1,ges_class_1


        return result_accuracy,ges_class

    @staticmethod
    def traffic_detect(img):

        if Vilib.detect_obj_parameter['ts_flag']  == True:
            # resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)              # 2.从BGR转换到HSV
            cv2.circle(img, (160,120), 1, (255,255,255), -1)
            # print(hsv[160,120])
            # print(Vilib.lower_color)
            
            ### red
            mask_red_1 = cv2.inRange(hsv,(166,20,10), (180,255,255))
            mask_red_2 = cv2.inRange(hsv,(0,20,10), (10,255,255))
            # mask_red_2 = cv2.inRange(hsv, (175,50,20), (180,255,255))

            ### blue
            mask_blue = cv2.inRange(hsv,(92,50,20), (110,255,255))

            ### all
            mask_all = cv2.bitwise_or(mask_red_1, mask_blue)
            
            mask_all = cv2.bitwise_or(mask_red_2, mask_all)
            

        # color_dict = {'red':[0,4],'orange':[5,18],'yellow':[22,37],'green':[42,85],'blue':[92,110],'purple':[115,165],'red_2':[166,180]}

            open_img = cv2.morphologyEx(mask_all, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)              #开运算 
            # open_img = cv2.dilate(open_img, Vilib.kernel_5,iterations=5)  

            contours, hierarchy = cv2.findContours(open_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          ####在binary中发现轮廓，轮廓按照面积从小到大排列
                # p=0
            contours = sorted(contours,key = Vilib.cnt_area, reverse=False)
            traffic_n = len(contours)
            max_area = 0
            traffic_sign_num = 0

            if traffic_n > 0: 
                for i in contours:    #遍历所有的轮廓
                    x,y,w,h = cv2.boundingRect(i)      #将轮廓分解为识别对象的左上角坐标和宽、高

                        #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w > 32 and h > 32: 
                        # cv2.drawContours(img,i,0,(0,0,255),3)

                        # if corners == 3:
                        #     count = self.shapes['triangle']
                        #     count = count+1
                        #     self.shapes['triangle'] = count
                        #     shape_type = "三角形"
                        # if corners == 4:
                        #     count = self.shapes['rectangle']
                        #     count = count + 1
                        #     self.shapes['rectangle'] = count
                        #     shape_type = "矩形"

                        #     self.shapes['circles'] = count
                        #     shape_type = "圆形"
                        # else if 4 < corners < 10:
                        #     count = self.shapes['polygons']
                        #     count = count + 1
                        #     self.shapes['polygons'] = count
                        #     shape_type = "多边形"
                        # x = x*2
                        # y = y*2
                        # w = w*2
                        # h = h*2
                        acc_val, traffic_type = Vilib.traffic_predict(img,x,y,w,h)
                        # print(traffic_type,acc_val)
                        acc_val = round(acc_val*100)
                        if acc_val >= 75:   

                            if traffic_type == 1 or traffic_type == 2 or traffic_type == 3:
                                # hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # 2.从BGR转换到HSV   'blue':[92,110]  
            # print(Vilib.lower_color)
                                # mask = cv2.inRange(hsv, (92,50,20), (110,255,255))           # 3.inRange()：介于lower/upper之间的为白色，其余黑色

                                simple_gray = cv2.cvtColor(img[y:y+h,x:x+w], cv2.COLOR_BGR2GRAY)
                                # new_mask_blue = cv2.inRange(hsv[y:y+h,x:x+w],(92,70,50), (118,255,255))
                                circles = cv2.HoughCircles(simple_gray,cv2.HOUGH_GRADIENT,1,32,\
                                param1=140,param2=70,minRadius=int(w/4.0),maxRadius=max(w,h))
                               
                                if circles is not None:
                                    for i in circles[0,:]:
                                    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2) 
                                        traffic_sign_coor = (int(x+i[0]),int(y+i[1]))
                                        cv2.circle(img,traffic_sign_coor,i[2],(255,0,255),2)
                                        cv2.putText(img,str(traffic_dict[traffic_type]) +': ' + str(round(acc_val)),(int(x+i[0]-i[2]),int(y+i[1]-i[2])), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,255),2)#加减10是调整字符位置
                                        if w * h > max_area:
                                            max_area = w * h
                                            max_obj_x = x
                                            max_obj_y = y
                                            max_obj_w = w
                                            max_obj_h = h
                                            max_obj_t = traffic_type
                                            max_obj_acc = acc_val
                                            traffic_sign_num += 1

                            elif traffic_type == 0:
                                # small_hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)
                                red_mask_1 = cv2.inRange(hsv[y:y+h,x:x+w],(0,50,20), (4,255,255))           # 3.inRange()：介于lower/upper之间的为白色，其余黑色
                                red_mask_2 = cv2.inRange(hsv[y:y+h,x:x+w],(163,50,20), (180,255,255))
                                red_mask_all = cv2.bitwise_or(red_mask_1,red_mask_2)

                                        
                                # circles = np.uint16(np.around(circles))

                                # ret, new_binary = cv2.threshold(simple_gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
                                new_binary = cv2.GaussianBlur(red_mask_all, (5, 5), 0)

                                open_img = cv2.morphologyEx(red_mask_all, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)              #开运算  
                                open_img = cv2.dilate(open_img, Vilib.kernel_5,iterations=5) 

                                blue_contours, hierarchy = cv2.findContours(open_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          ####在binary中发现轮廓，轮廓按照面积从小到大排列
                                
                                contours_count = len(blue_contours)
                                if contours_count >=1:
                                # print("contours:",contours_count)
                                    blue_contours = sorted(blue_contours,key = Vilib.cnt_area, reverse=True)
                                
                                # cv2.drawContours(img,contours,0,(0,0,255),3)
                                # print(len(blue_contours[0]))
                                
                                    epsilon = 0.025 * cv2.arcLength(blue_contours[0], True)
                                    approx = cv2.approxPolyDP(blue_contours[0], epsilon, True)

                                #     # 分析几何形状
                                    corners = len(approx)
                                    
                                #     # shape_type = ""
                                #     cv2.drawContours(img,blue_contours,0,(0,0,255),1)
                                    # print(corners)
                                    if corners >= 0:
                                        # print("corners:",corners)
                                        # print("eight")
                                        traffic_sign_coor = (int(x+w/2),int(y+h/2))
                                        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2)
                                        cv2.putText(img,str(traffic_dict[traffic_type]) +': ' + str(round(acc_val)),(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,0,255),2)#加减10是调整字符位置
                                        if w * h > max_area:
                                            max_area = w * h
                                            max_obj_x = x
                                            max_obj_y = y
                                            max_obj_w = w
                                            max_obj_h = h
                                            max_obj_t = traffic_type
                                            max_obj_acc = acc_val
                                            traffic_sign_num += 1

                                        
                # print("traffic_sign_num:",traffic_sign_num)         
                if traffic_sign_num > 0:

                    Vilib.detect_obj_parameter['traffic_sign_x'] = int(max_obj_x + max_obj_w/2)
                    Vilib.detect_obj_parameter['traffic_sign_y'] = int(max_obj_y + max_obj_h/2)
                    Vilib.detect_obj_parameter['traffic_sign_w'] = max_obj_w
                    Vilib.detect_obj_parameter['traffic_sign_h'] = max_obj_h
                    # print("traffic_sign_type:",)
                    Vilib.detect_obj_parameter['traffic_sign_t'] = traffic_dict[max_obj_t]
                    Vilib.detect_obj_parameter['traffic_sign_acc'] = max_obj_acc
                else:
                    Vilib.detect_obj_parameter['traffic_sign_x'] = 160
                    Vilib.detect_obj_parameter['traffic_sign_y'] = 120
                    Vilib.detect_obj_parameter['traffic_sign_w'] = 0
                    Vilib.detect_obj_parameter['traffic_sign_h'] = 0
                    Vilib.detect_obj_parameter['traffic_sign_t'] = 'None'
                    Vilib.detect_obj_parameter['traffic_sign_acc'] = 0
                                    # cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                        

                                    # cv2.putText(img,str(ges_dict[ges_type]) +': ' + str(round(acc_val*100)),(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)#加减10是调整字符位置
 
        #                 object_area = w*h
        #                 if object_area > max_area: 
        #                     max_area = object_area
        #                     Vilib.detect_obj_parameter['color_x'] = int(x + w/2)
        #                     Vilib.detect_obj_parameter['color_y'] = int(y + h/2)
        #                     Vilib.detect_obj_parameter['color_w'] = w
        #                     Vilib.detect_obj_parameter['color_h'] = h
        #                     # print()
        #     else:
        #         Vilib.detect_obj_parameter['color_x'] = 160
        #         Vilib.detect_obj_parameter['color_y'] = 120
        #         Vilib.detect_obj_parameter['color_w'] = 0
        #         Vilib.detect_obj_parameter['color_h'] = 0
        #         Vilib.detect_obj_parameter['color_n'] = 0
        #     return img
        # else:
        else:
            Vilib.detect_obj_parameter['traffic_sign_x'] = 160
            Vilib.detect_obj_parameter['traffic_sign_y'] = 120
            Vilib.detect_obj_parameter['traffic_sign_w'] = 0
            Vilib.detect_obj_parameter['traffic_sign_h'] = 0
            Vilib.detect_obj_parameter['traffic_sign_t'] = 'None'
            Vilib.detect_obj_parameter['traffic_sign_acc'] = 0

        return img


    @staticmethod
    def gesture_recognition(img):
        if Vilib.detect_obj_parameter['gs_flag'] == True:

    ###肤色部分

            target_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            # 首先对样本图像计算2D直方图
            roi_hsv_hist = cv2.calcHist([Vilib.roi_hsv], [0, 1], None, [180, 256], [0, 180, 0, 255])
            # 对得到的样本2D直方图进行归一化
            # 这样可以方便显示，归一化后的直方图就变成0-255之间的数了
            # cv2.NORM_MINMAX表示对数组所有值进行转换，线性映射到最大最小值之间
            cv2.normalize(roi_hsv_hist, roi_hsv_hist, 0, 255, cv2.NORM_MINMAX)
            # 对待检测图像进行反向投影
            # 最后一个参数为尺度参数
            dst = cv2.calcBackProject([target_hsv], [0, 1], roi_hsv_hist, [0, 180, 0, 256], 1)
            # 构建一个圆形卷积核，用于对图像进行平滑，连接分散的像素
            disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            dst = cv2.filter2D(dst, -1, disc,dst)
            ret, thresh = cv2.threshold(dst, 1, 255, 0)
            dilate = cv2.dilate(thresh, Vilib.kernel_5, iterations=3)
                # 注意由于原图是三通道BGR图像，因此在进行位运算之前，先要把thresh转成三通道
            # thresh = cv2.merge((dilate, dilate, dilate))
                # 对原图与二值化后的阈值图像进行位运算，得到结果
            # res = cv2.bitwise_and(img, thresh)
            
            # ycrcb=cv2.cvtColor(img,cv2.COLOR_BGR2YCR_CB)

            # cr_skin = cv2.inRange(ycrcb, (85,124,121), (111,131,128))

            # open_img = cv2.morphologyEx(cr_skin, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)

            contours, hierarchy = cv2.findContours(dilate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            ges_num = len(contours)
            # max_area = 0
            # max_x = 0
            # max_y = 0
            # max_w = 0
            # max_h = 0
            # point_size = 1
            # point_color = (0, 0, 255) # BGR
            # thickness = 4 # 可以为 0 、4、8
            
            # acc_val,ges_type = Vilib.gesture_predict(img,x,y,w,h) 
            # print(ycrcb[160,120])
            # cv2.rectangle(img,(160-96,120-96),(160+96, 120+96),(0,125,0),2, cv2.LINE_AA)
            # acc_val,ges_type = Vilib.gesture_predict(img,160-96,120-96,192,192) 

            # # cv2.rectangle(img,(160-96,120-96),(160+96, 120+96),(0,125,125),2, cv2.LINE_AA)
            # cv2.putText(img,str(ges_type)+': '+str(round(acc_val*100)) + '%',(160-96,120-96),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,97,240),2)

            if ges_num > 0:
                contours = sorted(contours,key = Vilib.cnt_area, reverse=True)
                # for i in range(0,len(contours)):    #遍历所有的轮廓
                x,y,w,h = cv2.boundingRect(contours[0])      #将轮廓分解为识别对象的左上角坐标和宽、高
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
                faces = Vilib.face_cascade.detectMultiScale(gray[y:y+h,x:x+w], 1.3, 2)
            # print(len(faces))
                face_len = len(faces)
                    

                        #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）

                    
                if w >= 60 and h >= 60 and face_len == 0:
                    # acc_val,ges_type = Vilib.gesture_predict(img,x-2.2*w,y-2.8*h,4.4*w,5.6*h) 
                    acc_val,ges_type = Vilib.gesture_predict(img,x-0.1*w,y-0.2*h,1.1*w,1.2*h) 
                        # x = x*2
                        # y = y*2
                        # w = w*2
                        # h = h*2
                    acc_val = round(acc_val*100,3)
                    if acc_val >= 50:
                        cv2.rectangle(img,(int(x-0.1*w),int(y-0.2*h)),(int(x+1.1*w), int(y+1.2*h)),(0,125,0),2, cv2.LINE_AA)
                        cv2.rectangle(img,(105,0),(220,27),(204,209,72),-1, cv2.LINE_AA)
                        cv2.putText(img,ges_dict[ges_type]+': '+str(acc_val) + '%',(105,17),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)  ##(0,97,240)

                        # object_area = w*h
                        # if object_area > max_area: 
                        #     max_area = object_area

                        # max_x = int(x + w/2)
                        # max_y = int(y + h/2)
                        # max_w = w
                        # max_h = h

                        Vilib.detect_obj_parameter['gesture_x'] = int(x + w/2)
                        Vilib.detect_obj_parameter['gesture_y'] = int(y + h/2)
                        Vilib.detect_obj_parameter['gesture_w'] = w
                        Vilib.detect_obj_parameter['gesture_h'] = h
                        Vilib.detect_obj_parameter['gesture_t'] = ges_dict[ges_type]
                        Vilib.detect_obj_parameter['gesture_acc'] = acc_val
                                # print()
                    else:
                        Vilib.detect_obj_parameter['gesture_x'] = 160
                        Vilib.detect_obj_parameter['gesture_y'] = 120
                        Vilib.detect_obj_parameter['gesture_w'] = 0
                        Vilib.detect_obj_parameter['gesture_h'] = 0
                        Vilib.detect_obj_parameter['gesture_t'] = 'None'
                        Vilib.detect_obj_parameter['gesture_acc'] = 0

            # else:
            #     # cv2.rectangle(img,(55,35),(210,160),(255,0,0),2, cv2.LINE_AA)
            #     return img
            #     # cv2.rectangle(img,(55,35),(210,160),(255,0,0),2, cv2.LINE_AA)
                else:
                    Vilib.detect_obj_parameter['gesture_x'] = 160
                    Vilib.detect_obj_parameter['gesture_y'] = 120
                    Vilib.detect_obj_parameter['gesture_w'] = 0
                    Vilib.detect_obj_parameter['gesture_h'] = 0
                    Vilib.detect_obj_parameter['gesture_t'] = 'None'
                    Vilib.detect_obj_parameter['gesture_acc'] = 0

            else:
                Vilib.detect_obj_parameter['gesture_x'] = 160
                Vilib.detect_obj_parameter['gesture_y'] = 120
                Vilib.detect_obj_parameter['gesture_w'] = 0
                Vilib.detect_obj_parameter['gesture_h'] = 0
                Vilib.detect_obj_parameter['gesture_t'] = 'None'
                Vilib.detect_obj_parameter['gesture_acc'] = 0

        return img

    @staticmethod
    def human_detect_func(img):
        if Vilib.detect_obj_parameter['hdf_flag'] == True:
            resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)            # 2.从BGR转换到RAY
            gray = cv2.cvtColor(resize_img, cv2.COLOR_BGR2GRAY) 
            faces = Vilib.face_cascade.detectMultiScale(gray, 1.3, 2)
            # print(len(faces))
            Vilib.detect_obj_parameter['human_n'] = len(faces)
            max_area = 0
            if Vilib.detect_obj_parameter['human_n'] > 0:
                for (x,y,w,h) in faces:
                    x = x*2
                    y = y*2
                    w = w*2
                    h = h*2
                    cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                    object_area = w*h
                    if object_area > max_area: 
                        object_area = max_area
                        Vilib.detect_obj_parameter['human_x'] = int(x + w/2)
                        Vilib.detect_obj_parameter['human_y'] = int(y + h/2)
                        Vilib.detect_obj_parameter['human_w'] = w
                        Vilib.detect_obj_parameter['human_h'] = h
            
            else:
                Vilib.detect_obj_parameter['human_x'] = 160
                Vilib.detect_obj_parameter['human_y'] = 120
                Vilib.detect_obj_parameter['human_w'] = 0
                Vilib.detect_obj_parameter['human_h'] = 0
                Vilib.detect_obj_parameter['human_n'] = 0
            return img
        else:
            return img


    # @staticmethod
    # def new_color_detect(img):
    #     # resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)
    #     brightLAB = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    #     bgr = [40, 158, 16]
    #     thresh = 40
    #     lab = cv2.cvtColor( np.uint8([[bgr]] ), cv2.COLOR_BGR2LAB)[0][0]

    #     minLAB = np.array([lab[0] - thresh, lab[1] - thresh, lab[2] - thresh])
    #     maxLAB = np.array([lab[0] + thresh, lab[1] + thresh, lab[2] + thresh])

    #     maskLAB = cv2.inRange(brightLAB, minLAB, maxLAB)
    #     resultLAB = cv2.bitwise_and(brightLAB, brightLAB, mask = maskLAB)

    #     return resultLAB



    @staticmethod
    def color_detect_func(img):

        # 蓝色的范围，不同光照条件下不一样，可灵活调整   H：色度，S：饱和度 v:明度
        if Vilib.detect_obj_parameter['cdf_flag']  == True:
            resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # 2.从BGR转换到HSV
            # print(Vilib.lower_color)
            color_type = Vilib.detect_obj_parameter['color_default']
            
            mask = cv2.inRange(hsv,np.array([min(Vilib.color_dict[color_type]), 60, 60]), np.array([max(Vilib.color_dict[color_type]), 255, 255]) )           # 3.inRange()：介于lower/upper之间的为白色，其余黑色
            if color_type == 'red':
                 mask_2 = cv2.inRange(hsv, (167,0,0), (180,255,255))
                 mask = cv2.bitwise_or(mask, mask_2)

            open_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)              #开运算  

            contours, hierarchy = cv2.findContours(open_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          ####在binary中发现轮廓，轮廓按照面积从小到大排列
                # p=0
            Vilib.detect_obj_parameter['color_n'] = len(contours)
            max_area = 0

            if Vilib.detect_obj_parameter['color_n'] > 0: 
                for i in contours:    #遍历所有的轮廓
                    x,y,w,h = cv2.boundingRect(i)      #将轮廓分解为识别对象的左上角坐标和宽、高

                        #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w >= 8 and h >= 8: 
                        x = x*2
                        y = y*2
                        w = w*2
                        h = h*2
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                #给识别对象写上标号
                        cv2.putText(img,color_type,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)#加减10是调整字符位置
 
                        object_area = w*h
                        if object_area > max_area: 
                            max_area = object_area
                            Vilib.detect_obj_parameter['color_x'] = int(x + w/2)
                            Vilib.detect_obj_parameter['color_y'] = int(y + h/2)
                            Vilib.detect_obj_parameter['color_w'] = w
                            Vilib.detect_obj_parameter['color_h'] = h
                            # print()
            else:
                Vilib.detect_obj_parameter['color_x'] = 160
                Vilib.detect_obj_parameter['color_y'] = 120
                Vilib.detect_obj_parameter['color_w'] = 0
                Vilib.detect_obj_parameter['color_h'] = 0
                Vilib.detect_obj_parameter['color_n'] = 0
            return img
        else:
            return img


    @staticmethod
    def qrcode_detect_func(img):
        if Vilib.detect_obj_parameter['qr_flag']  == True:
            barcodes = pyzbar.decode(img)
            # 循环检测到的条形码
            if len(barcodes) > 0:
                for barcode in barcodes:
                    # 提取条形码的边界框的位置
                    # 画出图像中条形码的边界框
                    (x, y, w, h) = barcode.rect
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

                    # 条形码数据为字节对象，所以如果我们想在输出图像上
                    # 画出来，就需要先将它转换成字符串
                    barcodeData = barcode.data.decode("utf-8")
                    # barcodeType = barcode.type

                    # 绘出图像上条形码的数据和条形码类型
                    # text = "{} ({})".format(barcodeData, barcodeType)
                    text = "{}".format(barcodeData)
                    if len(text) > 0:
                        Vilib.detect_obj_parameter['qr_data'] = text
                    # print("Vilib.qr_date:%s"%Vilib.qr_date)
                    cv2.putText(img, text, (x - 20, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5, (0, 0, 255), 2)
            else:
                Vilib.detect_obj_parameter['qr_data'] = "None"
            return img
        else:
            return img

    @staticmethod
    def new_color_detect_func(img,color):
        Vilib.detect_color_name(color)

        # 蓝色的范围，不同光照条件下不一样，可灵活调整   H：色度，S：饱和度 v:明度
        if Vilib.detect_obj_parameter['cdf_flag']  == True:
            resize_img = cv2.resize(img, (160,120), interpolation=cv2.INTER_LINEAR)
            hsv = cv2.cvtColor(resize_img, cv2.COLOR_BGR2HSV)              # 2.从BGR转换到HSV
            # print(Vilib.lower_color)
            color_type = Vilib.detect_obj_parameter['color_default']
            
            mask = cv2.inRange(hsv,np.array([min(Vilib.color_dict[color_type]), 60, 60]), np.array([max(Vilib.color_dict[color_type]), 255, 255]) )           # 3.inRange()：介于lower/upper之间的为白色，其余黑色
            if color_type == 'red':
                 mask_2 = cv2.inRange(hsv, (167,0,0), (180,255,255))
                 mask = cv2.bitwise_or(mask, mask_2)

            open_img = cv2.morphologyEx(mask, cv2.MORPH_OPEN,Vilib.kernel_5,iterations=1)              #开运算  

            contours, hierarchy = cv2.findContours(open_img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)          ####在binary中发现轮廓，轮廓按照面积从小到大排列
                # p=0
            Vilib.detect_obj_parameter['color_n'] = len(contours)
            max_area = 0

            if Vilib.detect_obj_parameter['color_n'] > 0: 
                for i in contours:    #遍历所有的轮廓
                    x,y,w,h = cv2.boundingRect(i)      #将轮廓分解为识别对象的左上角坐标和宽、高

                        #在图像上画上矩形（图片、左上角坐标、右下角坐标、颜色、线条宽度）
                    if w >= 8 and h >= 8: 
                        x = x*2
                        y = y*2
                        w = w*2
                        h = h*2
                        cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
                                #给识别对象写上标号
                        cv2.putText(img,color_type,(x,y), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)#加减10是调整字符位置
 
                        object_area = w*h
                        if object_area > max_area: 
                            max_area = object_area
                            Vilib.detect_obj_parameter['color_x'] = int(x + w/2)
                            Vilib.detect_obj_parameter['color_y'] = int(y + h/2)
                            Vilib.detect_obj_parameter['color_w'] = w
                            Vilib.detect_obj_parameter['color_h'] = h
                            # print()
            else:
                Vilib.detect_obj_parameter['color_x'] = 160
                Vilib.detect_obj_parameter['color_y'] = 120
                Vilib.detect_obj_parameter['color_w'] = 0
                Vilib.detect_obj_parameter['color_h'] = 0
                Vilib.detect_obj_parameter['color_n'] = 0
            return img
        else:
            return img


    # @staticmethod
    # def object_follow(img):
    #     if Vilib.detect_obj_parameter['object_follow_flag']  == True:
    #         hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #         dst = cv2.calcBackProject([hsv],[0,1],Vilib.roi_hist,[0,180,0,256],1)#反向投影
    #         disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    #         dst = cv2.filter2D(dst,-1,disc,dst)
    #         ret,thresh = cv2.threshold(dst,1,255,0)
    #         # dilate = cv2.dilate(thresh,kernel_5,iterations=3)

    #         #使用 meanshift获得新位置
    #         ret, track_window = cv2.CamShift(thresh,Vilib.track_window, term_crit)
    #         # print(ret)

    #         #显示标记
    #         print(ret)
    #         pts = cv2.boxPoints(ret)
    #         pts = np.int0(pts)
    #         img = cv2.polylines(img,[pts],True, (255,0,0),2)
    #         return img
    #     else:
    #         return img