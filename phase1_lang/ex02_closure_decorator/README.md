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
