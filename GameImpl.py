#!/usr/bin/env python
# coding: UTF-8
#
## @package GameImpl
#
#  Game implementation.
#
#  Concrete implementation of the IGame interface. This implementation has the following behavior:
#  - Moves are allowed via the select() method for pairs of adjacent cells only. 
#    The cells must have different types. The move must create at least one run.
#  - A run is defined to be three or more adjacent cells of the same type, horizontally or vertically. 
#    A given cell may be part of a horizontal run or a vertical run at the same time.
#  - Points are awarded for runs based on their length. A run of length 3 is awarded BASE_SCORE points, 
#    and a run of length (3 + n) points gets @f$BASE\_SCORE \times 2^n@f$.
#
#  @author Paulo Roma
#  @since 12/04/2020
#
from Cell import Cell
from IGame import IGame
from IGenerator import IGenerator
from Icon import Icon
from BasicGenerator import BasicGenerator
import logging
import math
import numpy as np


##
# Concrete implementation of the IGame interface. This implementation
# has the following behavior:
# <ul>
#   <li> Moves are allowed via the select() method for pairs of adjacent cells
#        only.  The cells must have different types.  The move must create
#        at least one run.
#   <li> A run is defined to be three or more adjacent cells of the same
#        type, horizontally or vertically. A given cell may be part
#        of a horizontal run or a vertical run at the same time.
#   <li> Points are awarded for runs based on their length.  A run of length
#        3 is awarded BASE_SCORE points, and a run of length (3 + n)
#        points gets @f$BASE\_SCORE \times 2^n@f$.
# </ul>
#
class GameImpl(IGame):
    ##
    # Score awarded for a three-cell run.
    __BASE_SCORE = 10
    ## Turn debugging on or off.
    __DEBUG__ = False

    ##
    # Constructs a game with the given number of columns and rows
    # that will use the given <code>IGenerator</code> instance
    # to create new icons.
    #
    # @param width number of columns.
    # @param height number of rows.
    # @param generator generator for new icons.
    #
    def __init__(self, width, height, generator):

        self.__width = width
        self.__height = height
        ## The grid of icons for this game.
        self.__grid = [[None for y in range(width)] for x in range(height)]

        # Initialize the grid.
        generator.initialize(self.__grid, True)

        ## Current score of the game.
        self.__score = 0
        while len(self.findRuns(False)) > 0:
            self.removeAllRuns()

        ##Reset score.
        self.__score = 0

        ## Icon generator.
        self.__generator = generator

        # ...

    ## Remove all runs from the grid.

    def removeAllRuns(self):
        c = []
        rem = self.findRuns(True)
        c.append(rem)
        if len(rem) > 0:
            a = []
            b = []
            for i in range(0, self.__width):
                a = a + (self.collapseColumn(i))
                b = b + (self.fillColumn(i))

            c.append(a)
            c.append(b)

        if self.setDebug:
            print("Cells = ", self.toString(c))
            print("Score = %d", self.__score)

        return c

    ## Get the debugging state.
    @property
    def getDebug(self):
        return GameImpl.__DEBUG__

    ## Set the debugging state.
    @staticmethod
    def setDebug(deb):
        GameImpl.__DEBUG__ = deb

    ## Returns the Icon at the given location in the game grid.
    #
    # @param row row in the grid.
    # @param col column in the grid.
    # @return Icon at the given row and column
    #
    def getIcon(self, row, col):
        return self.__grid[row][col]

    ## Sets the Icon at the given location in the game grid.
    #
    # @param row row in the grid.
    # @param col column in the grid.
    # @param icon to be set in (row,col).
    #
    def setIcon(self, row, col, icon):
        icon = self.__grid[row][col]
        return icon

    ## Returns the number of columns in the game grid.
    #
    # @return the width of the grid.
    #
    def getWidth(self):
        return self.__width

    ## Returns the number of rows in the game grid.
    # the height of the grid.
    #
    # @return the height of the grid.
    #
    def getHeight(self):
        return self.__height

    ## Returns the current score.
    #
    # @return current score for the game.
    #
    def getScore(self):
        return self.__score

    ## Swap the icons contained in two cells.
    #
    #  @param cells array with two cells.
    #  @see swapIcons (self, i, j, k, l)
    #
    def swapCells(self, cells):
        self.swapIcons(cells[0].row(), cells[0].col(), cells[1].row(), cells[1].col())

    ## Swap the positions of two icons.
    #
    #  @param (i,j) first icon.
    #  @param (k,l) second icon.
    #
    def swapIcons(self, i, j, k, l):
        [self.__grid[i][j], self.__grid[k][l]] = [self.__grid[k][l], self.__grid[i][j]]

    ##
    # In this implementation, the only possible move is a swap
    # of two adjacent cells.  In order for move to be made, the
    # following must be True.
    # <ul>
    #   <li>The given array has length 2
    #   <li>The two given cell positions must be adjacent
    #   <li>The two given cell positions must have different icon types
    #   <li>Swapping the two icons must result in at least one run.
    # </ul>
    # If the conditions above are satisfied, the icons for the two
    # positions are exchanged and the method returns True otherwise,
    # the method returns False.  No other aspects of the game state
    # are modified.
    #
    # @param cells cells to select.
    # @return True if the selected cells were modified, False otherwise.
    #
    def select(self, cells):

        if self.setDebug:
            print("select")
            print("Cell 0 = %s", cells[0].toString())
            print("Cell 1 = %s", cells[1].toString())

        if (len(cells) == 2) and cells[0].isAdjacent(cells[1]) \
                and (not cells[0].getIcon()).__eq__(cells[1].getIcon()) \
                and cells[0].inGrid(self.getWidth(), self.getHeight()) \
                and cells[1].inGrid(self.getWidth(), self.getHeight()):
            self.swapCells(cells)
            validSelection = True
            if len(self.findRuns(False)) == 0:
                self.swapCells(cells)
                validSelection = False
        else:
            validSelection = False

        return validSelection

    ## Returns a list of all cells forming part of a vertical or horizontal run.
    # The list is in no particular order and may contain duplicates.
    # If the argument is False, no modification is made to the game state;
    # if the argument is True, grid locations for all cells in the list are
    # nulled, and the score is updated.
    #
    # @param doMarkAndUpdateScore if False, game state is not modified.
    # @return list of all cells forming runs, in the form:
    # @f$[c_1, c_2, c_3,...], \text{where } c_i = Cell(row_i, col_i, iconType_i)@f$
    #
    def findRuns(self, doMarkAndUpdateScore):

        c = []
        
        self.doMarkAndUpdateScore = False

    

        return c

    ##
    # Removes an element at index pos, in a given column col, from the grid.
    # All elements above the given position are shifted down, and the first
    # cell of the column is set to null.
    #
    # @param pos the position at which the element should be removed.
    # @param col column of pos.
    #
    def removeAndShiftUp(self, pos, col):
        for i in range(pos, 1, -1):
            self.setIcon(i, col, self.getIcon(i - 1, col))

        return self.setIcon(0, col, None)

    ##
    #  Collapses the icons in the given column of the current game grid
    #  such that all null positions, if any, are at the top of the column
    #  and non-null icons are moved toward the bottom (i.e., as if by gravity).
    #  The returned list contains Cells representing icons that were moved
    #  (if any) in their new locations. Moreover, each Cell's previousRow property
    #  returns the original location of the icon. The list is in no particular order.
    #
    #  @param col column to be collapsed.
    #  @return list of cells for moved icons, in the form:
    #  @f$[c_1, c_2, c_3,...], \text{where } c_i = Cell(row_i, col_i, iconType_i)@f$
    #
    def collapseColumn(self, col):
        ## Array that contains all the changed cells.

        c = []

        ## Get the last column index.

        i = self.getHeight() - 1

        ##Holds how many cells were removed to shift down the cells above it.

        j = 0

        ## Check i >= j, because every cell from 0 to j is null(the ones on the top).
        ## As such, there is no need to proceed.
        while i >= j:
            ##if the cell is not null
            if self.getIcon(i, col) is not None:
                ## create a changed cell, that was moved "j" rows
                a = Cell(i, col, self.getIcon(i, col))
                a.previousRow(i - j)
                ## check if a was moved, if so, add it to "c"
                if a.row() != a.previousRow():
                    c.append(a)

                ## move one position up in the column and continue
                i = i - 1
                continue

            ## If it is not on the first row,
            ## call "removeAndShiftUp", so the null cell goes to the top.
            if i != 0:
                self.removeAndShiftUp(i, col)

            ## Increase j,if the cell was null.
            if Cell is None:
                a = Cell(j, col, None)
                c.append(a)
                j = j + 1

        return c

    ## Fills the null locations (if any) at the top of the given column in the current game grid.
    # The returned list contains Cells representing new icons added to this column in their new locations.
    # The list is in no particular order.
    #
    # @param col column to be filled.
    # @return list of new cells for icons added to the column, in the form:
    # @f$[c_1, c_2, c_3,...], \text{where } c_i = Cell(row_i, col_i, iconType_i)@f$
    #
    def fillColumn(self, col):
        ## variable that contains all changed cell
        c = []
        n = 0

        ## for each row in column
        for i in range(self.getHeight() - 1, 0, -1):
            ## check if the icon is null, if so, generate a new random icon to fill the position
            if self.getIcon(i, col) is None:
                icon = self.__generator
                self.setIcon(i, col, icon)
                a = Cell(i, col, icon)
                a.previousRow(n - 1)
                c.append(a)

        if self.getDebug and len(c) > 0:
            print("\nfillColumn %s", col)
            print("Cells = " + self.toString(c))
            print("Grid = \n%s", self.__str__())

        return c

    ##
    # Returns a String representation of the grid for this game,
    # with rows delimited by newlines.
    #
    def __str__(self):
        sb = ""
        for row in range(self.getHeight()):
            for col in range(self.getWidth()):
                icon = self.getIcon(row, col)
                sb += "%s" % ("*" if icon is None else str(icon)).rjust(3, ' ')
            sb += "\n"
        return sb

    ## Return a string representation of the grid, with 8 symbols:
    # - 01234567
    # - '!@+*$%#.'
    def __repr__(self):
        sb = " ".join(list(map(str, range(self.getWidth())))) + "\n\n"
        for i in range(self.getHeight()):
            for j in range(self.getWidth()):
                sb += "!@+*$%#."[self.getIcon(i, j).getType() % 8] + " "
            sb += "  " + str(i) + "\n"
        return sb

    ##
    # Returns a String representation of a List of cells.
    #
    # @param lcells given list.
    # @return string with cells.
    #
    def toString(self, lcells):
        s = ""
        for c in lcells:
            s += str(c) + " "

        if lcells is True:
            s += "\n"
        return s
