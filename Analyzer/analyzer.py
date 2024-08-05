import logging
from Error import *
from Ast import *

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()

    def analyze(self):
        logging.debug("Starting semantic analysis.")
        if error.has_error_occurred():
            logging.error("Parsing errors occurred. Cannot proceed with semantic analysis.")
            return
        
        if self.ast is None or self.symbol_table is None:
            logging.error("No AST or symbol table to analyze.")
            return
        try:
            self.ast.accept(self)
        except Exception as e:
            # let our custom errors pass through. while catching all others as "SemanticError"
            if isinstance(e, (UndefinedVariableError, TypeError)):
                raise
            else:
                raise SemanticError(f"{e}")     
        
        print("Semantic analysis completed successfully.")
        self.symbol_table.print_table()
        self.symbol_table.report_dead_code()
        return self.symbol_table
        
    def visit_program(self, node):
        for statement in node.statements:
            if statement is not None:
                statement.accept(self)

    def visit_block(self, node):
        self.symbol_table.enter_scope()
        for statement in node.statements:
            if statement is not None:
                statement.accept(self)
        self.symbol_table.exit_scope()
        
    def visit_variable(self, node):
        if isinstance(node, VariableDeclaration):
            if self.symbol_table.lookup(node.name) is not None:
                raise error.UndefinedVariableError(f"Variable '{node.name}' (Line number: {node.line}) is already defined.")
            else:
                # Determine the type from the initial value
                var_type = self.get_type(node.value)
                self.symbol_table.add(node.name, var_type)
                self.symbol_table.declare(node.name, node.line)

        elif isinstance(node, VariableUpdated):
            if not self.symbol_table.is_declared(node.name):
                raise error.UndefinedVariableError(f"Variable '{node.name}' (Line number: {node.line}) has not been defined.", node.line)
            elif not self.symbol_table.is_in_scope(node.name):
                raise error.UndefinedVariableError(f"Variable '{node.name}' (Line number: {node.line}) is not in scope.")
            else:
                # Update the type based on the new value
                var_type = self.get_type(node.value)
                self.symbol_table.update(node.name, var_type)
                node.value.accept(self)
                self.symbol_table.mark_as_used(node.name)
                logging.debug(f"Updated variable '{node.name}' to type '{var_type}'.")

        elif isinstance(node, VariableReference):
            if not self.symbol_table.is_declared(node.name):
                raise error.UndefinedVariableError(f"Variable '{node.name}'  (Line number: {node.line}) is used before it is defined.")
            self.symbol_table.mark_as_used(node.name)

    def visit_print(self, node):
        node.expression.accept(self)

    def visit_if(self, node):
        node.comparison.accept(self)
        node.block.accept(self)

    def visit_while(self, node):
        node.comparison.accept(self)
        node.block.accept(self)

    def visit_input(self, node):
        if not self.symbol_table.is_declared(node.var_name):
            raise error.UndefinedVariableError(f"Variable '{node.var_name}' is used before it is defined.", node.line)

    def visit_comparison(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)

    def visit_expression(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)

    def visit_term(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)

    def visit_unary(self, node):
        node.operand.accept(self)
        self.check_unary_type_compatibility(node.operand, node.operator)
        
    def visit_number(self, node):
        pass

    def visit_boolean(self, node):
        pass

    def visit_string(self, node):
        pass

    def visit_null(self, node):
        pass

    def check_type_compatibility(self, left_node, right_node, operator):
        left_type = self.get_type(left_node)
        right_type = self.get_type(right_node)

        # arithmetics
        if operator in ['/', '*', '+', '-']:
            if left_type != 'number' or right_type != 'number':
                raise error.TypeError(f"Illegal operation: {left_type} {operator} {right_type}", type_info=f"{left_type} {operator} {right_type}")

        # comparisons
        elif operator in ['==', '!=', '<', '<=', '>', '>=']:
            if left_type != right_type:
                raise error.TypeError(f"Type mismatch in comparison: {left_type} {operator} {right_type}", type_info=f"{left_type} {operator} {right_type}")

        # boolean operations
        elif operator in ['&&', '||']:
            if left_type != 'boolean' or right_type != 'boolean':
                raise error.TypeError(f"Illegal operation: {left_type} {operator} {right_type}", type_info=f"{left_type} {operator} {right_type}")

    def check_unary_type_compatibility(self, operand, operator):
        operand_type = self.get_type(operand)

        if operator == '!':
            if operand_type != 'boolean':
                raise error.TypeError(f"Illegal operation: {operator} {operand_type}", type_info=f"{operator} {operand_type}")

    def get_type(self, node):
        if isinstance(node, Number):
            return 'number'
        elif isinstance(node, String):
            return 'string'
        elif isinstance(node, Boolean):
            return 'boolean'
        elif isinstance(node, VariableReference):
            var_name = node.name
            if self.symbol_table.is_declared(var_name):
                return self.symbol_table.lookup(var_name)
            return 'undefined'
        elif isinstance(node, Null):
            return 'null'
        elif isinstance(node, Comparison):
            return 'boolean'
        elif isinstance(node, Expression):
            left_type = self.get_type(node.left)
            right_type = self.get_type(node.right)
            if left_type != right_type:
                raise error.TypeError(f"Type mismatch in expression: {left_type} {node.operator} {right_type}", type_info=f"{left_type} {node.operator} {right_type}")
            logging.debug(f"Expression type determined: {left_type}")
            return left_type
        elif isinstance(node, BinaryOp):
            left_type = self.get_type(node.left)
            right_type = self.get_type(node.right)
            if left_type != right_type:
                raise error.TypeError(f"Type mismatch in binary operation: {left_type} {node.operator} {right_type}", type_info=f"{left_type} {node.operator} {right_type}")
            return left_type
        return 'unknown'