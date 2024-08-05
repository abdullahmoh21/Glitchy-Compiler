class ASTNode:
    def accept(self, visitor):
        raise NotImplementedError("Subclasses should implement this!")

    def print_content(self, indent=0):
        raise NotImplementedError("Subclasses should implement this!")

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
        # no need to store line number for block

    def __eq__(self, other):
        return isinstance(other, Block) and self.statements == other.statements

    def __repr__(self):
        return f"Block({self.statements})"

    def accept(self, visitor):
        return visitor.visit_block(self)

    def print_content(self, indent=0):
        print(" " * indent + "Block")
        for stmt in self.statements:
            if stmt is not None:
                stmt.print_content(indent + 2)
            else:
                print(" " * (indent+2) + "null")
                
class VariableDeclaration(ASTNode):
    def __init__(self, name, expression,line):
        self.name = name
        self.value = expression
        self.line = line
        
    def __eq__(self, other):
        return (isinstance(other, VariableDeclaration) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableDeclaration({self.name}, {self.value})"
        
    def accept(self, visitor):
            return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + "VariableDeclaration")
        print(" " * (indent + 2) + f"Name: {self.name}")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class VariableReference(ASTNode):
    def __init__(self, name, line):
        self.name = name
        self.line = line
        
    def __eq__(self, other):
        return (isinstance(other, VariableReference) and self.name == other.name)
        
    def __repr__(self):
        return f"VariableReference({self.name})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableReference: {self.name}")

class VariableUpdated(ASTNode):
    def __init__(self, name, expression, line):
        self.name = name
        self.value = expression
        self.line = line
        
    def __eq__(self, other):
        return (isinstance(other, VariableUpdated) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableUpdated({self.name}, {self.value})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"VariableUpdated({self.name})")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class Print(ASTNode):
    def __init__(self, expression, line):
        self.expression = expression
        self.line = line
        
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
    def __init__(self, comparison, block, line, elifNodes=None, elseBlock=None):
        self.comparison = comparison
        self.block = block
        self.elifNodes = elifNodes
        self.elseBlock = elseBlock
        self.line = line
    
    def __eq__(self, other):
        return (isinstance(other, If) and
                self.comparison == other.comparison and
                self.block == other.block and
                self.elifNodes == other.elifNodes and
                self.elseBlock == other.elseBlock)
    
    def __repr__(self):
        return f"If({self.comparison}, {self.block}, {self.elifNodes}, {self.elseBlock})"
    
    def accept(self, visitor):
        return visitor.visit_if(self)
    
    def print_content(self, indent=0):
            print(" " * indent + "If")
            
            if self.comparison:
                self.comparison.print_content(indent + 2)
            else:
                print(" " * (indent + 2) + "None")
            
            if self.block:
                self.block.print_content(indent + 2)
            else:
                print(" " * (indent + 2) + "None")
            
            if self.elifNodes:
                for elif_comparison, elif_block in self.elifNodes:
                    print(" " * indent + "Elif")
                    if elif_comparison:
                        elif_comparison.print_content(indent + 2)
                    else:
                        print(" " * (indent + 2) + "None")
                    if elif_block:
                        elif_block.print_content(indent + 2)
                    else:
                        print(" " * (indent + 2) + "None")
            
            if self.elseBlock is not None:
                print(" " * indent + "Else")
                self.elseBlock.print_content(indent + 2)      

class While(ASTNode):
    def __init__(self, comparison, block, line):
        self.comparison = comparison
        self.block = block
        self.line = line
        
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

class Input(ASTNode):
    def __init__(self, var_name,line):
        self.var_name = var_name
        self.line = line
    
    def __eq__(self, other):
        return isinstance(other, Input) and self.var_name == other.var_name

    def __repr__(self):
        return f"Input({self.var_name})"
    
    def accept(self, visitor):
        return visitor.visit_input(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Input")
        print(" " * (indent + 2) + f"Variable: {self.var_name}")
            
# base class for all expressions
class Expression(ASTNode):
    def __init__(self, left, operator, right, line):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line
    
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

# For + - * /
class BinaryOp(Expression):
    def __init__(self, left, operator, right, line):
        super().__init__(left, operator, right, line)

    def __repr__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"

    def __eq__(self, other):
        return (isinstance(other, BinaryOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)

    def print_content(self, indent=0):
        print(" " * indent + f"BinaryOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
       
# for -5 / +5 and !
class UnaryOp(Expression):
    def __init__(self, operator, left, line):
        super().__init__(left, operator, None, line)  # UnaryOp has no right operand

    def __repr__(self):
        return f"UnaryOp({self.operator}, {self.left})"

    def __eq__(self, other):
        return (isinstance(other, UnaryOp) and
                self.operator == other.operator and
                self.left == other.left)

    def print_content(self, indent=0):
        print(" " * indent + f"UnaryOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)

# for < > <= >= == !=
class Comparison(Expression):
    def __init__(self, left, operator, right, line):
        super().__init__(left, operator, right, line)
    
    def __repr__(self):
        return f"Comparison({self.left} {self.operator} {self.right})"
    
    def accept(self, visitor):
        return visitor.visit_comparison(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Comparison")
        self.left.print_content(indent + 2)
        print(" " * (indent + 2) + f"Operator: {self.operator}")
        self.right.print_content(indent + 2)

# for && ||
class LogicalOp(Expression):
    def __init__(self, left, operator, right, line):
        super().__init__(left, operator, right, line)

    def __repr__(self):
        return f"LogicalOp({self.left} {self.operator} {self.right})"

    def __eq__(self, other):
        return (isinstance(other, LogicalOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)

    def print_content(self, indent=0):
        print(" " * indent + f"LogicalOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
        
# Base class for all literals
class Primary(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line

    def __eq__(self, other):
        return isinstance(other, Primary) and self.value == other.value and self.line == other.line

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"
    
    def print_content(self, indent=0):
        print(" " * indent + f"{self.__class__.__name__}: {self.value}")

class Integer(Primary):
    def __init__(self, value, line=None):
        super().__init__(value, line)

    def accept(self, visitor):
        return visitor.visit_number(self)
    
class Float(Primary):
    def __init__(self, value, line=None):
        super().__init__(value, line)

    def accept(self, visitor):
        return visitor.visit_float(self)

class Boolean(Primary):
    def __init__(self, value, line=None):
        super().__init__(value, line)

    def accept(self, visitor):
        return visitor.visit_boolean(self)

class String(Primary):
    def __init__(self, value, line=None):
        super().__init__(value, line)

    def accept(self, visitor):
        return visitor.visit_string(self)

class Null(Primary):
    def __init__(self):
        super().__init__(None)

    def __repr__(self):
        return "Null()"

    def print_content(self, indent=0):
        print(" " * indent + "Null")