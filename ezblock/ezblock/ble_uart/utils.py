import dbus

SERVICE_NAME = "org.bluez"
AGENT_INTERFACE =                  SERVICE_NAME + ".Agent1"
AGENT_MANAGER_INTERFACE =          SERVICE_NAME + ".AgentManager1"
ADAPTER_INTERFACE =                SERVICE_NAME + ".Adapter1"
DEVICE_INTERFACE =                 SERVICE_NAME + ".Device1"
LE_ADVERTISING_MANAGER_INTERFACE = SERVICE_NAME + ".LEAdvertisingManager1"
LE_ADVERTISEMENT_INTERFACE =       SERVICE_NAME + ".LEAdvertisement1"
GATT_MANAGER_INTERFACE =           SERVICE_NAME + ".GattManager1"
GATT_SERVICE_INTERFACE =           SERVICE_NAME + ".GattService1"
GATT_CHARACTERISTIC_INTERFACE =    SERVICE_NAME + ".GattCharacteristic1"
GATT_PROFILE_INTERFACE =           SERVICE_NAME + ".GattProfile1"
GATT_DESCRIPTOR_INTERFACE =        SERVICE_NAME + ".GattDescriptor1"


DBUS_OBJECT_MANAGER_INTERFACE =  "org.freedesktop.DBus.ObjectManager"
DBUS_PROPERTIES_INTERFACE =      "org.freedesktop.DBus.Properties"


class InvalidArgsException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.freedesktop.DBus.Error.InvalidArgs"
class NotSupportedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotSupported"
class NotPermittedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.NotPermitted"
class InvalidValueLengthException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.InvalidValueLength"
class FailedException(dbus.exceptions.DBusException):
    _dbus_error_name = "org.bluez.Error.Failed"

class Rejected(dbus.DBusException):
	_dbus_error_name = "org.bluez.Error.Rejected"

def find_adapter(bus):
    remote_om = dbus.Interface(bus.get_object(SERVICE_NAME, '/'),
                               DBUS_OBJECT_MANAGER_INTERFACE)
    objects = remote_om.GetManagedObjects()

    for o, props in objects.items():
        if GATT_MANAGER_INTERFACE in props.keys():
            return o

    return None
