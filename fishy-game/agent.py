from game_class import Game
import numpy as np


def get_episodes(num_episodes, max_episode_length):
    episodes = []
    for e in range(num_episodes):
        game = Game()
        states = []
        rewards = []
        for i in range(max_episode_length):
            # Select random action
            action = np.random.randint(0, 4)
            state, reward, done = game.on_update(action)
            states.append(state)
            rewards.append(reward)
            if(done):
                break
    episodes.append((states, rewards))
    return episodes


print(get_episodes(3, 5000))
