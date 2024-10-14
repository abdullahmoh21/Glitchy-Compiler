// Tower of hanoi game
function void hanoi(n:int, fromPeg:int, toPeg:int, auxPeg:int) {
    if (n == 1) {
        print("Move disk 1 from peg " + fromPeg + " to peg " + toPeg)
        return
    }
    hanoi(n - 1, fromPeg, auxPeg, toPeg)
    print("Move disk " + n + " from peg " + fromPeg + " to peg " + toPeg)
    hanoi(n - 1, auxPeg, toPeg, fromPeg)
}

set numDisks = 4
hanoi(numDisks, 1, 3, 2)