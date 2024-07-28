import sys
from token import Token, TokenType

class Lexer:
    def __init__(self, source):
        self.source = source + "\n"  # Appends a newline to simplify lexing the last token
        self.currentChar = ''
        self.currentPos = -1  # Pointer for current position in the source code
        self.nextChar()

    def nextChar(self):
        self.currentPos += 1
        if self.currentPos >= len(self.source):  # EOF
            self.currentChar = '\0'
        else:
            self.currentChar = self.source[self.currentPos]

    def peek(self):
        if self.currentPos + 1 >= len(self.source):
            return '\0'
        return self.source[self.currentPos + 1]

    def abort(self, message):
        sys.exit("Lexing error. " + message)

    def skipWhitespace(self):
        while self.currentChar in [' ', '\t', '\r']:
            self.nextChar()

    def skipComment(self):
        if self.currentChar == '#':
            while self.currentChar != '\n' and self.currentChar != '\0':
                self.nextChar()

    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None
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
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.LTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.LT, self.currentChar)
        elif self.currentChar == '>':
            if self.peek() == '=':
                prevChar = self.currentChar
                self.nextChar()
                token = Token(TokenType.GTEQ, prevChar + self.currentChar)
            else:
                token = Token(TokenType.GT, self.currentChar)
        elif self.currentChar == '\"':
            self.nextChar()
            startPos = self.currentPos
            while self.currentChar != '\"':
                if self.currentChar in ['\\', '\n', '\t', '%']:
                    self.abort("Illegal character in string: " + self.currentChar)
                self.nextChar()
            string = self.source[startPos:self.currentPos] 
            token = Token(TokenType.STRING, string)
        elif self.currentChar.isdigit():
            startPos = self.currentPos
            while self.peek().isdigit():
                self.nextChar()
            if self.peek() == '.':
                self.nextChar()
                if not self.peek().isdigit():
                    self.abort("Illegal character in number: " + self.peek())
                while self.peek().isdigit():
                    self.nextChar()
            numberString = self.source[startPos : self.currentPos + 1] 
            token = Token(TokenType.NUMBER, numberString)
        elif self.currentChar.isalpha():
            startPos = self.currentPos
            while self.peek().isalnum():
                self.nextChar()
            tokText = self.source[startPos : self.currentPos + 1] 
            keyword = Token.checkIfKeyword(tokText)
            if keyword == None:
                token = Token(TokenType.IDENT, tokText)
            else:
                token = Token(keyword, tokText)
        elif self.currentChar == '\n':
            token = Token(TokenType.NEWLINE,'\n')
        elif self.currentChar == '\0':
            token = Token(TokenType.EOF, '')
        else:
            self.abort("Unknown token: " + self.currentChar)
        self.nextChar()
        return token