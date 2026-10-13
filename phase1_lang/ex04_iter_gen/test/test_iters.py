from collections.abc import Iterator

import pytest

import iters
from iters import LogRecord


class CountingLines:
    """何行読まれたかを数えるイテレータ。遅延評価の確認に使う。"""

    def __init__(self, lines: list[str]) -> None:
        self._lines = iter(lines)
        self.consumed = 0

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        line = next(self._lines)
        self.consumed += 1
        return line


# 「終わりのない列」を読んでよい上限。これを超えて読んだら、テストを失敗させる。
# 上限がないと、全部をリストにためる実装でテストが止まらず、メモリを使い切ってしまう。
READ_LIMIT = 1000


def naturals() -> Iterator[int]:
    """0, 1, 2, ... と続くジェネレータ。READ_LIMIT 個を超えて読まれたら失敗させる。"""
    n = 0
    while True:
        if n >= READ_LIMIT:
            pytest.fail(f"{READ_LIMIT} 個も読んだ。必要なぶんだけ読むこと")
        yield n
        n += 1


# --- Countdown ---


def test_countdown() -> None:
    assert list(iters.Countdown(3)) == [3, 2, 1]


@pytest.mark.parametrize("start", [0, -2])
def test_countdown_from_non_positive_is_empty(start: int) -> None:
    assert list(iters.Countdown(start)) == []


def test_countdown_is_its_own_iterator() -> None:
    countdown = iters.Countdown(2)
    assert iter(countdown) is countdown


def test_countdown_is_exhausted_after_one_pass() -> None:
    countdown = iters.Countdown(2)
    assert list(countdown) == [2, 1]
    assert list(countdown) == []


def test_countdown_next_by_hand() -> None:
    countdown = iters.Countdown(2)
    assert next(countdown) == 2
    assert next(countdown) == 1
    with pytest.raises(StopIteration):
        next(countdown)
    with pytest.raises(StopIteration):
        next(countdown)


# --- take ---


def test_take() -> None:
    assert list(iters.take([1, 2, 3, 4], 2)) == [1, 2]
    assert list(iters.take([1, 2], 5)) == [1, 2]
    assert list(iters.take([1, 2], 0)) == []


def test_take_works_on_infinite_input() -> None:
    assert list(iters.take(naturals(), 3)) == [0, 1, 2]


def test_take_is_lazy() -> None:
    lines = CountingLines(["a", "b", "c", "d"])
    result = iters.take(lines, 2)
    assert lines.consumed == 0  # 作っただけでは、1 行も読まない
    assert list(result) == ["a", "b"]
    assert lines.consumed == 2  # 3 行目を読みにいかない


def test_take_zero_reads_nothing() -> None:
    lines = CountingLines(["a", "b"])
    assert list(iters.take(lines, 0)) == []
    assert lines.consumed == 0


# --- chunked ---


def test_chunked() -> None:
    assert list(iters.chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    assert list(iters.chunked([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]
    empty: list[int] = []
    assert list(iters.chunked(empty, 3)) == []


def test_chunked_yields_independent_lists() -> None:
    chunks = list(iters.chunked([1, 2, 3, 4], 2))
    assert chunks[0] is not chunks[1]
    chunks[0].append(99)
    assert chunks[1] == [3, 4]


def test_chunked_is_lazy() -> None:
    chunks = iters.chunked(naturals(), 3)
    assert next(chunks) == [0, 1, 2]
    assert next(chunks) == [3, 4, 5]


@pytest.mark.parametrize("size", [0, -1])
def test_chunked_rejects_bad_size(size: int) -> None:
    with pytest.raises(ValueError):
        list(iters.chunked([1, 2, 3], size))


# --- flatten ---


def test_flatten() -> None:
    assert list(iters.flatten([1, [2, 3], [[4], 5], []])) == [1, 2, 3, 4, 5]


def test_flatten_keeps_strings_and_tuples_whole() -> None:
    assert list(iters.flatten(["ab", ["cd", (1, 2)]])) == ["ab", "cd", (1, 2)]


def test_flatten_is_lazy() -> None:
    def source() -> Iterator[object]:
        yield [1, [2]]
        yield 3
        raise AssertionError("ここまで読んではいけない")

    result = iters.flatten(source())
    assert [next(result), next(result), next(result)] == [1, 2, 3]


# --- ログのパイプライン ---

LOG = [
    "INFO boot",
    "",
    "# comment",
    "ERROR disk full",
    "  WARN  low battery  ",
    "ERROR",
    "ERROR net down",
    "INFO done",
]


def test_parse() -> None:
    assert list(iters.parse(LOG)) == [
        LogRecord("INFO", "boot"),
        LogRecord("ERROR", "disk full"),
        LogRecord("WARN", "low battery"),
        LogRecord("ERROR", ""),
        LogRecord("ERROR", "net down"),
        LogRecord("INFO", "done"),
    ]


def test_parse_is_lazy() -> None:
    lines = CountingLines(LOG)
    records = iters.parse(lines)
    assert lines.consumed == 0
    assert next(records) == LogRecord("INFO", "boot")
    assert lines.consumed == 1


def test_only_level() -> None:
    records = [LogRecord("INFO", "a"), LogRecord("ERROR", "b"), LogRecord("ERROR", "c")]
    errors = list(iters.only_level(records, "ERROR"))
    assert errors == [LogRecord("ERROR", "b"), LogRecord("ERROR", "c")]
    assert list(iters.only_level(records, "DEBUG")) == []


def test_first_errors() -> None:
    assert iters.first_errors(LOG, 2) == ["disk full", ""]
    assert iters.first_errors(LOG, 10) == ["disk full", "", "net down"]
    assert iters.first_errors(LOG, 0) == []


def test_first_errors_stops_reading_early() -> None:
    lines = CountingLines(LOG)
    assert iters.first_errors(lines, 1) == ["disk full"]
    assert lines.consumed == 4  # "ERROR disk full" までの 4 行


def test_first_errors_on_endless_log() -> None:
    def endless() -> Iterator[str]:
        n = 0
        while True:
            n += 1
            if n > READ_LIMIT:
                pytest.fail(f"{READ_LIMIT} 行も読んだ。3 件そろったら読むのをやめること")
            yield f"ERROR e{n}" if n % 2 == 0 else f"INFO i{n}"

    assert iters.first_errors(endless(), 3) == ["e2", "e4", "e6"]
