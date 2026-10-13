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
