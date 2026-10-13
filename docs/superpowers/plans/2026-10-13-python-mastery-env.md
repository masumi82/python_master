# Python Mastery Exercise Environment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 設計書にある演習環境（共通の実行規則、8課題、ROADMAP・README・CLAUDE.md、ローカル専用の answers/）を `python_master` に作る。

**Architecture:** 課題は1つずつ独立したディレクトリで、`README.md`、スタブ入りの `src/`、提供テストの `test/`、1行だけの `Makefile` からなる。`Makefile` は `common/common.mk` を include し、common.mk がリポジトリ直下の `.venv` と `pyproject.toml` を使って pytest・ruff・mypy を実行する。模範解答は `answers/`（git から除外）に置き、`answers/verify.sh` が課題を一時ディレクトリへコピーして解答を差し込み、`make check` で検証する。

**Tech Stack:** Python 3.13（uv が管理）、pytest、ruff、mypy（strict）、GNU make、bash。

**Spec:** `docs/superpowers/specs/2026-10-13-python-mastery-roadmap-design.md`

## Global Constraints

- リポジトリは `/home/m-horiuchi/persol_ws/python_master`。以下、パスはここからの相対パス。
- Python は 3.13（`.python-version`）。依存は pytest、ruff、mypy の3つだけで、`pyproject.toml` の dev グループに書く。
- ツールの設定は `pyproject.toml` に集める。mypy は `strict = true`。ruff は `E`・`F`・`W`・`B`・`UP` を選び、`E501`（行の長さ）は外す。
- 課題の `Makefile` は `include ../../common/common.mk` の1行だけ。課題ごとの `conftest.py` は置かない。
- make ターゲットは `test`、`lint`、`type`、`check`、`clean`。完了条件は `make check`。
- スタブは、テストの収集が通り、1件以上失敗する状態にする。
- 模範解答はコミットしない。`src/` にも、この計画書にも書かない。解答・解説・速習は `answers/` にだけ置き、`answers/` は `.git/info/exclude` で除外する。
- 学習者向けの文章（README、ROADMAP、解説、速習）は日本語。課題コードと解答のコメントも日本語。識別子は英語。
- 見出しや本文に全角ダッシュを使わない。挿入は（）か読点にする。
- GitHub へのプッシュはしない。
- コミットメッセージは英語で、末尾に `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` を付ける。
- `$REPO` = `/home/m-horiuchi/persol_ws/python_master`
- `$SCRATCH` = `/tmp/claude-1000/-home-m-horiuchi-persol-ws-c-master/415bdd35-7ebd-4961-8e58-7a366bda2849/scratchpad`

### ファイルの書き方

この計画書では、作るファイルの中身を `**File:**` の行に続くコードブロックで示す。ブロックの中身をそのままファイルにする（ブロックを機械的に取り出すスクリプトを `$SCRATCH` に作って使ってよい）。README のように中に ``` を含むファイルは、外側を4つのバッククォートで囲んである。

### 標準の検証手順

課題ディレクトリを `$EX`（例 `phase1_lang/ex03_data_model`）とする。

1. スタブの確認
   ```bash
   make -C $REPO/$EX test; echo "rc=$?"
   ```
   期待: `rc=2`（make が pytest の失敗を伝える）。最後の集計行が `N failed ...` の形で、`error` という語を含まない。収集に失敗すると、この行に `N errors` と出る。
2. スタブの lint と type
   ```bash
   make -C $REPO/$EX lint; echo "rc=$?"; make -C $REPO/$EX type; echo "rc=$?"
   ```
   期待: どちらも `rc=0`。例外は各タスクに書く（ex02_bug_hunt、ex05_context、ex06_typing）。
3. 解答の確認。`answers/$EX/` に解答ファイルを書いてから実行する。解答はその場で書き、この計画書には載せない。
   ```bash
   bash $REPO/answers/verify.sh $(basename $EX)
   ```
   期待: `PASS  $EX  N passed ...` が1行出て、終了コード 0。
4. コミット前の確認
   ```bash
   git -C $REPO status --short            # answers/ が出ていないこと
   git -C $REPO grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
   ```
   期待: `answers/` の行がない。grep はファイル名を1つも出さず、`scan rc=1`（一致なし）。gitleaks は未導入なので grep で代用する。ステージ済みの全ファイルを調べ、検索語そのものを含むこの計画書（`docs/superpowers/`）は除く。一致したファイル名が出たら、中身を表示せずに該当箇所を確かめる。

## Review Focus

設計書が暗に求めているのに、素直にテストを書くと漏れやすい入力。それぞれ、担当するタスクのテストに入れてある。

1. `time_to_threshold` で、先頭の要素（位置 0）が閾値を超える。`if not idx:` と直すと 0 を「なし」と取り違える。→ Task 2 の `test_time_to_threshold`
2. `RingBuffer` に `None` を入れる。空きスロットの目印に `None` を使う実装だと、個数が狂う。→ Task 5 の `test_none_can_be_stored`
3. `take(items, 0)` と、`n` 個を返した直後。`enumerate` で数える素直な実装は1件余分に読む。→ Task 6 の `test_take_is_lazy`、`test_take_zero_reads_nothing`
4. `dispatch` で呼んだハンドラが例外を出す。握りつぶさず、そのまま呼び出し側へ伝わること。→ Task 4 の `test_handler_exception_propagates`
5. `typecases/` が1件も見つからない（パスの間違いなど）。パラメータ化テストが0件になり、何も検査せずに通ってしまう。→ Task 8 の `test_cases_exist`

テストでは扱わず、Task 1 の手順で確かめるもの: `.venv` がない状態で make を実行したとき、`uv sync` を促すメッセージを出して止まること。

---

### Task 1: 土台（pyproject・common.mk・verify.sh）と phase0_env/ex01_toolchain

設計書5章の「未検証の前提」のうち、`uv sync`、設定ファイルの解決、日本語コメントと ruff、`breakpoint()` の4つをここで確かめる。

**Files:**
- Create: `.gitignore`、`.python-version`、`pyproject.toml`、`uv.lock`（`uv sync` が生成）
- Create: `common/common.mk`
- Create: `phase0_env/ex01_toolchain/{Makefile,README.md,src/clamp.py,test/test_clamp.py}`
- Create（コミットしない）: `answers/verify.sh`、`answers/phase0_env/ex01_toolchain/clamp.py`
- Modify: `.git/info/exclude`

**Interfaces:**
- Produces: `common/common.mk`。ターゲット `test`、`lint`、`type`、`check`、`clean`。変数 `ROOT`（コマンドラインで上書きできる）、`ARGS`（pytest に渡す追加オプション）。
- Produces: `answers/verify.sh [絞り込み文字列]`。課題を一時ディレクトリへコピーし、解答を差し込んで `make check ROOT=$REPO` を実行する。
- Produces: `def clamp(v: int, lo: int, hi: int) -> int`

- [ ] **Step 1: answers/ を git から除外する**

```bash
cd $REPO && printf '\n# Local-only model answers (never commit or push)\nanswers/\n' >> .git/info/exclude && mkdir -p answers && git status --short
```
期待: `answers/` が表示されない。

- [ ] **Step 2: リポジトリ直下の設定ファイルを作る**

**File:** `.gitignore`
```
# Python / tool caches
__pycache__/
*.pyc
.pytest_cache/
.ruff_cache/
.mypy_cache/
.venv/
# secrets / local
.env
.env.*
!.env.example
*.pem
*.key
config/local.*
# misc
node_modules/
```

**File:** `.python-version`
```
3.13
```

**File:** `pyproject.toml`
```toml
[project]
name = "python-master"
version = "0.1.0"
description = "Python 習熟演習"
requires-python = ">=3.13"
dependencies = []

[dependency-groups]
dev = [
    "mypy>=1.13",
    "pytest>=8.3",
    "ruff>=0.8",
]

[tool.pytest.ini_options]
addopts = "-q --tb=short"

[tool.mypy]
strict = true

[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
# E/W: 書式、F: 未使用や未定義、B: バグになりやすい書き方、UP: 古い書き方
select = ["E", "F", "W", "B", "UP"]
ignore = ["E501"]
```

- [ ] **Step 3: 依存を入れる**

```bash
cd $REPO && uv sync && .venv/bin/python --version && .venv/bin/python -m pytest --version && .venv/bin/python -m ruff --version && .venv/bin/python -m mypy --version
```
期待: `Python 3.13.x` と3つのツールのバージョンが出る。`uv.lock` と `.venv/` ができる。
成り立たない場合: `.python-version` を `3.11`、`requires-python` を `>=3.11`、`target-version` を `py311` に変えてやり直し、以降の課題では `def f[T]` の書き方を `TypeVar` に置き換える。その旨を設計書5章に追記する。

- [ ] **Step 4: common.mk を作る**

**File:** `common/common.mk`
```make
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
```

- [ ] **Step 5: ex01_toolchain のテストとスタブを作る**

**File:** `phase0_env/ex01_toolchain/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase0_env/ex01_toolchain/test/test_clamp.py`
```python
import pytest

from clamp import clamp


@pytest.mark.parametrize(
    ("v", "lo", "hi", "expected"),
    [
        (5, 0, 10, 5),  # 範囲内
        (-3, 0, 10, 0),  # 下にはみ出す
        (42, 0, 10, 10),  # 上にはみ出す
        (0, 0, 10, 0),  # 下端ちょうど
        (10, 0, 10, 10),  # 上端ちょうど
        (7, 7, 7, 7),  # lo == hi
        (-5, -10, -1, -5),  # 負の範囲
    ],
)
def test_clamp(v: int, lo: int, hi: int, expected: int) -> None:
    assert clamp(v, lo, hi) == expected


def test_clamp_huge_values() -> None:
    # C の int32_t と違い、Python の int は桁あふれしない。
    big = 2**100
    assert clamp(big, 0, 2**64) == 2**64
    assert clamp(-big, -(2**64), 0) == -(2**64)


def test_clamp_rejects_reversed_range() -> None:
    with pytest.raises(ValueError):
        clamp(5, 10, 0)
```

**File:** `phase0_env/ex01_toolchain/src/clamp.py`
```python
"""値を範囲に収める。c_master の phase0_env/ex01_toolchain と同じ題材。"""


def clamp(v: int, lo: int, hi: int) -> int:
    """v を閉区間 [lo, hi] に収めた値を返す。

    lo > hi のときは ValueError を送出する。
    """
    raise NotImplementedError
```

- [ ] **Step 6: スタブで失敗することを確かめる**

```bash
make -C $REPO/phase0_env/ex01_toolchain test; echo "rc=$?"
make -C $REPO/phase0_env/ex01_toolchain lint; echo "rc=$?"
make -C $REPO/phase0_env/ex01_toolchain type; echo "rc=$?"
```
期待: test は `9 failed`、`rc=2`。lint と type は `rc=0`（日本語コメントが ruff に触れないことの確認を兼ねる）。
成り立たない場合: ruff が日本語の全角文字を指摘したら、そのルールを `pyproject.toml` の `ignore` に足す。

- [ ] **Step 7: verify.sh を作る**

**File:** `answers/verify.sh`
```bash
#!/usr/bin/env bash
# すべての模範解答を、実際に提供しているテストで検証する。
# 各課題を一時ディレクトリにコピーし、解答ファイルを差し込んでから make check を実行する。
# リポジトリ本体は一切変更しない。
#
#   bash answers/verify.sh          全課題
#   bash answers/verify.sh ex03     名前に ex03 を含む課題だけ
set -u
ANS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$ANS/.." && pwd)"
FILTER="${1:-}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
ln -s "$REPO/common" "$WORK/common"

# 課題ディレクトリ : 解答ファイル（<課題>/src/ にコピーする）
EXERCISES=(
  "phase0_env/ex01_toolchain:clamp.py"
  "phase0_env/ex02_bug_hunt:stats.py"
  "phase1_lang/ex01_names_objects:answers.py objects.py"
  "phase1_lang/ex02_closure_decorator:decorators.py commands.py"
  "phase1_lang/ex03_data_model:ring_buffer.py"
  "phase1_lang/ex04_iter_gen:iters.py"
  "phase1_lang/ex05_context:config.py resources.py"
  "phase1_lang/ex06_typing:typed.py"
)

fail=0
ran=0
for entry in "${EXERCISES[@]}"; do
  dir="${entry%%:*}"; files="${entry#*:}"
  case "$dir" in *"$FILTER"*) ;; *) continue ;; esac
  if [ ! -d "$REPO/$dir" ]; then
    printf 'SKIP  %-40s (課題がまだない)\n' "$dir"; continue
  fi
  ran=$((ran + 1))
  mkdir -p "$WORK/$(dirname "$dir")"
  cp -r "$REPO/$dir" "$WORK/$dir"
  find "$WORK/$dir" \( -name __pycache__ -o -name .mypy_cache \) -type d -prune -exec rm -rf {} +
  for f in $files; do cp "$ANS/$dir/$f" "$WORK/$dir/src/$f"; done
  # ROOT を渡すと、common.mk は本体の .venv と pyproject.toml を使う。
  if out=$(make -C "$WORK/$dir" check ROOT="$REPO" 2>&1); then
    printf 'PASS  %-40s %s\n' "$dir" "$(printf '%s\n' "$out" | grep -E '[0-9]+ passed' | tail -1)"
  else
    printf 'FAIL  %-40s\n' "$dir"; printf '%s\n' "$out" | tail -25; fail=1
  fi
done
[ "$ran" -gt 0 ] || { echo "一致する課題がない: $FILTER"; exit 1; }
exit $fail
```

- [ ] **Step 8: 解答を書いて検証する**

`answers/phase0_env/ex01_toolchain/clamp.py` に解答を書く（`src/clamp.py` と差し替えられる形）。

```bash
bash $REPO/answers/verify.sh ex01_toolchain; echo "rc=$?"
```
期待: `PASS  phase0_env/ex01_toolchain  9 passed ...`、`rc=0`。

- [ ] **Step 9: 設定ファイルが効いていることを確かめる**

一時コピーに、型のない関数と可変のデフォルト引数を足して、strict と `B` ルールが働くことを見る。

```bash
W=$SCRATCH/cfgprobe && rm -rf $W && mkdir -p $W/p && cp -r $REPO/phase0_env/ex01_toolchain $W/p/ex && ln -s $REPO/common $W/common
cp $REPO/answers/phase0_env/ex01_toolchain/clamp.py $W/p/ex/src/clamp.py
printf '\n\ndef probe(x, acc=[]):\n    return acc\n' >> $W/p/ex/src/clamp.py
make -C $W/p/ex lint ROOT=$REPO; echo "lint rc=$?"
make -C $W/p/ex type ROOT=$REPO; echo "type rc=$?"
make -C $W/p/ex test ROOT=/nonexistent; echo "novenv rc=$?"
rm -rf $W
```
期待: lint は `B006` を出して `rc=2`。type は `no-untyped-def` を出して `rc=2`。最後は「uv sync を実行してください」と出て `rc=2`。
成り立たない場合: common.mk の `--config` / `--config-file` / `-c` の渡し方を直す。

- [ ] **Step 10: `breakpoint()` が make 経由で pdb に入ることを確かめる**

```bash
W=$SCRATCH/pdbprobe && rm -rf $W && mkdir -p $W/p && cp -r $REPO/phase0_env/ex01_toolchain $W/p/ex && ln -s $REPO/common $W/common
sed -i 's/^    raise NotImplementedError$/    breakpoint()\n    raise NotImplementedError/' $W/p/ex/src/clamp.py
printf 'p v\nq\n' | make -C $W/p/ex test ROOT=$REPO 2>&1 | tail -15
rm -rf $W
```
スタブの `raise NotImplementedError` の前に `breakpoint()` を差し込んで試す。
期待: 出力に `(Pdb)` と、`p v` の結果（最初のテストの `5`）が出る。
成り立たない場合: README の手順5を `../../.venv/bin/python -m pdb -c continue -m pytest test` に替える。

- [ ] **Step 11: README を作る**

**File:** `phase0_env/ex01_toolchain/README.md`
````markdown
# Phase 0 / ex01_toolchain（開発環境を整える）

## 読み物: C の道具と Python の道具
c_master で使った道具には、それぞれ Python 側の相手がいます。

| C で使った道具 | Python での相手 | 何を見つけるか |
|---|---|---|
| `-Wall -Wextra -Werror` | ruff（`make lint`） | バグになりやすい書き方 |
| コンパイラの型検査 | mypy（`make type`） | 型の矛盾 |
| Unity（`make test`） | pytest（`make test`） | 仕様どおりに動くか |
| ASan / valgrind（`make asan`） | `python -X dev` と警告のエラー扱い（`make check`） | 閉じ忘れたファイルなど |
| gdb | pdb | 止めて中を見る |

C と大きく違う点が2つあります。

- Python の `int` は桁あふれしません。`2**100` もそのまま計算できます。
- 型ヒント（`v: int`）は、実行時には検査されません。`clamp("a", "b", "c")` と書いても、実行するまで誰も止めてくれません。C ならコンパイラが止める間違いを、Python では mypy に止めてもらいます。

## 目的
以降の全課題で使う道具（pytest、ruff、mypy、pdb）を一通り動かす。

## 手順
1. 環境を作る（リポジトリの一番上で、最初に1回だけ）
   ```bash
   cd ../.. && uv sync && cd phase0_env/ex01_toolchain
   ```
2. 失敗を確認する。`make test` を実行すると、まだ実装していないのでテストが失敗します
3. `src/clamp.py` の `clamp` を実装する（仕様は docstring）
4. `make check` が通ることを確認する
5. pdb を触る。`clamp` の本体の先頭に `breakpoint()` と1行書いて `make test`
   ```
   (Pdb) a          # 引数の値（gdb の info args）
   (Pdb) p v        # 変数の値（gdb の print v）
   (Pdb) n          # 1行進む（gdb の next）
   (Pdb) w          # 呼び出し履歴（gdb の bt）
   (Pdb) r          # 関数の終わりまで進む（gdb の finish）
   (Pdb) c          # 次の breakpoint() まで進む（gdb の continue）
   (Pdb) q          # 終了
   ```
   終わったら `breakpoint()` を消します。
6. mypy を試す。`src/clamp.py` の末尾に `clamp("a", 0, 10)` と書いて `make type` を実行し、エラーメッセージを読んでから消します

## 説明できるようになるべきこと
- ruff、mypy、pytest は、それぞれ何を見つけるか
- 型ヒントは実行時に検査されるか。されないなら、何のために書くのか
- `lo > hi` のとき、C 版は「前提条件」と書くだけだった。Python 版が例外にできるのはなぜか
- テストが通ることと、コードが正しいことは同じか
````

- [ ] **Step 12: コミットする**

```bash
cd $REPO && git add .gitignore .python-version pyproject.toml uv.lock common phase0_env/ex01_toolchain && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add shared make rules, tool config, and phase0 ex01_toolchain

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `answers/` と `.venv/` がステージされていない。`scan rc=1`。

