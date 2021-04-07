import sys
import mosek
import csv
import numpy as np

#  It is assumed we can parse a csv file into an array of N rows and M columns
# table = [[25, 10, 5],
#          [5, 10, 25],
#          [10, 5, 5]]
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

# Function to read in olympics data
# Reads data into passed in table
def olympic_read(min_size):
    table = []
    # Read data from csv
    with open('winter-olympic-medal-win.csv', mode='r') as Reader:
        R = csv.reader(Reader, delimiter=',')
        next(R)
        for row in R:
            my_row = row[1:16]  # Only read First 10 countries
            for i in range(len(my_row)):
                if my_row[i] == "0":
                    my_row[i] = min_size
                my_row[i] = float(my_row[i])
            table.append(my_row)
    print(table)
    return table


"""
Alter and scale the passed in table to one who's sum of all elements is 1
"""
def normalize(table):
    s = sum([sum(row) for row in table])
    for row in range(len(table)):
        for col in range(len(table[row])):
            table[row][col] = table[row][col]/s
    return table


"""
Return a list of heights for each row. The mode depends on how they are generated
mode=None -> random (default)
mode='Scale' -> Height proportional to sum of area in row
mode='Uniform' -> Height same for each row
"""
def getHeights(table, mode=None):
    # Generate a random height, which all sum to 1
    if mode == 'Scale':
        a = [sum(r) for r in table]
    elif mode == 'Uniform':
        a = [1/len(table) for r in table]
    else:
        a = np.random.random(len(table))
        a /= a.sum()
    return a


"""
Return a list of lengths for each rectangle, arranged in the same fashion as the table
Is a function of the heights generated
"""
def getLengths(table, heights):
    lengths = []
    for row in range(len(table)):
        length = [h/heights[row] for h in table[row]]
        lengths.append(length)
    return lengths


"""
Return a tuple of information for the error variables
"""
def generateErrorVariables(n):
    bkx = [mosek.boundkey.lo] * n
    blx = [0.0] * n
    # '+0.0' is a placeholder for positive infinity
    bux = [+0.0] * n
    return (bkx, blx, bux)


"""
Return a tuple of information for the constraints
"""
def generateConstraints(lengths, heights, eps):
    # Generate type of constraints
    bkc = [mosek.boundkey.lo for i in range((2*(len(lengths[0])-1))*(len(heights)-1))]
    for i in range(len(heights)-1):
        bkc.append(mosek.boundkey.fx)

    # Generate lower bound for constraints
    blc = []
    for row in range(len(heights)-1):
        for col in range(1, len(lengths[row])):
            # Use python slicing
            blc.append(sum(lengths[row+1][0:col]) -
                       lengths[row][col] -
                       sum(lengths[row][0:col])+eps)
            blc.append(sum(lengths[row][0:col]) -
                       lengths[row+1][col] -
                       sum(lengths[row+1][0:col])+eps)
    for i in range(len(heights)-1):
        blc.append(sum(lengths[i+1]) - sum(lengths[i]))

    # Generate upper bound for constraints
    buc = []
    for row in range(len(heights)-1):
        for col in range(1, len(lengths[row])):
            buc.append(+0.0)
            buc.append(+0.0)
    for i in range(len(heights)-1):
        buc.append(sum(lengths[i+1]) - sum(lengths[i]))

    return (bkc, blc, buc)

