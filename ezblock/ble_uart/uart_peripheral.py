import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from example_advertisement import Advertisement
from example_advertisement import register_ad_cb, register_ad_error_cb
from example_gatt_server import Service, Characteristic, Descriptor
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
        self.add_descriptor(UartDescriptor(bus, 0, self))
 
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
 
class UartDescriptor(Descriptor):
    TEST_DESC_UUID = '12345678-1234-5678-1234-56789abcdef2'

    def __init__(self, bus, index, characteristic):
        Descriptor.__init__(
                self, bus, index,
                self.TEST_DESC_UUID,
                ['notify', 'write'],
                characteristic)

    def ReadValue(self, options):
        return [
                dbus.Byte('U'), dbus.Byte('A'), dbus.Byte('R'), dbus.Byte('T')
        ]

class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/org/bluez/hci0'
        self.services = []
        dbus.service.Object.__init__(self, bus, self.path)
 
    def get_path(self):
        return dbus.ObjectPath(self.path)
 
    def add_service(self, service):
        self.services.append(service)
 
    @dbus.service.method(DBUS_OM_IFACE, out_signature='a{oa{sa{sv}}}')
    def GetManagedObjects(self):
        response = {}
        for service in self.services:
            response[service.get_path()] = service.get_properties()
            chrcs = service.get_characteristics()
            for chrc in chrcs:
                response[chrc.get_path()] = chrc.get_properties()
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
    
    def append_read_buf(self, value):
        self.read_buf += value

    def interfaces_added(self, path, interfaces):
        try:
            properties = interfaces["org.bluez.Device1"]
        except KeyError:
            return
        if properties["Connected"]:
            print(" Connect")
            self.ad_manager.UnregisterAdvertisement(self.adv.get_path())
	
    def properties_changed(self, interface, changed, invalidated, path):
        if "Connected" in changed:
            if changed["Connected"]:
                print("***have Connected!***")
                self.ad_manager.UnregisterAdvertisement(self.adv.get_path())
            else:
                print("One Disconnect")
                self.ad_manager.RegisterAdvertisement(self.adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)
            
    def init(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        # adapter = self.find_adapter(bus)
        adapter = "/org/bluez/hci1"
        
        capability = "NoInputNoOutput"
        path = "/test/agent"
     
        print(adapter)
        if not adapter:
            print('BLE adapter not found')
            return
    
        service_manager = dbus.Interface(
                                    bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    GATT_MANAGER_IFACE)
        self.ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)
    
        obj = bus.get_object(BLUEZ_SERVICE_NAME, "/org/bluez");
        # agent_manager = dbus.Interface(obj, "org.bluez.AgentManager1")
 
        app = UartApplication(bus, self.append_read_buf)
        self.adv = UartAdvertisement(bus, 0)
        # agent = Agent(bus, path)

        self.send_tx = app.send_tx
    
        self.mainloop = GLib.MainLoop()
        
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=register_app_cb,
                                            error_handler=register_app_error_cb)
        self.ad_manager.RegisterAdvertisement(self.adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)
        # agent_manager.RegisterAgent(path, capability)
        # print("Agent registered")
        # bus.add_signal_receiver(self.interfaces_added,
		# 	dbus_interface = "org.freedesktop.DBus.ObjectManager",
		# 	signal_name = "InterfacesAdded")

        # bus.add_signal_receiver(self.properties_changed,
        #         dbus_interface = "org.freedesktop.DBus.Properties",
        #         signal_name = "PropertiesChanged",
        #         arg0 = "org.bluez.Device1",
        #         path_keyword = "path")
     
        self.thread = threading.Thread(target=self.mainloop.run)

    def find_adapter(self, bus):
        remote_om = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, '/'),
                                DBUS_OM_IFACE)
        objects = remote_om.GetManagedObjects()
        for o, props in objects.items():
            # print("o:{0} props:{1}".format(o, props))
            if LE_ADVERTISING_MANAGER_IFACE in props and GATT_MANAGER_IFACE in props:
                return o
            # print('Skip adapter:', o)
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
        
    