---

### Task 2: phase0_env/ex02_bug_hunt

`src/` にはスタブではなく、バグ入りで動くコードを置く。3つのバグを、ruff・mypy・`make check` の pytest がそれぞれ1つずつ見つける。設計書5章の「閉じ忘れたファイルが `-X dev -W error` で失敗になる」をここで確かめる。

**Files:**
- Create: `phase0_env/ex02_bug_hunt/{Makefile,README.md,src/stats.py,test/test_stats.py}`
- Create（コミットしない）: `answers/phase0_env/ex02_bug_hunt/stats.py`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `collect(value, samples) -> list[float]`、`first_above(samples, threshold) -> int | None`、`time_to_threshold(samples, threshold, dt) -> float`、`load_samples(path) -> list[float]`

- [ ] **Step 1: テストを作る**

**File:** `phase0_env/ex02_bug_hunt/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase0_env/ex02_bug_hunt/test/test_stats.py`
```python
from pathlib import Path

import pytest

import stats


def test_collect_into_given_list() -> None:
    samples = [1.0]
    assert stats.collect(2.0, samples) == [1.0, 2.0]
    assert samples == [1.0, 2.0]


def test_collect_starts_empty_a() -> None:
    assert stats.collect(1.0) == [1.0]


def test_collect_starts_empty_b() -> None:
    # 上のテストと同じ内容。単独なら通るのに、続けて流すと落ちる理由を考える。
    assert stats.collect(1.0) == [1.0]


def test_first_above() -> None:
    assert stats.first_above([0.1, 0.5, 0.9], 0.4) == 1
    assert stats.first_above([0.1, 0.5, 0.9], 1.0) is None
    assert stats.first_above([], 0.0) is None


def test_time_to_threshold() -> None:
    assert stats.time_to_threshold([0.1, 0.5, 0.9], 0.4, 0.5) == pytest.approx(0.5)
    # 先頭の要素（位置 0）で超える場合。0 は「見つからない」ではない。
    assert stats.time_to_threshold([0.9], 0.4, 0.5) == pytest.approx(0.0)


def test_time_to_threshold_never_reached() -> None:
    assert stats.time_to_threshold([0.1, 0.2], 1.0, 0.5) == -1.0


def test_load_samples(tmp_path: Path) -> None:
    path = tmp_path / "samples.txt"
    path.write_text("1.5\n-2.0\n3\n", encoding="utf-8")
    assert stats.load_samples(str(path)) == [1.5, -2.0, 3.0]
```

- [ ] **Step 2: バグ入りのコードを作る**

**File:** `phase0_env/ex02_bug_hunt/src/stats.py`
```python
"""測定値を扱う小さな関数群。

このファイルには 3 つのバグがある。README の手順で、道具に見つけさせること。
各関数の docstring（仕様）は正しい。
"""


def collect(value: float, samples: list[float] = []) -> list[float]:
    """value を samples の末尾に加え、その samples を返す。

    samples を省略したときは、毎回新しい空のリストから始める。
    """
    samples.append(value)
    return samples


def first_above(samples: list[float], threshold: float) -> int | None:
    """threshold を超える最初の要素の位置を返す。なければ None を返す。"""
    for i, x in enumerate(samples):
        if x > threshold:
            return i
    return None


def time_to_threshold(samples: list[float], threshold: float, dt: float) -> float:
    """測定値が初めて threshold を超えるまでの時間（位置 × dt）を返す。

    一度も超えないときは -1.0 を返す。
    """
    return first_above(samples, threshold) * dt


def load_samples(path: str) -> list[float]:
    """1 行に 1 つ数値が書かれたテキストファイルを読み、リストで返す。"""
    f = open(path)
    return [float(line) for line in f]
```

- [ ] **Step 3: 3つのバグが、想定した道具で見つかることを確かめる**

```bash
EX=$REPO/phase0_env/ex02_bug_hunt
make -C $EX test; echo "test rc=$?"
make -C $EX test ARGS="-k starts_empty_b"; echo "single rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待:
- test は `2 failed, 5 passed`（`test_collect_starts_empty_b` と `test_time_to_threshold_never_reached`）、`rc=2`。`test_load_samples` は通る
- `-k starts_empty_b` だけなら `1 passed`、`rc=0`
- lint は `B006` を `stats.py` の `collect` に1件だけ出して `rc=2`
- type は `time_to_threshold` の行に `Unsupported operand types for *` を1件だけ出して `rc=2`

lint や type が、ここに書いた以外の指摘を出したら、`src/stats.py` を直して1つの道具に1つのバグの対応を保つ。

- [ ] **Step 4: 3つ目のバグが `make check` でだけ見つかることを確かめる**

1つ目と2つ目だけを直した版を一時コピーに作り、`make test` は通って `make check` は落ちることを見る。

```bash
W=$SCRATCH/bugprobe && rm -rf $W && mkdir -p $W/p && cp -r $REPO/phase0_env/ex02_bug_hunt $W/p/ex && ln -s $REPO/common $W/common
# $W/p/ex/src/stats.py の collect と time_to_threshold だけを手で直す（load_samples はそのまま）
make -C $W/p/ex test ROOT=$REPO; echo "test rc=$?"
make -C $W/p/ex check ROOT=$REPO 2>&1 | tail -25; echo "check rc=${PIPESTATUS[0]}"
rm -rf $W
```
期待: test は `7 passed`、`rc=0`。check は `test_load_samples` が `ResourceWarning: unclosed file` で落ちて `rc=2`。
出力に `stats.py` の行番号が出ていなければ、common.mk の check のレシピに `-X tracemalloc=5` を足し、ファイルを開いた場所が表示されるようにする。
成り立たない場合（check でも通ってしまう）: 3つ目のバグを「`load_samples` が空行で `ValueError` になる」に替える。仕様に「空行は読み飛ばす」を足し、テストに空行入りのファイルを足す。README の手順4と、設計書3.3・5章を合わせて直す。

- [ ] **Step 5: 解答を書いて検証する**

`answers/phase0_env/ex02_bug_hunt/stats.py` に、3つとも直した版を書く。

```bash
bash $REPO/answers/verify.sh ex02_bug_hunt; echo "rc=$?"
```
期待: `PASS  phase0_env/ex02_bug_hunt  7 passed ...`、`rc=0`。

- [ ] **Step 6: README を作る**

**File:** `phase0_env/ex02_bug_hunt/README.md`
````markdown
# Phase 0 / ex02_bug_hunt（道具でバグを捕まえる）

## 目的
`src/stats.py` には **3つのバグ** が入っています。目で探す前に、道具に見つけさせる練習をします。
各関数の仕様は docstring に書いてあり、そちらは正しいものとします。テスト（`test/`）は変更しないでください。

## 手順（この順で）
1. `make test` を実行する。2件失敗します。そのうち `test_collect_starts_empty_b` は、単独で実行すると通ります
   ```bash
   make test ARGS="-k starts_empty_b"
   ```
   まとめて流すと落ちて、単独だと通る。この食い違いがヒントです。
2. `make lint` を実行する。ruff が1つ目を指摘します。表示されたルール番号で検索すると説明が読めます。直す
3. `make type` を実行する。mypy が2つ目を指摘します。メッセージに出てくる型を読んで直す
4. `make check` を実行する。lint と type が通ると、警告をエラー扱いにしたテストが走り、3つ目が見つかります。`make test` では見つからないことを確かめてから直す
5. 最終確認
   ```bash
   make check
   ```

## ルール
- 修正は最小限に。関数名、引数の名前と順番、docstring の仕様は変えない（デフォルト値と型ヒントは直してよい）
- `time_to_threshold` は、先頭の要素（位置 0）で閾値を超える場合も正しく計算すること

## 説明できるようになるべきこと
- デフォルト引数の値は、いつ作られるか。なぜ「単独だと通る」のか
- `int | None` を返す関数の戻り値を、mypy はなぜそのまま掛け算に使わせないのか。`if not idx:` と `if idx is None:` は何が違うか
- ファイルを閉じ忘れると何が困るか。`make test` では見つからず、`make check` で見つかったのはなぜか
- ruff、mypy、pytest、`python -X dev` は、それぞれどの種類のバグに強いか
````

- [ ] **Step 7: コミットする**

```bash
cd $REPO && git add phase0_env/ex02_bug_hunt && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase0 ex02_bug_hunt

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。Step 4 で common.mk を変えた場合は、それも add する。

---

### Task 3: phase1_lang/ex01_names_objects

予想クイズ8問（`answers.py`）と、別名を作らない関数・クラスの実装（`objects.py`）。クイズの形式は c_master の ex03_int_promotion と同じで、テストは期待値を埋め込まず、その場でコードを実行して照合する。

**Files:**
- Create: `phase1_lang/ex01_names_objects/{Makefile,README.md,src/answers.py,src/objects.py,test/test_quiz.py,test/test_objects.py}`
- Create（コミットしない）: `answers/phase1_lang/ex01_names_objects/{answers.py,objects.py}`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `answers.UNSET`、`answers.Q1`〜`answers.Q8`
- Produces: `make_grid(rows, cols, fill=0) -> list[list[int]]`、`appended(items, value) -> list[int]`、`extend_in_place(items, values) -> None`、`deep_copy(obj) -> object`、`History(initial=None)` と `.add(value)`、`.snapshot() -> list[int]`

- [ ] **Step 1: テストを作る**

**File:** `phase1_lang/ex01_names_objects/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex01_names_objects/test/test_quiz.py`
```python
"""Part 1 の答え合わせ。期待値は埋め込まず、その場で実行して求めている。"""

import pytest

import answers


def check(answer: object, actual: object) -> None:
    if answer is answers.UNSET:
        pytest.fail("まだ予想が書かれていない（src/answers.py）", pytrace=False)
    assert answer == actual


def test_q1() -> None:
    a = [1, 2]
    b = a
    b.append(3)
    check(answers.Q1, a)


def test_q2() -> None:
    a = [1, 2]
    b = a
    b = b + [3]  # noqa: F841
    check(answers.Q2, a)


def test_q3() -> None:
    a = [1, 2]
    b = a
    b += [3]
    check(answers.Q3, a)


def test_q4() -> None:
    grid = [[0] * 2] * 2
    grid[0][0] = 1
    check(answers.Q4, grid)


def test_q5() -> None:
    a = [[1], [2]]
    b = a.copy()
    b.append([3])
    b[0].append(9)
    check(answers.Q5, a)


def test_q6() -> None:
    def add(x: int, acc: list[int] = []) -> list[int]:  # noqa: B006
        acc.append(x)
        return acc

    add(1)
    check(answers.Q6, add(2))


def test_q7() -> None:
    t: tuple[list[int], int] = ([1], 2)
    t[0].append(3)
    check(answers.Q7, t)


def test_q8() -> None:
    a = [1, 2]
    b = [1, 2]
    check(answers.Q8, (a == b, a is b))
```

**File:** `phase1_lang/ex01_names_objects/test/test_objects.py`
```python
import objects


def test_make_grid_shape() -> None:
    assert objects.make_grid(2, 3) == [[0, 0, 0], [0, 0, 0]]
    assert objects.make_grid(1, 2, fill=7) == [[7, 7]]
    assert objects.make_grid(0, 3) == []


def test_make_grid_rows_are_independent() -> None:
    grid = objects.make_grid(3, 2)
    grid[0][0] = 9
    assert grid == [[9, 0], [0, 0], [0, 0]]
    assert grid[0] is not grid[1]


def test_appended_returns_new_list() -> None:
    items = [1, 2]
    result = objects.appended(items, 3)
    assert result == [1, 2, 3]
    assert items == [1, 2]
    assert result is not items


def test_extend_in_place_mutates_argument() -> None:
    items = [1]
    objects.extend_in_place(items, [2, 3])
    assert items == [1, 2, 3]


def test_extend_in_place_does_not_touch_values() -> None:
    items = [1]
    values = [2, 3]
    objects.extend_in_place(items, values)
    assert values == [2, 3]


def test_deep_copy_nested() -> None:
    xy = [1, 2]
    pos = {"xy": xy}
    tags = ["x", "y"]
    original = {"name": "a", "tags": tags, "pos": pos}
    copied = objects.deep_copy(original)
    assert copied == original
    assert copied is not original
    # 複製を奥まで書き換えても、元は変わらない。
    assert isinstance(copied, dict)
    copied["tags"].append("z")
    copied["pos"]["xy"].append(3)
    copied["name"] = "b"
    assert tags == ["x", "y"]
    assert xy == [1, 2]
    assert original["name"] == "a"


def test_deep_copy_list_of_lists() -> None:
    inner = [1, 2]
    original = [inner, [3]]
    copied = objects.deep_copy(original)
    assert copied == [[1, 2], [3]]
    assert isinstance(copied, list)
    assert copied is not original
    assert copied[0] is not inner


def test_deep_copy_leaves_scalars() -> None:
    assert objects.deep_copy(5) == 5
    assert objects.deep_copy("abc") == "abc"
    assert objects.deep_copy(None) is None


def test_history_starts_empty() -> None:
    assert objects.History().snapshot() == []


def test_histories_do_not_share_storage() -> None:
    first = objects.History()
    second = objects.History()
    first.add(1)
    assert first.snapshot() == [1]
    assert second.snapshot() == []


def test_history_copies_initial() -> None:
    initial = [1, 2]
    history = objects.History(initial)
    initial.append(99)
    assert history.snapshot() == [1, 2]
    history.add(3)
    assert history.snapshot() == [1, 2, 3]
    assert initial == [1, 2, 99]


def test_history_snapshot_is_a_copy() -> None:
    history = objects.History([1])
    snap = history.snapshot()
    snap.append(99)
    assert history.snapshot() == [1]
```

- [ ] **Step 2: スタブを作る**

