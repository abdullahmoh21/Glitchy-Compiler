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
        if (typeof(10) == "integer"){
            print("the type is an int! BHENCHOD!!!!!")
        } else{
            print("Unfortunately that is not an Int :(")
        }
    """
        
    lexer = Lexer(source_code)
    parser = Parser(lexer)
    ast = parser.parse()
    if ast is None:
        return

    print("Parsing completed!")
    
    analyzer = SemanticAnalyzer(ast)
    symbol_table = analyzer.analyze()
    if symbol_table is not None:
        print("Semantic analysis completed!")
    
    print("\nThe following AST was returned:\n")
    ast.print_content()
    print("\nThe following Symbol table was returned:\n")
    symbol_table.print_table()

    llvm_code_generator = LLVMCodeGenerator(symbol_table)

    llvm_ir = llvm_code_generator.generate_code(ast)
    if llvm_ir is None:
        print("Error occurred during code generation. Aborting...")
        return 
    
    print("\nThe following LLVM IR code was generated:\n")
    print("---------------------------------------")
    print(str(llvm_ir))
    print("---------------------------------------")
    
    llvm.initialize()
    llvm.initialize_native_target()
    llvm.initialize_native_asmprinter()

    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()

    # Parse the generated LLVM IR
    mod = llvm.parse_assembly(str(llvm_ir))
    mod.verify()

    # # Apply optimization passes using a standard optimization level
    # pmb = llvm.create_pass_manager_builder()
    # pmb.opt_level = 3  # Optimization level 3 is a good default for aggressive optimizations

    # pass_manager = llvm.create_module_pass_manager()
    # pmb.populate(pass_manager)

    # pass_manager.run(mod)

    # # Print optimized LLVM IR
    # print("\nThe following optimized LLVM IR code was generated:\n")
    # print("---------------------------------------")
    # print(str(mod))
    # print("---------------------------------------")
    

    with llvm.create_mcjit_compiler(mod, target_machine) as engine:
        engine.finalize_object()
        engine.run_static_constructors()

        main_ptr = engine.get_function_address("main")
        c_main = CFUNCTYPE(None)(main_ptr)
        c_main()

if __name__ == "__main__":
    main()