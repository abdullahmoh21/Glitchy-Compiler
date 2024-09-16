from Lexer import Lexer
from Parser import Parser
from Analyzer import SemanticAnalyzer
from utils import error

def main():
    source_code = """
   
    """


    # Tokenize the source code
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    if ast:
        print("\nParser returned:")
        ast.print_content()

    # Run semantic analysis
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if not (error.has_error_occurred() or symbol_table is None):
        print("Analyzing completed")
        print("\nAnalyzer returned:\n")
        ast.print_content()
        print("\nThe following Symbol table was returned:\n")
        symbol_table.print_table()

if __name__ == "__main__":
    main()
