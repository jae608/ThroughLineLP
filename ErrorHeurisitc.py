import csv

# Note there is a fringe case when the length of a cell is equal to epsilon that I don't want to deal with

# We will assume that we are passed mosek_LP.csv, generated from NxMLP.py, rows and columns (include error cells) for table
# and the position of the error cell, (row, col)
my_error = (4, 5)
num_rows = 5
num_cols = 7
epsilon = 0.000025

# For context, each cell has its data distributed as follows:
# height, length, x-offset, y-offset, col (error or not)


###############FUNCTIONS###############


"""
Function to calculate the xoffset for the given cell
"""
def new_xoff(height, length, new_height, row_length, is_before):
    if is_before:
        return ((height * length) / new_height)
    else:
        return (-((height * length) / new_height)) + row_length


"""
For each x-offset, the lower bounds is its existing xoffset+length, (or upper if after target cell)
Its upper bound is defined by the min of (next_upper_cell xoff + length, next_lower_cell xoff + length)
"""
def new_xoff_bounds(cell, next_upper_cell, next_lower_cell, is_before):
    if is_before:
        if next_upper_cell == []:
            return cell[1] + cell[2], (next_lower_cell[1] + next_lower_cell[2])-epsilon
        elif next_lower_cell == []:
            return cell[1] + cell[2], (next_upper_cell[1] + next_upper_cell[2])-epsilon
        else:
            return cell[1]+cell[2], (min(next_upper_cell[1]+next_upper_cell[2], next_lower_cell[1]+next_lower_cell[2]))-epsilon
    else:
        if next_upper_cell == []:
            return next_lower_cell[2]+epsilon, cell[2]
        elif next_lower_cell == []:
            return next_upper_cell[2]+epsilon, cell[2]
        else:
            return (max(next_upper_cell[2], next_lower_cell[2]))+epsilon, cell[2]


"""
Make a function which returns a list of new xoffsets
"""
def new_xoff_list(target_row, my_height, row_length, error_pos):
    return_list = []
    for cell in range(len(target_row)):
        # Ignore cells with no length or the cell we want to reduce
        if target_row[cell][1] == 0.0 or cell == error_pos:
            return_list.append(None)
        else:
            if cell < error_pos:
                left_length = sum([i[1] for i in target_row[:cell+1]])
                return_list.append(new_xoff(target_row[cell][0], left_length, my_height, row_length, True))
            else:
                right_length = sum([i[1] for i in target_row[cell:]])
                return_list.append(new_xoff(target_row[cell][0], right_length, my_height, row_length, False))
    return return_list


"""
Make a function to return a list of x-offset bounds for a given row
"""
def new_xoff_bounds_list(up_target, target_row, down_target, error_pos):
    return_list = []
    for cell in range(len(target_row)):
        # Ignore the target cell
        if cell == error_pos:
            return_list.append(None)
        else:
            if cell < error_pos:
                if target_row[cell][4] == -1:  # If our cell is an error cell
                    if up_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], [], down_target[cell+1], True))
                    elif down_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell+1], [], True))
                    else:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell+1], down_target[cell+1], True))
                else:
                    if up_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], [], down_target[cell+2], True))
                    elif down_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell+2], [], True))
                    else:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell+2], down_target[cell+2], True))
            else:
                if target_row[cell][4] == -1:  # If our cell is an error cell
                    if up_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], [], down_target[cell-1], False))
                    elif down_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell-1], [], False))
                    else:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell-1], down_target[cell-1], False))
                else:
                    if up_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], [], down_target[cell-2], False))
                    elif down_target == []:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell-2], [], False))
                    else:
                        return_list.append(
                            new_xoff_bounds(target_row[cell], up_target[cell-2], down_target[cell-2], False))
    return return_list


