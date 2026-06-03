from typing import Any
from .signals import RuntimeError


def to_rune_string(value: Any) -> str:
    """Convert a Python value to its Rune string representation."""
    if value is None:
        return "empty"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class Builtins:
    """All built-in Rune functions, isolated from interpreter execution logic."""

    def write(self, *args: Any) -> None:
        print(" ".join(to_rune_string(a) for a in args))

    def input(self, prompt: Any = "") -> str:
        return input(to_rune_string(prompt))

    def type_of(self, value: Any) -> str:
        if value is None:
            return "empty"
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, (int, float)):
            return "number"
        if isinstance(value, str):
            return "word"
        return "unknown"

    def length(self, value: Any) -> float:
        if isinstance(value, str):
            return float(len(value))
        raise RuntimeError(f"Cannot get length of {self.type_of(value)}")

    def number(self, value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                raise RuntimeError(f"Cannot convert '{value}' to number")
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        raise RuntimeError(f"Cannot convert {self.type_of(value)} to number")

    def word(self, value: Any) -> str:
        return to_rune_string(value)
