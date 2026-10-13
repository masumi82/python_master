"""Part 1: クロージャとデコレータ。"""

from collections.abc import Callable

# traced が、呼ばれた関数の名前を記録していくリスト。
CALL_LOG: list[str] = []


def make_counter() -> Callable[[], int]:
    """呼ぶたびに 1, 2, 3, ... を返す関数を作って返す。

    make_counter を 2 回呼んで作った関数は、互いに独立して数える。
    グローバル変数とクラスは使わない。
    """
    raise NotImplementedError


def make_multipliers(n: int) -> list[Callable[[int], int]]:
    """n 個の関数のリストを返す。i 番目（0 始まり）の関数は、引数を i 倍して返す。"""
    raise NotImplementedError


def traced[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """func を包んだ関数を返すデコレータ。

    包んだ関数は、呼ばれるたびに、func を呼ぶ「前に」func の名前を CALL_LOG へ加える。
    引数はそのまま func に渡し、func の戻り値をそのまま返す。
    包んだ関数の __name__ と __doc__ は、func のものと同じにする。
    """
    raise NotImplementedError


def retry[**P, R](times: int) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """最大 times 回まで呼び直すデコレータを返す。

    包んだ関数は func を呼び、Exception が出たら呼び直す。
    成功したら、その戻り値を返して終わる（それ以上は呼ばない）。
    times 回とも失敗したら、最後の例外をそのまま送出する。
    times が 1 未満なら、retry(times) を呼んだ時点で ValueError。
    包んだ関数の __name__ と __doc__ は、func のものと同じにする。
    """
    raise NotImplementedError
