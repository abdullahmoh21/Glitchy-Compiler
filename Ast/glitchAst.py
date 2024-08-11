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
    def __init__(self, name, expression, line=None):
        self.name = name
        self.value = expression
        self.line = line
        self.type = self.getType()
    
    def getType(self):
        if self.value is not None:
            return self.value.getType()
        return "dynamic"
    
    def __eq__(self, other):
        return (isinstance(other, VariableDeclaration) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableDeclaration({self.name}, {self.value})"
        
    def accept(self, visitor):
            return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableDeclaration (type: {self.type})")
        print(" " * (indent + 2) + f"Name: {self.name}")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class VariableReference(ASTNode):
    def __init__(self, name, value = None, line = None):
        self.name = name  
        self.value = value  
        self.line = line
        self.type = self.getType()
        
    def getType(self):
        if self.value is not None:
            if isinstance(self.value, MethodCall):
                return "method_call"
            return self.value.getType()
        return "dynamic"
    
    def __eq__(self, other):
        return (isinstance(other, VariableReference) and self.name == other.name)
        
    def __repr__(self):
        return f"VariableReference({self.name})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableReference: (type: {self.type})")
        print(" " * (indent + 2) + f"Name: {self.name}")

class VariableUpdated(ASTNode):
    def __init__(self, name, expression, line=None):
        self.name = name
        self.value = expression
        self.line = line
        self.type = self.getType()
    
    def getType(self):
        if self.value is not None:
            if isinstance(self.value, MethodCall): 
                return "method_call"
            return self.value.getType()
        return "Variable Updated with None"
    
    def __eq__(self, other):
        return (isinstance(other, VariableUpdated) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableUpdated({self.name}, {self.value})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"VariableUpdated(type: {self.type})")
        print(" " * (indent + 2) + f"Name: {self.name}")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class FunctionDeclaration(ASTNode):
    def __init__(self, name, parameters, block, line=None):
        self.name = name
        self.parameters = parameters
        self.arity = len(parameters)
        self.block = block
        self.return_type = self.evaluate_return_type()
        self.line = line
    
    # We want to limit boxing, so we check if only one type is being returned
    def evaluate_return_type(self):
        return_types = set()

        def collect_return_types(block):
            for statement in block.statements:
                if isinstance(statement, Return):
                    return_types.add(statement.getType())
                elif isinstance(statement, Block):
                    collect_return_types(statement)

        collect_return_types(self.block)

        if len(return_types) == 0:
            return "null"
        elif len(return_types) == 1:
            return return_types.pop()
        else:
            return "dynamic"
        
    def __eq__(self, other):
        return (isinstance(other, FunctionDeclaration) and
                self.name == other.name and
                self.parameters == other.parameters and
                self.block == other.block)
    
    def __repr__(self):
        return f"FunctionDeclaration({self.name}, {self.parameters}, {self.block})"
    
    def accept(self, visitor):
        return visitor.visit_function_declaration(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"FunctionDeclaration: {self.name} (type: {self.return_type})")
        print(" " * (indent + 2) + f"Parameters: ({self.parameters})")
        self.block.print_content(indent + 2)

class Return(ASTNode):
    def __init__(self, expression):
        self.value = expression
        self.type = self.getType()
    
    def getType(self):
        return self.value.type
              
    def __repr__(self):
        return "return"

    def __eq__(self, other):
        return isinstance(other, Return) and self.value == other.value
    
    def accept(self, visitor):
        return visitor.visit_return(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Return: {self.value} (type: {self.type})")
    
class FunctionCall(ASTNode):
    def __init__(self, name, arguments, line=None):
        self.name = name
        self.arguments = arguments
        self.arity = len(arguments)
        self.line = line
    
    def getType(self):
        return "functionCall"
    
    def __eq__(self, other):
        return (isinstance(other, FunctionCall) and
                self.name == other.name and
                self.arguments == other.arguments)
    
    def __repr__(self):
        return f"FunctionCall({self.name}, {self.arguments})"
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"FunctionCall: {self.name}")
        if self.arguments is not None:
            for arg in self.arguments:
                arg.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Arguments: None")

class MethodCall(ASTNode):
    def __init__(self, varRef, name, arguments, line=None):
        self.varRef = varRef
        self.name = name
        self.arguments = arguments
        self.line = line
    
    def __eq__(self, other):
        return (isinstance(other, MethodCall) and
                self.varRef == other.varRef and
                self.name == other.name and
                self.arguments == other.arguments)
        
    def __repr__(self):
        return f"MethodCall({self.varRef.name}, {self.name} ,{self.arguments})"
        
    def accept(self, visitor):
        return visitor.visit_method_call(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"MethodCall: {self.varRef.name}.{self.name}()")
        if self.arguments is not None:
            for arg in self.arguments:
                arg.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Arguments: None")

