import time
from guppy import hpy

def isGoal(sudoku):
    for i in range(0,overall_dimension):
        for j in range(0,overall_dimension):
            if sudoku[i][j]==0:
                return False
    return True

def assignSudoku(sudoku, i, j, value):
    output = []
    for x in range(0,overall_dimension):
        output_line = []
        for y in range(0,overall_dimension):
            output_line.append(sudoku[x][y])
        output.append(output_line)
    output[i][j] = value
    return output

def getLegalValues(sudoku):
    output = []
    for line_array in sudoku:
        output_line = []
        for elem in line_array:
            initial_array = []
            for i in range(1,overall_dimension+1):
                initial_array.append(i)
            output_line.append(initial_array)
        output.append(output_line)
    for i in range(0,overall_dimension):
        for j in range(0,overall_dimension):
            if sudoku[i][j] !=0:
                output[i][j] = []
                for j2 in range(0,overall_dimension):
                    if j2!=j and sudoku[i][j] in output[i][j2]: output[i][j2].remove(sudoku[i][j])
                for i2 in range(0,overall_dimension):
                    if i2!=i and sudoku[i][j] in output[i2][j]: output[i2][j].remove(sudoku[i][j])
                num_of_sub_vertical = overall_dimension/sub_num_row
                num_of_sub_horizontal = overall_dimension/sub_num_col
                range_x = i//num_of_sub_horizontal # 0-3
                range_y = j//num_of_sub_vertical # 0-2
                x_min_range = int(overall_dimension/num_of_sub_vertical*range_x)
                y_min_range = int(overall_dimension/num_of_sub_horizontal*range_y)
                for sub_i in range(x_min_range, x_min_range+int(num_of_sub_horizontal)):
                    for sub_j in range(y_min_range, y_min_range+int(num_of_sub_vertical)):
                        if sudoku[i][j] in output[sub_i][sub_j]: 
                            output[sub_i][sub_j].remove(sudoku[i][j])
    return output

def select_unassigned_var(sudoku):
    legal_val = getLegalValues(sudoku)
    if constraint_propagation:
        legal_val = constraint_propagation_optimize(legal_val) # constraint_propagation: recheck arc consistency
    fewest_legal_val = overall_dimension
    min_i = 0
    min_j = 0
    for i in range(0,overall_dimension):
        for j in range(0,overall_dimension):
            if sudoku[i][j]==0 and len(legal_val[i][j])<fewest_legal_val:
                fewest_legal_val = len(legal_val[i][j])
                min_i = i
                min_j = j
    return min_i, min_j, fewest_legal_val, legal_val

def recusive_backtrack(sudoku, num_check):
    this_check = 0
    if isGoal(sudoku):# already solution
        return True, sudoku, num_check
    var_i, var_j, num_legal, legal_array = select_unassigned_var(sudoku)
    if forward_checking and sudoku[var_i][var_j]==0 and len(legal_array[var_i][var_j])==0:# forward checking: if unassigned var has no legal val, terminate
        return False, sudoku, num_check
    this_check+=1
    for value in least_constraint_order(var_i, var_j, legal_array):
        if constraint_propagation and len(legal_array[var_i][var_j])==1:
            this_check-=1
        result_sudoku = assignSudoku(sudoku, var_i,var_j, value)
        if not forward_checking:
            this_check+=1
        found, solution, total = recusive_backtrack(result_sudoku, this_check+num_check)
        if found: return True, solution, total
    return False, sudoku, this_check+num_check

