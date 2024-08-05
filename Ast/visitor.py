"""
This module defines the ASTVisitor class, which is the base class for all AST visitors.
Each method of the ASTVisitor class corresponds to a different AST node type. We then subclass ASTVisitor in different 
stages of the compiler (analyzing,optimizing,generation) to implement the desired behavior for each node type.
"""

class ASTVisitor:
    def visit_program(self, program):
        raise NotImplementedError("visit_program must be implemented")
    
    def visit_block(self, block):
        raise NotImplementedError("visit_block must be implemented")
    
    def visit_variable(self, var_decl):
        raise NotImplementedError("visit_variable must be implemented")
    
    def visit_print(self, print_stmt):
        raise NotImplementedError("visit_print must be implemented")
    
    def visit_if(self, if_stmt):
        raise NotImplementedError("visit_if must be implemented")
    
    def visit_while(self, while_stmt):
        raise NotImplementedError("visit_while must be implemented")
    
    def visit_input(self, input_stmt):
        raise NotImplementedError("visit_input must be implemented")
    
    def visit_comparison(self, comparison):
        raise NotImplementedError("visit_comparison must be implemented")
    
    def visit_expression(self, expression):
        raise NotImplementedError("visit_expression must be implemented")
    
    def visit_binary_op(self, binary_op):
        raise NotImplementedError("visit_binary_op must be implemented")
    
    def visit_unary_op(self, unary_op):
        raise NotImplementedError("visit_unary_op must be implemented")
    