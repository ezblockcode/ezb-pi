#!/usr/bin/env python3
import os

errors = []


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


def install():
    print("EzBlock service install process starts")
    print("Install dependency")
    do(msg="install clang",
        cmd='run_command("sudo apt-get install clang -y")')
    # do(msg="install opencv-python",
    #     cmd='run_command("sudo pip3 install opencv-python")')
    do(msg="unpackaging swift",
        cmd='run_command("tar zxvf ./lib/swift-4.1.3-RPi23-RaspbianStretch.tgz")')
    do(msg="copy swift to /usr",
        cmd='run_command("sudo cp -r usr /")')
    do(msg="cleanup",
        cmd='run_command("sudo rm -rf usr")')

    print("Setup interfaces")
    do(msg="turn on I2C",
        cmd='Config().set("dtparam=i2c_arm", "on")')
    do(msg="turn on SPI",
        cmd='Config().set("dtparam=spi", "on")')
    do(msg="turn on one-wire",
        cmd='Config().set("dtoverlay", "w1-gpio")')
    do(msg="turn on Lirc",
        cmd='Config().set("dtoverlay=lirc-rpi:gpio_in_pin", "26")')
    do(msg="turn on Uart",
        cmd='Config().set("enable_uart", "1")')
    do(msg="turn off serial terminal",
        cmd='Cmdline().remove("console=serial0")')

    print("Setup ezblock service")
    do(msg="add excutable mode for ezblock",
        cmd='run_command("sudo chmod +x ./bin/ezblock")')
    do(msg="copy ezblock file",
        cmd='run_command("sudo cp ./bin/ezblock /etc/init.d/ezblock")')
    do(msg="update service settings for ezblock",
        cmd='run_command("sudo update-rc.d ezblock defaults")')
    do(msg="add excutable mode for ezblock-boot",
        cmd='run_command("sudo chmod +x ./bin/ezblock-boot")')
    do(msg="copy ezblock-boot file",
        cmd='run_command("sudo cp ./bin/ezblock-boot /usr/bin")')
    do(msg="copy libezblock file",
        cmd='run_command("sudo cp ./lib/libezblock.so /usr/local/lib/python3.5/dist-packages")')

    print("Create workspace")
    do(msg="copy workspace",
        cmd='run_command("sudo cp -r ./workspace /opt/ezblock")')
    print("Touch .info file")
    do(msg="touch .info file",
        cmd='run_command("sudo touch /opt/ezblock/.info")')

    os.chdir("./raspberrypi")
    print("Install Raspberry Pi python package")
    do(msg="run setup file",
        cmd='run_command("sudo python3 setup.py install")')
    do(msg="cleanup",
        cmd='run_command("sudo rm -rf raspberrypi.egg-info")')
    os.chdir("../")

    if len(errors) == 0:
        print("Finished")
    else:
        print("\n\nError happened in install process:")
        for error in errors:
            print(error)
        print("Try to fix it yourself, or contact service@sunfounder.com with this message")


def test():
    do(msg="install clang",
        cmd='run_command("sudo apt-get install clang -y")')

def cleanup():
    do(msg="cleanup",
        cmd='run_command("sudo rm -rf usr raspberrypi.egg-info")')

if __name__ == "__main__":
    try:
        install()
    except KeyboardInterrupt:
        print("Canceled.")
        cleanup()

# if __name__ == "__main__":
#     test()
