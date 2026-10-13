"""イテレータとジェネレータ。

ルール: itertools は使わない。Countdown 以外は、ジェネレータ（yield）で書く。
"""

from collections.abc import Iterable, Iterator
from typing import NamedTuple


class LogRecord(NamedTuple):
    """ログ 1 行ぶん。提供済み。変更しない。"""

    level: str
    message: str


class Countdown:
    """start, start - 1, ..., 1 を順に返すイテレータ。

    yield を使わずに、__iter__ と __next__ を自分で書く。
    start が 0 以下なら、何も返さずに終わる。
    最後まで進んだあとは、何度 next() しても StopIteration。
    """

    def __init__(self, start: int) -> None:
        raise NotImplementedError

    def __iter__(self) -> "Countdown":
        """イテレータは、自分自身を返す。"""
        raise NotImplementedError

    def __next__(self) -> int:
        raise NotImplementedError


def take[T](items: Iterable[T], n: int) -> Iterator[T]:
    """items の先頭から最大 n 個を順に返す。

    n 個を返したら、それ以上 items を読まない。n が 0 以下なら、1 個も読まない。
    """
    raise NotImplementedError


def chunked[T](items: Iterable[T], size: int) -> Iterator[list[T]]:
    """items を size 個ずつのリストに区切って、順に返す。

    最後のリストは size 個に満たなくてよい。空のリストは返さない。
    返すリストは、毎回新しいリストにする。size が 1 未満なら ValueError。
    """
    raise NotImplementedError


def flatten(nested: Iterable[object]) -> Iterator[object]:
    """入れ子になった list を、奥まで平らにして順に返す。

    list 以外（str や tuple を含む）は、それ以上ほどかずに 1 つの要素として返す。
    """
    raise NotImplementedError


def parse(lines: Iterable[str]) -> Iterator[LogRecord]:
    """ "LEVEL message" 形式の行を、LogRecord に変換して順に返す。

    行の前後の空白を取り除いてから判定する。空行と、"#" で始まる行は読み飛ばす。
    LEVEL は最初の空白までの部分。message はその残りで、前後の空白を取り除く。
    LEVEL だけの行は、message を空文字列にする。
    """
    raise NotImplementedError


def only_level(records: Iterable[LogRecord], level: str) -> Iterator[LogRecord]:
    """level が一致する LogRecord だけを、順に返す。"""
    raise NotImplementedError


def first_errors(lines: Iterable[str], n: int) -> list[str]:
    """lines のうち level が "ERROR" の行の message を、先頭から最大 n 個、リストで返す。

    parse、only_level、take をつないで書く。n 個見つかったら、残りの行は読まない。
    """
    raise NotImplementedError
