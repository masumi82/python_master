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
#   make clean            キャッシュを削除する

COMMON_DIR := $(patsubst %/,%,$(dir $(lastword $(MAKEFILE_LIST))))
ROOT       := $(abspath $(COMMON_DIR)/..)
PY         := $(ROOT)/.venv/bin/python
CONFIG     := $(ROOT)/pyproject.toml
ARGS       ?=

.PHONY: test lint type check clean venv

# PYTHONPATH=src は、テストが src/ のモジュールを import できるようにするため。
test: venv
	PYTHONPATH=src $(PY) -m pytest -c $(CONFIG) test $(ARGS)

lint: venv
	$(PY) -m ruff check --config $(CONFIG) src test

type: venv
	$(PY) -m mypy --config-file $(CONFIG) src test

check: lint type
	PYTHONPATH=src $(PY) -X dev -m pytest -c $(CONFIG) -W error test $(ARGS)

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +

venv:
	@test -x $(PY) || { echo "$(PY) がありません。リポジトリの一番上で uv sync を実行してください。" >&2; exit 1; }