"""
Return a sparse matrix that give the position in the first tuple element and and value in the second tuple element
"""
def generateSparseMatrix(lengths, heights):
    # Generate a list of error names
    vals = []
    for i in range(len(heights)):
        comp = []
        for j in range(len(lengths[i])-1):
            comp.append(j + ((len(lengths[i])-1) * i))
        vals.append(comp)

    # Generate positions for sparse matrix
    asub = []
    for row in range(len(heights)-1):
        for col in range(1, len(lengths[row])):
            sub = []
            # Use slicing once again
            sub.extend(vals[row][0:col])
            sub.extend(vals[row+1][0:col])
            # We append twice since each pair of constraints uses same variables, their signs are just different
            asub.append(sub)
            asub.append(sub)
    for row in range(len(heights)-1):
        sub = []
        sub.extend(vals[row])
        sub.extend(vals[row + 1])
        asub.append(sub)

    # Generate values for sparse matrix
    aval = []
    for row in range(0, (len(asub)-(len(heights)-1)), 2):
        # Based on the formula for the constraints, we can "cheat" by recognizing a pattern
        sub_p = [1.0] * (len(asub[row])//2)
        sub_n = [-1.0] * (len(asub[row])//2)
        aval.append(sub_p+sub_n)
        # # Append the same with opposite signs
        sub_p = [-1.0] * (len(asub[row]) // 2)
        sub_n = [1.0] * (len(asub[row]) // 2)
        aval.append(sub_p + sub_n)
    for row in range(len(asub)-(len(heights)-1), len(asub)):
        sub = []
        sub.extend([1.0 for i in asub[row][0:len(asub[row])//2]])
        sub.extend([-1.0 for i in asub[row][len(asub[row])//2:len(asub[row])]])
        aval.append(sub)

    return (asub, aval)


# Small function to help with output
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

"""
Puts everything together to perform a convex optimization on the described LP
Output is an array which can be used to generate a CSV
Each element in the array is a row for the csv, with the first row being the header
"""
def main(t, eps, h=None):
    # Make mosek environment
    with mosek.Env() as env:
        # Create a task object
        with env.Task(0, 0) as task:
            # Attach a log stream printer to the task
            task.set_Stream(mosek.streamtype.log, streamprinter)

            # Scale the data to fit in a 1x1 square
            table = normalize(t)

            # Generate useful variables for later operations
            n_row = len(table)
            n_col = len(table[0])
            if h is None:
                heights = getHeights(table, mode='Scale')
            else:
                heights = h
            lengths = getLengths(table, heights)
            n_err = n_row*(n_col-1)
            n_con = (2*(len(lengths[0])-1))*(len(heights)-1)+(len(heights)-1)

            # Generate the matrix data for the LP
            Evars = generateErrorVariables(n_err)
            Bounds = generateConstraints(lengths, heights, eps)
            Matrix = generateSparseMatrix(lengths, heights)

            # Generate the objective function coefficients, which are all 1
            c = [1.0] * n_err

            # Now we append the number of variables and constraints to our task
            task.appendvars(n_err)
            task.appendcons(n_con)

            for j in range(n_err):
                # Add our coefficients to the objective function
                task.putcj(j, c[j])
                # Put the bounds on each error variable
                task.putvarbound(j, Evars[0][j], Evars[1][j], Evars[2][j])

            for i in range(n_con):
                # Add the bounds to each of our constraints
                task.putconbound(i, Bounds[0][i], Bounds[1][i], Bounds[2][i])
                # Add the constraints row by row
                task.putarow(i, Matrix[0][i], Matrix[1][i])

            # Input the objective sense (minimize/maximize)
            task.putobjsense(mosek.objsense.minimize)

            # Solve the problem
            task.optimize()

            # Print a summary containing information
            # about the solution for debugging purposes
            task.solutionsummary(mosek.streamtype.msg)

            # Get status information about the solution
            solsta = task.getsolsta(mosek.soltype.bas)

            if (solsta == mosek.solsta.optimal):
                xx = [0.] * n_err
                task.getxx(mosek.soltype.bas,  # Request the basic solution.
                           xx)
                print("Optimal solution: ")
                for i in range(n_err):
                    print("x[" + str(i) + "]=" + str(xx[i]))
            elif (solsta == mosek.solsta.dual_infeas_cer or
                  solsta == mosek.solsta.prim_infeas_cer):
                print("Primal or dual infeasibility certificate found.\n")
            elif solsta == mosek.solsta.unknown:
                print("Unknown solution status")
            else:
                print("Other solution status")

            # Construct data into an array to return. Each row represents the data for one rectangle
            # Aquire y offsets
            yoff = [0]*(n_col+(n_col-1))
            for i in range(0, len(heights)):
                    yoff.extend([heights[i]+yoff[(n_col+(n_col-1))*i]]*(n_col+(n_col-1)))

            # Aquire Heights
            h = []
            for val in heights:
                h.extend([val]*(n_col+(n_col-1)))

            # Aquire lengths
            l = []
            for i in range(n_row):
                for j in range(n_col):
                    l.append(lengths[i][j])
                    if j == n_col - 1:
                        break
                    l.append(xx[(n_col - 1) * i + j])

            # Aquire x offsets
            xoff = [0]
            for i in range(1, len(l)):
                if i % (n_col + n_col-1) == 0:
                    xoff.append(0)
                else:
                    xoff.append(l[i-1] + xoff[i-1])

            # Aquire column number
            c = []

            for i in range(n_row):
                for j in range(2*n_col-1):
                    if j%2 == 1:
                        c.append(-1)
                    else:
                        c.append(j%20)


            # Build our data
            sum = 0
            data = [['height', 'length', 'xoff', 'yoff', 'col', 0, n_row, n_col]]
            for i in range((n_row*n_col)+(n_row*(n_col-1))):
                temp = []
                temp.append(h[i])
                temp.append(l[i])
                temp.append(xoff[i])
                temp.append(yoff[i])
                temp.append(c[i])
                if c[i] == -1:
                    sum = sum + (h[i]*l[i])
                data.append(temp)
            # This tells us the percentage of the solution that is not error
            data[0][5] = (1/(1+sum))*100
            # Return our data
            return data


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


# call the main function
try:
    table = olympic_read(0.025)
    result = main(table, 0)  # Bug occurs when picking high values of epsilon

    # Write result to csv
    with open('mosek_LP.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in result:
            mosek_writer.writerow(row)

    # Additional csv for better drawing
    res_mod = to_Line(result)
    with open('line_tab.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in res_mod:
            mosek_writer.writerow(row)

except mosek.Error as e:
    print("ERROR: %s" % str(e.errno))
    if e.msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)


# ###### TESTING ######
# print("Input table:")
# for row in table:
#     print(row)
#
# # Normalize
# print("\nTest normalize sum of vals is 100 so we should expect each value to be 1/100th its size.")
# print("Normalized Table:")
# n_t = normalize(table)
# for row in n_t:
#     print(row)
# n_row = len(table)
# n_col = len(table[0])
# print("Table has "+str(n_row)+" rows and "+str(n_col)+" columns.")
#
# # Get Heights
# print("\nTest getHeights. Each val should the the sum of its row")
# heights = getHeights(n_t)
# print(heights)
#
# # Get Lengths
# print("\nTest getLengths. Each row should sum to one")
# print("Rectangle Lengths:")
# lengths = getLengths(n_t)
# for row in lengths:
#     print(row)
#
# # Constraint and Error size
# n_err = n_row*(n_col-1)
# n_con = (2*(len(lengths[0])-1))*(len(heights)-1)+(len(heights)-1)
# print("\nOur Linear Program should have "+str(n_err)+" error variables and "+str(n_con)+" constraints.")
#
# # Create Error Variables
# print("\nTest generateErrorVariables. Should print 3 lists of "+str(n_err)+" elements, each list by inspection.")
# Evars = generateErrorVariables(n_err)
# for val in Evars:
#     print(val)
#
# # Create constraints for our LP
# print("\nTest constraint generation for our LP.")
# Bounds = generateConstraints(lengths, heights, 0.025)
# print("We should expect "+str(n_con)+" elements for each list.")
# print("First check the constraint types. All should be 'lo', except for the last "+str(n_row-1)+" elements.")
# print(Bounds[0])
# print("Length: "+str(len(Bounds[0])))
# print("Now check the lower bounds. These will be harder to verify but the last "+str(n_row-1)+" should be zero.")
# print("Length: "+str(len(Bounds[1])))
# print(Bounds[1])
# print("Now check the upper bounds, which should all be zero")
# print("Length: "+str(len(Bounds[1])))
# print(Bounds[2])
#
# # Create array for our LP
# print("\nVerify the output the arrays generate.")
# print("We should expect "+str(n_con)+" rows for each array and 2-"+str((n_col-1)*2)+" elements per row.")
# Matrix = generateSparseMatrix(lengths, heights)
# print("Here is the sparse matrix positions:")
# print("Length: "+str(len(Matrix[0])))
# for row in Matrix[0]:
#     print(row)
# print("Here are the sparse matrix values. These should only be 1 or -1.")
# print("Each row should have the same number of elements between the two arrays.")
# print("Length: "+str(len(Matrix[1])))
# for row in Matrix[1]:
#     print(row)
#
# print("\nUnit Testing complete")

