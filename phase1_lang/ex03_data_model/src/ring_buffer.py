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
