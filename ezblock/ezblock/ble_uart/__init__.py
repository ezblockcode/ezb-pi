#!/usr/bin/python3

import uuid
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from .advertisement import Advertisement
from .gatt_server import Service, Characteristic
from .agent import Agent
from .profile import Profile
import threading
import time
from .utils import *
from ..utils import log


def _log(msg:str, location='BLE', end='\n', flush=False, timestamp=True):
    log(msg, location, end='\n', flush=False, timestamp=True)


UART_SERVICE_UUID =            'FF00' # 'FF00'
UART_TXRX_CHARACTERISTIC_UUID ='FFF1'
LOCAL_NAME =                   'ezb-Raspberry' # 'ezb-Raspberry'
mainloop = None


class TxRxCharacteristic(Characteristic):
    def __init__(self, bus, index, service, on_write_value):
        Characteristic.__init__(self, bus, index, UART_TXRX_CHARACTERISTIC_UUID,
                                ['notify', 'write'], service)
        self.notifying = False
        # GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)
        self.on_write_value = on_write_value

    # def on_console_input(self, fd, condition):
    #     time.sleep(0.1)
    #     s = fd.readline()
    #     if s.isspace():
    #         pass
    #     else:
    #         self.send_tx(s)
    #     return True
 
    def send_tx(self, s):
        if not self.notifying:
            return
        value = []
        for c in s:
            value.append(dbus.Byte(c.encode()))
        if len(value) != 0:
            self.PropertiesChanged(GATT_CHARACTERISTIC_INTERFACE, {'Value': value}, [])
        # else:
        #     _log("send_tx: Skip. emply value")
 
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
        _log('BLE_UART: remote: %s'%result.encode())

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
    def __init__(self, bus, index,name=LOCAL_NAME):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(UART_SERVICE_UUID)
        self.add_local_name(name)
        self.include_tx_power = True

class BLE_UART():
    def __init__(self,name):
        self.ble_name = name
        self.read_buf = ""
        self.adv = None
        self.adv_manager = None
        self.connected = 0
        self.adv_status = False


        self.init(self.ble_name)
       

    def append_read_buf(self, value):
        self.read_buf += value


    def init(self, name):
        capability = "NoInputNoOutput"
        profile_uuid = str(uuid.uuid4())
        agent_path = "/test/agent"

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

        # if not adapter:
        #     _log('BLE: adapter not found')
        #     return

        # add signal callback
        bus.add_signal_receiver(self.properties_changed,
                    dbus_interface = DBUS_PROPERTIES_INTERFACE,
                    signal_name = "PropertiesChanged",
                    path_keyword = "path")

        bus.add_signal_receiver(self.interfaces_added,
                dbus_interface = DBUS_OBJECT_MANAGER_INTERFACE,
                signal_name = "InterfacesAdded")


        service_manager = dbus.Interface(
                                    bus.get_object(SERVICE_NAME, adapter),
                                    GATT_MANAGER_INTERFACE)
        self.adv_manager = dbus.Interface(bus.get_object(SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_INTERFACE)
        agent_manager = dbus.Interface(
                                    bus.get_object(SERVICE_NAME, "/org/bluez"),
                                    "org.bluez.AgentManager1")

        profile = Profile(bus, [profile_uuid])
 
        app = UartApplication(bus, self.append_read_buf)
        self.adv = UartAdvertisement(bus, 0,name)
        agent = Agent(bus, agent_path)

        self.send_tx = app.send_tx
    
        self.mainloop = GLib.MainLoop()
    
        app.add_profile(profile)
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=self.register_app_cb,
                                            error_handler=self.register_app_error_cb)
        self.start_advertising()
        agent_manager.RegisterAgent(agent_path, capability)
        _log("BLE: Agent registered")
     
        self.thread = threading.Thread(target=self.mainloop.run)
        self.thread.start()


    def register_app_cb(self):
        _log('BLE: GATT application registered')

    def register_app_error_cb(self, error):
        _log('BLE: Failed to register application: ' + str(error))
        self.mainloop.quit()

    def register_ad_cb(self):

        _log('BLE: Advertisement registered OK')

    def register_ad_error_cb(self, error):
        _log('BLE: Failed to register advertisement: ' + str(error))
        self.mainloop.quit()
        

    def start_advertising(self):
        try:
            # we're only registering one advertisement object so index (arg2) is hard coded as 0
            self.adv_manager.RegisterAdvertisement(self.adv.get_path(), {},
                                    reply_handler=self.register_ad_cb,
                                    error_handler=self.register_ad_error_cb)
            _log("Registering advertisement OK ：%s"%self.adv.get_path())
            self.adv_status = True
        except Exception as e:
            _log('start_advertising failed: %s'%e)


    def stop_advertising(self):
        try:
            if self.adv_manager != None and self.adv_status:
                self.adv_manager.UnregisterAdvertisement(self.adv.get_path())
                self.adv_status = False
                _log('BLE: Advertisement unregistered OK')
            else:
                _log('BLE: Advertisement unregistered skip')
        except Exception as e:
            _log('BLE: Failed to unregister advertisement:\n %s'%e)
            

    # connected_status callback
    def properties_changed(self, interface, changed, invalidated, path):
        if (interface == DEVICE_INTERFACE):
            if ("Connected" in changed):
                # self.set_connected_status(changed["Connected"])
                _log('ble properties_changed: %s'%self.connected)
                self.connected = changed["Connected"]

    # connected_status callback
    def interfaces_added(self, path, interfaces):
        # global connected
        if DEVICE_INTERFACE in interfaces:
            properties = interfaces[DEVICE_INTERFACE]
            if "Connected" in properties:
                # self.set_connected_status(properties["Connected"])
                _log('ble interfaces_added: %s'%self.connected)
                self.connected = properties["Connected"]


    def set_connected_status(self, status):
        if (status == 1):
            _log("BLE connected")
            self.connected = 1
            self.stop_advertising()
        else:
            _log("BLE disconnected")
            self.connected = 0
            if self.adv_status == False:
                self.start_advertising()