**File:** `phase1_lang/ex01_names_objects/src/answers.py`
```python
"""Part 1: 予想クイズの答えを書く。

テストを実行する「前に」、README.md の各問の予想を書く。
UNSET を、予想した値（リストやタプル）に書き換える。
"""

# 「まだ答えていない」ことを表す目印。これ自体は書き換えない。
UNSET: object = object()

Q1: object = UNSET  # a = [1, 2]; b = a; b.append(3) のあとの a
Q2: object = UNSET  # a = [1, 2]; b = a; b = b + [3] のあとの a
Q3: object = UNSET  # a = [1, 2]; b = a; b += [3] のあとの a
Q4: object = UNSET  # grid = [[0] * 2] * 2; grid[0][0] = 1 のあとの grid
Q5: object = UNSET  # a = [[1], [2]]; b = a.copy(); b.append([3]); b[0].append(9) のあとの a
Q6: object = UNSET  # def add(x, acc=[]) を add(1)、add(2) の順に呼んだときの、2 回目の戻り値
Q7: object = UNSET  # t = ([1], 2); t[0].append(3) のあとの t
Q8: object = UNSET  # a = [1, 2]; b = [1, 2] のときの (a == b, a is b)
```

**File:** `phase1_lang/ex01_names_objects/src/objects.py`
```python
"""Part 2: 別名を作らない、漏らさない関数とクラス。"""


def make_grid(rows: int, cols: int, fill: int = 0) -> list[list[int]]:
    """rows 行 cols 列の 2 次元リストを返す。全要素は fill。

    どの行も、ほかの行と同じリストであってはならない。
    """
    raise NotImplementedError


def appended(items: list[int], value: int) -> list[int]:
    """items の末尾に value を加えた「新しい」リストを返す。items は変えない。"""
    raise NotImplementedError


def extend_in_place(items: list[int], values: list[int]) -> None:
    """items 自体の末尾に values の要素を加える。新しいリストは作らない。"""
    raise NotImplementedError


def deep_copy(obj: object) -> object:
    """list と dict を、入れ子の奥まで複製して返す。

    list と dict 以外（int、str、None など）は、そのまま返す。
    copy モジュールは使わない。
    """
    raise NotImplementedError


class History:
    """値の履歴を持つ。内部のリストを、外から書き換えられないようにする。"""

    def __init__(self, initial: list[int] | None = None) -> None:
        """initial があれば、その時点の内容で始める。なければ空で始める。

        あとで呼び出し側が initial を書き換えても、History の中身は変わらない。
        """
        raise NotImplementedError

    def add(self, value: int) -> None:
        """履歴の末尾に value を加える。"""
        raise NotImplementedError

    def snapshot(self) -> list[int]:
        """今の履歴を返す。返したリストを書き換えても、History の中身は変わらない。"""
        raise NotImplementedError
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex01_names_objects
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `20 failed`、`rc=2`。クイズ8問の失敗メッセージは「まだ予想が書かれていない」で、正解の値が出力に出ていないこと。lint と type は `rc=0`。
lint が `test_q3` の `b += [3]` などに `F841` を出したら、その行にも `# noqa: F841` を付ける。

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex01_names_objects/answers.py` と `objects.py` を書く。

```bash
bash $REPO/answers/verify.sh ex01_names_objects; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex01_names_objects  20 passed ...`、`rc=0`。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex01_names_objects/README.md`
````markdown
# Phase 1 / ex01_names_objects（名前とオブジェクト）

## 読み物: 変数は箱ではなく名札
C の `int a = 5; int b = a;` は、`a` という箱の中身を、`b` という別の箱へコピーします。
Python の `b = a` はコピーをしません。同じオブジェクトに、2枚目の名札を付けるだけです。

C の言葉で言えば、Python の変数はすべてポインタです。

| Python | C で書くなら | 起きること |
|---|---|---|
| `a = [1, 2]` | `list *a = new_list(1, 2);` | オブジェクトを作り、`a` がそれを指す |
| `b = a` | `list *b = a;` | `b` も同じものを指す。コピーはしない |
| `b.append(3)` | `list_append(b, 3);` | 指す先を書き換える。`a` からも見える |
| `b = [9]` | `b = new_list(9);` | `b` の指す先を付け替える。`a` は無関係 |
| `a == b` | 中身を1つずつ比べる | 値が等しいか |
| `a is b` | `a == b`（ポインタの比較） | 同じオブジェクトか |

オブジェクトには、作ったあとで中身を変えられるもの（可変: list、dict、set、自作クラスのインスタンス）と、変えられないもの（不変: int、float、str、tuple、None）があります。不変のオブジェクトは、名札が何枚付いていても困りません。困るのは可変のほうで、1枚の名札から書き換えると、ほかの名札からも変わって見えます。

関数の引数も同じです。渡されるのは名札で、中身のコピーではありません。

```python
def f(x):
    x.append(1)      # 指す先を書き換える。呼び出し側のリストが変わる

def g(x):
    x = x + [1]      # 関数の中の名札 x を付け替えるだけ。呼び出し側は変わらない
```

## Part 1: 予想クイズ
**テストを実行する前に**、各問の値を予想して `src/answers.py` に書いてください。

| Q | コード | 答えるもの |
|---|---|---|
| 1 | `a = [1, 2]; b = a; b.append(3)` | `a` |
| 2 | `a = [1, 2]; b = a; b = b + [3]` | `a` |
| 3 | `a = [1, 2]; b = a; b += [3]` | `a` |
| 4 | `grid = [[0] * 2] * 2; grid[0][0] = 1` | `grid` |
| 5 | `a = [[1], [2]]; b = a.copy(); b.append([3]); b[0].append(9)` | `a` |
| 6 | `def add(x, acc=[]): acc.append(x); return acc` を `add(1)`、`add(2)` の順に呼ぶ | 2回目の戻り値 |
| 7 | `t = ([1], 2); t[0].append(3)` | `t` |
| 8 | `a = [1, 2]; b = [1, 2]` | `(a == b, a is b)` |

`make test` で答え合わせをします。外れた問題は、上の表の「名札」と「指す先」の言葉で説明できるまで、対話環境（`../../.venv/bin/python`）で `id(a)` や `a is b` を表示して確かめてください。

### 考察問題（テストなし、レビューで扱います）
- `s = "ab"; t = s; t += "c"` のあと、`s` は何か。Q3 と結果が違うのはなぜか
- `t = ([1], 2); t[0] += [3]` を実行すると何が起きるか。例外は出るか。`t` は変わるか
- `x` が `None` かどうかを調べるとき、`x == None` と `x is None` のどちらを書くか。なぜか

## Part 2: 別名を作らない、漏らさない
`src/objects.py` を実装します。仕様は各関数の docstring にあります。

## 手順
1. `src/answers.py` に予想を書く → `make test`
2. `src/objects.py` を実装する → `make check`

## ヒント
- `[[0] * cols] * rows` と `[[0] * cols for _ in range(rows)]` は何が違う？
- `deep_copy` は、自分自身を呼ぶ（再帰する）と短く書けます。`isinstance(obj, list)` で種類を調べます
- `History.__init__` の引数は、なぜ `initial=[]` ではなく `initial=None` なのか（1日目の ex02_bug_hunt を思い出す）

## 発展課題（任意）
- `objects.deep_copy` と標準の `copy.deepcopy` に、自分自身を要素に持つリスト（`a = []; a.append(a)`）を渡して違いを見る
- `History.snapshot()` がタプルを返すようにしたら、複製は要るか

## 説明できるようになるべきこと
- 代入 `b = a` で起きること。C のポインタ代入との対応
- 可変と不変の違い。不変のオブジェクトなら別名が問題にならない理由
- `+=` が、list では中身を書き換え、str や int では名札を付け替えること
- 浅いコピーと深いコピーの違い。`[[0] * n] * m` で何が共有されるか
- `==` と `is` の違い。`is` を使うべき場面
- 関数に渡したリストが書き換わる場合と、書き換わらない場合
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex01_names_objects && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex01_names_objects

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 4: phase1_lang/ex02_closure_decorator

クロージャ（`make_counter`、`make_multipliers`）、デコレータ（`traced`、引数付きの `retry`）、デコレータでハンドラを登録する `CommandTable`。`CommandTable` は c_master の ex04_cmd_table と同じ題材。

設計書からの変更: 設計書の `count_calls` を `traced` に替える。呼び出し回数を関数の属性（`wrapper.calls`）に持たせる書き方は `mypy --strict` を通すのが難しく、2日目の学習者には型との格闘になる。`traced` は記録先をモジュールのリスト `CALL_LOG` にして、これを避ける。

**Files:**
- Create: `phase1_lang/ex02_closure_decorator/{Makefile,README.md,src/decorators.py,src/commands.py,test/test_decorators.py,test/test_commands.py}`
- Create（コミットしない）: `answers/phase1_lang/ex02_closure_decorator/{decorators.py,commands.py}`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `CALL_LOG: list[str]`、`make_counter() -> Callable[[], int]`、`make_multipliers(n) -> list[Callable[[int], int]]`、`traced(func)`、`retry(times)`
- Produces: `Handler = Callable[[list[str]], str]`、`EmptyCommandError`、`UnknownCommandError`、`CommandTable` と `.command(name)`、`.names() -> list[str]`、`.dispatch(line) -> str`

- [ ] **Step 1: テストを作る**

**File:** `phase1_lang/ex02_closure_decorator/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex02_closure_decorator/test/test_decorators.py`
```python
import pytest

import decorators

# --- クロージャ ---


def test_make_counter_counts_up() -> None:
    counter = decorators.make_counter()
    assert [counter(), counter(), counter()] == [1, 2, 3]


def test_counters_are_independent() -> None:
    first = decorators.make_counter()
    second = decorators.make_counter()
    first()
    first()
    assert second() == 1
    assert first() == 3


def test_make_multipliers() -> None:
    funcs = decorators.make_multipliers(4)
    assert len(funcs) == 4
    assert [f(10) for f in funcs] == [0, 10, 20, 30]


# --- traced ---


def test_traced_records_calls_in_order() -> None:
    decorators.CALL_LOG.clear()

    @decorators.traced
    def add(a: int, b: int) -> int:
        return a + b

    @decorators.traced
    def greet(name: str, *, polite: bool = False) -> str:
        return f"Dear {name}" if polite else f"Hi {name}"

    assert decorators.CALL_LOG == []  # デコレータを付けただけでは、呼ばれない
    assert add(1, 2) == 3
    assert greet("Ann", polite=True) == "Dear Ann"
    assert add(b=5, a=4) == 9
    assert decorators.CALL_LOG == ["add", "greet", "add"]


def test_traced_keeps_name_and_doc() -> None:
    @decorators.traced
    def area(w: int, h: int) -> int:
        """長方形の面積。"""
        return w * h

    assert area.__name__ == "area"
    assert area.__doc__ == "長方形の面積。"


def test_traced_logs_even_when_function_raises() -> None:
    decorators.CALL_LOG.clear()

    @decorators.traced
    def boom() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        boom()
    assert decorators.CALL_LOG == ["boom"]


# --- retry ---


def test_retry_returns_first_success() -> None:
    attempts: list[int] = []

    @decorators.retry(3)
    def flaky(x: int) -> int:
        attempts.append(x)
        if len(attempts) < 3:
            raise OSError("まだ失敗する")
        return x * 2

    assert flaky(21) == 42
    assert attempts == [21, 21, 21]


def test_retry_does_not_retry_after_success() -> None:
    calls: list[str] = []

    @decorators.retry(5)
    def fine() -> str:
        calls.append("called")
        return "ok"

    assert fine() == "ok"
    assert calls == ["called"]


def test_retry_reraises_last_error() -> None:
    attempts: list[int] = []

    @decorators.retry(2)
    def always_fails() -> None:
        attempts.append(len(attempts) + 1)
        raise ValueError(f"失敗 {len(attempts)}")

    with pytest.raises(ValueError, match="失敗 2"):
        always_fails()
    assert attempts == [1, 2]


def test_retry_keeps_name() -> None:
    @decorators.retry(2)
    def fetch() -> None:
        """取得する。"""

    assert fetch.__name__ == "fetch"
    assert fetch.__doc__ == "取得する。"


def test_retry_rejects_zero_times() -> None:
    with pytest.raises(ValueError):
        decorators.retry(0)
```

**File:** `phase1_lang/ex02_closure_decorator/test/test_commands.py`
```python
import pytest

from commands import CommandTable, EmptyCommandError, UnknownCommandError


def make_table() -> CommandTable:
    table = CommandTable()

    @table.command("echo")
    def echo(args: list[str]) -> str:
        return " ".join(args)

    @table.command("add")
    def add(args: list[str]) -> str:
        return str(sum(int(a) for a in args))

    return table


def test_dispatch_calls_matching_handler() -> None:
    table = make_table()
    assert table.dispatch("echo hello world") == "hello world"
    assert table.dispatch("add 1 2 3") == "6"


def test_dispatch_splits_on_repeated_spaces() -> None:
    table = make_table()
    assert table.dispatch("  echo   a    b  ") == "a b"


def test_dispatch_with_no_arguments() -> None:
    table = make_table()
    assert table.dispatch("echo") == ""
    assert table.dispatch("add") == "0"


def test_command_returns_handler_unchanged() -> None:
    table = CommandTable()

    def ping(args: list[str]) -> str:
        return "pong"

    registered = table.command("ping")(ping)
    assert registered is ping
    assert ping([]) == "pong"  # 登録したあとも、普通の関数として呼べる
    assert table.dispatch("ping") == "pong"


def test_names_in_registration_order() -> None:
    assert make_table().names() == ["echo", "add"]


def test_empty_line() -> None:
    table = make_table()
    for line in ["", "   "]:
        with pytest.raises(EmptyCommandError):
            table.dispatch(line)


def test_unknown_command() -> None:
    table = make_table()
    with pytest.raises(UnknownCommandError):
        table.dispatch("reboot now")


def test_name_must_match_exactly() -> None:
    table = make_table()
    for line in ["ech hello", "echoo hello", "ECHO hello"]:
        with pytest.raises(UnknownCommandError):
            table.dispatch(line)


def test_duplicate_name_is_rejected() -> None:
    table = make_table()
    with pytest.raises(ValueError):

        @table.command("echo")
        def echo_again(args: list[str]) -> str:
            return ""

    assert table.dispatch("echo still original") == "still original"


def test_tables_do_not_share_handlers() -> None:
    first = make_table()
    second = CommandTable()
    assert first.names() == ["echo", "add"]
    assert second.names() == []


def test_handler_exception_propagates() -> None:
    table = make_table()
    # "add" のハンドラが出す ValueError は、握りつぶさずに呼び出し側へ伝える。
    with pytest.raises(ValueError):
        table.dispatch("add 1 x")
```

- [ ] **Step 2: スタブを作る**

**File:** `phase1_lang/ex02_closure_decorator/src/decorators.py`
```python
"""Part 1: クロージャとデコレータ。"""

from collections.abc import Callable

# traced が、呼ばれた関数の名前を記録していくリスト。
CALL_LOG: list[str] = []


def make_counter() -> Callable[[], int]:
    """呼ぶたびに 1, 2, 3, ... を返す関数を作って返す。

    make_counter を 2 回呼んで作った関数は、互いに独立して数える。
    グローバル変数とクラスは使わない。
    """
    raise NotImplementedError


def make_multipliers(n: int) -> list[Callable[[int], int]]:
    """n 個の関数のリストを返す。i 番目（0 始まり）の関数は、引数を i 倍して返す。"""
    raise NotImplementedError


def traced[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """func を包んだ関数を返すデコレータ。

    包んだ関数は、呼ばれるたびに、func を呼ぶ「前に」func の名前を CALL_LOG へ加える。
    引数はそのまま func に渡し、func の戻り値をそのまま返す。
    包んだ関数の __name__ と __doc__ は、func のものと同じにする。
    """
    raise NotImplementedError


def retry[**P, R](times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """最大 times 回まで呼び直すデコレータを返す。

    包んだ関数は func を呼び、Exception が出たら呼び直す。
    成功したら、その戻り値を返して終わる（それ以上は呼ばない）。
    times 回とも失敗したら、最後の例外をそのまま送出する。
    times が 1 未満なら、retry(times) を呼んだ時点で ValueError。
    包んだ関数の __name__ と __doc__ は、func のものと同じにする。
    """
    raise NotImplementedError
```

