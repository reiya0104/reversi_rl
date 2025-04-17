import random
from typing import Any

import gymnasium as gym
import numpy as np
import tkinter as tk
from tkinter import Canvas

from reversi_rl import Board

class ReversiEnv(gym.Env):
    """Gymnasium environment for Reversi with an optional Tkinter GUI.

    The GUI is created lazily when `render()` is called in "human" mode.
    Clicking on a square issues the corresponding action and triggers the
    environment's `step`, so you can play against the built‑in random opponent.
    """

    metadata: dict[str, list[str]] = {"render_modes": ["human"]}

    def __init__(self, seed: int | None = None):
        super().__init__()
        self.rng = random.Random(seed)
        self.board = Board()
        self.action_space = gym.spaces.Discrete(64 + 1)  # 64 squares + pass
        self.observation_space = gym.spaces.Box(low=-1, high=1, shape=(65,), dtype=np.int8)

        # GUI elements (created on demand)
        self._tk: tk.Tk | None = None
        self._canvas: Canvas | None = None
        self._cell_size: int = 60
        self._terminated: bool = False

    # ------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):  # type: ignore[override]
        if seed is not None:
            self.rng.seed(seed)
        self.board.reset()
        self._terminated = False
        if self._canvas is not None:
            self._draw_board()  # refresh GUI if it exists
        obs = np.array(self.board.as_list() + [1], dtype=np.int8)
        return obs, {}

    def step(self, action: int):  # type: ignore[override]
        legal = self.board.legal_moves()
        reward: int = 0
        self._terminated = False
        if action != 64 and action in legal:
            self.board.play(action)
        # random opponent
        opp_moves = self.board.legal_moves()
        if opp_moves:
            self.board.play(self.rng.choice(opp_moves))
        else:
            # both players passed
            self._terminated = True

        obs = np.array(
            self.board.as_list() + [1 if self.board.get_black_to_move() else -1],
            dtype=np.int8,
        )
        if self._terminated:
            black, white = self.board.counts()
            reward = 1 if black > white else -1 if black < white else 0
        if self._canvas is not None:
            self._draw_board()
        return obs, reward, self._terminated, False, {}

    # -------------------------- GUI helpers ---------------------------
    def _ensure_gui(self) -> None:
        if self._tk is not None:
            return
        self._tk = tk.Tk()
        self._tk.title("Reversi RL")
        px = self._cell_size * 8
        self._canvas = Canvas(self._tk, width=px, height=px, bg="#388e3c", highlightthickness=0)
        self._canvas.pack()
        self._draw_grid()
        self._canvas.bind("<Button-1>", self._on_click)

    def _draw_grid(self) -> None:
        assert self._canvas is not None
        size = self._cell_size
        for i in range(9):
            x = i * size
            self._canvas.create_line(x, 0, x, 8 * size, fill="black")
            self._canvas.create_line(0, x, 8 * size, x, fill="black")

    def _draw_board(self) -> None:
        assert self._canvas is not None
        size = self._cell_size
        self._canvas.delete("stone")
        symbols = {1: "black", -1: "white"}
        cells = self.board.as_list()
        for idx, val in enumerate(cells):
            if val == 0:
                continue
            r, c = divmod(idx, 8)
            x0 = c * size + 4
            y0 = r * size + 4
            x1 = (c + 1) * size - 4
            y1 = (r + 1) * size - 4
            self._canvas.create_oval(x0, y0, x1, y1, fill=symbols[val], tags="stone")
        # highlight legal moves for current player
        for idx in self.board.legal_moves():
            r, c = divmod(idx, 8)
            x = c * size + size / 2
            y = r * size + size / 2
            self._canvas.create_text(x, y, text="·", fill="yellow", font=("Helvetica", size // 2), tags="stone")
        if self._tk is not None:
            self._tk.update_idletasks()
            self._tk.update()

    def _on_click(self, event: tk.Event) -> None:  # type: ignore[override]
        if self._terminated:
            return
        size = self._cell_size
        col = int(event.x // size)
        row = int(event.y // size)
        if 0 <= row < 8 and 0 <= col < 8:
            idx = row * 8 + col
            self.step(idx)  # ignore returned values; GUI refresh happens inside

    # ------------------------------ API ------------------------------
    def render(self):  # type: ignore[override]
        """Render the board.

        If called for the first time, creates a Tkinter window and enables
        interactive play via mouse clicks.
        """
        self._ensure_gui()
        self._draw_board()
