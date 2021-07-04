from pydbus import SystemBus
from gi.repository import GLib

from veikk.common.command.command import KeyCode
from veikk.common.veikk_config import VeikkConfig


VEIKK_DBUS_OBJECT = 'com.veikk.veikkd.VeikkDaemon'


class VeikkDaemonDbusObject:
    """
    Definition of the VeikkDaemon object for (py)dbus

    Notes:
    - CapsCase method names as per dbus convention.
    - Only use very simple dbus features, e.g., only simple types (int and
        string), and only use regular methods (no properties, signals, etc.).
        Objects are (de)serialized using the existing YAML serialization
        support. Don't want to complicate things.
    - The device parameter is present in case future versions support different
        configurations for different VEIKK devices. This is not currently
        implemented, so its value is ignored.
    - The filename parameter for LoadConfigFromFile/SaveConfigToFile is
        optional. If an empty string is passed, then it will use the default
        config file location.
    """

    # dbus introspection data
    dbus = f"""
    <node>
      <interface name='{VEIKK_DBUS_OBJECT}'>
        <method name='MapButton'>
          <arg type='i' name='device' direction='in'/>
          <arg type='i' name='keycode' direction='in'/>
          <arg type='s' name='command' direction='in'/>
        </method>
        <method name='MapPen'>
          <arg type='i' name='device' direction='in'/>
          <arg type='s' name='command' direction='in'/>
        </method>
        <method name='GetCurrentConfig'>
          <arg type='i' name='device' direction='in'/>
          <arg type='s' name='config' direction='out'/>
        </method>
        <method name='LoadConfigFromFile'>
          <arg type='i' name='device' direction='in'/>
          <arg type='s' name='filename' direction='in'/>
        </method>
        <method name='SaveConfigToFile'>
          <arg type='i' name='device' direction='in'/>
          <arg type='s' name='filename' direction='in'/>
        </method>
      </interface>
    </node>
    """

    def __init__(self, config: VeikkConfig) -> None:
        self._config = config

    def MapButton(self, _device: int, keycode: KeyCode, command: str) -> None:
        print('got MapButton request')

    def MapPen(self, _device: int, command: str) -> None:
        print('got MapPen request')

    def GetCurrentConfig(self, _device: int) -> str:
        print('got GetCurrentConfig request')
        return 'testing object'

    def LoadConfigFromFile(self, _device: int, filename: str) -> None:
        with open(filename, 'r') as fd:
            print(f'read file contents: {fd.read()}')

    def SaveConfigToFile(self, _device: int, filename: str) -> None:
        with open(filename, 'w+') as fd:
            fd.write('Hello, world!')


# TODO: move the following code to another file; this file should only contain
#   the definition of the dbus object

# remote_object = bus.get('org.freedesktop.DBus',
#                         '/org/freedesktop/DBus')
# print(remote_object.Introspect())

bus = SystemBus()
bus.publish(VEIKK_DBUS_OBJECT, VeikkDaemonDbusObject(VeikkConfig()))
loop = GLib.MainLoop()
loop.run()
