#!/usr/bin/env python3
import os, sys

errors = []

avaiable_options = ['-h', '--help', '--no-dep']

usage = '''
Usage:
    sudo python3 install.py [option]

Options:
               --no-dep    Do not download dependencies
    -h         --help      Show this help text and exit
'''
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
    print("EzBlock service install process starts")
    print("Install dependency")
    if "--no-dep" not in options:
        do(msg="update apt-get",
            cmd='run_command("sudo apt-get update")')
        do(msg="install pip",
            cmd='run_command("sudo apt-get install python3-pip -y")')
        do(msg="install i2c-tools",
            cmd='run_command("sudo apt-get install i2c-tools -y")')
        # do(msg="install libttspico-utils",
        #     cmd='run_command("sudo apt-get install libttspico-utils -y")')
        do(msg="install espeak",
            cmd='run_command("sudo apt-get install espeak -y")')
        do(msg="install picamera",
            cmd='run_command("sudo pip3 install picamera")')

        do(msg="install opencv-python",
            cmd='run_command("sudo pip3 install opencv-python")')
        do(msg="install libatlas-base-dev",
            cmd='run_command("sudo apt-get install libatlas-base-dev -y")')
        do(msg="install libjasper-dev",
            cmd='run_command("sudo apt-get install libjasper-dev -y")')
        do(msg="install libqt4-test",
            cmd='run_command("sudo apt-get install libqt4-test -y")')
        do(msg="install libwebp6",
            cmd='run_command("sudo apt-get install libwebp6 -y")')
        do(msg="install libtiff5",
            cmd='run_command("sudo apt-get install libtiff5 -y")')
        do(msg="install libopenexr23",
            cmd='run_command("sudo apt-get install libopenexr23 -y")')
        do(msg="install libgstreamer1.0-0",
            cmd='run_command("sudo apt-get install libgstreamer1.0-0 -y")')
        do(msg="install libavcodec-dev",
            cmd='run_command("sudo apt-get install libavcodec-dev -y")')
        do(msg="install libavformat-dev",
            cmd='run_command("sudo apt-get install libavformat-dev -y")')
        do(msg="install libswscale-dev",
            cmd='run_command("sudo apt-get install libswscale-dev -y")')
        do(msg="install libqtgui4",
            cmd='run_command("sudo apt-get install libqtgui4 -y")')

    # do(msg="unpackaging swift",
    #     cmd='run_command("tar zxvf ./lib/swift-4.1.3-RPi23-RaspbianStretch.tgz")')
    # do(msg="copy swift to /usr",
    #     cmd='run_command("sudo cp -r usr /")')
    # do(msg="cleanup",
    #     cmd='run_command("sudo rm -rf usr")')

    print("Setup interfaces")
    do(msg="turn on I2C",
        cmd='Config().set("dtparam=i2c_arm", "on")')
    do(msg="Add I2C module",
        cmd='Modules().set("i2c-dev")')
    do(msg="turn on SPI",
        cmd='Config().set("dtparam=spi", "on")')
    # do(msg="Add SPI module",
    #     cmd='Modules().set("i2c-dev")')
    do(msg="turn on one-wire",
        cmd='Config().set("dtoverlay", "w1-gpio")')
    do(msg="turn on Lirc",
        cmd='Config().set("dtoverlay=lirc-rpi:gpio_in_pin", "26")')
    do(msg="turn on Uart",
        cmd='Config().set("enable_uart", "1")')
    do(msg="set gpu memory to 128",
        cmd='Config().set("gpu_mem", "128")')
    do(msg="enable camera",
        cmd='Config().set("start_x", "1")')
    do(msg="turn off serial terminal",
        cmd='Cmdline().remove("console=serial0")')

    print("Setup ezblock service")
    do(msg="copy ezblock file",
        cmd='run_command("sudo cp ./bin/ezblock /etc/init.d/ezblock")')
    do(msg="add excutable mode for ezblock",
        cmd='run_command("sudo chmod +x /etc/init.d/ezblock")')
    do(msg="update service settings for ezblock",
        cmd='run_command("sudo update-rc.d ezblock defaults")')
    do(msg="copy ezblock-service file",
        cmd='run_command("sudo cp ./bin/ezblock-service /usr/bin")')
    do(msg="add excutable mode for ezblock-service",
        cmd='run_command("sudo chmod +x /usr/bin/ezblock-service")')
    do(msg="copy libezblock file",
        cmd='run_command("sudo cp ./lib/libezblock.so /usr/local/lib/python3.7/dist-packages")')

    print("Setup ezblock-reset service")
    do(msg="copy ezblock-reset file",
        cmd='run_command("sudo cp ./bin/ezblock-reset /etc/init.d/ezblock-reset")')
    do(msg="add excutable mode for ezblock-reset",
        cmd='run_command("sudo chmod +x /etc/init.d/ezblock-reset")')
    do(msg="update service settings for ezblock-reset",
        cmd='run_command("sudo update-rc.d ezblock-reset defaults")')
    do(msg="copy ezblock-reset-service file",
        cmd='run_command("sudo cp ./bin/ezblock-reset-service /usr/bin")')
    do(msg="add excutable mode for ezblock-reset-service",
        cmd='run_command("sudo chmod +x /usr/bin/ezblock-reset-service")')

    do(msg="copy resize_once file",
        cmd='run_command("sudo cp ./bin/resize_once /usr/bin")')
    do(msg="add excutable mode for resize_one",
        cmd='run_command("sudo chmod +x /usr/bin/resize_once")')

    print("Create workspace")
    _, result = run_command("ls /opt")
    if "ezblock" not in result:
        do(msg="create dir",
            cmd='run_command("mkdir /opt/ezblock")')
    do(msg="copy workspace",
        cmd='run_command("sudo cp -r ./workspace/* /opt/ezblock/")')
    _, result = run_command("ls /opt/ezblock/.info")
    if result == "":
        do(msg="copy .info file",
            cmd='run_command("sudo cp -r ./workspace/.info /opt/ezblock/")')
    #       cmd='run_command("sudo echo \'name: ezb-RPi\n\' > /opt/ezblock/.info")')
    do(msg="add write permission to log file",
        cmd='run_command("sudo chmod 666 /opt/ezblock/log")')

    os.chdir("./ezblock")
    print("Install ezblock python package")
    do(msg="run setup file",
        cmd='run_command("sudo python3 setup.py install")')
    do(msg="cleanup",
        cmd='run_command("sudo rm -rf ezblock.egg-info")')
    os.chdir("../")

    if len(errors) == 0:
        print("Finished")
    else:
        print("\n\nError happened in install process:")
        for error in errors:
            print(error)
        print("Try to fix it yourself, or contact service@sunfounder.com with this message")
        sys.exit(1)


