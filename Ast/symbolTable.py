class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # List of dictionaries to manage all scopes

    def enter_scope(self):
        self.scopes.append({})

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Attempted to exit global scope")

    def add(self, name, symbolType=None, functionData=None):
        # TODO: ensure types are valid
        if name in self.scopes[-1]:
            raise Exception(f"Symbol '{name}' already declared in this scope")
        
        if symbolType not in ['function', 'parameter', 'integer', 'float', 'string', 'null']:
            raise Exception(f"Invalid symbol type '{symbolType}' for symbol '{name}'")
        
        self.scopes[-1][name] = {
            'symbolType': symbolType, # 'function', 'parameter', 'integer', 'float', 'string', 'null'
            'alloca': None, 
            'functionData': functionData 
        }  

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def update(self, name, type_info):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['type'] = type_info  # Update type information
                return
        raise Exception(f"Symbol '{name}' not found in any scope")

    def is_declared(self, name):
        return any(name in scope for scope in self.scopes)

    def print_table(self):
        print("Symbol Table Contents:")
        has_function_data = any('functionData' in info for scope in self.scopes for info in scope.values())
        
        for i, scope in enumerate(self.scopes):
            print(f"Scope Level {i}:")
            if has_function_data:
                print("{:<20} {:<15} {:<10} {:<10} {:<20} {:<15}".format('Variable', 'Type', 'Allocation', 'Arity', 'Parameters', 'Return Type'))
                print("="*90)
            else:
                print("{:<20} {:<15} {:<10}".format('Symbol Name', 'Type', 'Allocation'))
                print("="*45)
            
            for name, info in scope.items():
                symbol_type = info.get('symbolType', 'n/a') or 'n/a'
                alloca = info.get('alloca', 'n/a') or 'n/a'
                if has_function_data:
                    function_data = info.get('functionData', {})
                    arity = function_data.get('arity', 'n/a') or 'n/a'
                    parameters = function_data.get('parameters', 'n/a') or 'n/a'
                    if isinstance(parameters, list):
                        parameters = ', '.join(parameters) if parameters else 'n/a'
                    return_type = function_data.get('return_type', 'n/a') or 'n/a'
                    print(f"{name:<20} {symbol_type:<15} {alloca:<10} {arity:<10} {parameters:<20} {return_type:<15}")
                else:
                    print(f"{name:<20} {symbol_type:<15} {alloca:<10}")
            
            if has_function_data:
                print("="*90)
            else:
                print("="*45)
    
    def is_global(self, name):
        return name in self.scopes[0]
    
    def get_type_info(self, name):
        return self.lookup(name).get('type') if self.lookup(name) else None
    
    def set_allocation(self, var_name, alloca):
        var_info = self.lookup(var_name)
        if var_info:
            var_info['alloca'] = alloca
        else:
            raise ValueError(f"Variable '{var_name}' not found.")

    def get_allocation(self, var_name):
        var_info = self.lookup(var_name)
        if var_info and 'alloca' in var_info:
            return var_info['alloca']
        else:
            raise ValueError(f"Allocation for variable '{var_name}' not found.")