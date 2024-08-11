import sys
from enum import Enum
class Token:
    def __init__(self, type, value):
        self.type = type      # type of the token
        self.value = value    # value of the token

    # Returns a string representation of the keyword or null if it's not a keyword.
    @staticmethod
    def checkIfKeyword(tokenText):
        for type in TokenType:
            # Relies on all keyword enum values being 1XX.
            if type.name.lower() == tokenText and 100 <= type.value < 200:
                return type
        return None
    
    @staticmethod
    def checkIfLogicalOperator(tokenText):
        for type in TokenType:
            # Relies on all keyword enum values being 4XX.
            if type.name.lower() == tokenText and 400 <= type.value < 500:
                return type
        return None

# TokenType is our enum for all the types of tokens.
class TokenType(Enum):
    ERROR = -2
    EOF = -1
    NEWLINE = 0
    INTEGER = 1
    BOOLEAN = 2
    IDENTIFIER = 3
    STRING = 4
    NULL = 5
    FLOAT = 6
    # Punctuation.
    LBRACE = 7      # {
    RBRACE = 8      # }
    LPAREN = 9      # (
    RPAREN = 10     # )
    SEMICOLON = 11  # ;
    COMMA = 12      # ,
    DOT = 13        # .
    # -------------------------------- #
    # Keywords.
    WHILE = 101
    FUNCTION = 102
    PRINT = 103  
    INPUT = 104
    SET = 105    
    IF = 106
    ELSE = 107
    ELIF = 108
    FOR = 109
    RETURN = 110
    # -------------------------------- #
    # Operators.
    EQ = 301        # =
    PLUS = 302
    MINUS = 303
    ASTERISK = 304
    SLASH = 305
    EQEQ = 306      # ==
    NOTEQ = 307     # !=
    LT = 308        # <
    LTEQ = 309      # <=
    GT = 310        # >
    GTEQ = 311      # >=
    INCREMENT = 312   # ++ 
    DECREMENT = 313   # --
    # -------------------------------- #
    # Logical operators.
    AND = 401       # &&
    OR = 402        # ||
    NOT = 403       # !
    