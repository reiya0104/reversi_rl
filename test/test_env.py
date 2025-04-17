"""Smoke tests for the Gym environment."""
from __future__ import annotations

import numpy as np

from agent.env import ReversiEnv


def test_reset_and_step():
    env = ReversiEnv(seed=1)
    obs, _ = env.reset()
    assert obs.shape == (65,)
    # take a random legal move or pass
    action = np.random.randint(0, 65)
    obs, reward, terminated, _, _ = env.step(int(action))
    assert obs.shape == (65,)
    assert isinstance(reward, int)
    assert isinstance(terminated, bool)
