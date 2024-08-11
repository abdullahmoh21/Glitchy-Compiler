import sys
from Lexer import *
from Parser import *
from Error import has_error_occurred


def main():
        source_code = """        
        function add(x, y) {
            set sum = x + y
            return "sum"
            return "sum"
        }
        
        set x = add(10,5)
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