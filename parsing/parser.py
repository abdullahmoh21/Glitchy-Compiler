import sys
from scanning.lexer import *
from .glitchAst import *

class Parser:
    def __init__(self, lexer, abortFunction):
        self.lexer = lexer
        self.abort = abortFunction  # Global function for errors
        self.line_number = 1
        self.currentToken = None
        self.peekToken = None
        
        self.symbolTable = SymbolTable()  # SymbolTable instance from AST

        # Initialize currentToken and peekToken
        self.nextToken()    
        self.nextToken()    

    # -------------- Helper Methods -----------------
    
    # Check if the current token matches the given type.
    def checkToken(self, type):
        return type == self.currentToken.type

    # Check if the next token matches the given type.
    def checkPeek(self, type):
        return type == self.peekToken.type

    # Try to match the current token with the given type. If not, raise an error.
    # Advances the current token.
    def match(self, type):
        if not self.checkToken(type):
            message = f"Expected {type.name}, got {self.currentToken.type.name}"
            self.abort(message, lineNumber=self.line_number, type="(Parser) Syntax")
        self.nextToken()

    # Advance the current token and pull the next token from the lexer.
    def nextToken(self):
        self.currentToken = self.peekToken
        self.peekToken = self.lexer.getToken()
        if self.currentToken and self.currentToken.type == TokenType.NEWLINE:
            self.line_number += 1
    
    # ------------ Recursive Descent Parsing -----------------
    
    def program(self):
        statements = []
        while not self.checkToken(TokenType.EOF):
            statements.append(self.statement())
        return Program(statements, self.symbolTable)

    def statement(self):
        node = None
        try:
            # Handle blocks of code
            if self.checkToken(TokenType.LBRACE):
                node = self.block()
            
            # "print" ( <expression> | <string> ) <nl>
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
                        self.abort(f"Variable '{self.currentToken.value}' not declared.", lineNumber=self.line_number, type="(Parser) Syntax")
                    valueToPrint = VariableReference(self.currentToken.value)
                    self.nextToken()
                else:
                    self.abort(f"Invalid value to print: {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
                
                self.match(TokenType.RPAREN)
                node = Print(valueToPrint)
                
            # "if" <comparison> "{" { <statement> } "}" <nl>
            elif self.checkToken(TokenType.IF):
                self.match(TokenType.IF)
                self.match(TokenType.LPAREN)
                comparison_node = self.comparison()
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = If(comparison_node, block_node)  

            # "while" <comparison> "{" { <statement> } "}" <nl>
            elif self.checkToken(TokenType.WHILE):
                self.match(TokenType.WHILE)
                self.match(TokenType.LPAREN)
                comparison_node = self.comparison()
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = While(comparison_node, block_node)
                
            # "for" "(" <var_name> "=" <expression> ";" <comparison> ";" <var_name> (("++" | "--") | ("=" <expression>)) ")" "{" { <statement> } "}" <nl>
            elif self.checkToken(TokenType.FOR):
                self.match(TokenType.FOR)
                self.match(TokenType.LPAREN)
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                initialCount = self.expression()
                self.match(TokenType.SEMICOLON)
                comparison_node = self.comparison()
                self.match(TokenType.SEMICOLON)
                increment = None
                if self.checkToken(TokenType.VAR_NAME):
                    increment_var = self.currentToken.value
                    self.match(TokenType.VAR_NAME)
                    # ++ or --
                    if self.checkToken(TokenType.INCREMENT) or self.checkToken(TokenType.DECREMENT):
                        increment = self.currentToken.value
                        self.nextToken()
                    # to ensure increments of i = i+5 also work
                    elif self.checkToken(TokenType.EQ):
                        self.nextToken()
                        increment_expr = self.expression()
                        # semantic analyzer will ensure that the expression is actually an increment/decrement
                        increment = (increment_var, increment_expr)
                    else:
                        message = f"Expected increment:'{var_name}++', '{var_name}--', or '{var_name}={var_name} +/- integer', got {self.currentToken.type.name}"
                        self.abort(message, lineNumber=self.line_number, type="(Parser) Syntax")
                else:
                    message = f"Expected variable name in increment/decrement statement, got {self.currentToken.type.name}"
                    self.abort(message, lineNumber=self.line_number, type="(Parser) Syntax")
                self.match(TokenType.RPAREN)
                block_node = self.block()
                node = For(VariableDeclaration(var_name, initialCount), comparison_node, increment, block_node)
                
            # "set" <var_name> "=" <expression> <nl>
            elif self.checkToken(TokenType.SET):
                self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.match(TokenType.EQ)
                expression_node = self.expression()

                if not self.symbolTable.lookup(var_name):
                    node = VariableDeclaration(var_name, expression_node)
                    self.symbolTable.add(var_name, expression_node)  # Add variable to symbol table
                else:
                    self.abort(f"Variable '{var_name}' already declared. Please use 'Set'", lineNumber=self.line_number, type="(Parser) Syntax")

            # <var_name> "=" <expression> <nl>
            elif self.checkToken(TokenType.VAR_NAME) and self.checkPeek(TokenType.EQ):
                var_name = self.currentToken.value
                if not self.symbolTable.lookup(var_name):
                    self.abort(f"Variable '{var_name}' not declared. Please use 'Set'", lineNumber=self.line_number, type="(Parser) Syntax")
                
                self.nextToken()  # consume the variable name
                self.match(TokenType.EQ)
                expression_node = self.expression()
                node = VariableUpdated(var_name, expression_node)

            # "input" <var_name> <nl>
            elif self.checkToken(TokenType.INPUT):
                self.nextToken()
                var_name = self.currentToken.value
                self.match(TokenType.VAR_NAME)
                self.symbolTable.add(var_name, None)  # Add input variable to symbol table
                node = Input(VariableDeclaration(var_name,"null"))    # Create an input node with an empty VariableDeclaration
            else:
                self.abort(f"Invalid statement at: {self.currentToken.value} ({self.currentToken.type.name})", lineNumber=self.line_number, type="(Parser) Syntax")
        except Exception as e:
            self.errorRecovery()
        
        self.nl()
        return node

    def comparison(self):
        left = self.expression()
        if not self.isComparisonOperator():
            self.abort(f"Expected comparison operator, got {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
        
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
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTE

) or \
            self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTE) or \
            self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def expression(self):
        node = self.term()
        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            operator = self.currentToken.value
            self.nextToken()
            right = self.term()
            node = Expression(node, operator, right)
        return node

    def term(self):
        node = self.unary()
        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            operator = self.currentToken.value
            self.nextToken()
            right = self.unary()
            node = Term(node, operator, right)
        return node

    def unary(self):
        operator = None
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            operator = self.currentToken.value
            self.nextToken()
        
        node = self.primary()
        if operator:
            node = Unary(operator, node)
        return node

    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            node = Number(int(self.currentToken.value))
            self.nextToken()
        elif self.checkToken(TokenType.VAR_NAME):
            if not self.symbolTable.lookup(self.currentToken.value):
                self.abort(f"Variable '{self.currentToken.value}' not declared.", lineNumber=self.line_number, type="(Parser) Syntax")
            node = VariableReference(self.currentToken.value)
            self.nextToken()
        elif self.checkToken(TokenType.LPAREN):
            self.nextToken()
            node = self.expression()
            self.match(TokenType.RPAREN)
        else:
            self.abort(f"Unexpected token: {self.currentToken.value}", lineNumber=self.line_number, type="(Parser) Syntax")
        return node
    
    def block(self):
        self.match(TokenType.LBRACE)
        statements = []
        self.symbolTable.enter_scope()
        while not self.checkToken(TokenType.RBRACE):
            statements.append(self.statement())
        self.symbolTable.exit_scope()
        self.match(TokenType.RBRACE)
        return Block(statements)

    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def errorRecovery(self):
        while not self.checkToken(TokenType.NEWLINE):
            self.nextToken()
        self.nl()