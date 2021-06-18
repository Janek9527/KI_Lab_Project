from constants import min_computer_fish_size, max_computer_fish_size, min_computer_fish_speed, max_computer_fish_speed, player_win_size, player_start_size
import arcade

import fish
from controls import PlayerControlsObject
from fish_generator import RandomFishGenerator, FishGenerator
import time
import numpy as np

SCREEN_TITLE = "Fishy Game"
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540

all_deltatimes = []
key_keyname_dict = {65362: 'UP', 65364: 'DOWN', 65361: 'LEFT', 65363: 'RIGHT'}
action_key_dict = {0: 65362, 1: 65364, 2: 65361, 3: 65363}
num_of_high_scores = 5


class Game():
    fish_sprites: arcade.SpriteList
    player_fish: fish.PlayerFish
    paused: bool
    episode: list

    time_played: float

    controls_handler: PlayerControlsObject

    fish_generator: FishGenerator

    b_did_win_already: bool
    FLAG_open_high_scores_menue: int

    max_fish: int
    allowed_keys: list

    last_time = None

    @property
    def height(self):
        return SCREEN_HEIGHT

    @property
    def width(self):
        return SCREEN_WIDTH

    def __init__(self):
        self.max_fish = 0
        self.allowed_keys = [arcade.key.UP, arcade.key.DOWN,
                             arcade.key.LEFT, arcade.key.RIGHT]
        self.episode = []
        self.restart_game()

    def restart_game(self):
        self.fish_sprites = arcade.SpriteList()
        self.player_fish = fish.PlayerFish(self)
        self.fish_generator = RandomFishGenerator(1.1, self, min_fish_size=min_computer_fish_size, max_fish_size=max_computer_fish_size,
                                                  min_fish_speed=min_computer_fish_speed, max_fish_speed=max_computer_fish_speed)
        self.fish_sprites.append(self.player_fish)
        self.paused = False
        self.controls_handler = PlayerControlsObject(change_player_direction=self.player_fish.change_movement_direction,
                                                     reset_game=self.restart_game)

        self.time_played = 0
        self.b_did_win_already = False

        self.FLAG_open_high_scores_menue = -1

    def on_update(self, action):
        delta_time = 1.0/10.0
        previous_fish_size = self.player_fish.size

        key = action_key_dict[action]
        keyname = key_keyname_dict[key]
        # Print selected key
        # print(f'Selected key {keyname}')

        # Execute selected action
        self.controls_handler.on_keyboard_press(key, None)

        # calculate delta_time
        if self.last_time is not None:
            delta_time = time.time() - self.last_time
        self.last_time = time.time()

        delta_time = 1.0/10.0
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
        if self.is_game_lost:
            reward = -1000
        else:
            pos_reward = 0
            neg_reward = 0
            smaller_fishes = list(filter(lambda x: x.size < self.player_fish.size, self.fish_sprites[1:]))
            bigger_fishes = list(filter(lambda x: x.size >= self.player_fish.size, self.fish_sprites[1:]))

            target_fish = sorted(smaller_fishes, key=lambda x: x.current_distance)
            if len(target_fish) > 0 and target_fish[0].better_distance:
                pos_reward = 10

            dangerous_bigger_fish = list(filter(lambda x:x.current_distance < 100 * x.size, bigger_fishes))

            if len(dangerous_bigger_fish) > 0:
                neg_reward = -20

            if (self.player_fish.size - previous_fish_size) > 0:
                pos_reward += 100

            reward = pos_reward + neg_reward
        #print(reward)
        # print((action, state, reward))

        self.episode.append((action, state, reward))

        if self.b_did_win_already or self.is_game_lost:
            return state, reward, True    # game ended

        return state, reward, False  # game not ended

    @property
    def is_game_lost(self):
        return not self.player_fish in self.fish_sprites

    def handle_game_won(self):
        if not self.b_did_win_already:
            self.b_did_win_already = True
