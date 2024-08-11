import os
import llvmlite.ir as ir
import llvmlite.binding as llvm
from Lexer import *
from Parser import *
from Analyzer import *
from Generator import *
from ctypes import CFUNCTYPE, c_void_p  


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    try:
        with open("source.g", 'r') as inputFile:
            source = inputFile.read()
    except FileNotFoundError as e:
        print(f"File not found{e}. Aborting...")
        return

    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse()
    if ast is None:
        print("Error occurred during parsing. Aborting...")
        return

    print("Parsing completed!")
    print("\nThe following AST was returned:\n")
    ast.print_content()

    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if symbol_table is None:
        print("Error occurred during semantic analysis. Aborting...")
        return

    print("Semantic analysis completed!")

    llvm_code_generator = LLVMCodeGenerator(symbol_table)


    llvm_ir = llvm_code_generator.generate_code(ast)
    if llvm_ir is None:
        print("Error occurred during code generation. Aborting...")
        return

    print("Code generation completed!")
    print("\nThe following LLVM IR code was generated:\n")
    print(str(llvm_ir))
    print("\n")

    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    mod = llvm.parse_assembly(str(llvm_ir))
    mod.verify()

    with llvm.create_mcjit_compiler(mod, target_machine) as engine:
        engine.finalize_object()
        engine.run_static_constructors()

        main_ptr = engine.get_function_address("main")
        c_main = CFUNCTYPE(None)(main_ptr)
        c_main()

if __name__ == "__main__":
    main()