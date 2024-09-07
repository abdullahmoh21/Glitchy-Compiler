from .lexer import *
import sys
import os

def main():
    source = """ 
        print("your input: "+input())
    """
        
    # Initialize the lexer and print generated tokens.
    lexer = Lexer(source)
    token = lexer.getToken()
    while token.type != TokenType.EOF:
        print(f"Token: {token.type.name}, Value: {repr(token.value)}")
        token = lexer.getToken()

main()
    