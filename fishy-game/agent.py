from game_class import run, GameWindow
from arcade.application import Window
import pyglet
import arcade
import time
import threading

for i in range(10):
    window = GameWindow(960, 540)
    arcade.set_window(window)
    #print(arcade.get_window())
    window.dispatch_events()
    arcade.run()