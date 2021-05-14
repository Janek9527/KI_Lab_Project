from game_constents import min_computer_fish_size, max_computer_fish_size, min_computer_fish_speed, max_computer_fish_speed, player_win_size, player_start_size
from game_sprite_buttons import TextureButton
import arcade
import arcade.gui

from modifications_to_python_arcade.gui_manager import ModifiedUIManager
from modifications_to_python_arcade.resizeable_window import ResizeableWindow

from arcade.gui.ui_style import UIStyle
from arcade.application import Window
import fish
from controls import PlayerControlsObject
from fish_generator import RandomFishGenerator, FishGenerator
import time
import pickle
import os
from game_sprite_buttons import RestartGameButton, ContinueGameButton, YouWinPoster, ViewHighScoresButton, YouLosePoster
import resources
import numpy as np

GL_NEAREST = 9728  # open_gl scaling filter key for nearest neighbor
SCREEN_TITLE = "Fishy Game"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

all_deltatimes = []
key_dict = {65362: 'UP', 65364: 'DOWN', 65361: 'LEFT', 65363: 'RIGHT'}
num_of_high_scores = 5


class GameWindow(arcade.Window):
    fish_sprites: arcade.SpriteList
    ui_manager: ModifiedUIManager
    player_fish: fish.PlayerFish
    paused: bool
    episode: list

    # buttons def
    restart_button_game_lost: RestartGameButton
    continue_button_paused: ContinueGameButton
    continue_button_game_lost: ContinueGameButton
    you_win_poster: YouWinPoster
    you_lose_poster: YouLosePoster
    view_high_scores_button: ViewHighScoresButton

    time_played: float

    controls_handler: PlayerControlsObject

    fish_generator: FishGenerator

    b_did_win_already: bool
    FLAG_open_high_scores_menue: int

    max_fish: int
    allowed_keys: list

    @property
    def height(self):
        return SCREEN_HEIGHT

    @property
    def width(self):
        return SCREEN_WIDTH

    def __init__(self, width, height):
        super().__init__(width, height, SCREEN_TITLE)
        self.max_fish = 0
        self.allowed_keys = [arcade.key.UP, arcade.key.DOWN,
                             arcade.key.LEFT, arcade.key.RIGHT]
        self.episode = []
        # self.on_resize()
        self.restart_game()

    def restart_game(self):
        """ Set up the game variables. Call to re-start the game. """
        # Create your sprites and sprite lists here

        # set up buttons

        self.background_texture = resources.background_texture_map["idle"]

        self.fish_sprites = arcade.SpriteList()
        self.ui_manager = ModifiedUIManager()
        self.player_fish = fish.PlayerFish(self)
        self.fish_generator = RandomFishGenerator(1.1, self, min_fish_size=min_computer_fish_size, max_fish_size=max_computer_fish_size,
                                                  min_fish_speed=min_computer_fish_speed, max_fish_speed=max_computer_fish_speed)
        self.fish_sprites.append(self.player_fish)
        self.paused = False
        self.controls_handler = PlayerControlsObject(change_player_direction=self.player_fish.change_movement_direction,
                                                     reset_game=self.restart_game, pause_game=self.toggle_game_paused)

        self.restart_button_game_lost = RestartGameButton(self, False)
        self.restart_button_game_won = self.restart_button_game_lost
        self.ui_manager.add_ui_element(self.restart_button_game_won)

        self.continue_button_paused = ContinueGameButton(self, False)
        self.ui_manager.add_ui_element(self.continue_button_paused)

        self.you_win_poster = YouWinPoster(self, False)
        self.you_win_poster.center_y += self.restart_button_game_won.height / \
            2 + self.you_win_poster.height/2 + 10
        self.ui_manager.add_ui_element(self.you_win_poster)

        self.you_lose_poster = YouLosePoster(self, False)
        self.you_lose_poster.center_y = self.restart_button_game_lost.top + \
            self.you_win_poster.height / 2 + 10
        self.ui_manager.add_ui_element(self.you_lose_poster)

        self.continue_button_game_won = ContinueGameButton(self, False)
        self.continue_button_game_won.center_y += -self.restart_button_game_won.height / \
            2 - self.continue_button_game_won.height / 2 - 10
        self.ui_manager.add_ui_element(self.continue_button_game_won)

        self.view_high_scores_button = ViewHighScoresButton(self, True)
        self.view_high_scores_button.center_x = arcade.get_window().width - \
            self.view_high_scores_button.width/2 - 20
        self.view_high_scores_button.center_y = self.view_high_scores_button.height / 2 + 20
        self.ui_manager.add_ui_element(self.view_high_scores_button)

        self.time_played = 0
        self.b_did_win_already = False

        self.FLAG_open_high_scores_menue = -1

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()

        left, right, bottom, top = arcade.get_window().get_viewport()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            right, top,
                                            self.background_texture)
        self.fish_sprites.draw(filter=GL_NEAREST)

        self.ui_manager.on_draw()

        # draw time
        arcade.draw_text("time: {:.0f}".format(self.time_played), 20, self.height - 40, color=(
            255, 240, 200, 210), font_size=25, bold=True, anchor_y="bottom", font_name="ariblk")

        # draw score (only wen game is lost)
        arcade.draw_text("score: {:.0f}%".format((self.player_fish.size - player_start_size)/(player_win_size-player_start_size)*100), 20, self.height - 40,
                         color=(255, 240, 200, 210), font_size=25, bold=True, anchor_y="top", font_name="ariblk")

    last_time = None

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        Normally, you'll call update() on the sprite lists that
        need it.
        """

        previous_fish_size = self.player_fish.size

        # Select random action
        action = np.random.choice(self.allowed_keys)

        # Print selected key
        print(f'Selected key {key_dict[action]}')

        # Execute selected action
        self.controls_handler.on_keyboard_press(action, None)

        # calculate delta_time
        if self.last_time is not None:
            delta_time = time.time() - self.last_time
        self.last_time = time.time()

        delta_time = 1.0/60.0
        # print(delta_time)
        # time.sleep(0.5)

        if not self.is_game_lost and not self.b_did_win_already and not self.paused:
            self.time_played += delta_time

        # update game
        if not self.paused:
            self.fish_sprites.on_update(delta_time)
            self.fish_generator.update(delta_time)
            self.max_fish = len(self.fish_sprites) if len(
                self.fish_sprites) > self.max_fish else self.max_fish
            # print("max number of fish", self.max_fish)
            # for sprite in self.fish_sprites:
            # print("velo", sprite.velocity)
            # print("size", sprite.size)
            # print("pos", sprite.position)
            all_deltatimes.append(delta_time)

        if self.FLAG_open_high_scores_menue == 0:
            self.FLAG_open_high_scores_menue = -1
        elif self.FLAG_open_high_scores_menue > 0:
            self.FLAG_open_high_scores_menue -= 1

        # Read state
        fishes = []
        for index, fish in enumerate(self.fish_sprites):
            fishes.append([fish.velocity[0], fish.velocity[1],
                           fish.position[0], fish.position[1], fish.size])

        for i in range(len(fishes), 15):
            fishes.append([0, 0, 0, 0, 0])

        state = np.array(fishes)
        #print(f'End velocity {self.player_fish.velocity}')

        # Read reward
        reward = self.player_fish.size - previous_fish_size

        self.episode.append((action, state, reward))

        if self.b_did_win_already or self.is_game_lost:
            arcade.close_window()

    @property
    def is_game_lost(self):
        return not self.player_fish in self.fish_sprites

    def unpause(self):
        self.paused = False
        self.continue_button_paused.is_visible = False
        self.you_win_poster.is_visible = False
        self.restart_button_game_won.is_visible = False
        self.continue_button_game_won.is_visible = False

    def toggle_game_paused(self):
        if not self.is_game_lost:
            if self.paused:
                self.unpause()
            else:
                self.paused = True
                self.continue_button_paused.is_visible = True

        else:
            self.restart_game()

    def handle_game_lost(self):
        self.restart_button_game_lost.is_visible = True
        self.you_lose_poster.is_visible = True

    def handle_game_won(self):
        if not self.b_did_win_already:
            self.you_win_poster.is_visible = True
            self.continue_button_game_won.is_visible = True
            self.restart_button_game_won.is_visible = True
            self.b_did_win_already = True

    def on_close(self):
        arcade.get_window().on_close()

    def on_show_view(self):
        self.last_time = time.time()
        self.controls_handler.reset_state()

    def on_resize(self, width: float = 0, height: float = 0):
        pass
        # ratio = self.height/self.width
        # arcade.get_window().height = int(arcade.get_window().width*ratio)
        # return False

        # UI
    def on_key_press(self, key, key_modifiers):
        """
        Called whenever a key on the keyboard is pressed.

        For a full list of keys, see:
        http://arcade.academy/arcade.key.html
        """
        self.controls_handler.on_keyboard_press(key, key_modifiers)

    def on_key_release(self, key, key_modifiers):
        """
        Called whenever the user lets off a previously pressed key.
        """
        self.controls_handler.on_keyboard_release(key, key_modifiers)

    def on_mouse_motion(self, *args, **kwargs):
        self.ui_manager.on_mouse_motion(*args, **kwargs)

    def on_mouse_press(self, *args, **kwargs):
        self.ui_manager.on_mouse_press(*args, **kwargs)

    def on_mouse_release(self, *args, **kwargs):
        self.ui_manager.on_mouse_release(*args, **kwargs)


def run():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    arcade.set_window(window)
    window.dispatch_events()
    arcade.run()
    return window.episode
