import sys
from Compiler.utils import *

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
        while self.currentChar in [' ']:
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
            stringValue = ""

            allowed_escapes = ['n', 't',  r"/", '"', 'r', 'f', 'v', 'a', 'b']

            while self.currentChar != '\"':
                if self.currentChar.startswith('\\'): 
                    self.nextChar()
                    escape_char = self.currentChar
                    if escape_char in allowed_escapes:
                        stringValue += r"/" + self.currentChar
                    else:
                        report(f"Unknown escape sequence '\\{self.currentChar}'", type_="Syntax", line=self.lineNumber)
                        token = Token(TokenType.ERROR, None)
                else:
                    stringValue += self.currentChar  
                    
                self.nextChar()

                if self.currentChar == '\0':
                    report("Unterminated string found.", type_="Syntax", line=self.lineNumber)
                    token = Token(TokenType.ERROR, None)
                    break
            
            token = Token(TokenType.STRING, stringValue)
        
        # INTEGERS AND DOUBLES  
        elif self.currentChar.isdigit():
            # parse number
            startPos = self.currentPos
            is_double = False
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                self.nextChar()
                is_double = True
                if not self.peek().isdigit():
                    message = f"Illegal character in number: {self.peek()}"
                    report(message, type_="Syntax", line=self.lineNumber)
                while self.peek().isdigit():
                    self.nextChar()
            # Extract the number as a string
            number_str = self.source[startPos:self.currentPos + 1]
            if is_double:
                try:
                    is_double = False
                    # Convert to double
                    number = float(number_str)
                except ValueError:
                    # Handle conversion error
                    message = f"Invalid double format: {number_str}"
                    report(message, type_="Syntax", line=self.lineNumber)
                token = Token(TokenType.DOUBLE, number)
            else:
                try:
                    # Convert to integer
                    number = int(number_str)
                except ValueError:
                    # Handle conversion error
                    message = f"Invalid integer format: {number_str}"
                    report(message, type_="Syntax", lineNumber=self.lineNumber)
                token = Token(TokenType.INTEGER, number)

        # ---------------- ALPHA-NUM ----------------
        
        elif self.currentChar.isalpha() or self.currentChar == '_':
            # Start of a variable name, keyword or boolean
            startPos = self.currentPos
            while self.peek().isalnum() or self.peek() == '_':
                self.nextChar()

            tokText = self.source[startPos : self.currentPos + 1]
            
            if '$' in tokText:
                report("Invalid Token '$' in identifier", type_="Syntax", line=startLine)

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
            if self.peek().isdigit():
                startPos = self.currentPos
                self.nextChar()  # consume '.'
                while self.peek().isdigit():
                    self.nextChar()
                number_str = self.source[startPos:self.currentPos+1]  # slice up to currentPos
                try:
                    number = float(number_str)
                except ValueError:
                    number = 0.0 
                    message = f"Invalid double format: {number_str}"
                    report(message, type_="Syntax", line=self.lineNumber)  # report() will stop further stages. 
                token = Token(TokenType.DOUBLE, number)
            else:
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
            message= f"Invalid Character: '{self.currentChar}'"
            report(message, type_="Syntax",line= self.lineNumber)
            
        self.lastToken = token
        self.nextChar()
        return token
