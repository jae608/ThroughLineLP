from pulp import *
#In the trapezoid partition, the x-lengths are variable but must adhere to a constraint

#3x3 Tile arranged as follows. We will assume the data is already normalized (hard code normalized data)
# <--1-->
# |a|b|c| ^
# |d|e|f| 1
# |g|h|i| v

#Establishing the geometry, there are the ares of our cells. Make sure they sum up to 1.0
a = .30 #30
b = .05 #05
c = .05
d = .05
e = .05 #05
f = .30 #30
g = .10
h = .05
i = .05

#This gets the height of each row, we will need this later for trapezoid areas
r1 = a+b+c
r2 = d+e+f
r3 = g+h+i

eps = 0.025 #Use this to adjust the size of minimally intersecting borders

#This is where it start to differ from Fixed3x3

#Build the problem
problem = LpProblem("ThroughLineTrapezoid", LpMinimize)

#We need a whopping 42 variables

#Inner Errors
e1 = LpVariable("e1", lowBound=0)
e2 = LpVariable("e2", lowBound=0)
e3 = LpVariable("e3", lowBound=0)
e4 = LpVariable("e4", lowBound=0)
e5 = LpVariable("e5", lowBound=0)
e6 = LpVariable("e6", lowBound=0)
e7 = LpVariable("e7", lowBound=0)
e8 = LpVariable("e8", lowBound=0)
e9 = LpVariable("e9", lowBound=0)
e10 = LpVariable("e10", lowBound=0)
e11 = LpVariable("e11", lowBound=0)
e12 = LpVariable("e12", lowBound=0)

#Lengths
x1 = LpVariable("x1", lowBound=0)
x2 = LpVariable("x2", lowBound=0)
x3 = LpVariable("x3", lowBound=0)
x4 = LpVariable("x4", lowBound=0)
x5 = LpVariable("x5", lowBound=0)
x6 = LpVariable("x6", lowBound=0)
x7 = LpVariable("x7", lowBound=0)
x8 = LpVariable("x8", lowBound=0)
x9 = LpVariable("x9", lowBound=0)
x10 = LpVariable("x10", lowBound=0)
x11 = LpVariable("x11", lowBound=0)
x12 = LpVariable("x12", lowBound=0)
x13 = LpVariable("x13", lowBound=0)
x14 = LpVariable("x14", lowBound=0)
x15 = LpVariable("x15", lowBound=0)
x16 = LpVariable("x16", lowBound=0)
x17 = LpVariable("x17", lowBound=0)
x18 = LpVariable("x18", lowBound=0)

#Objective function (just minimize all the errors)
problem += e1+e2+e3+e4+e5+e6+e7+e8+e9+e10+e11+e12

#Constraints- this is where it gets messy
#Start with area constraints
problem += ((x1+x4)/2)*r1 == a
problem += ((x2+x5)/2)*r1 == b
problem += ((x3+x6)/2)*r1 == c

problem += ((x7+x10)/2)*r2 == d
problem += ((x8+x11)/2)*r2 == e
problem += ((x9+x12)/2)*r2 == f

problem += ((x13+x16)/2)*r3 == g
problem += ((x14+x17)/2)*r3 == h
problem += ((x15+x18)/2)*r3 == i

#Left Column Constraints
problem += (e3+x5+e4+x6)+x4 >= e5+x8+e6+x9 + eps
problem += (e5+x8+e6+x9)+x7 >= e3+x5+e4+x6 + eps

problem += (e7+x11+e8+x12)+x10 >= e9+x14+e10+x15 + eps
problem += (e9+x14+e10+x15)+x13 >= e7+x11+e8+x12 + eps

#Middle Column
problem += (x4+e3)+x5 >= x7+e5 + eps
problem += (x7+e5)+x8 >= x4+e3 + eps

problem += (x10+e7)+x11 >= x13+e9 + eps
problem += (x13+e9)+x14 >= x10+e7 + eps

#Right Column
problem += (x4+e3+x5+e4)+x6 >= x7+e5+x8+e6 + eps
problem += (x7+e5+x8+e6)+x9 >= x4+e3+x5+e4 + eps

problem += (x10+e7+x11+e8)+x12 >= x13+e9+x14+e10 + eps
problem += (x13+e9+x14+e10)+x15 >= x10+e7+x11+e8 + eps

#Rectangle Constraints
problem += (x1+e1+x2+e2+x3) == (x4+e3+x5+e4+x6)
problem += (x1+e1+x2+e2+x3) == (x7+e5+x8+e6+x9)
problem += (x1+e1+x2+e2+x3) == (x10+e7+x11+e8+x12)
problem += (x1+e1+x2+e2+x3) == (x13+e9+x14+e10+x15)
problem += (x1+e1+x2+e2+x3) == (x16+e11+x17+e12+x18)

problem += (x4+e3+x5+e4+x6) == (x7+e5+x8+e6+x9)
problem += (x4+e3+x5+e4+x6) == (x10+e7+x11+e8+x12)
problem += (x4+e3+x5+e4+x6) == (x13+e9+x14+e10+x15)
problem += (x4+e3+x5+e4+x6) == (x16+e11+x17+e12+x18)

problem += (x7+e5+x8+e6+x9) == (x10+e7+x11+e8+x12)
problem += (x7+e5+x8+e6+x9) == (x13+e9+x14+e10+x15)
problem += (x7+e5+x8+e6+x9) == (x16+e11+x17+e12+x18)

problem += (x10+e7+x11+e8+x12) == (x13+e9+x14+e10+x15)
problem += (x10+e7+x11+e8+x12) == (x16+e11+x17+e12+x18)

problem += (x13+e9+x14+e10+x15) == (x16+e11+x17+e12+x18)

print(problem)

#Solving it
status = problem.solve()
print(LpStatus[status])
MyVars = [e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12,
          x1, x2, x3, x4, x5, x6, x7, x8, x9,
          x10, x11, x12, x13, x14, x15, x16, x17, x18]
print()
for i in MyVars:
    print(i+value(i))
print()
print(value(problem.objective))


###Some Functions To Make things easier in the future###
#Can't think of any right now
