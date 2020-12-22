from pulp import *
#In the recangular partition, the x-lengths are fixed

#3x3 Tile arranged as follows. We will assume the data is already normalized (hard code normalized data)
# <--1-->
# |a|b|c| ^
# |d|e|f| 1
# |g|h|i| v

#Establishing the geometry, there are the ares of our cells. Make sure they sum up to 1.0
a = .25 #25
b = .10 #10
c = .05
d = .05
e = .10
f = .25 #25
g = .10 #10
h = .05
i = .05 #05

#This gets the height of each row
r1 = a+b+c
r2 = d+e+f
r3 = g+h+i

#Which we then use to get the length of every cell
x11 = a/r1
x12 = b/r1
x13 = c/r1
x21 = d/r2
x22 = e/r2
x23 = f/r2
x31 = g/r3
x32 = h/r3
x33 = i/r3

eps = 0.025 #Use this to adjust the size of minimally intersecting borders

#Build the problem
problem = LpProblem("ThroughLineFixed", LpMinimize)

#Our variables for a 3x3 table
#Inside Error
e1 = LpVariable("e1", lowBound=0)
e2 = LpVariable("e2", lowBound=0)
e3 = LpVariable("e3", lowBound=0)
e4 = LpVariable("e4", lowBound=0)
e5 = LpVariable("e5", lowBound=0)
e6 = LpVariable("e6", lowBound=0)

#Objective function
problem += (e1+e2+e3+e4+e5+e6)

#Constraints
#LeftColumn
problem += (x12+x13+e1+e2) + x11 >= (x22+x23+e3+e4) + eps
problem += (x22+x23+e3+e4) + x21 >= (x12+x13+e1+e2) + eps

problem += (x22+x23+e3+e4) + x21 >= (x32+x33+e5+e6) + eps
problem += (x32+x33+e5+e6) + x31 >= (x22+x23+e3+e4) + eps

#MiddleColumn
problem += (x11+e1) + x12 >= (x21+e3) + eps
problem += (x21+e3) + x22 >= (x11+e1) + eps

problem += (x21+e3) + x22 >= (x31+e5) + eps
problem += (x31+e5) + x32 >= (x21+e3) + eps

#Right Column
problem += (x11+x12+e1+e2) + x13 >= (x21+x22+e3+e4) + eps
problem += (x21+x22+e3+e4) + x23 >= (x11+x12+e1+e2) + eps

problem += (x21+x22+e3+e4) + x23 >= (x31+x32+e5+e6) + eps
problem += (x31+x32+e5+e6) + x33 >= (x21+x22+e3+e4) + eps

#This ensures that our shape is rectangular
problem += (x11 + e1 + x12 + e2 + x13) ==\
           (x21 + e3 + x22 + e4 + x23)

problem += (x21 + e3 + x22 + e4 + x23) ==\
           (x31 + e5 + x32 + e6 + x33)

print(problem)

#Solving it
status = problem.solve()
print(LpStatus[status])
MyVars = [e1, e2, e3, e4, e5, e6]
print()
for i in MyVars:
    print(i+value(i))
print()
print(value(problem.objective))


###Some Functions To Make things easier in the future###
#Can't think of any right now
