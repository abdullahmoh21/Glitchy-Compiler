class SymbolTable:
    def __init__(self):
        self.scopes = [{}]  # scopes
        self.declarations = {}  # variable declarations
        self.used_variables = set()  # variables that were used
        self.dead_variables = set()  # dead variables for dead code elimination
    
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Attempted to exit global scope")
    
    def add(self, name, type_info):
        if name in self.scopes[-1]:
            raise Exception(f"Symbol '{name}' already declared in this scope")
        self.scopes[-1][name] = type_info
        if name not in self.declarations:
            self.declarations[name] = {'defined': False, 'line': None, 'type': type_info}
    
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def update(self, name, type_info):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = type_info
                return
        raise Exception(f"Symbol '{name}' not found in any scope")
    
    def declare(self, name, line):
        if name in self.declarations:
            self.declarations[name]['defined'] = True
            self.declarations[name]['line'] = line
        else:
            raise Exception(f"Symbol '{name}' not declared before usage")

    def is_declared(self, name):
        return name in self.declarations and self.declarations[name]['defined']
    
    def is_in_scope(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return True
        return False
    
    def get_declaration_line(self, name):
        return self.declarations.get(name, {}).get('line')
    
    def mark_as_used(self, name):
        if self.is_declared(name):
            self.used_variables.add(name)
    
    def report_dead_code(self):
        print("Dead Variables:")
        for var_name, info in self.declarations.items():
            if info['defined'] and var_name not in self.used_variables:
                self.dead_variables.add(var_name)
                print(f"Variable '{var_name}' declared on line {info['line']} is never used. Will be removed by the optimizer.")
                
    def print_table(self):
        print("Symbol Table Contents:")
        print("{:<20} {:<10} {:<10} {:<10}".format('Variable', 'Type', 'Defined', 'Line'))
        print("="*50)
        for name, info in self.declarations.items():
            is_defined = 'Yes' if info['defined'] else 'No'
            line = info['line'] if info['line'] is not None else 'N/A'
            print("{:<20} {:<10} {:<10} {:<10}".format(name, info['type'], is_defined, line))
        print("="*50)
