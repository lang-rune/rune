from typing import List, Optional
from ..lexer import Token, TokenType
from ..ast import (
    ASTNode, Expression, Statement, Program,
    NumberLiteral, WordLiteral, BooleanLiteral, EmptyLiteral,
    Identifier, BinaryOp, UnaryOp, FunctionCall,
    WriteStatement, AssignmentStatement, IfStatement, WhileStatement,
    ExpressionStatement, SpellDefinition, ReturnStatement, CastStatement,
    RepeatStatement, CountStatement, SkipStatement, StopStatement,
)
from .precedence import (
    OR_OPS, AND_OPS, EQUALITY_OPS, COMPARISON_OPS,
    TERM_OPS, FACTOR_OPS, UNARY_OPS,
)


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None

    def error(self, message: str):
        if self.current_token:
            raise SyntaxError(
                f"Parser error at line {self.current_token.line}, "
                f"column {self.current_token.column}: {message}"
            )
        raise SyntaxError(f"Parser error: {message}")

    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        return self.current_token

    def peek(self, offset: int = 1) -> Optional[Token]:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    def match(self, *token_types: TokenType) -> bool:
        return bool(self.current_token and self.current_token.type in token_types)

    def consume(self, token_type: TokenType, message: str = None) -> Token:
        if not self.match(token_type):
            msg = message or (
                f"Expected {token_type}, "
                f"got {self.current_token.type if self.current_token else 'EOF'}"
            )
            self.error(msg)
        token = self.current_token
        self.advance()
        return token

    def skip_newlines(self):
        while self.match(TokenType.NEWLINE):
            self.advance()

    # ── Top-level ──────────────────────────────────────────────────────────────

    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        while not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        return Program(statements)

    # ── Statements ─────────────────────────────────────────────────────────────

    def parse_statement(self) -> Optional[Statement]:
        if self.match(TokenType.WRITE):
            return self.parse_write_statement()
        elif self.match(TokenType.SET):
            return self.parse_assignment_statement()
        elif self.match(TokenType.IF):
            return self.parse_if_statement()
        elif self.match(TokenType.WHILE):
            return self.parse_while_statement()
        elif self.match(TokenType.SPELL):
            return self.parse_spell_definition()
        elif self.match(TokenType.CAST):
            return self.parse_cast_statement()
        elif self.match(TokenType.RETURN):
            return self.parse_return_statement()
        elif self.match(TokenType.REPEAT):
            return self.parse_repeat_statement()
        elif self.match(TokenType.COUNT):
            return self.parse_count_statement()
        elif self.match(TokenType.SKIP):
            self.advance()
            return SkipStatement()
        elif self.match(TokenType.STOP):
            self.advance()
            return StopStatement()
        elif self.match(TokenType.NEWLINE):
            self.advance()
            return None
        else:
            return ExpressionStatement(self.parse_expression())

    def parse_write_statement(self) -> WriteStatement:
        self.consume(TokenType.WRITE)
        self.consume(TokenType.LPAREN, "Expected '(' after 'write'")
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.parse_expression())
        self.consume(TokenType.RPAREN, "Expected ')' after write arguments")
        return WriteStatement(args)

    def parse_assignment_statement(self) -> AssignmentStatement:
        self.consume(TokenType.SET)
        variable_token = self.consume(TokenType.IDENTIFIER, "Expected variable name after 'set'")
        self.consume(TokenType.ASSIGN, "Expected '=' after variable name")
        return AssignmentStatement(variable_token.value, self.parse_expression())

    def parse_if_statement(self) -> IfStatement:
        self.consume(TokenType.IF)
        return self._parse_if_body()

    def _parse_if_body(self) -> IfStatement:
        condition = self.parse_expression()
        self.consume(TokenType.LBRACE, "Expected '{' after if condition")
        self.skip_newlines()

        then_body = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                then_body.append(stmt)
            self.skip_newlines()
        self.consume(TokenType.RBRACE, "Expected '}' after if body")
        self.skip_newlines()

        else_body = []
        if self.match(TokenType.ELSE):
            self.advance()
            self.skip_newlines()
            if self.match(TokenType.IF):
                self.advance()
                self.skip_newlines()
                else_body = [self._parse_if_body()]
            else:
                self.consume(TokenType.LBRACE, "Expected '{' after else")
                self.skip_newlines()
                while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
                    stmt = self.parse_statement()
                    if stmt:
                        else_body.append(stmt)
                    self.skip_newlines()
                self.consume(TokenType.RBRACE, "Expected '}' after else body")
        elif self.match(TokenType.OTHERWISE):
            self.advance()
            self.skip_newlines()
            if self.match(TokenType.LBRACE):
                self.consume(TokenType.LBRACE, "Expected '{' after otherwise")
                self.skip_newlines()
                while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
                    stmt = self.parse_statement()
                    if stmt:
                        else_body.append(stmt)
                    self.skip_newlines()
                self.consume(TokenType.RBRACE, "Expected '}' after otherwise body")
            else:
                else_body = [self._parse_if_body()]

        return IfStatement(condition, then_body, else_body)

    def parse_while_statement(self) -> WhileStatement:
        self.consume(TokenType.WHILE)
        condition = self.parse_expression()
        self.consume(TokenType.LBRACE, "Expected '{' after while condition")
        self.skip_newlines()

        body = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            self.skip_newlines()
        self.consume(TokenType.RBRACE, "Expected '}' after while body")
        return WhileStatement(condition, body)

    def _parse_block(self, open_msg: str = "Expected '{'",
                     close_msg: str = "Expected '}'") -> List[Statement]:
        self.consume(TokenType.LBRACE, open_msg)
        self.skip_newlines()
        stmts = []
        while not self.match(TokenType.RBRACE) and not self.match(TokenType.EOF):
            stmt = self.parse_statement()
            if stmt:
                stmts.append(stmt)
            self.skip_newlines()
        self.consume(TokenType.RBRACE, close_msg)
        return stmts

    def parse_spell_definition(self) -> SpellDefinition:
        self.consume(TokenType.SPELL)
        name_token = self.consume(TokenType.IDENTIFIER, "Expected spell name after 'spell'")
        self.consume(TokenType.LPAREN, "Expected '(' after spell name")
        params = []
        if not self.match(TokenType.RPAREN):
            params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
            while self.match(TokenType.COMMA):
                self.advance()
                params.append(self.consume(TokenType.IDENTIFIER, "Expected parameter name").value)
        self.consume(TokenType.RPAREN, "Expected ')' after spell parameters")
        self.skip_newlines()
        body = self._parse_block("Expected '{' after spell signature",
                                 "Expected '}' after spell body")
        return SpellDefinition(name_token.value, params, body)

    def parse_cast_statement(self) -> CastStatement:
        self.consume(TokenType.CAST)
        name_token = self.consume(TokenType.IDENTIFIER, "Expected spell name after 'cast'")
        self.consume(TokenType.LPAREN, "Expected '(' after cast target")
        args = []
        if not self.match(TokenType.RPAREN):
            args.append(self.parse_expression())
            while self.match(TokenType.COMMA):
                self.advance()
                args.append(self.parse_expression())
        self.consume(TokenType.RPAREN, "Expected ')' after cast arguments")
        return CastStatement(FunctionCall(name_token.value, args))

    def parse_return_statement(self) -> ReturnStatement:
        self.consume(TokenType.RETURN)
        if self.match(TokenType.NEWLINE, TokenType.RBRACE, TokenType.EOF):
            return ReturnStatement(None)
        return ReturnStatement(self.parse_expression())

    def parse_repeat_statement(self) -> RepeatStatement:
        self.consume(TokenType.REPEAT)
        count_expr = self.parse_expression()
        self.consume(TokenType.TIMES, "Expected 'times' after repeat count")
        self.skip_newlines()
        body = self._parse_block("Expected '{' after 'times'",
                                 "Expected '}' after repeat body")
        return RepeatStatement(count_expr, body)

    def parse_count_statement(self) -> CountStatement:
        self.consume(TokenType.COUNT)
        self.consume(TokenType.FROM, "Expected 'from' after 'count'")
        start_expr = self.parse_expression()
        self.consume(TokenType.TO, "Expected 'to' in count statement")
        end_expr = self.parse_expression()
        self.consume(TokenType.AS, "Expected 'as' in count statement")
        var_token = self.consume(TokenType.IDENTIFIER, "Expected loop variable after 'as'")
        self.skip_newlines()
        body = self._parse_block("Expected '{' after count header",
                                 "Expected '}' after count body")
        return CountStatement(var_token.value, start_expr, end_expr, body)

    # ── Expressions (recursive-descent, precedence from precedence.py) ─────────

    def parse_expression(self) -> Expression:
        return self.parse_logical_or()

    def parse_logical_or(self) -> Expression:
        expr = self.parse_logical_and()
        while self.match(*OR_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_logical_and())
        return expr

    def parse_logical_and(self) -> Expression:
        expr = self.parse_equality()
        while self.match(*AND_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_equality())
        return expr

    def parse_equality(self) -> Expression:
        expr = self.parse_comparison()
        while self.match(*EQUALITY_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_comparison())
        return expr

    def parse_comparison(self) -> Expression:
        expr = self.parse_addition()
        while self.match(*COMPARISON_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_addition())
        return expr

    def parse_addition(self) -> Expression:
        expr = self.parse_multiplication()
        while self.match(*TERM_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_multiplication())
        return expr

    def parse_multiplication(self) -> Expression:
        expr = self.parse_unary()
        while self.match(*FACTOR_OPS):
            operator = self.current_token.value
            self.advance()
            expr = BinaryOp(expr, operator, self.parse_unary())
        return expr

    def parse_unary(self) -> Expression:
        if self.match(*UNARY_OPS):
            operator = self.current_token.value
            self.advance()
            return UnaryOp(operator, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self) -> Expression:
        if self.match(TokenType.NUMBER):
            value = float(self.current_token.value)
            self.advance()
            return NumberLiteral(value)

        if self.match(TokenType.WORD):
            value = self.current_token.value
            self.advance()
            return WordLiteral(value)

        if self.match(TokenType.BOOLEAN):
            value = self.current_token.value == 'yes'
            self.advance()
            return BooleanLiteral(value)

        if self.match(TokenType.EMPTY):
            self.advance()
            return EmptyLiteral()

        if self.match(TokenType.IDENTIFIER):
            name = self.current_token.value
            self.advance()
            if self.match(TokenType.LPAREN):
                self.advance()
                args = []
                if not self.match(TokenType.RPAREN):
                    args.append(self.parse_expression())
                    while self.match(TokenType.COMMA):
                        self.advance()
                        args.append(self.parse_expression())
                self.consume(TokenType.RPAREN, "Expected ')' after function arguments")
                return FunctionCall(name, args)
            return Identifier(name)

        if self.match(TokenType.LPAREN):
            self.advance()
            expr = self.parse_expression()
            self.consume(TokenType.RPAREN, "Expected ')' after expression")
            return expr

        self.error(
            f"Unexpected token: {self.current_token.value if self.current_token else 'EOF'}"
        )
