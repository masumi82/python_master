import pytest

import decorators

# --- クロージャ ---


def test_make_counter_counts_up() -> None:
    counter = decorators.make_counter()
    assert [counter(), counter(), counter()] == [1, 2, 3]


def test_counters_are_independent() -> None:
    first = decorators.make_counter()
    second = decorators.make_counter()
    first()
    first()
    assert second() == 1
    assert first() == 3


def test_make_multipliers() -> None:
    funcs = decorators.make_multipliers(4)
    assert len(funcs) == 4
    assert [f(10) for f in funcs] == [0, 10, 20, 30]


# --- traced ---


def test_traced_records_calls_in_order() -> None:
    decorators.CALL_LOG.clear()

    @decorators.traced
    def add(a: int, b: int) -> int:
        return a + b

    @decorators.traced
    def greet(name: str, *, polite: bool = False) -> str:
        return f"Dear {name}" if polite else f"Hi {name}"

    assert decorators.CALL_LOG == []  # デコレータを付けただけでは、呼ばれない
    assert add(1, 2) == 3
    assert greet("Ann", polite=True) == "Dear Ann"
    assert add(b=5, a=4) == 9
    assert decorators.CALL_LOG == ["add", "greet", "add"]


def test_traced_keeps_name_and_doc() -> None:
    @decorators.traced
    def area(w: int, h: int) -> int:
        """長方形の面積。"""
        return w * h

    assert area.__name__ == "area"
    assert area.__doc__ == "長方形の面積。"


def test_traced_logs_even_when_function_raises() -> None:
    decorators.CALL_LOG.clear()

    @decorators.traced
    def boom() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        boom()
    assert decorators.CALL_LOG == ["boom"]


# --- retry ---


def test_retry_returns_first_success() -> None:
    attempts: list[int] = []

    @decorators.retry(3)
    def flaky(x: int) -> int:
        attempts.append(x)
        if len(attempts) < 3:
            raise OSError("まだ失敗する")
        return x * 2

    assert flaky(21) == 42
    assert attempts == [21, 21, 21]


def test_retry_does_not_retry_after_success() -> None:
    calls: list[str] = []

    @decorators.retry(5)
    def fine() -> str:
        calls.append("called")
        return "ok"

    assert fine() == "ok"
    assert calls == ["called"]


def test_retry_reraises_last_error() -> None:
    attempts: list[int] = []

    @decorators.retry(2)
    def always_fails() -> None:
        attempts.append(len(attempts) + 1)
        if len(attempts) > 10:
            # 回数を数え忘れた retry が、止まらずに呼び直し続けるのを防ぐ。
            pytest.fail("2 回までのはずが、10 回を超えて呼び直している")
        raise ValueError(f"失敗 {len(attempts)}")

    with pytest.raises(ValueError, match="失敗 2"):
        always_fails()
    assert attempts == [1, 2]


def test_retry_keeps_name() -> None:
    @decorators.retry(2)
    def fetch() -> None:
        """取得する。"""

    assert fetch.__name__ == "fetch"
    assert fetch.__doc__ == "取得する。"


def test_retry_rejects_zero_times() -> None:
    with pytest.raises(ValueError):
        decorators.retry(0)
