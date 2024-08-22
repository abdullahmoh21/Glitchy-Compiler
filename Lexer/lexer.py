import sys
from .TokenTable import Token, TokenType
from Error import report

class Lexer:
    def __init__(self, source): 
        self.source = source + "\n"  # Appends a newline to simplify lexing the last token
        
        self.lineNumber= 1     # Current line in the source code
        self.lastToken = None
        self.currentChar = ''
        self.currentPos = -1    # Pointer for current position in the source code
        self.nextChar()
        self.lineStart = 0

    def nextChar(self):
        self.currentPos += 1
        if self.currentPos >= len(self.source):  # EOF
            self.currentChar = '\0'
        else:
            self.currentChar = self.source[self.currentPos]
            
            if self.currentChar == '\n':
                self.lineNumber += 1
                self.lineStart = self.currentPos + 1

    def peek(self):
        if self.currentPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.currentPos + 1]

    def skipWhitespace(self):
        while self.currentChar in [' ', '\t', '\r']:
            self.nextChar()

    def skipComment(self):
        if self.currentChar == '/' and self.peek() == '/':
            while self.currentChar != '\n' and self.currentChar != '\0':
                self.nextChar()

    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None
        # ---------------- ARITHMETIC OPERATORS ----------------
        if self.currentChar == '+':
            #  ++ or +
            if self.peek() == '+':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.INCREMENT, prevChar + self.currentChar)
            elif self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.PLUS_EQUAL, prevChar + self.currentChar)
            else:
                token = Token(TokenType.PLUS, self.currentChar)
            
        elif self.currentChar == '-':
            # -- or -
            if self.peek() == '-':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.DECREMENT, prevChar + self.currentChar)
            elif self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.MINUS_EQUAL, prevChar + self.currentChar)
            else:
                token = Token(TokenType.MINUS, self.currentChar)
            
        elif self.currentChar == '*':
            token = Token(TokenType.ASTERISK, self.currentChar)
            
        elif self.currentChar == '/': 
            token = Token(TokenType.SLASH, self.currentChar)
            
        elif self.currentChar == '%': 
            token = Token(TokenType.MODUlO, self.currentChar)
            
        elif self.currentChar == '^': 
            token = Token(TokenType.POW, self.currentChar)
        
        # ---------------- LOGICAL OPERATORS ----------------
        elif self.currentChar == '=':   
            #  == or = 
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.EQEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.EQ, self.currentChar)
                
        elif self.currentChar == '!':
            # != or !
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.NOTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.NOT, self.currentChar)
                
        elif self.currentChar == '<':
            # <= or <
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.LTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.LT, self.currentChar)
                
        elif self.currentChar == '>':
            # >= or >
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.GTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.GT, self.currentChar)
                
        elif self.currentChar == '&':  
            #  && or & (error)?
            if self.peek() == '&':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.AND, prevChar + self.currentChar)  # Add an AND token type
            else:
                report("Expected &&, got &", lineNumber=self.lineNumber)

        elif self.currentChar == '|':
            # || or | (error)?
            if self.peek() == '|':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.OR, prevChar + self.currentChar)  # Add an OR token type
            else:
                report("Expected ||, got |", line=self.lineNumber)

        # ---------------- DATA TYPES ----------------
        
        # STRINGS
        elif self.currentChar == '\"':
            self.nextChar()
            startLine = self.lineNumber
            startPos = self.currentPos

            while self.currentChar != '\"' and self.currentChar != '\n':
                if self.currentChar in ['\\', '\t','\r']:
                    message = f"(Lexer) Illegal character in string: {repr(self.currentChar)}"  # repr to display \n as well
                    report(message, type="Syntax", lineNumber=startLine)
                self.nextChar()

            if self.currentChar == '\n':
                message = "(Lexer) Unterminated string literal"
                report(message, type="Syntax", lineNumber=startLine)
                token = Token(TokenType.ERROR, None) 
            else:
                # Create token for the string
                string = self.source[startPos:self.currentPos]
                token = Token(TokenType.STRING, string)
        
        # INTEGERS AND FLOATS  
        elif self.currentChar.isdigit():
            # parse number
            startPos = self.currentPos
            is_float = False
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                self.nextChar()
                is_float = True
                if not self.peek().isdigit():
                    message = f"(Lexer) Illegal character in number: {self.peek()}"
                    report(message, type="Syntax", lineNumber=self.lineNumber)
                while self.peek().isdigit():
                    self.nextChar()
            # Extract the number as a string
            number_str = self.source[startPos:self.currentPos + 1]
            if is_float:
                try:
                    is_float = False
                    # Convert to float
                    number = float(number_str)
                except ValueError:
                    # Handle conversion error
                    message = f"(Lexer) Invalid float format: {number_str}"
                    report(message, type="Syntax", lineNumber=self.lineNumber)
                token = Token(TokenType.FLOAT, number)
            else:
                try:
                    # Convert to integer
                    number = int(number_str)
                except ValueError:
                    # Handle conversion error
                    message = f"(Lexer) Invalid integer format: {number_str}"
                    report(message, type="Syntax", lineNumber=self.lineNumber)
                token = Token(TokenType.INTEGER, number)

        # ---------------- ALPHA-NUM ----------------
        
        elif self.currentChar.isalpha() or self.currentChar == '_':
            # Start of a variable name, keyword or boolean
            startPos = self.currentPos
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()

            tokText = self.source[startPos : self.currentPos + 1]
            
            if '$' in tokText:
                report("Invalid Token '$' in identifier", type="Syntax", line=startLine)

            # Check for boolean literals
            if tokText == "true" or tokText == "false":
                token = Token(TokenType.BOOLEAN, tokText)
            # Check for null literal
            elif tokText == "null":
                token = Token(TokenType.NULL, tokText)
            else:
                # Check if the token is a keyword
                keyword = Token.checkIfKeyword(tokText)
                if keyword is None:
                    token = Token(TokenType.IDENTIFIER, tokText)
                else:
                    token = Token(keyword, tokText)
                    
        # ---------------- PUNCTUATION ----------------
        
        elif self.currentChar == '{':
            token = Token(TokenType.LBRACE, self.currentChar)   
        elif self.currentChar == '}':
            token = Token(TokenType.RBRACE, self.currentChar)
        elif self.currentChar == '(':
            token = Token(TokenType.LPAREN, self.currentChar)
        elif self.currentChar == ')':
            token = Token(TokenType.RPAREN, self.currentChar)
        elif self.currentChar == ';':
            token = Token(TokenType.SEMICOLON, self.currentChar)
        elif self.currentChar == '.':
            token = Token(TokenType.DOT, self.currentChar)
        elif self.currentChar == ',':
            token = Token(TokenType.COMMA, self.currentChar)
        elif self.currentChar == ':':
            token = Token(TokenType.COLON, self.currentChar)
        elif self.currentChar == '?':
            token = Token(TokenType.QMARK, self.currentChar)
        
        elif self.currentChar == '\n':
            token = Token(TokenType.NEWLINE, '\n')   
        elif self.currentChar == '\0':
            token = Token(TokenType.EOF, '')
            
        else:
            message= f"(Lexer) Unknown token: {self.currentChar}"
            report(message, type="Syntax",line= self.lineNumber)
            
        self.lastToken = token
        self.nextChar()
        return token
