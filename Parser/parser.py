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
        
        self.symbolTable = SymbolTable()  # Initialize the symbol table

        # Initialize currentToken and peekToken
        self.nextToken()    
        self.nextToken()    

    # -------------- Helper Methods -----------------
    
    def checkToken(self, type):
        if self.currentToken is None:
            return False
        return type == self.currentToken.type

    def checkPeek(self, type):
        return type == self.peekToken.type

    def match(self, type):
        if not self.checkToken(type):
            message = f"Expected type: {type.name}, got '{self.currentToken.value}' (type: {self.currentToken.type.name}) "
            report(message, lineNumber=self.line_number, type="Syntax")
            raise SyntaxError(message) 
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
        # TODO: uncomment this once completed parser
        # if has_error_occurred():
        #     print("Parsing terminated due to syntax errors.")
        #     return None
        
        
        statements = []
        while not self.checkToken(TokenType.EOF):
            stmt = self.statement()
            # empty lines will return None (i didn't skip them in lexer because i wanted accurate line numbers)
            if stmt is not None:
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
                self.match(TokenType.LPAREN)
                
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
                elif self.checkToken(TokenType.VAR_NAME):
                    if not self.symbolTable.lookup(self.currentToken.value):
                        report(f"Variable '{self.currentToken.value}' not declared.", lineNumber=self.line_number, type="Syntax")
                        self.panic()
                    valueToPrint = VariableReference(self.currentToken.value, self.line_number)
                    self.nextToken()
                else:
                    report(f"Invalid value to print: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
                    raise Exception()    # we need to panic here because we can't proceed with the parsing
                
                self.match(TokenType.RPAREN)
                node = Print(valueToPrint, self.line_number)
              
            # If-elif-else statement  
            elif self.checkToken(TokenType.IF):
                self.match(TokenType.IF)
                self.match(TokenType.LPAREN)
                comparison_node = self.expression()     # parse an expression rn, will validate it later
                self.match(TokenType.RPAREN)
                if_block_node = self.block()

                else_block_node = None
                elif_nodes = []

                while self.checkToken(TokenType.ELIF):
                    self.match(TokenType.ELIF)
                    self.match(TokenType.LPAREN)
                    elif_comparison_node = self.expression()
                    self.match(TokenType.RPAREN)
                    elif_block_node = self.block()
                    elif_nodes.append((elif_comparison_node, elif_block_node))

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

            # While loop
            elif self.checkToken(TokenType.WHILE):
                self.match(TokenType.WHILE)
                self.match(TokenType.LPAREN)
                comparison_node = self.expression()   # parse an expression rn, will validate it later
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = While(comparison_node, block_node, self.line_number)
            
            # For loop 
            elif self.checkToken(TokenType.FOR):
                # We will desugar to a while loop
                self.match(TokenType.FOR)
                self.match(TokenType.LPAREN)

                # Enter new scope for the for loop and add the counter variable
                self.symbolTable.enter_scope()
                
                # Counter initialization
                if self.checkToken(TokenType.SET):      # allow "set i = 0"
                    self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                initialCount = self.expression()
                self.symbolTable.add(var_name, initialCount)    # Add the counter variable to the symbol table so it is in scope for the comparison expression
                self.match(TokenType.SEMICOLON)

                # Comparison expression
                comparison_node = self.expression()   # parse an expression rn, will validate it later
                self.match(TokenType.SEMICOLON)

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
                    
                self.match(TokenType.RPAREN)

                # Parse the block within the same scope
                while_body = self.block(False,increment)
                
                # Desugar to a while loop
                initialization_node = VariableDeclaration(var_name, initialCount, self.line_number)
                node = Block([initialization_node, While(comparison_node, while_body, self.line_number)])
                
                self.symbolTable.exit_scope()  # Exit the scope after the for loop parsing is complete

            # Variable Declaration
            elif self.checkToken(TokenType.SET):
                self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                expression_node = self.expression()

                if not self.symbolTable.lookup(var_name):
                    node = VariableDeclaration(var_name, expression_node, self.line_number)
                    self.symbolTable.add(var_name, expression_node)
                else:
                    report(f"Variable '{var_name}' already declared. Please use 'Set'", lineNumber=self.line_number, type="Syntax")
                    # continue parsing. no need to panic :)
            
            # Variable Assignment
            elif self.checkToken(TokenType.VAR_NAME) and self.checkPeek(TokenType.EQ):
                # Handle Variable Updates and references
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                if self.checkToken(TokenType.EQ):
                    self.nextToken()
                    expr = self.expression()
                    node = VariableUpdated(var_name, expr, self.line_number)
                else:
                    node = VariableReference(var_name, self.line_number)

            # Input statement
            elif self.checkToken(TokenType.INPUT):
                self.match(TokenType.INPUT)
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                
                # Check if the variable is already declared
                if self.symbolTable.lookup(var_name):
                    report(f"Variable '{var_name}' already declared.", lineNumber=self.line_number, type="Syntax")
                else:
                    # Add the variable to the symbol table without initializing it
                    self.symbolTable.add(var_name, Null())
                    
                    # Create the Input node with just the variable name
                    node = Input(VariableReference(var_name,self.line_number), self.line_number)

            # random empty lines
            elif self.checkToken(TokenType.NEWLINE):
                self.nl()

            # catch-all
            else:
                report(f"Invalid statement at: {self.currentToken.value} ({self.currentToken.type.name})", lineNumber=self.line_number, type="Syntax")
                self.panic()   
                
        # when things get fucked, we panic
        except Exception as e:
            print(f"Parsing Error: {e}")
            self.panic()
        
        self.nl()  # Ensure newline is consumed after each statement
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
        print(f"node returned from logical: {node}")
        return node

    # for == and != operators
    def equality(self):
        node = self.comparison()  # Equality comes after comparison in precedence
        while self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ):
            operator = self.currentToken.value
            self.nextToken()
            right = self.comparison()   #change to expression() to allow for comparison of expressions
            node = Comparison(node, operator, right, self.line_number)
        print(f"node returned from equality: {node}")
        return node

    # for <, <=, >, >= operators
    def comparison(self):
        node = self.additive()  # Comparison comes after additive in precedence
        while self.isComparisonOperator():
            operator = self.currentToken.value
            self.nextToken()
            right = self.additive()
            node = Comparison(node, operator, right, self.line_number)
        print(f"node returned from comparison: {node}")
        return node

    # for + and - operators
    def additive(self):
        node = self.term()  # Additive comes after term in precedence
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            operator = self.currentToken.value
            self.nextToken()
            right = self.term()
            node = BinaryOp(node, operator, right, self.line_number)
        print(f"node returned from additive: {node}")
        return node

    # for * and / operators
    def term(self):
        node = self.unary()  # Term comes after unary in precedence
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = BinaryOp(node, operator, right, self.line_number)
        print(f"node returned from term: {node}")
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
            
        print(f"node returned from unary: {node}")
        return node

    def primary(self):
        if self.checkToken(TokenType.INTEGER):
            node = Integer(int(self.currentToken.value), self.line_number)
            self.nextToken()
        if self.checkToken(TokenType.FLOAT):
            try:
                node = Float(float(self.currentToken.value), self.line_number)
                self.nextToken()
            except ValueError:
                report(f"Invalid float value: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
        elif self.checkToken(TokenType.STRING):
            node = String(self.currentToken.value, self.line_number)
            self.nextToken()
        elif self.checkToken(TokenType.VAR_NAME):
            var_name = self.currentToken.value
            if not self.symbolTable.lookup(var_name):
                report(f"Variable '{var_name}' not declared.", lineNumber=self.line_number, type="Syntax")
            self.nextToken()
            # We desugar x++ or x-- to normal assignment
            if self.checkToken(TokenType.INCREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, self.line_number), '+', Integer(1, self.line_number)), self.line_number)
            elif self.checkToken(TokenType.DECREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name, self.line_number), '-', Integer(1, self.line_number)), self.line_number)
            else:
                node = VariableReference(var_name, self.line_number)
        elif self.checkToken(TokenType.NULL):
            node = Null(self.line_number)
            self.nextToken()
        # For nested expressions using parenthesis
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = self.expression()
            self.match(TokenType.RPAREN)
        else:
            report(f"Unexpected token: {self.currentToken.value}", lineNumber=self.line_number, type="Syntax")
        return node
    
    # Block parsing
    def block(self,createNewScope=True,appendNode=None):
        self.match(TokenType.LBRACE)
        
        # most of the time, a block will be followed by a newline
        if self.checkToken(TokenType.NEWLINE):
            self.nl()
            
        statements = []
        #  created a flag to control scope creation because my for loop has one scope for the entire loop.
        if createNewScope:
            self.symbolTable.enter_scope()
        
        while not self.checkToken(TokenType.RBRACE) and not self.checkToken(TokenType.EOF):
            statement = self.statement()
            if statement is not None:
                statements.append(statement)
            
        if createNewScope:
            self.symbolTable.exit_scope()
            
        self.match(TokenType.RBRACE)
        
        # the flag is used to append the nodes to the end of the block. used in for loop 
        if appendNode:
            statements.append(appendNode)
        return Block(statements)

    # Panic mode error recovery
    def panic(self):
        print(f"Parser panic at line {self.line_number}")

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
            sys.exit("Parsing terminated due to unresolvable syntax errors.")

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

        print(f"Resumed parsing at line {self.line_number}, current token: {self.currentToken.value}")
        
    def nl(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or \
            self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) 
            