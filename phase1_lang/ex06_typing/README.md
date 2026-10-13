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

c_master の C++ 補足で書いた `template <typename T>` と同じ役目です。C++ は型ごとに別のコードを生成しますが、Python の `[T]` は mypy への説明で、実行時には何も変わりません。古いコードでは `T = TypeVar("T")` と `Generic[T]` を使った書き方を見かけます。意味は同じです。この課題では新しい書き方を使います（古い書き方は `make lint` が指摘します）。

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
どちらも「何でも入る」型ですが、逆の性質を持ちます。`object` は、取り出したあと何もさせてもらえません（安全）。`Any` は、何をしても mypy が黙ります（検査の放棄）。この課題の引数や戻り値を `Any` で埋めると、mypy は間違った使い方を止められなくなり、`ng_*.py` のテストが落ちます。

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
