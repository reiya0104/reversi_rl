import random
from typing import Any

import gymnasium as gym
import numpy as np
from reversi_rl import Board


class ReversiEnv(gym.Env):
    """Gymnasium‑compatible environment wrapping the Rust Board class."""

    metadata: dict[str, list[str]] = {"render_modes": ["human"]}

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.rng = random.Random(seed)
        self.board = Board()
        self.action_space = gym.spaces.Discrete(64 + 1)  # 64 squares + pass
        # observation: 64 ints (−1,0,1) + to_move (0/1)
        self.observation_space = gym.spaces.Box(
            low=-1, high=1, shape=(65,), dtype=np.int8
        )

    # ------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):  # type: ignore[override]
        if seed is not None:
            self.rng.seed(seed)
        self.board.reset()
        obs = np.array(self.board.as_list() + [1], dtype=np.int8)
        return obs, {}

    def step(self, action: int):  # type: ignore[override]
        legal = self.board.legal_moves()
        reward: int = 0
        terminated: bool = False
        if action != 64 and action in legal:
            self.board.play(action)  # may raise -> handled by gym
        else:  # pass or illegal (treated as pass)
            pass

        # opponent random move
        opp_moves = self.board.legal_moves()
        if opp_moves:
            self.board.play(self.rng.choice(opp_moves))
        else:
            # both players had to pass → game over
            terminated = True

        obs = np.array(
            self.board.as_list() + [1 if self.board.get_black_to_move() else -1],
            dtype=np.int8,
        )  # type: ignore[attr-defined]
        if terminated:
            black, white = self.board.counts()
            reward = 1 if black > white else -1 if black < white else 0
        return obs, reward, terminated, False, {}

    def render(self):  # type: ignore[override]
        symbols = {1: "●", -1: "○", 0: "."}
        for r in range(8):
            row = " ".join(symbols[self.board.as_list()[r * 8 + c]] for c in range(8))
            print(row)
        print()
