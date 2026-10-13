"""Part 2: コンテキストマネージャ。"""

from collections.abc import Iterator
from contextlib import contextmanager
from types import TracebackType


class Transaction:
    """辞書への変更を、with ブロックが正常に終わったときだけ反映する。

        with Transaction(settings) as draft:
            draft["port"] = "8080"      # この時点では、settings は変わらない
        # ここで settings に反映される

    - __enter__ は、target の浅いコピー（作業用の辞書）を返す
    - ブロックが正常に終わったら、target の中身を、作業用の辞書の中身に置き換える
      （target という辞書オブジェクト自体は、同じものを使い続ける）
    - ブロックの中で例外が出たら、target は変えない。例外は握りつぶさずに外へ伝える
    """

    def __init__(self, target: dict[str, str]) -> None:
        raise NotImplementedError

    def __enter__(self) -> dict[str, str]:
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        raise NotImplementedError


@contextmanager
def temporary_attr(obj: object, name: str, value: object) -> Iterator[None]:
    """with ブロックの間だけ obj の属性 name を value に変え、抜けるときに元の値へ戻す。

    ブロックの中で例外が出ても、必ず元に戻す。例外は握りつぶさない。
    name という属性がもともとなければ AttributeError（ブロックには入らない）。
    """
    raise NotImplementedError
