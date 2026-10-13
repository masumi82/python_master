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
- `test_not_hashable` のために書くコードはありません。`__init__` を実装すれば通ります。`__eq__` を定義したクラスは、Python がハッシュ不可にするためです

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
