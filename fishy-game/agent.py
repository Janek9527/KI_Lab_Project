from game_class import Game
import time


def get_episodes(num):
    game = Game()
    for i in range(5000):
        print(game.on_update(1.0/60.0))


get_episodes(1)
