from Lexer import Lexer
from Parser import Parser
from Analyzer import SemanticAnalyzer

def main():
    source_code = """
        function add(x,y){
            return x+y
        }
        
        add(x,y)
    
    
    """

    # Tokenize the source code
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    print("AST from parser:")
    ast.print_content()
    print("\n\n")
    
    # Run semantic analysis
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()
    print("Analyzing completed")

if __name__ == "__main__":
    main()
