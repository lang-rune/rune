from typing import Any, Dict
from .signals import RuntimeError


class Environment:
    """Lexically-scoped variable store with a parent-chain for closures."""

    def __init__(self, parent: "Environment" = None):
        self.parent = parent
        self.variables: Dict[str, Any] = {}

    def define(self, name: str, value: Any) -> None:
        self.variables[name] = value

    def get(self, name: str) -> Any:
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable: {name}")

    def set(self, name: str, value: Any) -> None:
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set(name, value)
        else:
            self.variables[name] = value
