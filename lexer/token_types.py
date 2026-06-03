from enum import Enum, auto


class TokenType(Enum):
    # Literals
    NUMBER = auto()
    WORD = auto()           # String literal
    BOOLEAN = auto()        # yes/no
    EMPTY = auto()          # empty keyword

    # Identifiers and keywords
    IDENTIFIER = auto()
    WRITE = auto()          # write() function
    SET = auto()            # variable assignment

    # Function keywords
    SPELL = auto()          # spell (function definition)
    CAST = auto()           # cast (optional function-call prefix)
    RETURN = auto()         # return from a spell

    # Loop keywords
    REPEAT = auto()         # repeat N times
    COUNT = auto()          # count from X to Y as Z
    FROM = auto()           # from  (part of count syntax)
    TO = auto()             # to    (part of count syntax)
    AS = auto()             # as    (part of count syntax)
    TIMES = auto()          # times (part of repeat syntax)

    # Loop control
    SKIP = auto()           # skip current iteration (continue)
    STOP = auto()           # stop loop (break)

    # Operators
    PLUS = auto()           # +
    MINUS = auto()          # -
    MULTIPLY = auto()       # *
    DIVIDE = auto()         # /
    MODULO = auto()         # %
    EQUALS = auto()         # ==
    NOT_EQUALS = auto()     # !=
    GREATER = auto()        # >
    LESS = auto()           # <
    GTE = auto()            # >=
    LTE = auto()            # <=
    ASSIGN = auto()         # =

    # Logical Operators
    AND = auto()            # and
    OR = auto()             # or
    NOT = auto()            # not

    # Delimiters
    LPAREN = auto()         # (
    RPAREN = auto()         # )
    LBRACE = auto()         # {
    RBRACE = auto()         # }
    LBRACKET = auto()       # [
    RBRACKET = auto()       # ]
    COMMA = auto()          # ,
    SEMICOLON = auto()      # ;
    NEWLINE = auto()        # \n

    # Control flow
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    OTHERWISE = auto()      # otherwise (else-if chaining)

    # Special
    EOF = auto()
    UNKNOWN = auto()
