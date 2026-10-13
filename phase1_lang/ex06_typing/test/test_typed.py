"""実行時の振る舞いのテスト。型の検査は test_typecases.py が行う。"""

import pytest

import typed


def test_first() -> None:
    assert typed.first([3, 1, 2]) == 3
    assert typed.first(("a", "b")) == "a"
    empty: list[int] = []
    assert typed.first(empty) is None


def test_find_user() -> None:
    users = {1: "Ann"}
    assert typed.find_user(users, 1) == "Ann"
    assert typed.find_user(users, 2) is None


def test_greeting() -> None:
    assert typed.greeting({1: "Ann"}, 1) == "Hello, Ann!"


def test_greeting_for_unknown_user() -> None:
    assert typed.greeting({1: "Ann"}, 2) == "Hello, guest!"


def test_stack() -> None:
    stack: typed.Stack[int] = typed.Stack()
    assert stack.peek() is None
    stack.push(1)
    stack.push(2)
    assert len(stack) == 2
    assert stack.peek() == 2
    assert stack.pop() == 2
    assert stack.pop() == 1
    with pytest.raises(IndexError):
        stack.pop()


class Rect:
    def __init__(self, w: float, h: float) -> None:
        self.w = w
        self.h = h

    def area(self) -> float:
        return self.w * self.h


def test_total_area() -> None:
    assert typed.total_area([Rect(1, 2), Rect(3, 4)]) == pytest.approx(14.0)
    assert typed.total_area([]) == 0
