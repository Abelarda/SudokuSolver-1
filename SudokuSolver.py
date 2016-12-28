
# Sudoku Solver
# Aiyu Cui
# Fall 2016

# This solver is able to solve all sudoku problems by using build-in python libaries

############################################################
# Imports
############################################################
import random
import time

############################################################
# Sudoku Solver
############################################################

#--------------------------------------------------------------------
# Function:     sudoku_cells()
# Objection:    to get all the cells in sudoku
# Input:        -
# Output:       set of all cells (i,j) in sudoku
def sudoku_cells():
    cell=[]
    for i in range(9):
        for j in range(9):
            cell.append((i,j))
    return cell

#--------------------------------------------------------------------
# Function:     sudoku_arcs()
# Objection:    to find all pairs of cells that have effective constraint with each others
# Input:        -
# Output:       set of constraint pairs ((i,j),(x,y))
def sudoku_arcs():
    arc=set([])
    for cell1 in sudoku_cells():
        for cell2 in sudoku_cells():
            if cell1 != cell2:
                if ((cell1,cell2) not in arc):
                    x1=cell1[0]
                    y1=cell1[1]
                    x2=cell2[0]
                    y2=cell2[1]
                    # same row or col
                    if x1==x2 or y1==y2:
                        arc.add((cell1,cell2))
                    # same module
                    elif(x1/3==x2/3 and y1/3==y2/3):
                        arc.add((cell1,cell2))
    return arc

#--------------------------------------------------------------------
# Function:     read_board(path)
# Objection:    to read a board out of a txt file
# Input:        path to a txt file
# Output:       a data structure to store the input sudoku
def read_board(path):
    # grab raw data out of file
    myfile=open(path)
    mytxt=myfile.read()
    myfile.close()
    # format data and return
    mytxt=mytxt.split()
    myBoard={}
    i=0
    for row in mytxt:
        myBoard[str(i)]=[]
        myBoard[str(i)].append(tuple(row[0:3]))
        myBoard[str(i)].append(tuple(row[3:6]))
        myBoard[str(i)].append(tuple(row[6:9]))
        i=i+1
    return myBoard