**File:** `phase1_lang/ex02_closure_decorator/src/commands.py`
```python
"""Part 2: デコレータでハンドラを登録するコマンド表。

c_master の phase1_lang/ex04_cmd_table と同じ題材。C では {名前, 関数ポインタ} の
配列を手で書いた。Python では、関数の定義にデコレータを付けるだけで表に載る。
"""

from collections.abc import Callable

# ハンドラは、引数（文字列のリスト）を受け取り、応答の文字列を返す。
Handler = Callable[[list[str]], str]


class EmptyCommandError(Exception):
    """行にトークンが 1 つもない。"""


class UnknownCommandError(Exception):
    """先頭のトークンが表にない。"""


class CommandTable:
    def __init__(self) -> None:
        raise NotImplementedError

    def command(self, name: str) -> Callable[[Handler], Handler]:
        """ハンドラを name で登録するデコレータを返す。

        登録したハンドラは包まずに、そのまま返す。
        同じ name がすでに登録されていたら ValueError（表は変えない）。
        """
        raise NotImplementedError

    def names(self) -> list[str]:
        """登録済みの名前を、登録した順に返す。"""
        raise NotImplementedError

    def dispatch(self, line: str) -> str:
        """line を空白（連続してもよい）で区切り、先頭のトークンと同じ名前のハンドラを呼ぶ。

        ハンドラには残りのトークンのリストを渡し、その戻り値を返す。
        トークンが 1 つもなければ EmptyCommandError。
        名前が表になければ UnknownCommandError（名前は完全一致で比べる）。
        どちらの場合も、ハンドラは呼ばない。ハンドラが出した例外は、そのまま伝える。
        """
        raise NotImplementedError
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex02_closure_decorator
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `22 failed`、`rc=2`。lint と type は `rc=0`。
type が `retry` の型（戻り値にしか現れない `P` と `R`）を解決できずにテスト側でエラーを出す場合は、`retry` の戻り値の型を次の `Protocol` に替え、README の骨組みも合わせる。

```python
class Decorator(Protocol):
    def __call__[**P, R](self, func: Callable[P, R], /) -> Callable[P, R]: ...
```

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex02_closure_decorator/decorators.py` と `commands.py` を書く。

```bash
bash $REPO/answers/verify.sh ex02_closure_decorator; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex02_closure_decorator  22 passed ...`、`rc=0`。
`traced` の中の `func.__name__` を mypy が通さない場合は、仕様を変えずに README のヒントへ「名前は `func.__name__` で取れる。mypy に止められたら `getattr(func, "__name__")`」と足す。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex02_closure_decorator/README.md`
````markdown
# Phase 1 / ex02_closure_decorator（クロージャとデコレータ）

## 読み物: 関数もオブジェクト
C の ex04_cmd_table では、関数ポインタを配列に入れて振り分けました。Python では関数そのものがオブジェクトで、変数に入れる、引数で渡す、戻り値で返す、のどれもできます。関数の中で関数を定義することもできます。

```python
def make_adder(n):
    def add(x):
        return x + n     # 外側の関数の変数 n を使っている
    return add

add5 = make_adder(5)     # make_adder はもう終わっている
add5(10)                 # 15。n = 5 を覚えている
```

`add` のように、定義された場所の変数を覚えたまま持ち歩ける関数を、クロージャと呼びます。C の関数ポインタは状態を持てないので、`void *ctx` を別に渡していました。クロージャはその `ctx` を関数が自分で抱えているものです。

注意が2つあります。

- 内側の関数から外側の変数に**代入**するには、`nonlocal n` と宣言します。宣言しないと、内側に同名の新しい変数ができます。読むだけなら宣言は要りません。
- クロージャが覚えるのは変数の「値」ではなく、変数そのものです。ループの中で作った関数がループ変数を使うと、すべての関数がループ終了後の最後の値を見ます。`make_multipliers` でこれを踏みます。

### デコレータ
デコレータは「関数を受け取り、関数を返す関数」です。`@` は次の書き換えの略記にすぎません。

```python
@twice
def hello(name): ...

# 上と同じ意味
def hello(name): ...
hello = twice(hello)
```

型ヒントまで書いた例を1つ示します。この課題のデコレータは、この形を写して中身を変えれば書けます。

```python
import functools
from collections.abc import Callable


def twice[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)                    # wrapper に func の名前と docstring を写す
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        func(*args, **kwargs)                 # 1 回目（戻り値は捨てる）
        return func(*args, **kwargs)          # 2 回目
    return wrapper
