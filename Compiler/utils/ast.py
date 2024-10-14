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
    
    def __str__(self):
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

    def __str__(self):
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
        
    def __str__(self):
        return f"set '{str(self.name)}' '=' '{str(self.value)}'"

    def __repr__(self):
        return f"VariableDeclaration('{self.name}')"
        
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
        
        # set in analyzer
        self.value = None
        self.type = None
        self.scope = None
        
    def evaluateType(self):
        if self.type is not None:
            return self.type
        return 'invalid'
        
    def __eq__(self, other):
        return (isinstance(other, VariableReference) and self.name == other.name)
        
    def __str__(self):
        return f"{str(self.name)}"
        
    def __repr__(self):
        return  f"VariableReference({self.name})"
    
    def accept(self, visitor):
        return visitor.visit_variable(self)

    def print_content(self, indent=0):
        _ = f":'{self.type}'" if self.type is not None else ""
        print(" " * indent + f"VariableReference: '{self.name}':{ _ } ")

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
        
    def __str__(self):
        return f"{str(self.value)}"
    
    def __repr__(self):
        return f"VariableUpdated({str(self.name)})"
        
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
    
    def __str__(self):
        params_str = ', '.join([str(param) for param in self.parameters])
        return f"function {str(self.name)}([{params_str}]) {{...}}"
    
    def __repr__(self):
        return f"FunctionDeclaration({str(self.name)})"
    
    def accept(self, visitor):
        return visitor.visit_function_declaration(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"FunctionDeclaration: {self.name} (return_type: {self.return_type})")
        print(" " * (indent + 2) + f"Parameters: ({self.parameters})")
        self.block.print_content(indent + 2)

