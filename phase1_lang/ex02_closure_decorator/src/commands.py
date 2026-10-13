"""Part 2: デコレータでハンドラを登録するコマンド表。

c_master の phase1_lang/ex04_cmd_table と同じ題材。C では {名前, 関数ポインタ} の
配列を手で書いた。Python では、関数の定義にデコレータを付けるだけで表に載る。
"""

from collections.abc import Callable

# ハンドラは、引数（文字列のリスト）を受け取り、応答の文字列を返す。
Handler = Callable[[list[str]], str]


class EmptyCommandError(Exception):
    """行にトークンが 1 つもない。"""


class UnknownCommandError(Exception):
    """先頭のトークンが表にない。"""


class CommandTable:
    def __init__(self) -> None:
        raise NotImplementedError

    def command(self, name: str) -> Callable[[Handler], Handler]:
        """ハンドラを name で登録するデコレータを返す。

        登録したハンドラは包まずに、そのまま返す。
        同じ name がすでに登録されていたら ValueError（表は変えない）。
        """
        raise NotImplementedError

    def names(self) -> list[str]:
        """登録済みの名前を、登録した順に返す。"""
        raise NotImplementedError

    def dispatch(self, line: str) -> str:
        """line を空白（連続してもよい）で区切り、先頭のトークンと同じ名前のハンドラを呼ぶ。

        ハンドラには残りのトークンのリストを渡し、その戻り値を返す。
        トークンが 1 つもなければ EmptyCommandError。
        名前が表になければ UnknownCommandError（名前は完全一致で比べる）。
        どちらの場合も、ハンドラは呼ばない。ハンドラが出した例外は、そのまま伝える。
        """
        raise NotImplementedError
