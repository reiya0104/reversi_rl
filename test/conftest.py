"""Pytest fixtures."""
from __future__ import annotations

import pytest

from agent.env import ReversiEnv

@pytest.fixture
def env():
    return ReversiEnv(seed=42)
