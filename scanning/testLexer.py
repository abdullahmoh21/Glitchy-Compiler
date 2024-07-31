from lexicalAnalysis.lexer import *
import sys
import os

# global function for errors
def abort(message,type="Unknown", lineNumber=None,line=None, emitter = None):
    error_message = f"{type}Error: {message}"
    if lineNumber is not None:
        error_message += f" at line {lineNumber}:"
    if line is not None:
        error_message += f"\n{line}"
    if emitter is not None:
        emitter.clearOutput()
    print(error_message,file=sys.stderr)
    sys.exit(1)

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
    lexer = Lexer(source,abort)
    token = lexer.getToken()
    while token.type != TokenType.EOF:
        print(f"Token: {token.type.name}, Value: {repr(token.value)}")
        token = lexer.getToken()

main()
    