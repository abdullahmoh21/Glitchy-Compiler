// expected output: 93.000000
function double fib(n:int) {  
    if (n == 0) {
        return 0.0
    }
    
    set a = 0.0
    set b = 1.0

    for (i = 2; i <= n; i++) {
        set next = a + b      
        a = b
        b = next
    }

    return b
}
set result = fib(1)+fib(4)+fib(11)
print(result)