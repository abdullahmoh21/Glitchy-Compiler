from lexer import *
from token import TokenType

def main():
    source = "IF+-123 foo*THEN/"
    lexer = Lexer(source)

    token = lexer.getToken()
    while token.type != TokenType.EOF:
        print(token.type)
        token = lexer.getToken()

main()
