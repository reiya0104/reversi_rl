.PHONY: run test lint build build-dev build-release clean run-auto

# Pythonのライブラリパスを設定
PYTHON_ROOT := $(shell python3-config --prefix)
PYTHON_LIB_PATH := $(PYTHON_ROOT)/lib
PYTHON_INCLUDE_PATH := $(PYTHON_ROOT)/include/python3.12
export LIBRARY_PATH := $(PYTHON_LIB_PATH):$(LIBRARY_PATH)
export LD_LIBRARY_PATH := $(PYTHON_LIB_PATH):$(LD_LIBRARY_PATH)
export C_INCLUDE_PATH := $(PYTHON_INCLUDE_PATH):$(C_INCLUDE_PATH)
export CPLUS_INCLUDE_PATH := $(PYTHON_INCLUDE_PATH):$(CPLUS_INCLUDE_PATH)
export RUSTFLAGS = -L $(PYTHON_LIB_PATH)

# クリーンアップ
clean:
	rm -rf target/
	rm -rf *.egg-info/
	rm -rf dist/
	rm -rf build/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .pytest_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} +

# Build the Rust extension in develop mode
build-dev:
	poetry run maturin develop

# リリース用ビルド（最適化あり）
build-release:
	poetry run maturin develop --release

# デフォルトはリリースビルド
build: build-release

run: build
	poetry run python -m agent.run

run-auto: build
	AUTO=1 poetry run python -m agent.run

test: build
	cargo test --quiet
	poetry run pytest -q

lint:
	cargo fmt
	poetry run ruff check . --fix
	poetry run mypy -p agent
