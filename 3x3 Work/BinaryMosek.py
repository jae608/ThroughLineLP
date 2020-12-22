import sys
import mosek
import matplotlib.pyplot as plt

A = .25  # 25
B = .10  # 10
C = .05
D = .05
E = .10
F = .25  # 25
G = .10  # 10
H = .05
I = .05  # 05

eps = 0.025  # Use this to adjust the size of minimally intersecting borders

#This is the problem we are trying to solve
#      x1 e1  x2  e2 x3
#    ------|------|------
#    |     |      |     |
# h1 |  A  |   B  |  C  |
#    | x4 e3  x5  e4 x6 |
#    ------|------|------
#    |     |      |     |
# h2 |  D  |   E  |  F  |
#    | x7 e5  x8  e6 x9 |
#    ------|------|------
#    |     |      |     |
# h3 |  G  |   H  |  I  |
#    |     |      |     |
#    ------|------|------

# Helper Function to make readible output
def streamprinter(text):
    sys.stdout.write(text)
    sys.stdout.flush()

# Helper function to get the error area sum of one run from the QP
def errorArea(xx):
    return xx[0] * (xx[1] + xx[2]) + \
           xx[3] * (xx[4] + xx[5]) + \
           xx[6] * (xx[7] + xx[8])


####################################################################################################################


