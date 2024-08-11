import llvmlite.ir as ir
import llvmlite.binding as llvm
from Error import *
from Ast import *

class LLVMCodeGenerator:
    def __init__(self, symbol_table):
        self.module = ir.Module(name="module")
        self.module.globals = {}
        self.builder = None
        self.function = None
        self.symbol_table = symbol_table
        self.string_counter = 0     # for unique string names

    def generate_code(self, node):
        if has_error_occurred():
            print("Error occurred during semantic analysis. Code generation aborted.")
            return
        
        # Create the main function and its entry block
        func_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, func_type, name="main")
        block = self.function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)
        
        self.declare_methods()

        # Generate code for the AST
        node.accept(self)
        
        # End the main function
        self.builder.ret_void()

        return self.module

    # optimizer will remove unused functions
    def declare_methods(self):
        # printf 
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        ir.Function(self.module, printf_ty, name="printf")
        
        # scanf
        scanf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        ir.Function(self.module, scanf_ty, name="scanf")

    def visit_program(self, node):
        for statement in node.statements:
            statement.accept(self)

    def visit_block(self, node):
        for statement in node.statements:
            statement.accept(self)

    def get_ir_type(self, type_str):
        if type_str == 'integer':
            return ir.IntType(32)
        elif type_str == 'float':
            return ir.FloatType()
        elif type_str == 'string':
            return ir.PointerType(ir.IntType(8))
        elif type_str == 'boolean':
            return ir.IntType(1)
        else:
            raise Exception(f"Unsupported type: {type_str}")

    def visit_variable(self, node):
        if isinstance(node, VariableDeclaration):
            # Allocate variable in the appropriate scope
            var_name = node.name
            var_type_str = node.type
            var_type = self.get_ir_type(var_type_str)
            
            if self.symbol_table.is_global(var_name):
                # Global variable
                initial_value = node.value.accept(self)
                alloca = ir.GlobalVariable(self.module, var_type, name=var_name)
                alloca.initializer = ir.Constant(var_type, initial_value.constant)
            else:
                # Local variable
                alloca = self.builder.alloca(var_type, name=var_name)
                self.builder.store(node.value.accept(self), alloca)
            
            var = self.symbol_table.lookup(var_name)
            self.symbol_table.set_allocation(var_name, alloca)
        
        elif isinstance(node, VariableUpdated):
            alloca = self.symbol_table.get_allocation(node.name)
            if alloca is None:
                raise ValueError(f"Variable '{node.name}' not declared.")
            value = node.value.accept(self)
            self.symbol_table.update(node.name, value)
            self.builder.store(value, alloca)

        elif isinstance(node, VariableReference):
            alloca = self.symbol_table.get_allocation(node.name)
            if alloca is None:
                raise ValueError(f"Variable '{node.name}' not declared.")
            return self.builder.load(alloca)

    # TODO: add expression printing like print(x + 1)
    def visit_print(self, node):
        expr_type = node.expression.type

        # Determine the name for the global format string based on the type
        if expr_type == 'integer':
            format_str_name = "format_int"
            format_str = "%d\n\0"
        elif expr_type == 'float':
            format_str_name = "format_float"
            format_str = "%f\n\0"
        elif expr_type == 'bool':
            format_str_name = "format_bool"
            format_str = "%d\n\0"  # booleans as integers
        elif expr_type == 'string':
            format_str_name = "format_str"
            format_str = "%s\n\0"
        elif expr_type == 'null':   # null is printed as a string
            format_str_name = "format_str"
            format_str = "%s\n\0"
        else:
            raise Exception(f"Unsupported expression type: {expr_type}")

        # Try to get the global format string
        try:
            c_format_str_global = self.module.get_global(format_str_name)
        except KeyError:
            # If it does not exist, create it
            c_format_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode("utf8")))
            c_format_str_global = ir.GlobalVariable(self.module, c_format_str.type, name=format_str_name)
            c_format_str_global.global_constant = True
            c_format_str_global.initializer = c_format_str

        fmt_ptr = self.builder.bitcast(c_format_str_global, ir.PointerType(ir.IntType(8)))

        # Get the value of the expression
        if isinstance(node.expression, VariableReference):
            alloca = self.symbol_table.get_allocation(node.expression.name)

            # Check if the allocation is of array type
            if isinstance(alloca.type.pointee, ir.ArrayType):
                # Do not load the entire array; instead, use the array pointer directly
                expr_val = alloca
            else:
                # Load the value from the alloca
                expr_val = self.builder.load(alloca)
            
            print(f"expr_val: {expr_val}")

            
        else:
            expr_val = node.expression.accept(self)

        # Retrieve the printf function
        printf = self.module.get_global('printf')

        # Handle different types
        if expr_type in ['integer', 'bool', 'float']:
            self.builder.call(printf, [fmt_ptr, expr_val])
        elif expr_type in ['string','null']:
            str_ptr = self.builder.bitcast(expr_val, ir.PointerType(ir.IntType(8)))
            self.builder.call(printf, [fmt_ptr, str_ptr])

    def visit_if(self, node):
        # Evaluate the condition of the if statement
        cond_val = node.comparison.accept(self)
        
        # Create blocks for the 'then', 'else', and end sections
        if_true_block = self.builder.append_basic_block(name="if_true_branch")
        if_false_block = self.builder.append_basic_block(name="if_false_branch")
        end_block = self.builder.append_basic_block(name="end")

        # Conditional branch based on the 'if' condition
        self.builder.cbranch(cond_val, if_true_block, if_false_block)

        # Emit code for the 'then' branch
        self.builder.position_at_end(if_true_block)
        node.block.accept(self)
        self.builder.branch(end_block)  # Ensure branching to the end block

        # Start handling the false condition (else or elif)
        self.builder.position_at_end(if_false_block)

        if node.elifNodes:
            # Iterate through each elif clause
            for elif_comparison, elif_block in node.elifNodes:
                # Create blocks for elif's true and false branches
                elif_true_branch = self.builder.append_basic_block(name="elif_true_branch")
                elif_false_branch = self.builder.append_basic_block(name="elif_false_branch")
                
                # Evaluate the elif condition and create a conditional branch
                elif_cond_val = elif_comparison.accept(self)
                self.builder.cbranch(elif_cond_val, elif_true_branch, elif_false_branch)

                # Emit code for the elif's true branch
                self.builder.position_at_end(elif_true_branch)
                elif_block.accept(self)
                self.builder.branch(end_block)  # Branch to the end block

                # Move to the elif's false branch
                self.builder.position_at_end(elif_false_branch)

            # After processing all elifs, handle the else block if it exists
            if node.elseBlock:
                else_block = self.builder.append_basic_block(name="else")
                self.builder.position_at_end(elif_false_branch)
                self.builder.branch(else_block)
                
                # Emit code for the else block
                self.builder.position_at_end(else_block)
                node.elseBlock.accept(self)
                self.builder.branch(end_block)  # Branch to the end block
            else: 
                # If there is no else block after elif, branch directly to the end block
                self.builder.branch(end_block)

        elif node.elseBlock:
            # Handle the else block if there are no elifs
            else_block = self.builder.append_basic_block(name="else")
            self.builder.position_at_end(if_false_block)
            self.builder.branch(else_block)
            
            # Emit code for the else block
            self.builder.position_at_end(else_block)
            node.elseBlock.accept(self)
            self.builder.branch(end_block)  # Branch to the end block

        else:
            # If no else or elif, just branch directly to the end block
            self.builder.branch(end_block)

        # Finalize the end block, ensuring all branches connect here
        self.builder.position_at_end(end_block) 
                 
    def visit_while(self, node):
        # Create basic blocks for the while loop and the block after the while loop
        while_cond_block = self.builder.append_basic_block(name="while_cond")
        while_body_block = self.builder.append_basic_block(name="while_body")
        after_while_block = self.builder.append_basic_block(name="after_while")
        
        # Branch to the while condition block
        self.builder.branch(while_cond_block)
        
        # Position the builder at the start of the while condition block
        self.builder.position_at_start(while_cond_block)
        
        # Evaluate the condition of the while loop
        cond_val = node.comparison.accept(self)
        
        # Create conditional branching based on the condition value
        self.builder.cbranch(cond_val, while_body_block, after_while_block)
        
        # Position the builder at the start of the while body block
        self.builder.position_at_start(while_body_block)
        
        # Generate code for the loop body
        node.block.accept(self)
        
        # Branch back to the while condition block
        self.builder.branch(while_cond_block)
        
        # Position the builder at the start of the block after the while loop
        self.builder.position_at_start(after_while_block)

    def visit_function_declaration(self,node):
        pass
    
    def visit_function_call(self,node):
        pass

    def visit_input(self, node):
        # Declare the format string for scanf if it doesn't already exist
        format_str = "%s\0"
        format_str_name = "format_scanf"
        try:
            c_format_str_global = self.module.get_global(format_str_name)
        except KeyError:
            # If it does not exist, create it
            c_format_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode("utf8")))
            c_format_str_global = ir.GlobalVariable(self.module, c_format_str.type, name=format_str_name)
            c_format_str_global.global_constant = True
            c_format_str_global.initializer = c_format_str

        fmt_ptr = self.builder.bitcast(c_format_str_global, ir.PointerType(ir.IntType(8)))

        # Allocate space for the input string on the stack
        alloca = self.builder.alloca(ir.ArrayType(ir.IntType(8), 256), name=node.varRef.name)  # 256-byte buffer
        str_ptr = self.builder.bitcast(alloca, ir.PointerType(ir.IntType(8)))

        # Get the scanf function
        scanf = self.module.get_global('scanf')

        # Call scanf with the format string and the allocated space
        self.builder.call(scanf, [fmt_ptr, str_ptr])

        # Store the pointer to the input string in the variable's allocation
        self.symbol_table.set_allocation(node.varRef.name, alloca)

    def visit_binary_op(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.operator == '+':
            return self.builder.add(left, right)
        elif node.operator == '-':
            return self.builder.sub(left, right)
        elif node.operator == '*':
            return self.builder.mul(left, right)
        elif node.operator == '/':
            return self.builder.sdiv(left, right)

    def visit_unary_op(self, node):
        operand = node.left.accept(self)
        if node.operator == '-':
            return self.builder.neg(operand)
        elif node.operator == '+':
            return operand

    def visit_comparison(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.operator == '==':
            return self.builder.icmp_signed('==', left, right)
        elif node.operator == '!=':
            return self.builder.icmp_signed('!=', left, right)
        elif node.operator == '<':
            return self.builder.icmp_signed('<', left, right)
        elif node.operator == '<=':
            return self.builder.icmp_signed('<=', left, right)
        elif node.operator == '>':
            return self.builder.icmp_signed('>', left, right)
        elif node.operator == '>=':
            return self.builder.icmp_signed('>=', left, right)

    def visit_logical_op(self, node):
        left = node.left.accept(self)
        right = node.right.accept(self)
        if node.operator == '&&':
            return self.builder.and_(left, right)
        elif node.operator == '||':
            return self.builder.or_(left, right)

    def visit_integer(self, node):
        return ir.Constant(ir.IntType(32), node.value)

    def visit_float(self, node):
        return ir.Constant(ir.FloatType(), node.value)

    def visit_boolean(self, node):
        return ir.Constant(ir.IntType(1), node.value)

    def visit_string(self, node):
            str_val = bytearray(node.value.encode("utf8")) + b"\0"
            str_constant = ir.Constant(ir.ArrayType(ir.IntType(8), len(str_val)), str_val)

            # Generate a unique name using the counter
            unique_name = f"str_{self.string_counter}"
            self.string_counter += 1

            str_var = ir.GlobalVariable(self.module, str_constant.type, name=unique_name)
            str_var.global_constant = True
            str_var.initializer = str_constant

            return self.builder.bitcast(str_var, ir.PointerType(ir.IntType(8)))

    def visit_null(self, node):
        return ir.Constant(ir.IntType(32), 0)
