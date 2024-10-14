// basic calculator
function void calculator() {
    print("Welcome to the calculator")
    
    while(true) {
        print("Please choose an operation: +, -, *, /, or type 'exit' to quit")
        set operation = input()
        
        if (operation == "exit") {
            break
        } else {
            print("Enter the first number: ")
            set num1:int = input().toInteger()
            print("Enter the second number: ")
            set num2:int = input().toInteger()
            
            if (operation == "+") {
                print("Result: " + (num1 + num2))
            } elif (operation == "-") {
                print("Result: " + (num1 - num2))
            } elif (operation == "*") {
                print("Result: " + (num1 * num2))
            } elif (operation == "/") {
                if (num2 == 0) {
                    print("Error: Division by zero")
                } else {
                    print("Result: " + (num1 / num2))
                }
            } else {
                print("Invalid operation")
            }
        }
    }
    print("Calculator exited!")
}

calculator()
