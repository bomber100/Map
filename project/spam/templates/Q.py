# def Main():
#     print("")

class stack():
    def __init__(self):
        self.values = [None for i in range(10)]
        self.tos = -1

    def push(self, item):
        if self.isFull():
            raise Exception("The stack is full")
        self.tos += 1
        self.values[self.tos] = item

    def pop(self):
        if self.isEmpty():
            raise Exception("The stack is empty")
        item = self.values[self.tos]
        self.values[self.tos] = None
        self.tos -= 1
        return item
    
    def peek(self):
        if self.isEmpty():
            return None
        item = self.values[self.tos]
        return item

    def isEmpty(self):
        return (self.tos == -1)
    
    def isFull(self):
        return (self.tos == len(self.values) - 1)



class queue():
    def __repr__(self):
        return f"Queue: {self.values}"

    def __init__(self):
        self.values = [None for i in range(10)]
        self.front = 0
        self.end = -1

    def enqueue(self, value):
        if self.isFull():
            raise Exception("The queue is full")
        self.end += 1
        if self.end > 9:
            self.end = 0
        self.values[self.end] = value

    def dequeue(self):
        if self.isEmpty():
            return None
        value = self.values[self.front]
        self.values[self.front] = None
        self.front += 1

        if(self.front > 9):
            self.front = 0

        return value

    def isFull(self):
        return (((self.front - self.end) % len(self.values) == 1) and (self.values[self.end] != None))

    def isEmpty(self):
        return (((self.front - self.end) % len(self.values) == 1) and (self.values[self.end] == None))
    
    def reverse(self):
        s = stack()
        while not (self.isEmpty()):
            item = self.dequeue()
            s.push(item)

        while not (s.isEmpty()):
            self.enqueue(s.pop())

# q = queue()



# q.enqueue("a")
# q.enqueue("b")
# q.enqueue("1")
# q.enqueue("2")
# q.enqueue("6")
# q.enqueue("8")
# q.enqueue("4")
# q.enqueue("5")
# q.enqueue("9")
# q.dequeue()
# print(q)

# q.dequeue()
# q.dequeue()
# q.dequeue()
# q.enqueue("9")
# q.enqueue("8")
# q.enqueue("7")
# q.enqueue("p")

# q.enqueue("q")


# print(q)

# q.reverse()
# print(q)

def calcullateRPN(expression):
    exp = expression.split()
    s = stack()
    for item in exp:
        try:
            number = int(item)
            s.push(number)
        except:
            num1 = s.pop()
            num2 = s.pop()
            result = eval(f"{num2} {item} {num1}")
            s.push(result)
    result = s.pop()
    return result



def infixToRPN(expression):
    exp = expression.split()
    q = queue()
    s = stack()
    for item in exp: 
        try:
            number = int(item)
            q.enqueue(number)
        except:
            if (item == '*' or item == '//' or item == '('):
                s.push(item)
            elif (item == '+' or item == '-'):
                while (s.peek() == '*' or s.peek() == "//"):
                    q.enqueue(s.pop())
                s.push(item)
            elif (item == ')'):
                while s.peek() != '(':
                    q.enqueue(s.pop())
                s.pop()
    while not s.isEmpty():
        q.enqueue(s.pop())
    return q
    
    
    
expression = input("Enter an infix expression with spaces:")
result = infixToRPN(expression)
resultString = ''
while not result.isEmpty():
    resultString += str(result.dequeue())
    resultString += " "

print(resultString)