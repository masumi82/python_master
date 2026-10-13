# 全課題で共通の実行規則。
#
# 課題側の Makefile に書くのは、この 1 行だけ:
#   include ../../common/common.mk
#
# ターゲット:
#   make test             テストを実行する（実装中の速い確認用）
#   make test ARGS="-x"   pytest にオプションを渡す（-x: 最初の失敗で止める、-k 名前: 絞り込む）
#   make lint             ruff で、バグになりやすい書き方を調べる
#   make type             mypy --strict で、型の矛盾を調べる
#   make check            lint、type に続けて、警告をエラー扱いにしてテストを実行する（完了条件）
#   make repl             対話環境を開く（この課題の src/ のモジュールを import できる）
#   make clean            キャッシュを削除する

COMMON_DIR := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))
ROOT       := $(abspath $(COMMON_DIR)/..)
PY         := $(ROOT)/.venv/bin/python
CONFIG     := $(ROOT)/pyproject.toml
ARGS       ?=

# シェルに PYTHONPATH が設定されていても（ROS など）、ここで動かす道具には引き継がない。
unexport PYTHONPATH

# テストが使えるメモリの上限（KB 単位。4GB）。終わらないループでリストが伸び続けても、
# PC が固まる前に MemoryError で止まる。ulimit -v が使えない環境では、上限なしで動く。
MEM_LIMIT_KB := 4194304
LIMIT        := ulimit -v $(MEM_LIMIT_KB) 2>/dev/null || true;

.PHONY: test lint type check repl clean venv

# PYTHONPATH=src は、テストが src/ のモジュールを import できるようにするため。
test: venv
	$(LIMIT) PYTHONPATH=src $(PY) -m pytest -c $(CONFIG) test $(ARGS)

lint: venv
	$(PY) -m ruff check --config $(CONFIG) src test

type: venv
	$(PY) -m mypy --config-file $(CONFIG) src test

# pytest の -W error は、警告（閉じ忘れたファイルの ResourceWarning など）をテストの失敗にする。
# -X dev は Python の開発モードで、実行時の検査を増やす。
# -X tracemalloc=5 は、警告の原因になったオブジェクトを「どこで作ったか」まで表示させる。
check: lint type
	$(LIMIT) PYTHONPATH=src $(PY) -X dev -X tracemalloc=5 -m pytest -c $(CONFIG) -W error test $(ARGS)

# 対話環境。import clamp のように、この課題の src/ のモジュールを読み込める。
repl: venv
	PYTHONPATH=src $(PY)

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

venv:
	@test -x $(PY) || { echo "$(PY) がありません。リポジトリの一番上で uv sync を実行してください。" >&2; exit 1; }
