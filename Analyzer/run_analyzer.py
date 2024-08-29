from Lexer import Lexer
from Parser import Parser
from Analyzer import SemanticAnalyzer
from Error import error

def main():
    source_code = """
        if (typeof(10) == "integer"){
            print("the type is an int! BHENCHOD!!!!!")
        }
    """


    # Tokenize the source code
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()

    # Run semantic analysis
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if error.has_error_occurred() or symbol_table is None:
        print("Analyzer found an error")
    else:
        print("Analyzing completed")
        print("\nThe following AST was returned:\n")
        ast.print_content()
        print("\nThe following Symbol table was returned:\n")
        symbol_table.print_table()

if __name__ == "__main__":
    main()