class Return(ASTNode):
    def __init__(self, value, line = None):
        self.value = value
        self.line = line
     
    def evaluateType(self):
        if self.value is not None:
            return self.value.evaluateType()
        return 'invalid'
    
    def __str__(self):
        return f"{str(self.value)}"
    
    def __repr__(self):
        return f"Return({repr(self.value)})"

    def __eq__(self, other):
        return isinstance(other, Return) and self.value == other.value
    
    def accept(self, visitor):
        return visitor.visit_return(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Return: {self.value}")

class Break(ASTNode):
    def __init__(self, line):
        self.line = line
    
    def __str__(self):
        return "Break"
    
    def __repr__(self):
        return "Break"

    def __eq__(self, other):
        return isinstance(other, Break)
    
    def accept(self, visitor):
        return visitor.visit_break(self)
    
    def print_content(self, indent=0):
        print(" "*indent + "Break")
    
class Parameter(ASTNode):
    def __init__(self, name, type):
        self.name = name
        self.type = type
    
    def evaluateType(self):
        return self.type
    
    def __str__(self):
        return f"{self.name}"
    
    def __repr__(self):
        return f"Parameter({self.name})"

    def __eq__(self, other):
        return isinstance(other, Parameter) and self.type == other.type
    
    def accept(self, visitor):
        return visitor.visit_parameter(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Parameter: {self.name} (type: {self.type})")

class FunctionCall(ASTNode):
    def __init__(self, name, args, parent=None, line=None):
        self.name = name
        self.args = args
        self.arity = len(args)
        self.parent = parent
        self.line = line
        self.type = None     # set in analyzer
        self.transformed = None 
    
    def evaluateType(self):
        if self.type is not None:
            return self.type
        return 'invalid'
    
    def accept(self, visitor):
        return visitor.visit_function_call(self)
    
    def replace_with(self, new_node):
        attrs = ['value', 'receiver', 'arguments', 'left','right'] 

        def recursive_replace(node, parent, attr_name):
            """ Recursively search for and replace `self` within specified attributes. """
            if isinstance(node, (list, tuple)):
                for index, item in enumerate(node):
                    if item == self:
                        if isinstance(node, list):
                            node[index] = new_node
                        else:
                            node = node[:index] + (new_node,) + node[index + 1:]
                            setattr(parent, attr_name, node)
                        return True
                    for attr in attrs:
                        if hasattr(item, attr):
                            if recursive_replace(getattr(item, attr), item, attr):
                                return True
            elif isinstance(node, dict):
                for key, item in node.items():
                    if item == self:
                        node[key] = new_node
                        return True
                    for attr in attrs:
                        if hasattr(item, attr):
                            if recursive_replace(getattr(item, attr), item, attr):
                                return True
            elif node == self:
                setattr(parent, attr_name, new_node)
                return True
            else:
                for attr in attrs:
                    if hasattr(node, attr):
                        if recursive_replace(getattr(node, attr), node, attr):
                            return True
            return False

        if self.parent:
            # Look through all attributes of the parent object
            for attr, value in vars(self.parent).items():
                if recursive_replace(value, self.parent, attr):
                    new_node.parent = self.parent
                    self.transformed = True
                    del self
                    return

            new_node.parent = self.parent
    
    def __eq__(self, other):
        return (isinstance(other, FunctionCall) and
                self.name == other.name and
                self.args == other.args and
                self.parent == other.parent)
    
    def __str__(self):
        _ = ",".join(str(arg) for arg in self.args) if self.args else ""
        return f"{str(self.name)}({ _ })"
        
    def __repr__(self):
        return f"FunctionCall({str(self.name)})"
    
    def print_content(self, indent=0):
        print(" " * indent + f"FunctionCall: {self.name}")
        if self.parent is not None:
            print(" " * (indent + 2) + f"parent : {self.parent}")
        if len(self.args) > 0:
            for arg in self.args:
                arg.print_content(indent + 2)
        else:
            print(" " * (indent + 2) + "Arguments: None")

class Argument(ASTNode):
    def __init__(self, value, name = None):
        self.name = name
        self.value = value
        self.parent = None
        self.cached_type = None
    
    def evaluateType(self):
        if self.cached_type is not None:
            return self.cached_type
        else:
            return self.value.evaluateType()
    
    def __str__(self):
        if isinstance(self.value, list):
            list_str = ', '.join(str(item) for item in self.value)
            return f"[{list_str}]"
        else:
            return f"{str(self.value)}"
    
    def __repr__(self):
        if isinstance(self.value, list):
            list_str = ', '.join(repr(item) for item in self.value)
            return f"Argument([{list_str}])"
        else:
            return f"Argument({repr(self.value)})"

    def __eq__(self, other):
        return isinstance(other, Argument) and self.type == other.type
    
    def accept(self, visitor):
        return visitor.visit_argument(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"Argument: {repr(self.value)}")
        if self.parent is not None:
            print(" " * indent+2 + f"parent: {repr(self.parent)}")

class MethodCall(ASTNode):
    def __init__(self, receiver, name, args, line=None):
        self.receiver = receiver
        self.name = name
        self.args = args
        self.receiverTy = None
        self.line = line
    
    def evaluateType(self):
        if self.return_type is not None:
            return self.return_type
        return 'invalid'
    
    def __eq__(self, other):
        return (isinstance(other, MethodCall) and
                self.receiver == other.receiver and
                self.name == other.name and
                self.args == other.args)
        
    def __str__(self):
        _ = ",".join(str(arg) for arg in self.args) if self.args else ""
        return f"{str(self.receiver)}.{str(self.name)}({ _ })"

    def __repr__(self):
        return f"MethodCall({str(self.receiver)}.{str(self.name)}(...))"
        
    def accept(self, visitor):
        return visitor.visit_method_call(self)
    
    def print_content(self, indent=0):
        print(" " * indent + f"MethodCall: {self.name}()")
        if isinstance(self.receiver, MethodCall):
            print(" " * (indent + 2) + "Receiver:")
            self.receiver.print_content(indent + 4)
        else:
            print(" " * (indent + 2) + f"Receiver: {self.receiver}")

        if self.args:
            print(" " * (indent + 2) + "Arguments:")
            for arg in self.args:
                arg.print_content(indent + 4)
        else:
            print(" " * (indent + 2) + "Arguments: None")
            
class If(ASTNode):
    def __init__(self, comparison, block, line=None, elifNodes=[], elseBlock=None):
        self.comparison = comparison
        self.block = block
        self.elifNodes = elifNodes  # an array of tuples in format: (comparison, block)
        self.elseBlock = elseBlock
        self.line = line
    
    def __eq__(self, other):
        return (isinstance(other, If) and
                self.comparison == other.comparison and
                self.block == other.block and
                self.elifNodes == other.elifNodes and
                self.elseBlock == other.elseBlock)
    
    def __str__(self):
        return f"{str(self.comparison)}"
    
    def __repr__(self):
        return f"If({repr(self.comparison)})"
    
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

    def __str__(self):
        return f"{str(self.comparison)}"
        
    def __repr__(self):
        return f"While({repr(self.comparison)})"
        
    def accept(self, visitor):
        return visitor.visit_while(self)
    
    def print_content(self, indent=0):
        print(" " * indent + "While")
        self.comparison.print_content(indent + 2)
        self.block.print_content(indent + 2)
       
class StringCat(ASTNode):
    """ Holds string concatenations. Will be transformed from BinaryOps. The strings array holds all the values to be concatenated """
    def __init__(self, strings, parent, line=None):
        self.strings = strings
        self.line = line
        self.parent = parent
        self.evaluated = None

    def evaluateType(self):
        return "string"

    def accept(self, visitor):
        return visitor.visit_string_cat(self)
    
    def __str__(self):
        _ = f"{str(self.evaluated)}" if self.evaluated is not None else f"{str(self.strings)}"
        return f"{ _ }"

    def __repr__(self):
        _ = "True" if self.evaluated is not None else "False"
        return f"StringCat(eval: { _ })"
    
    def __eq__(self, other):
        return (isinstance(other, StringCat) and
                self.parent == other.parent and
                self.strings == other.strings and
                self.evaluated == other.evaluated)

    def print_content(self, indent=0):
        _ = "True" if self.evaluated is not None else "False"
        print(" " * indent + f"StringCat (evaluated: {_})")
        if self.evaluated is not None:
            print(" " * (indent+2) + f"{self.evaluated}")
        else:
            for value in self.strings:
                if isinstance(value, ASTNode):
                    value.print_content(indent + 2)
                else:
                    print(" " *(indent +2) +f"{str(value)}")
    
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
    
    def __str__(self):
        raise NotImplementedError("Subclasses should implement this!")
    
    def print_content(self, indent=0):
        print(" " * indent + "Expression")
        self.left.print_content(indent + 2)
        print(" " * (indent + 2) + f"Operator: {self.operator}")
        self.right.print_content(indent + 2)

# For + - * /
class BinaryOp(Expression):
    def __init__(self, left, operator, right, parent=None, line=None):
        self.left = left
        self.operator = operator
        self.right = right
        self.cached_type = None
        self.parent = parent   
        self.transformed = None     # flag to know if binaryOp has been transformed
        super().__init__(left, operator, right, line)

    def evaluateType(self):
        if self.cached_type is not None:
            return self.cached_type
        
        left_type = self.left.evaluateType()
        right_type = self.right.evaluateType()
        numeric_types = ['integer', 'double']
        
        if self.operator in ['+', '-', '*', '/', '%','^']:
            if left_type in numeric_types and right_type in numeric_types:
                # If one is double, the result is double
                if left_type == 'double' or right_type == 'double':
                    self.cached_type = 'double'
                else:
                    self.cached_type = 'integer'
            elif (self.operator == '+') and (left_type == 'string' or right_type == 'string'):
                self.cached_type = 'string'

        return self.cached_type or "invalid"
    
    def accept(self, visitor):
        return visitor.visit_binary_op(self)
        
    def replace_with(self, new_node):
        attrs_to_check = ['value', 'receiver', 'arguments', 'left', 'right']  

        if self.parent:
            for attr in attrs_to_check:
                if hasattr(self.parent, attr):
                    value = getattr(self.parent, attr)
                    try:
                        if value == self:
                            setattr(self.parent, attr, new_node)
                        elif isinstance(value, (list, tuple)) and self in value:
                            index = value.index(self)
                            if isinstance(value, list):
                                value[index] = new_node
                            else:
                                value = value[:index] + (new_node,) + value[index + 1:]
                                setattr(self.parent, attr, value)
                    except Exception as e:
                        print(f"Error replacing node in '{attr}': {e}")

            new_node.parent = self.parent

            self.transformed = True
            del self
            
        else:
            print("No parent found for replacement")
        
    def __str__(self):
        return f"{str(self.left)} '{self.operator}' {str(self.right)}"
 
    def __repr__(self):
        return f"BinaryOp({repr(self.left)} '{self.operator}' {repr(self.right)})"

    def __eq__(self, other):
        return (isinstance(other, BinaryOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)

    def print_content(self, indent=0):
        print(" " * indent + f"BinaryOp (Operator {self.operator})")
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
            if left_type != 'integer' and left_type != 'double':
                return "invalid"
            self._cached_type = left_type
            
        return self._cached_type or "invalid"
    
    def accept(self, visitor):
        return visitor.visit_unary_op(self)
    
    def __str__(self):
        return f"'{self.operator}{self.left}'"

    def __repr__(self):
        return f"UnaryOp({self.operator}{repr(self.left)})"

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
        if left_type not in ['integer', 'double','string','boolean'] or right_type not in ['integer', 'double','string','boolean']:
            return "invalid"
        self._cached_type = 'boolean'
        return self._cached_type
    
    def accept(self, visitor):
        return visitor.visit_comparison(self)
    
    def __str__(self):
        return f"{str(self.left)} '{self.operator}' {str(self.right)}"
    
    def __repr__(self):
        return f"Comparison({repr(self.left)} '{self.operator}' {repr(self.right)})"
    
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
    
    def __str__(self):
        return f"'{str(self.left)}' '{self.operator}' '{str(self.right)}'"
    
    def __repr__(self):
        return f"LogicalOp('{repr(self.left)}' '{self.operator}' '{repr(self.right)}')"

    def __eq__(self, other):
        return (isinstance(other, LogicalOp) and
                self.left == other.left and
                self.operator == other.operator and
                self.right == other.right)
    
    def print_content(self, indent=0):
        print(" " * indent + f"LogicalOp (Operator: {self.operator})")
        self.left.print_content(indent + 2)
        self.right.print_content(indent + 2)        

# ------------------------- Literals ------------------------- #

class Primary(ASTNode):
    def __init__(self, value, line=None):
        self.value = value
        self.line = line
        self.type = self.evaluateType()

    def __eq__(self, other):
        return isinstance(other, Primary) and self.value == other.value and self.line == other.line

    def __str__(self):
        return f"{self.__class__.__name__}({self.value})"
    
    def print_content(self, indent=0):
        print(" " * indent + f"{self.__class__.__name__}: {str(self.value)}")

class Integer(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value , line = line)

    def evaluateType(self):
        if isinstance(self.value, int):
            return 'integer'
        return "invalid"
    
    def __str__(self):
        return f"{str(self.value)}"
    
    def __repr__(self):
        return f"Integer({self.value})"

    def accept(self, visitor):
        return visitor.visit_integer(self)
    
class Double(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value, line = line)

    def evaluateType(self):
        if isinstance(self.value, float):
            return 'double'
        return "invalid"
      
    def __str__(self):
        return f"{str(self.value)}"
   
    def __repr__(self):
        return f"Double({self.value})"

    def accept(self, visitor):
        return visitor.visit_double(self)

class Boolean(Primary):
    def __init__(self, value, line=None):
        self.value = value
        super().__init__(value, line = line)

    def evaluateType(self):
        if isinstance(self.value, str) and self.value.lower().strip() in ['true', 'false']:
            return 'boolean'
        return "invalid"
   
    def __str__(self):
        return f"{self.value}" 
   
    def __repr__(self):
        return f"Boolean({self.value})"
 
    def accept(self, visitor):
        return visitor.visit_boolean(self)

class String(Primary):
    def __init__(self, value, isTypeStr=None, line=None):
        self.value = value
        self.isTypeStr = isTypeStr
        super().__init__(value, line = line)

    def evaluateType(self):
        if self.value is not None and isinstance(self.value, str):
            return 'string'
        return "invalid"

    def __str__(self):
        return f"'{self.value}'"

    def __repr__(self):
        return f'"{self.value}"'
    
    def accept(self, visitor):
        return visitor.visit_string(self)

class Null(Primary):
    def __init__(self, line=None):
        super().__init__(None, line = line)

    def evaluateType(self):
        return 'null'
   
    def __str__(self):
        return "Null"
   
    def __repr__(self):
        return "Null"

    def accept(self, visitor):
        return visitor.visit_null(self)

    def print_content(self, indent=0):
        print(" " * indent + "Null")