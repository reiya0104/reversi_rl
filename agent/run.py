"""Quick manual play loop for smoke‑testing the environment."""
from __future__ import annotations

import numpy as np

from agent.env import ReversiEnv

if __name__ == "__main__":
    env = ReversiEnv()
    obs, _ = env.reset()
    done: bool = False
    while not done:
        env.render()
        legal_moves = [i for i in range(64) if obs[i] == 0]
        action = np.random.choice(legal_moves + [64])  # random with occasional pass
        obs, reward, done, _, _ = env.step(int(action))
    env.render()
    print("Game finished with reward", reward)
