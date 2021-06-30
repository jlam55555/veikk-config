class _VeikkDevice:
    """
    Avoid circular dependency w/ VeikkDevice
    """

    def fileno(self) -> int: ...

    def handle_events(self) -> None: ...