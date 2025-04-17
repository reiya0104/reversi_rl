"""Reversi game with optional auto-play mode.

Usage:
    AUTO=1 python -m agent.run  # Auto-play mode
    python -m agent.run         # Manual play mode
"""

import os
import time
import tkinter as tk
from typing import Protocol

import numpy as np

from agent.env import ReversiEnv


class Player(Protocol):
    """プレイヤーのインターフェース"""

    def get_action(self, env: ReversiEnv) -> int:
        """次の手を返す"""
        raise NotImplementedError


class AutoPlayer:
    """自動プレイヤー（ランダム）"""

    def get_action(self, env: ReversiEnv) -> int:
        legal_moves = env.board.legal_moves()
        if legal_moves:
            action = np.random.choice(legal_moves)
            print(f"Auto: Playing at {action}")
            return action
        print("Auto: Passing")
        return 64  # パス


class ManualPlayer:
    """手動プレイヤー（マウスクリック）"""

    def __init__(self) -> None:
        self._action: int | None = None
        self._click_event = None

    def get_action(self, env: ReversiEnv) -> int:
        """クリックイベントで設定されたアクションを返す"""
        print("Waiting for click...")
        while self._action is None:
            env.update_gui()  # GUIの更新
            time.sleep(0.1)
        action = self._action
        self._action = None
        return action

    def set_action(self, action: int) -> None:
        """クリックイベントでアクションを設定"""
        print(f"Setting action: {action}")
        self._action = action


def play_game(env: ReversiEnv, player: Player) -> None:
    """ゲームを進行する"""
    env.reset()
    done: bool = False
    reward: int = 0
    step_count: int = 0

    print("Starting game...")
    while not done:
        env.render()
        time.sleep(0.1)  # 少し待機してGUIの更新を確認

        # 現在のプレイヤーの手を選ぶ
        action = player.get_action(env)
        print(
            f"Step {step_count}: {'Auto' if isinstance(player, AutoPlayer) else 'Manual'} player action: {action}"
        )
        _, reward, done, _, _ = env.step(action)
        step_count += 1

    env.render()
    black, white = env.board.counts()
    reward = 1 if black > white else -1 if black < white else 0
    print(f"\nGame finished in {step_count} steps")
    print(f"Final score: Black {black} - White {white}")
    print(f"Reward: {reward}")


def setup_manual_player(env: ReversiEnv, player: ManualPlayer) -> None:
    """手動プレイヤーのクリックイベントを設定"""

    def on_click(event: tk.Event) -> None:
        print("Click detected!")
        if env._terminated:
            return
        size = env._cell_size
        col = int(event.x // size)
        row = int(event.y // size)
        if 0 <= row < 8 and 0 <= col < 8:
            idx = row * 8 + col
            if idx in env.board.legal_moves():
                print(f"Legal move at {idx}")
                player.set_action(idx)
            else:
                print("不正な手です!")

    if env._canvas is not None:
        env._canvas.bind("<Button-1>", on_click)
        print("Click event bound to canvas")
    else:
        print("GUIが見つかりません")


if __name__ == "__main__":
    env = ReversiEnv()
    if os.getenv("AUTO") == "1":
        play_game(env, AutoPlayer())
    else:
        player = ManualPlayer()
        # 最初のrender()を呼び出してGUIを初期化
        env.render()
        setup_manual_player(env, player)
        play_game(env, player)
