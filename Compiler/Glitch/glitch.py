from Compiler.Analyzer import *
from Compiler.Generator import *
from Compiler.utils import *
from ctypes import CFUNCTYPE, c_void_p
import llvmlite.ir as ir
import llvmlite.binding as llvm
from enum import Enum
import random

class GlitchType(Enum):
    FLIP_LOG_OPS = "Flip Logical ops"
    FLIP_COMPARISONS = "Flip comparisons"
    VARIABLE_SHUFFLING = "Variable Shuffling"
    IGNORE_FUNCTION_CALLS = "Ignores Function Calls"
    FUNCTION_BODY_SWAP = "Function Body Swap"
    ARITHMETIC_GLITCH = "Random Arithmetic Glitch"
    CHANGE_VARIABLE = "Change A variable's value"
    REF_SWAP = "A variable reference could point to a different variable instead"
    NO_GLITCH = "No glitch occurred"

class GlitchEngine:
    def __init__(self, ast):
        self.ast = ast
        self.stats = ast.stats
        self.cycle_count = 0  
        self.glitch_applied = None          # Single glitch applied
        self.glitch_detail = None           # Detail of the glitch
        self.glitch_history = []            # History of all glitches

    def run(self):
        print("Initial AST:")
        self.ast.print_content()
        while True:
            self.cycle()

            # Ask the user if they want to continue
            continue_game = input("Do you want to continue to the next glitch intensity? (y/n) ")
            if continue_game.lower() != 'y':
                print("Exiting the Glitch Engine.")
                break

            # Increase intensity for the next cycle
            self.cycle_count += 1

    def cycle(self):
        glitches = self.possible_glitches()

        self.glitch_applied = None
        self.glitch_detail = None

        self.apply_glitches(glitches)
        print("After glitches, the AST is:\n")
        self.ast.print_content()
        print("Output:")
        print("----------------------------------")
        self.compile_glitched()
        print("----------------------------------")
        self.present_mcq()

    def apply_glitches(self, possible_glitches):
        """Applies a random glitch (or none) from the possible glitches."""
        
        if not possible_glitches or random.random() <= 0.2:
            print("[DEBUG] Glitching skipped")
            self.glitch_applied = GlitchType.NO_GLITCH
            self.glitch_detail = "No glitch occurred"
            self.glitch_history.append((self.glitch_applied, self.glitch_detail))
            return  # Exit early since no glitch is applied

        glitch_to_apply = random.choice(possible_glitches)

        

        # if glitch_to_apply == GlitchType.FLIP_LOG_OPS:
        #     self.flip_logical_ops()
            
        if True:
            self.ignore_function_calls()
            
        elif glitch_to_apply == GlitchType.FLIP_COMPARISONS:
            self.flip_comparisons()

        elif glitch_to_apply == GlitchType.VARIABLE_SHUFFLING:
            self.variable_shuffling()

        elif glitch_to_apply == GlitchType.CHANGE_VARIABLE:
            self.change_variable()
            
        elif glitch_to_apply == GlitchType.IGNORE_FUNCTION_CALLS:
            self.ignore_function_calls()

        elif glitch_to_apply == GlitchType.FUNCTION_BODY_SWAP:
            self.function_body_swap()

        elif glitch_to_apply == GlitchType.ARITHMETIC_GLITCH:
            self.arithmetic_glitch()

        elif glitch_to_apply == GlitchType.REF_SWAP:
            self.ref_swap()

        # self.glitch_applied = glitch_to_apply
        self.glitch_applied = GlitchType.IGNORE_FUNCTION_CALLS
        self.glitch_history.append((self.glitch_applied, self.glitch_detail))

    def present_mcq(self):
        if self.glitch_applied == GlitchType.NO_GLITCH:
            correct_answer = "No glitch occurred"
        else:
            correct_answer = self.glitch_detail

        all_answers = [correct_answer]

        # Generate three unique incorrect answers
        incorrect_answers = self.generate_incorrect_answers(3, self.glitch_applied, self.glitch_detail)
        
        if incorrect_answers:
            all_answers.extend(incorrect_answers)
        else:
            # Handle the case where insufficient incorrect answers could be generated
            print("Unable to generate enough unique incorrect answers.")
            return

        random.shuffle(all_answers)
        question = f"What glitch occurred?\n"
        for idx, answer in enumerate(all_answers, 1):
            question += f"{idx}. {answer}\n"
        question += "\nYour answer (-1 to quit, type 'hint' for a hint): "

        while True:
            user_input = input(question).strip().lower()

            if user_input == '-1':
                print(f"Quitting. The correct answer was: {correct_answer}")
                return
            elif user_input == 'hint':
                if self.glitch_applied != GlitchType.NO_GLITCH:
                    print(f"Hint: The glitch is of type '{self.glitch_applied.value}'.")
                    print(f"Explanation: {self.get_glitch_explanation(self.glitch_applied)}")
                else:
                    print("Hint: No glitch occurred.")
                continue  # Ask for input again after providing hint
            else:
                try:
                    answer_index = int(user_input)
                    if 1 <= answer_index <= len(all_answers):
                        selected_answer = all_answers[answer_index - 1]
                        if selected_answer == correct_answer:
                            print("Correct!")
                        else:
                            print("Incorrect, the correct answer was:", correct_answer)
                        break  # Exit after answering
                    else:
                        print(f"Invalid choice. Please select a number between 1 and {len(all_answers)}, '-1' to quit, or type 'hint'.")
                except ValueError:
                    print("Invalid input. Please enter a number, '-1' to quit, or type 'hint'.")

    def generate_incorrect_answers(self, length, actual_glitch_type, actual_glitch_detail):
        """
        Generates a list of plausible incorrect answers based on the possible glitches,
        avoiding the actual glitch type if possible.
        Ensures each is of a different type and not the actual glitch detail.
        """
        # Gather all possible glitches including NO_GLITCH
        all_possible_glitches = self.possible_glitches()
        all_possible_glitches.append(GlitchType.NO_GLITCH)

        if actual_glitch_type != GlitchType.NO_GLITCH:
            # Exclude only the actual glitch type
            possible_incorrect_glitches = [glitch for glitch in all_possible_glitches if glitch != actual_glitch_type]
        else:
            # If the actual glitch is NO_GLITCH, exclude it from incorrect answers
            possible_incorrect_glitches = [glitch for glitch in all_possible_glitches if glitch != actual_glitch_type]

        random.shuffle(possible_incorrect_glitches)  # Shuffle to ensure randomness

        incorrect_answers = []
        used_glitch_types = set()  # Track glitches already used

        for glitch in possible_incorrect_glitches:
            if glitch in used_glitch_types:
                continue  # Ensure each glitch type is used only once
            answer = self._generate_answer_by_type(glitch)
            if answer and answer != actual_glitch_detail and answer not in incorrect_answers:
                incorrect_answers.append(answer)
                used_glitch_types.add(glitch)
                if len(incorrect_answers) == length:
                    break

        return incorrect_answers if len(incorrect_answers) == length else incorrect_answers  # Return whatever was generated

    def _generate_answer_by_type(self, selected_type):
        """Generates an incorrect answer based on the specified type."""
        
        if selected_type == GlitchType.CHANGE_VARIABLE and self.stats.get('varDecl'):
            var = random.choice(self.stats['varDecl'])
            int_val = random.randint(0, 100)
            double_val = round(random.uniform(0, 100), 2)
            null_val = "Null"
            str_val = random.choice([
                "Why is glitchy so good?", "Who made this genius language?",
                "Please end me.", "I am so happy!", "I had to add a Hello World!!",
                "Does heaven exist?", "I am so bored", "Can I be loved?",
                "I can make a compiler, but can I make a life for myself?"
            ])
            incorrect_value = random.choice([int_val, double_val, str_val, null_val])
            return f"Variable '{var.name}' value changed to {incorrect_value}"

        elif selected_type == GlitchType.IGNORE_FUNCTION_CALLS and self.stats.get('funcCall'):
            func = random.choice(self.stats['funcCall'])
            return f"Function call '{func.name}' at line {func.line} was ignored"

        elif selected_type == GlitchType.ARITHMETIC_GLITCH and self.stats.get('binOp'):
            node = random.choice(self.stats['binOp'])
            ops = ['+', '-', '*', '/']
            if hasattr(node, 'operator') and node.operator in ops:
                ops.remove(node.operator)
            new_operator = random.choice(ops) if ops else node.operator
            return f"Arithmetic operator at line {node.line} changed from '{node.operator}' to '{new_operator}'"

        elif selected_type == GlitchType.FUNCTION_BODY_SWAP and len(self.stats.get('funcDecl', [])) > 1:
            func1, func2 = random.sample(self.stats['funcDecl'], 2)
            return f"Function bodies of '{func1.name}' and '{func2.name}' were swapped"

        elif selected_type == GlitchType.FLIP_LOG_OPS and self.stats.get('logOp'):
            node = random.choice(self.stats['logOp'])
            flip_map = {'&&': '||', '||': '&&'}
            original_op = node.operator
            flipped_op = flip_map.get(original_op, original_op)
            return f"Logical operator at line {node.line} flipped from '{original_op}' to '{flipped_op}'"

        elif selected_type == GlitchType.FLIP_COMPARISONS and self.stats.get('comparison'):
            node = random.choice(self.stats['comparison'])
            flip_map = {'==': '!=', '!=': '==', '>': '<=', '<': '>=', '>=': '<', '<=': '>'}
            original_op = node.operator
            flipped_op = flip_map.get(original_op, original_op)
            return f"Comparison operator at line {node.line} flipped from '{original_op}' to '{flipped_op}'"

        elif selected_type == GlitchType.VARIABLE_SHUFFLING and len(self.stats.get('varDecl', [])) > 1:
            var1, var2 = random.sample(self.stats['varDecl'], 2)
            return f"Variables '{var1.name}' and '{var2.name}' have been shuffled"

        elif selected_type == GlitchType.REF_SWAP and len(self.stats.get('varRef', [])) > 1:
            var1, var2 = random.sample(self.stats['varRef'], 2) 
            while var1.name == var2.name:
                var2 = random.choice(self.stats['varRef'])
            return f"The reference of '{var1.name}' on line {var1.line} points to the variable '{var2.name}' instead"

        elif selected_type == GlitchType.NO_GLITCH:
            # This should only be used when NO_GLITCH is an incorrect answer
            return "No glitch occurred"

        return None

    def possible_glitches(self):
        """Returns a list of possible glitches based on AST statistics."""
        glitches = []

        if self.stats.get('comparison'):
            glitches.append(GlitchType.FLIP_COMPARISONS)
            
        if self.stats.get('logOp'):
            glitches.append(GlitchType.FLIP_LOG_OPS)

        if len(self.stats.get('varDecl', [])) > 1:
            glitches.append(GlitchType.VARIABLE_SHUFFLING)

        if self.stats.get('funcCall'):
            glitches.append(GlitchType.IGNORE_FUNCTION_CALLS)

        if len(self.stats.get('funcDecl', [])) > 1:
            glitches.append(GlitchType.FUNCTION_BODY_SWAP)

        if self.stats.get('binOp'):
            glitches.append(GlitchType.ARITHMETIC_GLITCH)

        if self.stats.get('varDecl'):
            glitches.append(GlitchType.CHANGE_VARIABLE)

        if len(self.stats.get('varRef', [])) > 1:
            glitches.append(GlitchType.REF_SWAP)

        return glitches

    def compile_glitched(self):
        # Semantic analysis 
        analyzer = SemanticAnalyzer(self.ast)
        _ , symbol_table = analyzer.analyze()

        if has_error_occurred():
            return  

        # LLVM Initialization 
        try:
            llvm.initialize()
            llvm.initialize_native_target()
            llvm.initialize_native_asmprinter()
        except Exception as e:
            print(f"LLVM initialization failed: {str(e)}")
            return

        # LLVM IR code generation phase
        llvmir_gen = LLVMCodeGenerator(symbol_table)
        llvm_ir = llvmir_gen.generate_code(self.ast)

        if has_error_occurred() or llvm_ir is None:
            llvm.shutdown()
            return  

        # LLVMIR verification
        try:
            mod = llvm.parse_assembly(str(llvm_ir))
            mod.verify()
        except Exception as e:
            print(f"An error occurred during the LLVM IR verification: {e}")
            llvm.shutdown()
            return  # Return early to avoid running passes on invalid IR

        # optimization passes
        try:
            target = llvm.Target.from_default_triple()
            target_machine = target.create_target_machine()

            # Set up the pass manager and apply optimizations
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 3

            pass_manager = llvm.create_module_pass_manager()
            pmb.populate(pass_manager)

            # Run the pass manager
            pass_manager.run(mod)
        except Exception as e:
            print(f"An error occurred during the LLVM optimization pass: {e}")
            llvm.shutdown()
            return
        
        # Mcjit compiler
        try:
            if not has_error_occurred():
                with llvm.create_mcjit_compiler(mod, target_machine) as engine:
                    engine.finalize_object()
                    engine.run_static_constructors()

                    main_ptr = engine.get_function_address("main")
                    if main_ptr:
                        c_main = CFUNCTYPE(None)(main_ptr)
                        c_main()  # Call the main function
                    else:
                        log("Error: 'main' function not found.", 0, 'red', immediate=True)
        except Exception as e:
            print(f"Execution failed: {str(e)}")
            llvm.shutdown()
            return

        # Shutdown LLVM and return stdout
        llvm.shutdown()
    
    # ------------------------------- Glitch Helpers ------------------------------- #
    
    def flip_logical_ops(self):
        """Applies '!' to randomly chosen logical operation node."""
        node = random.choice(self.stats['logOp'])
        new_node = UnaryOp('!', node, line=node.line)
        node.replace_self(new_node)
        self.glitch_detail = f"Logical operation at line {node.line} flipped with '!' operator"
    
    def flip_comparisons(self):
        """Flips the operator of a randomly chosen comparison node."""
        node = random.choice(self.stats['comparison'])
        # Map of comparison operators to their flipped counterparts
        flip_map = {
            '==': '!=',
            '!=': '==',
            '<': '>=',
            '>': '<=',
            '<=': '>',
            '>=': '<'
        }

        # Get the new flipped operator
        flipped_operator = flip_map.get(node.operator, node.operator)
        new_node = Comparison(node.left, flipped_operator, node.right, line=node.line)
        node.replace_self(new_node)
        self.glitch_detail = f"Comparison at line {node.line} flipped from '{node.operator}' to '{flipped_operator}'"

    def variable_shuffling(self):
        """Randomly swaps the values of two variables in the current scope and deletes their cached_type."""
        var1, var2 = random.sample(self.stats['varDecl'], 2)
        var1.value, var2.value = var2.value, var1.value
        if hasattr(var1, 'cached_type'):
            del var1.cached_type
        if hasattr(var2, 'cached_type'):
            del var2.cached_type
        self.glitch_detail = f"Variables '{var1.name}' and '{var2.name}' were swapped"
    
    def ignore_function_calls(self):
        """Randomly ignores function calls, effectively removing them from the AST."""
        node = random.choice(self.stats['funcCall'])
        self.glitch_detail = f"Function call '{node.name}' at line {node.line} was ignored"
        node.replace_self(None)
    
    def function_body_swap(self):
        """Swaps the function body of two functions."""
        func1, func2 = random.sample(self.stats['funcDecl'], 2)
        func1.body, func2.body = func2.body, func1.body
        self.glitch_detail = f"Function bodies of '{func1.name}' and '{func2.name}' were swapped"
    
    def arithmetic_glitch(self):
        """Swaps arithmetic operators in a random binary operation node."""
        node = random.choice(self.stats['binOp'])
        operators = ['+', '-', '*', '/']
        if hasattr(node, 'operator') and node.operator in operators:
            operators.remove(node.operator)     # Remove the current operator from the list
        swapped_operator = random.choice(operators) if operators else node.operator
        new_node = BinaryOp(node.left, swapped_operator, node.right, line=node.line)
        node.replace_self(new_node)
        self.glitch_detail = f"Arithmetic operator at line {node.line} changed from '{node.operator}' to '{swapped_operator}'"
    
    def ref_swap(self):
        var1, var2 = random.sample(self.stats['varRef'], 2) 
        while var1.name == var2.name:
            var2 = random.choice(self.stats['varRef'])
        new_ref = VariableReference(var2.name, line=var1.line)
        var1.replace_self(new_ref)
        var1.value = None
        var1.type = None
        var1.scope = None
        self.glitch_detail = f"The variable reference '{var1.name}' on line {var1.line} now points to the variable '{var2.name}'"
            
    def change_variable(self):
        """Changes the value of a variable to a random value."""
        var = random.choice(self.stats['varDecl'])
        old_value = var.value
        int_val = random.randint(0, 100)
        double_val = round(random.uniform(0, 100), 2)
        null_val = "Null"
        str_val = random.choice([
            "Who made this phenomenal language?", "Please end me.", "I am so happy!",
            "I had to add a Hello World!!", "Does heaven exist?", "I am so bored",
            "Can I be loved?", "I can make a compiler, but can I make a life for myself?",
            "Who will compile my soul?"
        ])
        var.value = random.choice([int_val, double_val, str_val, null_val])
        if hasattr(var, 'type'):
            var.type = None
        if hasattr(var, 'cached_type'):
            var.cached_type = None
        self.glitch_detail = f"Variable '{var.name}' value changed from {repr(old_value)} to {repr(var.value)}"
    
    def get_glitch_explanation(self, glitch_type):
        """Provides explanations for each glitch type."""
        explanations = {
            GlitchType.FLIP_LOG_OPS: "Logical operations have been inverted (e.g., '&&' to '||').",
            GlitchType.FLIP_COMPARISONS: "Comparison operators have been flipped (e.g., '==' to '!=').",
            GlitchType.VARIABLE_SHUFFLING: "Values of variables have been shuffled between each other.",
            GlitchType.IGNORE_FUNCTION_CALLS: "Function calls are being ignored and not executed.",
            GlitchType.FUNCTION_BODY_SWAP: "The bodies of two functions have been swapped.",
            GlitchType.ARITHMETIC_GLITCH: "Arithmetic operators have been randomly changed (e.g., '+' to '-').",
            GlitchType.CHANGE_VARIABLE: "A variable's value has been randomly altered.",
            GlitchType.REF_SWAP: "Variable references now point to different variables.",
            GlitchType.NO_GLITCH: "No glitch has occurred."
        }
        return explanations.get(glitch_type, "No explanation available.")
