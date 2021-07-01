from typing import Dict

from evdev import InputDevice, UInput, AbsInfo, InputEvent
from evdev import ecodes

from ._veikk_device import _VeikkDevice
from .event_loop import EventLoop
from ..common.command.pentransform_command import AffineTransform2D, AffineTransform1D
from ..common.evdev_util import EvdevUtil
from ..common.veikk_config import VeikkConfig
from ..common.veikk_model import VeikkModel


class VeikkDevice(_VeikkDevice):
    """
    Model for a connected VEIKK device whose outputs are being mapped.
    """

    def __init__(self,
                 device: InputDevice,
                 event_loop: EventLoop,
                 config: VeikkConfig,
                 models_info: Dict) -> None:

        self._device: InputDevice = device
        self._config = config

        # configure device-specific features
        self._device_specific_setup(models_info)

        # create virtual pen and keyboard devices for commands to use
        self._uinput_devices = (self._setup_uinput_pen(),
                                self._setup_uinput_keyboard())

        # get exclusive access to device (i.e., the events will not get used
        # by the display server)
        self._device.grab()

        # the destroy method may be called from the udev event or when
        # the InputDevice::read() fails, whichever comes sooner
        self._already_destroyed = False

        if __debug__:
            print(f'New VeikkDevice: {self._model_name}')

        self._event_loop = event_loop
        self._event_loop.register_device(self)

    def _device_specific_setup(self,
                               models_info: Dict[str, VeikkModel]) -> None:
        """
        Retrieves information about the VEIKK model and performs
        device-specific setup.

        One task is to map each device to a square, because otherwise
        the transforms don't work as expected. For example, performing the
        rotation (0, 1, 0, 1, 0, 0, 0, 0, 1) will not cause the edges of the
        screen to line up with the device in the rotated orientation.

        This matches the behavior when using
        `xinput set-prop <device> 'Coordinate Transformation Matrix' ...`
        to set the coordinate transform.

        :param models_info:     information about each model
        """
        # the device name should be 'VEIKK [model name] Bundled', extract
        # model name
        self._model_name = ' '.join(self._device.name.split(" ")[1:-1])

        if self._model_name not in models_info:
            print('Warning: device model unknown, using generic A50 model. '
                  'You may want to contact the developer to add this model '
                  'to the list of models.')
            self._model_name = 'A50'

        self._model = models_info[self._model_name]

        # transforms all coordinates to 65536x65536 so that rotations work
        # as expected
        ratio_x, ratio_y = 65536./self._model.x_max, 65536./self._model.y_max
        self._pen_pretransform_matrix = (AffineTransform1D((ratio_x, 0)),
                                         AffineTransform1D((ratio_y, 0)))

    def _setup_uinput_pen(self) -> UInput:
        """
        Creates uinput device to dispatch pen (ABS_*, BTN_*) events on.

        TODO: get capabilities from the device

        :return:
        """
        capabilities = {
            ecodes.EV_KEY: EvdevUtil.get_pen_evkey_events(),
            ecodes.EV_ABS: [
                (ecodes.ABS_X, AbsInfo(value=0, min=0, max=65536,
                                       fuzz=0, flat=0, resolution=100)),
                (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=65536,
                                       fuzz=0, flat=0, resolution=100)),
                (ecodes.ABS_PRESSURE, AbsInfo(value=0, min=0, max=8192,
                                              fuzz=0, flat=0,
                                              resolution=100))
            ]
        }
        input_props = [ecodes.INPUT_PROP_POINTER]
        return UInput(events=capabilities,
                      name=f'{self._model_name} Pen',
                      input_props=input_props)

    def _setup_uinput_keyboard(self) -> UInput:
        """
        Creates uinput device to dispatch keyboard events on. Allows any
        keyboard event, except those that only work when dispatched on a pen
        device (see EvdevUtil::is_pen_event).

        :return:    created uinput device
        """
        capabilities = {
            ecodes.EV_KEY: [code
                            for code, _ in ecodes.bytype[ecodes.EV_KEY].items()
                            if not EvdevUtil.is_pen_event(code)]
        }
        input_props = None
        return UInput(events=capabilities,
                      name=f'{self._model_name} Keyboard',
                      input_props=input_props)

    def _pen_pretransform(self, event: InputEvent) -> None:
        """
        For pen ABS_X and ABS_Y events, first linearly transform the coordinates
        to a 65536x65536 square. This is for rotations to work correctly. See
        _device_specific_setup() for details.

        Is a no-op if the event is not ABS_X or ABS_Y.
        :param event:   EV_ABS event to transform
        :return:
        """
        if event.code == ecodes.ABS_X:
            event.value = \
                self._pen_pretransform_matrix[0].transform((event.value,))[0]
        elif event.code == ecodes.ABS_Y:
            event.value = \
                self._pen_pretransform_matrix[1].transform((event.value,))[0]

    def handle_events(self) -> None:
        """
        Gets called when an event is emitted by the InputDevice. Is set up with
        pen/mouse and button capabilities.

        :return:
        """
        try:
            for event in self._device.read():
                # automatically send all sync events, regardless of mapping;
                # this is so to simplify the mappings
                if event.type == ecodes.EV_SYN:
                    self._uinput_devices[0].write_event(event)
                    self._uinput_devices[1].write_event(event)
                else:
                    self._pen_pretransform(event)
                    self._config.execute_event(event, self._uinput_devices)
        except OSError:
            # device removed -- clean up normally
            self.cleanup()

    def cleanup(self) -> bool:
        """
        Perform any cleanup actions.
        :return:    True if this device has not been cleaned up before
        """
        if self._already_destroyed:
            return False

        try:
            self._event_loop.unregister_device(self)
            self._uinput_devices[0].close()
            self._uinput_devices[1].close()
        except OSError as err:
            # sometimes occurs if device was not registered with the event loop
            print(f'Ignoring error: {err.strerror}')

        self._already_destroyed = True

        if __debug__:
            print(f'Disconnected VeikkDevice: {self._model_name}')

        return True

    def fileno(self) -> int:
        """
        Implement the HasFileno interface
        :return:    fd of the associated InputDevice
        """
        return self._device.fileno()