class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    #--------------------------------------------------------------------
    # Function:     __init__(board)
    #  Objection:   Constructor -> the Sudoku Object
    # Input:        board - data structure
    # Output:       ?
    def __init__(self, board):
        self.map=board
        self.possible_values_table=[[self.get_processed_values((i,j)) for j in range(9)] for i in range(9)]


    #--------------------------------------------------------------------
    # Function:     get_values(cell)
    # Objection:    get a set of possible values of a given cell
    # Input:        cell (i,j)
    # Output:       set([possible values])
    def get_values(self,cell):
        return self.possible_values_table[cell[0]][cell[1]]

    #--------------------------------------------------------------------
    # Function:     get_processed_values(cell)
    # Objection:    initialized the possible_value_table with given input board by cells
    # Input:        cell (i,j)
    # Output:       set of possible values of the given cell
    def get_processed_values(self, cell):
        if self.get_cell_value(cell)=="*":
            return set([1,2,3,4,5,6,7,8,9])
        else:
            value=int(self.get_cell_value(cell))
            mySet=set([])
            mySet.add(value)
            return mySet

    #--------------------------------------------------------------------
    # Function:     get_cell_value()
    # Objection:    get solved cell's value
    # Input:        cell (i,j)
    # Output:       int value
    def get_cell_value(self,cell):
        x=cell[0]
        y=cell[1]
        return self.map[str(x)][y/3][y%3]


    #--------------------------------------------------------------------
    # Function:     remove_inconsistent_values(cell1,cell2)
    # Objection:    check whether they are violated, if so modify the first input
    # Input:        cell1, cell2
    # Output:       ?
    def remove_inconsistent_values(self, cell1, cell2):

        cell2_values=list(self.get_values(cell2))
        if len(cell2_values)==1:
            curr_values=self.possible_values_table[cell1[0]][cell1[1]]
            if cell2_values[0] in curr_values:
                if (len(list(curr_values))>1):
                    self.possible_values_table[cell1[0]][cell1[1]].remove(cell2_values[0])
                    return True
        return False

    #--------------------------------------------------------------------
    # Function:     get_neighbors(cell)
    # Objection:    get all neighbors (who has constraint relationship with the given cell
    # Input:        cell
    # Output:       list of neighbor
    def get_neighbors(self,cell):
        neighbors=self.get_col_neighbor(cell)
        neighbors+=self.get_row_neighbor(cell)
        neighbors+=self.get_block_neighbors(cell)

        return neighbors

    #--------------------------------------------------------------------
    # Function:     get_row_neighbors(cell)
    # Objection:    get all neighbors (who has constraint relationship with the given cell) in row
    # Input:        cell
    # Output:       list of neighbor
    def get_row_neighbor(self,cell):
        neighbors=[]
        x=cell[0]
        y=cell[1]
        for i in range(9):
            if (i,y) not in set(neighbors):
                neighbors.append((i,y))
        neighbors.remove(cell)
        return neighbors

    #--------------------------------------------------------------------
    # Function:     get_col_neighbors(cell)
    # Objection:    get all neighbors (who has constraint relationship with the given cell) in col
    # Input:        cell
    # Output:       list of neighbor
    def get_col_neighbor(self,cell):
        neighbors=[]
        x=cell[0]
        y=cell[1]
        for i in range(9):
            if (x,i) not in set(neighbors):
                neighbors.append((x,i))
        neighbors.remove(cell)
        return neighbors

    #--------------------------------------------------------------------
    # Function:     get_block_neighbors(cell)
    # Objection:    get all neighbors (who has constraint relationship with the given cell) in block
    # Input:        cell
    # Output:       list of neighbor
    def get_block_neighbors(self,cell):
        neighbors=[]
        x=cell[0]
        y=cell[1]
        for i in range((x/3)*3,(x/3)*3+3):
            for j in range((y/3)*3,(y/3)*3+3):
                if(i,j) not in set(neighbors):
                    neighbors.append((i,j))
        neighbors.remove(cell)
        return neighbors

    def get_undetermined_pairs(self):
        list=set([])
        for cell in self.get_undetermined_cells():
            for neighbors in self.get_neighbors(cell):
                if self.is_solved(neighbors):
                    list.add((cell,neighbors))
        return list
    #--------------------------------------------------------------------
    # Function:     infer_ac3()
    # Objection:    solve soduku by ac3 algorithm, try to minimize the possible
    #                   values for each cell
    # Input:        -
    # Output:       ?
    def infer_ac3(self):
        if self.is_solved_all():
            return
        st=time.time()
        print "infer_ac(): start"
        # Initialize the arcs queue
        myQueue=[i for i in self.get_undetermined_pairs()]
        #for item in sudoku_arcs():
        #    myQueue.append(item)

        while(len(myQueue)!=0):
            curr=myQueue.pop(0)
            #if not self.is_solved(curr[0]) and self.is_solved(curr[1]):

            if self.remove_inconsistent_values(curr[0],curr[1]) and self.is_solved(curr[0]):
                for neighbor in self.get_neighbors(curr[0]):
                    if not self.is_solved(neighbor):
                        myQueue.append((neighbor,curr[0]))
        #print "infer_ac(): end"
        print "Time - infer_ac3():", time.time()-st
    #--------------------------------------------------------------------
    # Function:     get_undetermined_cells()
    # Objection:    get a list of all currently unsolved cells
    # Input:        -
    # Output:       List of unsolved cells
    def get_undetermined_cells(self):
        undetermined=[]
        for i in range(9):
            for j in range(9):
                if len(list(self.get_values((i,j))))>1:
                    undetermined.append((i,j))
        return undetermined

    #--------------------------------------------------------------------
    # Function:     infer_improved()
    # Objection:    To solve the sudoku
    # Input:        -
    # Output:       ?
    def infer_improved(self):
        st=time.time()
        # arc constraint
        self.infer_ac3()
        if self.is_solved_all():
            return

        undetermined=self.get_undetermined_cells()

        while (len(undetermined)!=0):
            get_done=False
            cell=undetermined.pop(0)
            if not get_done:
                myList=[i for i in list(self.get_values(cell))]
                for neighbor in self.get_block_neighbors(cell):
                    for potential in list(self.get_values(neighbor)):
                        if potential in set(myList):
                            myList.remove(potential)
                if len(myList)==1:
                    self.possible_values_table[cell[0]][cell[1]]=set(myList)
                    #print cell, myList, "block"
                    get_done=True

            if not get_done:
                myList=[i for i in list(self.get_values(cell))]
                for neighbor in self.get_row_neighbor(cell):
                    for potential in list(self.get_values(neighbor)):
                        if potential in set(myList):
                            myList.remove(potential)
                if len(myList)==1:
                    self.possible_values_table[cell[0]][cell[1]]=set(myList)
                    #print cell, myList, "col"
                    get_done=True

            if not get_done:
                myList=[i for i in list(self.get_values(cell))]
                for neighbor in self.get_col_neighbor(cell):
                    for potential in list(self.get_values(neighbor)):
                        if potential in set(myList):
                            myList.remove(potential)
                if len(myList)==1:
                    self.possible_values_table[cell[0]][cell[1]]=set(myList)
                    #print cell, myList, "row"
                    get_done=True

            if get_done:
                undetermined=self.get_undetermined_cells()

        self.infer_ac3()
        print "time-improved: ",time.time()-st
    def check(self):
        if not self.is_solved_all():
            return False
        for arc in sudoku_arcs():
            if self.get_values(arc[0])==self.get_values(arc[1]):
                print arc
                return False
        return True


    #--------------------------------------------------------------------
    # Function:     infer_with_guessing()
    # Objection:    To solve the sudoku by guessing undetermined value until all solved
    # Input:        -
    # Output:       ?
    def infer_with_guessing(self):
        st_time=time.time()
        self.infer_improved()
        print "infer_with_guessing(): start"

        undetermined=self.get_undetermined_cells()
        while len(undetermined)!=0:
        #    print "undetermined set: ",undetermined
            curr=undetermined.pop()
            st=time.time()
            self.guessing(curr)

            undetermined=self.get_undetermined_cells()
        #print "infer_with_guessing(): end"
        print "time - guessing: ",time.time()-st_time

    #--------------------------------------------------------------------
    # Function:     guessing(cell)
    # Objection:    guessing value for the Sudoku, start at giving cell
    # Input:        cell (i,j)
    # Output:       ?
    def guessing(self,cell):

        curr_potential_list=list(self.get_values(cell))
        possible_table=self.values_table_copy()

        for potential in curr_potential_list:
            flag_solved=True
            self.possible_values_table[cell[0]][cell[1]]=set([potential])
            if not self.is_wrong_guessing(cell):


                for neighbors in self.get_neighbors(cell):
                    if not self.is_solved(neighbors):
                        if (not self.guessing(neighbors)):
                            flag_solved=False;
                            break;
                if flag_solved:
                    return True

        # if current guess lead to an unsolvable map, set back value of cell to its orignial value list
        self.possible_values_table[cell[0]][cell[1]]=set(curr_potential_list)
        return False


    def values_table_copy(self):
        return [[set([ item for item in list(self.get_values((i,j)))]) for j in range(9)] for i in range(9)]

    #--------------------------------------------------------------------
    # Function:     is_wrong_guessing(cell)
    # Objection:    check whether the current guess of a cell is wrong ->violate to any constraint
    # Input:        cell (i,j)
    # Output:       True if wrong
    def is_wrong_guessing(self,cell):
        for neighbor in self.get_neighbors(cell):
            if self.is_solved(neighbor):
                if self.get_values(cell)==self.get_values(neighbor):
                    return True
        return False

    #--------------------------------------------------------------------
    # Function:     is_solved_all()
    # Objection:    check whether the sudoku stored in object is solved
    #                   *solved: all cell have single solutions
    # Input:        -
    # Output:       True if solved
    def is_solved_all(self):
        for i in range(9):
            for j in range(9):
                if len(list(self.possible_values_table[i][j]))!=1:
                    return False
        return True

    #--------------------------------------------------------------------
    # Function:     is_solved(cell)
    # Objection:    check whether a single cell in sudoku stored in object is solved
    #                   *solved: all cell have single solutions
    # Input:        cell (i,j)
    # Output:       True if solved
    def is_solved(self,cell):
        if len(list(self.possible_values_table[cell[0]][cell[1]]))==1:
            return True
        return False

    #--------------------------------------------------------------------
    # Function:     get_solution
    # Objection:    to get the solution if solved
    # Input:        self
    # Output:       solution as 2D array if solved, None if not
    def get_solution(self):
        if not self.is_solved_all():
            print "Not solved yet!"
            return None
        return [list(list(self.possible_values_table[i][j])[0] for j in range(9))for i in range(9)]

