#!/usr/bin/env python3
import os, sys
import time
import threading

# define color print
# =================================================================
def warn(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;33m{msg}\033[0m', end=end, file=file, flush=flush)

def error(msg, end='\n', file=sys.stdout, flush=False):
    print(f'\033[0;31m{msg}\033[0m', end=end, file=file, flush=flush)

# version
# =================================================================
sys.path.append('./ezblock/ezblock')
try:
    from version import __version__
    print(f"ezblock version {__version__}")
except:
    warn("Please run within the ezb-pi directory.")
    quit(1)

# check if run as root
# =================================================================
if os.geteuid() != 0:
    warn("Script must be run as root. Try \"sudo python3 install.py\".")
    quit(1)


# get username and userhome, file abspath 
# =================================================================
from pathlib import Path
import pwd

try:
    abspath = Path("install.py").resolve().parent
except:
    warn("Please run within the ezb-pi directory.")
    quit(1)

uid = os.stat(abspath).st_uid
pw = pwd.getpwuid(uid)
user_name = pw.pw_name
user_home = pw.pw_dir

# print(f"abspath: {abspath}")
# print(f"user: {user_name}")
# print(f"userhome: {user_home}")

# variables defined
# =================================================================
errors = []

avaiable_options = ['-h', '--help', '--no-dep']

usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --no-dep             Do not download dependencies
    -h         --help               Show this help text and exit
'''

# utils
# =================================================================
def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

at_work_tip_sw = False
def working_tip():
    char = ['/', '-', '\\', '|']
    i = 0
    global at_work_tip_sw
    while at_work_tip_sw:  
            i = (i+1)%4 
            sys.stdout.write('\033[?25l') # cursor invisible
            sys.stdout.write('%s\033[1D'%char[i])
            sys.stdout.flush()
            time.sleep(0.5)

    sys.stdout.write('\033[?25h') # cursor visible 
    sys.stdout.flush()  

def do(msg="", cmd=""):
    print(" - %s ... " % (msg), end='', flush=True)
    # at_work_tip start 
    global at_work_tip_sw
    at_work_tip_sw = True
    _thread = threading.Thread(target=working_tip)
    _thread.daemon = True
    _thread.start()
    # process run
    status, result = run_command(cmd)
    # print(status, result)
    # at_work_tip stop
    at_work_tip_sw = False
    _thread.join()
    # status
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

def set_config(msg="", name="", value=""):
    print(" - %s... " % (msg), end='', flush=True)
    try:
        Config().set(name, value)
        print('Done')
    except Exception as e:
        print('\033[1;35mError\033[0m')
        errors.append("%s error:\n Error:%s" %(msg, e))       

class Config(object):
    '''
        To setup /boot/config.txt (Raspbian, Kali OSMC, etc)
        /boot/firmware/config.txt (Ubuntu)
     
    '''
    DEFAULT_FILE_1 = "/boot/config.txt" # raspbian
    DEFAULT_FILE_2 = "/boot/firmware/config.txt" # ubuntu

    def __init__(self, file=None):
        # check if file exists
        if file is None:
            if os.path.exists(self.DEFAULT_FILE_1):
                self.file = self.DEFAULT_FILE_1
            elif os.path.exists(self.DEFAULT_FILE_2):
                self.file = self.DEFAULT_FILE_2
            else:
                raise FileNotFoundError(f"{self.DEFAULT_FILE_1} or {self.DEFAULT_FILE_2} are not found.")
        else:
            self.file = file
            if not os.path.exists(file):
                raise FileNotFoundError(f"{self.file} is not found.")
        # read config file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name, value=None, device="[all]"):
        '''
        device : "[all]", "[pi3]", "[pi4]" or other
        '''
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                if value != None:
                    tmp += '=' + value
                self.configs[i] = tmp
                break

        if not have_excepted:
            self.configs.append(device)
            tmp = name
            if value != None:
                tmp += '=' + value
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

def cleanup():
    import signal

    def handle(signal, frame):
        print('\nplease wait for cleanup ... ', end='')

    def handle_timeout(signum, frame):
        raise TimeoutError('function timeout')

    signal.signal(signal.SIGINT, handle)
    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(5) # 5s timeout


    do(msg="cleanup",
        cmd=f'rm -rf {abspath}/ezblock/ezblock.egg-info')

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.alarm(0)
    
# dependencies list installed with apt
# =================================================================
APT_INSTALL_LIST = [
    # 
    'python3-pip',
    'python3-setuptools',
    # --- robot_hat ---
    'raspi-config',
    "i2c-tools",
    "bluez-firmware",  # Update bluez firmware
    'python3-dbus', # ble
    "lsof",  # tcp port
    "mplayer", # music player
    'libsdl2-dev',
    'libsdl2-mixer-dev',
    "python3-pyaudio",
    'portaudio19-dev',  # pyaudio
    "espeak", # tts
    'libttspico-utils', # tts pico2wave
    # --- vilib ---
    "python3-libcamera",
    "python3-picamera2",
    "python3-opencv",
    "ffmpeg",
    "python3-flask",
    'libzbar0', # pyzbar dependencies
]

# dependencies list installed with pip3
# =================================================================
PIP_INSTALL_LIST = [
    # --- robot_hat ---
    "gpiozero",
    "smbus2",
    "spidev",
    "pyserial",
    "pillow",
    "pygame>=2.1.2",
    # --- websockets ---
    "websockets",
    # --- iot ---
    "paho-mqtt",
    # --- vilib ---
    "tflite-runtime",
    "pyzbar", # QR codes
    "pyzbar[scripts]",
    "imutils",
    'numpy==1.26.4',
    # --- process management --- 
    'psutil',
]

# main function
# =================================================================
def install():
    options = []
    if len(sys.argv) > 1:
        options = sys.argv[1:]
        for o in options:
            if o not in avaiable_options:
                print("Option {} is not found.".format(o))
                print(usage)
                quit()
    if "-h" in options or "--help" in options:
        print(usage)
        quit()

    # print info
    # ===================================
    # username
    print(f'user: {user_name}')
    # Kernel version
    status, result = run_command("uname -a")
    if status == 0:
        print(f"Kernel Version:\n{result}")
    # OS version
    status, result = run_command("lsb_release -a|grep Description")
    if status == 0:
        print(f"OS Version:\n{result}")
    # PCB information
    status, result = run_command("cat /proc/cpuinfo|grep -E \'Revision|Model\'")
    if status == 0:
        print(f"PCB info:\n{result}")

    if "--no-dep" not in options:
        # install dependencies with apt
        # ===================================
        print("Install dependencies with apt:")
        do(msg="update apt-get",
            cmd='apt-get update -y')
        do(msg="dpkg configure",
            cmd='dpkg --configure -a') 

        for dep in APT_INSTALL_LIST:
            do(msg=f"install {dep}",
                cmd=f'apt-get install {dep} -y')
        
        # install dependencies with pip
        # ===================================
        print("Install dependencies with pip3:")
        # check whether pip has the option "--break-system-packages"
        _is_bsps = ''
        status, _ = run_command("pip3 help install|grep break-system-packages")
        if status == 0: # if true
            _is_bsps = "--break-system-packages"
            print("\033[38;5;8m pip3 install with --break-system-packages\033[0m")
        # update pip
        do(msg="update pip3",
            cmd=f'python3 -m pip install --upgrade pip {_is_bsps}'
        )
        for dep in PIP_INSTALL_LIST:
            do(msg=f"install {dep}",
                cmd=f'pip3 install {dep} {_is_bsps}')

    # setup interfaces
    # ===================================
    print("Setup interfaces")
    #
    _status, _ = run_command("raspi-config nonint")
    if _status == 0:
        do(msg="enable i2c with raspi-config",
            cmd='raspi-config nonint do_i2c 0'
        )
        do(msg="enable spi with raspi-config",
            cmd='raspi-config nonint do_spi 0'
        )
    #
    set_config(msg="enable i2c",
        name="dtparam=i2c_arm",
        value="on"
    )
    set_config(msg="enable spi",
        name="dtparam=spi",
        value="on"
    )
    set_config(msg="enable uart",
        name="enable_uart",
        value="1"
    )
    set_config(msg="enable one-wire",
        name="dtoverlay",
        value="w1-gpio"
    )
    set_config(msg="turn on Lirc in Pin 26",
        name="lirc-rpi:gpio_in_pin",
        value="26"
    )
    set_config(msg="set gpu memory to 128",
        name="gpu_mem",
        value="128"
    )
    # Copy sound files
    # ===================================
    if not os.path.exists(f"{user_home}/Music/"):
        do(msg="mkdir ~/Music/",
        cmd=f'mkdir {user_home}/Music/'
        + f' && chown {user_name}:{user_name} {user_home}/Music/'
        + f' && chmod 774 {user_home}/Music/'
        )
    if not os.path.exists(f"{user_home}/Sound/"):
        do(msg="mkdir ~/Sound/",
        cmd=f'mkdir {user_home}/Sound/'
        + f' && chown {user_name}:{user_name} {user_home}/Sound/'
        + f' && chmod 774 {user_home}/Sound/'
        )
    do(msg="copy sound files",
        cmd=f'cp -arf ./music/* {user_home}/Music/'
        + f' && cp -arf ./sound/* {user_home}/Sound/'
        )
    # Setup ezblock service
    # ===================================
    print("Setup ezblock service")
    do(msg="copy ezblock file",
        cmd='cp ./bin/ezblock /etc/init.d/ezblock')
    do(msg="add excutable mode for ezblock",
        cmd='chmod +x /etc/init.d/ezblock')
    do(msg="update service settings for ezblock",
        cmd='update-rc.d ezblock defaults')
    do(msg="copy ezblock-service file",
        cmd='cp ./bin/ezblock-service /usr/bin')
    do(msg="add excutable mode for ezblock-service",
        cmd='chmod +x /usr/bin/ezblock-service')
    #
    print("Setup ezblock-reset service")
    do(msg="copy ezblock-reset file",
        cmd='cp ./bin/ezblock-reset /etc/init.d/ezblock-reset')
    do(msg="add excutable mode for ezblock-reset",
        cmd='chmod +x /etc/init.d/ezblock-reset')
    do(msg="update service settings for ezblock-reset",
        cmd='update-rc.d ezblock-reset defaults')
    do(msg="copy ezblock-reset-service file",
        cmd='cp ./bin/ezblock-reset-service /usr/bin')
    do(msg="add excutable mode for ezblock-reset-service",
        cmd='chmod +x /usr/bin/ezblock-reset-service')

    # Setup resize_once service
    # ===================================
    print("Setup resize_once service")
    do(msg="copy resize_once file",
        cmd='cp ./bin/resize_once /usr/bin')
    do(msg="add excutable mode for resize_one",
        cmd='chmod +x /usr/bin/resize_once')

    # Create workspace
    # ===================================
    print("Create workspace")
    _, result = run_command("ls /opt")
    if "ezblock" not in result:
        do(msg="create dir",
            cmd='mkdir /opt/ezblock')

    do(msg="copy workspace",
        cmd='cp -r ./workspace/* /opt/ezblock/')

    _, result = run_command("ls /opt/ezblock/.info")
    if result == "":
        do(msg="copy .info file",
            cmd='cp -r ./workspace/.info /opt/ezblock/')

    do(msg="add write permission to log file",
        cmd='chmod 666 /opt/ezblock/log')

    do(msg=f"change owner to opt ezblock",
        cmd=f'chown -R {user_name}:{user_name} /opt/ezblock/')

    do(msg="create .uspid_init_config file",
        cmd='touch /opt/ezblock/.uspid_init_config')

    # Install ezblock python3 package
    # ===================================
    print('Install ezblock python3 package')
    os.chdir("./ezblock")
    do(msg="run setup file",
        cmd='python3 setup.py install')
    cleanup()
    os.chdir("../")

    # end and check errors
    # =================================
    if len(errors) == 0:
        print("Finished")
        print("\033[1;32mWhether to restart for the changes to take effect(Y/N):\033[0m")
        while True:
            key = input()
            if key == 'Y' or key == 'y':
                print(f'reboot')
                run_command('reboot')
            elif key == 'N' or key == 'n':
                print(f'exit')
                sys.exit(0)
            else:
                continue
    else:
        print("\n\nError happened in install process:")
        for error in errors:
            print(error)
        print("Try to fix it yourself, or contact service@sunfounder.com with this message")
        sys.exit(1)


if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("\n\n User Canceled.")
    finally:
        cleanup()
        sys.stdout.write(' \033[1D')
        sys.stdout.write('\033[?25h') # cursor visible 
        sys.stdout.flush()

