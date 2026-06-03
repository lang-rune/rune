from .token import Token
from .token_types import TokenType
from .keywords import KEYWORDS


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        self.keywords = KEYWORDS

    def error(self, message: str):
        raise SyntaxError(f"Lexer error at line {self.line}, column {self.column}: {message}")

    def peek(self, offset: int = 0) -> str:
        pos = self.pos + offset
        if pos >= len(self.text):
            return '\0'
        return self.text[pos]

    def advance(self) -> str:
        if self.pos >= len(self.text):
            return '\0'

        char = self.text[self.pos]
        self.pos += 1

        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def skip_whitespace(self):
        while self.peek() in ' \t':
            self.advance()

    def skip_comment(self):
        if self.peek() == "#":
            while self.peek() != '\n' and self.peek() != '\0':
                self.advance()

    def read_number(self) -> str:
        number = ''
        has_decimal = False

        while self.peek().isdigit() or (self.peek() == '.' and not has_decimal):
            char = self.peek()
            if char == '.':
                has_decimal = True
            number += self.advance()

        return number

    def read_word_literal(self) -> str:
        quote_char = self.advance()
        word = ''

        while self.peek() != quote_char and self.peek() != '\0':
            char = self.advance()
            if char == '\\':
                next_char = self.advance()
                if next_char == 'n':
                    word += '\n'
                elif next_char == 't':
                    word += '\t'
                elif next_char == '\\':
                    word += '\\'
                elif next_char == quote_char:
                    word += quote_char
                else:
                    word += next_char
            else:
                word += char

        if self.peek() == '\0':
            self.error("Unterminated string literal")

        self.advance()
        return word

    def read_identifier(self) -> str:
        ident = ''
        while self.peek().isalnum() or self.peek() == '_':
            ident += self.advance()
        return ident

    def tokenize(self) -> list[Token]:
        while self.pos < len(self.text):
            self.skip_whitespace()

            char = self.peek()

            if char == '\0':
                break
            elif char == '#':
                self.skip_comment()
            elif char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, self.advance(), self.line, self.column))
            elif char.isdigit():
                number = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, number, self.line, self.column))
            elif char in '"\'':
                word = self.read_word_literal()
                self.tokens.append(Token(TokenType.WORD, word, self.line, self.column))
            elif char.isalpha() or char == '_':
                ident = self.read_identifier()
                token_type = self.keywords.get(ident, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, ident, self.line, self.column))
            elif char == '+':
                self.tokens.append(Token(TokenType.PLUS, self.advance(), self.line, self.column))
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, self.advance(), self.line, self.column))
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, self.advance(), self.line, self.column))
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, self.advance(), self.line, self.column))
            elif char == '=':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQUALS, '==', self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', self.line, self.column))
            elif char == '!':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NOT_EQUALS, '!=', self.line, self.column))
                else:
                    self.error("Unexpected character '!'")
            elif char == '>':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GTE, '>=', self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.GREATER, '>', self.line, self.column))
            elif char == '<':
                self.advance()
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LTE, '<=', self.line, self.column))
                else:
                    self.tokens.append(Token(TokenType.LESS, '<', self.line, self.column))
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, self.advance(), self.line, self.column))
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, self.advance(), self.line, self.column))
            elif char == '{':
                self.tokens.append(Token(TokenType.LBRACE, self.advance(), self.line, self.column))
            elif char == '}':
                self.tokens.append(Token(TokenType.RBRACE, self.advance(), self.line, self.column))
            elif char == '[':
                self.tokens.append(Token(TokenType.LBRACKET, self.advance(), self.line, self.column))
            elif char == ']':
                self.tokens.append(Token(TokenType.RBRACKET, self.advance(), self.line, self.column))
            elif char == '%':
                self.tokens.append(Token(TokenType.MODULO, self.advance(), self.line, self.column))
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, self.advance(), self.line, self.column))
            elif char == ';':
                self.tokens.append(Token(TokenType.SEMICOLON, self.advance(), self.line, self.column))
            else:
                self.error(f"Unexpected character '{char}'")

        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens
