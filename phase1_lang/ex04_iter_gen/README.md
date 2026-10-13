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
- `test_first_errors_on_endless_log` は、終わりのないログを渡します。どこかでリストに全部ためていると、1000行を読んだところで「読みすぎ」として落ちます（上限がなければ、テストは終わらず、メモリを使い切ります）

## ヒント
- `Countdown` は、`__iter__` で `self` を返し、`__next__` で値を返すか `raise StopIteration` します
- `take` で `for i, item in enumerate(items):` と書くと、`n` 個目を返したあとにもう1個読んでしまいます。「返してから数え、足りたらすぐ抜ける」順にします
- `flatten` は、要素が list なら自分自身を呼びます。`yield from` が使えます
- `"ERROR disk full".split(maxsplit=1)` と `"ERROR".split(maxsplit=1)` を対話環境で試す

## 発展課題（任意）
- `take` を `itertools.islice` で、`chunked` を `itertools.batched` で書き直してみる。どちらも、そのままでは仕様と少し違う（`batched` はタプルを返し、`islice` は負の個数を受け付けない）。何を足せばテストが通るか
- `first_errors` を、ジェネレータ式 `(r.message for r in ...)` を使って書き直す
- `sum(x * x for x in range(10**7))` と `sum([x * x for x in range(10**7)])` で、メモリの使い方がどう違うか

## 説明できるようになるべきこと
- `for` 文が裏で呼んでいるもの。イテラブルとイテレータの違い
- イテレータは1回で使い切りなのに、list は何度でも `for` で回せる理由
- `yield` を含む関数を呼んだとき、何が起きて、何が起きないか
- 遅延評価の利点。`first_errors` が、必要な行までしか読まない仕組み
- `chunked` に `size=0` を渡したとき、`ValueError` が出るのは `chunked(...)` を呼んだ時点か、最初の `next()` の時点か。なぜか
