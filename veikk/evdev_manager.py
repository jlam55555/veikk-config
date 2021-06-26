import evdev


class EvdevManager:

    @staticmethod
    def get_initial_devices():
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            print(device.path, device.name, device.phys)
