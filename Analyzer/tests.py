import unittest
import logging
from Analyzer import SemanticAnalyzer
from Ast import *
from Error.error import *

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class TestSemanticAnalyzer(unittest.TestCase):

    def test_variable_declaration(self):
        ast = Program([
            VariableDeclaration('x', Number(5), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        symbol_table = analyzer.analyze()
        print(f"is declared: {symbol_table.is_declared('x')}")
        print(f"symbols: {symbol_table.declarations}")
        self.assertIn('x', symbol_table.declarations)

    def test_variable_redeclaration(self):
        ast = Program([
            VariableDeclaration('x', Number(5), 1),
            VariableDeclaration('x', Number(10), 2)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(UndefinedVariableError):
            analyzer.analyze()

    def test_variable_update(self):
        ast = Program([
            VariableDeclaration('x', Number(5), 1),
            VariableUpdated('x', Number(10), 2)
        ])
        analyzer = SemanticAnalyzer(ast)
        symbol_table = analyzer.analyze()
        self.assertEqual(symbol_table.lookup('x'), 'number')

        # Test update without declaration
        ast = Program([
            VariableUpdated('y', Number(10), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(UndefinedVariableError):
            analyzer.analyze()

    def test_variable_reference(self):
        ast = Program([
            VariableReference('x', 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(error.UndefinedVariableError):
            analyzer.analyze()

        # Test valid reference
        ast = Program([
            VariableDeclaration('x', Number(5), 1),
            VariableReference('x', 2)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

    def test_type_compatibility(self):
        # Arithmetic operation
        ast = Program([
            Expression(BinaryOp(Number(5), '+', Number(10),1), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

        # Type mismatch in arithmetic
        ast = Program([
                BinaryOp(Number(5), '+', String("test"),1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(Error.TypeError):
            analyzer.analyze()

        # Comparison operation
        ast = Program([
            Comparison(Number(5), '==', Number(10), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

        # Type mismatch in comparison
        ast = Program([
            Comparison(Number(5), '==', String("test"), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(Error.TypeError):
            analyzer.analyze()

        # Boolean operation
        ast = Program([
            BinaryOp(Boolean(True), '&&', Boolean(False),1)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

        # Type mismatch in boolean operation
        ast = Program([
            Expression(BinaryOp(Boolean(True), '&&', Number(5),1), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(Error.TypeError):
            analyzer.analyze()

    def test_scope_handling(self):
        ast = Program([
            Block([
                VariableDeclaration('x', Number(5), 1)
            ]),
            VariableUpdated('x', Number(10), 2)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

        # Test variable out of scope
        ast = Program([
            Block([
                VariableDeclaration('x', Number(5), 1)
            ]),
            Block([
                VariableUpdated('x', Number(10), 2)
            ])
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(Error.UndefinedVariableError):
            analyzer.analyze()

    def test_print_input(self):
        # Test print statement
        ast = Program([
            Print(Expression(Number(5)), 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

        # Test input statement
        ast = Program([
            Input('x', 1)
        ])
        analyzer = SemanticAnalyzer(ast)
        with self.assertRaises(Error.UndefinedVariableError):
            analyzer.analyze()

        # Test input with declaration
        ast = Program([
            VariableDeclaration('x', Number(5), 1),
            Input('x', 2)
        ])
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()

if __name__ == '__main__':
    unittest.main()