class Print(ASTNode):
    def __init__(self, expression, line=None):
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
    def __init__(self, comparison, block, line=None, elifNodes=None, elseBlock=None):
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
    def __init__(self, comparison, block, line=None):
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
    def __init__(self, varRef, line=None):
        self.varRef = varRef
        self.line = line
    
    def __eq__(self, other):
        return isinstance(other, Input) and self.varRef == other.varRef

    def __repr__(self):
        return f"Input({self.varRef})"
    
    def accept(self, visitor):
        return visitor.visit_input(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Input")
        print(" " * (indent + 2) + f"Variable: {self.varRef.name}")
            
# ------------------------- Expressions ------------------------- #
class Expression(ASTNode):
    def __init__(self, left, operator, right, nodeType, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line
        self.type = nodeType
    
    def __eq__(self, other):
        raise NotImplementedError("Subclasses should implement this!")

    def accept(self, visitor):
        raise NotImplementedError("Subclasses should implement this!")
    
    def __repr__(self):
        raise NotImplementedError("Subclasses should implement this!")
    
    def print_content(self, indent=0):
        print(" " * indent + "Expression")
        self.left.print_content(indent + 2)
        print(" " * (indent + 2) + f"Operator: {self.operator}")
        self.right.print_content(indent + 2)

# For + - * /
class BinaryOp(Expression):
    def __init__(self, left, operator, right, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        nodeType = self.getType()
        super().__init__(left, operator, right, nodeType, line)

    def getType(self):
        left_type = self.left.getType()
        right_type = self.right.getType()

        numeric_types = ['integer', 'float']
    
        if self.operator in ['+', '-', '*', '/']:
            if left_type in numeric_types and right_type in numeric_types:
                # If one is float, the result is float
                if left_type == 'float' or right_type == 'float':
                    return 'float'
                return 'integer'
            elif self.operator == '+' and left_type == 'string' and right_type == 'string':
                return 'string'
            else:
                return "dynamic"

        return "invalid"

    def accept(self, visitor):
        return visitor.visit_binary_op(self)
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"

    def __eq__(self, other):
        return (isinstance(other, BinaryOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)

    def print_content(self, indent=0):
        print(" " * indent + f"BinaryOp (Operator: {self.operator}, type: {self.type})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
       
# for -5 / +5 and !
class UnaryOp(Expression):
    def __init__(self, operator, left, line=None):
        self.operator = operator
        self.left = left
        nodeType = self.getType()
        super().__init__(left, operator, None, line, nodeType)  # UnaryOp has no right operand

    def getType(self):
        left_type = self.left.getType()
        if self.operator == '!':
            if left_type != 'boolean':
                return "dynamic"
            return 'boolean'
        elif self.operator == '-' or self.operator == '+':
            if left_type != 'integer' and left_type != 'float':
                return "dynamic"
            return left_type
        return "invalid"
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)
    
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
    def __init__(self, left, operator, right, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        nodeType = self.getType()
        super().__init__(left, operator, right, line, nodeType)
    
    def getType(self):
        left_type = self.left.getType()
        right_type = self.right.getType()
        if left_type not in ['integer', 'float'] or right_type not in ['integer', 'float']:
            return "dynamic"
        return 'boolean'
    
    def accept(self, visitor):
        return visitor.visit_comparison(self)
    
    def __repr__(self):
        return f"Comparison({self.left} {self.operator} {self.right})"
    
    def __eq__(self, other):
        return (isinstance(other, Comparison) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Comparison (Operator: {self.operator}, type: {self.type})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)

# for && ||
class LogicalOp(Expression):
    def __init__(self, left, operator, right, line= None):
        self.left = left
        self.operator = operator
        self.right = right
        nodeType = self.getType()
        super().__init__(left, operator, right, line, nodeType)

    def getType(self):
        left_type = self.left.getType()
        right_type = self.right.getType()
        if left_type != 'boolean' or right_type != 'boolean':
            return "dynamic"
        return 'boolean'
    
    def accept(self, visitor):
        return visitor.visit_logical_op(self)
    
    def __repr__(self):
        return f"LogicalOp({self.left} {self.operator} {self.right})"

    def __eq__(self, other):
        return (isinstance(other, LogicalOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)
    
    def print_content(self, indent=0):
        print(" " * indent + f"LogicalOp (Operator: {self.operator}, type: {self.type})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
        
# ------------------------- Literals ------------------------- #
class Primary(ASTNode):
    def __init__(self, value, nodeType, line=None):
        self.value = value
        self.line = line
        self.type = nodeType

    def __eq__(self, other):
        return isinstance(other, Primary) and self.value == other.value and self.line == other.line

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value})"
    
    def print_content(self, indent=0):
        print(" " * indent + f"{self.__class__.__name__}: {self.value}")

class Integer(Primary):
    def __init__(self, value, line=None):
        self.value = value
        nodeType = self.getType()
        super().__init__(value, nodeType , line = line)

    def __repr__(self):
        return f"{self.value}"

    def getType(self):
        if isinstance(self.value, int):
            return 'integer'
        return "dynamic"
    
    def accept(self, visitor):
        return visitor.visit_integer(self)
    
class Float(Primary):
    def __init__(self, value, line=None):
        self.value = value
        nodeType = self.getType()
        super().__init__(value, nodeType, line = line)

    def __repr__(self):
        return f"{self.value}"
    
    def getType(self):
        if isinstance(self.value, float):
            return 'float'
        return "dynamic"
        
    def accept(self, visitor):
        return visitor.visit_float(self)

class Boolean(Primary):
    def __init__(self, value, line=None):
        self.value = value
        nodeType = self.getType()
        super().__init__(value, nodeType, line = line)

    def __repr__(self):
        return f"{self.value}"
    
    def getType(self):
        if isinstance(self.value, str) and self.value.lower().strip() in ['true', 'false']:
            return 'boolean'
        return "dynamic"
    
    def accept(self, visitor):
        return visitor.visit_boolean(self)

class String(Primary):
    def __init__(self, value, line=None):
        self.value = value
        nodeType = self.getType()
        super().__init__(value, nodeType, line = line)

    def __repr__(self):
        return self.value
    
    def getType(self):
        if self.value is not None and isinstance(self.value, str):
            return 'string'
        return "dynamic"

    def accept(self, visitor):
        return visitor.visit_string(self)

class Null(Primary):
    def __init__(self, line=None):
        nodeType = self.getType()
        super().__init__(None, nodeType, line = line)

    def __repr__(self):
        return "Null"

    def getType(self):
        return 'null'
    
    def print_content(self, indent=0):
        print(" " * indent + "Null")