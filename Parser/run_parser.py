import sys
from Lexer import *
from Parser import *
from Error import has_error_occurred


def main():
        source_code = """        
            set y = "10"
            if (typeof(y) == "int"){
                print("int")
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