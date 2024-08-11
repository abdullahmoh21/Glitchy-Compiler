from Error import *
from Ast import *
from .methodTable import get_methods


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()

    def analyze(self):
        if error.has_error_occurred():
            print("Parsing errors occurred. Cannot proceed with semantic analysis.")
            return
        
        if self.ast is None or self.symbol_table is None:
            print("No AST or symbol table to analyze.")
            return
        try:
            self.ast.accept(self)
        except Exception as e:
                raise SemanticError(f"{e}")     
        
        print("\n\n")
        self.symbol_table.print_table()
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
        if isinstance(node,VariableDeclaration):
            if self.symbol_table.lookup(node.name) is not None:
                report(f"Variable '{node.name}' (Line number: {node.line}) is already defined.", type="Variable Declaration", lineNumber=node.line)
                return 
            else:
                # Determine the type from the initial value
                var_type = node.type
                self.symbol_table.add(node.name, var_type)

        elif isinstance(node, VariableUpdated):
            if not self.symbol_table.is_declared(node.name):
                report(f"Variable '{node.name}' (Line number: {node.line}) has not been defined.", type="Variable Update")
                return
            elif self.symbol_table.lookup(node.name) is None:
                report(f"Variable '{node.name}' (Line number: {node.line}) is not in scope.", type="Variable Update")
                return
            else:
                # Update the type based on the new value
                var_type = node.type
                self.symbol_table.update(node.name, var_type)
                node.value.accept(self)
                print(f"Updated variable '{node.name}' to type '{var_type}'.")

        elif isinstance(node, VariableReference):
            if not self.symbol_table.is_declared(node.name):
                report(f"Variable '{node.name}' (Line number: {node.line}) is used before it is defined.", type="Variable Reference")
                return

    def visit_print(self, node):
        node.expression.accept(self)
        
    def visit_if(self, node):
        self.ensure_boolean_context(node.comparison)
        node.comparison.accept(self)
        
        node.block.accept(self)
        
        if node.elifNodes is not None:
            for elif_comparison, elif_block in node.elifNodes:
                self.ensure_boolean_context(elif_comparison)
                elif_comparison.accept(self)
                elif_block.accept(self)
        
        if node.elseBlock is not None:
            node.elseBlock.accept(self)

    def visit_while(self, node):
        self.ensure_boolean_context(node.comparison)
        node.comparison.accept(self)
        node.block.accept(self)

    def visit_input(self, node):
        if not self.symbol_table.is_declared(node.varRef.name):
            self.symbol_table.add(node.varRef.name, symbolType='string')   # input() always returns a string

    # native methods like strVar.toInteger()
    def visit_method_call(self, node):
        if not self.symbol_table.is_declared(node.varRef.name):
            report(f"Variable '{node.varRef.name}' is not defined", type="Method Call", lineNumber=node.line)
            return

        var_type = node.varRef.type
        method_dict = get_methods(var_type)
        
        if node.name not in method_dict:
            report(f"Method '{node.name}' is not available for type '{var_type}'", type="Method Call", lineNumber=node.line)
            return
        
        # Get the method signature
        method_signature = method_dict[node.name]
        
        # Parse the signature to extract argument types
        expected_arg_types = self.parse_signature(method_signature)
        
        
        # validate arity
        if len(node.arguments) != len(expected_arg_types):
            report(f"Method '{node.name}' expects {len(expected_arg_types)} arguments but got {len(node.arguments)}", type="Method Call", lineNumber=node.line)
            return

        # Validate argument types
        for arg, expected_type in zip(node.arguments, expected_arg_types):
            if arg.type != expected_type:
                report(f"Argument '{arg}' does not match expected type '{expected_type}' for method '{node.name}'", type="Method Call", lineNumber=node.line)
    
    def visit_function_declaration(self,function):
        if self.symbol_table.lookup(function.name) is not None:
            report(f"The symbol name '{self.name}' already exists. Please rename.", type="Function Declaration", lineNumber=function.line)
            return 
        
        self.symbol_table.add(name=function.name,symbolType="function", functionData={"parameters": function.parameters, "arity": function.arity, "return_type": function.return_type})
        
        self.symbol_table.enter_scope()
        
        for parameter in function.parameters:
            self.symbol_table.add(name=parameter, symbolType="parameter")
        
        for statement in function.block.statements:
            if statement is not None:
                statement.accept(self)
            
        self.symbol_table.exit_scope()
    
    def visit_function_call(self,functionCall):
        symbol = self.symbol_table.lookup(functionCall.name)

        if symbol and 'functionData' in symbol:
            function = symbol['functionData']
        else:
            report(f"A function with name '{functionCall.name}' does not exists.", type="Function Declaration", lineNumber=functionCall.line)
            return
        
        if function['arity'] != functionCall.arity:
            report(f"Function '{functionCall.name}' expects {function['arity']} arguments but received {functionCall.arity} arguments", type="Function Call", lineNumber=functionCall.line)
        
    def visit_return(self, node):
        node.value.accept(self)

    def visit_comparison(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)
    
    def visit_binary_op(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)

    def visit_logical_op(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)

        if node.type != 'boolean':
            report(f"Logical operation does not result in boolean: {node.left.type} {node.operator} {node.right.type}", type="Type Error", lineNumber=node.line)
            return
    
    def visit_unary(self, node):
        node.operand.accept(self)
        self.check_unary_type_compatibility(node.operand, node.operator)
        
    def visit_integer(self, node):
        pass
    
    def visit_float(self, node):
        pass

    def visit_boolean(self, node):
        pass

    def visit_string(self, node):
        pass

    def visit_null(self, node):
        pass
    
    def parse_signature(self, signature):
        """Parse the method signature to extract the expected argument types."""
        
        # Extract the part inside the parentheses
        args_string = signature.split('(')[1].split(')')[0]
        
        if not args_string:
            return []  # No arguments expected
        
        # Split arguments and extract their types
        arg_types = [arg.split()[0] for arg in args_string.split(',')]
        
        return arg_types

    def check_unary_type_compatibility(self, left, operator):
        operand_type = left.type

        if operator == '!':
            if operand_type != 'boolean':
                report(f"Illegal operation: {operator} {operand_type}", type="Type", lineNumber=operand.line)
                return
        elif operator == '-' or operator == '+':
            if operand_type not in ['integer', 'float']:
                report(f"Illegal operation: {operator} {operand_type}", type="Type", lineNumber=operand.line)
                return
        else:
            report(f"Unknown unary operator: {operator}", type="Type", lineNumber=operand.line)
            return
        
    def check_type_compatibility(self, left, right, operator):
        left_type = left.type
        print(f"Left type in check_type_compatibility: {left_type}")
        right_type = right.type
        print(f"Right type in check_type_compatibility: {right_type}")
        
        # Un resolved types
        if left_type == 'dynamic' or right_type == 'dynamic':
            return

        # Arithmetic operations
        if operator in ['/', '*', '+', '-']:
            if left_type not in ['integer', 'float'] or right_type not in ['integer', 'float']:
                report(f"Illegal operation: {left_type} {operator} {right_type}", type="Type", lineNumber=left_node.line)
                return

        # Comparisons
        elif operator in ['==', '!=', '<', '<=', '>', '>=']:
            if left_type != right_type:
                report(f"Type mismatch in comparison: {left_type} {operator} {right_type}", type="Type", lineNumber=left_node.line)
                return
            elif left_type not in ['integer', 'float']:
                report(f"Invalid types for comparison: {left_type} {operator} {right_type}", type="Type", lineNumber=left_node.line)
                return

        # Boolean operations
        elif operator in ['&&', '||']:
            if left_type != 'boolean' or right_type != 'boolean':
                report(f"Type mismatch in logical operation: {left_type} {operator} {right_type}", type="Type", lineNumber=left_node.line)
                return

    def ensure_boolean_context(self, node):
        expression_type = node.type
        if expression_type != 'boolean':
            formattedType = "Invalid" if (expression_type == 'unknown' or expression_type == None) else expression_type
            report(f"(ensure_boolean_context) Expression does not evaluate to boolean but to: {expression_type}\n\t {node.left} {node.operator} {node.right}\n",
                   type="Type", 
                   lineNumber=node.line
            )
            return
    