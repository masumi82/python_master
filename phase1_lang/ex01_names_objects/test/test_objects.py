import objects


def test_make_grid_shape() -> None:
    assert objects.make_grid(2, 3) == [[0, 0, 0], [0, 0, 0]]
    assert objects.make_grid(1, 2, fill=7) == [[7, 7]]
    assert objects.make_grid(0, 3) == []


def test_make_grid_rows_are_independent() -> None:
    grid = objects.make_grid(3, 2)
    grid[0][0] = 9
    assert grid == [[9, 0], [0, 0], [0, 0]]
    assert grid[0] is not grid[1]


def test_appended_returns_new_list() -> None:
    items = [1, 2]
    result = objects.appended(items, 3)
    assert result == [1, 2, 3]
    assert items == [1, 2]
    assert result is not items


def test_extend_in_place_mutates_argument() -> None:
    items = [1]
    objects.extend_in_place(items, [2, 3])
    assert items == [1, 2, 3]


def test_extend_in_place_does_not_touch_values() -> None:
    items = [1]
    values = [2, 3]
    objects.extend_in_place(items, values)
    assert values == [2, 3]


def test_deep_copy_nested() -> None:
    xy = [1, 2]
    pos = {"xy": xy}
    tags = ["x", "y"]
    original = {"name": "a", "tags": tags, "pos": pos}
    copied = objects.deep_copy(original)
    assert copied == original
    assert copied is not original
    # 複製を奥まで書き換えても、元は変わらない。
    assert isinstance(copied, dict)
    copied["tags"].append("z")
    copied["pos"]["xy"].append(3)
    copied["name"] = "b"
    assert tags == ["x", "y"]
    assert xy == [1, 2]
    assert original["name"] == "a"


def test_deep_copy_list_of_lists() -> None:
    inner = [1, 2]
    original = [inner, [3]]
    copied = objects.deep_copy(original)
    assert copied == [[1, 2], [3]]
    assert isinstance(copied, list)
    assert copied is not original
    assert copied[0] is not inner


def test_deep_copy_leaves_scalars() -> None:
    assert objects.deep_copy(5) == 5
    assert objects.deep_copy("abc") == "abc"
    assert objects.deep_copy(None) is None


def test_history_starts_empty() -> None:
    assert objects.History().snapshot() == []


def test_histories_do_not_share_storage() -> None:
    first = objects.History()
    second = objects.History()
    first.add(1)
    assert first.snapshot() == [1]
    assert second.snapshot() == []


def test_history_copies_initial() -> None:
    initial = [1, 2]
    history = objects.History(initial)
    initial.append(99)
    assert history.snapshot() == [1, 2]
    history.add(3)
    assert history.snapshot() == [1, 2, 3]
    assert initial == [1, 2, 99]


def test_history_snapshot_is_a_copy() -> None:
    history = objects.History([1])
    snap = history.snapshot()
    snap.append(99)
    assert history.snapshot() == [1]
