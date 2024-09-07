import sys
from Lexer import *
from Parser import *
from utils import error


def main():
        source_code = """ 
        toPeg = 1
        fromPeg = 0
        num = 1+2+3+4
        print("Move disk 1 from peg " + fromPeg + " to peg " + toPeg)
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