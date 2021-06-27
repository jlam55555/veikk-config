class Command:
    """
    An action spawned by a button press or gesture. Can be either a key
    combination or a command.
    """

    def __init__(self):
        pass

    def execute(self):
        pass

    def execute_keyup(self):
        # for key combinations only -- emits keyup events for the same keys,
        # but in opposite order
        pass
