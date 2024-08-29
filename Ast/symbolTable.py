from collections import deque

class SymbolTable:
    def __init__(self):
        # Initialize with global scope (id, symbols, parent_id, child_indices)
        self.scopes = deque([(0, {}, None, [])])
        self.current_scope_index = 0
        self.scope_pointer_stack = [self.current_scope_index]  # Stack to manage scope pointers
        self.unique_scope_id = 1
        self.visited_children_stack = [0]  # Stack to manage which children have been visited
    
    def createScope(self):
        # Create a new scope with the current scope as the parent
        new_scope = (self.unique_scope_id, {}, self.current_scope_index, [])
        self.scopes.append(new_scope)
        # Add this new scope's index as a child of the current scope
        self.scopes[self.current_scope_index][3].append(len(self.scopes) - 1)
        self.unique_scope_id += 1
        # Update scope and stacks
        self.current_scope_index = len(self.scopes) - 1
        self.scope_pointer_stack.append(self.current_scope_index)
        self.visited_children_stack.append(0)  # Initialize visited children tracker for the new scope
    
    def enterScope(self):
        if self.visited_children_stack and self.visited_children_stack[-1] < len(self.scopes[self.current_scope_index][3]):
            current_scope = self.scopes[self.current_scope_index]
            child_indices = current_scope[3]
            # Get the next unvisited child index
            next_child_index = child_indices[self.visited_children_stack[-1]]
            self.visited_children_stack[-1] += 1
            # Update scope and stacks
            self.current_scope_index = next_child_index
            self.scope_pointer_stack.append(self.current_scope_index)
            self.visited_children_stack.append(0)  # Initialize visited tracker for the new scope
        else:
            raise Exception("No further unvisited child scope to enter.")
    
    def exitScope(self):
        if len(self.scope_pointer_stack) > 1:
            self.scope_pointer_stack.pop()
            self.visited_children_stack.pop()
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
            'symbol_type': symbolType,          # one of: variable, function, parameter
            'mangled_name': self._mangleVariableName(name) if symbolType == 'variable' else None,
            'variable_data': variableData,      # dict with fields : "value", "data_type", "annotated"
            'function_data': functionData,      # dict with fields : "parameters", "arity", "return_type"
            'parameter_data': parameterData     # dict with fields : "data_type", "function_name"
        }

    def addGlobalFunction(self, name, functionData=None):
        # Assuming that the global scope is always at index 0
        global_scope_dict = self.scopes[0][1]
        
        if name in global_scope_dict:
            raise Exception(f"Symbol '{name}' already declared in the global scope")
        
        global_scope_dict[name] = {
            'ref': None,    
            'symbol_type': 'function',         
            'mangled_name': None,               
            'variable_data': None,             
            'function_data': functionData,     
            'parameter_data': None             
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

    def update(self, name, type_info, value=None):
        symbol = self.lookup(name)
        if symbol is not None:
            symbol['type'] = type_info
            if value is not None: 
                if symbol['symbol_type'] != 'variable':
                    raise Exception(f"Symbol {name} is not a variable so cannot update it's value")
                symbol['variable_data']['value'] = value
            return
        raise Exception(f"Symbol '{name}' not found in any scope")

    def isDeclared(self, name):
        # Check if the symbol is declared in any scope
        return any(name in scope[1] for scope in self.scopes)
   
    def getType(self, name):
        symbol = self.lookup(name)
        symbol_type = symbol.get('symbol_type')
        
        if symbol_type == 'parameter':
            return symbol.get('parameter_data').get('data_type')
        elif symbol_type == 'function':
            return symbol.get('function_data').get('return_type')
        elif symbol_type == 'variable':
            return symbol.get('variable_data').get('data_type') 
        
    def setType(self, name, type_str):
        symbol = self.lookup(name)
        symbol_type = symbol.get('symbol_type')
        
        if symbol_type == 'parameter':
            symbol['parameter_data']['data_type'] = type_str
        elif symbol_type == 'function':
            symbol['function_data']['return_type'] = type_str
        elif symbol_type == 'variable':
            symbol['variable_data']['data_type'] = type_str
        else:
            raise ValueError(f"Unknown symbol type: {symbol_type}")

        
    def setReference(self, var_name, ref):
        var_info = self.lookup(var_name)
        if var_info:
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

    def print_table(self):
        for i, (scope_id, scope_dict, parent_id, child_indices) in enumerate(self.scopes):
            if not scope_dict:  # Skip empty scopes
                continue
            
            # Header with scope level and ID
            if i == 0:
                header = "Global Scope"
            else:
                header = f"Scope {scope_id} - Parent ID: {parent_id}"
            
            print(header)

            # Display child scopes
            if child_indices:
                child_scope_str = ", ".join(str(child_id) for child_id in child_indices)
                print(f"Child Scope idx: {child_scope_str}\n")
            
            # Check if there's function data to adjust the header
            has_function_data = any('function_data' in info for info in scope_dict.values())
            if has_function_data:
                print("{:<20} {:<15} {:<10} {:<15} {:<20} {:<15}".format(
                    'Symbol Name', 'Symbol Type', 'Reference', 'Data Type', 'Parameters', 'Return Type'
                ))
                print("="*95)
            else:
                print("{:<20} {:<15} {:<10} {:<15}".format(
                    'Symbol Name', 'Symbol Type', 'Reference', 'Data Type'
                ))
                print("="*60)
            
            # Display symbols in the scope
            for name, info in scope_dict.items():
                symbol_type = info.get('symbol_type', 'n/a') or 'n/a'
                ref = info.get('ref', 'n/a') or 'n/a'
                data_type = 'n/a'
                
                if symbol_type == 'variable':
                    data_type = info.get('variable_data', {}).get('data_type', 'n/a') or 'n/a'
                elif symbol_type == 'parameter':
                    data_type = info.get('parameter_data', {}).get('data_type', 'n/a') or 'n/a'
                
                name = name or 'n/a'
                
                if has_function_data and symbol_type == 'function':
                    function_data = info.get('function_data', {})
                    parameters = function_data.get('parameters', 'n/a') or 'n/a'
                    if isinstance(parameters, list):
                        parameters = ', '.join(param.name for param in parameters) if parameters else 'n/a'
                    return_type = function_data.get('return_type', 'n/a') or 'n/a'
                    print(f"{name:<20} {symbol_type:<15} {ref:<10} {data_type:<15} {parameters:<20} {return_type:<15}")
                else:
                    print(f"{name:<20} {symbol_type:<15} {ref:<10} {data_type:<15}")
            
            # Print footer line
            if has_function_data:
                print("="*95)
            else:
                print("="*60)
            
            print("\n")            
                 
                 