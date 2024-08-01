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
    
    def visit_variable_declaration(self, var_decl):
        raise NotImplementedError("visit_variable_declaration must be implemented")
    
    def visit_variable_reference(self, var_ref):
        raise NotImplementedError("visit_variable_reference must be implemented")
    
    def visit_variable_updated(self, var_updated):
        raise NotImplementedError("visit_variable_updated must be implemented")
    
    def visit_print(self, print_stmt):
        raise NotImplementedError("visit_print must be implemented")
    
    def visit_if(self, if_stmt):
        raise NotImplementedError("visit_if must be implemented")
    
    def visit_while(self, while_stmt):
        raise NotImplementedError("visit_while must be implemented")
    
    def visit_for(self, for_stmt):
        raise NotImplementedError("visit_for must be implemented")
    
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
    
    def visit_primary(self, primary):
        raise NotImplementedError("visit_primary must be implemented")
    
    def visit_number(self, number):
        raise NotImplementedError("visit_number must be implemented")
    
    def visit_boolean(self, boolean):
        raise NotImplementedError("visit_boolean must be implemented")
    
    def visit_string(self, string):
        raise NotImplementedError("visit_string must be implemented")
    
    def visit_null(self, null):
        raise NotImplementedError("visit_null must be implemented")
