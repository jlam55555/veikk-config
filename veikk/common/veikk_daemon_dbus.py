from .constants import VEIKK_DBUS_OBJECT
from .command.command import KeyCode, Command
from .command.pentransform_command import PenTransformCommand
from .evdev_util import EvdevUtil
from .veikk_config import VeikkConfig



class VeikkDaemonDbus:
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
        """
        Map a button to command
        :param _device:     (not implemented)
        :param keycode:     button to map (integer keycode)
        :param command:     serialized button mapping command
        """
        cmd = Command.load_yaml(command)

        assert not isinstance(cmd, PenTransformCommand)
        assert EvdevUtil.is_valid_keycode(keycode)

        self._config.map_button(keycode, cmd)

    def MapPen(self, _device: int, command: str) -> None:
        """
        Set a pen transform
        :param _device:     (not implemented)
        :param command:     serialized pen transform to apply
        """
        cmd = PenTransformCommand.load_yaml(command)
        self._config.map_pen(cmd)

    def GetCurrentConfig(self, _device: int) -> str:
        """
        Returns the current command
        :param _device:     (not implemented)
        :return:            serialized current configuration
        """
        return self._config.dump_yaml()

    def LoadConfigFromFile(self, _device: int, filename: str) -> None:
        """
        Sets the active configuration from a file.
        :param _device:     (not implemented)
        :param filename:    file to read from
        """
        with open(filename, 'r') as fd:
            self._config = VeikkConfig.load_yaml(fd.read())

    def SaveConfigToFile(self, _device: int, filename: str) -> None:
        """
        Saves the active configuration to a file.
        :param _device:     (not implemented)
        :param filename:    file to write to
        """
        with open(filename, 'w+') as fd:
            fd.write(self._config.dump_yaml())
