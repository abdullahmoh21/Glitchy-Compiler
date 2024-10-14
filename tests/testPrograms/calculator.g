// expected output: 148.571429
function double calculator(double num1, double num2, string operation) {
    double result = 0.0;

    if (operation == "+") {
        result = num1 + num2;
    } elif (operation == "-") {
        result = num1 - num2;
    } elif (operation == "*") {
        result = num1 * num2;
    } elif (operation == "/") {
        if (num2 == 0) {
            print("Error: Division by zero");
            return 0.0; // handle divide by zero case by returning 0.0 or some error value
        } else {
            result = num1 / num2;
        }
    } else {
        print("Invalid operation");
        return 0.0; // handle invalid operation case by returning 0.0 or some error value
    }

    return result;
}

double op1 = calculator(10.0, 5.0, "+");
double op2 = calculator(10.0, 5.0, "-");
double op3 = calculator(10.0, .35, "/");
double op4 = calculator(20, 5.0, "*");
double result = op1+op2+op3+op4

print(result);