// Simple simulation of a Turing machine that increments a value by 1 
// using state transitions and recursion

function void stateMachine(currentState:int, value:int) {
    if (currentState == 0) {
        print("State 0: Incrementing value")
        value++
        stateMachine(1, value)  // Transition to state 1
    } elif (currentState == 1) {
        print("State 1: Decrementing value")
        value--
        stateMachine(2, value)  // Transition to state 2
    } elif (currentState == 2) {
        print("State 2: Doubling value")
        value--
        stateMachine(3, value)  // Transition to state 3
    } elif (currentState == 3) {
        print("State 3: Halving value")
        value = value / 2
        stateMachine(4, value)  // Transition to state 4
    } elif (currentState == 4) {
        print("State 4: Terminating, final value = " + value)
        return  // Final state, halt the machine
    }
}

print("Starting Turing Machine Simulation")
set initial_value = 5
stateMachine(0, initial_value)  // Start at state 0 with an initial value
