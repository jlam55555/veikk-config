from .command import CommandType, Command


class NoopCommand(Command):
    """
    Default command for an action. Means this action is not mapped to anything.
    """
    def __init__(self):
        super(NoopCommand, self).__init__(CommandType.NOOP)

    def execute(self, _, __):
        if __debug__:
            print('event -> noop')