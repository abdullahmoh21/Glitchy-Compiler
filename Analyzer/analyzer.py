from Error import *
from Ast import *
from .methodTable import get_methods


class SemanticAnalyzer:
    def __init__(self, ast):
        self.ast = ast
        self.symbol_table = SymbolTable()
        
        # node context
        self.func_name = None
        self.func_params = None
        self.func_return_type = None

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
            raise SemanticError({e})     
        
        print("\n\n")
        self.symbol_table.print_table()
        return self.symbol_table
        
    def visit_program(self, node):
        for statement in node.statements:
            if statement is not None:
                statement.accept(self)

    def visit_block(self, node):
        self.symbol_table.createScope()
        for statement in node.statements:
            if statement is not None:
                statement.accept(self)
        self.symbol_table.exitScope()
        
    def visit_variable(self, node):
        if isinstance(node, VariableDeclaration): 
            if self.symbol_table.inScope(node.name) is not None:
                report(f"Variable '{node.name}' is already defined.", type="Variable Declaration", line=node.line)
                return 
            else:
                node.value.accept(self)
                data_type = node.evaluateType()
                
                if node.annotation is not None:
                    if node.annotation != data_type:
                        report(f"Variable '{node.name}' expects type '{node.annotation} but got expression: '{node.value}' of type '{data_type}'", type="Type", line=node.line)
                        return
                
                self.symbol_table.add(
                    name=node.name,
                    symbolType='variable',
                    variableData={
                        'data_type':data_type,
                        'annotated': True if node.annotation is not None else False
                    }
                )

        elif isinstance(node, VariableUpdated):
            var = self.symbol_table.lookup(node.name)
            if var is None or var['variable_data'] is None:
                report(f"Variable '{node.name}' has not been defined.", type="Variable Update")
                return
            
            node.value.accept(self)
            data_type = node.evaluateType()
            
            var_data = var.get('variable_data')
            if var_data.get('annotated') is True:
                expected_type = var_data.get('data_type') 
                if expected_type != data_type:
                    report(f"Variable '{node.name}' expects type '{expected_type}' but got expression: '{node.value}' of type '{data_type}'", type="Type", line=node.line)
                    return
            
            self.symbol_table.update(node.name, data_type)

        elif isinstance(node, VariableReference):                
            if not self.symbol_table.lookup(node.name):
                report(f"Variable '{node.name}' (Line number: {node.line}) is used before it is defined.", type="Variable Reference")
                return
            
            # set type tag so that expression types can be inferred directly without having to lookup value
            var_type = self.symbol_table.get_type(node.name)
            node.type = var_type
            print(f"Variable {node.name} visited. Type set to: {var_type}")
    
    def visit_print(self, node):
        node.value.accept(self)
        
    def visit_if(self, node):
        node.comparison.accept(self)
        self.ensure_boolean_context(node.comparison)
        
        node.block.accept(self)
        
        if node.elifNodes is not None:
            for elif_comparison, elif_block in node.elifNodes:
                elif_comparison.accept(self)
                self.ensure_boolean_context(elif_comparison)
                elif_block.accept(self)
        
        if node.elseBlock is not None:
            node.elseBlock.accept(self)

    def visit_while(self, node):
        self.ensure_boolean_context(node.comparison)
        node.comparison.accept(self)
        node.block.accept(self)

    def visit_input(self, node):
        if not self.symbol_table.isDeclared(node.varRef.name):
            self.symbol_table.add(node.varRef.name, symbolType='string')   # input() always returns a string
            
    # TODO: rename
    def visit_method_call(self, node):
        if not self.symbol_table.isDeclared(node.varRef.name):
            report(f"Variable '{node.varRef.name}' is not defined", type="Method Call", line=node.line)
            return

        var_type = node.varRef.evaluateType()
        method_dict = get_methods(var_type)
        
        if node.name not in method_dict:
            report(f"Method '{node.name}' is not available for type '{var_type}'", type="Method Call", line=node.line)
            return
        
        method_signature = method_dict[node.name]
        expected_arg_types = self.parse_signature(method_signature)
        
        if len(node.arguments) != len(expected_arg_types):
            report(f"Method '{node.name}' expects {len(expected_arg_types)} arguments but got {len(node.arguments)}", type="Method Call", line=node.line)
            return

        for arg, expected_type in zip(node.arguments, expected_arg_types):
            if arg.type != expected_type:
                report(f"Argument '{arg}' does not match expected type '{expected_type}' for method '{node.name}'", type="Method Call", line=node.line)
    
    def visit_function_declaration(self, node):
        if self.symbol_table.lookup(node.name) is not None:
            report(f"The symbol name '{self.name}' already exists. Please rename.", type="Function Declaration", line=node.line)
            return 
        
        self.symbol_table.add(
            name=node.name, 
            symbolType="function", 
            functionData={
                "parameters": node.parameters,
                "arity": node.arity, 
                "return_type": node.return_type
            }
        )
        
        self.symbol_table.createScope()
        
        for parameter in node.parameters:
            self.symbol_table.add(
                name = parameter.name,
                symbolType = 'parameter',
                parameterData = {
                    'data_type': parameter.type,
                    'function_name': node.name
                }
            )
            
        self.func_name = node.name
        self.func_params = node.parameters
        self.func_return_type = node.return_type
        
        
        for statement in node.block.statements:
            statement.accept(self)
            
        self.symbol_table.exitScope()
        
        self.func_name = None
        self.func_params = None
        self.func_return_type = None
        
    def visit_return(self, node):
        node.value.accept(self)
        
        inferred_type = node.evaluateType()
        
        if inferred_type != self.func_return_type:
            report(f"Expected return of type '{self.func_return_type}' for function '{self.func_name}' got: '{inferred_type}' instead.",type="Return", line=node.line)
            self.symbol_table.exitScope()
            return
        
    def visit_parameter(self, node):
        if not self.symbol_table.lookup(node.name):
            report(f"Parameter '{node.name}' can only be used inside its function body.", type="Parameter Reference")
            return
        
    def visit_function_call(self, node):
        func_name = node.name
        symbol = self.symbol_table.lookup(func_name)
        
        if symbol and 'function_data' in symbol:
            function = symbol['function_data']
        else:
            report(f"A function with name '{node.name}' does not exists.", type="Function Call", line=node.line)
            return
        
        if node.arity != function.get('arity'):
            report(f"Function '{func_name}' expects {function['arity']} arguments but received {node.arity} arguments", type="Node Call", line=node.line)
        
        for received_arg, expected_arg in zip(node.arguments, function.get('parameters')):
            received_arg.value.accept(self)
            received_arg_type = received_arg.value.evaluateType()
            if received_arg_type != expected_arg.type:
                report(f"Expected type '{expected_arg.type}' for parameter '{expected_arg.name}' got type '{received_arg.type}'",type="Parameter",line=node.line)
        
        # to make generators life easier
        node.type = function.get('return_type', None) 
           
    def visit_comparison(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)
    
    # TODO: add illegal math op checks like x / 0
    def visit_binary_op(self, node):
        node.left.accept(self)
        node.right.accept(self)
        self.check_type_compatibility(node.left, node.right, node.operator)
        
    def visit_logical_op(self, node):
        node.left.accept(self)
        node.right.accept(self)
        
        self.check_type_compatibility(node.left, node.right, node.operator)
        
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
        operand_type = left.evaluateType()

        if operator == '!':
            if operand_type != 'boolean':
                report(f"Illegal operation: {operator} {operand_type}", type="Type", line=operand.line)
                return
        elif operator == '-' or operator == '+':
            if operand_type not in ['integer', 'float']:
                report(f"Illegal operation: {operator} {operand_type}", type="Type", line=operand.line)
                return
        else:
            report(f"Unknown unary operator: {operator}", type="Type", line=operand.line)
            return
        
    def check_type_compatibility(self, left, right, operator):
        # TODO: add err for 'invalid' returned
        left_type = left.evaluateType()
        right_type = right.evaluateType()

        # Handle binary operations
        if operator in ['/', '*', '+', '-']:
            if left_type not in ['integer', 'float'] or right_type not in ['integer', 'float']:
                report(f"Illegal Binary operation: '{left_type}' '{operator}' '{right_type}'", type="Type", line=left.line)

        # Handle comparisons
        elif operator in ['==', '!=', '<', '<=', '>', '>=']:
            if left_type != right_type:
                report(f"Type mismatch in comparison: '{left_type}' '{operator}' '{right_type}'", type="Type", line=left.line)
            elif left_type not in ['integer', 'float']:
                report(f"Invalid types for comparison: '{left_type}' '{operator}' '{right_type}'", type="Type", line=left.line)

        # Handle logical operations
        elif operator in ['&&', '||']:
            if left_type != 'boolean' or right_type != 'boolean':
                report(f"Logical operation does not result in boolean: '{left_type}' '{operator}' '{right_type}'\n\t {left} {operator} {right}", type="Type Error", line=left.line)

    def ensure_boolean_context(self, node):
        expression_type = node.evaluateType()
        if expression_type != 'boolean':
            formattedType = "Invalid" if (expression_type is None) else expression_type
            report(f"(ensure_boolean_context) Expression does not evaluate to boolean but to: '{formattedType}'\n\t {node.left} {node.operator} {node.right}\n", type="Type", line=node.line)