import unittest
from Error import *
from Ast import *
from SemanticAnalyzer import SemanticAnalyzer

# TODO: edit to check for errors thrown instead of console logs

class SemanticAnalyzerTests(unittest.TestCase):
    
    def test_analyze_no_errors(self):
        # Create a valid AST
        ast = Program([
            VariableDeclaration('x', 'integer', Integer(5)),
            VariableDeclaration('y', 'integer', Integer(10)),
            VariableUpdated('x', 'integer', Integer(7)),
            VariableReference('x'),
            Print(VariableReference('y'))
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that no errors occurred
        self.assertFalse(error.has_error_occurred())
        
        # Assert that the symbol table is not None
        self.assertIsNotNone(symbol_table)
        
        # Assert that the symbol table contains the expected variables
        self.assertIn('x', symbol_table.symbols)
        self.assertIn('y', symbol_table.symbols)
        
        # Assert that the variables have the expected types
        self.assertEqual(symbol_table.symbols['x'], 'integer')
        self.assertEqual(symbol_table.symbols['y'], 'integer')
        
        # Assert that the variables have been declared and used
        self.assertTrue(symbol_table.isDeclared('x'))
        self.assertTrue(symbol_table.isDeclared('y'))
        self.assertTrue(symbol_table.is_used('x'))
        self.assertTrue(symbol_table.is_used('y'))
        
    def test_analyze_with_errors(self):
        # Create an AST with errors
        ast = Program([
            VariableDeclaration('x', 'integer', Integer(5)),
            VariableDeclaration('x', 'integer', Integer(10)),  # Duplicate variable declaration
            VariableUpdated('y', 'integer', Integer(7)),  # Variable not declared
            VariableReference('z')  # Variable not declared
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that errors occurred
        self.assertTrue(error.has_error_occurred())
        
        # Assert that the symbol table is None
        self.assertIsNone(symbol_table)
        
        # Assert that the expected errors were reported
        self.assertIn("Variable 'x' (Line number: 3) is already defined.", error.get_errors())
        self.assertIn("Variable 'y' (Line number: 4) has not been defined.", error.get_errors())
        self.assertIn("Variable 'z' (Line number: 5) is used before it is defined.", error.get_errors())

    def test_analyze_float_integer_comparison(self):
        # Create a valid AST with float and integer comparison
        ast = Program([
            VariableDeclaration('a', 'float', Float(2.5)),
            VariableDeclaration('b', 'integer', Integer(2)),
            VariableReference('a'),
            VariableReference('b'),
            Print(Comparison(VariableReference('b'), '<', VariableReference('a')))
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that no errors occurred
        self.assertFalse(error.has_error_occurred())
        
        # Assert that the symbol table is not None
        self.assertIsNotNone(symbol_table)
        
        # Assert that the symbol table contains the expected variables
        self.assertIn('a', symbol_table.symbols)
        self.assertIn('b', symbol_table.symbols)
        
        # Assert that the variables have the expected types
        self.assertEqual(symbol_table.symbols['a'], 'float')
        self.assertEqual(symbol_table.symbols['b'], 'integer')
        
        # Assert that the variables have been declared and used
        self.assertTrue(symbol_table.isDeclared('a'))
        self.assertTrue(symbol_table.isDeclared('b'))
        self.assertTrue(symbol_table.is_used('a'))
        self.assertTrue(symbol_table.is_used('b'))
        
    def test_analyze_invalid_comparison(self):
        # Create an AST with invalid comparison
        ast = Program([
            VariableDeclaration('a', 'string', String("hello")),
            VariableDeclaration('b', 'integer', Integer(2)),
            Print(Comparison(VariableReference('a'), '<', VariableReference('b')))
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that errors occurred
        self.assertTrue(error.has_error_occurred())
        
        # Assert that the symbol table is None
        self.assertIsNone(symbol_table)
        
        # Assert that the expected error was reported
        self.assertIn("Invalid types for comparison: string < integer", error.get_errors())

    def test_analyze_logical_operation(self):
        # Create a valid AST with logical operation
        ast = Program([
            VariableDeclaration('a', 'boolean', Boolean(True)),
            VariableDeclaration('b', 'boolean', Boolean(False)),
            Print(LogicalOp(VariableReference('a'), '&&', VariableReference('b')))
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that no errors occurred
        self.assertFalse(error.has_error_occurred())
        
        # Assert that the symbol table is not None
        self.assertIsNotNone(symbol_table)
        
        # Assert that the symbol table contains the expected variables
        self.assertIn('a', symbol_table.symbols)
        self.assertIn('b', symbol_table.symbols)
        
        # Assert that the variables have the expected types
        self.assertEqual(symbol_table.symbols['a'], 'boolean')
        self.assertEqual(symbol_table.symbols['b'], 'boolean')
        
        # Assert that the variables have been declared and used
        self.assertTrue(symbol_table.isDeclared('a'))
        self.assertTrue(symbol_table.isDeclared('b'))
        self.assertTrue(symbol_table.is_used('a'))
        self.assertTrue(symbol_table.is_used('b'))
        
    def test_analyze_invalid_logical_operation(self):
        # Create an AST with invalid logical operation
        ast = Program([
            VariableDeclaration('a', 'integer', Integer(1)),
            VariableDeclaration('b', 'boolean', Boolean(False)),
            Print(LogicalOp(VariableReference('a'), '&&', VariableReference('b')))
        ])
        
        # Create a semantic analyzer
        analyzer = SemanticAnalyzer(ast)
        
        # Analyze the AST
        symbol_table = analyzer.analyze()
        
        # Assert that errors occurred
        self.assertTrue(error.has_error_occurred())
        
        # Assert that the symbol table is None
        self.assertIsNone(symbol_table)
        
        # Assert that the expected error was reported
        self.assertIn("Type mismatch in logical operation: integer && boolean", error.get_errors())

if __name__ == '__main__':
    unittest.main()