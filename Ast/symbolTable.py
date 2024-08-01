class SymbolTable:
    def __init__(self):
        self.scopes = [{}]
    
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Attempted to exit global scope")
    
    def add(self, name, value):
        if name in self.scopes[-1]:
            raise Exception(f"Symbol '{name}' already declared in this scope")
        self.scopes[-1][name] = value
    
    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def update(self, name, value):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name] = value
                return
        raise Exception(f"Symbol '{name}' not found in any scope")