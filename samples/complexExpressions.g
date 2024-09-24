set a1 = 4, b1 = 3, c1 = 10, d1 = 25 // Expected output: "first if passed"
if ((a1 + b1 * 2) > 9 && (c1 * d1 - (c1 * d1 / 4) * 4) == 2 && d1 > a1) {
    print("first if passed")
}

set a2 = 8, b2 = 5, c2 = 3, d2 = 7 // Expected output: "second if passed"
if ((a2 - (a2 / 3) * 3) == 2 || (b2 * c2) < 50 || (d2 - b2) * 2 == a2) {
    print("second if passed")
}

set a3 = 10, b3 = 2, c3 = 4, d3 = 5 // Expected output: "third if passed"
if (d3 + a3 > c3 * 2 && b3 - 1 == a3 / 10 && c3 != d3) {
    print("third if passed")
} else{
    print("The third if expression evaluated to false please check why ")
}

set a4 = 5, b4 = 4, c4 = 12, d4 = 8 // Expected output: "fourth if passed"
if ((a4 * c4 == 24 || d4 / b4 == 2) && c4 - d4 < a4) {
    print("fourth if passed")
} else{
    print("The fourth if expression evaluated to false please check why ")
}

set a5 = 1, b5 = 2, c5 = 3, d5 = 4 
if ((a5 + b5 * 2) > 10 && (c5 * d5 - (c5 * d5 / 4) * 4) == 0 && d5 > a5) {
    print("first if passed")
} elif ((a5 - (a5 / 3) * 3) == 2 || (b5 * c5) < 50 || (d5 - b5) * 2 == a5) {
    print("first elif passed")
} elif (d5 + a5 > c5 * 2 && b5 - 1 == a5 / 10 && c5 != d5) {
    print("third if passed")
} elif ((a5 * c5 == 24 || d5 / b5 == 2) && c5 - d5 < a5) {
    print("fourth if passed")
} else {
    print("nothing passed")
}