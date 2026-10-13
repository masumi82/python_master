# Python 習熟ロードマップ & 演習環境 設計書

- 作成日: 2026-10-13
- 対象者: C の基礎を終え、Python は基本構文（クラス・`self`・デコレータの入口）まで押さえた学習者
- 目的: 言語そのものの深部を説明でき、書けるようになること。組込みは対象にしない
- 学習時間: 1日3〜4時間 × 5日（合計15〜20時間）
- 開発PC: WSL2 Ubuntu 22.04 / uv 0.10.4 / システムの `python3` は 3.10.12
- 手本: `../c_master`（同じ学習者の C 版。課題の形式と進め方を揃える）

## 1. 方針

c_master と同じ形式にする。課題は「仕様（README）とテストを提供する → 学習者が `src/` を実装する → チェックが通る → Claude がレビューする」。

- 8課題を5日に割り当てる。各課題は1.5〜2時間、3日目だけ1課題に3〜4時間を使う。
- 学習者は以前 `self`、`@staticmethod`、デコレータでつまずいた。2日目に「名前とオブジェクト」「スコープとクロージャ」を先に扱い、クラスとデコレータはその後に置く。
- 題材を c_master と揃え、同じものを C と Python で書き比べられるようにする（`clamp`、コマンド振り分け、リングバッファ）。
- 1〜4日目のスタブには型ヒントを書いておき、学習者はそれを読む。5日目に自分で型を書く。
- 1週間ぶんの8課題だけを作る。それ以降は ROADMAP の「この先の学習」に項目として載せる。

## 2. ロードマップ

| 日 | 課題 | 目安 | 到達目標 |
|---|---|---|---|
| 1日目 | phase0_env/ex01_toolchain、ex02_bug_hunt | 3h | pytest・ruff・mypy・pdb でバグを捕まえられる |
| 2日目 | phase1_lang/ex01_names_objects、ex02_closure_decorator | 4h | 別名・可変性・コピーを説明でき、クロージャからデコレータを自作できる |
| 3日目 | phase1_lang/ex03_data_model | 3〜4h | 特殊メソッドで、組み込み型のように振る舞うクラスを書ける |
| 4日目 | phase1_lang/ex04_iter_gen、ex05_context | 4h | ジェネレータで遅延パイプラインを書け、例外と `with` で後片付けを保証できる |
| 5日目 | phase1_lang/ex06_typing、ふり返り | 3h | 型ヒントと `Protocol` を書いて `mypy --strict` を通せる |

この先の学習。ROADMAP に項目だけ載せ、課題は作らない。

- 並行処理（GIL、threading と asyncio の使い分け）
- メタプログラミング（ディスクリプタ、メタクラス）
- パッケージングと配布
- 性能計測と C 連携（ctypes で c_master の関数を呼ぶ）
- 応用分野（Web API、データ処理、CLI）

副読本（任意）: 『Fluent Python』Luciano Ramalho、『Effective Python』Brett Slatkin。

## 3. 演習環境の構成

```
python_master/
  ROADMAP.md              # 第2章の表、チェックリスト、この先の学習、副読本
  README.md               # 環境構築、課題の進め方、make ターゲット
  CLAUDE.md               # Claude がレビューするときの決まり（3.5）
  pyproject.toml          # 依存（pytest・ruff・mypy）と各ツールの設定
  uv.lock
  .python-version         # 3.13
  .gitignore
  common/
    common.mk             # 共通の make 規則
  phase0_env/
    ex01_<name>/
      README.md           # 課題文
      Makefile            # include ../../common/common.mk の1行
      src/                # 学習者が実装する
      test/               # 提供テスト（変更しない）
  phase1_lang/
    ex01_<name>/ ...
  docs/superpowers/       # この設計書と実装計画
  answers/                # 模範解答・解説・速習。ローカル専用（3.4）
```

### 3.1 共通の実行規則

- Python は 3.13 に固定し、uv に管理させる。システムの 3.10 は使わない（2026年10月でサポートが切れる）。
- 依存は pytest、ruff、mypy の3つ。`pyproject.toml` の dev グループに書き、`uv sync` でリポジトリ内の `.venv` に入れる。学習者の PATH にあるツールには依存しない。
- 型チェッカは mypy だけにする。pip で `.venv` に入り、Node が要らない。
- ツールの設定はリポジトリ直下の `pyproject.toml` に集める。mypy は `strict = true`。ruff は `E`・`F`・`W`・`B`・`UP`・`SIM` を選ぶ。
- 課題の Makefile は `include ../../common/common.mk` だけにする。`src/` を import できるようにする設定（`PYTHONPATH=src`）は common.mk に書き、課題ごとの `conftest.py` は置かない。
- `.venv` がない状態で make を実行したら、`uv sync` を促すメッセージを出して止まる。

