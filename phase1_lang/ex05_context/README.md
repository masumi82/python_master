# Phase 1 / ex05_context（例外とコンテキストマネージャ）

## 読み物: 失敗の伝え方と、後片付けの保証
C の ex04_cmd_table では、失敗を `CMD_ERR_UNKNOWN` のような負の戻り値で伝えました。呼び出し側が戻り値を調べ忘れると、失敗は黙って無視されます。Python の例外は逆です。誰も受け取らなければプログラムが止まり、無視したければ、わざわざ `except` を書くことになります。

### 例外はクラスの階層
`except SomeError:` は、`SomeError` とその子クラスをすべて受け取ります。そこで、自分のモジュールの例外には共通の親を1つ作り、細かい種類を子にします。受け方は使う側が選べます。まとめて受けたければ親、区別したければ子。

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

クラスを書かずに済ませる方法が `@contextmanager` です。これを付けたジェネレータ関数では、`yield` の前が `__enter__`、後が `__exit__` にあたります。後片付けは `try: yield` と `finally:` で挟みます。

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
