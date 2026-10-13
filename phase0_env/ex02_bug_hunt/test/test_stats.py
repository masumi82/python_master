from pathlib import Path

import pytest

import stats


def test_collect_into_given_list() -> None:
    samples = [1.0]
    assert stats.collect(2.0, samples) == [1.0, 2.0]
    assert samples == [1.0, 2.0]


def test_collect_into_given_empty_list() -> None:
    # 空のリストを渡したときも、渡された「そのリスト」に加えて返す。
    samples: list[float] = []
    assert stats.collect(1.0, samples) is samples
    assert samples == [1.0]


def test_collect_starts_empty_a() -> None:
    assert stats.collect(1.0) == [1.0]


def test_collect_starts_empty_b() -> None:
    # 上のテストと同じ内容。単独なら通るのに、続けて流すと落ちる理由を考える。
    assert stats.collect(1.0) == [1.0]


def test_first_above() -> None:
    assert stats.first_above([0.1, 0.5, 0.9], 0.4) == 1
    assert stats.first_above([0.1, 0.5, 0.9], 1.0) is None
    assert stats.first_above([], 0.0) is None


def test_time_to_threshold() -> None:
    assert stats.time_to_threshold([0.1, 0.5, 0.9], 0.4, 0.5) == pytest.approx(0.5)
    # 先頭の要素（位置 0）で超える場合。0 は「見つからない」ではない。
    assert stats.time_to_threshold([0.9], 0.4, 0.5) == pytest.approx(0.0)


def test_time_to_threshold_never_reached() -> None:
    assert stats.time_to_threshold([0.1, 0.2], 1.0, 0.5) == -1.0


def test_load_samples(tmp_path: Path) -> None:
    path = tmp_path / "samples.txt"
    path.write_text("1.5\n-2.0\n3\n", encoding="utf-8")
    assert stats.load_samples(str(path)) == [1.5, -2.0, 3.0]