| コマンド | 内容 | c_master での対応 |
|---|---|---|
| `make test` | pytest を実行する。実装中の速い確認用 | `make test` |
| `make lint` | `ruff check src test` | コンパイラ警告 |
| `make type` | `mypy src test`（strict） | コンパイラ警告 |
| `make check` | lint、type に続けて、`python -X dev -W error` で pytest を実行する | `make asan` |
| `make clean` | キャッシュを削除する | `make clean` |

課題の完了条件は `make check` が通ること。

### 3.2 課題の形式

- README: 読み物（C との対比。10〜20分）/ 目的 / 手順 / ヒント / 発展課題（任意）/ 説明できるようになるべきこと
- src: シグネチャと docstring だけのスタブ。本体は `raise NotImplementedError`。初期状態では、テストの収集は通り、テストは失敗する。
- test: 正常系・境界値・異常系を含む pytest のテスト。型ヒント付き（`-> None`）。
- 課題コードと解答のコメントは日本語で書く。識別子は英語。
- 模範解答はコミットしない（3.4）。

例外が2つある。ex02_bug_hunt の `src/` には、バグ入りで動くコードを置く。ex06_typing は型ヒントを学習者が書くので、スタブに型を書かない。

### 3.3 作成する課題

Phase 0（1日目）

- ex01_toolchain: `uv sync`、`make test`、`make check`、pdb を一通り動かす。`clamp(v, lo, hi)` を実装する（c_master と同じ題材）。`lo > hi` は `ValueError`。README で `breakpoint()` と pdb の基本操作を、gdb の操作と並べて示す。
- ex02_bug_hunt: `src/stats.py` に3つのバグを入れ、それぞれ別の道具に見つけさせる。
  1. 可変オブジェクトのデフォルト引数。ruff（B006）が指摘する。テストは単独だと通り、まとめて流すと落ちる。
  2. `int | None` を返す関数の戻り値を、`None` の検査なしで計算に使う。mypy が指摘する。
  3. 開いたファイルを閉じない。`make test` は通り、`make check` の `-X dev -W error` で `ResourceWarning` がエラーになる。

Phase 1（2〜5日目）

- ex01_names_objects（2日目）: 予想クイズ8問と実装。クイズは c_master の ex03_int_promotion と同じ形式で、`src/answers.py` に予想を書き、テストが実際に式を評価して照合する。題材は別名、`+=` と `+` の違い、`[[0] * n] * m`、浅いコピー、デフォルト引数、タプルの中のリスト、`==` と `is`。実装は `make_grid`、元を変えずに追加する関数、`deep_copy`（`copy` モジュールを使わない）、内部状態を外へ漏らさない `History` クラス。
- ex02_closure_decorator（2日目）: `src/decorators.py` に `make_counter`（`nonlocal`）、`make_multipliers`（ループ変数の遅延束縛）、`count_calls`、引数付きの `retry(times)`。デコレータは `functools.wraps` で元の関数名を保つ。`src/commands.py` に `CommandTable`。`@table.command("name")` でハンドラを登録し、`dispatch(line)` で振り分ける（c_master の ex04_cmd_table と同じ題材）。
- ex03_data_model（3日目）: `src/ring_buffer.py` の `RingBuffer`（c_master の C++ 補足と同じ題材）。`__len__`、`__iter__`、`__getitem__`（負の添字を含む）、`__repr__`、`__eq__`、読み取り専用の `capacity` プロパティ、`is_full` プロパティ、クラスメソッド `from_iterable`。満杯での `push` は提供する `BufferFullError`、空での `pop` は `IndexError`。インスタンス同士が格納領域を共有しないことをテストで確かめる（クラス属性とインスタンス属性の取り違え）。`collections.deque` は使わない。要素の型は `object` にしておき、ex06 でジェネリクスに進む。
- ex04_iter_gen（4日目）: `src/iters.py`。`__iter__` と `__next__` を手で書く `Countdown`、ジェネレータ関数の `take`、`chunked`、`flatten`（`yield from`）、ログ行を `LogRecord` に変換する `parse` と、それらをつないだ遅延パイプライン。テストは「何行読まれたか」を数えるイテレータを渡し、必要なぶんしか消費しないことを確かめる。
- ex05_context（4日目）: `src/config.py` に例外の階層（`ConfigError`、`MissingKeyError`、`InvalidValueError`）、`parse_config`、`get_int`（`raise ... from` で原因を残す）。`src/resources.py` に `__enter__` と `__exit__` を書く `Transaction`（例外が出たら変更を捨て、例外は握りつぶさない）と、`@contextmanager` で書く `temporary_attr`。
- ex06_typing（5日目）: `src/typed.py`。ジェネリックな `first` と `Stack[T]`、`Protocol` の `Shape` と `total_area`、`None` を返しうる関数の絞り込み。型の正しさは `typecases/` で確かめる。`ok_*.py` は mypy を通り、`ng_*.py`（`Stack[int]` に文字列を積むなど）は mypy がエラーにする。テストが mypy を呼んでこれを検査するので、`Any` で埋めると通らない。`typecases/` は `src/` と `test/` の外に置き、`make lint` と `make type` の対象から外す。