```

`[**P, R]` は「`func` の引数の型をまとめて `P`、戻り値の型を `R` と呼ぶ」という宣言です。`Callable[P, R]` を受け取って `Callable[P, R]` を返すので、「包んでも、引数と戻り値の型は変わらない」と読めます。`*args: P.args, **kwargs: P.kwargs` は、どんな引数でもそのまま `func` へ渡すための決まった書き方です。型ヒントは5日目に詳しく扱います。

`@retry(3)` のように引数を取るデコレータは、「デコレータを返す関数」です。関数が3段になります。

```python
def repeat[**P, R](n: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            ...
        return wrapper
    return decorator

# @repeat(3) は f = repeat(3)(f) と同じ
```

## 目的
クロージャが何を覚えているかを確かめ、デコレータを自分で書く。最後に、デコレータで関数を登録するコマンド表を作る。

## 手順
1. `make test` で失敗を確認
2. `src/decorators.py` を上から順に実装する（`make_counter` → `make_multipliers` → `traced` → `retry`）
3. `src/commands.py` を実装する
4. `make check`

## ルール
- `make_counter` は、グローバル変数とクラスを使わない
- `test/` は変更しない

## ヒント
- 内側の関数にも型ヒントが要ります（`def counter() -> int:`）。書かないと `make type` が指摘します
- `make_multipliers` を素直に書いてテストが `[30, 30, 30, 30]` になったら、読み物の注意の2つ目です。`make lint` も同じ場所を指摘します
- `retry` は「最後の1回」をどう扱うかが要点です。mypy に「戻り値のない経路がある」と言われたら、ループの回数と、最後の呼び出しの置き場所を見直します
- `CommandTable.command` が返すデコレータは、関数を包みません。表に載せて、受け取った関数をそのまま返します
- `"  echo   a  ".split()` を対話環境で試す

## 発展課題（任意）
- `functools.wraps` を外すと、どのテストがどう落ちるか
- `help` コマンドを足す。登録済みの名前と、各ハンドラの docstring の1行目を返す
- `traced` に、引数と戻り値も記録させる

## 説明できるようになるべきこと
- クロージャは何を覚えているか。C の関数ポインタと `void *ctx` の組との対応
- `nonlocal` が要る場合と、要らない場合
- ループの中で作った関数が、すべて同じ値を見てしまう理由と、直し方
- `@decorator` を、`@` を使わない代入の形に書き直せること。`@retry(3)` ならどうなるか
- `*args, **kwargs` と `functools.wraps` は、それぞれ何のためにあるか
- C の ex04_cmd_table の表（構造体の配列）と、`CommandTable` の違い
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex02_closure_decorator && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex02_closure_decorator

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 5: phase1_lang/ex03_data_model

`RingBuffer` を、組み込み型と同じ書き方（`len(rb)`、`rb[0]`、`for x in rb`、`rb == other`、`repr(rb)`）で使えるようにする。c_master の C++ 補足（phase3_cpp/ex01_ring_buffer）と同じ題材。

**Files:**
- Create: `phase1_lang/ex03_data_model/{Makefile,README.md,src/ring_buffer.py,test/test_ring_buffer.py}`
- Create（コミットしない）: `answers/phase1_lang/ex03_data_model/ring_buffer.py`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `BufferFullError`、`RingBuffer(capacity)`、`RingBuffer.from_iterable(items, capacity=None)`、プロパティ `capacity`・`is_full`、`push(value)`、`pop()`、`clear()`、`__len__`、`__getitem__`、`__iter__`、`__eq__`、`__repr__`

- [ ] **Step 1: テストを作る**

**File:** `phase1_lang/ex03_data_model/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex03_data_model/test/test_ring_buffer.py`
```python
import pytest

from ring_buffer import BufferFullError, RingBuffer


def filled(*values: object, capacity: int = 4) -> RingBuffer:
    rb = RingBuffer(capacity)
    for v in values:
        rb.push(v)
    return rb


# --- 生成 ---


def test_new_buffer_is_empty() -> None:
    rb = RingBuffer(4)
    assert len(rb) == 0
    assert rb.capacity == 4
    assert not rb.is_full


@pytest.mark.parametrize("capacity", [0, -1])
def test_capacity_must_be_positive(capacity: int) -> None:
    with pytest.raises(ValueError):
        RingBuffer(capacity)


def test_buffers_do_not_share_storage() -> None:
    first = RingBuffer(2)
    second = RingBuffer(2)
    first.push("a")
    assert len(first) == 1
    assert len(second) == 0
    assert list(second) == []


# --- push / pop ---


def test_fifo_order() -> None:
    rb = filled(1, 2, 3)
    assert [rb.pop(), rb.pop(), rb.pop()] == [1, 2, 3]
    assert len(rb) == 0


def test_push_to_full_buffer_raises_and_changes_nothing() -> None:
    rb = filled(1, 2, capacity=2)
    assert rb.is_full
    with pytest.raises(BufferFullError):
        rb.push(3)
    assert list(rb) == [1, 2]


def test_pop_from_empty_buffer_raises_index_error() -> None:
    with pytest.raises(IndexError):
        RingBuffer(2).pop()


def test_wraparound() -> None:
    rb = filled(1, 2, 3, capacity=3)
    assert rb.pop() == 1
    rb.push(4)  # 書き込み位置が、配列の末尾から先頭へ戻る
    assert rb.pop() == 2
    rb.push(5)
    assert list(rb) == [3, 4, 5]
    assert rb.is_full


def test_clear() -> None:
    rb = filled(1, 2, 3)
    rb.clear()
    assert len(rb) == 0
    rb.push(9)
    assert list(rb) == [9]


def test_none_can_be_stored() -> None:
    # None も普通の値として入る。「空き」の目印に None を使うと、ここで個数が狂う。
    rb = filled(None, None)
    assert len(rb) == 2
    assert rb.pop() is None
    assert len(rb) == 1


# --- 組み込み型のように振る舞う ---


def test_truthiness_follows_len() -> None:
    rb = RingBuffer(2)
    assert not rb
    rb.push(0)
    assert rb


def test_iteration_does_not_consume() -> None:
    rb = filled(1, 2, 3)
    assert list(rb) == [1, 2, 3]
    assert list(rb) == [1, 2, 3]
    assert len(rb) == 3


def test_two_iterators_are_independent() -> None:
    rb = filled(1, 2)
    pairs = [(a, b) for a in rb for b in rb]
    assert pairs == [(1, 1), (1, 2), (2, 1), (2, 2)]


def test_indexing() -> None:
    rb = filled(10, 20, 30)
    assert rb[0] == 10
    assert rb[2] == 30
    assert rb[-1] == 30
    assert rb[-3] == 10


def test_indexing_after_wraparound() -> None:
    rb = filled(1, 2, 3, capacity=3)
    rb.pop()
    rb.push(4)
    assert [rb[0], rb[1], rb[2]] == [2, 3, 4]
    assert rb[-1] == 4


@pytest.mark.parametrize("index", [3, -4, 100])
def test_index_out_of_range(index: int) -> None:
    # 容量は 4、要素は 3 個。位置 3 は配列の中だが、要素はない。
    rb = filled(10, 20, 30)
    with pytest.raises(IndexError):
        rb[index]


def test_membership_and_reversed_come_for_free() -> None:
    rb = filled(1, 2, 3)
    assert 2 in rb
    assert 9 not in rb
    assert list(reversed(rb)) == [3, 2, 1]


def test_repr() -> None:
    assert repr(filled(1, 2, 3)) == "RingBuffer([1, 2, 3], capacity=4)"
    assert repr(RingBuffer(2)) == "RingBuffer([], capacity=2)"
    assert repr(filled("a", capacity=1)) == "RingBuffer(['a'], capacity=1)"


def test_equality() -> None:
    assert filled(1, 2) == filled(1, 2)
    assert filled(1, 2) != filled(1, 3)
    assert filled(1, 2) != filled(1, 2, capacity=8)


def test_equality_ignores_internal_position() -> None:
    plain = filled(2, 3, capacity=3)
    wrapped = filled(1, 2, capacity=3)
    wrapped.pop()
    wrapped.push(3)  # 中身は [2, 3] だが、内部の先頭位置は plain と違う
    assert wrapped == plain


def test_equality_with_other_types() -> None:
    rb = filled(1, 2)
    assert rb != [1, 2]
    result: object = rb.__eq__([1, 2])
    assert result is NotImplemented


def test_not_hashable() -> None:
    # __eq__ を定義した可変オブジェクトは、dict のキーや set の要素にできない。
    with pytest.raises(TypeError):
        hash(RingBuffer(2))


# --- プロパティとクラスメソッド ---


def test_capacity_is_read_only() -> None:
    rb = RingBuffer(2)
    name = "capacity"
    with pytest.raises(AttributeError):
        setattr(rb, name, 10)
    assert rb.capacity == 2


def test_is_full_is_a_property() -> None:
    rb = filled(1, capacity=1)
    assert rb.is_full is True
    rb.pop()
    assert rb.is_full is False


def test_from_iterable() -> None:
    rb = RingBuffer.from_iterable([1, 2, 3])
    assert isinstance(rb, RingBuffer)
    assert list(rb) == [1, 2, 3]
    assert rb.capacity == 3
    assert rb.is_full


def test_from_iterable_with_capacity() -> None:
    rb = RingBuffer.from_iterable("ab", capacity=5)
    assert list(rb) == ["a", "b"]
    assert rb.capacity == 5


def test_from_iterable_accepts_a_generator() -> None:
    rb = RingBuffer.from_iterable(n * n for n in range(3))
    assert list(rb) == [0, 1, 4]


def test_from_iterable_too_many_items() -> None:
    with pytest.raises(BufferFullError):
        RingBuffer.from_iterable([1, 2, 3], capacity=2)


def test_from_iterable_empty_without_capacity() -> None:
    with pytest.raises(ValueError):
        RingBuffer.from_iterable([])
```

- [ ] **Step 2: スタブを作る**

**File:** `phase1_lang/ex03_data_model/src/ring_buffer.py`
```python
"""容量固定の FIFO リングバッファ。

c_master の phase3_cpp/ex01_ring_buffer と同じ題材。C++ 版との違い:
  - 失敗は、戻り値の bool ではなく例外で知らせる
  - len(rb)、rb[0]、for x in rb、x in rb、rb == other、print(rb) が、
    組み込み型と同じ書き方で使える

ルール: collections.deque は使わない。格納領域は、長さ capacity の list を
インスタンスごとに 1 つ持つ。
"""

from collections.abc import Iterable, Iterator
from typing import Self


class BufferFullError(Exception):
    """満杯のバッファに push した。"""


class RingBuffer:
    def __init__(self, capacity: int) -> None:
        """容量 capacity の空のバッファを作る。capacity が 1 未満なら ValueError。"""
        raise NotImplementedError

    @classmethod
    def from_iterable(cls, items: Iterable[object], capacity: int | None = None) -> Self:
        """items を順に push したバッファを作って返す。

        capacity を省略したら、items の個数を容量にする（0 個なら ValueError）。
        items が capacity より多ければ BufferFullError。
        """
        raise NotImplementedError

    @property
    def capacity(self) -> int:
        """容量。読み取り専用で、代入すると AttributeError になる。"""
        raise NotImplementedError

    @property
    def is_full(self) -> bool:
        """満杯なら True。"""
        raise NotImplementedError

    def push(self, value: object) -> None:
        """value を末尾に加える。満杯なら、何も変えずに BufferFullError。"""
        raise NotImplementedError

    def pop(self) -> object:
        """最も古い要素を取り出して返す。空なら IndexError。"""
        raise NotImplementedError

    def clear(self) -> None:
        """空にする。容量は変わらない。"""
        raise NotImplementedError

    def __len__(self) -> int:
        """今入っている要素の数。"""
        raise NotImplementedError

    def __getitem__(self, index: int) -> object:
        """古い順で index 番目の要素を返す。取り出しはしない。

        負の添字は末尾から数える（-1 が最も新しい要素）。範囲外なら IndexError。
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[object]:
        """古い順に要素をたどる。取り出しはしない。"""
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        """容量と、古い順に並べた中身が同じなら等しい。

        RingBuffer 以外と比べたときは、NotImplemented を返す。
        """
        raise NotImplementedError

    def __repr__(self) -> str:
        """RingBuffer([1, 2, 3], capacity=4) の形の文字列を返す。"""
        raise NotImplementedError
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex03_data_model
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `31 failed`、`rc=2`。lint と type は `rc=0`。
lint が `test_index_out_of_range` の `rb[index]` に `B018` を出したら、`_ = rb[index]` に替える。
type が `rb != [1, 2]` に `comparison-overlap` を出したら、`other: object = [1, 2]` に入れてから比べる。

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex03_data_model/ring_buffer.py` を書く。

```bash
bash $REPO/answers/verify.sh ex03_data_model; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex03_data_model  31 passed ...`、`rc=0`。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex03_data_model/README.md`
````markdown
# Phase 1 / ex03_data_model（特殊メソッドとクラス）

## 読み物: `len(x)` の中身
Python の組み込みの書き方は、裏で決まった名前のメソッドを呼んでいます。`__len__` のように前後を `__` で挟んだ名前で、特殊メソッドと呼びます。自分のクラスにこれを定義すると、そのクラスのインスタンスが組み込み型と同じ書き方で使えるようになります。

| 書いたコード | Python が呼ぶもの |
|---|---|
| `RingBuffer(4)` | `__init__(self, 4)` |
| `len(rb)` | `rb.__len__()` |
| `rb[i]` | `rb.__getitem__(i)` |
| `for x in rb:` | `rb.__iter__()` が返したものを、1つずつ進める |
| `x in rb` | `__contains__`。なければ `__iter__` でたどって `==` で比べる |
| `rb == other` | `rb.__eq__(other)` |
| `repr(rb)`、対話環境での表示 | `rb.__repr__()` |
| `if rb:` | `__bool__`。なければ `__len__() != 0` |

### `self` は第1引数
`rb.push(1)` は `RingBuffer.push(rb, 1)` と同じ意味です。C で `ring_push(&r, 1)` と書いていた `&r` が `self` で、Python はそれをドットの左から自動で渡します。メソッドの定義に `self` を書くのは、渡されてくる第1引数に名前を付けるためです。

### クラス属性とインスタンス属性
`self.x = ...` と書いた変数はインスタンスごとに1つずつ、クラスの本体に直接書いた変数はクラスに1つだけです。

```python
class Bad:
    items = []                 # クラスに 1 つ。全インスタンスが同じリストを見る

    def add(self, x):
        self.items.append(x)   # 共有のリストを書き換えてしまう


class Good:
    def __init__(self):
        self.items = []        # インスタンスごとに、新しいリストを作る
```

2日目の「名札」の話そのままです。`Bad` では、どのインスタンスの `self.items` も同じ1つのリストを指します。

### メソッドの3種類とプロパティ
| 書き方 | 第1引数 | 使いどころ |
|---|---|---|
| `def push(self, v)` | インスタンス | インスタンスの状態を読み書きする。ほとんどはこれ |
| `@classmethod`<br>`def from_iterable(cls, items)` | クラス | 別の作り方を用意する。`cls(...)` で新しいインスタンスを作って返す |
| `@staticmethod`<br>`def helper(a, b)` | なし | `self` も `cls` も使わないが、このクラスの中に置きたい関数 |
| `@property`<br>`def capacity(self)` | インスタンス | `rb.capacity` と、かっこなしで読ませる。代入はできない |

## 目的
c_master の C++ 補足で書いたリングバッファを、Python の特殊メソッドで「組み込み型のように」使えるクラスにする。仕様は `src/ring_buffer.py` の各 docstring。

## 手順
1. `make test` で失敗を確認
2. `__init__`、`push`、`pop`、`__len__` を先に書く
3. `__iter__`、`__getitem__`、`__eq__`、`__repr__` を書く
4. プロパティと `from_iterable` を書く
5. `make check`

## ルール
- `collections.deque` を使わない。格納領域は、長さ `capacity` の list を1つ
- `test/` は変更しない

## テストについて
- `test_buffers_do_not_share_storage` は、格納領域をクラス属性にすると落ちます
- `test_none_can_be_stored` は、「空き」を `None` で表すと落ちます。個数は別に数えます
- `test_two_iterators_are_independent` は、`__iter__` が `self` を返して位置をインスタンスに持つと落ちます。`__iter__` をジェネレータ（`yield`）で書くのが簡単です。ジェネレータは4日目に扱います
- `test_membership_and_reversed_come_for_free` は、`in` と `reversed()` を使います。`__contains__` と `__reversed__` を書かなくても、`__iter__`、`__len__`、`__getitem__` があれば動きます
- `test_not_hashable` は、何も書かなくても通ります。`__eq__` を定義すると、Python がそのクラスをハッシュ不可にするためです

## ヒント
- 要素の型が `object` なのは、「何でも入る」を型で表すためです。5日目に、要素の型を指定できる書き方を扱います
- `from_iterable` の戻り値の型 `Self` は、「このクラス自身」を表します
- `repr()` の出力には `f"{list(self)!r}"` が使えます。`!r` は `repr()` を通す指定です

## 発展課題（任意）
- 位置を1つ進める計算を `@staticmethod` に切り出す。`self` を使わない関数を、クラスの中に置く意味を考える
- `rb[1:3]` のようなスライスに対応する（`index` が `slice` のときに list を返す）
- `collections.deque(maxlen=4)` と振る舞いを比べる。満杯のときに何が違うか

## 説明できるようになるべきこと
- `rb.push(1)` と `RingBuffer.push(rb, 1)` の関係。`self` とは何か
- クラス属性とインスタンス属性の違い。可変なものをクラス属性にすると何が起きるか
- インスタンスメソッド、`@classmethod`、`@staticmethod` の違いと使い分け
- `__iter__` と `__len__` と `__getitem__` を書くだけで、`in` や `reversed()` が動く理由
- `__eq__` が `NotImplemented` を返すと、Python は次に何をするか
- C++ 版は満杯のとき `false` を返した。Python 版が例外にするのはなぜか。それぞれの利点
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex03_data_model && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex03_data_model

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 6: phase1_lang/ex04_iter_gen

イテレータを手で書く `Countdown`、ジェネレータ関数（`take`、`chunked`、`flatten`）、ログ行の遅延パイプライン（`parse` → `only_level` → `take`）。テストは「何行読まれたか」を数えるイテレータを渡して、必要なぶんしか読まないことを確かめる。

**Files:**
- Create: `phase1_lang/ex04_iter_gen/{Makefile,README.md,src/iters.py,test/test_iters.py}`
- Create（コミットしない）: `answers/phase1_lang/ex04_iter_gen/iters.py`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `LogRecord(level, message)`（提供済みの `NamedTuple`）、`Countdown(start)`、`take(items, n)`、`chunked(items, size)`、`flatten(nested)`、`parse(lines)`、`only_level(records, level)`、`first_errors(lines, n) -> list[str]`

- [ ] **Step 1: テストを作る**

**File:** `phase1_lang/ex04_iter_gen/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex04_iter_gen/test/test_iters.py`
```python
from collections.abc import Iterator

import pytest

import iters
from iters import LogRecord


class CountingLines:
    """何行読まれたかを数えるイテレータ。遅延評価の確認に使う。"""

    def __init__(self, lines: list[str]) -> None:
        self._lines = iter(lines)
        self.consumed = 0

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        line = next(self._lines)
        self.consumed += 1
        return line


def naturals() -> Iterator[int]:
    """0, 1, 2, ... と終わりなく続くジェネレータ。"""
    n = 0
    while True:
        yield n
        n += 1


# --- Countdown ---


def test_countdown() -> None:
    assert list(iters.Countdown(3)) == [3, 2, 1]


@pytest.mark.parametrize("start", [0, -2])
def test_countdown_from_non_positive_is_empty(start: int) -> None:
    assert list(iters.Countdown(start)) == []


def test_countdown_is_its_own_iterator() -> None:
    countdown = iters.Countdown(2)
    assert iter(countdown) is countdown


def test_countdown_is_exhausted_after_one_pass() -> None:
    countdown = iters.Countdown(2)
    assert list(countdown) == [2, 1]
    assert list(countdown) == []


def test_countdown_next_by_hand() -> None:
    countdown = iters.Countdown(2)
    assert next(countdown) == 2
    assert next(countdown) == 1
    with pytest.raises(StopIteration):
        next(countdown)
    with pytest.raises(StopIteration):
        next(countdown)


# --- take ---


def test_take() -> None:
    assert list(iters.take([1, 2, 3, 4], 2)) == [1, 2]
    assert list(iters.take([1, 2], 5)) == [1, 2]
    assert list(iters.take([1, 2], 0)) == []


def test_take_works_on_infinite_input() -> None:
    assert list(iters.take(naturals(), 3)) == [0, 1, 2]


def test_take_is_lazy() -> None:
    lines = CountingLines(["a", "b", "c", "d"])
    result = iters.take(lines, 2)
    assert lines.consumed == 0  # 作っただけでは、1 行も読まない
    assert list(result) == ["a", "b"]
    assert lines.consumed == 2  # 3 行目を読みにいかない


def test_take_zero_reads_nothing() -> None:
    lines = CountingLines(["a", "b"])
    assert list(iters.take(lines, 0)) == []
    assert lines.consumed == 0


# --- chunked ---


def test_chunked() -> None:
    assert list(iters.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(iters.chunked([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]
    empty: list[int] = []
    assert list(iters.chunked(empty, 3)) == []


def test_chunked_yields_independent_lists() -> None:
    chunks = list(iters.chunked([1, 2, 3, 4], 2))
    assert chunks[0] is not chunks[1]
    chunks[0].append(99)
    assert chunks[1] == [3, 4]


def test_chunked_is_lazy() -> None:
    chunks = iters.chunked(naturals(), 3)
    assert next(chunks) == [0, 1, 2]
    assert next(chunks) == [3, 4, 5]


@pytest.mark.parametrize("size", [0, -1])
def test_chunked_rejects_bad_size(size: int) -> None:
    with pytest.raises(ValueError):
        list(iters.chunked([1, 2, 3], size))


# --- flatten ---


def test_flatten() -> None:
    assert list(iters.flatten([1, [2, 3], [[4], 5], []])) == [1, 2, 3, 4, 5]


def test_flatten_keeps_strings_and_tuples_whole() -> None:
    assert list(iters.flatten(["ab", ["cd", (1, 2)]])) == ["ab", "cd", (1, 2)]


def test_flatten_is_lazy() -> None:
    def source() -> Iterator[object]:
        yield [1, [2]]
        yield 3
        raise AssertionError("ここまで読んではいけない")

    result = iters.flatten(source())
    assert [next(result), next(result), next(result)] == [1, 2, 3]


# --- ログのパイプライン ---

LOG = [
    "INFO boot",
    "",
    "# comment",
    "ERROR disk full",
    "  WARN  low battery  ",
    "ERROR",
    "ERROR net down",
    "INFO done",
]


def test_parse() -> None:
    assert list(iters.parse(LOG)) == [
        LogRecord("INFO", "boot"),
        LogRecord("ERROR", "disk full"),
        LogRecord("WARN", "low battery"),
        LogRecord("ERROR", ""),
        LogRecord("ERROR", "net down"),
        LogRecord("INFO", "done"),
    ]


def test_parse_is_lazy() -> None:
    lines = CountingLines(LOG)
    records = iters.parse(lines)
    assert lines.consumed == 0
    assert next(records) == LogRecord("INFO", "boot")
    assert lines.consumed == 1


def test_only_level() -> None:
    records = [LogRecord("INFO", "a"), LogRecord("ERROR", "b"), LogRecord("ERROR", "c")]
    errors = list(iters.only_level(records, "ERROR"))
    assert errors == [LogRecord("ERROR", "b"), LogRecord("ERROR", "c")]
    assert list(iters.only_level(records, "DEBUG")) == []


def test_first_errors() -> None:
    assert iters.first_errors(LOG, 2) == ["disk full", ""]
    assert iters.first_errors(LOG, 10) == ["disk full", "", "net down"]
    assert iters.first_errors(LOG, 0) == []


def test_first_errors_stops_reading_early() -> None:
    lines = CountingLines(LOG)
    assert iters.first_errors(lines, 1) == ["disk full"]
    assert lines.consumed == 4  # "ERROR disk full" までの 4 行


def test_first_errors_on_endless_log() -> None:
    def endless() -> Iterator[str]:
        n = 0
        while True:
            n += 1
            yield f"ERROR e{n}" if n % 2 == 0 else f"INFO i{n}"

    assert iters.first_errors(endless(), 3) == ["e2", "e4", "e6"]
```

- [ ] **Step 2: スタブを作る**

**File:** `phase1_lang/ex04_iter_gen/src/iters.py`
```python
"""イテレータとジェネレータ。

ルール: itertools は使わない。Countdown 以外は、ジェネレータ（yield）で書く。
"""

from collections.abc import Iterable, Iterator
from typing import NamedTuple


class LogRecord(NamedTuple):
    """ログ 1 行ぶん。提供済み。変更しない。"""

    level: str
    message: str


class Countdown:
    """start, start - 1, ..., 1 を順に返すイテレータ。

    yield を使わずに、__iter__ と __next__ を自分で書く。
    start が 0 以下なら、何も返さずに終わる。
    最後まで進んだあとは、何度 next() しても StopIteration。
    """

    def __init__(self, start: int) -> None:
        raise NotImplementedError

    def __iter__(self) -> "Countdown":
        """イテレータは、自分自身を返す。"""
        raise NotImplementedError

    def __next__(self) -> int:
        raise NotImplementedError


def take[T](items: Iterable[T], n: int) -> Iterator[T]:
    """items の先頭から最大 n 個を順に返す。

    n 個を返したら、それ以上 items を読まない。n が 0 以下なら、1 個も読まない。
    """
    raise NotImplementedError


def chunked[T](items: Iterable[T], size: int) -> Iterator[list[T]]:
    """items を size 個ずつのリストに区切って、順に返す。

    最後のリストは size 個に満たなくてよい。空のリストは返さない。
    返すリストは、毎回新しいリストにする。size が 1 未満なら ValueError。
    """
    raise NotImplementedError


def flatten(nested: Iterable[object]) -> Iterator[object]:
    """入れ子になった list を、奥まで平らにして順に返す。

    list 以外（str や tuple を含む）は、それ以上ほどかずに 1 つの要素として返す。
    """
    raise NotImplementedError


def parse(lines: Iterable[str]) -> Iterator[LogRecord]:
    """ "LEVEL message" 形式の行を、LogRecord に変換して順に返す。

    行の前後の空白を取り除いてから判定する。空行と、"#" で始まる行は読み飛ばす。
    LEVEL は最初の空白までの部分。message はその残りで、前後の空白を取り除く。
    LEVEL だけの行は、message を空文字列にする。
    """
    raise NotImplementedError


def only_level(records: Iterable[LogRecord], level: str) -> Iterator[LogRecord]:
    """level が一致する LogRecord だけを、順に返す。"""
    raise NotImplementedError


def first_errors(lines: Iterable[str], n: int) -> list[str]:
    """lines のうち level が "ERROR" の行の message を、先頭から最大 n 個、リストで返す。

    parse、only_level、take をつないで書く。n 個見つかったら、残りの行は読まない。
    """
    raise NotImplementedError
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex04_iter_gen
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `24 failed`、`rc=2`。lint と type は `rc=0`。

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex04_iter_gen/iters.py` を書く。

```bash
bash $REPO/answers/verify.sh ex04_iter_gen; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex04_iter_gen  24 passed ...`、`rc=0`。
追加の確認: `take` を `enumerate` で数えて `i >= n` で抜ける素直な版に書き換えた一時コピーで、`test_take_is_lazy` が落ちること（Review Focus 3）。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex04_iter_gen/README.md`
````markdown
# Phase 1 / ex04_iter_gen（イテレータとジェネレータ）

## 読み物: `for` 文の中身
`for x in xs:` は、次のコードと同じことをしています。

```python
it = iter(xs)              # xs.__iter__() を呼び、イテレータを受け取る
while True:
    try:
        x = next(it)       # it.__next__() を呼び、次の値を受け取る
    except StopIteration:  # 「もうない」は、例外で知らせる
        break
    ...                    # ループの本体
```

登場するものが2つあります。

- イテラブル: `__iter__` を持ち、イテレータを作れるもの。list、str、dict、3日目の `RingBuffer` など。何度でもたどれます
- イテレータ: `__next__` を持ち、「今どこまで進んだか」を覚えているもの。1回たどると使い切りです

C で配列を走査するときの添字 `i` にあたるものを、オブジェクトとして切り出したのがイテレータです。

### ジェネレータ
`__iter__` と `__next__` を毎回手で書くのは面倒なので、`yield` を使った関数で書けるようになっています。

```python
def countdown(n):
    while n > 0:
        yield n        # 値を 1 つ渡して、ここで止まる。次の next() で続きから再開する
        n -= 1
```

`yield` を含む関数は、呼んでも本体が1行も実行されません。イテレータ（ジェネレータ）が返るだけです。`next()` されるたびに、次の `yield` まで進んで止まります。ローカル変数は止まっている間も残ります。

### 遅延評価
ジェネレータは、求められた分しか計算しません。そのため、次のことができます。

- 終わりのない列を扱う（先頭の3個だけ取る、など）
- 大きなファイルを、1行ぶんのメモリで処理する
- 「読む」「変換する」「絞り込む」「数を限る」を別々の関数に分け、つないで使う

C で `fgets` のループの中に解析と絞り込みを全部書いていた処理を、メモリの使い方はそのままに、部品へ分けられます。`yield from other` は、別のイテラブルの要素をそのまま順に `yield` する書き方です。

## 目的
イテレータの決まりごとを手で書いて確かめ、ジェネレータで遅延パイプラインを組む。仕様は `src/iters.py` の各 docstring。

## 手順
1. `make test` で失敗を確認
2. `Countdown` を、`yield` を使わずに書く
3. `take`、`chunked`、`flatten` を、ジェネレータで書く
4. `parse`、`only_level`、`first_errors` を書く
5. `make check`

## ルール
- `itertools` を使わない（発展課題で置き換えます）
- `test/` は変更しない

## テストについて
- `CountingLines` は、何行読まれたかを数えるイテレータです。`test_take_is_lazy` は、2個取るのに3行目まで読んでいたら落ちます
- `test_chunked_yields_independent_lists` は、1つのリストを使い回して `clear()` していると落ちます（2日目の別名の話）
- `test_first_errors_on_endless_log` は、終わりのないログを渡します。どこかでリストに全部ためていると、テストが終わりません

## ヒント
- `Countdown` は、`__iter__` で `self` を返し、`__next__` で値を返すか `raise StopIteration` します
- `take` で `for i, item in enumerate(items):` と書くと、`n` 個目を返したあとにもう1個読んでしまいます。「返してから数え、足りたらすぐ抜ける」順にします
- `flatten` は、要素が list なら自分自身を呼びます。`yield from` が使えます
- `"ERROR disk full".split(maxsplit=1)` と `"ERROR".split(maxsplit=1)` を対話環境で試す

## 発展課題（任意）
- `take` を `itertools.islice` で、`chunked` を `itertools.batched` で置き換える
- `first_errors` を、ジェネレータ式 `(r.message for r in ...)` を使って書き直す
- `sum(x * x for x in range(10**7))` と `sum([x * x for x in range(10**7)])` で、メモリの使い方がどう違うか

## 説明できるようになるべきこと
- `for` 文が裏で呼んでいるもの。イテラブルとイテレータの違い
- イテレータは1回で使い切りなのに、list は何度でも `for` で回せる理由
- `yield` を含む関数を呼んだとき、何が起きて、何が起きないか
- 遅延評価の利点。`first_errors` が、必要な行までしか読まない仕組み
- `chunked` に `size=0` を渡したとき、`ValueError` が出るのは `chunked(...)` を呼んだ時点か、最初の `next()` の時点か。なぜか
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex04_iter_gen && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex04_iter_gen

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 7: phase1_lang/ex05_context

例外の階層と `raise ... from`（`config.py`）、`__enter__`／`__exit__` を書く `Transaction` と、`@contextmanager` で書く `temporary_attr`（`resources.py`）。

**Files:**
- Create: `phase1_lang/ex05_context/{Makefile,README.md,src/config.py,src/resources.py,test/test_config.py,test/test_resources.py}`
- Create（コミットしない）: `answers/phase1_lang/ex05_context/{config.py,resources.py}`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `ConfigError`（提供済み）、`MissingKeyError`、`InvalidValueError`（学習者が定義する）、`parse_config(text) -> dict[str, str]`、`get_int(config, key) -> int`
- Produces: `Transaction(target)`（`with` で作業用の辞書を返す）、`temporary_attr(obj, name, value)`

- [ ] **Step 1: テストを作る**

**File:** `phase1_lang/ex05_context/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex05_context/test/test_config.py`
```python
import pytest

import config


def test_exception_hierarchy() -> None:
    assert issubclass(config.ConfigError, Exception)
    assert issubclass(config.MissingKeyError, config.ConfigError)
    assert issubclass(config.InvalidValueError, config.ConfigError)
    assert not issubclass(config.MissingKeyError, config.InvalidValueError)
    assert not issubclass(config.InvalidValueError, config.MissingKeyError)


def test_parse_config() -> None:
    text = """
    # サーバの設定
    host = example.com
    port=8080

    url = http://example.com/?a=1
    """
    assert config.parse_config(text) == {
        "host": "example.com",
        "port": "8080",
        "url": "http://example.com/?a=1",
    }


def test_parse_config_empty_text() -> None:
    assert config.parse_config("") == {}


def test_parse_config_later_value_wins() -> None:
    assert config.parse_config("a = 1\na = 2") == {"a": "2"}


def test_parse_config_allows_empty_value() -> None:
    assert config.parse_config("name =") == {"name": ""}


@pytest.mark.parametrize(
    ("text", "line_number"),
    [
        ("host example.com", "1"),  # "=" がない
        ("a = 1\n\n= 5", "3"),  # key が空。空行も 1 行に数える
        ("a = 1\nb = 2\noops\nc = 3", "3"),
    ],
)
def test_parse_config_reports_line_number(text: str, line_number: str) -> None:
    with pytest.raises(config.ConfigError, match=line_number):
        config.parse_config(text)


def test_get_int() -> None:
    assert config.get_int({"port": "8080"}, "port") == 8080
    assert config.get_int({"offset": " -5 "}, "offset") == -5


def test_get_int_missing_key() -> None:
    with pytest.raises(config.MissingKeyError, match="port"):
        config.get_int({"host": "example.com"}, "port")


def test_get_int_invalid_value_keeps_cause() -> None:
    with pytest.raises(config.InvalidValueError, match="port") as excinfo:
        config.get_int({"port": "80a"}, "port")
    assert isinstance(excinfo.value.__cause__, ValueError)


def test_errors_can_be_caught_as_config_error() -> None:
    missing: dict[str, str] = {}
    invalid = {"port": "x"}
    for cfg in [missing, invalid]:
        with pytest.raises(config.ConfigError):
            config.get_int(cfg, "port")
```

**File:** `phase1_lang/ex05_context/test/test_resources.py`
```python
import pytest

from resources import Transaction, temporary_attr

# --- Transaction ---


def test_transaction_commits_on_success() -> None:
    settings = {"host": "a", "port": "80"}
    with Transaction(settings) as draft:
        draft["port"] = "8080"
        draft["debug"] = "1"
        del draft["host"]
        assert settings == {"host": "a", "port": "80"}  # まだ反映されない
    assert settings == {"port": "8080", "debug": "1"}


def test_transaction_draft_is_a_copy() -> None:
    settings = {"a": "1"}
    with Transaction(settings) as draft:
        assert draft == {"a": "1"}
        assert draft is not settings


def test_transaction_rolls_back_on_error() -> None:
    settings = {"host": "a"}
    with pytest.raises(RuntimeError, match="途中で失敗"):
        with Transaction(settings) as draft:
            draft["host"] = "b"
            raise RuntimeError("途中で失敗")
    assert settings == {"host": "a"}


def test_transaction_can_be_used_repeatedly() -> None:
    settings = {"n": "0"}
    for value in ["1", "2"]:
        with Transaction(settings) as draft:
            draft["n"] = value
    assert settings == {"n": "2"}


# --- temporary_attr ---


class Screen:
    def __init__(self) -> None:
        self.color = "white"


def test_temporary_attr_sets_and_restores() -> None:
    screen = Screen()
    with temporary_attr(screen, "color", "red"):
        assert screen.color == "red"
    assert screen.color == "white"


def test_temporary_attr_restores_on_error() -> None:
    screen = Screen()
    with pytest.raises(KeyError):
        with temporary_attr(screen, "color", "red"):
            raise KeyError("boom")
    assert screen.color == "white"


def test_temporary_attr_requires_existing_attribute() -> None:
    screen = Screen()
    with pytest.raises(AttributeError):
        with temporary_attr(screen, "size", 10):
            pytest.fail("ブロックに入ってはいけない")
    assert not hasattr(screen, "size")


def test_temporary_attr_can_nest() -> None:
    screen = Screen()
    with temporary_attr(screen, "color", "red"):
        with temporary_attr(screen, "color", "blue"):
            assert screen.color == "blue"
        assert screen.color == "red"
    assert screen.color == "white"
```

- [ ] **Step 2: スタブを作る**

**File:** `phase1_lang/ex05_context/src/config.py`
```python
"""Part 1: 例外の階層と、原因を残した送出。"""


class ConfigError(Exception):
    """この課題の例外すべての親。提供済み。"""


# ここに、次の 2 つの例外クラスを定義する。どちらも ConfigError の子にする。
#   MissingKeyError    必要な key がない
#   InvalidValueError  値の形式が正しくない


def parse_config(text: str) -> dict[str, str]:
    """ "key = value" 形式のテキストを、辞書にして返す。

    - 行の前後の空白を取り除いてから判定する。空行と、"#" で始まる行は読み飛ばす
    - "=" は最初の 1 つで区切る（value は "=" を含んでよい）
    - key と value の前後の空白は取り除く。value は空でもよい
    - "=" がない行と、key が空の行は ConfigError。メッセージに行番号を含める
      （行番号は 1 始まりで、空行やコメント行も 1 行に数える）
    - 同じ key が 2 回出たら、後の値で上書きする
    """
    raise NotImplementedError


def get_int(config: dict[str, str], key: str) -> int:
    """config[key] を int に変換して返す。

    - key がなければ MissingKeyError。メッセージに key を含める
    - int に変換できなければ InvalidValueError。メッセージに key を含め、
      元の ValueError を原因（__cause__）として残す
    """
    raise NotImplementedError
```

**File:** `phase1_lang/ex05_context/src/resources.py`
```python
"""Part 2: コンテキストマネージャ。"""

from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType


class Transaction:
    """辞書への変更を、with ブロックが正常に終わったときだけ反映する。

        with Transaction(settings) as draft:
            draft["port"] = "8080"      # この時点では、settings は変わらない
        # ここで settings に反映される

    - __enter__ は、target の浅いコピー（作業用の辞書）を返す
    - ブロックが正常に終わったら、target の中身を、作業用の辞書の中身に置き換える
      （target という辞書オブジェクト自体は、同じものを使い続ける）
    - ブロックの中で例外が出たら、target は変えない。例外は握りつぶさずに外へ伝える
    """

    def __init__(self, target: dict[str, str]) -> None:
        raise NotImplementedError

    def __enter__(self) -> dict[str, str]:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError


@contextmanager
def temporary_attr(obj: object, name: str, value: object) -> Iterator[None]:
    """with ブロックの間だけ obj の属性 name を value に変え、抜けるときに元の値へ戻す。

    ブロックの中で例外が出ても、必ず元に戻す。例外は握りつぶさない。
    name という属性がもともとなければ AttributeError（ブロックには入らない）。
    """
    raise NotImplementedError
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex05_context
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `20 failed`、`rc=2`（`test_config.py` の収集は通ること）。lint は `rc=0`。type は `rc=2` で、指摘は `test/test_config.py` の `MissingKeyError` と `InvalidValueError`（まだ定義されていない）だけ。

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex05_context/config.py` と `resources.py` を書く。

```bash
bash $REPO/answers/verify.sh ex05_context; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex05_context  20 passed ...`、`rc=0`。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex05_context/README.md`
````markdown
# Phase 1 / ex05_context（例外とコンテキストマネージャ）

## 読み物: 失敗の伝え方と、後片付けの保証
C の ex04_cmd_table では、失敗を `CMD_ERR_UNKNOWN` のような負の戻り値で伝えました。呼び出し側が戻り値を調べ忘れると、失敗は黙って無視されます。Python の例外は逆で、誰も受け取らなければプログラムが止まります。無視するには `except` を書く必要があります。

### 例外はクラスの階層
`except SomeError:` は、`SomeError` とその子クラスをすべて受け取ります。そこで、自分のモジュールの例外には共通の親を1つ作り、細かい種類を子にします。使う側は、まとめて受けたければ親を、区別したければ子を書けます。

```python
class AppError(Exception): ...
class NotFound(AppError): ...

try:
    ...
except NotFound:        # 細かい種類を先に書く
    ...
except AppError:        # 残りをまとめて受ける
    ...
```

### 原因を残す
低い層の例外（`ValueError` など）を、自分の例外に付け替えて出し直すときは、`raise 新しい例外 from 元の例外` と書きます。元の例外が `__cause__` に残り、トレースバックに両方が表示されます。`from` を付けないと、「例外の処理中に別の例外が起きた」という、事故のような表示になります。

### `with` 文
C では、途中で失敗しても後片付けを通すために `goto cleanup;` を使いました。C++ はそれをデストラクタに任せました（RAII）。Python でこれにあたるのが `with` 文です。

```python
with open(path) as f:      # 入るときに __enter__() が呼ばれ、その戻り値が f になる
    data = f.read()
# ブロックを抜けるときに、例外が出ていても必ず __exit__() が呼ばれる（ここで閉じる）
```

`__exit__(self, exc_type, exc, tb)` の3つの引数には、ブロックの中で出た例外の情報が入ります。正常に終わったときは3つとも `None` です。`__exit__` が `True` を返すと例外は握りつぶされ、`None` や `False` なら外へ伝わります。この課題の `__exit__` は戻り値の型を `None` にしてあるので、握りつぶす書き方は mypy が止めます。

クラスを書かずに済ませる方法もあります。`@contextmanager` を付けたジェネレータ関数では、`yield` の前が `__enter__`、後が `__exit__` にあたります。後片付けは `try: yield` と `finally:` で挟みます。

## 目的
例外の階層を作って原因を残す書き方と、後片付けを保証するコンテキストマネージャの2通りの書き方（クラス、`@contextmanager`）を身につける。仕様は `src/config.py` と `src/resources.py` の各 docstring。

## 手順
1. `make test` で失敗を確認
2. `src/config.py` に例外クラスを2つ定義し、`parse_config` と `get_int` を実装する
3. `src/resources.py` の `Transaction` と `temporary_attr` を実装する
4. `make check`

## ルール
- `except:` と `except Exception:` で何でも受けない。受ける例外の種類を書く
- `test/` は変更しない

## ヒント
- `enumerate(text.splitlines(), start=1)` で、行番号と行を同時に取れます
- `"url = http://x/?a=1".partition("=")` を対話環境で試す
- `Transaction.__exit__` で「正常に終わったか」は `exc_type is None` で分かります
- `target = draft` と書いても、呼び出し側の辞書は変わりません（2日目の名札の話）。`target` の中身を書き換えます
- `temporary_attr` は、`getattr`、`setattr`、`try`／`finally` で書けます

## 発展課題（任意）
- `get_int` の `from e` を外して `make test` し、失敗するテストとトレースバックの表示を見る
- 指定した種類の例外だけを握りつぶすコンテキストマネージャ `ignoring(*exc_types)` を、クラスで書く。標準の `contextlib.suppress` と比べる
- `Transaction` を2つ入れ子にして、内側だけ失敗させる。どちらの変更が残るか

## 説明できるようになるべきこと
- 戻り値でエラーを返す方式と例外の、それぞれの利点と欠点
- 例外に共通の親クラスを作る理由。`except` を書く順番
- `raise X from e` は何を残すか。付けないとどう表示されるか
- `with` 文が保証すること。C の `goto cleanup`、C++ の RAII との対応
- `__exit__` の引数と戻り値の意味
- `@contextmanager` の関数で、`yield` を `try`／`finally` で挟まないと何が起きるか
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex05_context && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex05_context

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 8: phase1_lang/ex06_typing

型ヒントを学習者が書く課題。`src/typed.py` の本体は動く状態で提供し、型ヒントだけを書いていない。型の正しさは `typecases/` で確かめる。テストが mypy を子プロセスで呼び、`ok_*.py` はエラーなし、`ng_*.py` は「# NG」の行だけがエラーになることを検査する。設計書5章の「テストから mypy を呼んで検査できる」をここで確かめる。

**Files:**
- Create: `phase1_lang/ex06_typing/{Makefile,README.md,src/typed.py,test/test_typed.py,test/test_typecases.py}`
- Create: `phase1_lang/ex06_typing/typecases/{ok_generics.py,ng_generics.py,ok_optional.py,ng_optional.py,ok_protocol.py,ng_protocol.py}`
- Create（コミットしない）: `answers/phase1_lang/ex06_typing/typed.py`

**Interfaces:**
- Consumes: `common/common.mk`、`answers/verify.sh`（Task 1）
- Produces: `first(items)`、`find_user(users, user_id)`、`greeting(users, user_id)`、`Stack`（`push`、`pop`、`peek`、`__len__`）、`Shape`（学習者が定義する `Protocol`）、`total_area(shapes)`

- [ ] **Step 1: テストと typecases を作る**

**File:** `phase1_lang/ex06_typing/Makefile`
```make
include ../../common/common.mk
```

**File:** `phase1_lang/ex06_typing/test/test_typed.py`
```python
"""実行時の振る舞いのテスト。型の検査は test_typecases.py が行う。"""

import pytest

import typed


def test_first() -> None:
    assert typed.first([3, 1, 2]) == 3
    assert typed.first(("a", "b")) == "a"
    empty: list[int] = []
    assert typed.first(empty) is None


def test_find_user() -> None:
    users = {1: "Ann"}
    assert typed.find_user(users, 1) == "Ann"
    assert typed.find_user(users, 2) is None


def test_greeting() -> None:
    assert typed.greeting({1: "Ann"}, 1) == "Hello, Ann!"


def test_greeting_for_unknown_user() -> None:
    assert typed.greeting({1: "Ann"}, 2) == "Hello, guest!"


def test_stack() -> None:
    stack: typed.Stack[int] = typed.Stack()
    assert stack.peek() is None
    stack.push(1)
    stack.push(2)
    assert len(stack) == 2
    assert stack.peek() == 2
    assert stack.pop() == 2
    assert stack.pop() == 1
    with pytest.raises(IndexError):
        stack.pop()


class Rect:
    def __init__(self, w: float, h: float) -> None:
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h


def test_total_area() -> None:
    assert typed.total_area([Rect(1, 2), Rect(3, 4)]) == pytest.approx(14.0)
    assert typed.total_area([]) == 0
```

**File:** `phase1_lang/ex06_typing/test/test_typecases.py`
```python
"""typecases/ の各ファイルを mypy --strict にかけて、型ヒントの正しさを確かめる。

ok_*.py は、エラーなしで通らなければならない。
ng_*.py は、「# NG」と書いた行だけがエラーにならなければならない。
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

EXERCISE = Path(__file__).resolve().parent.parent
CASES = sorted((EXERCISE / "typecases").glob("*.py"))
OK_CASES = [p for p in CASES if p.name.startswith("ok_")]
NG_CASES = [p for p in CASES if p.name.startswith("ng_")]
ERROR_LINE = re.compile(r"^(?P<path>.+?):(?P<line>\d+): error: (?P<message>.*)$")


@pytest.fixture(scope="module")
def mypy_errors() -> dict[str, dict[int, str]]:
    """src/typed.py と typecases/ をまとめて mypy にかけ、{ファイル名: {行番号: メッセージ}} を返す。"""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mypy",
            "--strict",
            "--no-error-summary",
            "--no-color-output",
            str(EXERCISE / "src" / "typed.py"),
            *(str(p) for p in CASES),
        ],
        capture_output=True,
        text=True,
        cwd=EXERCISE,
        env=env,
        check=False,
    )
    # 0 はエラーなし、1 は型エラーあり。それ以外は mypy 自体が動いていない。
    assert result.returncode in (0, 1), result.stderr
    errors: dict[str, dict[int, str]] = {}
    for raw in result.stdout.splitlines():
        match = ERROR_LINE.match(raw)
        if match:
            errors.setdefault(Path(match["path"]).name, {})[int(match["line"])] = match["message"]
    return errors


