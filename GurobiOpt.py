import gurobipy as gp
from gurobipy import GRB

#  It is assumed we can parse a csv file into an array of N rows and M columns
table = [[25, 10, 5],
         [5, 10, 25],
         [10, 5, 5]]
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
# table = [[10, 2, 12, 14, 4, 6],
#          [3, 5, 1, 15, 19, 9],
#          [8, 18, 1, 14, 17, 3],
#          [13, 4, 14, 10, 2, 3],
#          [8, 16, 20, 4, 1, 19],
#          [15, 11, 7, 3, 17, 10]]


# For an arbitrary NxM table, we would have 2NM variables, of which they are height, length, or error
# The first NxM are the lengths, then the next N are the heights, and the last N*(M-1) are the errors
# Adds variables to the passed in model
def add_errs(table, model):
    n_row = len(table)
    n_col = len(table[0])

    # Lengths
    for i in range(n_row*n_col):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='l'+str(i+1))
    # Heights
    for i in range(n_row):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='h'+str(i+1))
    # Errors
    for i in range(n_row*(n_col-1)):
        model.addVar(lb=0.0, ub=float('inf'), vtype=GRB.CONTINUOUS, name='e'+str(i+1))


# Add 2(M-1)(N-1)+(N-1) Linear constraints
# 2(M-1)(N-1) of these are column boundary, the remaining N-1 are row length constraints
# Adds constraints to the passed in model
def addL_const(table, model, eps):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars)//2]
    heights = vars[len(vars)//2:len(vars)//2+n_row]
    errors = vars[len(vars)//2+n_row:]

    i = 1

    # First get the column adjacency constraints, of which there are 2(M-1)(N-1)
    # These constraints are a+b>=c and c+d>=a
    for row in range(n_row-1):
        for col in range(1, n_col):
            # Initialize a,b,c,d
            a = lengths[row*n_row:col+row*n_row]
            a.extend(errors[row*(n_row-1):row*(n_row-1)+(col)])
            b = lengths[col+row*n_row]
            c = lengths[(row+1)*n_row:col+(row+1)*n_row]
            c.extend(errors[(row+1)*(n_row-1):(row+1)*(n_row-1)+(col)])
            d = lengths[col+(row+1)*n_row]

            # Make our left and right sides for both equations
            left1 = gp.LinExpr(b)
            for var in a:
                left1.add(var)
            right1 = gp.LinExpr()
            for var in c:
                right1.add(var)
            right1.add(eps)

            left2 = gp.LinExpr(d)
            for var in c:
                left2.add(var)
            right2 = gp.LinExpr()
            for var in a:
                right2.add(var)
            right2.add(eps)

            model.addLConstr(left1, sense=GRB.GREATER_EQUAL, rhs=right1, name='bc'+str(i))
            i = i+1
            model.addLConstr(left2, sense=GRB.GREATER_EQUAL, rhs=right2, name='bc'+str(i))
            i = i+1

    i = 1
    # Get row lengths constraints
    for row in range(n_row - 1):
        l_len = lengths[row*(n_row):(row+1)*(n_row)]
        l_err = errors[row*(n_row-1):(row+1)*(n_row-1)]
        left = gp.LinExpr()
        for var in l_len:
            left.add(var)
        for var in l_err:
            left.add(var)

        r_len = lengths[(row+1) * (n_row):(row + 2) * (n_row)]
        r_err = errors[(row+1) * (n_row - 1):(row + 2) * (n_row - 1)]
        right = gp.LinExpr()
        for var in r_len:
            right.add(var)
        for var in r_err:
            right.add(var)

        m.addLConstr(left, sense=GRB.EQUAL, rhs=right, name='lc'+str(i))
        i = i + 1

try:

    epsilon = 0.000025

    # Create a new model
    m = gp.Model("Solver")

    # Add the variables to our model
    add_errs(table, m)
    m.presolve()

    # Add the constraints to our model
    # Do it for both the linear and quadratic constraints separately
    addL_const(table, m, epsilon)
    m.presolve()
    # Now add the quadratic constraints


    print(m)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')