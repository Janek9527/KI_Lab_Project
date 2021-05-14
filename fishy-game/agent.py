from game_class import run
from arcade.application import Window
import time


def get_episodes(num):
    game_in = Window(960, 540, "Fishy Game1")
    #game.maximize()
    run(game_in)
    time.sleep(3)
    game_in = Window(960, 540, "Fishy Game2")
    #game.maximize()
    run(game_in)
    #for i in range(num):

get_episodes(1)
