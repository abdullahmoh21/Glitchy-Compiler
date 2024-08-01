import sys
import os

# Adjust sys.path to include the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.insert(0, parent_dir)

from scanning.lexer import *
from parsing.parser import *
from parsing.glitchAst import *

# Global function for reporting errors
def abort(message, type="Unknown", lineNumber=None, line=None):
    error_message = f"{type}Error: {message}"
    if lineNumber is not None:
        error_message += f" at line {lineNumber}:"
    if line is not None:
        error_message += f"\n{line}"
    print(error_message)

def main():
        source_code = """
        print(x)
        
        set x=10
        print(y)
        10 = 5
        
        """
        lexer = Lexer(source_code, abort)
        parser = Parser(lexer, abort)
        generated_ast = parser.program()
        
        if generated_ast is not None:
            print("Generated AST:")
            generated_ast.print_content()
        else:
            print("Error: No AST generated.")
            
main()