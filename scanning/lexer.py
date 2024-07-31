import sys
from .tokenClass import Token, TokenType

class Lexer:
    def __init__(self, source, abortFunction): 
        self.source = source + "\n"  # Appends a newline to simplify lexing the last token
        self.abort = abortFunction
        
        self.lineNumber = 1     # Current line in the source code
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
            else:
                token = Token(TokenType.PLUS, self.currentChar)
            
        elif self.currentChar == '-':
            # -- or -
            if self.peek() == '-':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.DECREMENT, prevChar + self.currentChar)
            else:
                token = Token(TokenType.MINUS, self.currentChar)
            
        elif self.currentChar == '*':
            token = Token(TokenType.ASTERISK, self.currentChar)
            
        elif self.currentChar == '/': 
            token = Token(TokenType.SLASH, self.currentChar)
        
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
                self.abort("Expected &&, got &", lineNumber=self.lineNumber, line=self.source[self.lineStart:self.currentPos + 1])

        elif self.currentChar == '|':
            # || or | (error)?
            if self.peek() == '|':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.OR, prevChar + self.currentChar)  # Add an OR token type
            else:
                self.abort("Expected ||, got |", lineNumber =self.lineNumber, line=self.source[self.lineStart:self.currentPos + 1])

        # ---------------- DATA TYPES ----------------
        elif self.currentChar == '\"':
            # parse string
            self.nextChar()
            startPos = self.currentPos
            while self.currentChar != '\"' and self.currentChar != '\0':
                if self.currentChar in ['\\', '\n', '\t']:
                    message= f"(Lexer) Illegal character in string: {repr(self.currentChar)}"   #repr to display \n as well
                    self.abort(message, type="Syntax", lineNumber=self.lineNumber,line= self.source[self.lineStart:self.currentPos + 1])
                self.nextChar()
            if self.currentChar == '\0':
                self.abort("Unterminated string", type="Syntax", lineNumber=self.lineNumber, line=self.source[self.lineStart:self.currentPos + 1])
            string = self.source[startPos:self.currentPos] 
            token = Token(TokenType.STRING, string)
            
        elif self.currentChar.isdigit():
            # parse number
            startPos = self.currentPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                self.nextChar()
                if not self.peek().isdigit():
                    message = f"(Lexer) Illegal character in number: {self.peek()}"
                    self.abort(message, type="Syntax", lineNumber=self.lineNumber, line=self.source[self.lineStart:self.currentPos + 1])
                while self.peek().isdigit():
                    self.nextChar()
            # Extract the number as a string and convert to float
            number_str = self.source[startPos:self.currentPos + 1]
            try:
                # Convert to float if it contains a decimal point
                number = float(number_str)
            except ValueError:
                # Handle conversion error
                message = f"(Lexer) Invalid number format: {number_str}"
                self.abort(message, type="Syntax", lineNumber=self.lineNumber, line=self.source[self.lineStart:self.currentPos + 1])
            token = Token(TokenType.NUMBER, number)
        # ---------------- ALPHA-NUM ----------------
        elif self.currentChar.isalpha() or self.currentChar == '_':
            # Start of a variable name, keyword or boolean
            startPos = self.currentPos
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()
            
            tokText = self.source[startPos : self.currentPos + 1]

            # Check for boolean literals
            if tokText == "true" or tokText == "false":
                token = Token(TokenType.BOOLEAN, tokText)
            else:
                # Check if the token is a keyword
                keyword = Token.checkIfKeyword(tokText)
                if keyword is None:
                    token = Token(TokenType.VAR_NAME, tokText)
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
            
        elif self.currentChar == '\n':
            if self.lastToken and self.lastToken.type != TokenType.NEWLINE:
                token = Token(TokenType.NEWLINE, '\n')
            else:
                self.nextChar()
                return self.getToken()

            
        elif self.currentChar == '\0':
            token = Token(TokenType.EOF, '')
            
        else:
            message= f"(Lexer) Unknown token: {self.currentChar}"
            self.abort(message, type="Syntax",lineNumber = self.lineNumber, line = self.source[self.lineStart:self.currentPos + 1])
            
        self.lastToken = token
        self.nextChar()
        return token
