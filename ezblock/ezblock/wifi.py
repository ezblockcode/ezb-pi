from ezblock.basic import _Basic_class
import re
import time

class WiFi(_Basic_class):
	# def __init__(self):
	#     pass
	message = """
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country={}
network={{
	ssid="{}"
	psk="{}"
	key_mgmt=WPA-PSK 
}}"""
 
	def write(self, ssid, psk, country="CN"):
		message = self.message.format(country, ssid, psk)
		with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
			f.write(message)
			
		self.run_command("wpa_cli -i wlan0 reconfigure")

		self.run_command("sudo ifconfig wlan0 down && sudo ifconfig wlan0 up")	# 可以不用这条命令，但是切换wifi需要一定时间，需要运行这条命令的时间，不然会误判，所以最好留着
 
	# 不用这个方法
	def is_network(self, count=2, test_host="google.com"):
		status, output = self.run_command("ping -c 2 {}".format(test_host))
		# print("ping status: {}\noutput: {}".format(status, output))
		if status == 0:
			return True
		else:
			return False

	def is_network_rpi(self):
		print("connecting...")
		time_start = time.time()
		while True:
			status, output = self.run_command("ifconfig wlan0")
			if re.search("inet", output):
				return 'WiFi connect success'

			time_end = time.time()
			if time_end-time_start > 5:
				return 'WiFi connect failed'
def test():
	import time
	WiFi().write("MakerStarsHall", "sunfounder", "CN")
	print(WiFi().is_network_rpi())
if __name__ == "__main__":
	test()

