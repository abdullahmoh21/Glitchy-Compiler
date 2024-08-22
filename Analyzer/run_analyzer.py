from Lexer import Lexer
from Parser import Parser
from Analyzer import SemanticAnalyzer

def main():
    source_code = """
        // set x = 10, y = 5, z = 15, w = 20
        // set x = 10, y = 5, z = 15, w = 25 // first elif passed
        // set x = 15, y = 5, z = 15, w = 20 // second elif passed
        // set x = 10, y = 5, z = 15, w = 10 // third elif passed
        
        set x = 1, y = 2, z = 3, w = 4 // nothing passed
        
        if ((x + y) * z > 100 && x < z && w != x){
            print("first if passed")
        }
        elif (x == 10 || (y + z) < x || w > z){
            print("first elif passed")
        } elif (w - y == x && z / y == 3){
            print("second elif passed")
        } elif (x * z == 150 && w / 2 == y){
           print("third elif passed")
        } else{
            print("nothing passed")
        }
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
