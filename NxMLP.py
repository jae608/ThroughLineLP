import sys
import mosek
import csv

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
Return a list of heights for each row
"""
def getHeights(table):
    return [sum(r) for r in table]


"""
Return a list of lengths for each rectangle, arranged in the same fashion as the table
"""
def getLengths(table):
    lengths = []
    for row in table:
        s = sum(row)
        length = [h/s for h in row]
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
def main(t, eps):
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
            lengths = getLengths(table)
            heights = getHeights(table)
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
                        c.append(j%6)


            # Build our data
            data = [['height', 'length', 'xoff', 'yoff', 'col']]
            for i in range((n_row*n_col)+(n_row*(n_col-1))):
                temp = []
                temp.append(h[i])
                temp.append(l[i])
                temp.append(xoff[i])
                temp.append(yoff[i])
                temp.append(c[i])
                data.append(temp)

            # Return our data
            return data


# call the main function
try:
    result = main(table, 0.000025)  # Bug occurs when picking high values of epsilon

    # Write result to csv
    with open('mosek_LP.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        for row in result:
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

