import subprocess
import os

class WiFi(object):
    # def __init__(self):
    #     pass
    
    def write(self, country="CN", ssid, key):
        message = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdevupdate_config=1\ncountry="+ country +"\nnetwork={\n\tssid=\'"+ ssid +"\'\n\tpsk=\'" + key +"\'\n\tkey_mgmt=WPA-PSK\n\t}"

        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as f:
            f.write(message)
def test():
    WiFi().write("CN", "abc", "88888888")

if __name__ == "__main__":
    test()