def least_constraint_order(i,j,legal_sudoku):
    count_dict = {}
    for elem in legal_sudoku[i][j]:
        count_dict[elem] = 0
    for i2 in range(0,overall_dimension):
        for x in count_dict:
            if x in legal_sudoku[i2][j]: count_dict[x]+=1
    for j2 in range(0,overall_dimension):
        for x in count_dict:
            if x in legal_sudoku[i][j2]: count_dict[x]+=1
    num_of_sub_vertical = overall_dimension/sub_num_row
    num_of_sub_horizontal = overall_dimension/sub_num_col
    range_x = i//num_of_sub_horizontal # 0-3
    range_y = j//num_of_sub_vertical # 0-2
    x_min_range = int(overall_dimension/num_of_sub_vertical*range_x)
    y_min_range = int(overall_dimension/num_of_sub_horizontal*range_y)
    for sub_i in range(x_min_range, x_min_range+int(num_of_sub_horizontal)):
        for sub_j in range(y_min_range, y_min_range+int(num_of_sub_vertical)):
            for x in count_dict:
                if x in legal_sudoku[sub_i][sub_j]: count_dict[x]+=1
    sort_dict = sorted(count_dict.items(), key=lambda x: x[1], reverse=True)
    output = []
    for i in sort_dict:
	    output.append(i[0])
    return output

def constraint_propagation_optimize(sudoku_legal_values):
    for i in range(0,overall_dimension):
        for j in range(0,overall_dimension):
            if len(sudoku_legal_values[i][j])==1:
                for j2 in range(0,overall_dimension):
                    if len(sudoku_legal_values[i][j])>0 and sudoku_legal_values[i][j][0] in sudoku_legal_values[i][j2] and len(sudoku_legal_values[i][j2])>1: sudoku_legal_values[i][j2].remove(sudoku_legal_values[i][j][0])
                for i2 in range(0,overall_dimension):
                    if len(sudoku_legal_values[i][j])>0 and sudoku_legal_values[i][j][0] in sudoku_legal_values[i2][j] and len(sudoku_legal_values[i2][j])>1: sudoku_legal_values[i2][j].remove(sudoku_legal_values[i][j][0])
    return sudoku_legal_values
    
overall_dimension = 0
sub_num_row = 0
sub_num_col = 0
forward_checking = False
constraint_propagation = False

f = open("sample_board.txt", "r")
sudoku_array = []
fisrt_line = True
for line in f: # process into array
    if fisrt_line:
        fisrt_line = False
        a = line.split(',')
        overall_dimension = int(a[0])
        sub_num_row = int(a[1])
        sub_num_col = int(a[2])
        continue
    line_list = []
    for char in line.split(','):
        if char=='_' or char=='_\n':
            line_list.append(0)
        else:
            line_list.append(int(char))
    sudoku_array.append(line_list)
t0 = time.time()
found, solution, consistency_check = recusive_backtrack(sudoku_array, 0)
t1 = time.time()
if found: 
    print("A solution is found: ")
    for line in solution:
        print(line)
else:
    print("Solution is not found.")
print('1.) Backtracking + MRV heuristic ')
print('     Memory usage:', hpy().heap().size, 'bytes')
print('     Running time: {0:.2f} seconds'.format(t1 - t0))
print('     Number of consistency checks:', consistency_check)
forward_checking = True
t0 = time.time()
found, solution, consistency_check = recusive_backtrack(sudoku_array, 0)
t1 = time.time()
print()
if found: 
    print("A solution is found: ")
    for line in solution:
        print(line)
else:
    print("Solution is not found.")
print('2.) Backtracking + MRV + Forward Checking ')
print('     Memory usage:', hpy().heap().size, 'bytes')
print('     Running time: {0:.2f} seconds'.format(t1 - t0))
print('     Number of consistency checks:', consistency_check)
forward_checking = False
constraint_propagation = True
t0 = time.time()
found, solution, consistency_check = recusive_backtrack(sudoku_array, 0)
t1 = time.time()
print()
if found: 
    print("A solution is found: ")
    for line in solution:
        print(line)
else:
    print("Solution is not found.")
print('3.) Backtracking + MRV + Constraint Propagation ')
print('     Memory usage:', hpy().heap().size, 'bytes')
print('     Running time: {0:.2f} seconds'.format(t1 - t0))
print('     Number of consistency checks:', consistency_check)