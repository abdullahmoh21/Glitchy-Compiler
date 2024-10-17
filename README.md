# Glitchy Language Compiler

## Overview

Glitchy is an educational programming language that combines favorite syntax elements from various languages, designed to help users learn programming concepts through interactive challenges. It features type inference, optional type annotations enforced by the compiler, and a runtime type system for cases like user inputs where type inference is not possible.

The primary goal of Glitchy is to demystify the compiler process, which often feels like "black magic" to many programmers. By creating Glitchy, I aimed to provide an engaging platform for users to understand both programming and compiler design. The language introduces random "glitches" through the `glitch()` function, prompting users to troubleshoot and learn through multiple-choice questions (MCQs).

## Features

- **Type Inference**: Automatically infers the data type of variables without requiring explicit type declarations.

  ```glitchy
  set num = 10  // num is inferred as integer
  set name = "Glitchy"  // name is inferred as string
  ```

- **Optional Type Annotations**: Users can provide type annotations, which the compiler enforces.

  ```glitchy
  set num:int = 10
  set name:string = "Glitchy"
  ```

- **Flexible Type Names**: Allows various acceptable type names (e.g., `int`, `inte`, `integ`, etc.) for the same underlying type.

  ```glitchy
  set num:int = 10
  set num:integ = 10
  set num:integer = 10
  ```

- **Basic Constructs**: Includes `if`, `elif`, `else`, `for`, `while` loops, and functions.

  ```glitchy
  if (num > 5) {
      print("Greater than 5")
  } elif (num ^ 2 == 10) {  // '^' is operator for exponents
      print("Equal to 5")
  } else {
      print("Less than 5")
  }
  ```

- **Glitches**: Introduces unexpected behavior such as variable shuffling, random delays, and unexpected exits, making programming an interactive learning experience.

  ```glitchy
  function void example() {
      set a = 5
      set b = 10
      glitch()  // Could randomly shuffles values of a and b
      print("a: " + a + ", b: " + b)  // a and b may be shuffled
  }
  ```

## Installation

To install the Glitchy compiler, ensure you have Python and LLVM installed on your system. You can use the provided `setup.py` file for a straightforward installation:

```bash
pip install .
```

After installation, you can run Glitchy files using the following command:

```bash
glitchy example/filepath --log [level]
```

_Log levels can be optionally set from 1 to 3._

## Usage

Here's a quick example of Glitchy code:

```glitchy
// Highly recursive Ackermann function
function int ackermann(m:int, n:int) {
    print("Ackermann called!")
    if (m == 0) {
        return n + 1
    } elif (m > 0 && n == 0) {
        return ackermann(m - 1, 1)
    } else {
        return ackermann(m - 1, ackermann(m, n - 1))
    }
}

set m = input().toInteger()
set n = input().toInteger()
print("Ackermann(" + m + ", " + n + ") = " + ackermann(m, n))
```

### Additional Examples

- **Collatz Conjecture**:

```glitchy
function void collatz(n:int) {
    print("Starting number: " + n)
    set steps = 0

    while (n != 1) {
        if (n % 2 == 0) {
            n = n / 2
        } else {
            n = n * 3 + 1
        }
        print("Next number: " + n)
        steps++
    }

    print("Collatz Conjecture completed in " + steps + " steps.")
}

set num = input().toInteger()
collatz(num)
```

- **Exponent Calculation**:

```glitchy
print("Please enter your base:")
set base = input().toDouble()
print("Please enter your exponent:")
set exp = input().toDouble()
print("The exponent of " + base + "^" + exp + " is: " + (base^exp))
```

## Contributing

Contributions are welcome! Please follow the standard open-source practices. Feel free to open issues or submit pull requests on the GitHub repository.

## Testing

Glitchy uses the unittest framework for testing. You can run the tests using the following command:

```bash
python -m unittest discover
```

## License

This project is licensed under the [MIT License](LICENSE).
