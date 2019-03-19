from ezblock.basic import _Basic_class

class WiFi(_Basic_class):
    # def __init__(self):
    #     pass
    message = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country="{}"
network={{
    ssid="{}"
    psk="{}"
    key_mgmt=WPA-PSK 
}}"""
 
    def write(self, ssid, psk, country="CN"):
        message = self.message.format(country, ssid, psk)
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
            f.write(message)
        self.run_command("sudo ifconfig wlan0 down;sudo ifconfig wlan0 up")

    def is_network(self, count=2, test_host="google.com"):
        status, output = self.run_command("ping -c 2 {}".format(test_host))
        # print("ping status: {}\noutput: {}".format(status, output))
        if status == 0:
            return True
        else:
            return False
def test():
    import time
    WiFi().write("MakerStarsHall", "sunfounder", "CN")
    while True:
        status = WiFi().is_network()
        print(status)
        time.sleep(1)
        if status:
            break
if __name__ == "__main__":
    test()

