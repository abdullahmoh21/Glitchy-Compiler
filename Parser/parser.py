import sys
import re
from Lexer import *
from Error import report, has_error_occurred
from Ast import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.line_number = 1
        self.currentToken = None
        self.peekToken = None
        self.inFunctionBlock = False
        
        # Initialize currentToken and peekToken
        self.nextToken()    
        self.nextToken()    

    # -------------- General Helper Methods ----------------- #
    
    def checkToken(self, *types):
        """ 
        Will check if the current token is of any of the specified types.
        Supports multiple token types and variable arguments.
        """
        if self.currentToken is None:
            return False
        return self.currentToken.type in types

    def checkPeek(self, type):
        """ 
        Will check if the NEXT token is of the specified type
        """
        return type == self.peekToken.type

    def match(self, type, errorMsg = None):
        """
        will consume the current token if it is of the specified type. otherwise report
        """
        if not self.checkToken(type):
            if errorMsg is None:
                errorMsg = f"Expected type: {type.name}, got '{self.currentToken.value}' (type: {self.currentToken.type.name}) "    #generic
            report(errorMsg, line=self.line_number, type="Syntax")
            self.panic()
        self.nextToken()

    def nextToken(self):
        # To ensure tokens don't loop back to the start since we are directly connected to lexer
        if self.currentToken and self.checkToken(TokenType.EOF):
            return self.currentToken
        
        self.currentToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        
        if self.currentToken and self.currentToken.type == TokenType.NEWLINE:
            self.line_number += 1
    
    def validateType(self, type_string, variable_err_msg = None):
        """
        first three chars of type name up till the end are allowed. int, inte, integ, intege, integer are all allowed 
        Why? 
        Why not?
        """
        type_pattern = r"""
            \b(?:
                (?P<int_type>int(?:eger|ege|eg|e)?)   |  # Matches int, inte, integ, intege, integer
                (?P<float_type>float)                |  # Matches float
                (?P<str_type>str(?:ing|in|i)?)       |  # Matches str, stri, strin, string
                (?P<bool_type>bool(?:ean|ea|e)?)        # Matches bool, boole, boolea, boolean
            )\b
        """
        match = re.search(type_pattern, type_string, re.VERBOSE)
        type_tag = 'invalid'
        
        if match is not None:
            if match.group("int_type"):
                type_tag = 'integer'
            elif match.group("float_type"):
                type_tag= 'float'
            elif match.group("str_type"):
                type_tag = 'string'
            elif match.group("bool_type"):
                type_tag = 'boolean'      
        
        return type_tag    

        # Panic mode error recovery
    
    def panic(self):

        # Skip tokens until we find a synchronization point or reach end of file
        while not (self.checkToken(TokenType.NEWLINE) or 
                self.checkToken(TokenType.RBRACE) or 
                self.checkToken(TokenType.IF) or 
                self.checkToken(TokenType.WHILE) or 
                self.checkToken(TokenType.FOR) or 
                self.checkToken(TokenType.PRINT) or 
                self.checkToken(TokenType.SET) or 
                self.checkToken(TokenType.INPUT) or 
                self.checkToken(TokenType.EOF)):
            self.nextToken()

        # Consume newlines to ensure we are on a new line
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Check if we are at the end of the file, if so, exit
        if self.checkToken(TokenType.EOF):
            sys.exit("Parsing terminated.")

        # Try to synchronize at the end of the current block or statement
        if self.checkToken(TokenType.RBRACE):
            self.match(TokenType.RBRACE)
        elif self.checkToken(TokenType.NEWLINE):
            self.nextToken()  # Consume newline
        else:
            # Skip to the next known synchronization point
            while not (self.checkToken(TokenType.NEWLINE) or 
                    self.checkToken(TokenType.RBRACE) or 
                    self.checkToken(TokenType.IF) or 
                    self.checkToken(TokenType.WHILE) or 
                    self.checkToken(TokenType.FOR) or 
                    self.checkToken(TokenType.PRINT) or 
                    self.checkToken(TokenType.SET) or 
                    self.checkToken(TokenType.INPUT) or 
                    self.checkToken(TokenType.EOF)):
                self.nextToken()
   
    def nl(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or \
            self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) 
    
    # ------------ Recursive Descent Parsing ----------------- #
    
    def parse(self):
        statements = []

        # statement() can return an array of nodes or a single node.
        # sometimes I want to add multiple nodes in one pass such as for multiple variable declarations
        # statement() is also called recursively, without this we would have nested arrays everywhere
        while not self.checkToken(TokenType.EOF):
            stmt = self.statement()
            if stmt is not None:     
                if isinstance(stmt, list):
                    statements.extend(stmt)
                else:
                    statements.append(stmt)
        
        return Program(statements)

    def statement(self):
        node = None
        try:
            # Print statement
            if self.checkToken(TokenType.PRINT):
                self.match(TokenType.PRINT)
                self.match(TokenType.LPAREN, errorMsg="Print expressions must be enclosed with parenthesis: '(' value to print ')'")
                
                valueToPrint = None
                if self.checkToken(TokenType.STRING):
                    valueToPrint = String(self.currentToken.value)
                    self.nextToken()
                    
                elif self.checkToken(TokenType.INTEGER):
                    valueToPrint = Integer(int(self.currentToken.value))
                    self.nextToken()
                    
                elif self.checkToken(TokenType.FLOAT):
                    try:
                        valueToPrint = Float(float(self.currentToken.value))
                        self.nextToken()
                    except ValueError:
                        report(f"Invalid float value: {self.currentToken.value}", line=self.line_number, type="Syntax")
                        self.panic()
                        
                elif self.checkToken(TokenType.IDENTIFIER) and self.checkPeek(TokenType.RPAREN) :
                    var_name = self.currentToken.value
                    valueToPrint = VariableReference(var_name, line = self.line_number)
                    self.nextToken()
                
                else:   #catch-all: assume its an expression, if its not self.expression will throw appropriate error
                    valueToPrint = self.expression()
                
                self.match(TokenType.RPAREN, errorMsg=f"No closing Parenthesis for print statement.")
                node = Print(valueToPrint, self.line_number)
                
            # If-elif-else statements  
            elif self.checkToken(TokenType.IF):
                self.match(TokenType.IF)
                self.match(TokenType.LPAREN, errorMsg="if conditions must be enclosed within parenthesis: '(' 'condition' ')'")
                comparison_node = self.expression()    
                self.match(TokenType.RPAREN, errorMsg="No closing parenthesis ')' for if statement found.")
                if_block_node = self.block()

                else_block_node = None
                elif_nodes = []
                
                if(self.checkToken(TokenType.NEWLINE)):
                    self.nl()   
                
                while self.checkToken(TokenType.ELIF):
                    self.match(TokenType.ELIF)
                    self.match(TokenType.LPAREN, errorMsg="elif conditions must be enclosed within parenthesis: '(' 'condition' ')'")
                    elif_comparison_node = self.expression()
                    self.match(TokenType.RPAREN, errorMsg="No closing parenthesis ')' for elif condition found.")
                    elif_block_node = self.block()
                    elif_nodes.append((elif_comparison_node, elif_block_node))
                    
                    if(self.checkToken(TokenType.NEWLINE)):
                        self.nl()

                if(self.checkToken(TokenType.NEWLINE)):
                    self.nl()   
                
                if self.checkToken(TokenType.ELSE):
                    self.match(TokenType.ELSE)
                    else_block_node = self.block()
                
                base_args = {
                    'comparison': comparison_node,
                    'block': if_block_node,
                    'line': self.line_number
                }
                # Add optional arguments conditionally
                if elif_nodes:
                    base_args['elifNodes'] = elif_nodes

                if else_block_node:
                    base_args['elseBlock'] = else_block_node

                node = If(**base_args)

            # Function Declaration
            elif self.checkToken(TokenType.FUNCTION):
                self.match(TokenType.FUNCTION)
                return_type = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                return_type_tag = self.validateType(return_type)
                function_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                self.match(TokenType.LPAREN, errorMsg="Function declarations must have parenthesis '(' after the function name.")
                parameters = []
                while not self.checkToken(TokenType.RPAREN):
                    parameter_name = self.currentToken.value
                    self.nextToken()
                    self.match(TokenType.COLON,errorMsg="Missing token ':' Parameters must be in format parm_name ':' param_type")
                    param_type = self.currentToken.value
                    param_type_tag = self.validateType(param_type)
                    self.nextToken()
                    parameters.append(Parameter(parameter_name, param_type_tag))
                    if self.checkToken(TokenType.COMMA): #trailing comma's allowed
                        self.match(TokenType.COMMA)
                self.match(TokenType.RPAREN, errorMsg="No enclosing parenthesis ')' found for function declaration")
                
                self.inFunctionBlock = True
                function_body = self.block()
                self.inFunctionBlock = False
                node = FunctionDeclaration(function_name, return_type_tag, parameters, function_body, self.line_number)
            
            elif self.checkToken(TokenType.RETURN):
                if self.inFunctionBlock == False:
                    report("Return statements are only allowed inside a functions body",type="Syntax",line=self.line_number)
                    self.panic()
                    
                self.nextToken()
                if not self.checkToken(TokenType.NEWLINE):
                    returnVal = self.expression()
                    node = Return(returnVal, self.line_number)
                else:
                    node = Return(Null(),self.line_number)
            
            # While loop
            elif self.checkToken(TokenType.WHILE):
                self.match(TokenType.WHILE)
                self.match(TokenType.LPAREN, errorMsg="While conditions must be enclosed within parenthesis: '(' 'condition' ')'")
                comparison_node = self.expression()   # parse an expression rn, will validate it later
                self.match(TokenType.RPAREN, errorMsg="No closing parenthesis ')' for while condition found.")
                block_node = self.block()
                node = While(comparison_node, block_node, self.line_number)
            
            # For loop 
            elif self.checkToken(TokenType.FOR):
                # We will desugar to a while loop
                self.match(TokenType.FOR)
                self.match(TokenType.LPAREN, errorMsg="Missing '(' after 'for' ")

                # Counter initialization
                if self.checkToken(TokenType.SET):      # allow "set i = 0"
                    self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER, errorMsg=f"Expected counter variable, got: {var_name}")
                self.match(TokenType.EQ,errorMsg="Missing '=' token in for loop's counter initialization")
                initialCount = self.expression()
                self.match(TokenType.SEMICOLON, errorMsg=f"For loops Counter initialization should be followed by a semicolon, got: {self.currentToken.value}")

                # Comparison expression
                comparison_node = self.expression()   # parse an expression rn, will validate it later
                self.match(TokenType.SEMICOLON, errorMsg="For loop's Comparison should be followed by a semicolon, got: {self.currentToken.value}")

                # Increment expression
                increment = None
                if self.checkPeek(TokenType.EQ):
                    if self.currentToken.value != var_name:     # continue parsing. no need to panic :)
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", line=self.line_number, type="Syntax")
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the '=' token
                    update_expression = self.expression()  
                    increment = VariableUpdated(var_name,update_expression,self.line_number)
                elif self.checkPeek(TokenType.INCREMENT):
                    if self.currentToken.value != var_name: 
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", line=self.line_number, type="Syntax")
                    increment = VariableUpdated(var_name,BinaryOp(VariableReference(var_name, self.line_number), '+', Integer(1),self.line_number),self.line_number)
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the ++ token
                elif self.checkPeek(TokenType.DECREMENT):
                    if self.currentToken.value != var_name:
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", line=self.line_number, type="Syntax")
                    increment = VariableUpdated(var_name,BinaryOp(VariableReference(var_name, self.line_number), '-', Integer(1),self.line_number), self.line_number)
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the -- token
                else:
                    report(f"Expected increment expression, got '{self.currentToken.value} '", line=self.line_number, type="Syntax")
                    self.panic()
                    
                self.match(TokenType.RPAREN, errorMsg="Missing closing parenthesis ')' in For loop")

                # Parse the block within the same scope
                while_body = self.block(appendNode=increment)
                
                # Desugar to a while loop
                initialization_node = VariableDeclaration(var_name, initialCount, self.line_number)
                node = Block([initialization_node, While(comparison_node, while_body, self.line_number)])
                
            # (SET) Variable Declaration
            elif self.checkToken(TokenType.SET):
                self.match(TokenType.SET)
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                
                # Handle optional type annotation
                type_tag = self.handle_type_annotation(var_name)
                
                self.match(TokenType.EQ, errorMsg="Missing '=' in variable declaration")
                
                if self.checkToken(TokenType.INPUT):
                    if type_tag is not None:
                        report(f"Cannot type annotate function calls like input(). Invalid token: '{type_tag}'", type="Type Annotation", line=self.line_number)
                    node = self.handle_input(var_name)
                else:
                    node = self.handle_variable_declaration(var_name, type_tag)
    
            # Variable assignment, increment, decrement, member methods calls, and user-defined function calls.
            elif self.checkToken(TokenType.IDENTIFIER):
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)

                if self.checkToken(TokenType.INCREMENT):
                    node = self.handle_increment(var_name)

                elif self.checkToken(TokenType.DECREMENT):
                    node = self.handle_decrement(var_name)

                elif self.checkToken(TokenType.DOT):
                    node = self.handle_member_method_call(var_name)

                elif self.checkToken(TokenType.LPAREN):
                    node = self.handle_function_call(var_name)

                elif self.checkToken(TokenType.EQ, TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL):
                    node = self.handle_variable_assignment(var_name)

            # (\n) random empty lines
            elif self.checkToken(TokenType.NEWLINE):
                self.nl()
            
            # Random blocks
            elif self.checkToken(TokenType.LBRACE):
                node = self.block()
            
            # TODO: helper function to check token and give appropriate errs? like lone elif/else, 
            # catch-all
            else:
                report(f"Invalid statement at: '{self.currentToken.value}' ({self.currentToken.type.name})", line=self.line_number, type="Syntax")
                self.panic()   
        
        # when things get fucked, we panic
        except Exception as e:
            report(f"{e}")
            self.panic()
        
        self.nl()  
        return node or None

    # ------------ Statement Helpers ----------------- #
    
    def handle_type_annotation(self, var_name):
            type_tag = None
            if self.checkToken(TokenType.COLON):
                self.nextToken()
                type_annotation = self.currentToken.value
                self.nextToken()
                type_tag = self.validateType(type_annotation)
                if type_tag == 'invalid':
                    report(f"Invalid type annotation received: '{type_annotation}' ", type="Type Annotation", line=self.line_number)
                    type_tag = None
            return type_tag

    def handle_input(self, var_name, type_tag):
            
        self.match(TokenType.INPUT)
        self.match(TokenType.LPAREN, errorMsg="Input keyword should be followed by '()'")
        self.match(TokenType.RPAREN, errorMsg="Input keyword should be followed by '()'")
        
        return Input(
            VariableReference(var_name, self.line_number),
            self.line_number
        )

    def handle_variable_declaration(self, var_name, type_tag):
        var_expr = self.expression()
        if self.checkToken(TokenType.COMMA):
            node = []
            self.nextToken()
            node.append(VariableDeclaration(var_name, var_expr, annotation=type_tag, line=self.line_number))
            
            # set x:int = 10, y:string = "hello", 
            while not self.checkToken(TokenType.NEWLINE):
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER, errorMsg=f"Missing variable name after comma in multiple assignment, got: '{repr(self.currentToken.value)}' \n\t format: set x = 10, y = 20, z = \"hello world \" ")
                if self.checkToken(TokenType.COLON):
                    type_tag = self.handle_type_annotation(var_name)
                self.match(TokenType.EQ, errorMsg=f"Missing '=' after variable name '{var_name}' in multiple assignment, got: '{repr(self.currentToken.value)}' \n\t format: set x = 10, y = 20, z = \"hello world \" ")
                var_expr = self.expression()
                if self.checkToken(TokenType.COMMA):
                    self.nextToken()
                node.append(VariableDeclaration(var_name, var_expr, annotation=type_tag, line=self.line_number))
            
        else:
            node = VariableDeclaration(var_name, var_expr, annotation=type_tag, line=self.line_number)
            
        return node

    def handle_increment(self, var_name):
        self.match(TokenType.INCREMENT)
        return VariableUpdated(
            var_name,
            BinaryOp(VariableReference(var_name, line=self.line_number), '+', Integer(1)),
            self.line_number
        )

    def handle_decrement(self, var_name):
        self.match(TokenType.DECREMENT)
        return VariableUpdated(
            var_name,
            BinaryOp(VariableReference(var_name, line=self.line_number), '-', Integer(1)),
            self.line_number
        )

    def handle_member_method_call(self, var_name):
        self.nextToken()
        method_name = self.currentToken.value
        self.match(TokenType.IDENTIFIER)
        self.match(TokenType.LPAREN, errorMsg=f"Missing opening '(' for function call:{method_name}")
        arguments = []
        while not self.checkToken(TokenType.RPAREN):
            arguments.append(self.expression())
            if self.checkToken(TokenType.COMMA):
                self.match(TokenType.COMMA)
        self.match(TokenType.RPAREN, errorMsg=f"Missing closing parenthesis ')' for function call:{method_name}")
        varRef = VariableReference(var_name, line=self.line_number)
        return MethodCall(varRef, method_name, arguments, self.line_number)

    def handle_function_call(self, func_name):
        self.nextToken()
        args = []
        while not self.checkToken(TokenType.RPAREN):
            arg_value = self.primary()
            args.append(Argument(arg_value))
            if self.checkToken(TokenType.COMMA):
                self.match(TokenType.COMMA)
        self.match(TokenType.RPAREN)
        return FunctionCall(func_name, args, self.line_number)

    def handle_variable_assignment(self, var_name):
        if self.checkToken(TokenType.PLUS_EQUAL, TokenType.MINUS_EQUAL):
            assignment_operator = self.currentToken.value
            self.nextToken()
            expr = self.expression()
            
            operator = assignment_operator[0]
            print(f"operator extracted: {operator}")
            
            var = VariableReference(var_name)
            expr = BinaryOp(var, operator, expr)
            return VariableUpdated(var_name, expr, line= self.line_number)
        
        self.match(TokenType.EQ, f"Expected an '=' token but instead got: {self.currentToken.value}")
        if self.checkToken(TokenType.INPUT):
            self.match(TokenType.INPUT)
            self.match(TokenType.LPAREN, errorMsg="Input keyword should be followed by '()'")
            self.match(TokenType.RPAREN, errorMsg="Input keyword should be followed by '()'")
            return Input(
                VariableReference(var_name, self.line_number),
                self.line_number
            )
        
        elif self.checkToken(TokenType.IDENTIFIER):
            vars = [var_name]
            while self.checkToken(TokenType.IDENTIFIER):
                var_name = self.currentToken.value
                vars.append(var_name)
                self.nextToken()
                if self.checkToken(TokenType.EQ):
                    self.nextToken()
            expr = self.expression()
            if expr is None:
                report(f"Expected an expression in multiple variable assignment, got: {repr(self.currentToken.value)} instead",type="Syntax",line=self.line_number)
            nodes = []
            for var_name in vars:
                update_node = VariableUpdated(var_name, expr, self.line_number)
                nodes.append(update_node)
            
            return nodes
            
        else:
            expr = self.expression()
            return VariableUpdated(var_name, expr, self.line_number)

    def block(self, appendNode=None ):
        self.match(TokenType.LBRACE)
        
        # most of the time, a block will be followed by a newline
        if self.checkToken(TokenType.NEWLINE):
            self.nl()
            
        statements = []
        while not self.checkToken(TokenType.RBRACE) and not self.checkToken(TokenType.EOF):
            statement = self.statement()
        
            if statement is not None:     
                if isinstance(statement, list):
                    statements.extend(statement)
                else:
                    statements.append(statement)
        
        currentTokenErrFormat = "End of File" if self.checkToken(TokenType.EOF) else self.currentToken.value
        self.match(TokenType.RBRACE,errorMsg="Blocks must be closed by a '}' right brace,"+f"got: '{currentTokenErrFormat}'")
        
        # For loops are desugared to a while loop. we append increment node to the block
        if appendNode:
            statements.append(appendNode)
        return Block(statements)

    # ---------------- Expression Parsing ----------------- #
    
    # Calling self.expression() is more readable than self.logical()
    def expression(self):
        return self.logical()  
    
    # for  && and || operators
    def logical(self):
        node = self.ternary()  # Logical comes after equality in precedence
        while self.checkToken(TokenType.AND) or self.checkToken(TokenType.OR):
            logical_operator = self.currentToken.value
            self.nextToken()
            right = self.equality()
            node = LogicalOp(node, logical_operator, right, self.line_number)
        return node

    # for ? : ternary operator
    def ternary(self):
        node = self.equality()  # Ternary comes after equality in precedence
        if self.checkToken(TokenType.QMARK):
            condition = node
            self.nextToken()
            true_expr = self.expression()  
            self.match(TokenType.COLON, "Expected ':' after true expression in ternary operator")
            false_expr = self.ternary() 
            node = TernaryOp(condition, true_expr, false_expr, self.line_number)
        return node
    
    # for == and != operators
    def equality(self):
        node = self.comparison()  # Equality comes after comparison in precedence
        while self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ):
            operator = self.currentToken.value
            self.nextToken()
            right = self.comparison()   
            node = Comparison(node, operator, right, self.line_number)
        return node

    # for <, <=, >, >= operators
    def comparison(self):
        node = self.additive()  # Comparison comes after additive in precedence
        while self.isComparisonOperator():
            operator = self.currentToken.value
            self.nextToken()
            right = self.additive()
            node = Comparison(node, operator, right, self.line_number)
        return node

    # for + and - operators
    def additive(self):
        node = self.term()  # Additive comes after term in precedence
        
        while self.checkToken(TokenType.PLUS):
            self.nextToken()
            right = self.term()

            # if only one operand is a string we convert the other such that: "hello"+ 2 => "hello2"
            if (isinstance(right, String) or isinstance(node, String)):
                if isinstance(right, Primary) and isinstance(node, Primary):  
                    right_str = repr(right)
                    left_str = repr(node)

                    node = String(left_str+right_str)
                else:
                    report(f"fInvalid string concatenation. Operands must be literals. received: '{right.type}' + '{node.type}' ")
                    
            else:
                node = BinaryOp(node, "+", right, self.line_number)

        while self.checkToken(TokenType.MINUS):
            self.nextToken()
            right = self.term()
            node = BinaryOp(node, "-", right, self.line_number)

        return node

    # for *, /, % operators 
    def term(self):
        node = self.factor()  # Term comes after factor in precedence
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH) or self.checkToken(TokenType.MODUlO):
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = BinaryOp(node, operator, right, self.line_number)
        return node
    
    # for ^ operator (exponentiation)
    def factor(self):
        node = self.unary()  # Factor comes after unary in precedence
        
        while self.checkToken(TokenType.POW): 
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = BinaryOp(node, operator, right, self.line_number)
        
        return node

    # for +5, -5, and ! operators
    def unary(self):
        operator = None
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS) or self.checkToken(TokenType.NOT):
            operator = self.currentToken.value
            self.nextToken()
        
        node = self.primary()
        if operator:
            node = UnaryOp(operator, node, self.line_number)
            
        return node

    # for literals and nested expressions
    def primary(self):
        node = None
        # Integers
        if self.checkToken(TokenType.INTEGER):
            node = Integer(value=int(self.currentToken.value), line=self.line_number)
            self.nextToken()
        
        # Floats
        elif self.checkToken(TokenType.FLOAT):
            try:
                node = Float(float(self.currentToken.value), self.line_number)
                self.nextToken()
            except ValueError:
                report(f"Invalid float value: {self.currentToken.value}", line=self.line_number, type="Syntax")
        
        # Booleans
        elif self.checkToken(TokenType.BOOLEAN):
            try:
                value = "true" if self.currentToken.value == "true" else "false"
                if value not in ["true",'false']:
                    report(f"Invalid boolean value. Should be 'true' or 'false. Found: {self.currentToken.value}", line=self.line_number, type="Syntax")
                node = Boolean(value, self.line_number)
                self.nextToken()
            except ValueError:
                report(f"Invalid float value: {self.currentToken.value}", line=self.line_number, type="Syntax")
        
        # Strings
        elif self.checkToken(TokenType.STRING):
            node = String(self.currentToken.value, self.line_number)
            self.nextToken()
            
        # Null types
        elif self.checkToken(TokenType.NULL):
            node = Null(self.line_number)
            self.nextToken()
       
        # Function calls
        elif self.checkToken(TokenType.IDENTIFIER) and self.checkPeek(TokenType.LPAREN):
            func_name = self.currentToken.value
            self.nextToken()
            self.match(TokenType.LPAREN)
            args = []
            while not self.checkToken(TokenType.RPAREN):
                arg_value = self.expression()
                args.append(Argument(arg_value))
                if self.checkToken(TokenType.COMMA):
                    self.match(TokenType.COMMA)
            self.match(TokenType.RPAREN)
            node = FunctionCall(func_name, args, self.line_number)
       
        # Variable References
        elif self.checkToken(TokenType.IDENTIFIER):
            var_name = self.currentToken.value
            self.match(TokenType.IDENTIFIER)
                       
            # x++ 
            if self.checkToken(TokenType.INCREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name,line = self.line_number), '+', Integer(1)), self.line_number)

            # x-- 
            elif self.checkToken(TokenType.DECREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, line = self.line_number), '-', Integer(1)), self.line_number)
            
            # Method calls
            elif self.checkToken(TokenType.DOT):
                self.nextToken()
                method_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                self.match(TokenType.LPAREN,errorMsg=f"missing opening '(' parenthesis after function call: {method_name}")
                arguments = []
                while not self.checkToken(TokenType.RPAREN):
                    arguments.append(self.expression())
                    if self.checkToken(TokenType.COMMA):
                        self.match(TokenType.COMMA)
                self.match(TokenType.RPAREN, errorMsg=f"missing opening '(' parenthesis after function call: {method_name}")
                varRef = VariableReference(var_name, line = self.line_number)
                node = MethodCall(varRef, method_name, arguments, self.line_number)
            
            else:
                node = VariableReference(var_name, line = self.line_number)
        
        # ensure nested expressions are parsed correctly
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = self.expression()
            self.match(TokenType.RPAREN)
        
        # catch-all
        else:
            report(f"Unexpected token in expression: {repr(self.currentToken.value)} ", line=self.line_number, type="Syntax")
        
        return node 
    