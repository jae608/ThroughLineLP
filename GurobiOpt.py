import gurobipy as gp
from gurobipy import GRB

#  It is assumed we can parse a csv file into an array of N rows and M columns
# table = [[2, 3, 4, 5],
#          [4, 7, 2, 8],
#          [8, 5, 3, 3],
#          [2, 5, 9, 7],
#          [9, 3, 7, 4]]
# table = [[9, 5, 6, 5, 11],
#          [4, 4, 4, 16, 8],
#          [6, 14, 9, 4, 3],
#          [2, 3, 11, 10, 10],
#          [7, 3, 3, 18, 5]]
table = [[10, 2, 12, 14, 4, 6],
         [3, 5, 1, 15, 19, 9],
         [8, 18, 1, 14, 17, 3],
         [13, 4, 14, 10, 2, 3],
         [8, 16, 20, 4, 1, 19],
         [15, 11, 7, 3, 17, 10]]


# For an arbitrary NxM table, we would have 2NM variables, of which they are height, length, or error
# The first NxM are the lengths, then the next N are the heights, and the last N*(M-1) are the errors
# Adds variables to the passed in model
def add_errs(table, model):
    n_row = len(table)
    n_col = len(table[0])

    # Lengths
    for i in range(n_row*n_col):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS)
    # Heights
    for i in range(n_row):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='h'+str(i+1))
    # Errors
    for i in range(n_row*(n_row*(n_col-1))):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='e'+str(i+1))


def addL_const(table, model, eps):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    print(vars)
    lengths = vars[:len(vars)//2]
    heights = vars[len(vars)//2:len(vars)//2+n_row]
    errors = vars[len(vars)//2+n_row:]

    print(lengths)
    print(heights)
    print(errors)

    # First get the column adjacency constraints, of which there are 2M*(N-1)
    for row in range(n_row-1):
        for col in range(n_col):
            pass
            #model.addLConstr(left, sense=GRB.GREATER_EQUAL, rhs=right, name='l'+str(n))

try:

    epsilon = 0.000025

    # Create a new model
    m = gp.Model("Solver")
    e1 = m.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='e1')
    print(m)
    # Add the variables to our model
    add_errs(table, m)

    print(m)

    # Add the constraints to our model
    # Do it for both the linear and quadratic constraints separately
    addL_const(table, m, epsilon)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')