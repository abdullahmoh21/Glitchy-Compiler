from Error import *
from Ast import *
import llvmlite.ir as ir
import llvmlite.binding as llvm

class LLVMCodeGenerator:
    def __init__(self, symbol_table):
        self.module = ir.Module(name="module")
        self.module.globals = {}
        self.builder = None
        self.function = None
        self.symbol_table = symbol_table
        self.string_counter = 0  
        self.declare_globals()

    def generate_code(self, node):
        if has_error_occurred():
            return None

        # Create the main function and its entry block
        func_type = ir.FunctionType(ir.VoidType(), [])
        self.function = ir.Function(self.module, func_type, name="main")
        block = self.function.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(block)

        # Generate code for the AST
        node.accept(self)

        if not self.builder.block.is_terminated:
            self.builder.ret_void()


        return self.module

    def declare_globals(self):
        format_strings = {
            "format_int": "%d\n\0",
            "format_float": "%f\n\0",
            "format_bool": "%d\n\0",
            "format_string": "%s\n\0"
        }

        for name, fmt in format_strings.items():
            c_format_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)), bytearray(fmt.encode("utf8")))
            format_global = ir.GlobalVariable(self.module, c_format_str.type, name=name)
            format_global.global_constant = True
            format_global.initializer = c_format_str
        
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
        self.symbol_table.enterScope()
        for statement in node.statements:
            statement.accept(self)
        self.symbol_table.exitScope()

    def visit_variable(self, node):
        if isinstance(node, VariableDeclaration):
            mangled_name = self.symbol_table.getMangledName(node.name)
            value = node.value.accept(self)
            var_type = value.type

            # Allocate space for the variable within the current function (likely main)
            local_var = self.builder.alloca(var_type, name=mangled_name)
            self.builder.store(value, local_var)
            self.symbol_table.setReference(node.name, local_var)

        elif isinstance(node, VariableUpdated):
            mangled_name = self.symbol_table.getMangledName(node.name)
            if mangled_name is None:
                raise Error("Could not retrieve mangled name from symbol table")
            value = node.value.accept(self)

            local_var = self.symbol_table.getReference(node.name)
            if local_var is None:
                raise Error(f"Variable '{node.name}' referenced before declaration or update")
            
            self.builder.store(value, local_var)

        elif isinstance(node, VariableReference):
            mangled_name = self.symbol_table.getMangledName(node.name)
            if mangled_name is None:  # If no mangled name, assume it's a function parameter
                mangled_name = node.name

            reference = self.symbol_table.getReference(node.name)
            if reference is None:
                raise Error(f"Variable '{node.name}' referenced before declaration")

            if isinstance(reference, ir.AllocaInstr):
                return self.builder.load(reference, name=mangled_name)
            else:
                # For function parameters
                return reference
            
    def visit_print(self, node):
        expr_value = node.value.accept(self)
        expr_type = node.value.evaluateType()
        
        if expr_type == 'integer':
            format_str_name= "format_int"
        elif expr_type == 'float':
            format_str_name = "format_float"
        elif expr_type == 'bool':
            format_str_name = "format_bool"
        elif expr_type == 'string':
            format_str_name = "format_string"
        else:
            raise Exception(f"Unsupported expression type: {expr_type}")

        # Get the global format string pointer
        fmt_ptr = self.builder.bitcast(self.module.get_global(format_str_name), ir.PointerType(ir.IntType(8)))

        # Retrieve the printf function
        printf = self.module.get_global('printf')

        # Handle different types for printf
        if expr_type in ['integer', 'bool', 'float']:
            # Print the value directly
            self.builder.call(printf, [fmt_ptr, expr_value])
        elif expr_type == 'string':
            expr_value = self.builder.bitcast(expr_value, ir.PointerType(ir.IntType(8)))
            self.builder.call(printf, [fmt_ptr, expr_value])
        else:
            raise Exception(f"Unsupported print type: {expr_type}")

    def visit_if(self, node):
        cond_val = node.comparison.accept(self)

        if_true_block = self.builder.append_basic_block(name="if_true_branch")
        if_false_block = self.builder.append_basic_block(name="if_false_branch")
        end_block = self.builder.append_basic_block(name="end")

        self.builder.cbranch(cond_val, if_true_block, if_false_block)

        # True Branch
        self.builder.position_at_end(if_true_block)
        node.block.accept(self)
        if not self.builder.block.is_terminated:
            self.builder.branch(end_block)

        # False Branch / Elif / Else Handling
        self.builder.position_at_end(if_false_block)

        if len(node.elifNodes) > 0:
            for i, elif_node in enumerate(node.elifNodes):
                elif_cond_val = elif_node[0].accept(self)

                elif_true_block = self.builder.append_basic_block(name=f"elif{i}_true_branch")
                elif_false_block = self.builder.append_basic_block(name=f"elif{i}_false_branch")

                self.builder.cbranch(elif_cond_val, elif_true_block, elif_false_block)

                self.builder.position_at_end(elif_true_block)
                elif_node[1].accept(self)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_block)

                self.builder.position_at_end(elif_false_block)

            # Handle the final `else` block if it exists
            if node.elseBlock is not None:
                node.elseBlock.accept(self)
                if not self.builder.block.is_terminated:
                    self.builder.branch(end_block)
            else:
                self.builder.branch(end_block)

        elif node.elseBlock is not None:
            # Directly handle the else block if there are no elifs
            node.elseBlock.accept(self)
            if not self.builder.block.is_terminated:
                self.builder.branch(end_block)
        else:
            self.builder.branch(end_block)

        # Final End Block
        self.builder.position_at_end(end_block)

    def visit_while(self, node):
        while_cond_block = self.builder.append_basic_block(name="while_cond")
        while_body_block = self.builder.append_basic_block(name="while_body")
        after_while_block = self.builder.append_basic_block(name="after_while")

        print(f"Before While Cond Block terminated: {self.builder.block.is_terminated}")

        self.builder.branch(while_cond_block)

        self.builder.position_at_end(while_cond_block)
        cond_val = node.comparison.accept(self)
        self.builder.cbranch(cond_val, while_body_block, after_while_block)
        print(f"While Cond Block terminated: {self.builder.block.is_terminated}")

        self.builder.position_at_end(while_body_block)
        node.block.accept(self)  # This will include 'if' statements
        
        if not self.builder.block.is_terminated:
            self.builder.branch(while_cond_block)  # Recheck the condition after each loop
        print(f"While Body Block terminated: {self.builder.block.is_terminated}")

        self.builder.position_at_end(after_while_block)
        print(f"After While Block terminated: {self.builder.block.is_terminated}")
        
    def visit_function_declaration(self, function):
        return_type = self.get_ir_type(function.return_type)
        param_types = [self.get_ir_type(param.type) for param in function.parameters]
        func_type = ir.FunctionType(return_type, param_types)
        
        func = ir.Function(self.module, func_type, name=function.name)
        entry_block = func.append_basic_block(name="entry")
        self.builder = ir.IRBuilder(entry_block)

        self.symbol_table.enterScope()

        for i, param in enumerate(function.parameters):
            param_value = func.args[i]
            param_value.name = param.name
            self.symbol_table.setReference(param.name, param_value)

        self.builder.position_at_end(entry_block)

        for statement in function.block.statements:
            if isinstance(statement, Return):
                return_value = statement.value.accept(self)

                if isinstance(return_value.type, ir.PointerType):
                    return_value = self.builder.load(return_value)

                if return_value.type != return_type:
                    raise TypeError(f"Return type mismatch: expected {return_type}, got {return_value.type}")
                if not self.builder.block.is_terminated:
                    self.builder.ret(return_value)
            else:
                statement.accept(self)
            
        self.symbol_table.exitScope()

        # reset builders pointer to main function 
        if 'main' in self.module.globals:
            main_func = self.module.get_global("main")
            main_block = main_func.entry_basic_block
            self.builder = ir.IRBuilder(main_block)

    def visit_return(self, node):
        return_value = node.value.accept(self)

        if isinstance(return_value.type, ir.PointerType):
            return_value = self.builder.load(return_value)

        if not self.builder.block.is_terminated:
            self.builder.ret(return_value)

    def visit_function_call(self, node):
        func = self.module.get_global(node.name)
        
        args = [arg.value.accept(self) for arg in node.arguments]
        
        call_result = self.builder.call(func, args)
        
        return_type_str = self.symbol_table.getFunctionType(node.name)
        
        return_type = self.get_ir_type(return_type_str)
        
        if return_type != ir.VoidType():
            return call_result
        else:
            return None
        
    def visit_input(self, node):
        # Declare the format string for scanf if it doesn't already exist
        format_str = "%s\0"
        format_str_name = "format_scanf"
        try:
            c_format_str_global = self.module.get_global(format_str_name)
        except KeyError:
            c_format_str = ir.Constant(ir.ArrayType(ir.IntType(8), len(format_str)), bytearray(format_str.encode("utf8")))
            c_format_str_global = ir.GlobalVariable(self.module, c_format_str.type, name=format_str_name)
            c_format_str_global.linkage = 'internal'
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
        self.symbol_table.setReference(node.varRef.name, alloca)

    def visit_binary_op(self, node):
        left = node.left.accept(self)       # Evaluate the left operand
        right = node.right.accept(self)     # Evaluate the right operand

        if node.operator == '+':
            result = self.builder.add(left, right)
        elif node.operator == '-':
            result = self.builder.sub(left, right)
        elif node.operator == '*':
            result = self.builder.mul(left, right)
        elif node.operator == '/':
            result = self.builder.sdiv(left, right)
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

        return result  

    def visit_unary_op(self, node):
        operand = node.left.accept(self)  

        if node.operator == '-':
            result = self.builder.neg(operand)
        elif node.operator == '+':
            result = operand
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

        return result  

    def visit_comparison(self, node):
        left = node.left.accept(self)  
        right = node.right.accept(self)  

        if node.operator == '==':
            result = self.builder.icmp_signed('==', left, right)
        elif node.operator == '!=':
            result = self.builder.icmp_signed('!=', left, right)
        elif node.operator == '<':
            result = self.builder.icmp_signed('<', left, right)
        elif node.operator == '<=':
            result = self.builder.icmp_signed('<=', left, right)
        elif node.operator == '>':
            result = self.builder.icmp_signed('>', left, right)
        elif node.operator == '>=':
            result = self.builder.icmp_signed('>=', left, right)
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

        return result 

    def visit_logical_op(self, node):
        left = node.left.accept(self)  
        right = node.right.accept(self)  

        if node.operator == '&&':
            result = self.builder.and_(left, right)
        elif node.operator == '||':
            result = self.builder.or_(left, right)
        else:
            raise ValueError(f"Unknown operator: {node.operator}")

        return result  
    
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
        return ir.Constant(ir.IntType(32), None)

    def get_ir_type(self, type_str):
        if type_str == 'integer':
            return ir.IntType(32)
        elif type_str == 'float':
            return ir.DoubleType()
        elif type_str == 'string':
            return ir.PointerType(ir.IntType(8))
        elif type_str == 'boolean':
            return ir.IntType(1)
        elif type_str == 'null':
            return ir.VoidType()
        else:
            raise ValueError(f"Unknown type: {type_str}")
