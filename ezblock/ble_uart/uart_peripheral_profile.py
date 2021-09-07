import sys
import uuid
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic, TestEncryptCharacteristic
from example_gatt_server import register_app_cb, register_app_error_cb
import threading
import time
from optparse import OptionParser
import bluezutils
from agent import Agent
from filedb import fileDB
 
BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
GATT_PROFILE_IFACE =           'org.bluez.GattProfile1'
DBUS_PROP_IFACE =              'org.freedesktop.DBus.Properties'
UART_SERVICE_UUID =            'FFF0'
UART_TXRX_CHARACTERISTIC_UUID ='FFF1'
LOCAL_NAME =                   'ezb-test'
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
        self.PropertiesChanged(GATT_CHRC_IFACE, {'Value': value}, [])
 
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

    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
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

class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = 'org.freedesktop.DBus.Error.InvalidArgs'


class Profile(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/profile'

    def __init__(self, bus, uuids):
        self.path = self.PATH_BASE
        self.bus = bus
        self.uuids = uuids
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_PROFILE_IFACE: {
                'UUIDs': self.uuids,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(GATT_PROFILE_IFACE,
                        in_signature="",
                        out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_PROFILE_IFACE:
            raise InvalidArgsException()

        return self.get_properties[GATT_PROFILE_IFACE]

 
class BLE_UART():
    def __init__(self):
        self.init()
        self.run_flag = True
        self.thread.start()
        self.read_buf = ""
    
    def append_read_buf(self, value):
        self.read_buf += value

    def init(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        adapter = self.find_adapter(bus)
        
        capability = "NoInputNoOutput"
        profile_uuid = str(uuid.uuid4())
        agent_path = "/test/agent"
        profile_path = bluezutils.find_adapter().object_path
     
        print(adapter)
        if not adapter:
            print('BLE adapter not found')
            return
    
        service_manager = dbus.Interface(
                                    bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    GATT_MANAGER_IFACE)
        ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)
        agent_manager = dbus.Interface(
                                    bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez"),
                                    "org.bluez.AgentManager1")

        profile = Profile(bus, [profile_uuid])
 
        app = UartApplication(bus, self.append_read_buf)
        adv = UartAdvertisement(bus, 0)
        agent = Agent(bus, agent_path)

        self.send_tx = app.send_tx
    
        self.mainloop = GLib.MainLoop()
    
        app.add_profile(profile)
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=register_app_cb,
                                            error_handler=register_app_error_cb)
        ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)
        agent_manager.RegisterAgent(agent_path, capability)
        print("Agent registered")
     
        self.thread = threading.Thread(target=self.mainloop.run)

    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()
        for o, props in objects.items():
            if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
                return o
            print('Skip adapter:', o)
        return None
 
    def read(self, num=None):
        if num == None:
            result = self.read_buf
        else:
            result = self.read_buf[:num]
        return result


    def flush(self):
        self.read_buf = ""

    def writechar(self, data):
        self.send_tx(data)
    
    def write(self, data):
        self.send_tx(data)

    def inWaiting(self):
        return len(self.read_buf)
    
def temp():
    fb = fileDB()
    uart = BLE_UART()
    while True:
        temp_buff = uart.read()
        if uart.inWaiting():
            print(temp_buff)
            if temp_buff == "get name":
                name = fb.get('name')
                if name != None:
                    uart.write(name)
                else:
                    uart.write("do not have setted name!")
            elif temp_buff == 'get type':
                dv_type = fb.get('type')
                if dv_type != None:
                    uart.write(dv_type)
                else:
                    uart.write("do not have setted type!")
            
              
        uart.flush()    
        time.sleep(0.01)

def test():
    uart = BLE_UART()
    while True:
        temp_buff = uart.read()
        if uart.inWaiting():
            print(temp_buff)
            uart.write("hello")
        # uart.flush()  
        uart.flush()    
        time.sleep(0.01)
        
test()
        
    
