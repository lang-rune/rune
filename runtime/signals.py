class RuntimeError(Exception):
    """Raised for Rune-level runtime errors."""
    pass


class ReturnSignal(Exception):
    """Raised by `return` to unwind the call stack back to the spell frame."""
    def __init__(self, value):
        self.value = value


class SkipSignal(Exception):
    """Raised by `skip` to continue to the next loop iteration."""
    pass


class StopSignal(Exception):
    """Raised by `stop` to break out of the enclosing loop."""
    pass