def marked_lines(path: Path) -> set[int]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return {number for number, line in enumerate(lines, start=1) if line.rstrip().endswith("# NG")}


def require_clean_module(errors: dict[str, dict[int, str]]) -> None:
    # typed.py 自体に型エラーがあると、使う側のエラーが「型ヒントがないから」なのか
    # 「使い方が間違っているから」なのか区別できない。先にそちらをなくす。
    assert errors.get("typed.py", {}) == {}, "先に src/typed.py 自体の型エラーをなくす"


def test_cases_exist() -> None:
    # typecases/ が見つからないと、下のテストが 0 件になって素通りしてしまう。
    assert len(OK_CASES) == 3
    assert len(NG_CASES) == 3


def test_typed_module_has_no_type_errors(mypy_errors: dict[str, dict[int, str]]) -> None:
    require_clean_module(mypy_errors)


@pytest.mark.parametrize("case", OK_CASES, ids=lambda p: p.name)
def test_ok_case_passes(case: Path, mypy_errors: dict[str, dict[int, str]]) -> None:
    require_clean_module(mypy_errors)
    assert mypy_errors.get(case.name, {}) == {}


@pytest.mark.parametrize("case", NG_CASES, ids=lambda p: p.name)
def test_ng_case_is_rejected_only_on_marked_lines(
    case: Path, mypy_errors: dict[str, dict[int, str]]
) -> None:
    require_clean_module(mypy_errors)
    assert set(mypy_errors.get(case.name, {})) == marked_lines(case)