### 3.4 answers/（ローカル専用）

c_master と同じく `.git/info/exclude` に `answers/` を書き、コミットもプッシュもされないようにする。

- 課題ごとに、`src/` の同名ファイルと差し替えられる解答、`解説.md`、`速習.md`
- `answers/README.md`: 使い方、速習の順番、一覧
- `answers/verify.sh`: 各課題を一時ディレクトリにコピーし、解答を差し込んで `make check` を実行する。リポジトリ本体には触らない

### 3.5 CLAUDE.md

Claude の記憶はディレクトリごとに分かれており、c_master 側の記憶は python_master では読み込まれない。レビューの決まりを短い `CLAUDE.md` に書いてコミットする。

- 学習者の前提（C 既習、Python は基本構文まで、1週間）
- 「phaseX/exY をレビューして」と頼まれたら、`src/` を提供テストと照合し、README の「説明できるようになるべきこと」を質問する
- 詰まっているときはヒントが先。`answers/` は頼まれるまで引用しない
- 模範解答をコミットしない。課題を勝手に増やさない
- 課題コードのコメントは日本語

### 3.6 そのほか

- `docs/基本構文/Python.md` は複製しない。README から c_master のものへリンクする。
- `git init` まで行う。GitHub への公開とプッシュはしない。
- `.gitignore` は c_master のものに `.pytest_cache/`、`.ruff_cache/`、`.mypy_cache/` を足す。

## 4. 検証方法

- スタブの確認: 各課題で `make test` を実行し、テストの収集が通って1件以上失敗することを確かめる。
- 解答の確認: `answers/verify.sh` で、全課題の解答が `make check` を通ることを確かめる。
- ex02_bug_hunt は、3つのバグがそれぞれ想定した道具（`make lint`、`make type`、`make check`）で指摘されることを個別に確かめる。
- 日本語の文書（README、ROADMAP、解説、速習）は deslop-ja の `check.py` にかける。

## 5. 未検証の前提

次の点は設計時に実行して確かめていない。実装計画の最初のタスクで確かめ、成り立たなければ右の代替に切り替える。

| 前提 | 成り立たない場合 |
|---|---|
| `uv sync` で 3.13 の `.venv` に pytest・ruff・mypy が入る | Python を 3.11 に下げる（uv で 3.11 の仮想環境が作れることは確認済み） |
| 課題ディレクトリから実行した pytest・ruff・mypy が、リポジトリ直下の `pyproject.toml` を読む | common.mk で設定ファイルのパスを明示して渡す |
| 閉じ忘れたファイルが、`-X dev -W error` を付けた pytest で失敗になる | 3つ目のバグを、テストだけが見つける別のバグに替える |
| 日本語コメントの全角文字が、選んだ ruff のルールに触れない | 触れるルールを個別に外す |
| `breakpoint()` が make 経由の pytest で pdb に入る | README の手順を `python -m pdb` に替える |
| テストから mypy を呼んで `typecases/` を検査できる | `make type` に `typecases/` 用の検査を足す |

## 6. 範囲外

- 実機演習（c_master の `phase2_pi`）
- 上流工程の文書演習（c_master の `upstream/`）
- 並行処理の課題（ROADMAP に項目だけ載せる）
- CI 環境
- GitHub への公開
