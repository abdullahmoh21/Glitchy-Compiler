from collections import deque

class SymbolTable:
    def __init__(self):
        self.scopes = deque([(0, {})])  # Initialize with global scope
        self.current_scope_index = 0  
        self.scope_pointer_stack = [self.current_scope_index]  # Stack to manage scope pointers
        self.unique_scope_id = 1  

    def createScope(self):
        self.scopes.append((self.unique_scope_id, {}))
        self.unique_scope_id += 1
        
        # Push new scope index onto the stack
        self.scope_pointer_stack.append(len(self.scopes) - 1)
        self.current_scope_index = self.scope_pointer_stack[-1]

    def enterScope(self):
        # Check if there are more scopes ahead
        if self.current_scope_index < len(self.scopes) - 1:
            self.current_scope_index += 1
            self.scope_pointer_stack.append(self.current_scope_index)
        else:
            raise Exception("No further scope to enter.")

    def exitScope(self):
        if len(self.scope_pointer_stack) > 1:
            self.scope_pointer_stack.pop()
            self.current_scope_index = self.scope_pointer_stack[-1]
        else:
            raise Exception("Cannot exit global scope.")
        
    def getScopeId(self):
        return self.scopes[self.current_scope_index][0]

    def add(self, name, variableData=None, symbolType=None, functionData=None, parameterData=None):
        current_scope_dict = self.scopes[self.current_scope_index][1]
        
        if name in current_scope_dict:
            raise Exception(f"Symbol '{name}' already declared in this scope")
        
        current_scope_dict[name] = {
            'ref': None,    # alloca or value
            'symbol_type': symbolType,
            'mangled_name': self._mangleVariableName(name) if symbolType == 'variable' else None,
            'variable_data': variableData,      # dict with fields : "data_type", "annotated"
            'function_data': functionData,      # dict with fields : "parameters", "arity", "return_type"
            'parameter_data': parameterData     # dict with fields : "data_type", "function_name"
        }

    def inScope(self, name):
        current_scope_dict = self.scopes[self.current_scope_index][1]
        return current_scope_dict.get(name, None)

    def isGlobal(self, name):
        mangled_name = self.getMangledName(name)
        if mangled_name is not None:
            return mangled_name.endswith('$0')
        return None

    def getFunctionType(self, name):
        function = self.lookup(name)
        if function is None or function.get('symbol_type') != 'function':
            raise Exception(f"Function '{name}' does not exist.")
        return function.get('function_data').get('return_type')

    def getMangledName(self, name):
        symbol = self.lookup(name)
        if symbol is not None:
            return symbol.get('mangled_name')
        return None

    def lookup(self, name):
        # Search from the current scope backward using the pointer stack
        for scope_id in reversed(self.scope_pointer_stack):
            scope_dict = self.scopes[scope_id][1]
            if name in scope_dict:
                return scope_dict[name]
        return None

    def update(self, name, type_info):
        symbol = self.lookup(name)
        if symbol is not None:
            symbol['type'] = type_info
            return
        raise Exception(f"Symbol '{name}' not found in any scope")

    def isDeclared(self, name):
        # Check if the symbol is declared in any scope
        return any(name in scope[1] for scope in self.scopes)

    def print_table(self):
        has_function_data = any('function_data' in info for _, scope_dict in self.scopes for info in scope_dict.values())
        
        for i, (scope_id, scope_dict) in enumerate(self.scopes):
            header = "Global Scope" if i == 0 else f"Scope Level {i} (ID {scope_id}):"
            print(header)
            if has_function_data:
                print("{:<20} {:<15} {:<10} {:<10} {:<20} {:<15}".format('Variable', 'Type', 'Reference', 'Arity', 'Parameters', 'Return Type'))
                print("="*90)
            else:
                print("{:<20} {:<15} {:<10}".format('Symbol Name', 'Type', 'Reference'))
                print("="*45)
            
            for name, info in scope_dict.items():
                symbol_type = info.get('symbol_type', 'n/a') or 'n/a'
                ref = info.get('ref', 'n/a') or 'n/a'
                if has_function_data and symbol_type == 'function':
                    function_data = info.get('function_data', {})
                    arity = function_data.get('arity', 'n/a') or 'n/a'
                    parameters = function_data.get('parameters', 'n/a') or 'n/a'
                    if isinstance(parameters, list):
                        parameters = ', '.join(param.name for param in parameters) if parameters else 'n/a'
                    return_type = function_data.get('return_type', 'n/a') or 'n/a'
                    print(f"{name:<20} {symbol_type:<15} {ref:<10} {arity:<10} {parameters:<20} {return_type:<15}")
                    
                    # Print each parameter as a separate row with function name in brackets
                    if isinstance(function_data.get('parameters'), list):
                        for param in function_data['parameters']:
                            param_info = self.lookup(param.name)
                            if param_info:
                                param_ref = param_info.get('ref', 'n/a') or 'n/a'
                                function_name = name  # Use the current function name
                                print(f"{param.name}({function_name}):<20 {'parameter':<15} {param_ref:<10}")
                else:
                    print(f"{name:<20} {symbol_type:<15} {ref:<10}")
            
            if has_function_data:
                print("="*90)
                print("\n")
            else:
                print("="*45)      
                print("\n")
                
    def get_type(self, name):
        symbol = self.lookup(name)
        symbol_type = symbol.get('symbol_type')
        
        if symbol_type == 'parameter':
            return symbol.get('parameter_data').get('data_type')
        elif symbol_type == 'function':
            return symbol.get('function_data').get('return_type')
        elif symbol_type == 'variable':
            return symbol.get('variable_data').get('data_type') 
        
    def setReference(self, var_name, ref):
        var_info = self.lookup(var_name)
        if var_info:
            print(f"var: {var_name}, reference: {ref}")
            var_info['ref'] = ref
        else:
            raise ValueError(f"Variable '{var_name}' not found.")

    def getReference(self, var_name):
        var_info = self.lookup(var_name)
        if var_info and 'ref' in var_info:
            return var_info['ref']
        else:
            raise ValueError(f"Reference for variable '{var_name}' not found.")
        
    def _mangleVariableName(self, name):
        return f"{name}${self.getScopeId()}"

    def _mangleFunctionName(self, name, params, return_type):
        pass