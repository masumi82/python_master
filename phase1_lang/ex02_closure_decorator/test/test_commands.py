import pytest

from commands import CommandTable, EmptyCommandError, UnknownCommandError


def make_table() -> CommandTable:
    table = CommandTable()

    @table.command("echo")
    def echo(args: list[str]) -> str:
        return " ".join(args)

    @table.command("add")
    def add(args: list[str]) -> str:
        return str(sum(int(a) for a in args))

    return table


def test_dispatch_calls_matching_handler() -> None:
    table = make_table()
    assert table.dispatch("echo hello world") == "hello world"
    assert table.dispatch("add 1 2 3") == "6"


def test_dispatch_splits_on_repeated_spaces() -> None:
    table = make_table()
    assert table.dispatch("  echo   a    b  ") == "a b"


def test_dispatch_with_no_arguments() -> None:
    table = make_table()
    assert table.dispatch("echo") == ""
    assert table.dispatch("add") == "0"


def test_command_returns_handler_unchanged() -> None:
    table = CommandTable()

    def ping(args: list[str]) -> str:
        return "pong"

    registered = table.command("ping")(ping)
    assert registered is ping
    assert ping([]) == "pong"  # 登録したあとも、普通の関数として呼べる
    assert table.dispatch("ping") == "pong"


def test_names_in_registration_order() -> None:
    assert make_table().names() == ["echo", "add"]


def test_empty_line() -> None:
    table = make_table()
    for line in ["", "   "]:
        with pytest.raises(EmptyCommandError):
            table.dispatch(line)


def test_unknown_command() -> None:
    table = make_table()
    with pytest.raises(UnknownCommandError):
        table.dispatch("reboot now")


def test_name_must_match_exactly() -> None:
    table = make_table()
    for line in ["ech hello", "echoo hello", "ECHO hello"]:
        with pytest.raises(UnknownCommandError):
            table.dispatch(line)


def test_duplicate_name_is_rejected() -> None:
    table = make_table()
    with pytest.raises(ValueError):

        @table.command("echo")
        def echo_again(args: list[str]) -> str:
            return ""

    assert table.dispatch("echo still original") == "still original"


def test_tables_do_not_share_handlers() -> None:
    first = make_table()
    second = CommandTable()
    assert first.names() == ["echo", "add"]
    assert second.names() == []


def test_handler_exception_propagates() -> None:
    table = make_table()
    # "add" のハンドラが出す ValueError は、握りつぶさずに呼び出し側へ伝える。
    with pytest.raises(ValueError):
        table.dispatch("add 1 x")


def test_handler_key_error_is_not_mistaken_for_unknown_command() -> None:
    table = CommandTable()

    @table.command("get")
    def get(args: list[str]) -> str:
        return {"a": "1"}[args[0]]

    assert table.dispatch("get a") == "1"
    # ハンドラの中で出た KeyError を、「コマンドが表にない」と取り違えない。
    with pytest.raises(KeyError):
        table.dispatch("get b")