"""
This is our main, which returns the updated row and all its elements
"""
def binary_search(my_table, my_error, num_rows, num_cols):
    # Partition the table into its rows
    temp_table = []
    row = []
    for cell in my_table:
        row.append(cell)
        if len(row) == num_cols:
            temp_table.append(row)
            row = []
    my_table = temp_table

    # Calculate / acquire the target row and adjacent rows (if any)
    target_row = my_table[my_error[0]]

    error_pos = my_error[1]

    if my_error[0] == 0:
        up_target = []
    else:
        up_target = my_table[my_error[0] - 1]

    if my_error[0] == num_rows - 1:
        down_target = []
    else:
        down_target = my_table[my_error[0] + 1]

    # We need this to acquire the height range for our improved row
    row_height = target_row[0][0]

    # We also need the length of the whole row
    row_length = 0
    for cell in target_row:
        row_length += cell[1]

    # Initializing info
    prev_height = row_height
    max = row_height
    min = 0
    my_height = (max+min)/2
    # We only need to define the bounds of each cell once
    my_x_bounds = new_xoff_bounds_list(up_target, target_row, down_target, error_pos)
    print(my_x_bounds)
    # Begin search
    while my_height != prev_height:
        # This list will return the xoffset for all relevant cells with my_height
        my_xoffs = new_xoff_list(target_row, my_height, row_length, error_pos)
        print(my_xoffs)
        # We now want to evaluate if such a height is feasible
        # This is done by checking if all heights are in their bounds, and that their order is preserved
        feasible = True
        prev_off = 0
        for cell in range(len(target_row)):
            if my_x_bounds[cell] is not None and my_xoffs[cell] is not None:
                # Each cell needs to be in its feasible bounds and have an xoffset less than the next (order)
                if (my_x_bounds[cell][0] <= my_xoffs[cell] <= my_x_bounds[cell][1])\
                        and prev_off <= my_xoffs[cell]:
                    prev_off = my_xoffs[cell]
                    continue
                else:
                    feasible = False
                    break

        if feasible:
            max = my_height
        else:
            min = my_height
        prev_height = my_height
        my_height = (max + min) / 2

    # Update our target row with the new information
    temp = target_row[0][0]
    target_row[0][0] = my_height
    target_row[0][1] = (target_row[0][1] * temp) / target_row[0][0]
    for cell in range(1, len(target_row)):
        temp = target_row[cell][0]  # Update Heights
        target_row[cell][0] = my_height
        if cell == error_pos:  # Update Lengths
            target_row[cell][1] = abs(my_xoffs[cell-1]-my_xoffs[cell+1])
        else:
            target_row[cell][1] = (target_row[cell][1]*temp)/target_row[cell][0]
        target_row[cell][2] = target_row[cell-1][2] + target_row[cell-1][1]  # Update xoffsets
        # We will update lengths outside this function

    return target_row


###############FUNCTIONS###############


# Read in table
my_table = []
with open('mosek_LP.csv', newline='') as mosekLP:
    mosek_reader = csv.reader(mosekLP, delimiter=' ', quotechar='|')
    for row in mosek_reader:
        row = row[0].split(',')
        my_table.append(row)
header = my_table[0]
my_table = my_table[1:]  # Trim header
for row in my_table:
    for item in range(len(row)):
        row[item] = float(row[item])

# Call our binary search and print the height
result = binary_search(my_table, my_error, num_rows, num_cols)

# Partition the table into its rows
temp_table = []
row = []
for cell in my_table:
    row.append(cell)
    if len(row) == num_cols:
        temp_table.append(row)
        row = []
my_table = temp_table

# Now we update the yoffset of every row
my_table[my_error[0]] = result

for row in range(1, len(my_table)):
    for cell in range(len(my_table[row])):
        my_table[row][cell][3] = my_table[row-1][cell][3] + my_table[row-1][cell][0]

# Write table into CSV, overwritng the old one
# Write result to csv
    with open('mosek_LP.csv', mode='w') as mosekLP:
        mosek_writer = csv.writer(mosekLP, delimiter=',')
        mosek_writer.writerow(header)
        for row in my_table:
            for cell in row:
                mosek_writer.writerow(cell)
