import requests
import json
from configparser import ConfigParser
import time
import sys
from ezblock.user_info import USER, USER_HOME
from ezblock.utils import log

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result


def _log(msg:str, location='Update', end='\n', flush=False, timestamp=True, color=''):
    log(msg, location=location, end=end, flush=flush, timestamp=timestamp, color=color)


class Ezbupdate(object):

    SERVER_URL = 'http://ezblock.cc/fileUpload/'
    VERSION_URL = '/version33.json'

    def __init__(self,url=SERVER_URL):
        self.config = ConfigParser()
        self.file_address = "/opt/ezblock/ezb-info.ini"
        self.url = url
        
    def get_status(self, _app_version:str):
        result = self.check_version(_app_version)
        if result == False:
            return False
        else:
            if result[1] > 0:
                return True
            else:
                return False

    def check_version(self, _app_version:str):
        result = {}
        version_list = []
       
        # Read the local version information
        self.config.read(self.file_address)
        
        # Get information from the server
        for i in range(1,6,1):
            try:
                r = requests.get(self.SERVER_URL+self.VERSION_URL,timeout=5)
                if r.status_code != 200:
                    _log('Failed to connect server. Reconnect ... %s'% i)
                else:
                    _log('Connection succeeded.')
                    break
                _log('requests status_code: %s' % r.status_code)
            except Exception as e:
                _log('\n[Exception] requests.get(): %s\n'% e)
        else:
            _log('\nFailed to connect server. Please try again later.\n')
            return False

        # Read the version information returned by the server
        result = json.loads(r.text)
        version_list = result.get('version')
        _log('version_list: %s'%version_list)
        latest_version = version_list[0]
        _log('latest version: %s'%latest_version)
        # Read the local version information in flie '/opt/ezblock/ezb-info.ini'
        version_message = dict(self.config.items("message"))
        if version_message['version'] == None or version_message['version'] == '':
            _log("Failed to read the version information. Please try again,or check if there is the value of version "
                + "\nin the \'/opt/ezblock/ezb-info.ini\' file"
                + "\n [message] \n version =  \n ")
            return False
        else:
            local_version = version_message['version']
            _log('local version: %s'% local_version)
            _log('app version: %s'% _app_version)

        try:
            # Determine how many versions are different based on the position of the version in the column
            index = 0
            updatable_version_list = []

            # In python, you can directly use strings to compare the version size
            for _compare_version in version_list:
                if _compare_version[0] > local_version:
                        index += 1
                else:
                    break

            if index == 0:
                _log('\n\tAlready the latest version.')
                return None, 0
            else:
                for i in range(index-1,-1,-1):
                    if version_list[i][1] <= _app_version:
                        updatable_version_list.append(version_list[i][0])
                    else:
                        _log("minimum compatible version: %s"%_compare_version[1])
                        _log("\033[1;35m%s\033[0m"%"There are some updates that are not compatible with the app version.")
                        break
                _log("updatable_version_list: %s"%updatable_version_list)
                return updatable_version_list, len(updatable_version_list)

        except Exception as e:
            _log('\033[1;35mlog: \033[0m\n\t%s'% e)
            return False

    def update(self, _app_version:str):
        # check version return list of all versions and the index of local version in the list
        updatable_version_list, index = self.check_version(_app_version)

        if index == 0:
            return False
        else:
            # Update one by one from the old version to the new version
            for i in range(index):
                # Download
                _log("Download the %s version update package ..."% updatable_version_list[i])
                download_cmd = "sudo wget -c " + self.url + str(updatable_version_list[i])+ ".zip" + " -O /opt/ezblock/" + str(updatable_version_list[i]) + ".zip"
                for j in range(1,6,1):
                    try:
                        cmd_status, cmd_result = run_command(download_cmd)
                        if cmd_status != 0:
                            _log('Download failed.Retrying now ...  %s'% j)
                        else:
                            _log('Download completed')
                            break
                    except Exception as e:
                        _log('\n[Exception] : %s\n'% e)
                else:
                    _log('Download failed.Please check the network and try again later.')
                    _log('\033[1;35merror: \033[0m\n\t%s'% cmd_result)
                    run_command("sudo rm /opt/ezblock/"+str(updatable_version_list[i])+".zip")
                    return False

                # Unpacking
                _log('Unpacking update package ....')
                unzip_cmd = "sudo unzip -o /opt/ezblock/" + str(updatable_version_list[i]) + '.zip' + " -d /opt/ezblock/"
                try:
                    cmd_status, cmd_result = run_command(unzip_cmd)
                    if cmd_status != 0:
                        _log('Unpacking error.Please try again.')
                        _log('\033[1;35mlog: \033[0m\n%s'% cmd_result)
                        return False
                    else:
                        _log('Unzip completed')
                except Exception as e:
                    _log('\n[Exception] : %s\n'% e)

                # Install
                _log('Installing the update package of version %s ...'% updatable_version_list[i])
                install_cmd = "sudo python3 /opt/ezblock/" + str(updatable_version_list[i]) + "/" + "ezb-update.py"
                try:
                    cmd_status, cmd_result = run_command(install_cmd)
                    if cmd_status != 0:
                        _log('Install error.Please try again.')
                        _log('\033[1;35mlog: \033[0m\n%s'% cmd_result)
                        return False
                    else:
                        _log('Install completed')
                except Exception as e:
                    _log('\n[Exception] : %s\n'% e)

                # clean install egg-info
                _log("cleaning egg-info ...")
                clean_cmd = f"sudo rm -rf {USER_HOME}/ezb-pi//ezblock/ezblock.egg-info"
                    
                # Update version information
                self.config.set('message', 'version',updatable_version_list[i])
                try:
                    with open(self.file_address, 'w') as configfile:
                        self.config.write(configfile)
                    _log('Successfully updated version information')
                except Exception as e:
                    _log('\n[Exception] : %s\n'% e)
                    return False

                # Clean up update package
                _log('Cleaning up the update package of version %s ...'% updatable_version_list[i])
                clean_cmd = "sudo rm -rf /opt/ezblock/" + str(updatable_version_list[i]) + " " + "/opt/ezblock/"+ str(updatable_version_list[i]) + ".zip"
                try:
                    cmd_status, cmd_result = run_command(clean_cmd)
                    if cmd_status != 0:
                        _log('Failed to clean up the update package.Please clean up manually.')
                        _log('\033[1;35m log: \033[0m\n%s'% cmd_result)
                    else:
                        _log('Cleaned up successfully')
                except Exception as e:
                    _log('\n[Exception] : %s\n'% e)

        # Update completed
        _log("Successfully updated. Have fun with it.")
        # Reboot
        _log("Please restart the device for the changes to take effect.")

        return True

if __name__ == "__main__":
    ezb = Ezbupdate()
    result = ezb.get_status("3.2.15")
    print('Has update ? : %s'%result)
    # result = ezb.update("3.2.15")
    # print('update result : %s'%result)