def test():
    do(msg="install clang",
        cmd='run_command("sudo apt-get install clang -y")')

def cleanup():
    do(msg="cleanup",
        cmd='run_command("sudo rm -rf usr ezblock.egg-info")')

class Modules(object):
    ''' 
        To setup /etc/modules
    '''

    def __init__(self, file="/etc/modules"):
        self.file = file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name):
        have_excepted = False
        for i in range(len(self.configs)):
            config = self.configs[i]
            if name in config:
                have_excepted = True
                tmp = name
                self.configs[i] = tmp
                break

        if not have_excepted:
            tmp = name
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            # print(config)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

class Config(object):
    ''' 
        To setup /boot/config.txt
    '''

    def __init__(self, file="/boot/config.txt"):
        self.file = file
        with open(self.file, 'r') as f:
            self.configs = f.read()
        self.configs = self.configs.split('\n')

    def remove(self, expected):
        for config in self.configs:
            if expected in config:
                self.configs.remove(config)
        return self.write_file()

    def set(self, name, value=None):
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
            tmp = name
            if value != None:
                tmp += '=' + value
            self.configs.append(tmp)
        return self.write_file()

    def write_file(self):
        try:
            config = '\n'.join(self.configs)
            # print(config)
            with open(self.file, 'w') as f:
                f.write(config)
            return 0, config
        except Exception as e:
            return -1, e

class Cmdline(object):
    ''' 
        To setup /boot/cmdline.txt
    '''

    def __init__(self, file="/boot/cmdline.txt"):
        self.file = file
        with open(self.file, 'r') as f:
            cmdline = f.read()
        self.cmdline = cmdline.strip()
        self.cmds = self.cmdline.split(' ')

    def remove(self, expected):
        for cmd in self.cmds:
            if expected in cmd:
                self.cmds.remove(cmd)
        return self.write_file()

    def write_file(self):
        try:
            cmdline = ' '.join(self.cmds)
            # print(cmdline)
            with open(self.file, 'w') as f:
                f.write(cmdline)
            return 0, cmdline
        except Exception as e:
            return -1, e


def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result


def do(msg="", cmd=""):
    print(" - %s..." % (msg), end='\r')
    print(" - %s... " % (msg), end='')
    status, result = eval(cmd)
    # print(status, result)
    if status == 0 or status == None or result == "":
        print('Done')
    else:
        print('Error')
        errors.append("%s error:\n  Status:%s\n  Error:%s" %
                      (msg, status, result))

if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("Canceled.")
        cleanup()

# if __name__ == "__main__":
#     test()
