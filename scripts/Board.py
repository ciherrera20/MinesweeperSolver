import numpy as np
import random

class Board:
    HIDDEN = "?"
    MINE = "X"
    FLAGGED = "F"

    def __init__(self, rows, cols, numMines, seed = None):
        self.rows = rows
        self.cols = cols
        self.numMines = min(numMines, rows * cols)

        # 2D array of 1s or 0s. 1s correspond to mines, 0s correspond to open spaces
        self.board = np.zeros((rows, cols))

        # 2D array of integers, where each integer is the number of mines surrounding the cell
        self.mines = np.zeros((rows, cols))

        # 2D array of 1s or 0s. 1s correspond to a cell that has been clicked and 0s correspond to a cell that is hidden
        self.clicked = np.zeros((rows, cols))

        # 2D array of 1s or 0s. 1s correspond to a cell that has been flagged and 0s correspond to a cell that is not flagged
        self.flagged = np.zeros((rows, cols))

        # Seed the random generator, then add mines
        if seed is not None:
            np.random.seed(seed)
        i = 0
        while i < numMines:
            row = np.random.randint(1, self.rows)
            col = np.random.randint(1, self.cols)
            if not self.isMine(row, col):
                self.addMine(row, col)
                i += 1

    def addMine(self, row, col):
        """
        Set the given cell to a mine and update the neighbors array
        """
        if not self.isMine(row, col):
            self.board[row, col] = 1
            # Update neighbors array
            for neighborRow, neighborCol in self.getNeighbors(row, col):
                self.mines[neighborRow, neighborCol] += 1

    def computeNeighbors(self, row, col):
        """
        Compute all of the entries in the neighbors array
        """
        self.mines = np.zeros((self.rows, self.cols))
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if self.isMine(row, col):
                    self.board[row, col] = 0
                    self.addMine(row, col)

    def getNeighbors(self, row, col):
        """
        Return a list of tuples that are the rows and columns of neighboring cells, taking into account the edges of the board
        """
        neighbors = []
        for deltaRow in range(-1, 2):
            for deltaCol in range(-1, 2):
                if not (deltaRow == 0 and deltaCol == 0) and self.inBoard(row + deltaRow, col + deltaCol):
                    neighbors += [(row + deltaRow, col + deltaCol)]
        return neighbors

    def inBoard(self, row, col):
        """
        Whether or not the given cell is in the board
        """
        return 0 <= row < self.rows and 0 <= col < self.cols

    def isMine(self, row, col):
        """
        Whether or not the given cell is a mine
        """
        return self.board[row, col] == 1
    
    def isClicked(self, row, col):
        """
        Whether or not a cell is clicked
        """
        return self.clicked[row, col] == 1

    def isFlagged(self, row, col):
        """
        Whether or not a cell is flagged
        """
        return self.flagged[row, col] == 1

    def getMines(self, row, col):
        """
        Return the number of surrounding mines in the given cell
        """
        return self.mines[row, col]

    def clickCell(self, row, col):
        """
        Set a cell to have been clicked
        """
        self.clicked[row, col] = 1

    def flagCell(self, row, col):
        """
        Set a cell to have been flagged
        """
        self.flagged[row, col] = 1

    def isGameOver(self):
        """
        Checks whether the game is over by checking if any mines have been clicked
        """
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                if self.isMine(row, col) and self.isClicked(row, col):
                    return True
        return False

    def getSurroundingMines(self, row, col):
        return self.mines[row, col]

    def __repr__(self):
        """
        Returns a string representation
        """
        s = ''
        nums = (self.mines + 1) * self.clicked
        for row in range(0, self.rows):
            for col in range(0, self.cols):
                num = nums[row, col]
                if self.isFlagged(row, col):
                    s += str(Board.FLAGGED) + ' '
                elif num == 0:
                    s += str(Board.HIDDEN) + ' '
                else:
                    if self.isMine(row, col):
                        s += str(Board.MINE) + ' '
                    else:
                        s += str(int(num - 1)) + ' '
            s += '\n'
        return s