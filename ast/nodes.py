from abc import ABC
from typing import Any, List, Optional


class ASTNode(ABC):
    pass


class Expression(ASTNode):
    pass


class Statement(ASTNode):
    pass


# ── Literals ──────────────────────────────────────────────────────────────────

class NumberLiteral(Expression):
    def __init__(self, value: float):
        self.value = value

    def __repr__(self):
        return f"NumberLiteral({self.value})"


class WordLiteral(Expression):
    def __init__(self, value: str):
        self.value = value

    def __repr__(self):
        return f"WordLiteral('{self.value}')"


class BooleanLiteral(Expression):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self):
        return f"BooleanLiteral({self.value})"


class EmptyLiteral(Expression):
    def __init__(self):
        self.value = None

    def __repr__(self):
        return "EmptyLiteral()"


# ── Expressions ───────────────────────────────────────────────────────────────

class Identifier(Expression):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return f"Identifier('{self.name}')"


class BinaryOp(Expression):
    def __init__(self, left: Expression, operator: str, right: Expression):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"BinaryOp({self.left}, '{self.operator}', {self.right})"


class UnaryOp(Expression):
    def __init__(self, operator: str, operand: Expression):
        self.operator = operator
        self.operand = operand

    def __repr__(self):
        return f"UnaryOp('{self.operator}', {self.operand})"


class FunctionCall(Expression):
    def __init__(self, name: str, args: List[Expression]):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"FunctionCall('{self.name}', {self.args})"


# ── Statements ────────────────────────────────────────────────────────────────

class WriteStatement(Statement):
    def __init__(self, args: List[Expression]):
        self.args = args

    def __repr__(self):
        return f"WriteStatement({self.args})"


class AssignmentStatement(Statement):
    def __init__(self, variable: str, value: Expression):
        self.variable = variable
        self.value = value

    def __repr__(self):
        return f"AssignmentStatement('{self.variable}', {self.value})"


class IfStatement(Statement):
    def __init__(self, condition: Expression, then_body: List[Statement],
                 else_body: List[Statement] = None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body or []

    def __repr__(self):
        return f"IfStatement({self.condition}, {self.then_body}, {self.else_body})"


class WhileStatement(Statement):
    def __init__(self, condition: Expression, body: List[Statement]):
        self.condition = condition
        self.body = body

    def __repr__(self):
        return f"WhileStatement({self.condition}, {self.body})"


class ExpressionStatement(Statement):
    def __init__(self, expression: Expression):
        self.expression = expression

    def __repr__(self):
        return f"ExpressionStatement({self.expression})"


class Program(ASTNode):
    def __init__(self, statements: List[Statement]):
        self.statements = statements

    def __repr__(self):
        return f"Program({self.statements})"


# ── Spell (function) ──────────────────────────────────────────────────────────

class SpellDefinition(Statement):
    def __init__(self, name: str, params: List[str], body: List[Statement]):
        self.name = name
        self.params = params
        self.body = body

    def __repr__(self):
        return f"SpellDefinition('{self.name}', {self.params})"


class ReturnStatement(Statement):
    def __init__(self, value: Optional[Expression] = None):
        self.value = value

    def __repr__(self):
        return f"ReturnStatement({self.value})"


class CastStatement(Statement):
    def __init__(self, call: FunctionCall):
        self.call = call

    def __repr__(self):
        return f"CastStatement({self.call})"


# ── Loops ─────────────────────────────────────────────────────────────────────

class RepeatStatement(Statement):
    def __init__(self, count: Expression, body: List[Statement]):
        self.count = count
        self.body = body

    def __repr__(self):
        return f"RepeatStatement({self.count})"


class CountStatement(Statement):
    def __init__(self, variable: str, start: Expression, end: Expression,
                 body: List[Statement]):
        self.variable = variable
        self.start = start
        self.end = end
        self.body = body

    def __repr__(self):
        return f"CountStatement('{self.variable}', {self.start}, {self.end})"


class SkipStatement(Statement):
    def __repr__(self):
        return "SkipStatement()"


class StopStatement(Statement):
    def __repr__(self):
        return "StopStatement()"
