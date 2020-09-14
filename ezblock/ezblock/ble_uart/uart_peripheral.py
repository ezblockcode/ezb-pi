import sys
import dbus, dbus.mainloop.glib
from gi.repository import GLib
from .example_advertisement import Advertisement
from .example_advertisement import register_ad_cb, register_ad_error_cb
from .example_gatt_server import Service, Characteristic
from .example_gatt_server import register_app_cb, register_app_error_cb
import threading
 
BLUEZ_SERVICE_NAME =           'org.bluez'
DBUS_OM_IFACE =                'org.freedesktop.DBus.ObjectManager'
LE_ADVERTISING_MANAGER_IFACE = 'org.bluez.LEAdvertisingManager1'
GATT_MANAGER_IFACE =           'org.bluez.GattManager1'
GATT_CHRC_IFACE =              'org.bluez.GattCharacteristic1'
# UART_SERVICE_UUID =            '6e400001-b5a3-f393-e0a9-e50e24dcca9e'
# UART_RX_CHARACTERISTIC_UUID =  '6e400002-b5a3-f393-e0a9-e50e24dcca9e'
# UART_TX_CHARACTERISTIC_UUID =  '6e400003-b5a3-f393-e0a9-e50e24dcca9e'
UART_SERVICE_UUID =            'FFF0'
UART_RX_CHARACTERISTIC_UUID =  'FFF1'
UART_TX_CHARACTERISTIC_UUID =  'FFF2'
LOCAL_NAME =                   'ezb-raspad'
mainloop = None
 
class TxCharacteristic(Characteristic):
    def __init__(self, bus, index, service):
        Characteristic.__init__(self, bus, index, UART_TX_CHARACTERISTIC_UUID,
                                ['notify'], service)
        self.notifying = False
        GLib.io_add_watch(sys.stdin, GLib.IO_IN, self.on_console_input)
 
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
 
class RxCharacteristic(Characteristic):
    def __init__(self, bus, index, service, on_write_value):
        Characteristic.__init__(self, bus, index, UART_RX_CHARACTERISTIC_UUID,
                                ['write'], service)
 
    def WriteValue(self, value, options):
        result = bytearray(value).decode()
        on_write_value(result)
        print('remote: {}'.format(result))
 
class UartService(Service):
    def __init__(self, bus, index, on_write_value):
        Service.__init__(self, bus, index, UART_SERVICE_UUID, True)
        self.txc = TxCharacteristic(bus, 0, self)
        self.rxc = RxCharacteristic(bus, 1, self, on_write_value)
        self.add_characteristic(self.txc)
        self.add_characteristic(self.rxc)
        self.send_tx = self.txc.send_tx
 
class Application(dbus.service.Object):
    def __init__(self, bus):
        self.path = '/opt/ezblock'
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

    def init(self):
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        adapter = self.find_adapter(bus)
        if not adapter:
            print('BLE adapter not found')
            return
    
        service_manager = dbus.Interface(
                                    bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    GATT_MANAGER_IFACE)
        ad_manager = dbus.Interface(bus.get_object(BLUEZ_SERVICE_NAME, adapter),
                                    LE_ADVERTISING_MANAGER_IFACE)
    
        app = UartApplication(bus, self.append_read_buf)
        adv = UartAdvertisement(bus, 0)

        self.send_tx = app.send_tx
    
        self.mainloop = GLib.MainLoop()
    
        service_manager.RegisterApplication(app.get_path(), {},
                                            reply_handler=register_app_cb,
                                            error_handler=register_app_error_cb)
        ad_manager.RegisterAdvertisement(adv.get_path(), {},
                                        reply_handler=register_ad_cb,
                                        error_handler=register_ad_error_cb)
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
 
    def read(self, num):
        result = self.read_buf[:num]
        self.read_buf = self.read_buf[num:]
        return 

    def flush(self):
        self.read_buf = ""

    def writechar(self, data):
        self.send_tx(data)
    
    def write(self, data):
        self.send_tx(data)

    def inWaiting(self):
        return len(self.read_buf) > 0
