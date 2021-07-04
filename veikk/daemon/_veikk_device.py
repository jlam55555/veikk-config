class _VeikkDevice:
    """
    Avoid circular dependency w/ VeikkDevice
    """

    def fileno(self) -> int:
        raise NotImplementedError()

    def handle_events(self) -> None:
        raise NotImplementedError()