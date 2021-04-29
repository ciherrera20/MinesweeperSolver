import numpy as np
import time
from Board import *

class Solver:
    def __init__(self, board):
        self.board = board

    def solveOne(self):
        # Click any zeros and all of its neighbors
        # Get list of squares: that touch non-clicked squaes and athe adjacent squares that have not been clicked
        start = time.time()
        squares = s.getSquares()
        end = time.time()
        print("Get squares", end - start)

        # Create augmented matrix
        start = time.time()
        augMatrix, coords = s.createAugmentedMatrix(*squares)
        end = time.time()
        print("Create augmented matrix", end - start)
        # print(squares)
        # print(augMatrix)
        # print(coords)

        # Row reduce
        start = time.time()
        reducedMatrix = s.reduce(augMatrix)
        end = time.time()
        print("Row reduce", end - start)
        # print(reducedMatrix)

        # Use special rule
        start = time.time()
        mines = s.specialRule(reducedMatrix)
        end = time.time()
        print("Special rule", end - start)
        # print(mines)

        # Click necessary squares
        start = time.time()
        numClicks = s.clickSquares(mines, coords)
        end = time.time()
        print("Click squares", end - start)
        # print(b)
        return numClicks
    
    def getSquares(self):
        """
        Returns a list of cells that are numbered and adjacent to an open, non-flagged cell
        """
        rows = self.board.rows
        cols = self.board.cols
        listNumSquares = []
        visited = {}
        
        count = 0
        for r in range(rows):
            for c in range(cols):
                # checks if current cell is clicked
                if self.board.isClicked(r, c):
                    added = False
                    for neighbor in self.board.getNeighbors(r, c):
                        neighborRow, neighborCol = neighbor
                        # checks if neighbor cell hasn't been clicked nor flagged
                        if not self.board.isClicked(neighborRow, neighborCol) and not self.board.isFlagged(neighborRow, neighborCol):
                            if not added:
                                listNumSquares += [(r, c)]
                                added = True
                            if neighbor not in visited:
                                visited[neighbor] = count
                                count += 1
        
        return (listNumSquares, visited, count)
    
    def createAugmentedMatrix(self, cells, unclickedDict, numUnclicked):
        """
        Create the augmented matrix and a list of coordinates from the list of numbered cells adjacent to at least one unclicked, unflagged cell
        """
        augRows = len(cells)
        augCols = numUnclicked
        augMatrix = np.zeros((augRows, augCols + 1))
        coords = {}

        for augRow in range(augRows):
            neighbors = self.board.getNeighbors(*cells[augRow])
            for neighbor in neighbors:
                if neighbor in unclickedDict:
                    augCol = unclickedDict[neighbor]
                    augMatrix[augRow, augCol] = 1
                    coords[augCol] = neighbor
            
            # Create augmented column
            augMatrix[augRow, -1] = self.board.getMines(*cells[augRow])
        return augMatrix, coords

    def reduce(self, matrix):
        """
        Convert matrix to reduced row echelon form
        """
        rows = len(matrix)
        cols = len(matrix[0])

        # Reducing to RREF can be broken into sub problems: reducing a single row and column, and then reducing the resulting sub matrix
        # Keep track of which column we are on
        col = 0

        # Loop through rows
        for row in range(rows):
            # Check if we have gone through all the columns
            if col >= cols:
                return matrix

            # Row of the left-most, then top-most non-zero entry
            lrow = row

            # Find the left-most, then top-most non-zero entry
            while matrix[lrow, col] == 0:
                # Increment row
                lrow += 1

                # If we reach the number of rows in the matrix, loop back around to row and increment col
                if lrow == rows:
                    lrow = row
                    col += 1
                
                    # Check if we have gone through all the columns
                    if col == cols:
                        return matrix

            # If the left-most, top-most non-zero entry is not in row, swap its row with row
            if lrow != row:
                temp = list(matrix[row])
                matrix[row] = matrix[lrow]
                matrix[lrow] = np.array(temp)
            
            # Cancel out entries in the column col in all rows except lrow
            for j in range(rows):
                if j != row:
                    if matrix[j, col] != 0:
                        matrix[j] = matrix[row, col] * matrix[j] - matrix[j, col] * matrix[row]

            # Increment col by 1, and move on to the next row
            col += 1
        return matrix

    def specialRule(self, matrix):
        """
        Applies Special Rule :)) 

        Handy chart:
                                | Coefficient is Positive   | Coefficient is Negative |
        Row meets lower bound   |        Not Mine           |           Mine          |
        Row meets upper bound   |          Mine             |         Not Mine        |
        Row meets neither bound |         Unsure            |          Unsure         |
        
        """
        # Remove all zero rows. Results in a pretty significant speedup
        matrix = matrix[np.all(matrix == 0, axis = 1) == False]

        # Loop through the matrices rows looking for equations that can be solved
        rows = len(matrix)
        if rows == 0:
            return np.array([])
        cols = len(matrix[0]) - 1
        mines = np.zeros(cols) - 1
        lead = 0
        for row in range(rows):
            # Compute the upper bound and lower bound, as well as the values of the cells needed to meet the upper bound,
            # and record the corresponding column numbers.
            upperbound = 0
            lowerbound = 0
            nonzeroCols = []
            nonzeroColsDict = {}
            vals = []
            for col in range(lead, cols):
                entry = matrix[row, col]
                if entry != 0:
                    if entry > 0:
                        upperbound += entry
                        vals.append(1)
                    elif entry < 0:
                        lowerbound += entry
                        vals.append(0)
                    if len(nonzeroCols) == 0:
                        lead = col
                    nonzeroCols.append(col)
                    nonzeroColsDict[col] = True
            vals = np.array(vals)

            # If the upperbound or lowerbound are not met, we can't say anything about the cell
            # Otherwise, we can reduce the matrix further and recursively compute the values of cells
            if len(vals) != 0 and (upperbound == matrix[row, -1] or lowerbound == matrix[row, -1]):
                # Flip 0s and 1s if the lower bound is met
                if lowerbound == matrix[row, -1]:
                    vals = 1 + vals * -1
                
                # Extract columns with nonzero entries in this row from A
                C = np.array([matrix[:, i] for i in nonzeroCols]).T

                # Reduce the matrix by removing columns of the cells whose values we just found and adjusting the last column
                reducedMatrix = np.array([matrix[:, i] for i in range(cols + 1) if i not in nonzeroColsDict]).T
                reducedMatrix[:, -1] = reducedMatrix[:, -1] -  C @ vals

                # Recursively compute the values of the other cells and insert them into the array of values
                newMines = self.specialRule(reducedMatrix)
                j = k = 0
                for i in range(cols):
                    if i in nonzeroColsDict:
                        mines[i] = vals[k]
                        k += 1
                    else:
                        mines[i] = newMines[j]
                        j += 1
                break
        return mines
    
    def clickSquares(self, mines, coords):
        """
        generates list of clicks that should be made: 
        flagging known mines and clicking known empty squares.
        everything else should be left alone.
        """
        numClicks = 0
        for x in range(len(mines)):
            # bomb so add corresponding coords to list of cells to flag
            if mines[x] == 1:
                self.board.flagCell(*coords[x])
            # not a bomb so add corresponding coords to list of cells to click
            elif mines[x] == 0:
                self.board.clickCell(*coords[x])
                numClicks += 1
        return numClicks

    def solve(self):
        # while (solveOne):
        #     pass
        pass


if __name__ == "__main__":
    # s = Solver(Board(100, 100, 12))
    # a = np.array([
    #     [1, 1, 0, 0, 0, 1],
    #     [1, 1, 1, 0, 0, 2],
    #     [0, 1, 1, 1, 0, 2],
    #     [0, 0, 1, 1, 1, 2],
    #     [0, 0, 0, 1, 1, 1]
    # ])
    # a = np.array([
    #     [4, 10, 8],
    #     [10, 150, -5],
    # ])
    # print(a)
    # print(s.reduce(a))

    # Set up test board
    # b = Board(5, 2, 0)
    # b.addMine(0, 0)
    # b.addMine(1, 0)
    # b.addMine(2, 0)
    # b.addMine(3, 0)
    # b.addMine(4, 0)
    # for i in range(0, 5):
    #     b.clickCell(i, 1)

    b = Board(99, 99, 0)
    b.clickCell(49, 49)
    print(b)

    s = Solver(b)
    s.solveOne()