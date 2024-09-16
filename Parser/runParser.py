import sys
from Lexer import *
from Parser import *
from utils import error


def main():
        source_code = """
        {
            set sum = "lpc" 
        }
        
        sum = 10
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