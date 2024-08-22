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
    def __init__(self, name, value, line=None, annotation=None):
        self.name = name
        self.value = value
        self.annotation = annotation
        self.line = line
    
    def evaluateType(self):
        if self.value is not None:
            return self.value.evaluateType()
        return "invalid"
    
    def __eq__(self, other):
        return (isinstance(other, VariableDeclaration) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableDeclaration({self.name}, {self.value})"
        
    def accept(self, visitor):
            return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableDeclaration: {self.name}")
        if self.annotation is not None:
            print(" " * (indent + 2) + f"Type Annotation: {self.annotation}")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class VariableReference(ASTNode):
    def __init__(self, name, line = None):
        self.name = name  
        self.line = line
        self.type = None
        
    def evaluateType(self):
        if self.type is not None:
            return self.type
        return 'invalid'
        
    def __eq__(self, other):
        return (isinstance(other, VariableReference) and self.name == other.name)
        
    def __repr__(self):
        return f"VariableReference({self.name})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)

    def print_content(self, indent=0):
        print(" " * indent + f"VariableReference: {self.name}")

class VariableUpdated(ASTNode):
    def __init__(self, name, value, line=None):
        self.name = name
        self.value = value
        self.line = line
    
    def evaluateType(self):
        if self.value is not None:
            return self.value.evaluateType()
        return "invalid"
    
    def __eq__(self, other):
        return (isinstance(other, VariableUpdated) and
                self.name == other.name and
                self.value == other.value)
        
    def __repr__(self):
        return f"VariableUpdated({self.name}, {self.value})"
        
    def accept(self, visitor):
        return visitor.visit_variable(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"VariableUpdated: {self.name} ")
        if self.value is not None:
            self.value.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Value: None")

class FunctionDeclaration(ASTNode):
    def __init__(self, name, return_type, parameters, block, line=None):
        self.name = name
        self.return_type = return_type
        self.parameters = parameters
        self.block = block
        self.arity = len(parameters)
        self.line = line
    
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
        print(" " * indent + f"FunctionDeclaration: {self.name} (return_type: {self.return_type})")
        print(" " * (indent + 2) + f"Parameters: ({self.parameters})")
        self.block.print_content(indent + 2)

class Return(ASTNode):
    def __init__(self, expression, line = None):
        self.value = expression
        self.line = line
     
    def evaluateType(self):
        if self.value is not None:
            return self.value.evaluateType()
        return 'invalid'
    
    def __repr__(self):
        return "return"

    def __eq__(self, other):
        return isinstance(other, Return) and self.value == other.value
    
    def accept(self, visitor):
        return visitor.visit_return(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Return: {self.value}")
    
class Parameter(ASTNode):
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def evaluateType(self):
        return self.type
    
    def __repr__(self):
        return f"Parameter: {self.name} "

    def __eq__(self, other):
        return isinstance(other, Parameter) and self.type == other.type
    
    def accept(self, visitor):
        return visitor.visit_parameter(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Parameter: {self.name} (type: {self.type})")

class FunctionCall(ASTNode):
    def __init__(self, name, arguments, line=None):
        self.name = name
        self.arguments = arguments
        self.arity = len(arguments)
        self.line = line
        self.type = None     # set in analyzer
    
    def evaluateType(self):
        if self.type is not None:
            return self.type
        return 'invalid'
    
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

# TODO: implement named and default args
class Argument(ASTNode):
    def __init__(self, value, name = None):
        self.name = name
        self.value = value
        self.type = None
    
    def evaluateType(self):
        if self.type is not None:
            return self.type
        return 'invalid'
    
    def __repr__(self):
        return f"Argument: {self.value} "

    def __eq__(self, other):
        return isinstance(other, Argument) and self.type == other.type
    
    def accept(self, visitor):
        return visitor.visit_argument(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Argument: {self.name} (type: {self.type})")

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
    def __init__(self, value, line=None):
        self.value = value
        self.line = line
        
    def __eq__(self, other):
        return isinstance(other, Print) and self.value == other.value

    def __repr__(self):
        return f"Print({self.value})"
    
    def accept(self, visitor):
        return visitor.visit_print(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "Print")
        self.value.print_content(indent + 2)

class If(ASTNode):
    def __init__(self, comparison, block, line=None, elifNodes=[], elseBlock=None):
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
    def __init__(self, left, operator, right, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.line = line
    
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
        self._cached_type = None
        super().__init__(left, operator, right, line)

    def evaluateType(self):
        if self._cached_type is not None:
            return self._cached_type
        
        left_type = self.left.evaluateType()
        right_type = self.right.evaluateType()
        numeric_types = ['integer', 'float']
    
        if self.operator in ['+', '-', '*', '/']:
            if left_type in numeric_types and right_type in numeric_types:
                # If one is float, the result is float
                if left_type == 'float' or right_type == 'float':
                    self._cached_type = 'float'
                self._cached_type = 'integer'
            elif self.operator == '+' and left_type == 'string' and right_type == 'string':
                self._cached_type = 'string'

        return self._cached_type or "invalid"

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
        print(" " * indent + f"BinaryOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
       
# for -5 / +5 and !
class UnaryOp(Expression):
    def __init__(self, operator, left, line=None):
        self.operator = operator
        self.left = left
        self._cached_type = None
        super().__init__(left, operator, None, line)  # UnaryOp has no right operand

    def evaluateType(self):
        if self._cached_type is not None:
            return self._cached_type
        
        left_type = self.left.evaluateType()
        if self.operator == '!':
            if left_type != 'boolean':
                return "invalid"
            self._cached_type = 'boolean'
        elif self.operator == '-' or self.operator == '+':
            if left_type != 'integer' and left_type != 'float':
                return "invalid"
            self._cached_type = left_type
            
        return self._cached_type or "invalid"
    
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
        self._cached_type = None  
        super().__init__(left, operator, right, line)
    
    def evaluateType(self):
        if self._cached_type is not None:
            return self._cached_type 
        
        left_type = self.left.evaluateType()
        right_type = self.right.evaluateType()
        if left_type not in ['integer', 'float'] or right_type not in ['integer', 'float']:
            return "invalid"
        self._cached_type = 'boolean'
        return self._cached_type
    
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
        print(" " * indent + f"Comparison (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)

# for && ||
class LogicalOp(Expression):
    def __init__(self, left, operator, right, line= None):
        self.left = left
        self.operator = operator
        self.right = right
        self._cached_type = None
        super().__init__(left, operator, right, line)

    def evaluateType(self):
        if self._cached_type is not None:
            return self._cached_type 
        
        left_type = self.left.evaluateType()
        right_type = self.right.evaluateType()
        if left_type != 'boolean' or right_type != 'boolean':
            return "invalid"
        
        self._cached_type = 'boolean'
        return self._cached_type
    
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
        print(" " * indent + f"LogicalOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)
        
class TernaryOp(ASTNode):
    def __init__(self, condition, true_expr, false_expr, line= None):
        self.condition = condition
        self.true_expr = true_expr
        self.false_expr = false_expr
        self.line = line

    def evaluateType(self):
        pass
    
    def accept(self, visitor):
        return visitor.visit_ternary_op(self)
    
    def __repr__(self):
        return f"TernaryOp({self.condition}) ? {self.true_expr} : {self.false_expr})"

    def __eq__(self, other):
        return (isinstance(other, TernaryOp) and
                self.condition == other.condition and
                self.true_expr == other.true_expr and
                self.false_expr == other.false_expr)
    
    def print_content(self, indent=0):
        print(" " * indent + f"TernaryOp (Condition: {self.condition} )")
        self.true_expr.print_content(indent + 2)
        self.false_expr.print_content(indent + 2)
            

# ------------------------- Literals ------------------------- #
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
        self.value = value
        super().__init__(value , line = line)

    def evaluateType(self):
        if isinstance(self.value, int):
            return 'integer'
        return "invalid"
    
    def __repr__(self):
        return f"{self.value}"

    def accept(self, visitor):
        return visitor.visit_integer(self)
    
class Float(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value, line = line)

    def evaluateType(self):
        if isinstance(self.value, float):
            return 'float'
        return "invalid"
      
    def __repr__(self):
        return f"{self.value}"
  
    def accept(self, visitor):
        return visitor.visit_float(self)

class Boolean(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value, line = line)

    def evaluateType(self):
        if isinstance(self.value, str) and self.value.lower().strip() in ['true', 'false']:
            return 'boolean'
        return "invalid"
   
    def __repr__(self):
        return f"{self.value}"
 
    def accept(self, visitor):
        return visitor.visit_boolean(self)

class String(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value, line = line)

    def evaluateType(self):
        if self.value is not None and isinstance(self.value, str):
            return 'string'
        return "invalid"

    def __repr__(self):
        return self.value
    

    def accept(self, visitor):
        return visitor.visit_string(self)

class Null(Primary):
    def __init__(self, line=None):
        super().__init__(None, line = line)

    def evaluateType(self):
        return 'null'
   
    def __repr__(self):
        return "Null"

    def print_content(self, indent=0):
        print(" " * indent + "Null")