import time as t
import NxMLP as LP
import random as rand
import csv

# Desired Population Size
popsize = 100
# Time to try and find best solution
time_limit = 600


# Functions we need
"""
Creates a new LP solution using random heights. Table is an NxM array to values to make LP solution for
"""
def new_LP_individual(table):
    return LP.main(table, 0)


"""
Returns the fitness evaluation of this LP solution individual
"""
def fitness(indiv):
    return indiv[0][5]
    # sum = 0
    # for element in indiv:
    #     if element[4] == -1:
    #         sum = sum + (element[0] * element[1])  # Length * height if it is an error cell
    # # Return the sum of all areas of all errors
    # # Invert it so that small sums are large (for select with replacement)
    # return 1/sum


"""
Chooses an LP solution from our population based on the fitness function.
Two values are returned, which is the pair of to be parents
"""
def selectWithReplacement(population):
    sum = 0
    ranges = []
    # Create our range list
    for indiv in population:
        ranges.append((sum, sum+fitness(indiv)))
        sum = sum + fitness(indiv)

    # Pick a random number in our range, see which individual range it falls into
    Pa = None
    Pb = None
    num1 = rand.uniform(0, sum)
    num2 = rand.uniform(0, sum)
    for i in range(len(ranges)):
        if ranges[i][0] < num1 <= ranges[i][1]:
            Pa = population[i]
        if ranges[i][0] < num2 <= ranges[i][1]:
            Pb = population[i]

    return (Pa, Pb)


"""
Mixes two LP solution via some heuristic-> the crossover method
Our method of choice is to pick the heights which yielded rows with less total error
"""
def Crossover(A, B):
    n_row = A[0][6]
    n_col = A[0][7]+(A[0][7]-1)
    A = A[1:] # Trim off the header
    B = B[1:]
    heights = []
    # We will take the rows with the smallest area error
    # For each row, sum their error and take the height of the one with less
    for i in range(n_row):
        A_row = A[i*n_col:(i*n_col)+n_col]
        B_row = B[i*n_col:(i*n_col)+n_col]
        a_sum = 0
        b_sum = 0
        # Sum the error for that row
        for j in range(len(A_row)):
            if A_row[j][4] == -1 and B_row[j][4] == -1:
                a_sum = a_sum + (A_row[j][0]*A_row[j][1])
                b_sum = b_sum + (B_row[j][0]*B_row[j][1])
        # Compare error total
        if a_sum > b_sum:
            heights.append(B_row[0][0])
        else:
            heights.append(A_row[0][0])

    # create and return our new individual with the specified heights
    # normalize the heights
    s = sum(heights)
    heights = [h/s for h in heights]
    return LP.main(table, 0, h=heights)


"""
Mutates an LP solution via some heuristic to make it unique
Our method to mutate is to scale a random height to be the average of the others
"""
def Mutate(individual):
    n_row = individual[0][6]
    n_col = individual[0][7] + (individual[0][7] - 1)
    heights = []
    individual = individual[1:]
    # We will take the rows with the smallest area error
    for i in range(n_row):
        heights.append(individual[i*n_col][0])

    # Now randomly pick a height to make it the average
    a = rand.choice([i for i in range(len(heights))])
    heights[a] = sum(heights)/len(heights)

    # create and return our new individual with the specified heights
    # normalize the heights
    s = sum(heights)
    heights = [h / s for h in heights]
    return LP.main(table, 0, h=heights)


##### The genetic algorithm #####
# Make initial population
table = LP.olympic_read(0.025)
P = []
for i in range(popsize):
    P.append(new_LP_individual(table))
# Setup Loop
best = None
p_best = None
time = t.perf_counter()
# Loop until best found or time limit up
while True:
    # Check if a better solution exists
    for individual in P:
        if best is None or fitness(individual) >= fitness(best):
            p_best = best
            best = individual
    # Improve our population
    Q = []
    for i in range(popsize//2):
        # Find good parents
        result = selectWithReplacement(P)
        Pa = result[0]
        Pb = result[1]
        # Make good children
        Ca = Crossover(Pa, Pb)
        Cb = Crossover(Pa, Pb)
        # Make children unique
        Q.append(Mutate(Ca))
        Q.append(Mutate(Cb))
    # Replace old population
    P = Q
    # Check if we are done looping
    if t.perf_counter() - time > time_limit:
        print("A solution was found- time limit reached")
        break
    if best == p_best:
        print("A solution was found- local optimum reached")
        break

# Write result to csv
with open('mosek_LP.csv', mode='w') as mosekLP:
    mosek_writer = csv.writer(mosekLP, delimiter=',')
    for row in best:
        mosek_writer.writerow(row)

# Additional csv for better drawing
res_mod = LP.to_Line(best)
with open('line_tab.csv', mode='w') as mosekLP:
    mosek_writer = csv.writer(mosekLP, delimiter=',')
    for row in res_mod:
        mosek_writer.writerow(row)
