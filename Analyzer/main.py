from Lexer import Lexer
from Parser import Parser
from Analyzer import SemanticAnalyzer

def main():
    source_code = """
    set x = 5
    set y = 10
    set t = "hello chutiya"
    if (x > 0 ) {
        set z = x + y
        print("x is positive")
    }
    z = 30
    """

    # Tokenize the source code
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    print("AST from parser:")
    ast.print_content()
    print("\n\n")
    
    try:
        # Run semantic analysis
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()
    except Exception as e:
        # analyzer will format the error message. Just print it
        print(f"{e}")

if __name__ == "__main__":
    main()
