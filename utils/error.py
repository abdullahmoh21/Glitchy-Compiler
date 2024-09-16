import sys
from .ast import *

"""
This module defines all the exceptions that can be raised by the compiler.
"""

error_occurred = False
red = "\033[31m"
reset = "\033[0m"

def throw(exception, exit=True, line=None):
    """
    Raises an exception and handles it by printing only the error message without a stack trace.
    This hides python from the user. We can also raise an Exit exception that exits the current stage of compilation
    
    Args:
        exception (Error): The exception instance to raise and handle.
    """
    global error_occurred
    error_occurred = True
    try:
        raise exception
    except Error as e:
        _ = f" on line {line}" if line is not None else ""
        ty = f"{type(e).__name__}{ _ }:"
        msg = str(e).split(":", 1)[-1].strip()
        
        print(f"{red}{ty}{reset} {msg}")
        if exit:
            raise ExitSignal()

def report(message, type_="Complier",error=True, line=None):
    """
    Prints an error message to standard output without exiting the program. 
    Marks that code is erroneous so that further execution (after parser) can be stopped.

    Args:
        message (str): The error message to report.
        type (str): The type of error (e.g., Syntax, Lexer, etc.).
        line (int, optional): The line number where the error occurred.
    """
    if error:
        global error_occurred
        error_occurred = True
    
    if line is not None:
        if type_ =='Warning':
            error_message = f"{red}Warning at line {line}: {reset}{message}"
        else:   
            error_message = f"{red}{type_} Error at line {line}: {reset}{message}"
    else:
        if type_ =='Warning':
            error_message = f"{red}Warning: {reset}{message}"
        else:
            error_message = f"{red}{type_} Error: {reset}{message}"
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
        return f"{self.message}"

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
class ParsingError(Error):
    """Exception raised for parsing errors."""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"

class ExitSignal(Error):
    """Exception raised to exit a compilation stage"""
    def __init__(self):
        super().__init__(None)
        
    def __str__(self):
        return "Exit Exception"

class TypeError(Error):
    """Exception raised for type mismatches or illegal operations."""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"TypeError: {self.message}"
class ReturnError(Error):
    """Exception raised for Return errors."""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"ReturnError: {self.message}"

class ArgumentError(Error):
    """Exception raised for function and method arguments"""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"ArgumentError: {self.message}"

class ReferenceError(Error):
    """Exception raised for incorrect references"""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"ReferenceError: {self.message}"

class CompilationError(Error):
    """Exception raised for all generator errors"""
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"

