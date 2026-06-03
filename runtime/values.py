from typing import Any, List


class SpellValue:
    """A user-defined function (spell) captured with its closure environment."""

    def __init__(self, name: str, params: List[str], body: Any, closure: Any):
        self.name = name
        self.params = params
        self.body = body        # List[Statement] — typed as Any to avoid coupling ast here
        self.closure = closure  # Environment

    def __repr__(self):
        return f"<spell {self.name}({', '.join(self.params)})>"
