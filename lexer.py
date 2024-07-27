from token import Token, TokenType
import sys

class Lexer:
    def __init__(self, source):
        self.source = source + '\n'  # Appends a newline to simplify lexing the last token
        self.currentChar = ''
        self.currentPos = -1  # pointer for current position in the source code
        self.nextChar()

    # Processes the next character
    def nextChar(self):
        self.currentPos += 1
        if self.currentPos >= len(self.source):  # EOF
            self.currentChar = '\0'
        else:
            self.currentChar = self.source[self.currentPos]

    # Returns the next token, without changing the position
    def peek(self):
        # if there is no next character
        if self.currentPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.currentPos + 1]

    # abort with an error message
    def abort(self, message):
        sys.exit("Lexing error. " + message)

    # skips whitespace characters until it finds a non-whitespace character (except newline)
    def skipWhitespace(self):
        while self.currentChar in [' ', '\t', '\r']:
            self.nextChar()

    # ignore comments
    def skipComment(self):
        if self.currentChar == '#':
            # skip till the end of the line
            while self.currentChar != '\n':
                self.nextChar()

    # returns the next token
    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        if self.currentChar == '+':
            token = Token(TokenType.PLUS, self.currentChar)
        elif self.currentChar == '-':
            token = Token(TokenType.MINUS, self.currentChar)
        elif self.currentChar == '*':
            token = Token(TokenType.ASTERISK, self.currentChar)
        elif self.currentChar == '/':
            token = Token(TokenType.SLASH, self.currentChar)
        elif self.currentChar == '=':
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.EQEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.EQ, self.currentChar)
        elif self.currentChar == '!':
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.NOTEQ, prevChar + self.currentChar)
            else:
                self.abort("Expected !=, got !" + self.peek())
        elif self.currentChar == '<':
            # check if symbol is <=
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.LTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.LT, self.currentChar)
        elif self.currentChar == '>':
            # check if symbol is >=
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.GTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.GT, self.currentChar)
        elif self.currentChar == '\"':
            # extract string
            self.nextChar()
            startPos = self.currentPos

            while self.currentChar != '\"':
                # We don't support escape characters in strings
                if self.currentChar in ['\\', '\n', '\t', '%']:
                    self.abort("Illegal character in string: " + self.currentChar)
                self.nextChar()

            string = self.source[startPos:self.currentPos] # Get the substring.
            token = Token(TokenType.STRING, string)
            self.nextChar()  # Move past the closing quote
            
        elif self.currentChar.isdigit():
            # extract number
            startPos = self.currentPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':      # is it a decimal?
                self.nextChar()
                if not self.peek().isdigit():   # A number must follow the '.' char
                    self.abort("Illegal character in number: " + self.peek())
                while self.peek().isdigit():
                    self.nextChar()
            numberString = self.source[startPos : self.currentPos + 1] # Get the substring.  
            token = Token(TokenType.NUMBER, numberString)
        elif self.currentChar.isalpha():
            #  either a keyword or an identifier
            startPos = self.currentPos
            while self.peek().isalnum():
                self.nextChar()
            # Check if the token is in the list of keywords.
            tokText = self.source[startPos : self.currentPos + 1] # Get the substring.
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None: # Identifier
                token = Token(TokenType.IDENT, tokText)
            else:   # Keyword
                token = Token(keyword, tokText)

        elif self.currentChar == '\n':
            token = Token(TokenType.NEWLINE, self.currentChar)
        elif self.currentChar == '\0':
            token = Token(TokenType.EOF, '')
        else:
            # Unknown token!
            self.abort("Unknown token: " + self.currentChar)

        self.nextChar()
        return token
