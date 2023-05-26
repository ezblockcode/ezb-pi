import os

# USER = os.popen("echo ${SUDO_USER:-$(who -m | awk '{ print $1 }')}").readline().strip()
USER = os.popen("ls -l /opt/ |grep ezblock | awk '{print $3}'").readline().strip()
USER_HOME = os.popen(f'getent passwd {USER} | cut -d: -f 6').readline().strip()
# print(f"user: {USER}")
# print(f"userhome: {USER_HOME}")
