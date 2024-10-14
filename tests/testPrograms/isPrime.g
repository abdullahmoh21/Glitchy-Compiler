// expected output: true
function bool isPrime(n:int) {
    if (n <= 1) {
        return false
    }
    for (i = 2; i < n; i++) {
        if (n % i == 0) {
            // scope 4
            return false
        }
    }
    return true
}

print(isPrime(997))