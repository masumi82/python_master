"""Part 2: 別名を作らない、漏らさない関数とクラス。"""


def make_grid(rows: int, cols: int, fill: int = 0) -> list[list[int]]:
    """rows 行 cols 列の 2 次元リストを返す。全要素は fill。

    どの行も、ほかの行と同じリストであってはならない。
    """
    raise NotImplementedError


def appended(items: list[int], value: int) -> list[int]:
    """items の末尾に value を加えた「新しい」リストを返す。items は変えない。"""
    raise NotImplementedError


def extend_in_place(items: list[int], values: list[int]) -> None:
    """items 自体の末尾に values の要素を加える。新しいリストは作らない。"""
    raise NotImplementedError


def deep_copy(obj: object) -> object:
    """list と dict を、入れ子の奥まで複製して返す。

    list と dict 以外（int、str、None など）は、そのまま返す。
    copy モジュールは使わない。
    """
    raise NotImplementedError


class History:
    """値の履歴を持つ。内部のリストを、外から書き換えられないようにする。"""

    def __init__(self, initial: list[int] | None = None) -> None:
        """initial があれば、その時点の内容で始める。なければ空で始める。

        あとで呼び出し側が initial を書き換えても、History の中身は変わらない。
        """
        raise NotImplementedError

    def add(self, value: int) -> None:
        """履歴の末尾に value を加える。"""
        raise NotImplementedError

    def snapshot(self) -> list[int]:
        """今の履歴を返す。返したリストを書き換えても、History の中身は変わらない。"""
        raise NotImplementedError
