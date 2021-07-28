from BasicGenerator import BasicGenerator
from GameImpl import GameImpl


def main(args):
    gen = BasicGenerator(5)
    testGame = GameImpl(4, 4, gen)
    print(testGame)


main('args')
