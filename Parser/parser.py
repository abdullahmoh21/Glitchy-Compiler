import sys
from Lexer import *
from Error import report
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
            message = f"Expected {type.name}, got {self.currentToken.type.name}"
            report(message, lineNumber=self.line_number, type="(Parser) Syntax")
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
    
    def program(self):
        statements = []
        while not self.checkToken(TokenType.EOF):
            stmt = self.statement()
            if stmt is not None:
                statements.append(stmt)
            else: 
                print(f"None received in statement: currentToken: {self.currentToken.value}, next token: {self.peekToken.value}")
        
        return Program(statements, self.symbolTable)

    def statement(self):
        node = None
        try:
            if self.checkToken(TokenType.LBRACE):
                node = self.block()
            
            elif self.checkToken(TokenType.PRINT):
                self.match(TokenType.PRINT)
                self.match(TokenType.LPAREN)
                
                valueToPrint = None
                if self.checkToken(TokenType.STRING):
                    valueToPrint = String(self.currentToken.value)
                    self.nextToken()
                elif self.checkToken(TokenType.NUMBER):
                    valueToPrint = Number(int(self.currentToken.value))
                    self.nextToken()
                elif self.checkToken(TokenType.VAR_NAME):
                    if not self.symbolTable.lookup(self.currentToken.value):
                        report(f"Variable '{self.currentToken.value}' not declared.", lineNumber=self.line_number, type="(Parser) Syntax")
                    valueToPrint = VariableReference(self.currentToken.value)
                    self.nextToken()
                else:
                    report(f"Invalid value to print: {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
                
                self.match(TokenType.RPAREN)
                node = Print(valueToPrint)
                
            elif self.checkToken(TokenType.IF):
                self.match(TokenType.IF)
                self.match(TokenType.LPAREN)
                comparison_node = self.comparison()
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = If(comparison_node, block_node)  

            elif self.checkToken(TokenType.WHILE):
                self.match(TokenType.WHILE)
                self.match(TokenType.LPAREN)
                comparison_node = self.comparison()
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = While(comparison_node, block_node)
            
            elif self.checkToken(TokenType.FOR):
                self.match(TokenType.FOR)
                self.match(TokenType.LPAREN)

                # Enter new scope for the for loop and add the counter variable
                self.symbolTable.enter_scope()
                
                # Counter initialization
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                initialCount = self.expression()
                self.symbolTable.add(var_name, initialCount)    # Add the counter variable to the symbol table so next statements can access it
                self.match(TokenType.SEMICOLON)

                # Comparison expression
                comparison_node = self.comparison()
                self.match(TokenType.SEMICOLON)

                # Increment expression
                increment = None
                if self.checkToken(TokenType.VAR_NAME) and self.checkPeek(TokenType.EQ):
                    if self.currentToken.value != var_name:
                        report(f"Expected variable '{var_name}' for increment, got '{self.currentToken.value}'", lineNumber=self.line_number, type="(Parser) Syntax")
                    self.nextToken()    # Skip the variable name
                    self.nextToken()    # Skip the '=' token
                    increment = self.expression()
                    # increment = VariableUpdated(var_name, expressionNode)
                    
                else:
                    increment = self.expression()
                    
                self.match(TokenType.RPAREN)

                # Parse the block within the same scope
                block_node = self.block(False)
                
                node = For(VariableDeclaration(var_name, initialCount), comparison_node, increment, block_node)
                self.symbolTable.exit_scope()  # Exit the scope after the for loop parsing is complete

            elif self.checkToken(TokenType.SET):
                self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                expression_node = self.expression()

                if not self.symbolTable.lookup(var_name):
                    node = VariableDeclaration(var_name, expression_node)
                    self.symbolTable.add(var_name, expression_node)
                else:
                    report(f"Variable '{var_name}' already declared. Please use 'Set'", lineNumber=self.line_number, type="(Parser) Syntax")

            elif self.checkToken(TokenType.VAR_NAME) and self.checkPeek(TokenType.EQ):
                # Handle Variable Updates and references
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                if self.checkToken(TokenType.EQ):
                    self.nextToken()
                    expr = self.expression()
                    node = VariableUpdated(var_name, expr)
                else:
                    node = VariableReference(var_name)

            elif self.checkToken(TokenType.INPUT):
                self.match(TokenType.INPUT)
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                
                # Check if the variable is already declared
                if self.symbolTable.lookup(var_name):
                    report(f"Variable '{var_name}' already declared.", lineNumber=self.line_number, type="(Parser) Syntax")
                else:
                    # Add the variable to the symbol table without initializing it
                    self.symbolTable.add(var_name, Null())
                    
                    # Create the Input node with just the variable name
                    node = Input(VariableReference(var_name))

            # empty lines
            elif self.checkToken(TokenType.NEWLINE):
                self.nl()
            else:
                report(f"Invalid statement at: {self.currentToken.value} ({self.currentToken.type.name})", lineNumber=self.line_number, type="(Parser) Syntax")
                self.panic()    # To skip to the next statement

        except Exception as e:
            # Enter Panic Mode
            self.panic()
        
        self.nl()  # Ensure newline is consumed after each statement
        return node

    def comparison(self):
        left = self.expression()
        if not self.isComparisonOperator():
            report(f"Expected comparison operator, got {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
        
        operator = self.currentToken.value
        self.nextToken()
        right = self.expression()
        comparison_node = Comparison(left, operator, right)

        while self.isComparisonOperator():
            operator = self.currentToken.value
            self.nextToken()
            right = self.expression()
            comparison_node = Comparison(left, operator, right)

        return comparison_node

    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or \
            self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or \
            self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ) or \
            self.checkToken(TokenType.AND) or self.checkToken(TokenType.OR)

    def expression(self):
        node = self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            operator = self.currentToken.value
            self.nextToken()
            right = self.term()
            node = BinaryOp(node, operator, right)
        return node

    def term(self):
        node = self.unary()
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = BinaryOp(node, operator, right)
        return node

    def unary(self):
        operator = None
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS) or self.checkToken(TokenType.NOT):
            operator = self.currentToken.value
            self.nextToken()
        
        node = self.primary()
        if operator:
            node = UnaryOp(operator, node)
        return node

    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            node = Number(int(self.currentToken.value))
            self.nextToken()
        elif self.checkToken(TokenType.VAR_NAME):
            var_name = self.currentToken.value
            if not self.symbolTable.lookup(var_name):
                report(f"Variable '{var_name}' not declared.", lineNumber=self.line_number, type="(Parser) Syntax")
            self.nextToken()
            if self.checkToken(TokenType.INCREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name), '+', Number(1)))
            elif self.checkToken(TokenType.DECREMENT):
                self.nextToken()
                node = VariableUpdated(var_name, BinaryOp(VariableReference(var_name), '-', Number(1)))
            else:
                node = VariableReference(var_name)
        # elif self.checkToken(TokenType.NULL):
        #     node = Null()
        #     self.nextToken()
        # for nested expressions using parenthesis
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = self.expression()
            self.match(TokenType.RPAREN)
        else:
            report(f"Unexpected token: {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
        return node


    def block(self,createNewScope=True):
        self.match(TokenType.LBRACE)
        
        # most of the time, a block will be followed by a newline
        if self.checkToken(TokenType.NEWLINE):
            self.nl()
            
        statements = []
        #  created a flag to control scope creation because my for loop has one scope for the entire loop.
        if createNewScope:
            self.symbolTable.enter_scope()
        
        while not self.checkToken(TokenType.RBRACE):
            statements.append(self.statement())
            
        if createNewScope:
            self.symbolTable.exit_scope()
            
        self.match(TokenType.RBRACE)
        return Block(statements)

    def nl(self):
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
            
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

        # After synchronization point, try to consume newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Check if we are at the end of the file, if so, exit
        if self.checkToken(TokenType.EOF):
            sys.exit("Parsing terminated due to unresolvable syntax errors.")

        # Try to synchronize at the end of the current block or statement
        if self.checkToken(TokenType.RBRACE):
            self.match(TokenType.RBRACE)
        elif self.checkToken(TokenType.NEWLINE):
            self.nl()
        else:
            # If we are not at a known synchronization point, skip until a newline or EOF
            self.nl()
