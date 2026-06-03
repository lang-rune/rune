from .token_types import TokenType

KEYWORDS = {
    'write': TokenType.WRITE,
    'set': TokenType.SET,
    'yes': TokenType.BOOLEAN,
    'no': TokenType.BOOLEAN,
    'empty': TokenType.EMPTY,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'not': TokenType.NOT,
    # Functions
    'spell': TokenType.SPELL,
    'cast': TokenType.CAST,
    'return': TokenType.RETURN,
    # Loops
    'repeat': TokenType.REPEAT,
    'count': TokenType.COUNT,
    'from': TokenType.FROM,
    'to': TokenType.TO,
    'as': TokenType.AS,
    'times': TokenType.TIMES,
    # Loop control
    'skip': TokenType.SKIP,
    'stop': TokenType.STOP,
    # Conditional
    'otherwise': TokenType.OTHERWISE,
}
