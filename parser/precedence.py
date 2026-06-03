from ..lexer import TokenType

# Numeric levels — higher value = tighter binding
PRECEDENCE_OR = 1
PRECEDENCE_AND = 2
PRECEDENCE_EQUALITY = 3
PRECEDENCE_COMPARISON = 4
PRECEDENCE_TERM = 5       # + -
PRECEDENCE_FACTOR = 6     # * / %
PRECEDENCE_UNARY = 7

# Token-type sets for each level (used by the recursive-descent parser)
OR_OPS = (TokenType.OR,)
AND_OPS = (TokenType.AND,)
EQUALITY_OPS = (TokenType.EQUALS, TokenType.NOT_EQUALS)
COMPARISON_OPS = (TokenType.GREATER, TokenType.LESS, TokenType.GTE, TokenType.LTE)
TERM_OPS = (TokenType.PLUS, TokenType.MINUS)
FACTOR_OPS = (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO)
UNARY_OPS = (TokenType.MINUS, TokenType.PLUS, TokenType.NOT)
