import unittest
import sys
import os

# Adjust sys.path to include the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
sys.path.insert(0, parent_dir)

from scanning.lexer import *
from parsing.parser import *
from parsing.glitchAst import *

# Global function for reporting errors
def abort(message, type="Unknown", lineNumber=None, line=None):
    error_message = f"{type}Error: {message}"
    if lineNumber is not None:
        error_message += f" at line {lineNumber}:"
    if line is not None:
        error_message += f"\n{line}"
    print(error_message)

# Unit test class
class TestParser(unittest.TestCase):
    def test_simple_set_and_print(self):
        source_code = '''
        set x = 42
        print("Hello, world")
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(42)),
            Print(String("Hello, world"))
        ])
        self.run_test(source_code, expected_ast)

    def test_if_statement(self):
        source_code = '''
        set x = 10
        if (x == 10) {
            print("x is ten")
        }
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(10)),
            If(
                Comparison(VariableReference("x"), "==", Number(10)),
                Block([
                    Print(String("x is ten"))
                ])
            )
        ])
        self.run_test(source_code, expected_ast)
        
    def test_nested_if_statement(self):
        source_code = '''
        set x = 10
        if (x > 1) {
            if (x > 5) {
                if (x == 10) {
                    print("x is ten")
                }
            }
        }
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(10)),
            If(
                Comparison(VariableReference("x"), ">", Number(1)),
                Block([
                    If(
                        Comparison(VariableReference("x"), ">", Number(5)),
                        Block([
                            If(
                                Comparison(VariableReference("x"), "==", Number(10)),
                                Block([
                                    Print(String("x is ten"))
                                ])
                            )
                        ])
                    )
                ])
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_while_loop(self):
        source_code = '''
        set x = 0
        while (x < 10) {
            x = x + 1
        }
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(0)),
            While(
                Comparison(VariableReference("x"), "<", Number(10)),
                Block([
                    VariableUpdated("x", Expression(
                        VariableReference("x"), "+", Number(1)
                    ))
                ])
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_for_loop(self):
        source_code = '''
        for (i = 0; i < 10; i++) {
            print("Looping")
        }
        '''
        expected_ast = Program([
            For(
                VariableDeclaration("i", Number(0)),  # Initialization
                Comparison(VariableReference("i"), "<", Number(10)),  # Condition
                "++",  # Increment
                Block([
                    Print(String("Looping"))
                ])  # Body
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_input_statement(self):
        source_code = '''
        input foo
        print(foo)
        '''
        expected_ast = Program([
            Input(VariableDeclaration("foo", None)),  # Changed from "null" to None for input
            Print(VariableReference("foo"))
        ])
        self.run_test(source_code, expected_ast)

    def test_complex_expression(self):
        source_code = '''
        set result = (a + b) * (c - d) / e
        '''
        expected_ast = Program([
            VariableDeclaration("result", 
                Expression(
                    Expression(
                        Expression(
                            VariableReference("a"), "+", VariableReference("b")
                        ),
                        "*",
                        Expression(
                            VariableReference("c"), "-", VariableReference("d")
                        )
                    ),
                    "/",
                    VariableReference("e")
                )
            )
        ])
        self.run_test(source_code, expected_ast)

    # Additional tests
    def test_missing_variable(self):
        source_code = '''
        print(x)
        '''
        expected_ast = Program([
            Print(VariableReference("x"))
        ])
        self.run_test(source_code, expected_ast)

    def test_uninitialized_variable(self):
        source_code = '''
        set x = y + 1
        '''
        expected_ast = Program([
            VariableDeclaration("x", Expression(
                VariableReference("y"), "+", Number(1)
            ))
        ])
        self.run_test(source_code, expected_ast)

    def test_nested_blocks(self):
        source_code = '''
        set x = 1
        if (x == 1) {
            set y = 2
            if (y == 2) {
                print("y is two")
            }
        }
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(1)),
            If(
                Comparison(VariableReference("x"), "==", Number(1)),
                Block([
                    VariableDeclaration("y", Number(2)),
                    If(
                        Comparison(VariableReference("y"), "==", Number(2)),
                        Block([
                            Print(String("y is two"))
                        ])
                    )
                ])
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_expression_with_parentheses(self):
        source_code = '''
        set result = (a + (b * c) - d) / e
        '''
        expected_ast = Program([
            VariableDeclaration("result", 
                Expression(
                    Expression(
                        Expression(
                            VariableReference("a"),
                            "+",
                            Expression(
                                Expression(
                                    VariableReference("b"), "*", VariableReference("c")
                                ),
                                "-",
                                VariableReference("d")
                            )
                        ),
                        "/",
                        VariableReference("e")
                    )
                )
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_empty_block(self):
        source_code = '''
        set x = 10
        if (x > 5) {
        }
        '''
        expected_ast = Program([
            VariableDeclaration("x", Number(10)),
            If(
                Comparison(VariableReference("x"), ">", Number(5)),
                Block([])  # Empty block
            )
        ])
        self.run_test(source_code, expected_ast)

    def test_for_loop_with_complex_update(self):
        source_code = '''
        for (i = 0; i < 10; i = i + 2) {
            print("Looping")
        }
        '''
        expected_ast = Program([
            For(
                VariableDeclaration("i", Number(0)),
                Comparison(VariableReference("i"), "<", Number(10)),
                Expression(
                    VariableReference("i"), "+", Number(2)
                ),
                Block([
                    Print(String("Looping"))
                ])
            )
        ])
        self.run_test(source_code, expected_ast)
    
    def run_test(self, source_code, expected_ast):
        lexer = Lexer(source_code, abort)
        parser = Parser(lexer, abort)
        generated_ast = parser.program()
        
        if generated_ast is not None:
            print("Generated AST:")
            generated_ast.print_content()
        
        print("Expected AST:")
        expected_ast.print_content()
        
        if not TestParser.compare_ast(generated_ast, expected_ast):
            self.fail("\n[ERROR] Generated AST does not match expected AST\n")
    
    @staticmethod
    def compare_ast(node1, node2, path=""):
        if type(node1) != type(node2):
            print(f"Type mismatch at {path}: {type(node1).__name__} != {type(node2).__name__}")
            return False

        if isinstance(node1, Program):
            if len(node1.statements) != len(node2.statements):
                print(f"Number of statements mismatch at {path}: {len(node1.statements)} != {len(node2.statements)}")
                return False
            for i, (stmt1, stmt2) in enumerate(zip(node1.statements, node2.statements)):
                if not TestParser.compare_ast(stmt1, stmt2, path + f".statements[{i}]"):
                    return False

        elif isinstance(node1, VariableDeclaration):
            if node1.name != node2.name:
                print(f"VariableDeclaration name mismatch at {path}: {node1.name} != {node2.name}")
                return False
            if not TestParser.compare_ast(node1.value, node2.value, path + ".value"):
                print(f"VariableDeclaration's value mismatch at {path}: {node1.value} != {node2.value}")
                return False

        elif isinstance(node1, VariableUpdated):
            if node1.name != node2.name:
                print(f"VariableUpdated name mismatch at {path}: {node1.name} != {node2.name}")
                return False
            if not TestParser.compare_ast(node1.value, node2.value, path + ".value"):
                print(f"VariableUpdated's value mismatch at {path}: {node1.value} != {node2.value}")
                return False

        elif isinstance(node1, VariableReference):
            if node1.name != node2.name:
                print(f"VariableReference name mismatch at {path}: {node1.name} != {node2.name}")
                return False

        elif isinstance(node1, Print):
            if not TestParser.compare_ast(node1.expression, node2.expression, path + ".expression"):
                return False

        elif isinstance(node1, If):
            if not TestParser.compare_ast(node1.comparison, node2.comparison, path + ".comparison"):
                return False
            if len(node1.statements) != len(node2.statements):
                print(f"Number of body statements mismatch at {path}: {len(node1.statements)} != {len(node2.statements)}")
                return False
            for i, (stmt1, stmt2) in enumerate(zip(node1.statements, node2.statements)):
                if not TestParser.compare_ast(stmt1, stmt2, path + f".statements[{i}]"):
                    return False

        elif isinstance(node1, While):
            if not TestParser.compare_ast(node1.comparison, node2.comparison, path + ".comparison"):
                return False
            if len(node1.statements) != len(node2.statements):
                print(f"Number of body statements mismatch at {path}: {len(node1.statements)} != {len(node2.statements)}")
                return False
            for i, (stmt1, stmt2) in enumerate(zip(node1.statements, node2.statements)):
                if not TestParser.compare_ast(stmt1, stmt2, path + f".statements[{i}]"):
                    return False

        elif isinstance(node1, For):
            if not TestParser.compare_ast(node1.variable, node2.variable, path + ".variable"):
                return False
            if not TestParser.compare_ast(node1.comparison, node2.comparison, path + ".comparison"):
                return False
            if node1.increment != node2.increment:
                print(f"Increment mismatch at {path}: {node1.increment} != {node2.increment}")
                return False
            if len(node1.statements) != len(node2.statements):
                print(f"Number of body statements mismatch at {path}: {len(node1.statements)} != {len(node2.statements)}")
                return False
            for i, (stmt1, stmt2) in enumerate(zip(node1.statements, node2.statements)):
                if not TestParser.compare_ast(stmt1, stmt2, path + f".statements[{i}]"):
                    return False


        elif isinstance(node1, Input):
            if not TestParser.compare_ast(node1.var_name, node2.var_name, path + ".var_name"):
                return False

        elif isinstance(node1, Comparison):
            if not TestParser.compare_ast(node1.left, node2.left, path + ".left"):
                return False
            if node1.operator != node2.operator:
                print(f"Operator mismatch at {path}.operator: {node1.operator} != {node2.operator}")
                return False
            if not TestParser.compare_ast(node1.right, node2.right, path + ".right"):
                return False

        elif isinstance(node1, Expression):
            if not TestParser.compare_ast(node1.left, node2.left, path + ".left"):
                return False
            if node1.operator != node2.operator:
                print(f"Operator mismatch at {path}.operator: {node1.operator} != {node2.operator}")
                return False
            if not TestParser.compare_ast(node1.right, node2.right, path + ".right"):
                return False

        elif isinstance(node1, Term):
            if not TestParser.compare_ast(node1.left, node2.left, path + ".left"):
                return False
            if node1.operator != node2.operator:
                print(f"Operator mismatch at {path}.operator: {node1.operator} != {node2.operator}")
                return False
            if not TestParser.compare_ast(node1.right, node2.right, path + ".right"):
                return False

        elif isinstance(node1, Unary):
            if node1.operator != node2.operator:
                print(f"Unary operator mismatch at {path}: {node1.operator} != {node2.operator}")
                return False
            if not TestParser.compare_ast(node1.operand, node2.operand, path + ".operand"):
                return False

        elif isinstance(node1, Primary):
            if not TestParser.compare_ast(node1.value, node2.value, path + ".value"):
                return False
        
        elif isinstance(node1, Number):
            if node1.value != node2.value:
                print(f"Number value mismatch at {path}: {node1.value} != {node2.value}")
                return False
        
        elif isinstance(node1, String):
            if node1.value != node2.value:
                print(f"String value mismatch at {path}: {node1.value} != {node2.value}")
                return False


        else:
            print(f"Unsupported node type at {path}: {type(node1).__name__}")
            return False

        return True
