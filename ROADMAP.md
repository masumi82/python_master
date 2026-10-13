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
