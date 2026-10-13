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
- 型ヒント（`v: int`）は、実行時には検査されません。`clamp("a", "b", "c")` と書いても誰も止めず、実行すると文字列どうしを比べた結果が返ってきます。C ならコンパイラが止める間違いを、Python では mypy に止めてもらいます。

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