def qprog(W):
    # Make mosek environment
    with mosek.Env() as env:
        # Create a task object
        with env.Task(0, 0) as task:
            # Attach a log stream printer to the task
            # task.set_Stream(mosek.streamtype.log, streamprinter)
            inf = 0.0

            ##############
            # DEFINITION #
            ##############

            # Error Variables, their order is:
            # h1 e1 e2 h2 e3 e4 h3 e5 e6 x1 x2 x3 x4 x5 x6 x7 x8 x9
            numvar = 18
            bkx = [mosek.boundkey.lo] * numvar
            blx = [0.0] * numvar
            bux = [+inf] * numvar

            # Boundary Constraints
            numcon = 25
            bkc = [mosek.boundkey.lo] * 12  # For the 6*2 intersections
            bkc.extend([mosek.boundkey.fx] * 3)  # One Length For Each Row
            bkc.append(mosek.boundkey.fx)  # Constraint For Height
            bkc.extend([mosek.boundkey.up] * 9)  # For each cell
            blc = [eps] * 12
            blc.extend([W] * 3)
            blc.append(1.0)
            blc.extend([-inf] * 9)
            buc = [+inf] * 12
            buc.extend([W] * 3)
            buc.append(1.0)
            buc.extend([A, B, C, D, E, F, G, H, I])

            # Sparce Matrix For Linear Constraints (16 Of them, so a 18x16 Matrix if non-sparce)
            asub = [[1, 2, 4, 5, 9, 10, 11, 13, 14],
                    [1, 2, 4, 5, 10, 11, 12, 13, 14],
                    [4, 5, 7, 8, 12, 13, 14, 16, 17],
                    [4, 5, 7, 8, 13, 14, 15, 16, 17],
                    [1, 4, 9, 10, 12],
                    [1, 4, 9, 12, 13],
                    [4, 7, 12, 13, 15],
                    [4, 7, 12, 15, 16],
                    [1, 2, 4, 5, 9, 10, 11, 12, 13],
                    [1, 2, 4, 5, 9, 10, 12, 13, 14],
                    [4, 5, 7, 8, 12, 13, 14, 15, 16],
                    [4, 5, 7, 8, 12, 13, 15, 16, 17],
                    [1, 2, 9, 10, 11],
                    [4, 5, 12, 13, 14],
                    [7, 8, 15, 16, 17],
                    [0, 3, 6]]
            aval = [[1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                    [1.0, -1.0, 1.0, 1.0, -1.0],
                    [-1.0, 1.0, -1.0, 1.0, 1.0],
                    [1.0, -1.0, 1.0, 1.0, -1.0],
                    [-1.0, 1.0, -1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, -1.0, -1.0],
                    [-1.0, -1.0, 1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0, 1.0, 1.0],
                    [1.0, 1.0, 1.0]]

            #  Now we setup the quadratic constraints to the sparce matrix. Each one is for a given area
            qcons = [[[9], [0], [1.0]],
                    [[10], [0], [1.0]],
                     [[11], [0], [1.0]],
                     [[12], [3], [1.0]],
                     [[13], [3], [1.0]],
                     [[14], [3], [1.0]],
                     [[15], [6], [1.0]],
                     [[16], [6], [1.0]],
                     [[17], [6], [1.0]]]

            # Now we setup objective function
            c = [0.0] * 18
            # This is an 18*18 matrix
            qsubi = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            qsubj = [0, 1, 2, 3, 4, 5, 6, 7, 8]
            qval = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

            # Alternate, simpler setup
            # c = [0.0, 1.0, 1.0,
            #      0.0, 1.0, 1.0,
            #      0.0, 1.0, 1.0,
            #      0.0, 0.0, 0.0,
            #      0.0, 0.0, 0.0,
            #      0.0, 0.0, 0.0]
            # qsubi = []
            # qsubj = []
            # qval = []

            ################
            # CONSTRUCTION #
            ################

            # Now we append the number of variables and constraints to our task
            task.appendvars(numvar)
            task.appendcons(numcon)

            # For variable related
            for j in range(numvar):
                # Add our coefficients to the objective function
                task.putcj(j, c[j])
                # Put the already decided bounds on each error variable
                task.putvarbound(j, bkx[j], blx[j], bux[j])

            # For constraint related
            for i in range(numcon-9):
                # Add the bounds to each of our constraints
                task.putconbound(i, bkc[i], blc[i], buc[i])
                # Add the constraints row by row
                task.putarow(i, asub[i], aval[i])

            # Add the 9 quadratic terms to the last 9 constraints
            for i in range(len(qcons)):  # These are the indices of our quadratic constraints
                task.putqconk(i + 16, qcons[i][0], qcons[i][1], qcons[i][2])

            # Input Quadratic term to objective function
            task.putqobj(qsubi, qsubj, qval)

            #############
            # EXECUTION #
            #############

            # Input the objective sense (minimize/maximize)
            task.putobjsense(mosek.objsense.minimize)

            # Optimize the task
            task.optimize()

            # Print a summary containing information
            # about the solution for debugging purposes
            task.solutionsummary(mosek.streamtype.msg)

            prosta = task.getprosta(mosek.soltype.itr)
            solsta = task.getsolsta(mosek.soltype.itr)

            # Output a solution
            xx = [0.] * numvar
            task.getxx(mosek.soltype.itr,
                       xx)

            # if solsta == mosek.solsta.optimal:
            #     for i in range(numvar):
            #         print("x[" + str(i) + "]=" + str(xx[i]))
            # elif solsta == mosek.solsta.dual_infeas_cer:
            #     print("Primal or dual infeasibility.\n")
            # elif solsta == mosek.solsta.prim_infeas_cer:
            #     print("Primal or dual infeasibility.\n")
            # elif mosek.solsta.unknown:
            #     print("Unknown solution status")
            # else:
            #     print("Other solution status")

            return xx


####################################################################################################################


def binarySearch(areas):
    # These are the bounds of our binary search that W can be
    low = 1
    high = 5  # Need some way to properly define max W

    # First (initial) iteration
    W = (low + high)/2
    result = qprog(W)
    error = errorArea(result)
    prev = None

    # Begin Search!
    while prev != result:
        # If W is too small
        if W - sum(areas) < error:
            low = W
            W = (low + high) / 2
        # If W id equal to or greater, we assume there is a smaller, more optimal solution
        else:
            high = W
            W = (low + high) / 2
        prev = result
        result = qprog(W)
        error = errorArea(result)

    # Return
    return (W)


####################################################################################################################


def plot3x3(p):
    # The "border" lines
    # Top line
    topX = [0, p[1]+p[2]+p[9]+p[10]+p[11]]
    topY = [p[0]+p[3]+p[6], p[0]+p[3]+p[6]]
    plt.plot(topX, topY, label="Top")
    # Upper Line
    uppX = [0, p[1]+p[2]+p[9]+p[10]+p[11]]
    uppY = [p[6]+p[3], p[6]+p[3]]
    plt.plot(uppX, uppY, label="Upper")
    # Lower Line
    lowX = [0, p[1]+p[2]+p[9]+p[10]+p[11]]
    lowY = [p[6], p[6]]
    plt.plot(lowX, lowY, label="Lower")
    # Bottom Line
    botX = [0, p[1]+p[2]+p[9]+p[10]+p[11]]
    botY = [0, 0]
    plt.plot(botX, botY, label="Bottom")
    # Left Line
    lftX = [0, 0]
    lftY = [0, p[0]+p[3]+p[6]]
    plt.plot(lftX, lftY, label="Left")
    # Right Line
    rhtX = [p[1]+p[2]+p[9]+p[10]+p[11], p[1]+p[2]+p[9]+p[10]+p[11]]
    rhtY = [0, p[0]+p[3]+p[6]]
    plt.plot(rhtX, rhtY, label="Right")

    # The "varied" lines
    # Top row
    row1Y = [p[6]+p[3], p[0]+p[3]+p[6]]
    line1X = [p[9], p[9]]
    line2X = [p[9]+p[1], p[9]+p[1]]
    line3X = [p[9]+p[1]+p[10], p[9]+p[1]+p[10]]
    line4X = [p[9]+p[1]+p[10]+p[2], p[9]+p[1]+p[10]+p[2]]
    plt.plot(line1X, row1Y)
    plt.plot(line2X, row1Y)
    plt.plot(line3X, row1Y)
    plt.plot(line4X, row1Y)
    # Middle Row
    row2Y = [p[6], p[6]+p[3]]
    line5X = [p[12], p[12]]
    line6X = [p[12] + p[4], p[12] + p[4]]
    line7X = [p[12] + p[4] + p[13], p[12] + p[4] + p[13]]
    line8X = [p[12] + p[4] + p[13] + p[5], p[12] + p[4] + p[13] + p[5]]
    plt.plot(line5X, row2Y)
    plt.plot(line6X, row2Y)
    plt.plot(line7X, row2Y)
    plt.plot(line8X, row2Y)
    # Bottom Row
    row3Y = [0, p[6]]
    line9X = [p[15], p[15]]
    line10X = [p[15] + p[7], p[15] + p[7]]
    line11X = [p[15] + p[7] + p[16], p[15] + p[7] + p[16]]
    line12X = [p[15] + p[7] + p[16] + p[8], p[15] + p[7] + p[16] + p[8]]
    plt.plot(line9X, row3Y)
    plt.plot(line10X, row3Y)
    plt.plot(line11X, row3Y)
    plt.plot(line12X, row3Y)

    # Display
    plt.title('3x3 Output Visualized')
    plt.show()


####################################################################################################################


# call the main function
try:

    # opt_W = binarySearch([A, B, C, D, E ,F, G, H, I])
    opt_W = 10

    # Output
    vals = qprog(opt_W)
    print(opt_W)
    print(vals)
    print(A - vals[0] * vals[9])
    print(B - vals[0] * vals[10])
    print(C - vals[0] * vals[11])
    print(D - vals[3] * vals[12])
    print(E - vals[3] * vals[13])
    print(F - vals[3] * vals[14])
    print(G - vals[6] * vals[15])
    print(H - vals[6] * vals[16])
    print(I - vals[6] * vals[17])

    plot3x3(vals)

except mosek.Error as e:
    print("ERROR: %s" % str(e.errno))
    if e.msg is not None:
        print("\t%s" % e.msg)
        sys.exit(1)
