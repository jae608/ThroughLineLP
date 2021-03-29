import gurobipy as gp
from gurobipy import GRB
import csv
import math
import numpy as np

#  It is assumed we can parse a csv file into an array of N rows and M columns

# table = [[50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50],
#          [50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50],
#          [50, 5, 2, 5, 2, 5],
#          [5, 2, 5, 2, 5, 50]]
# # US States table
table = [[6.725, 0.989, 0.673, 5.304, 5.687, 19.378, 0.626, 1.328],
         [3.831, 1.568, 0.814, 3.046, 9.884, 12.702, 1.316, 6.548],
         [2.701, 0.564, 1.826, 12.831, 6.484, 11.537, 3.574, 1.053],
         [2.764, 5.029, 2.853, 5.989, 4.339, 1.853, 5.774, 8.792],
         [37.254, 2.059, 3.751, 2.916, 6.346, 4.625, 8.001, 0.898],
         [6.392, 25.146, 4.533, 2.967, 4.780, 9.688, 18.801, 9.535]]

# table = np.random.rand(10, 10)
# table = table.tolist()
# print(table)


# Function to read in olympics data
# Reads data into passed in table
def olympic_read(min_size):
    table = []
    # Read data from csv
    with open('winter-olympic-medal-win.csv', mode='r') as Reader:
        R = csv.reader(Reader, delimiter=',')
        next(R)
        for row in R:
            my_row = row[1:16]  # Only read First 15 countries
            for i in range(len(my_row)):
                if my_row[i] == "0":
                    my_row[i] = min_size
                my_row[i] = float(my_row[i])
            table.append(my_row)
    return table


# Normalize Table size
def normalize(table):
    s = sum([sum(row) for row in table])
    for row in range(len(table)):
        for col in range(len(table[row])):
            table[row][col] = table[row][col]/s
    return table


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


# Add 2(M-1)(N-1)+(N-1)+1 Linear constraints
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
            a = lengths[row*n_col:col+row*n_col]
            a.extend(errors[row*(n_col-1):row*(n_col-1)+(col)])
            b = lengths[col+row*n_col]
            c = lengths[(row+1)*n_col:col+(row+1)*n_col]
            c.extend(errors[(row+1)*(n_col-1):(row+1)*(n_col-1)+(col)])
            d = lengths[col+(row+1)*n_col]

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
        l_len = lengths[row*(n_col):(row+1)*(n_col)]
        l_err = errors[row*(n_col-1):(row+1)*(n_col-1)]
        left = gp.LinExpr()
        for var in l_len:
            left.add(var)
        for var in l_err:
            left.add(var)

        r_len = lengths[(row+1) * (n_col):(row + 2) * (n_col)]
        r_err = errors[(row+1) * (n_col - 1):(row + 2) * (n_col - 1)]
        right = gp.LinExpr()
        for var in r_len:
            right.add(var)
        for var in r_err:
            right.add(var)

        m.addLConstr(left, sense=GRB.EQUAL, rhs=right, name='lc'+str(i))
        i = i + 1

    # Lastly add constraint so the height of our table is 1
    left = gp.LinExpr()
    for item in heights:
        left.add(item)
    m.addLConstr(left, sense=GRB.EQUAL, rhs=1, name='hc')


# Add NM quadratic constraints which fix the area for each cell. This requires setting NonConvex to 2
def addQ_const(table, model):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]

    # We add NM Quadratic constraints.
    # These are the ones which will ensure the area of each cell is constant
    count = 1
    for i in range(n_row):
        for j in range(n_col):
            right = gp.LinExpr(table[i][j])
            left = gp.QuadExpr(heights[i]*lengths[(i*n_col)+j])
            model.addQConstr(left, sense=GRB.EQUAL, rhs=right, name='q'+str(count))
            count = count + 1


# Add the objective function. This will just be the sum of each error cell
def addObj(table, model):
    n_row = len(table)
    n_col = len(table[0])

    vars = model.getVars()
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]

    exp = gp.QuadExpr()
    for i in range(n_row):
        for j in range(n_col-1):
            exp.add(heights[i]*errors[(i*(n_col-1))+j])
    model.setObjective(exp, sense=GRB.MINIMIZE)


