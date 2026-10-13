import pytest

from clamp import clamp


@pytest.mark.parametrize(
    ("v", "lo", "hi", "expected"),
    [
        (5, 0, 10, 5),  # 範囲内
        (-3, 0, 10, 0),  # 下にはみ出す
        (42, 0, 10, 10),  # 上にはみ出す
        (0, 0, 10, 0),  # 下端ちょうど
        (10, 0, 10, 10),  # 上端ちょうど
        (7, 7, 7, 7),  # lo == hi
        (-5, -10, -1, -5),  # 負の範囲
    ],
)
def test_clamp(v: int, lo: int, hi: int, expected: int) -> None:
    assert clamp(v, lo, hi) == expected


def test_clamp_huge_values() -> None:
    # C の int32_t と違い、Python の int は桁あふれしない。
    big = 2**100
    assert clamp(big, 0, 2**64) == 2**64
    assert clamp(-big, -(2**64), 0) == -(2**64)


def test_clamp_rejects_reversed_range() -> None:
    with pytest.raises(ValueError):
        clamp(5, 10, 0)
