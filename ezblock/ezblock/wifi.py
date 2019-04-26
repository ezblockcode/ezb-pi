from ezblock.basic import _Basic_class
from ezblock.utils import print
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
 
	def write(self, ssid, psk, country="CN"):                                   # 传入wifi名称、密码和国家
		print("connecting to \"{}\" ...".format(ssid))
		message = self.message.format(country, ssid, psk)                       # 将名称、密码和国家传入到message中
		with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:         # 将message传入到树莓派的wifi配置文件中
			f.write(message)
		
		for i in range(6):
			if i != 0:
				print('Timeout, retry ({})...'.format(i))
			self.run_command("wpa_cli -i wlan0 reconfigure")     # 运行树莓派（linux）命令，重启wifi
			time.sleep(1)
			time_start = time.time()
			while True:																# 最多循环5秒，在此期间检测到WiFi连接成功就返回“success”，否则5秒后返回“failed”
				# result = self.run_command("sudo ifconfig wlan0")
				_, output = self.run_command("hostname -I")							# 返回IP地址
				output = output.strip().strip()
				if output != "":
					print("IP: %s" %output)
					print('WiFi connect success')
					return True

				time_end = time.time()												# 记录此时的时间
				if time_end-time_start > 10:										# 超过10秒返回“failed”
					print('WiFi connect failed')
					break 
				time.sleep(0.1)
		return False

def test():
	WiFi().write("MakerStarsHall", "sunfounder", "CN")
if __name__ == "__main__":
	test()

