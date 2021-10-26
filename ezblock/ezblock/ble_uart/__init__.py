import sys
import uuid
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from .advertisement import Advertisement
from .gatt_server import Service, Characteristic, TestEncryptCharacteristic
from .agent import Agent
from .profile import Profile
import threading
import time
from os import system as run_command
from .utils import *

UART_SERVICE_UUID =            'FF00' # 'FF00' 
UART_TXRX_CHARACTERISTIC_UUID ='FFF1'
LOCAL_NAME =                   'ezb-Raspberry' # 'ezb-Raspberry'
mainloop = None 
 
class TxRxCharacteristic(Characteristic):
    def __init__(self, bus, index, service, on_write_value):
        Characteristic.__init__(self, bus, index, UART_TXRX_CHARACTERISTIC_UUID,
                                ['notify', 'write'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)
        self.on_write_value = on_write_value
 
    def on_console_input(self, fd, condition):
        s = fd.readline()
        if s.isspace():
            pass
        else:
            self.send_tx(s)
        return True
 
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        if len(value) != 0:
            self.PropertiesChanged(GATT_CHARACTERISTIC_INTERFACE, {'Value': value}, [])
        else:
            self.log("send_tx: Skip. emply value")
 
    def StartNotify(self):
        if self.notifying:
            return
        self.notifying = True
 
    def StopNotify(self):
        if not self.notifying:
            return
        self.notifying = False
 
    def WriteValue(self, value, options):
        result = bytearray(value).decode()
        self.on_write_value(result)
        print('remote: {}'.format(result))

class UartService(Service):
    def __init__(self, bus, index, on_write_value):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.txrxc = TxRxCharacteristic(bus, 0, self, on_write_value)
        # self.encryptc = TestEncryptCharacteristic(bus, 1, self)
        self.add_characteristic(self.txrxc)
        # self.add_characteristic(self.encryptc)
        self.send_tx = self.txrxc.send_tx
 
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/org/bluez/hci0'
        self.services = []
        self.profiles = []
        dbus.service.Object.__init__(self, bus, self.path)
 
    def get_path(self):
        return dbus.ObjectPath(self.path)
 
    def add_service(self, service):
        self.services.append(service)
 
    def add_profile(self, profile):
        self.profiles.append(profile)

    @dbus.service.method(DBUS_OBJECT_MANAGER_INTERFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
                
        for profile in self.profiles:
            response[profile.get_path()] = profile.get_properties()

        return response
 
class UartApplication(Application):
    def __init__(self, bus, on_write_value):
        Application.__init__(self, bus)
        self.us = UartService(bus, 0, on_write_value)
        self.add_service(self.us)
        self.send_tx = self.us.send_tx
 
class UartAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(LOCAL_NAME)
        self.include_tx_power = True

class BLE_UART():
    def __init__(self):
        self.init()
        self.run_flag = True
        self.thread.start()
        self.read_buf = ""
    
    def log(self, msg):
        msg = "BLE_UART [{}] [DEBUG] {}".format(time.asctime(), msg)
        run_command("echo {} >> /opt/ezblock/log".format(msg))
        print(msg)

    def append_read_buf(self, value):
        self.read_buf += value

    def init(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        for _ in range(10):
            adapter = find_adapter(bus)
            if adapter != None:
                break
            else:
                time.sleep(1)
        else:
            raise Exception("Bluetooth adapter not found")
        
        capability = "NoInputNoOutput"
        profile_uuid = str(uuid.uuid4())
        agent_path = "/test/agent"
     
        if not adapter:
            self.log('BLE adapter not found')
            return
    
        service_manager = dbus.Interface(
                                    bus.get_object(SERVICE_NAME, adapter),
                                    GATT_MANAGER_INTERFACE)
        ad_manager = dbus.Interface(bus.get_object(SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_INTERFACE)
        agent_manager = dbus.Interface(
                                    bus.get_object(SERVICE_NAME, "/org/bluez"),
                                    "org.bluez.AgentManager1")

        profile = Profile(bus, [profile_uuid])
 
        app = UartApplication(bus, self.append_read_buf)
        adv = UartAdvertisement(bus, 0)
        agent = Agent(bus, agent_path)

        self.send_tx = app.send_tx
    
        self.mainloop = GLib.MainLoop()
    
        app.add_profile(profile)
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=self.register_app_cb,
                                            error_handler=self.register_app_error_cb)
        ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                        reply_handler=self.register_ad_cb,
                                        error_handler=self.register_ad_error_cb)
        agent_manager.RegisterAgent(agent_path, capability)
        self.log("Agent registered")
     
        self.thread = threading.Thread(target=self.mainloop.run)

    def register_app_cb(self):
        self.log('GATT application registered')

    def register_app_error_cb(self, error):
        self.log('Failed to register application: ' + str(error))
        self.mainloop.quit()

    def register_ad_cb(self):
        self.log('Advertisement registered')

    def register_ad_error_cb(self, error):
        self.log('Failed to register advertisement: ' + str(error))
        self.mainloop.quit()
