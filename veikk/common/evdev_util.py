from evdev import InputDevice, list_devices, ecodes
from typing import List

from .command.command import KeyCode


class EvdevUtil:
    """
    Static utility functions for evdev
    """

    @staticmethod
    def get_initial_devices() -> List[InputDevice]:
        """
        Gets the list of VEIKK devices at boot
        :return:    list of current VEIKK devices
        """
        return list(filter(EvdevUtil.is_veikk_device,
                           [InputDevice(path) for path in list_devices()]))

    @staticmethod
    def is_veikk_device(device: InputDevice) -> bool:
        """
        Determines whether a evdev device is a VEIKK device
        :param device:  evdev device
        :return:        whether evdev device is a VEIKK device
        """
        return device.name.startswith("VEIKK ")

    @staticmethod
    def is_valid_keycode(code: KeyCode) -> bool:
        """
        Checks if keycode exists in evdev key/button input events list
        :param code:    keycode
        :return:        whether keycode exists in evdev input events list
        """
        return code in ecodes.keys

    @staticmethod
    def keycode_to_str(code: KeyCode) -> str:
        """
        Some keys may have multiple aliases representations, so we take
        the first one (arbitrarily).
        TODO: error handling
        :param code:    keycode to find the string representation of
        :return:
        """
        code = ecodes.keys[code]
        return code[0] if isinstance(code, list) else code

    @staticmethod
    def str_to_keycode(code_str: str) -> KeyCode:
        """
        Convert string representation of key to keycode (number).
        TODO: error handling
        :param code_str:
        :return:
        """
        return ecodes.ecodes[code_str]

    @staticmethod
    def is_pen_event(event_code) -> bool:
        """
        Some button events (which fall under EV_KEY) will not work if sent
        by the keyboard device. This is probably due to X's interpretation of
        which events should go with which event types. For example, the
        BTN_STYLUS and BTN_STYLUS_2 events only work with the pen input, and
        probably other digitizer pen events as well.

        See /include/uapi/linux/input-event-codes.h

        TODO: this list is not exhaustive

        :param event_code:  keyboard event to test
        :return:            whether this event should be fired on the pen
                            uinput device rather than the keyboard uinput device
        """
        return event_code in EvdevUtil._known_pen_evkey_events

    @staticmethod
    def get_pen_evkey_events() -> List[KeyCode]:
        return list(EvdevUtil._known_pen_evkey_events)

    _known_pen_evkey_events = {
        ecodes.BTN_STYLUS, ecodes.BTN_STYLUS2, ecodes.BTN_STYLUS3,
        ecodes.BTN_LEFT, ecodes.BTN_RIGHT
    }
