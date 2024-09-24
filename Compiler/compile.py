import argparse
import os
import llvmlite.ir as ir
import llvmlite.binding as llvm
from utils import error
from Lexer import *
from Parser import *
from Analyzer import *
from Generator import *
from collections import deque
from ctypes import CFUNCTYPE, c_void_p

COLORS = {
    'red': "\033[31m",
    'green': "\033[32m",
    'blue': "\033[34m",
    'reset': "\033[0m"
}


def compile(source_code, log_level):
    LOG_LEVELS = {
        0: "No Logging",
        1: "Minimal information",
        2: "Intermediate information",
        3: "Full information"
    }

    log_queue = deque()

    def log(message, level, color='reset', immediate=False, action=None):
        if level <= log_level:
            if immediate:
                print(f"{COLORS[color]}{message}{COLORS['reset']}")
                if action:
                    action() 
            else:
                log_queue.append((message, color, action))  # Add callable action to queue

    # Lexer and parsing phase
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()

    if has_error_occurred():
        return 

    log("Parsing completed!", 1, 'green', immediate=True)
    log("Initial AST generated:", 2, 'blue', action=lambda: ast.print_content())  

    # Semantic analysis phase
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()

    if has_error_occurred():
        return  

    log("Semantic analysis completed!", 1, 'green', immediate=True)
    log("The following Symbol table was returned:", 2, 'blue', action=lambda: symbol_table.print_table())  
    log("The analyzer returned this AST:", 3, 'blue', action=lambda: ast.print_content())  

    # LLVM IR code generation phase
    llvmir_gen = LLVMCodeGenerator(symbol_table)
    llvm_ir = llvmir_gen.generate_code(ast)

    if has_error_occurred() or llvm_ir is None:
        return  

    try:
        log("LLVM IR generated:", 1, 'blue')
        log("---------------------------------------", 1)
        log(None, 1, action=lambda: print(str(llvm_ir)))  
        log("---------------------------------------", 1)

        mod = llvm.parse_assembly(str(llvm_ir))
        mod.verify()
    except Exception as e:
        log(f"An error occurred during the LLVM IR verification {e}", 0, 'red', immediate=True)

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = 3

    pass_manager = llvm.create_module_pass_manager()
    pmb.populate(pass_manager)
    pass_manager.run(mod)
    
    
    if not has_error_occurred():
        while log_queue:
            message, color, action = log_queue.popleft()
            if message:
                print(f"{COLORS[color]}{message}{COLORS['reset']}")
            if action:
                action()  # Call deferred action (e.g., print AST or LLVM IR)

    if not has_error_occurred():
        with llvm.create_mcjit_compiler(mod, target_machine) as engine:
            engine.finalize_object()
            engine.run_static_constructors()

            try:
                main_ptr = engine.get_function_address("main")
                if main_ptr:
                    c_main = CFUNCTYPE(None)(main_ptr)
                    c_main()
                else:
                    log("Error: 'main' function not found.", 0, 'red', immediate=True)
            except Exception as e:
                log(f"Execution failed: {str(e)}", 0, 'red', immediate=True)

    llvm.shutdown()


def main():
    parser = argparse.ArgumentParser(description='Compile a single .g file to executable.')
    parser.add_argument('file', metavar='FILE', type=str, help='source .g file to compile')
    parser.add_argument('--log', type=int, default=0, choices=[0, 1, 2, 3],
                        help='set the verbosity level (0:none 1: minimal, 2: intermediate, 3: full)')

    args = parser.parse_args()

    file_name = args.file

    if not file_name.endswith('.g'):
        print(f"Error: The file must have a .g extension. received: '{file_name}'")
        return

    if not os.path.exists(file_name):
        print(f"File not found: {file_name}")
        return

    with open(file_name, 'r') as file:
        source_code = file.read()

    compile(source_code, log_level=args.log)


if __name__ == "__main__":
    main()