```

**File:** `phase1_lang/ex06_typing/typecases/ok_generics.py`
```python
"""mypy --strict を通らなければならない使い方。"""

from typed import Stack, first

numbers: Stack[int] = Stack()
numbers.push(1)
n: int = numbers.pop()
top: int | None = numbers.peek()
size: int = len(numbers)

words: Stack[str] = Stack()
words.push("a")
w: str = words.pop()

head_int: int | None = first([1, 2, 3])
head_str: str | None = first(("a", "b"))
```

**File:** `phase1_lang/ex06_typing/typecases/ng_generics.py`
```python
"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import Stack, first

numbers: Stack[int] = Stack()
numbers.push("one")  # NG
text: str = numbers.pop()  # NG
value: int = first([1, 2, 3])  # NG
```

**File:** `phase1_lang/ex06_typing/typecases/ok_optional.py`
```python
"""mypy --strict を通らなければならない使い方。"""

from typed import find_user, greeting

users = {1: "Ann", 2: "Bob"}
name: str | None = find_user(users, 1)
message: str = greeting(users, 3)
if name is not None:
    upper: str = name.upper()
```

**File:** `phase1_lang/ex06_typing/typecases/ng_optional.py`
```python
"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import find_user

users = {1: "Ann"}
name: str = find_user(users, 1)  # NG
length: int = len(find_user(users, 2))  # NG
find_user(users, "1")  # NG
```

**File:** `phase1_lang/ex06_typing/typecases/ok_protocol.py`
```python
"""mypy --strict を通らなければならない使い方。"""

from typed import Shape, total_area


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius**2


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


# Circle も Square も Shape を継承していない。area() を持つので、Shape として通る。
total: float = total_area([Circle(1.0), Square(2.0)])
total_from_generator: float = total_area(Square(float(n)) for n in range(3))
one: Shape = Circle(1.0)
```

**File:** `phase1_lang/ex06_typing/typecases/ng_protocol.py`
```python
"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import Shape, total_area


class Line:
    def __init__(self, length: float) -> None:
        self.length = length


class Label:
    def area(self) -> str:
        return "big"


total_area([1, 2, 3])  # NG
total_area([Line(1.0)])  # NG
bad: Shape = Label()  # NG
```

- [ ] **Step 2: 型ヒントのないスタブを作る**

**File:** `phase1_lang/ex06_typing/src/typed.py`
```python
"""型ヒントを書く課題。このファイルには、わざと型ヒントを書いていない。

本体は、1 か所を除いてすでに動く。やることは 4 つ。
  1. すべての関数とメソッドに型ヒントを書く
  2. Stack をジェネリックにする（Stack[int] と Stack[str] を区別できるように）
  3. Shape を Protocol として定義する
  4. 型ヒントを書くと mypy が見つけるバグを 1 つ直す
"""


def first(items):
    """items の先頭の要素を返す。空なら None を返す。list でも tuple でも受け取れる。"""
    if not items:
        return None
    return items[0]


def find_user(users, user_id):
    """users（ID の整数 → 名前の文字列）から名前を探す。なければ None を返す。"""
    return users.get(user_id)


def greeting(users, user_id):
    """ "Hello, <名前>!" を返す。user_id が users になければ "Hello, guest!" を返す。"""
    name = find_user(users, user_id)
    return "Hello, " + name + "!"


class Stack:
    """後入れ先出しのスタック。"""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        """最後に積んだ要素を取り出して返す。空なら IndexError。"""
        return self._items.pop()

    def peek(self):
        """最後に積んだ要素を、取り出さずに返す。空なら None。"""
        if not self._items:
            return None
        return self._items[-1]

    def __len__(self):
        return len(self._items)


# ここに Shape を Protocol として定義する。
# 「引数なしで呼べて float を返す area() を持つもの」が Shape。


def total_area(shapes):
    """shapes に含まれる図形の面積の合計を返す。"""
    return sum(shape.area() for shape in shapes)
```

- [ ] **Step 3: スタブで失敗することを確かめる**

```bash
EX=$REPO/phase1_lang/ex06_typing
make -C $EX test; echo "test rc=$?"
make -C $EX lint; echo "lint rc=$?"
make -C $EX type; echo "type rc=$?"
```
期待: test は `8 failed, 6 passed`、`rc=2`。失敗するのは `test_greeting_for_unknown_user`（`TypeError`）と、`test_typecases.py` の `test_cases_exist` 以外の7件。lint は `rc=0`。type は `rc=2`（型ヒントがないため。この課題の出発点）。
成り立たない場合（テストから mypy を呼べない）: `test_typecases.py` をやめ、common.mk の `type` に `typecases/` を検査する手順を足す方式へ切り替える。設計書3.3と5章を合わせて直す。

- [ ] **Step 4: 解答を書いて検証する**

`answers/phase1_lang/ex06_typing/typed.py` を書く。

```bash
bash $REPO/answers/verify.sh ex06_typing; echo "rc=$?"
```
期待: `PASS  phase1_lang/ex06_typing  14 passed ...`、`rc=0`。
追加の確認: 解答の型をすべて `Any` に置き換えた一時コピーで、`ng_*.py` の3件が落ちること（`Any` で埋めると通らない、という設計書の要求）。

- [ ] **Step 5: README を作る**

**File:** `phase1_lang/ex06_typing/README.md`
````markdown
# Phase 1 / ex06_typing（型ヒントと Protocol）

## 読み物: 型ヒントは誰が読むか
4日目までのスタブには型ヒントが書いてあり、`make type` がそれを検査していました。今日は自分で書きます。

型ヒントは実行時には検査されません。読むのは mypy と、エディタと、人です。C のコンパイラが必ずやっていた型検査を、Python では mypy に頼んでやってもらいます。頼む以上、検査できるだけの情報を書く必要があります。

### 基本の書き方
| 書き方 | 意味 |
|---|---|
| `x: int`、`-> str`、`-> None` | 変数や引数の型、戻り値の型 |
| `list[int]`、`dict[str, int]`、`tuple[int, str]` | 中身の型まで書く |
| `str \| None` | 文字列か `None`。使う前に `None` でないことを確かめないと、mypy が止める |
| `Sequence[int]`、`Iterable[int]`、`Mapping[str, int]` | 「順番に並んだもの」「`for` で回せるもの」「辞書のようなもの」。`collections.abc` から import する |

引数の型は、広く受けるほうが使いやすくなります。`list[int]` と書くと tuple を渡せません。添字で読むだけなら `Sequence[int]`、`for` で回すだけなら `Iterable[int]` と書きます。

### ジェネリクス
3日目の `RingBuffer` は、要素の型を `object` にしました。何でも入りますが、取り出した値も `object` で、`rb.pop() + 1` は mypy が通しません。入れた型のまま取り出せるようにするのがジェネリクスです。

```python
def last[T](items: Sequence[T]) -> T:     # 「要素の型を T と呼ぶ。同じ T を返す」
    return items[-1]

class Box[T]:                             # Box[int] と Box[str] は別の型
    def __init__(self, value: T) -> None:
        self.value = value
```

c_master の C++ 補足で書いた `template <typename T>` と同じ役目です。C++ は型ごとに別のコードを生成しますが、Python の `[T]` は mypy への説明で、実行時には何も変わりません。古いコードでは `T = TypeVar("T")` と `Generic[T]` を使った書き方を見かけます。意味は同じです。

### Protocol
Python は昔から「`area()` を持っていれば図形として扱う」という書き方をしてきました（ダックタイピング）。継承していなくても、必要なメソッドがあれば使えます。これを型で表すのが `Protocol` です。

```python
from typing import Protocol

class Named(Protocol):
    def name(self) -> str: ...            # 本体は ... と書く

def show(x: Named) -> None:               # name() を持つものなら、何でも渡せる
    print(x.name())
```

### `Any` と `object`
どちらも「何でも入る」型ですが、逆の性質を持ちます。`object` は、取り出したあと何もさせてもらえません（安全）。`Any` は、何をしても mypy が黙ります（検査の放棄）。この課題を `Any` で埋めると `make type` は通りますが、`ng_*.py` のテストが落ちます。

## 目的
`src/typed.py` に型ヒントを書く。本体はすでに動きます。

1. すべての関数とメソッドに型ヒントを書く
2. `Stack` をジェネリックにする
3. `Shape` を `Protocol` として定義し、`total_area` の引数に使う
4. 型ヒントを書くと mypy が見つけるバグを1つ直す

## 手順
1. `make test` で失敗を確認。`make type` のエラーの数も見ておく
2. `first`、`find_user`、`greeting` に型ヒントを書く → `make type`。mypy が `greeting` のバグを指摘するので直す
3. `Stack` をジェネリックにする
4. `Shape` を定義し、`total_area` に型ヒントを書く
5. `make check`

## テストについて
`typecases/` には、`typed.py` を使う側のコードが入っています。テストはこれを mypy にかけます。

- `ok_*.py` は、正しい使い方です。エラーが出たら、型ヒントが厳しすぎるか、間違っています
- `ng_*.py` は、間違った使い方です。「# NG」の行を mypy がエラーにしなければなりません。エラーにならないなら、型ヒントが緩すぎます

`typecases/` と `test/` は変更しないでください。

## ヒント
- `first` に tuple を渡す使い方が `ok_generics.py` にあります。引数を `list[T]` と書くと通りません
- `find_user` の戻り値は、見つからないときがあります
- `Stack` の中のリストにも型が要ります（`self._items: list[T] = []`）
- `total_area` の引数は、list でもジェネレータでも受け取れるようにします

## 発展課題（任意）
- 3日目の `RingBuffer` をジェネリックにする。`object` をどこまで `T` に置き換えられるか
- `Shape` に `@runtime_checkable` を付けると、`isinstance(x, Shape)` が使えるようになる。何を調べていて、何を調べていないか
- `ng_optional.py` のエラーメッセージを、`make type` ではなく次のコマンドで直接読む
  ```bash
  ../../.venv/bin/python -m mypy --strict src/typed.py typecases/ng_optional.py
  ```

## 説明できるようになるべきこと
- 型ヒントは実行時に何をするか。誰が、いつ検査するか
- `str | None` を返す関数の戻り値を、そのまま使えない理由。mypy を納得させる書き方
- 引数の型を `list[int]` ではなく `Sequence[int]` や `Iterable[int]` と書く利点
- ジェネリクスが解決する問題。C++ のテンプレートとの共通点と違い
- `Protocol` と継承の違い。`Circle` が `Shape` を継承していないのに通る理由
- `Any` と `object` の違い。`Any` を避ける理由
````

- [ ] **Step 6: コミットする**

```bash
cd $REPO && git add phase1_lang/ex06_typing && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "feat: add phase1 ex06_typing

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。

