import sys
from Lexer import *
from Error import report, has_error_occurred
from Ast import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.line_number = 1
        self.currentToken = None
        self.peekToken = None
        
        # Initialize currentToken and peekToken
        self.nextToken()    
        self.nextToken()    

    # -------------- Helper Methods -----------------
    
    def checkToken(self, type):
        """ 
        Will check if the current token is of the specified type
        """
        if self.currentToken is None:
            return False
        return type == self.currentToken.type

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
            report(errorMsg, lineNumber=self.line_number, type="Syntax")
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
    
    # ------------ Recursive Descent Parsing -----------------
    
    def parse(self):
        statements = []
        
        while not self.checkToken(TokenType.EOF):
            stmt = self.statement()
            if stmt is not None:     # empty lines will return None (i didn't skip them in lexer because i wanted accurate line numbers)
                statements.append(stmt)
        
        return Program(statements)

    def statement(self):
        node = None
        try:
            # Random blocks
            if self.checkToken(TokenType.LBRACE):
                node = self.block()
            
            # Print statement
            elif self.checkToken(TokenType.PRINT):
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
                        report(f"Invalid float value: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
                        self.panic()
                        
                elif self.checkToken(TokenType.IDENTIFIER) and self.checkPeek(TokenType.RPAREN) :
                    var_name = self.currentToken.value
                    valueToPrint = VariableReference(var_name, value = None, line = self.line_number)
                    self.nextToken()
                
                else:   #catch-all: assume its an expression, if its not self.expression will throw appropriate error
                    valueToPrint = self.expression()
                
                self.match(TokenType.RPAREN, errorMsg=f"No closing Parenthesis for print statement.")
                node = Print(valueToPrint, self.line_number)
              
            # If-elif-else statement  
            elif self.checkToken(TokenType.IF):
                self.match(TokenType.IF)
                self.match(TokenType.LPAREN, errorMsg="if conditions must be enclosed within parenthesis: '(' 'condition' ')'")
                comparison_node = self.expression()     # parse an expression rn, will validate it later
                self.match(TokenType.RPAREN, errorMsg="No closing parenthesis ')' for if statement found.")
                if_block_node = self.block()

                else_block_node = None
                elif_nodes = []
                
                if(self.checkToken(TokenType.NEWLINE)):
                    self.nl()   # consume newlines after the if block
                
                while self.checkToken(TokenType.ELIF):
                    self.match(TokenType.ELIF)
                    self.match(TokenType.LPAREN, errorMsg="elif conditions must be enclosed within parenthesis: '(' 'condition' ')'")
                    elif_comparison_node = self.expression()
                    self.match(TokenType.RPAREN, errorMsg="No closing parenthesis ')' for elif condition found.")
                    elif_block_node = self.block()
                    elif_nodes.append((elif_comparison_node, elif_block_node))
                    
                    # the token: '}' is usually followed by a newline
                    if(self.checkToken(TokenType.NEWLINE)):
                        self.nl()

                if(self.checkToken(TokenType.NEWLINE)):
                    self.nl()   
                
                if self.checkToken(TokenType.ELSE):
                    self.match(TokenType.ELSE)
                    else_block_node = self.block()
                
                # Define the base arguments for the If node
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
                function_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                self.match(TokenType.LPAREN, errorMsg="Function declarations must have parenthesis '(' after the function name.")
                parameters = []
                while not self.checkToken(TokenType.RPAREN):
                    parameter = self.currentToken.value
                    self.nextToken()
                    parameters.append(parameter)
                    if self.checkToken(TokenType.COMMA):
                        self.match(TokenType.COMMA)
                self.match(TokenType.RPAREN, errorMsg="No enclosing parenthesis ')' found for function declaration")
                block_node = self.block(functionBlock=True)
                node = FunctionDeclaration(function_name, parameters, block_node, self.line_number)
            
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
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", lineNumber=self.line_number, type="Syntax")
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the '=' token
                    update_expression = self.expression()  
                    increment = VariableUpdated(var_name,update_expression,self.line_number)
                elif self.checkPeek(TokenType.INCREMENT):
                    if self.currentToken.value != var_name: 
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", lineNumber=self.line_number, type="Syntax")
                    increment = VariableUpdated(var_name,BinaryOp(VariableReference(var_name,self.line_number), '+', Integer(1),self.line_number),self.line_number)
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the ++ token
                elif self.checkPeek(TokenType.DECREMENT):
                    if self.currentToken.value != var_name:
                        report(f"Expected variable '{var_name}' in increment expression, got '{self.currentToken.value}'", lineNumber=self.line_number, type="Syntax")
                    increment = VariableUpdated(var_name,BinaryOp(VariableReference(var_name,self.line_number), '-', Integer(1),self.line_number), self.line_number)
                    self.nextToken()    # skip the variable name
                    self.nextToken()    # skip the -- token
                else:
                    report(f"Expected increment expression, got '{self.currentToken.value} '", lineNumber=self.line_number, type="Syntax")
                    self.panic()
                    
                self.match(TokenType.RPAREN, errorMsg="Missing closing parenthesis ')' in For loop")

                # Parse the block within the same scope
                while_body = self.block(False,increment)
                
                # Desugar to a while loop
                initialization_node = VariableDeclaration(var_name, initialCount, self.line_number)
                node = Block([initialization_node, While(comparison_node, while_body, self.line_number)])
                
                self.symbolTable.exit_scope()  # Exit the scope after the for loop parsing is complete

            # Variable Declaration
            elif self.checkToken(TokenType.SET):
                self.match(TokenType.SET)
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)
                self.match(TokenType.EQ, errorMsg="Missing '=' in variable declaration")
                    
                # set x = input()
                if self.checkToken(TokenType.INPUT):
                    self.match(TokenType.INPUT)
                    self.match(TokenType.LPAREN, errorMsg="Input keyword should be followed by '()' ")
                    self.match(TokenType.RPAREN, errorMsg="Input keyword should be followed by '()' ")
                    # simply refer to the variable without declaring it, we will declare for user in generation
                    node = Input(
                        VariableReference(var_name, Null(), self.line_number),
                        self.line_number
                    )
                    
                # set x = foo()
                elif self.checkToken(TokenType.IDENTIFIER) and self.checkPeek(TokenType.LPAREN):
                    method_name = self.currentToken.value
                    self.nextToken()
                    self.match(TokenType.LPAREN)
                    arguments = []
                    while not self.checkToken(TokenType.RPAREN):
                        argument = self.primary()
                        arguments.append(argument)
                        if self.checkToken(TokenType.COMMA):
                            self.match(TokenType.COMMA)
                    self.match(TokenType.RPAREN)
                    function_call = FunctionCall(method_name, arguments, self.line_number)
                    node = VariableDeclaration(var_name, function_call, self.line_number)
                    
                else:  
                    expression_node = self.expression() 
                    node = VariableDeclaration(var_name, expression_node, self.line_number)
            
            # Variable Assignment / Increment(++) / Decrement(--) / Member Method Calls / Function Calls
            elif self.checkToken(TokenType.IDENTIFIER):
                """
                This entire elif block is for variable assignment, increment, decrement, member methods calls (in format var.function()),
                and user-defined function calls. since all of them start with an identifier, i grouped them together. can be a bit confusing to read.
                First we ensure the variable is declared, then we check for the different cases
                """
                
                var_name = self.currentToken.value
                self.match(TokenType.IDENTIFIER)

                # x++ is desugared to x = x + 1
                if self.checkToken(TokenType.INCREMENT):
                   self.match(TokenType.INCREMENT)
                   node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, value = None, line = self.line_number), '+', Integer(1)), self.line_number)
                
                # x-- is desugared to x = x - 1
                elif self.checkToken(TokenType.DECREMENT):
                    self.match(TokenType.DECREMENT)
                    node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, value = None, line = self.line_number), '-', Integer(1)), self.line_number)
                
                # member methods calls
                elif self.checkToken(TokenType.DOT): 
                    self.match(TokenType.DOT)
                    method_name = self.currentToken.value
                    self.match(TokenType.IDENTIFIER)
                    self.match(TokenType.LPAREN, errorMsg=f"Missing opening '(' for function call:{method_name}")
                    arguments = []
                    while not self.checkToken(TokenType.RPAREN):
                        arguments.append(self.expression())
                        if self.checkToken(TokenType.COMMA):
                            self.match(TokenType.COMMA)
                    self.match(TokenType.RPAREN, errorMsg=f"Missing closing parenthesis ')' for function call:{method_name}")
                    varRef = VariableReference(var_name, value = None, line = self.line_number)
                    node = MethodCall(varRef, method_name, arguments, self.line_number)
                
                # function calls without "set x ="
                elif self.checkToken(TokenType.LPAREN):
                    method_name = var_name
                    self.match(TokenType.LPAREN)
                    arguments = []
                    while not self.checkToken(TokenType.RPAREN):
                        argument = self.primary()
                        arguments.append(argument)
                        if self.checkToken(TokenType.COMMA):
                            self.match(TokenType.COMMA)
                    self.match(TokenType.RPAREN, errorMsg="Missing closing parenthesis ')' for function call")
                    node = FunctionCall(method_name, arguments, self.line_number)
                    
                # variable assignment. to an expression or input()
                elif self.checkToken(TokenType.EQ):
                        self.match(TokenType.EQ)
                        if(self.checkToken(TokenType.INPUT)):
                            # input in the format: x = input() { where x is a declared variable }
                            self.match(TokenType.INPUT)
                            self.match(TokenType.LPAREN, errorMsg="Input keyword should be followed by '()'")
                            self.match(TokenType.RPAREN, errorMsg="Input keyword should be followed by '()'")
                            node = Input(
                                VariableReference(var_name, Null(), self.line_number),
                                self.line_number
                            )
                        else:
                            # normal variable assignment: x = 5
                            expr = self.expression()
                            node = VariableUpdated(var_name, expr, self.line_number)
            
            # random empty lines
            elif self.checkToken(TokenType.NEWLINE):
                self.nl()

            # catch-all
            else:
                if self.checkToken(TokenType.RETURN):
                    report("Return statements are only allowed inside a functions body",type="Syntax",lineNumber=self.line_number)
                else:   
                    report(f"Invalid statement at: {self.currentToken.value} ({self.currentToken.type.name})", lineNumber=self.line_number, type="Syntax")
                    self.panic()   
                
        # when things get fucked, we panic
        except Exception as e:
            report(f"{e}")
            self.panic()
        
        self.nl()  # Ensure newline(s) is consumed after each statement
        return node

    # ------------ Expression Parsing -----------------
    
    # Calling self.expression() is more readable than self.logical()
    def expression(self):
        return self.logical()  
    
    # for  && and || operators
    def logical(self):
        node = self.equality()  # Logical comes after equality in precedence
        while self.checkToken(TokenType.AND) or self.checkToken(TokenType.OR):
            logical_operator = self.currentToken.value
            self.nextToken()
            right = self.equality()
            node = LogicalOp(node, logical_operator, right, self.line_number)
        # print(f"node returned from logical: {node}")
        return node

    # for == and != operators
    def equality(self):
        node = self.comparison()  # Equality comes after comparison in precedence
        while self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ):
            operator = self.currentToken.value
            self.nextToken()
            right = self.comparison()   #change to expression() to allow for comparison of expressions
            node = Comparison(node, operator, right, self.line_number)
        # print(f"node returned from equality: {node}")
        return node

    # for <, <=, >, >= operators
    def comparison(self):
        node = self.additive()  # Comparison comes after additive in precedence
        while self.isComparisonOperator():
            operator = self.currentToken.value
            self.nextToken()
            right = self.additive()
            node = Comparison(node, operator, right, self.line_number)
        # print(f"node returned from comparison: {node}")
        return node

    # for + and - operators
    def additive(self):
        node = self.term()  # Additive comes after term in precedence
        
        # string and numeric addition
        while self.checkToken(TokenType.PLUS):
            self.nextToken()
            right = self.term()

            # if only one operand is a string we convert the other such that: "hello"+ 2 => "hello2"
            if (isinstance(right, String) or isinstance(node, String)):
                if isinstance(right, Primary) and isinstance(node, Primary):  
                    rightValue = repr(right)
                    leftValue = repr(node)
                    node = BinaryOp(String(rightValue), "+", String(leftValue))
                else:
                    report(f"fInvalid string concatenation. Operands must be literals. received: '{right.type}' + '{node.type}' ")
                    
            else:
                node = BinaryOp(node, "+", right, self.line_number)

        while self.checkToken(TokenType.MINUS):
            self.nextToken()
            right = self.term()
            node = BinaryOp(node, "-", right, self.line_number)

        return node

    # for * and / operators
    def term(self):
        node = self.unary()  # Term comes after unary in precedence
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = BinaryOp(node, operator, right, self.line_number)
        # print(f"node returned from term: {node}")
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
            
        # print(f"node returned from unary: {node}")
        return node

    # for literals and parentheses
    def primary(self):
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
                report(f"Invalid float value: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
        
        # Booleans
        elif self.checkToken(TokenType.BOOLEAN):
            try:
                value = "true" if self.currentToken.value == "true" else "false"
                if value not in ["true",'false']:
                    report(f"Invalid boolean value. Should be 'true' or 'false. Found: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
                node = Boolean(value, self.line_number)
                self.nextToken()
            except ValueError:
                report(f"Invalid float value: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
        
        # Strings
        elif self.checkToken(TokenType.STRING):
            node = String(self.currentToken.value, self.line_number)
            self.nextToken()
            
        # Null types
        elif self.checkToken(TokenType.NULL):
            node = Null(self.line_number)
            self.nextToken()
       
        # Variable References
        elif self.checkToken(TokenType.IDENTIFIER):
            var_name = self.currentToken.value
            self.match(TokenType.IDENTIFIER)
                       
            # x++ 
            if self.checkToken(TokenType.INCREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, value = None, line = self.line_number), '+', Integer(1)), self.line_number)

            # x-- 
            elif self.checkToken(TokenType.DECREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, value = None, line = self.line_number), '-', Integer(1)), self.line_number)
            
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
                varRef = VariableReference(var_name, value = None, line = self.line_number)
                node = MethodCall(varRef, method_name, arguments, self.line_number)
            
            else:
                node = VariableReference(var_name, value = None, line = self.line_number)
        
        # ensure nested expressions are parsed correctly
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = self.expression()
            self.match(TokenType.RPAREN)
        
        # catch-all
        else:
            report(f"Unexpected token in expression: '{repr(self.currentToken.value)}' ", lineNumber=self.line_number, type="Syntax")
        
        return node
    
    # Block parsing
    def block(self, appendNode=None, functionBlock=None ):
        self.match(TokenType.LBRACE)
        
        # most of the time, a block will be followed by a newline
        if self.checkToken(TokenType.NEWLINE):
            self.nl()
            
        statements = []
        while not self.checkToken(TokenType.RBRACE) and not self.checkToken(TokenType.EOF):
            if self.checkToken(TokenType.RETURN):
                if functionBlock is None:
                    report("Return statements are only allowed inside a functions body",type="Syntax",lineNumber=self.line_number)
                    self.nextToken()
                    continue
                self.nextToken()
                if not self.checkToken(TokenType.NEWLINE):
                    returnVal = self.expression()
                    statement = Return(returnVal)
                else:
                    statement = Return(Null())
            else:
                statement = self.statement()
            
            if statement is not None:
                statements.append(statement)
        
        currentTokenErrFormat = "End of File" if self.checkToken(TokenType.EOF) else self.currentToken.value
        self.match(TokenType.RBRACE,errorMsg="Blocks must be closed by a '}' right brace,"+f"got: {currentTokenErrFormat}")
        
        # For loops are desugared to a while loop. we append increment node to the block
        if appendNode:
            statements.append(appendNode)
        return Block(statements)

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
            