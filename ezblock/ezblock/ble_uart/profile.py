import dbus

from .utils import *

class Profile(dbus.service.Object):
    PATH_BASE = '/org/bluez/example/profile'

    def __init__(self, bus, uuids):
        self.path = self.PATH_BASE
        self.bus = bus
        self.uuids = uuids
        dbus.service.Object.__init__(self, bus, self.path)

    def get_properties(self):
        return {
            GATT_PROFILE_INTERFACE: {
                'UUIDs': self.uuids,
            }
        }

    def get_path(self):
        return dbus.ObjectPath(self.path)

    @dbus.service.method(GATT_PROFILE_INTERFACE,
                        in_signature="",
                        out_signature="")
    def Release(self):
        print("Release")
        mainloop.quit()

    @dbus.service.method(DBUS_PROPERTIES_INTERFACE,
                         in_signature='s',
                         out_signature='a{sv}')
    def GetAll(self, interface):
        if interface != GATT_PROFILE_INTERFACE:
            raise InvalidArgsException()

        return self.get_properties[GATT_PROFILE_INTERFACE]
