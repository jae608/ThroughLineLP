import sys
import mosek

#This is a trial run of using Mosek to get used ot how it operates, recreating the test in Fixed3x3.py

"""
This Function generates n (int) error variables, returning the following three lists as a tuple:
(bkx, blx, bux), where bkx defines the boundary for the x'th variable, blx defines the lower bound for
the x'th variable, and bux defines the upper bound for the x'th variable.
This function operates under the assumption that all error variables have range [0, +inf)
"""
def generateErrorVariables(n):
    bkx = [mosek.boundkey.lo for i in range(n)]
    blx = [0.0 for i in range(n)]
    bux = [+0.0 for i in range(n)] # '+0.0' is a placeholder for positive infinity
    return (bkx, blx, bux)


def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def main():
    # Make mosek environment
    with mosek.Env() as env:
        # Create a task object
        with env.Task(0, 0) as task:
            # Attach a log stream printer to the task
            task.set_Stream(mosek.streamtype.log, streamprinter)

            a = .25  # 25
            b = .10  # 10
            c = .05
            d = .05
            e = .10
            f = .25  # 25
            g = .10  # 10
            h = .05
            i = .05  # 05

            # This gets the height of each row
            r1 = a + b + c
            r2 = d + e + f
            r3 = g + h + i

            # Which we then use to get the length of every cell
            x1 = a / r1
            x2 = b / r1
            x3 = c / r1
            x4 = d / r2
            x5 = e / r2
            x6 = f / r2
            x7 = g / r3
            x8 = h / r3
            x9 = i / r3

            eps = 0.025  # Use this to adjust the size of minimally intersecting borders

            #Behold, all the setup

            # Error Variables
            Evars = generateErrorVariables(6)

            # Boundary Constraints
            bkc = [mosek.boundkey.lo for i in range(12)]
            bkc.append(mosek.boundkey.fx)
            bkc.append(mosek.boundkey.fx)
            blc = [x5+x6-x1-x2-x3+eps,
                   x2+x3-x4-x5-x6+eps,
                   x8+x9-x4-x5-x6+eps,
                   x5+x6-x7-x8-x9+eps,
                   x4-x1-x2+eps,
                   x1-x4-x5+eps,
                   x7-x4-x5+eps,
                   x4-x7-x8+eps,
                   x4+x5-x1-x2-x3+eps,
                   x1+x2-x4-x5-x6+eps,
                   x7+x8-x4-x5-x6+eps,
                   x4+x5-x7-x8-x9+eps,
                   x4+x5+x6-x1-x2-x3,
                   x7+x8+x9-x4-x5-x6]
            buc = [+0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   +0.0,
                   x4+x5+x6-x1-x2-x3,
                   x7+x8+x9-x4-x5-x6]

            # Sparce Matrix
            asub = [[0, 1, 2, 3],
                    [0, 1, 2, 3],
                    [2, 3, 4, 5],
                    [2, 3, 4, 5],
                    [0, 2],
                    [0, 2],
                    [2, 4],
                    [2, 4],
                    [0, 1, 2, 3],
                    [0, 1, 2, 3],
                    [2, 3, 4, 5],
                    [2, 3, 4, 5],
                    [0, 1, 2, 3],
                    [2, 3, 4, 5]]
            aval = [[1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0],
                    [1.0, -1.0],
                    [-1.0, 1.0],
                    [1.0, -1.0],
                    [-1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0],
                    [1.0, 1.0, -1.0, -1.0]]

            #  Objective Coefficients
            c = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            # The end, of all the setup

            # Now we setup the problem
            numvar = len(Evars[0])
            numcon = len(bkc)

            # Now we append the number of variables and constraints to our task
            task.appendvars(numvar)
            task.appendcons(numcon)

            for j in range(numvar):
                # Add our coefficients to the objective function
                task.putcj(j, c[j])

                # Put the already decided bounds on each error variable
                task.putvarbound(j, Evars[0][j], Evars[1][j], Evars[2][j])

            for i in range(numcon):
                # Add the bounds to each of our constraints
                task.putconbound(i, bkc[i], blc[i], buc[i])

                # Add the constraints row by row
                task.putarow(i, asub[i], aval[i])

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
                xx = [0.] * numvar
                task.getxx(mosek.soltype.bas,  # Request the basic solution.
                           xx)
                print("Optimal solution: ")
                for i in range(numvar):
                    print("x[" + str(i) + "]=" + str(xx[i]))
            elif (solsta == mosek.solsta.dual_infeas_cer or
                  solsta == mosek.solsta.prim_infeas_cer):
                print("Primal or dual infeasibility certificate found.\n")
            elif solsta == mosek.solsta.unknown:
                print("Unknown solution status")
            else:
                print("Other solution status")













            # call the main function
try:
    main()
except mosek.Error as e:
    print("ERROR: %s" % str(e.errno))
    if e.msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)