def to_Line(data):
    result = []
    header = ["l1x", "l1y", "l2x", "l2y", "l3x", "l3y", "l4x", "l4y", "l5x", "l5y",
              "l6x", "l6y", "l7x", "l7y", "l8x", "l8y", "l9x", "l9y", "l10x", "l10y",
              "l11x", "l11y", "l12x", "l12y", "l13x", "l13y", "l14x", "l14y", "l15x", "l15y",
              "l16x", "l16y", "l17x", "l17y", "l18x", "l18y", "l19x", "l19y", "l20x", "l20y",
              "l21x", "l21y", "l22x", "l22y", "l23x", "l23y", "l24x", "l24y", "l25x", "l25y",
              "l26x", "l26y", "l27x", "l27y", "l28x", "l28y", "l29x", "l29y", "l30x", "l30y"]

    # First Identify How many columns there are
    data = data[1:]
    n_col = 0
    i = 0
    while(True):
        if data[i][4] != -1:
            if data[i+1][4] == -1:
                n_col = n_col + 1
            else:
                n_col = n_col + 1
                break
        i = i + 1

    n_row = (len(data)//(n_col+n_col-1))
    n_pt = (n_row*4)+1
    # First loop for the left side
    for j in range((n_pt-1)//4):
        top = []
        bot = []
        c_row = data[(n_col+n_col-1)*j:((n_col+n_col-1)*j)+(n_col+n_col-1)]
        for cell in c_row:
            if cell[4] == -1:
                continue
            else:
                top.append(cell[2])
                top.append(cell[3])
                top.append(cell[2] + cell[1])
                top.append(cell[3])
                bot.append(cell[2])
                bot.append(cell[3]+cell[0])
                bot.append(cell[2] + cell[1])
                bot.append(cell[3] + cell[0])
        result.append(top)
        result.append(bot)

    result.insert(0, header)

    return result


try:

    epsilon = 0
    #table = olympic_read(0.025)
    time_limit = 1800

    normalize(table)
    # Create a new model
    m = gp.Model("Solver")
    # Must do this so that our non-convex quadratic constraints can be used
    m.setParam(GRB.Param.NonConvex, 2)
    m.Params.TimeLimit = time_limit
    # Add the variables to our model
    add_errs(table, m)
    m.presolve()
    # Add the constraints to our model
    # Do it for both the linear and quadratic constraints separately
    addL_const(table, m, epsilon)
    m.presolve()
    # Now add the quadratic constraints
    addQ_const(table, m)
    m.presolve()
    # Lastly add the objective
    addObj(table, m)
    m.presolve()
    # Optimize our model
    m.optimize()
    # Display results
    print('Obj: %g' % m.objVal)

    # Write results to a csv so they can be visualized
    vars = m.getVars()
    n_col = len(table[0])
    n_row = len(table)
    lengths = vars[:len(vars) // 2]
    heights = vars[len(vars) // 2:len(vars) // 2 + n_row]
    errors = vars[len(vars) // 2 + n_row:]
    # Construct data into an array to return. Each row represents the data for one rectangle
    # Aquire y offsets
    yoff = [0] * (n_col + (n_col - 1))
    for i in range(0, len(heights)):
        yoff.extend([heights[i].x + yoff[(n_col + (n_col - 1)) * i]] * (n_col + (n_col - 1)))
    # Aquire Heights
    h = []
    for val in heights:
        h.extend([val.x] * (n_col + (n_col - 1)))
    # Aquire lengths
    l = []
    for i in range(n_row):
        for j in range(n_col):
            l.append(lengths[j+i*n_col].x)
            if j == n_col - 1:
                break
            l.append(errors[(n_col - 1) * i + j].x)
    # Aquire x offsets
    xoff = [0]
    for i in range(1, len(l)):
        if i % (n_col + n_col - 1) == 0:
            xoff.append(0)
        else:
            xoff.append(l[i - 1] + xoff[i - 1])
    # Aquire column number
    c = []
    for i in range(n_row):
        for j in range(2 * n_col - 1):
            if j % 2 == 1:
                c.append(-1)
            else:
                c.append(j % 20)
    # Build our data
    data = [['height', 'length', 'xoff', 'yoff', 'col']]
    for i in range((n_row * n_col) + (n_row * (n_col - 1))):
        temp = []
        temp.append(h[i])
        temp.append(l[i])
        temp.append(xoff[i])
        temp.append(yoff[i])
        temp.append(c[i])
        data.append(temp)

    # Write data into csv
    with open('mosek_LP.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in data:
            mosek_writer.writerow(row)
    # Additional csv for better drawing
    res_mod = to_Line(data)
    with open('line_tab.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in res_mod:
            mosek_writer.writerow(row)

except gp.GurobiError as e:
    print('Error code ' + str(e.errno) + ': ' + str(e))

except AttributeError:
    print('Encountered an attribute error')