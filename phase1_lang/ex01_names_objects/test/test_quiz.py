"""Part 1 の答え合わせ。期待値は埋め込まず、その場で実行して求めている。"""

import pytest

import answers


def check(answer: object, actual: object) -> None:
    if answer is answers.UNSET:
        pytest.fail("まだ予想が書かれていない（src/answers.py）", pytrace=False)
    assert answer == actual


def test_q1() -> None:
    a = [1, 2]
    b = a
    b.append(3)
    check(answers.Q1, a)


def test_q2() -> None:
    a = [1, 2]
    b = a
    b = b + [3]  # noqa: F841
    check(answers.Q2, a)


def test_q3() -> None:
    a = [1, 2]
    b = a
    b += [3]
    check(answers.Q3, a)


def test_q4() -> None:
    grid = [[0] * 2] * 2
    grid[0][0] = 1
    check(answers.Q4, grid)


def test_q5() -> None:
    a = [[1], [2]]
    b = a.copy()
    b.append([3])
    b[0].append(9)
    check(answers.Q5, a)


def test_q6() -> None:
    def add(x: int, acc: list[int] = []) -> list[int]:  # noqa: B006
        acc.append(x)
        return acc

    add(1)
    check(answers.Q6, add(2))


def test_q7() -> None:
    t: tuple[list[int], int] = ([1], 2)
    t[0].append(3)
    check(answers.Q7, t)


def test_q8() -> None:
    a = [1, 2]
    b = [1, 2]
    check(answers.Q8, (a == b, a is b))
