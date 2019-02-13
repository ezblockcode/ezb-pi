# from tools.makeversionhdr import make_version_file
import sys
version = sys.argv[1]

def run_command(cmd=""):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    # print(result)
    # print(status)
    return status, result

run_command("echo 'VERSION = %s' > ./raspberrypi/raspberrypi/version.py"%version)

run_command("git tag %s -m '%s'"%(version, version))
