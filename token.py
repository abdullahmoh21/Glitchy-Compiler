from enum import Enum

class Token:
    def __init__(self, type, value):
        self.type = type      # type of the token
        self.value = value    # value of the token
        
    @staticmethod
    def checkIfKeyword(tokenText):
        for type in TokenType:
            # Relies on all keyword enum values being 1XX.
            if type.name == tokenText and type.value >= 100 and type.value < 200:
                return type
        return None

# TokenType is our enum for all the types of tokens.
class TokenType(Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201        # =
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206      # ==
    NOTEQ = 207     # !=
    LT = 208        # <
    LTEQ = 209      # <=
    GT = 210        # >
    GTEQ = 211      # >=
