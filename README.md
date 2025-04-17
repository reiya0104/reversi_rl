# Reversi RL

Base project for experimenting with reinforcement‑learning on the game **Reversi / Othello**.

* Rust core (`src/lib.rs`) — fast board logic exposed to Python via PyO3.
* Gymnasium environment (`agent/env.py`) — compatible with popular RL libraries.

## Quick start
```bash
poetry install
make build   # compile Rust extension via maturin
make test    # run Rust + Python tests
make run     # play random moves in console
```
---

## 3. Next steps
* Integrate your preferred RL algorithm (e.g., DQN, AlphaZero‑style MCTS) on top of `ReversiEnv`.
* Extend the Rust core for performance (bitboards, symmetry, etc.).
* Swap the random opponent with self‑play or scripted heuristics.

Enjoy hacking! 🎉
