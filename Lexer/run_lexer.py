from .lexer import *
import sys
import os

#  eventually this will be the main function, that includes bash scripting to exec out.c
def main():
    print("Glitchy Lexer")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    
    # Change the working directory to the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
        
    
    with open(f"{sys.argv[1]}", 'r') as inputFile:
        source = inputFile.read()
        
    # Initialize the lexer and print generated tokens.
    lexer = Lexer(source)
    token = lexer.getToken()
    while token.type != TokenType.EOF:
        print(f"Token: {token.type.name}, Value: {repr(token.value)}")
        token = lexer.getToken()

main()
    