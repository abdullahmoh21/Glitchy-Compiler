import sys
from Lexer import *
from Parser import *


def main():
        source_code = """
        set x = 10
        if (x > 10) {
            print("x is ten")
        }
        """
        lexer = Lexer(source_code)
        parser = Parser(lexer)
        generated_ast = parser.parse()
        
        if generated_ast is not None:
            print("Generated AST:")
            generated_ast.print_content()
        else:
            print("Error: No AST generated.")
            
main()