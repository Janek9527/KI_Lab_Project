from game_class import GameWindow
from arcade.application import Window
import pyglet
import arcade
import time
import numpy as np
import torch
import torch.nn as nn
from torch import optim
import random
import numpy
import math
from collections import namedtuple, deque
from itertools import count
import torch.nn.functional as F

window = GameWindow(960, 540)
arcade.set_window(window)
#print(arcade.get_window())
window.dispatch_events()
arcade.run()
