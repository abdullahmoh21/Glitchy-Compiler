import sys
"""
This module defines all the exceptions that can be raised by the compiler.
"""

error_occurred = False

def report(message, type="Unknown", lineNumber=None):
    """
    Prints an error message to standard output without exiting the program. 
    Marks that code is erroneous so that further execution (after parser) can be stopped.

    Args:
        message (str): The error message to report.
        type (str): The type of error (e.g., Syntax, Lexer, etc.).
        lineNumber (int, optional): The line number where the error occurred.
    """
    global error_occurred
    error_occurred = True
    
    if lineNumber is not None:
        error_message = f"{type} Error at line {lineNumber}: {message}"
    else:
        error_message = f"{type} Error: {message}"
    print(error_message)  # Print the error message instead of exiting

def has_error_occurred():
    return error_occurred

def reset_error_flag():
    global error_occurred
    error_occurred = False

class Error(Exception):
    """Base class for all compiler-related errors."""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return f"Error: {self.message}"


class SyntaxError(Error):
    """Exception raised for syntax errors."""
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

    def __str__(self):
        return f"SyntaxError: {self.message} at line {self.line}"


class SemanticError(Error):
    """Exception raised for semantic errors."""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"


class LexerError(Error):
    """Exception raised for errors during tokenization."""
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line

    def __str__(self):
        return f"LexerError: {self.message} at line {self.line}"


class TypeError(Error):
    """Exception raised for type mismatches or illegal operations."""
    def __init__(self, message, type_info):
        super().__init__(message)
        self.type_info = type_info

    def __str__(self):
        return f"TypeError: {self.message}"


class UndefinedVariableError(Error):
    """Exception raised when a variable is used before it's defined."""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"UndefinedVariableError: {self.message}"


