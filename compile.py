from lexicalAnalysis.lexer import *
from syntaxAnalysis.parser import *
from emitter import *
import sys

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
    print("Glitchy Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(f"source/{sys.argv[1]}", 'r') as inputFile:
        source = inputFile.read()
        
    # Initialize the lexer, emitter, and parser.
    lexer = Lexer(source,abort)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter, abort, True)


    parser.program() # Start the parser.
    # emitter.writeFile() # Write the output to file.
    print("Compiling completed.")

main()
    