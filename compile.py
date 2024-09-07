import argparse
import os
import llvmlite.ir as ir
import llvmlite.binding as llvm
from utils import error
from Lexer import *
from Parser import *
from Analyzer import *
from Generator import *
from ctypes import CFUNCTYPE, c_void_p

COLORS = {
    'red': "\033[31m",
    'green': "\033[32m",
    'blue': "\033[34m",
    'reset': "\033[0m"
}


def compile_source(source_code, log_level):
    LOG_LEVELS = {
        0: "No Logging",
        1: "Minimal information",
        2: "Intermediate information",
        3: "Full information"
    }

    def log(message, level, color='reset'):
        if level <= log_level:
            print(f"{COLORS[color]}{message}{COLORS['reset']}")
    
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    if has_error_occurred():
        log("Parsing failed. Aborting compilation...", 0, 'red')
        return

    log("Parsing completed!", 1, 'green')
    if log_level >= 2:
        log("Initial AST generated:", 2, 'blue')
        ast.print_content()

    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if has_error_occurred() is False:
        log("Semantic analysis completed!", 1, 'green')
        if log_level >= 2:
            log("The following Symbol table was returned:", 2, 'blue')
            symbol_table.print_table()
        if log_level >= 3:
            log("The analyzer returned this AST:", 2, 'blue')
            ast.print_content()
    else:
        log("Semantic analysis failed. Aborting compilation...", 0, 'red')
        return

    llvmir_gen = LLVMCodeGenerator(symbol_table)
    llvm_ir = llvmir_gen.generate_code(ast)
    if llvm_ir is None:
        log("Error occurred during code generation. Aborting...", 0, 'red')
        return

    try:
        log("LLVM IR generated:", 1, 'blue')
        log("---------------------------------------", 1)
        log(str(llvm_ir), 1)
        log("---------------------------------------", 1)

        mod = llvm.parse_assembly(str(llvm_ir))
        mod.verify()
        log("LLVM IR verification succeeded!", 1, 'green')
    except Exception as e:
        log(f"LLVM verification failed: {e}", 0, 'red')
        return

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

    if log_level == 3:
        print(f"\n{COLORS['blue']}The following optimized LLVM IR code was generated:{COLORS['reset']}\n")
        print("---------------------------------------")
        print(str(mod))
        print("---------------------------------------")

    with llvm.create_mcjit_compiler(mod, target_machine) as engine:
        engine.finalize_object()
        engine.run_static_constructors()

        try:
            main_ptr = engine.get_function_address("main")
            if main_ptr:
                c_main = CFUNCTYPE(None)(main_ptr)
                c_main()
            else:
                log("Error: 'main' function not found.", 0, 'red')
        except Exception as e:
            log(f"Execution failed: {str(e)}", 0, 'red')

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

    compile_source(source_code, log_level=args.log)

if __name__ == "__main__":
    main()