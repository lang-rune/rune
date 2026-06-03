from typing import Any
from ..ast import (
    ASTNode, Program,
    NumberLiteral, WordLiteral, BooleanLiteral, EmptyLiteral,
    Identifier, BinaryOp, UnaryOp, FunctionCall,
    WriteStatement, AssignmentStatement, ExpressionStatement,
    IfStatement, WhileStatement,
    SpellDefinition, CastStatement, ReturnStatement,
    SkipStatement, StopStatement,
    RepeatStatement, CountStatement,
)
from .signals import RuntimeError, ReturnSignal, SkipSignal, StopSignal
from .environment import Environment
from .values import SpellValue
from .builtins import Builtins, to_rune_string


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.current_env = self.global_env

        _b = Builtins()
        self.builtins = {
            'write':  _b.write,
            'input':  _b.input,
            'type':   _b.type_of,
            'length': _b.length,
            'number': _b.number,
            'word':   _b.word,
        }

    # ── Helpers ────────────────────────────────────────────────────────────────

    def error(self, message: str):
        raise RuntimeError(message)

    def is_truthy(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

    def are_equal(self, left: Any, right: Any) -> bool:
        return left == right

    def to_string(self, value: Any) -> str:
        return to_rune_string(value)

    # ── Dispatch ───────────────────────────────────────────────────────────────

    def interpret(self, node: ASTNode) -> Any:
        method = getattr(self, f'visit_{type(node).__name__}', None)
        if method:
            return method(node)
        self.error(f"No visit method for {type(node)}")

    def run(self, program: Program) -> Any:
        try:
            return self.interpret(program)
        except RuntimeError as e:
            print(f"Runtime Error: {e}")
            return None

    # ── Visitors — literals ────────────────────────────────────────────────────

    def visit_Program(self, node: Program) -> Any:
        result = None
        for stmt in node.statements:
            result = self.interpret(stmt)
        return result

    def visit_NumberLiteral(self, node: NumberLiteral) -> float:
        return node.value

    def visit_WordLiteral(self, node: WordLiteral) -> str:
        return node.value

    def visit_BooleanLiteral(self, node: BooleanLiteral) -> bool:
        return node.value

    def visit_EmptyLiteral(self, node: EmptyLiteral) -> None:
        return None

    def visit_Identifier(self, node: Identifier) -> Any:
        return self.current_env.get(node.name)

    # ── Visitors — expressions ─────────────────────────────────────────────────

    def visit_BinaryOp(self, node: BinaryOp) -> Any:
        # Short-circuit logical operators
        if node.operator == 'and':
            return self.is_truthy(self.interpret(node.left)) and \
                   self.is_truthy(self.interpret(node.right))
        if node.operator == 'or':
            left = self.interpret(node.left)
            if self.is_truthy(left):
                return True
            return self.is_truthy(self.interpret(node.right))

        left = self.interpret(node.left)
        right = self.interpret(node.right)

        if node.operator == '+':
            if isinstance(left, str) or isinstance(right, str):
                return to_rune_string(left) + to_rune_string(right)
            return left + right
        if node.operator == '-':   return left - right
        if node.operator == '*':   return left * right
        if node.operator == '/':
            if right == 0:
                self.error("Division by zero")
            return left / right
        if node.operator == '%':
            if right == 0:
                self.error("Modulo by zero")
            return left % right
        if node.operator == '==':  return self.are_equal(left, right)
        if node.operator == '!=':  return not self.are_equal(left, right)
        if node.operator == '>':   return left > right
        if node.operator == '<':   return left < right
        if node.operator == '>=':  return left >= right
        if node.operator == '<=':  return left <= right
        self.error(f"Unknown binary operator: {node.operator}")

    def visit_UnaryOp(self, node: UnaryOp) -> Any:
        operand = self.interpret(node.operand)
        if node.operator == '-':    return -operand
        if node.operator == '+':    return +operand
        if node.operator == 'not':  return not self.is_truthy(operand)
        self.error(f"Unknown unary operator: {node.operator}")

    def visit_FunctionCall(self, node: FunctionCall) -> Any:
        args = [self.interpret(a) for a in node.args]

        if node.name in self.builtins:
            return self.builtins[node.name](*args)

        try:
            spell = self.current_env.get(node.name)
        except RuntimeError:
            self.error(f"Unknown function or spell: '{node.name}'")

        if not isinstance(spell, SpellValue):
            self.error(f"'{node.name}' is not callable")

        if len(args) != len(spell.params):
            self.error(
                f"Spell '{node.name}' expects {len(spell.params)} argument(s), "
                f"got {len(args)}"
            )

        call_env = Environment(spell.closure)
        for param, arg in zip(spell.params, args):
            call_env.define(param, arg)

        prev_env = self.current_env
        self.current_env = call_env
        return_value = None
        try:
            for stmt in spell.body:
                self.interpret(stmt)
        except ReturnSignal as ret:
            return_value = ret.value
        finally:
            self.current_env = prev_env
        return return_value

    # ── Visitors — statements ──────────────────────────────────────────────────

    def visit_WriteStatement(self, node: WriteStatement) -> None:
        self.builtins['write'](*[self.interpret(a) for a in node.args])

    def visit_AssignmentStatement(self, node: AssignmentStatement) -> None:
        self.current_env.define(node.variable, self.interpret(node.value))

    def visit_ExpressionStatement(self, node: ExpressionStatement) -> Any:
        return self.interpret(node.expression)

    def visit_IfStatement(self, node: IfStatement) -> Any:
        if self.is_truthy(self.interpret(node.condition)):
            result = None
            for stmt in node.then_body:
                result = self.interpret(stmt)
            return result
        if node.else_body:
            result = None
            for stmt in node.else_body:
                result = self.interpret(stmt)
            return result

    def visit_WhileStatement(self, node: WhileStatement) -> None:
        while self.is_truthy(self.interpret(node.condition)):
            try:
                for stmt in node.body:
                    self.interpret(stmt)
            except SkipSignal:
                continue
            except StopSignal:
                break

    # ── Visitors — spells ──────────────────────────────────────────────────────

    def visit_SpellDefinition(self, node: SpellDefinition) -> None:
        self.current_env.define(
            node.name,
            SpellValue(node.name, node.params, node.body, self.current_env)
        )

    def visit_CastStatement(self, node: CastStatement) -> Any:
        return self.interpret(node.call)

    def visit_ReturnStatement(self, node: ReturnStatement) -> None:
        value = self.interpret(node.value) if node.value is not None else None
        raise ReturnSignal(value)

    # ── Visitors — loop control ────────────────────────────────────────────────

    def visit_SkipStatement(self, node: SkipStatement) -> None:
        raise SkipSignal()

    def visit_StopStatement(self, node: StopStatement) -> None:
        raise StopSignal()

    def visit_RepeatStatement(self, node: RepeatStatement) -> None:
        count = self.interpret(node.count)
        if not isinstance(count, (int, float)):
            self.error("repeat count must be a number")
        for _ in range(int(count)):
            try:
                for stmt in node.body:
                    self.interpret(stmt)
            except SkipSignal:
                continue
            except StopSignal:
                break

    def visit_CountStatement(self, node: CountStatement) -> None:
        start = self.interpret(node.start)
        end = self.interpret(node.end)
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            self.error("count from/to values must be numbers")
        start, end = int(start), int(end)
        step = 1 if start <= end else -1
        i = start
        while (step == 1 and i <= end) or (step == -1 and i >= end):
            self.current_env.define(node.variable, float(i))
            try:
                for stmt in node.body:
                    self.interpret(stmt)
            except SkipSignal:
                pass
            except StopSignal:
                break
            i += step
