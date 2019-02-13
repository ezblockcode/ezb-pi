# from tools.makeversionhdr import make_version_file
import sys, os


if len(sys.argv) == 1:
    with open("./raspberrypi/raspberrypi/version.py", "r") as f:
        VERSION = f.read().strip().split('=')[1].strip().strip()
    versionlist = VERSION.replace('v', '').split('.')
    version = "v%s.%s.%s"%(versionlist[0], versionlist[1], int(versionlist[2])+1)
elif len(sys.argv) == 2:
    version = sys.argv[1]
else:
    print("\nUsage: python3 publish.py <version>\n\nExample:\n    python3 publish.py ")
    exit()

def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result

print("New version: %s"%(version))
# os.system("echo \"VERSION = \"%s\"\" > ./raspberrypi/raspberrypi/version.py"%version)
with open("./raspberrypi/raspberrypi/version.py", "w") as f:
    f.write('VERSION = "%s"'%version)
os.system("git tag %s -m '%s'"%(version, version))
