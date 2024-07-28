import sys
from lexer import *

class Parser:
    def __init__(self, lexer, emitter, print_tree):
        self.lexer = lexer
        self.emitter = emitter
        self.print_tree = print_tree  # Add print_tree to the constructor
        
        self.currentToken = None
        self.peekToken = None
        self.depth = 0  # Track the depth of the parse tree
        self.tree_prefix = ""  # Track the prefix for the tree structure
        
        self.symbols = set()    # Variables declared so far.
        self.labelsDeclared = set() # Labels declared so far.
        self.labelsGotoed = set() # Labels goto'ed so far.
        
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
            self.abort(f"Expected {type.name}, got {self.currentToken.type.name}")
        self.nextToken()

    # Advance the current token and pull the next token from the lexer.
    def nextToken(self):
        self.currentToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    # Print an error message and exit the program.
    def abort(self, message):
        sys.exit("Error: " + message)
    
    # Helper method to print messages with indentation based on the current depth.
    def print_with_indent(self, message, is_last):
        if self.print_tree:  # Print only if print_tree is True
            connector = "└── " if is_last else "├── "
            print(self.tree_prefix + connector + message)
            if not is_last:
                self.tree_prefix += "│   "
            else:
                self.tree_prefix += "    "
    
    # ------------ Recursive Descent Parsing -----------------
    
    # Parse one or more newline characters.
    def nl(self):
        self.match(TokenType.NEWLINE)
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()
    
    # Entry point of the parser. Parse the entire program.
    def program(self):
        self.print_with_indent("PROGRAM", False)
        self.depth += 1
        previous_prefix = self.tree_prefix
        
        # Emit the header of the C program
        self.emitter.headerLine("#include <stdio.h>")   # Include I/O library
        self.emitter.headerLine("int main(void){")

        # Skip initial newlines
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        # Parse all statements until the end of the file
        while not self.checkToken(TokenType.EOF):
            self.statement()
            self.tree_prefix = previous_prefix
            
        # After all code is emitted, Close the C function
        self.emitter.emitLine("return 0;")
        self.emitter.emitLine("}")
        
        for label in self.labelsGotoed:
            if label not in self.labelsDeclared:
                self.abort("Attempting to GOTO to undeclared label: " + label)

        self.depth -= 1

    # Parse a single statement.
    def statement(self):
        previous_prefix = self.tree_prefix
        
        # "PRINT" (expression | string)
        if self.checkToken(TokenType.PRINT):
            self.print_with_indent("STATEMENT-PRINT", True)
            self.depth += 1
            
            self.nextToken()

            if self.checkToken(TokenType.STRING):
                # Simple string, so print it.
                self.print_with_indent(f"STRING ({self.currentToken.value})", True)
                self.emitter.emitLine("printf(\"" + self.currentToken.value + "\\n\");")
                self.nextToken()

            else:
                # Expect an expression and print the result as a float.
                self.emitter.emit("printf(\"%" + ".2f\\n\", (float)(")
                self.expression(True)
                self.emitter.emitLine("));")

            self.depth -= 1

        # "IF" comparison "THEN" block "ENDIF"
        elif self.checkToken(TokenType.IF):
            self.print_with_indent("STATEMENT-IF", True)
            self.depth += 1
            
            self.nextToken()
            self.emitter.emit("if(")
            self.comparison(False)   

            self.match(TokenType.THEN)
            self.nl()
            self.emitter.emitLine("){")

            # Zero or more statements in the body.
            while not self.checkToken(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
            self.emitter.emitLine("}")

            self.depth -= 1

        # "WHILE" comparison "REPEAT" block "ENDWHILE"
        elif self.checkToken(TokenType.WHILE):
            self.print_with_indent("STATEMENT-WHILE", True)
            self.depth += 1
            
            self.nextToken()
            self.emitter.emit("while(")
            self.comparison(False)

            self.match(TokenType.REPEAT)
            self.nl()
            self.emitter.emitLine("){")

            # Zero or more statements in the loop body.
            while not self.checkToken(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
            self.emitter.emitLine("}")

            self.depth -= 1

        # "LABEL" ident
        elif self.checkToken(TokenType.LABEL):
            self.print_with_indent("STATEMENT-LABEL", True)
            self.depth += 1
            
            self.nextToken()

            # Make sure this label doesn't already exist.
            if self.currentToken.value in self.labelsDeclared:
                self.abort("Label already exists: " + self.currentToken.value)
            self.labelsDeclared.add(self.currentToken.value)

            self.print_with_indent(f"LABEL ({self.currentToken.value})", True)
            self.emitter.emitLine(self.currentToken.value + ":")
            self.match(TokenType.IDENT)

            self.depth -= 1

        # "GOTO" ident
        elif self.checkToken(TokenType.GOTO):
            self.print_with_indent("STATEMENT-GOTO", True)
            self.depth += 1
            
            self.nextToken()
            self.labelsGotoed.add(self.currentToken.value)
            self.print_with_indent(f"GOTO ({self.currentToken.value})", True)
            self.emitter.emitLine("goto " + self.currentToken.value + ";")
            self.match(TokenType.IDENT)
            
            self.depth -= 1
        
        # "LET" ident = expression
        elif self.checkToken(TokenType.LET):
            self.print_with_indent("STATEMENT-LET", True)
            self.depth += 1
            
            self.nextToken()

            # Check if ident exists in symbol table. If not, declare it.
            if self.currentToken.value not in self.symbols:
                self.symbols.add(self.currentToken.value)
                self.emitter.headerLine("float " + self.currentToken.value + ";")    # First declaration must be up top

            self.print_with_indent(f"IDENT ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value + " = ")
            self.match(TokenType.IDENT)
            self.print_with_indent(f"OPERATOR (=)", False)
            self.match(TokenType.EQ)
            
            self.expression(True)
            self.emitter.emitLine(";")
            
            self.depth -= 1
            
        # "INPUT" ident
        elif self.checkToken(TokenType.INPUT):
            self.print_with_indent("STATEMENT-INPUT", True)
            self.depth += 1
            
            self.nextToken()  # Consume INPUT
            
            # If variable doesn't already exist, declare it.
            if self.currentToken.value not in self.symbols:
                self.symbols.add(self.currentToken.value)
                self.emitter.headerLine("float " + self.currentToken.value + ";")

            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.emitter.emitLine("if(0 == scanf(\"%" + "f\", &" + self.currentToken.value + ")) {")
            self.emitter.emitLine(self.currentToken.value + " = 0;")
            self.emitter.emit("scanf(\"%")
            self.emitter.emitLine("*s\");")
            self.emitter.emitLine("}")
            self.print_with_indent(f"IDENT ({self.currentToken.value})", True)
            self.match(TokenType.IDENT)

            
            self.depth -= 1

        else:
            self.abort(f"Invalid statement at {self.currentToken.value} ({self.currentToken.type.name})")
        
        self.nl()  # Consume newline characters.
        self.tree_prefix = previous_prefix
        
    # comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def comparison(self, is_last):
        self.print_with_indent("COMPARISON", is_last)
        self.depth += 1
        previous_prefix = self.tree_prefix

        self.expression(False)
        
        # Must be at least one comparison operator and another expression.
        if self.isComparisonOperator():
            self.print_with_indent(f"OPERATOR ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value)
            self.nextToken()
            self.expression(True)

        # Continue parsing as long as there are comparison operators
        while self.isComparisonOperator():
            self.print_with_indent(f"OPERATOR ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value)  # Emit the operator
            self.nextToken()
            self.expression(True)

        self.tree_prefix = previous_prefix
        self.depth -= 1
     
    # Check if the current token is a comparison operator.
    def isComparisonOperator(self):
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    # Parse an expression.
    def expression(self, is_last):
        self.print_with_indent("EXPRESSION", is_last)
        self.depth += 1
        previous_prefix = self.tree_prefix

        self.term(False)

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.print_with_indent(f"OPERATOR ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value)  # Emit the operator
            self.nextToken()
            self.term(True)

        self.tree_prefix = previous_prefix
        self.depth -= 1
    
    # term ::= unary {( "/" | "*" ) unary}
    def term(self, is_last):
        self.print_with_indent("TERM", is_last)
        self.depth += 1
        previous_prefix = self.tree_prefix

        self.unary(False)

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.print_with_indent(f"OPERATOR ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value)  # Emit the operator
            self.nextToken()
            self.unary(True)

        self.tree_prefix = previous_prefix
        self.depth -= 1

    # unary ::= ["+" | "-"] primary
    def unary(self, is_last):
        self.print_with_indent("UNARY", is_last)
        self.depth += 1
        previous_prefix = self.tree_prefix

        # Support unary + or - operators
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.print_with_indent(f"OPERATOR ({self.currentToken.value})", False)
            self.emitter.emit(self.currentToken.value)
            self.nextToken()

        self.primary(True)

        self.tree_prefix = previous_prefix
        self.depth -= 1
    
    # primary ::= number | ident
    def primary(self, is_last):
        self.print_with_indent("PRIMARY", is_last)
        self.depth += 1
        previous_prefix = self.tree_prefix

        if self.checkToken(TokenType.NUMBER):
            self.print_with_indent(f"NUMBER ({self.currentToken.value})", True)
            self.emitter.emit(self.currentToken.value)
            self.nextToken()

        elif self.checkToken(TokenType.IDENT):
            self.print_with_indent(f"IDENT ({self.currentToken.value})", True)
            if self.currentToken.value not in self.symbols:
                self.abort("Referencing variable before assignment: " + self.currentToken.value)
            self.emitter.emit(self.currentToken.value)
            self.nextToken()

        else:
            self.abort(f"Unexpected token at {self.currentToken.value}")

        self.tree_prefix = previous_prefix
        self.depth -= 1