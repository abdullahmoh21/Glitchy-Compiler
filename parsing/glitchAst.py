class ASTNode:
    def accept(self, visitor):
        raise NotImplementedError("Subclasses should implement this!")

    def print_content(self, indent=0):
        raise NotImplementedError("Subclasses should implement this!")

    def print_tree(self, type='structure'):
        if type == 'structure':
            self.print_structure()
        elif type == 'content':
            self.print_content()
        else:
            raise ValueError("Invalid type. Use 'structure' or 'content'.")

class Program(ASTNode):
    def __init__(self, statements, symbols=None):
        self.statements = statements
        self.symbols = symbols
    
    def __eq__(self, other):
        return isinstance(other, Program) and self.statements == other.statements
    
    def __repr__(self):
        return f"Program({self.statements})"
    
    def accept(self, visitor):
        return visitor.visit_program(self)
    
    def print_content(self, indent=0):
        for stmt in self.statements:
            if stmt is not None:
                stmt.print_content(indent + 2)
            else:
                print(" " * (indent+2) + "null")
                

class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def __eq__(self, other):
        return isinstance(other, Block) and self.statements == other.statements

    def __repr__(self):
        return f"Block({self.statements})"

    def accept(self, visitor):
        return visitor.visit_block(self)

    def print_content(self, indent=0):
        print(" " * indent + "Block")
        for stmt in self.statements:
            stmt.print_content(indent + 2)

class VariableDeclaration(ASTNode):
    def __init__(self, var_name, expression):
        self.name = var_name
        self.value = expression
        
    def __eq__(self, other):
        return (isinstance(other, VariableDeclaration) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableDeclaration({self.name}, {self.value})"
        
    def accept(self, visitor):
        return visitor.visit_variable_declaration(self)

    def print_content(self, indent=0):
        print(" " * indent + "VariableDeclaration")
        print(" " * (indent + 2) + f"Name: {self.name}")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class VariableReference(ASTNode):
    def __init__(self, var_name):
        self.name = var_name
        
    def __eq__(self, other):
        return (isinstance(other, VariableReference) and self.name == other.name)
        
    def __repr__(self):
        return f"VariableReference({self.name})"
        
    def accept(self, visitor):
        return visitor.visit_variable_reference(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableReference: {self.name}")

class VariableUpdated(ASTNode):
    def __init__(self, var_name, expression):
        self.name = var_name
        self.value = expression
        
    def __eq__(self, other):
        return (isinstance(other, VariableUpdated) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableUpdated({self.name}, {self.value})"
        
    def accept(self, visitor):
        return visitor.visit_variable_updated(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableUpdated({self.name})")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class Print(ASTNode):
    def __init__(self, expression):
        self.expression = expression
        
    def __eq__(self, other):
        return isinstance(other, Print) and self.expression == other.expression

    def __repr__(self):
        return f"Print({self.expression})"
    
    def accept(self, visitor):
        return visitor.visit_print(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Print")
        self.expression.print_content(indent + 2)

class If(ASTNode):
    def __init__(self, comparison, block):
        self.comparison = comparison
        self.block = block
    
    def __eq__(self, other):
        return isinstance(other, If) and self.comparison == other.comparison and self.block == other.block

    def __repr__(self):
        return f"If({self.comparison}, {self.block})"
    
    def accept(self, visitor):
        return visitor.visit_if(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "If")
        self.comparison.print_content(indent + 2)
        self.block.print_content(indent + 2)

class While(ASTNode):
    def __init__(self, comparison, block):
        self.comparison = comparison
        self.block = block
        
    def __eq__(self, other):
        return isinstance(other, While) and self.comparison == other.comparison and self.block == other.block

    def __repr__(self):
        return f"While({self.comparison}, {self.block})"
        
    def accept(self, visitor):
        return visitor.visit_while(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "While")
        self.comparison.print_content(indent + 2)
        self.block.print_content(indent + 2)

class For(ASTNode):
    def __init__(self, variable, comparison, increment, block):
        self.variable = variable        # type: Variable
        self.comparison = comparison    # type: Comparison
        self.increment = increment
        self.block = block
        
    def __eq__(self, other):
        return (isinstance(other, For) and self.variable == other.variable and
                self.comparison == other.comparison and self.increment == other.increment and self.block == other.block)

    def __repr__(self):
        return f"For({self.variable.name}={'None' if self.variable.value is None else self.variable.value};{self.comparison};{self.increment}, {self.block})"

    def accept(self, visitor):
        return visitor.visit_for(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "For")
        print(" " * (indent + 2) + f"Variable: {self.variable.name}")
        if self.variable.value is not None:
            self.variable.value.print_content(indent + 2)
        self.comparison.print_content(indent + 2)
        print(" " * (indent + 2) + f"Increment: {self.increment}")
        self.block.print_content(indent + 2)

class Input(ASTNode):
    def __init__(self, var_name):
        self.var_name = var_name
    
    def __eq__(self, other):
        return isinstance(other, Input) and self.var_name == other.var_name

    def __repr__(self):
        return f"Input({self.var_name})"
    
    def accept(self, visitor):
        return visitor.visit_input(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Input")
        print(" " * (indent + 2) + f"Variable: {self.var_name}")

class Comparison(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __eq__(self, other):
        return isinstance(other, Comparison) and self.left == other.left and self.operator == other.operator and self.right == other.right

    def __repr__(self):
        return f"Comparison({self.left} {self.operator} {self.right})"
    
    def accept(self, visitor):
        return visitor.visit_comparison(self)
      
    def print_content(self, indent=0):
        print(" " * indent + "Comparison")
        self.left.print_content(indent + 2)
        print(" " * (indent + 2) + f"Operator: {self.operator}")
        self.right.print_content(indent + 2)

class Expression(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right
    
    def __eq__(self, other):
        return isinstance(other, Expression) and self.left == other.left and self.operator == other.operator and self.right == other.right

    def __repr__(self):
        return f"Expression({self.left} {self.operator} {self.right})"
    
    def accept(self, visitor):
        return visitor.visit_expression(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Expression")
        self.left.print_content(indent + 2)
        print(" " * (indent + 2) + f"Operator: {self.operator}")
        self.right.print_content(indent + 2)

class Primary(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, Primary) and self.value == other.value

    def __repr__(self):
        return f"Primary({self.value})"
    
    def accept(self, visitor):
        return visitor.visit_primary(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Primary: {self.value}")

class Number(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value

    def __repr__(self):
        return f"Number({self.value})"
    
    def accept(self, visitor):
        return visitor.visit_number(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Number: {self.value}")

class Boolean(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, Boolean) and self.value == other.value

    def __repr__(self):
        return f"Boolean({self.value})"
    
    def accept(self, visitor):
        return visitor.visit_boolean(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Boolean: {self.value}")

class String(ASTNode):
    def __init__(self, value):
        self.value = value
    
    def __eq__(self, other):
        return isinstance(other, String) and self.value == other.value

    def __repr__(self):
        return f"String({self.value})"
    
    def accept(self, visitor):
        return visitor.visit_string(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"String: {self.value}")

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
