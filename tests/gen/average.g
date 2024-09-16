set sum:double = 0.0
set count:double = 0.0

while(true){
    print("Please enter a number (-1 to exit): ")
    set num = input().toInteger()
    if(num == -1){
        break
    }
    sum += num
    count++
}

print("Loop exited!")
print("Sum: "+sum)
print("Average "+(sum/count))