---

### Task 9: ROADMAP.md、README.md、CLAUDE.md

**Files:**
- Create: `ROADMAP.md`、`README.md`、`CLAUDE.md`

**Interfaces:**
- Consumes: Task 1〜8 で作った課題のディレクトリ名と make ターゲット

- [ ] **Step 1: ROADMAP.md を作る**

**File:** `ROADMAP.md`
````markdown
# Python 習熟ロードマップ（1週間 / 言語の深部）

- 想定: 1日3〜4時間 × 5日（合計15〜20時間）
- 進め方: 1日目に道具をそろえ、2日目から5日目で言語の「分かったつもりになりやすいところ」を課題で確かめる
- 各課題は `make check` が通ったら、Claude に「phaseX/exY をレビューして」と依頼する
- 発展課題はすべて任意。時間が余ったときだけ取り組む

## 1週間の予定

| 日 | 課題 | 目安 | 到達目標 |
|---|---|---|---|
| 1日目 | phase0_env/ex01_toolchain、ex02_bug_hunt | 3h | pytest・ruff・mypy・pdb でバグを捕まえられる |
| 2日目 | phase1_lang/ex01_names_objects、ex02_closure_decorator | 4h | 別名・可変性・コピーを説明でき、クロージャからデコレータを自作できる |
| 3日目 | phase1_lang/ex03_data_model | 3〜4h | 特殊メソッドで、組み込み型のように振る舞うクラスを書ける |
| 4日目 | phase1_lang/ex04_iter_gen、ex05_context | 4h | ジェネレータで遅延パイプラインを書け、例外と `with` で後片付けを保証できる |
| 5日目 | phase1_lang/ex06_typing、1週間のふり返り | 3h | 型ヒントと `Protocol` を書いて `mypy --strict` を通せる |

## チェックリスト
- [ ] 1日目: ex01_toolchain（`uv sync`、`make test` / `make check`、pdb の基本操作）
- [ ] 1日目: ex02_bug_hunt（ruff・mypy・`make check` で3つのバグを特定して直す）
- [ ] 2日目: ex01_names_objects（予想クイズ8問、別名を作らない関数とクラス）
- [ ] 2日目: ex02_closure_decorator（クロージャ、デコレータ、デコレータで登録するコマンド表）
- [ ] 3日目: ex03_data_model（特殊メソッドで書くリングバッファ、プロパティ、クラスメソッド）
- [ ] 4日目: ex04_iter_gen（イテレータを手で書く、ジェネレータの遅延パイプライン）
- [ ] 4日目: ex05_context（例外の階層と原因の連鎖、コンテキストマネージャ）
- [ ] 5日目: ex06_typing（ジェネリクス、`Protocol`、`None` の絞り込み）
- [ ] 5日目: ふり返り（各 README の「説明できるようになるべきこと」を Claude に説明してみる）

## c_master との対応
同じ題材を C と Python で書き比べられるようにしてあります。

| python_master | c_master | 見比べるところ |
|---|---|---|
| phase0_env/ex01_toolchain | phase0_env/ex01_toolchain | `clamp`。桁あふれ、前提条件の扱い |
| phase1_lang/ex02_closure_decorator | phase1_lang/ex04_cmd_table | コマンド振り分け。関数ポインタの表と、デコレータでの登録 |
| phase1_lang/ex03_data_model | phase3_cpp/ex01_ring_buffer | リングバッファ。`bool` の戻り値と例外、テンプレートと特殊メソッド |

## この先の学習（任意）
1週間を終えて続けたくなったら、次の順がおすすめです。
1. 並行処理: GIL、threading と asyncio と multiprocessing の使い分け
2. メタプログラミング: ディスクリプタ、`__getattr__`、`__init_subclass__`、メタクラス
3. パッケージングと配布: `pyproject.toml`、src レイアウト、コマンドの登録
4. 性能と C 連携: cProfile での計測、ctypes で c_master の関数を Python から呼ぶ
5. 応用分野: Web API（FastAPI）、データ処理（pandas）、CLI ツール

## 副読本（任意）
- 『Fluent Python』 Luciano Ramalho
- 『Effective Python』 Brett Slatkin
````

- [ ] **Step 2: README.md を作る**

**File:** `README.md`
````markdown
# python_master（Python 習熟演習）

Python の言語そのものの深部を、説明できて書けるレベルまで鍛えるための、1週間の演習環境です。
C を一通り学んだ人を想定していて、各課題の読み物は C との対比で書いてあります。組込みは扱いません。
日ごとの予定は [ROADMAP.md](ROADMAP.md) を参照してください。

## 必要なもの
[uv](https://docs.astral.sh/uv/)（Python 本体と依存ライブラリを管理するツール）と make。
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh    # uv が入っていない場合だけ
uv sync                                             # リポジトリの一番上で、最初に1回
```
`uv sync` は、Python 3.13 と pytest・ruff・mypy を、このリポジトリの `.venv/` に入れます。システムの Python には触りません。

## 構成
```
common/          共通の実行規則（common.mk）
phase0_env/      1日目の課題（開発環境）
phase1_lang/     2〜5日目の課題（言語の深部）
docs/            設計書・計画書
pyproject.toml   依存と、pytest・ruff・mypy の設定
```
各課題ディレクトリは `README.md`（読み物と課題文）、`src/`（あなたが実装する）、`test/`（提供テスト）、`Makefile` からなります。
`phase1_lang/ex06_typing` だけ、型の検査に使う `typecases/` があります。

## 課題の進め方
1. 課題の `README.md` を読む（読み物 → 目的 → 手順）
2. `make test` で、テストが失敗することを確認する
3. `src/` を実装する（`test/` は変更しない）
4. `make check` が通ったら完了
5. Claude Code に「phase1_lang/ex01_names_objects をレビューして」のように依頼する。README の「説明できるようになるべきこと」についても質問されます
6. `git commit` して、ROADMAP.md のチェックボックスを埋める

## make ターゲット
各課題のディレクトリで実行します。

| コマンド | 内容 |
|---|---|
| `make test` | テストを実行する。実装中の速い確認用 |
| `make test ARGS="-x"` | pytest にオプションを渡す（`-x` 最初の失敗で止める、`-k 名前` 絞り込む、`-v` テスト名を表示） |
| `make lint` | ruff で、バグになりやすい書き方を調べる |
| `make type` | `mypy --strict` で、型の矛盾を調べる |
| `make check` | lint、type に続けて、警告をエラー扱いにしてテストを実行する。**これが通れば完了** |
| `make clean` | キャッシュを削除する |

対話環境で試したいときは、`../../.venv/bin/python` を起動します。

## 基本構文を確認したいとき
c_master の [docs/基本構文/Python.md](https://github.com/masumi82/c_master/blob/master/docs/基本構文/Python.md) にまとめがあります（手元では `../c_master/docs/基本構文/Python.md`）。
````

- [ ] **Step 3: CLAUDE.md を作る**

**File:** `CLAUDE.md`
````markdown
# python_master

Python の言語の深部を、1週間（1日3〜4時間 × 5日）で学ぶ演習リポジトリ。姉妹リポジトリは `../c_master`。

## 学習者
- C の基礎を終えている。Python は基本構文（クラス、`self`、デコレータの入口）まで
- 構文の初歩は説明しなくてよい。別名と可変性、スコープ、データモデル、遅延評価、例外、型を、C との対比で説明する

## レビューを頼まれたとき
「phase1_lang/ex03_data_model をレビューして」のように頼まれたら、次の順で進める。
1. その課題のディレクトリで `make check` を実行し、結果を見る
2. `src/` を、README の仕様と `test/` に照らして読む
3. README の「説明できるようになるべきこと」を1つずつ質問し、学習者に自分の言葉で答えてもらう

## 決まり
- 詰まっているときは、まずヒントを出す。答えのコードは、頼まれるまで書かない
- `answers/` はローカル専用の模範解答で、`.git/info/exclude` で除外してある。学習者が答えを求めるまで、中身を引用しない
- 模範解答をコミットしない。`src/` に解答を書き込まない
- 課題を増やさない。1週間ぶんの8課題で完結している。続きを頼まれたら、ROADMAP.md の「この先の学習」から相談する
- `test/` と `typecases/` は変更しない
- 課題コードと解答のコメントは日本語、識別子は英語
````

- [ ] **Step 4: 文章を確かめてコミットする**

```bash
cd $REPO && python3 /home/m-horiuchi/.claude/skills/deslop-ja/scripts/check.py --tech --reading-load README.md ROADMAP.md CLAUDE.md phase0_env/*/README.md phase1_lang/*/README.md 2>&1 | grep -E '^==|^重大|^\[重大\]'
```
期待: どのファイルも `重大 0`。警告は読んで、直すか、理由を付けて残す。

```bash
cd $REPO && git add ROADMAP.md README.md CLAUDE.md && git status --short
git grep --cached -Eil '(api[_-]?key|secret|token|password|BEGIN [A-Z ]*PRIVATE KEY)' -- . ':!docs/superpowers'; echo "scan rc=$?"
git commit -q -m "docs: add roadmap, top-level README, and CLAUDE.md

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
```
期待: `scan rc=1`。課題の README を直した場合は、それも add する。

---

### Task 10: answers/ の解説・速習・README（コミットしない）

`answers/` は git から除外されているので、このタスクにコミットはない。8課題は互いに独立しているので、並行して書ける。

**Files:**
- Create（コミットしない）: 8課題それぞれに `answers/<課題>/解説.md` と `answers/<課題>/速習.md`
- Create（コミットしない）: `answers/README.md`

**Interfaces:**
- Consumes: Task 1〜8 の README（「説明できるようになるべきこと」「考察問題」「発展課題」）と、`answers/` の解答ファイル

- [ ] **Step 1: 手本の書式を読む**

c_master の次の4つを読み、節の立て方と分量を合わせる。

```
/home/m-horiuchi/persol_ws/c_master/answers/README.md
/home/m-horiuchi/persol_ws/c_master/answers/phase1_lang/ex01_bitops/解説.md
/home/m-horiuchi/persol_ws/c_master/answers/phase1_lang/ex01_bitops/速習.md
/home/m-horiuchi/persol_ws/c_master/answers/phase1_lang/ex03_int_promotion/解説.md
```

- [ ] **Step 2: 課題ごとに 解説.md を書く**

各 `解説.md` に書くこと。

- 解答のコードの要点（なぜその書き方か。別の書き方との比較）
- README の「説明できるようになるべきこと」の全項目への答え。項目の順番と数を README と揃える
- README に「考察問題」がある課題（ex01_names_objects）は、その全問への答え
- テストが狙っている落とし穴と、踏んだときに出るエラーメッセージ

課題ごとに、必ず触れる点。

| 課題 | 必ず触れる点 |
|---|---|
| ex01_toolchain | 4つの道具の守備範囲。型ヒントが実行時に検査されないこと |
| ex02_bug_hunt | 3つのバグと、それぞれを見つけた道具。`if not idx:` と直すと位置 0 で間違うこと |
| ex01_names_objects | クイズ8問の答えと理由。`+=` が list と str で違う理由。`t[0] += [3]` で例外が出るのに中身は変わること |
| ex02_closure_decorator | 遅延束縛の仕組みと直し方2通り。`@retry(3)` を代入の形に展開したもの。`functools.wraps` を外したときに落ちるテスト |
| ex03_data_model | クラス属性にした場合の失敗例。`__iter__` をジェネレータで書く理由。`__eq__` を書くとハッシュ不可になること |
| ex04_iter_gen | `take` が1件余分に読む書き方と、その直し方。ジェネレータ関数の中の `raise` がいつ実行されるか |
| ex05_context | `from e` の有無でのトレースバックの違い。`__exit__` の戻り値。`target = draft` では反映されない理由 |
| ex06_typing | `Any` で埋めると落ちるテスト。`list[T]` と `Sequence[T]` の違い。`Protocol` と継承の違い |

- [ ] **Step 3: 課題ごとに 速習.md を書く**

c_master の `速習.md` と同じ4節（課題、こう作れる、つまずきポイント、30秒チェック）で、1本を5〜10分で読める長さにする。

- [ ] **Step 4: answers/README.md を書く**

c_master の `answers/README.md` と同じ節（使い方、速習の順番、一覧、検証）で書く。検証の節には、`bash answers/verify.sh` の実行結果（日付と、PASS した課題の数）を書く。

- [ ] **Step 5: 文中のコードを実行して確かめる**

`解説.md` と `速習.md` に載せたコード片のうち、「こう書くとこうなる」と結果を示しているものは、`$SCRATCH` に書き出して実際に実行し、書いた結果と一致することを確かめる。

```bash
$REPO/.venv/bin/python $SCRATCH/snippets/<課題>_<番号>.py
```
期待: 文中に書いた出力、または例外の種類と一致する。

- [ ] **Step 6: 文章を確かめる**

```bash
cd $REPO && python3 /home/m-horiuchi/.claude/skills/deslop-ja/scripts/check.py --tech answers/README.md answers/*/*/解説.md answers/*/*/速習.md 2>&1 | grep -E '^==|^重大|^\[重大\]'
ls answers/*/*/解説.md answers/*/*/速習.md | wc -l
git -C $REPO status --short
```
期待: どのファイルも `重大 0`。ファイル数は 16。`git status` に `answers/` が出ない。

---

### Task 11: 全体の検証と、設計書の更新

**Files:**
- Modify: `docs/superpowers/specs/2026-10-13-python-mastery-roadmap-design.md`（5章に、確かめた結果を書く）

- [ ] **Step 1: 全課題のスタブが失敗することを、まとめて確かめる**

```bash
cd $REPO && for ex in phase0_env/ex01_toolchain phase0_env/ex02_bug_hunt phase1_lang/ex01_names_objects phase1_lang/ex02_closure_decorator phase1_lang/ex03_data_model phase1_lang/ex04_iter_gen phase1_lang/ex05_context phase1_lang/ex06_typing; do printf '%-40s ' "$ex"; make -C "$ex" test 2>&1 | grep -E '[0-9]+ (failed|passed)' | tail -1; done
```
期待（失敗数 / 通過数）: 9/0、2/5、20/0、22/0、31/0、24/0、20/0、8/6。どの集計行にも `error` という語が出ない。

- [ ] **Step 2: 全課題の解答が通ることを、まとめて確かめる**

```bash
bash $REPO/answers/verify.sh; echo "rc=$?"
```
期待: `PASS` が8行、`SKIP` と `FAIL` はなし、`rc=0`。

- [ ] **Step 3: リポジトリに解答が入っていないことを確かめる**

```bash
cd $REPO && git ls-files | grep -c '^answers/'; git status --short; grep -rn "NotImplementedError" phase0_env/ex01_toolchain/src phase1_lang/*/src | wc -l
```
期待: 1行目は `0`。`git status` は何も出ない。`src/` には `raise NotImplementedError` が残っている（解答で上書きしていない）。

- [ ] **Step 4: `.gitignore` が必要なものを除外していることを確かめる**

```bash
cd $REPO && for p in .env .env.local a.pem a.key config/local.toml __pycache__/x node_modules/x .venv/x; do git check-ignore -q "$p" && echo "ignored  $p" || echo "NOT IGNORED  $p"; done; git check-ignore -q .env.example && echo "NOT TRACKABLE .env.example" || echo "trackable .env.example"
```
期待: 8行とも `ignored`。最後は `trackable .env.example`。

- [ ] **Step 5: 設計書5章に結果を書いてコミットする**

設計書5章の表に「結果」の列を足し、6つの前提それぞれについて、確かめたコマンドと、成り立ったか、代替に切り替えたかを書く。代替に切り替えたものがあれば、3章の該当箇所も直す。

```bash
cd $REPO && git add docs/superpowers/specs/2026-10-13-python-mastery-roadmap-design.md && git commit -q -m "docs: record verification results for design assumptions

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git log --oneline | head -15 && git status --short
```
期待: `git status` は何も出ない。

