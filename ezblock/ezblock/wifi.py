from .basic import _Basic_class
# __print__ = print
from .utils import getIP
from .utils import print
import time
# re-正则表达式
class WiFi(_Basic_class):
    message = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country={}
network={{
    ssid="{}"
    psk="{}"
    key_mgmt=WPA-PSK
}}"""

    def __init__(self):
        self.country = ""

    def connect(self, ssid, psk):
        result = self.get_current_ssid()
        ip = getIP('wlan0')
        if result == ssid and ip != False:
            print('Wi-Fi is already connected to %s, skip'%(ssid))
            print("IP: %s" % ip)
            return True
        print("Connecting to \"{}\"...".format(ssid))
        message = self.message.format(self.country, ssid, psk)
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
            f.write(message)
        
        for i in range(6):
            if i != 0:
                print('Timeout, retry (%s)...'%i)
            self.run_command("wpa_cli -i wlan0 reconfigure")
            time.sleep(1)
            time_start = time.time()
            while True:
                ip = getIP('wlan0')
                if ip:
                    print("IP: %s" % ip)
                    print('WiFi connect success')
                    return True

                time_end = time.time()
                if time_end-time_start > 10:
                    print('WiFi connect failed')
                    break 
                time.sleep(0.1)
        return False

    def get_current_ssid(self):
        _, result = self.run_command("iwgetid")
        if result != "":
            result = result.split(":")[1].strip().strip('"')
        return result
    
    def set_country(self, country):
        print("Setting country")
        _, result = self.run_command("wpa_cli -i wlan0 set country {}".format(country))
        result = result.strip()
        # print(result)
        # print(result != "OK")
        if result != "OK":
            print("Set country failed")
            return False
        _, result = self.run_command("wpa_cli -i wlan0 save_config")
        result = result.strip()
        if result != "OK":
            print("Save country config failed")
            return False
        self.run_command("sudo iw reg set {}".format(country))
        self.run_command("hash rfkill")
        self.run_command("rfkill unblock wifi")
        self.country = country
        print("Set country success")
        

    def write(self, country, ssid, psk):
        self.set_country(country)
        self.connect(ssid, psk)

def test():
    WiFi().write("CN", "MakerStarsHall_5G", "sunfounder")
    # status, result = WiFi().run_command("iwgetid")
    # result = result.split(":")[1].strip().strip('"')
    # print(result)
if __name__ == "__main__":
    test()

