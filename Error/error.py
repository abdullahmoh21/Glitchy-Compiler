import sys
"""
This module defines custom exceptions that can be raised by the compiler. I dont want user to know i use py :)
"""

error_occurred = False

def report(message, type="Unknown", lineNumber=None, line=None):
    """
    Prints an error message to standard output without exiting the program. 
    Marks that code is erroneous so that further execution (after parser) can be stopped.

    Args:
        message (str): The error message to report.
        type (str): The type of error (e.g., Syntax, Lexer, etc.).
        lineNumber (int, optional): The line number where the error occurred.
        line (str, optional): The actual line of code where the error occurred.
    """
    
    global error_occurred
    error_occurred = True
    error_message = f"{type} Error: {message}"
    if lineNumber is not None:
        error_message += f" at line {lineNumber}:"
    if line is not None:
        error_message += f"\n{line}"
    print(error_message)  # Print the error message instead of exiting

def has_error_occurred():
    return error_occurred

def reset_error_flag():
    global error_occurred
    error_occurred = False

class CompilerError(Exception):
    """Base class for all compiler-related errors."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"CompilerError: {self.message}"


class SyntaxError(CompilerError):
    """Exception raised for syntax errors."""
    def __init__(self, message, line, column):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self):
        return f"SyntaxError at line {self.line}, column {self.column}: {self.message}"


class SemanticError(CompilerError):
    """Exception raised for semantic errors."""
    def __init__(self, message, context):
        super().__init__(message)
        self.context = context

    def __str__(self):
        return f"SemanticError in context '{self.context}': {self.message}"


class LexerError(CompilerError):
    """Exception raised for errors during tokenization."""
    def __init__(self, message, line, column):
        super().__init__(message)
        self.line = line
        self.column = column

    def __str__(self):
        return f"LexerError at line {self.line}, column {self.column}: {self.message}"


class TypeError(CompilerError):
    """Exception raised for type mismatches or illegal operations."""
    def __init__(self, message, type_info):
        super().__init__(message)
        self.type_info = type_info

    def __str__(self):
        return f"TypeError with type info '{self.type_info}': {self.message}"


class UndefinedVariableError(CompilerError):
    """Exception raised when a variable is used before it's defined."""
    def __init__(self, message, variable_name):
        super().__init__(message)
        self.variable_name = variable_name

    def __str__(self):
        return f"UndefinedVariableError for variable '{self.variable_name}': {self.message}"


