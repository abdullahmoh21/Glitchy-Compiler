import os
import llvmlite.ir as ir
import llvmlite.binding as llvm
from Lexer import *
from Parser import *
from Analyzer import *
from Generator import *
from ctypes import CFUNCTYPE, c_void_p  

def main():
    source_code = """ 
        set in = input()
        print(in.length())
    """
        
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    if ast is None:
        return

    print(f"Parsing completed!\nParser returned:\n{ast.print_content()}")
    
    
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if symbol_table is not None:
        print("Semantic analysis completed!")
        print("\nThe following AST was returned:\n")
        ast.print_content()
        print("\nThe following Symbol table was returned:\n")
        symbol_table.print_table()
    else:
        print("No symbol table returned from analyzer")

    llvm_code_generator = LLVMCodeGenerator(symbol_table)

    llvm_ir = llvm_code_generator.generate_code(ast)
    if llvm_ir is None:
        print("Error occurred during code generation. Aborting...")
        return 
    
    try:
        mod = llvm.parse_assembly(str(llvm_ir))
        mod.verify()
        print("\nLLVM IR verification succeeded!")
    except Exception as e:
        print(f"LLVM verification failed: {e}")
        return
    
    print("\nThe following LLVM IR code was generated:\n")
    print("---------------------------------------")
    print(str(llvm_ir))  # This should be safer now if IR is valid
    print("---------------------------------------")
    
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    with llvm.create_mcjit_compiler(mod, target_machine) as engine:
        engine.finalize_object()
        engine.run_static_constructors()

        main_ptr = engine.get_function_address("main")
        c_main = CFUNCTYPE(None)(main_ptr)
        c_main()

if __name__ == "__main__":
    main()