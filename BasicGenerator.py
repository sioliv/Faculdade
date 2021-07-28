import math
import random

from BasicIcon import BasicIcon
from IGenerator import IGenerator


class BasicGenerator(IGenerator):

    def __init__(self, numtypes, seed=None):

        self.__numtypes = numtypes

    def getJewelTypes(self):
        return self.__numtypes

    def generate(self):
        generate = BasicIcon(math.floor(random.randint(0, self.__numtypes)))
        return generate

    def initialize(self, grid, randIcons=True):
        pattern = False
        icon1 = 0
        icon2 = 1

        for i in range(len(grid)):
            pattern = not pattern

            if pattern is False:
                icon1 = icon1 + 1
                n = self.getJewelTypes()

                icon1 = icon1 % n
                if icon1 == icon2:
                    icon1 = (icon2 + 1) % n
                icon2 = (icon1 + 1) % n
                if icon1 == icon2:
                    icon2 = (icon1 + 1) % n

            for j in range(len(grid[0])):
                if randIcons is False:
                    grid[i][j] = BasicIcon(icon1 if pattern else icon2)

                else:
                    grid[i][j] = self.generate()

                pattern = not pattern
