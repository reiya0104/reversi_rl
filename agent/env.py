import random
import tkinter as tk
from tkinter import Canvas
from typing import Any

import gymnasium as gym
import numpy as np
from reversi_rl import Board


class ReversiEnv(gym.Env):
    """Gymnasium environment for Reversi with an optional Tkinter GUI.

    The GUI is created lazily when `render()` is called in "human" mode.
    Clicking on a square issues the corresponding action and triggers the
    environment's `step`, so you can play against the built‑in random opponent.
    """

    metadata: dict[str, list[str]] = {"render_modes": ["human"]}

    def __init__(self, seed: int | None = None, manual_mode: bool = False):
        super().__init__()
        self.rng = random.Random(seed)
        self.board = Board()
        self.action_space = gym.spaces.Discrete(64 + 1)  # 64 squares + pass
        self.observation_space = gym.spaces.Box(
            low=-1, high=1, shape=(65,), dtype=np.int8
        )
        self.manual_mode = manual_mode

        # GUI elements (created on demand)
        self._tk: tk.Tk | None = None
        self._canvas: Canvas | None = None
        self._pass_button: tk.Button | None = None
        self._cell_size: int = 60
        self._terminated: bool = False
        self._consecutive_passes: int = 0  # 連続パス回数

    # ------------------------------------------------------------
    def reset(self, *, seed: int | None = None, options: dict[str, Any] | None = None):  # type: ignore[override]
        if seed is not None:
            self.rng.seed(seed)
        self.board.reset()
        self._terminated = False
        self._consecutive_passes = 0
        if self._canvas is not None:
            self._draw_board()  # refresh GUI if it exists
        obs = np.array(self.board.as_list() + [1], dtype=np.int8)
        return obs, {}

    def step(self, action: int):  # type: ignore[override]
        legal = self.board.legal_moves()
        reward: int = 0
        self._terminated = False

        # 観測値を作成
        obs = np.array(
            self.board.as_list() + [1 if self.board.get_black_to_move() else -1],
            dtype=np.int8,
        )

        # 盤面が埋まっているかチェック
        board_state = self.board.as_list()
        if all(cell != 0 for cell in board_state):
            print("\nGame over: Board is full!")
            self._terminated = True
            black, white = self.board.counts()
            print("\nFinal score:")
            print(f"Black: {black}")
            print(f"White: {white}")
            print(
                f"\n{'Black' if black > white else 'White' if white > black else 'No one'} wins!"
            )
            reward = 1 if black > white else -1 if black < white else 0
            return obs, reward, self._terminated, False, {}

        # 現在のプレイヤーの手
        print(
            f"\nCurrent player: {'Black' if self.board.get_black_to_move() else 'White'}"
        )
        print(f"Legal moves: {legal}")

        if action != 64 and action in legal:
            print(f"Playing at {action}")
            self.board.play(action)
            self._consecutive_passes = 0
        else:
            if not legal:
                print("Passing...")
                self._consecutive_passes += 1
                self.board.pass_turn()
            else:
                print("Cannot pass when legal moves are available!")
                return obs, reward, self._terminated, False, {}

        # 相手の手
        opp_moves = self.board.legal_moves()
        print(f"Opponent's legal moves: {opp_moves}")
        if opp_moves:
            opp_action = self.rng.choice(opp_moves)
            print(f"Opponent plays at {opp_action}")
            self.board.play(opp_action)
            self._consecutive_passes = 0

            # 相手の手の後で盤面が埋まっているかチェック
            board_state = self.board.as_list()
            if all(cell != 0 for cell in board_state):
                print("\nGame over: Board is full!")
                self._terminated = True
                black, white = self.board.counts()
                print("\nFinal score:")
                print(f"Black: {black}")
                print(f"White: {white}")
                print(
                    f"\n{'Black' if black > white else 'White' if white > black else 'No one'} wins!"
                )
                reward = 1 if black > white else -1 if black < white else 0
                return obs, reward, self._terminated, False, {}
        else:
            print("Opponent passes...")
            self._consecutive_passes += 1
            self.board.pass_turn()
            if self._consecutive_passes >= 2:
                print("\nGame over: Both players passed")
                self._terminated = True

        # ゲーム終了時の処理
        if self._terminated:
            black, white = self.board.counts()
            print("\nFinal score:")
            print(f"Black: {black}")
            print(f"White: {white}")
            print(
                f"\n{'Black' if black > white else 'White' if white > black else 'No one'} wins!"
            )
            reward = 1 if black > white else -1 if black < white else 0
        elif self._canvas is not None:
            self._draw_board()

        return obs, reward, self._terminated, False, {}

    # -------------------------- GUI helpers ---------------------------
    def _ensure_gui(self) -> None:
        if self._tk is not None:
            return
        self._tk = tk.Tk()
        self._tk.title("Reversi RL")
        px = self._cell_size * 8
        button_height = 50  # パスボタンの領域の高さ

        # 画面の中央に配置（ボタンの高さを含む）
        screen_width = self._tk.winfo_screenwidth()
        screen_height = self._tk.winfo_screenheight()
        x = (screen_width - px) // 2
        y = (screen_height - (px + button_height)) // 2
        self._tk.geometry(f"{px}x{px + button_height}+{x}+{y}")

        # キャンバスを配置
        self._canvas = Canvas(
            self._tk, width=px, height=px, bg="#388e3c", highlightthickness=0
        )
        self._canvas.pack(pady=(0, 0))  # 上下のパディングを0に設定
        self._draw_grid()
        self._canvas.bind("<Button-1>", self._on_click)

        # パスボタンを追加（手動モードでは常に表示）
        self._pass_button = tk.Button(
            self._tk,
            text="パス",
            command=self._on_pass,
            font=("Helvetica", 12),
            bg="#cccccc",  # 初期状態は無効（グレー）
            fg="white",
            padx=20,
            pady=5,
            state="disabled",  # 初期状態は無効
        )
        if self.manual_mode:
            self._pass_button.pack(pady=5)

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
        legal_moves = self.board.legal_moves()
        for idx in legal_moves:
            r, c = divmod(idx, 8)
            x = c * size + size / 2
            y = r * size + size / 2
            self._canvas.create_text(
                x,
                y,
                text="·",
                fill="yellow",
                font=("Helvetica", size // 2),
                tags="stone",
            )
        if self._tk is not None:
            self._tk.update_idletasks()
            self._tk.update()

    def _on_pass(self) -> None:
        """パスボタンがクリックされたときの処理"""
        if not self._terminated:
            _, _, self._terminated, _, _ = self.step(64)  # 64はパスを表す

    def _on_click(self, event: tk.Event) -> None:  # type: ignore[override]
        if self._terminated:
            return
        size = self._cell_size
        col = int(event.x // size)
        row = int(event.y // size)
        if 0 <= row < 8 and 0 <= col < 8:
            idx = row * 8 + col
            if idx in self.board.legal_moves():
                _, _, self._terminated, _, _ = self.step(
                    idx
                )  # GUI refresh happens inside
            else:
                print("不正な手です!")
        else:
            # 盤面外をクリックした場合はパス
            self._on_pass()

    # ------------------------------ API ------------------------------
    def render(self):  # type: ignore[override]
        """Render the board.

        If called for the first time, creates a Tkinter window and enables
        interactive play via mouse clicks.
        """
        self._ensure_gui()
        self._draw_board()

    def update_gui(self) -> None:
        """GUIを更新する"""
        if self._tk is not None:
            # パスボタンの状態を更新（手動モードの場合のみ）
            if self.manual_mode and self._pass_button is not None:
                legal_moves = self.board.legal_moves()
                # 自分の手番で合法手がない場合のみパスボタンを有効化
                if not legal_moves and not self._terminated:
                    self._pass_button.config(state="normal", bg="#4CAF50")  # 緑色
                else:
                    self._pass_button.config(state="disabled", bg="#cccccc")  # グレー
            self._tk.update_idletasks()
            self._tk.update()
