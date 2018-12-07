
# coding: utf-8

# In[76]:


'''
This test python module is to exam fibonacci function and memory-cached solution
'''
mem = [0,1] # memory cache implemented as a stack

def fibonacci(num, st=None):
    global mem
    print("mem now is: ", mem)
    print("num now is: ", num)
    print("fib(",num,") ",st)
    print("-----------------")
    if (num == 0): 
        print("returning 0")
        print("-----------------")
        return 0
    elif (num == 1):
        print("returning 1")
        print("-----------------")
        return 1
    elif (len(mem) >= num):
        print("returning mem -1 value ", mem[num-1])
        print("-----------------")
        return mem[num-1]
    else:
        temp = fibonacci(num-1,"left") + fibonacci(num-2,"right")
        print("going into the next step of mem push")
        mem.append(temp)
        print("Done of mem push")
        print("returning temp ",temp)
        print("-----------------")
        return temp
    
# for self execution
def main():
    input_var = input("Please input an integer number so that it will calculate Fibonacci result: ")
    print(fibonacci(int(input_var)))

if __name__ == "__main__":
    main()

