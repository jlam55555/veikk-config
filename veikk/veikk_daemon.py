from veikk.evdev_manager import EvdevManager
from veikk.udev_manager import UdevManager


class VeikkDaemon:

    def __init__(self):
        # print("Testing")
        # UdevManager.init_udev_monitor()
        EvdevManager.get_initial_devices()


# device = evdev.InputDevice('/dev/input/event7')
# print(device)
#
# init_udev_monitor()
#
# for event in device.read_loop():
#     print(evdev.categorize(event))
#
# print("Done.")