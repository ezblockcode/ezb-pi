from ezblock.basic import _Basic_class
import re
import time
# re-正则表达式
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
 
	def write(self, ssid, psk, country="CN"):                                   # 传入wifi名称、密码和国家
		message = self.message.format(country, ssid, psk)                       # 将名称、密码和国家传入到message中
		with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:         # 将message传入到树莓派的wifi配置文件中
			f.write(message)
			
		self.run_command("wpa_cli -i wlan0 reconfigure")     # 运行树莓派（linux）命令，重启wifi

		self.run_command("sudo ifconfig wlan0 down && sudo ifconfig wlan0 up")	# 重启系统wifi配置，可以不用这条命令，但是切换wifi需要一定时间，需要运行这条命令的时间，不然会误判，所以最好留着
 
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
		time_start = time.time()												# 记录开始时间
		while True:																# 最多循环5秒，在此期间检测到WiFi连接成功就返回“success”，否则5秒后返回“failed”
			status, output = self.run_command("ifconfig wlan0")					# 返回wifi连接的状态和输出的内容
			if re.search("inet", output):										# 从返回的内容中搜索是否有“inet”字样，有——连接成功
				return 'WiFi connect success'

			time_end = time.time()												# 记录此时的时间
			if time_end-time_start > 5:											# 超过5秒返回“failed”
				return 'WiFi connect failed'
def test():
	import time
	WiFi().write("MakerStarsHall", "sunfounder", "CN")
	print(WiFi().is_network_rpi())
if __name__ == "__main__":
	test()

