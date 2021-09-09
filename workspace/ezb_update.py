import requests
import json
from configparser import ConfigParser
import time

def run_command(cmd):
    import subprocess
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    result = p.stdout.read().decode('utf-8')
    status = p.poll()
    return status, result

def log(msg,module_name=' ',tag='Update'):
    msg = "{} [{}] [{}] {}".format(module_name,time.asctime(),tag, msg)
    run_command("echo {} >> /opt/ezblock/log".format(msg))
    print(msg)

class Ezbupdate(object):

    def __init__(self,url = 'http://ezblock.cc/fileUpload/'):

        self.config = ConfigParser()
        self.file_address = "/opt/ezblock/ezb-info.ini"
        self.url = url
        

    def get_status(self):
        _,index =  self.check_version()
        if index > 0:
            return True
        else:
            return False

    def check_version(self):
        result = {}
        version_list = []
       
        # Read the local version information
        self.config.read(self.file_address)
        
        # Get information from the server
        for i in range(1,6,1):
            try:               
                r = requests.get(self.url+'/version.json',timeout=5)               
                if r.status_code != 200:
                    log('Failed to connect server.Reconnect ... %s'% i)
                else:
                    log('Connection succeeded.')
                    break
                log('requests status_code : %s' % r.status_code)
            except Exception as e:
                log('\n[Exception] requests.get() : %s\n'% e)  
        else:
            log('\nFailed to connect server.Please try again later.\n')
            return False

        # Read the version information returned by the server
        result = json.loads(r.text)
        version_list = result.get('version')
        latest_version = version_list[0]
        log('latest version : %s'% latest_version)        
        # Read the local version information in flie '/opt/ezblock/ezb-info.ini'
        version_message = dict(self.config.items("message"))
        if version_message['version'] == None or version_message['version'] == '':
            log("Failed to read the version information.Please try again,or check if there is the value of version "
                + "\nin the \'/opt/ezblock/ezb-info.ini\' file"
                + "\n [message] \n version =  \n ")
            return False
        else: 
            local_version = version_message['version']
            log('local version : %s'% local_version)

        # Determine how many versions are different based on the position of the version in the column
        try:
            index = version_list.index(local_version)
        except Exception as e:
            log("Incorrect version information in the \'/opt/ezblock/ezb-info.ini\' file.")
            log('\033[1;35mlog: \033[0m\n%s'% e)
            return False

        if index == 0:
            log('\nAlready the latest version.')    
            return list([0]),index  
        else:
            return list(version_list),index

    def update(self):
        # check version return list of all versions and the index of local version in the list
        version_list,index = self.check_version()

        if index == 0:
            log('\nAlready the latest version.')    
            return False      
        else:
            # Update one by one from the old version to the new version
            for i in range(index-1,-1,-1):
                # Download
                log("Download the %s version update package ..."% version_list[i])
                download_cmd = "sudo wget -c " + self.url + str(version_list[i])+ ".zip" + " -O /opt/ezblock/" + str(version_list[i]) + ".zip"
                for j in range(1,6,1):
                    try:
                        cmd_status, cmd_result = run_command(download_cmd) 
                        if cmd_status != 0:
                            log('Download failed.Retrying now ...  %s'% j)
                        else:
                            log('Download completed')
                            break
                    except Exception as e:
                        log('\n[Exception] : %s\n'% e)  
                else:
                    log('Download failed.Please check the network and try again later.')
                    log('\033[1;35mlog: \033[0m\n%s'% cmd_result)
                    run_command("sudo rm /opt/ezblock/"+str(version_list[i])+".zip")
                    return False

                # Unpacking
                log('Unpacking update package ....')       
                unzip_cmd = "sudo unzip -o /opt/ezblock/" + str(version_list[i]) + '.zip' + " -d /opt/ezblock/" 
                try:
                    cmd_status, cmd_result = run_command(unzip_cmd)
                    if cmd_status != 0:
                        log('Unpacking error.Please try again.')
                        log('\033[1;35mlog: \033[0m\n%s'% cmd_result)
                        return False 
                    else:
                        log('Unzip completed')
                except Exception as e:
                    log('\n[Exception] : %s\n'% e)    

                # Install
                log('Installing the update package of version %s ...'% version_list[i])
                install_cmd = "sudo python3 /opt/ezblock/" + str(version_list[i]) + "/" + "ezb-update.py"
                try:
                    cmd_status, cmd_result = run_command(install_cmd)
                    if cmd_status != 0:
                        log('Install error.Please try again.')
                        log('\033[1;35mlog: \033[0m\n%s'% cmd_result)
                        return False
                    else:
                        log('Install completed')
                except Exception as e:
                    log('\n[Exception] : %s\n'% e) 

                # Update version information   
                self.config.set('message', 'version',version_list[i])
                try:
                    with open(self.file_address, 'w') as configfile:
                        self.config.write(configfile)
                    log('Successfully updated version information')    
                except Exception as e:
                    log('\n[Exception] : %s\n'% e) 
                    return False

                # Clean up update package
                log('Cleaning up the update package of version %s ...'% version_list[i])
                clean_cmd = "sudo rm -rf /opt/ezblock/" + str(version_list[i]) + " " + "/opt/ezblock/"+ str(version_list[i]) + ".zip"
                try:
                    cmd_status, cmd_result = run_command(clean_cmd)
                    if cmd_status != 0:
                        log('Failed to clean up the update package.Please clean up manually.')
                        log('\033[1;35m log: \033[0m\n%s'% cmd_result)
                    else:
                        log('Cleaned up successfully')
                except Exception as e:
                    log('\n[Exception] : %s\n'% e)    

        # Update completed
        log("Successfully updated.Have fun with it.")
        # Reboot
        log("Please restart the device for the changes to take effect.")          

        return True

if __name__ == "__main__":
    ezb = Ezbupdate()
    ezb.get_status()
    # ezb.update()
