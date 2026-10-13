import pytest

from ring_buffer import BufferFullError, RingBuffer


def filled(*values: object, capacity: int = 4) -> RingBuffer:
    rb = RingBuffer(capacity)
    for v in values:
        rb.push(v)
    return rb


# --- 生成 ---


def test_new_buffer_is_empty() -> None:
    rb = RingBuffer(4)
    assert len(rb) == 0
    assert rb.capacity == 4
    assert not rb.is_full


@pytest.mark.parametrize("capacity", [0, -1])
def test_capacity_must_be_positive(capacity: int) -> None:
    with pytest.raises(ValueError):
        RingBuffer(capacity)


def test_buffers_do_not_share_storage() -> None:
    first = RingBuffer(2)
    second = RingBuffer(2)
    first.push("a")
    assert len(first) == 1
    assert len(second) == 0
    assert list(second) == []


# --- push / pop ---


def test_fifo_order() -> None:
    rb = filled(1, 2, 3)
    assert [rb.pop(), rb.pop(), rb.pop()] == [1, 2, 3]
    assert len(rb) == 0


def test_push_to_full_buffer_raises_and_changes_nothing() -> None:
    rb = filled(1, 2, capacity=2)
    assert rb.is_full
    with pytest.raises(BufferFullError):
        rb.push(3)
    assert list(rb) == [1, 2]


def test_pop_from_empty_buffer_raises_index_error() -> None:
    with pytest.raises(IndexError):
        RingBuffer(2).pop()


def test_wraparound() -> None:
    rb = filled(1, 2, 3, capacity=3)
    assert rb.pop() == 1
    rb.push(4)  # 書き込み位置が、配列の末尾から先頭へ戻る
    assert rb.pop() == 2
    rb.push(5)
    assert list(rb) == [3, 4, 5]
    assert rb.is_full


def test_clear() -> None:
    rb = filled(1, 2, 3)
    rb.clear()
    assert len(rb) == 0
    rb.push(9)
    assert list(rb) == [9]


def test_none_can_be_stored() -> None:
    # None も普通の値として入る。「空き」の目印に None を使うと、ここで個数が狂う。
    rb = filled(None, None)
    assert len(rb) == 2
    assert rb.pop() is None
    assert len(rb) == 1


# --- 組み込み型のように振る舞う ---


def test_truthiness_follows_len() -> None:
    rb = RingBuffer(2)
    assert not rb
    rb.push(0)
    assert rb


def test_iteration_does_not_consume() -> None:
    rb = filled(1, 2, 3)
    assert list(rb) == [1, 2, 3]
    assert list(rb) == [1, 2, 3]
    assert len(rb) == 3


def test_two_iterators_are_independent() -> None:
    rb = filled(1, 2)
    pairs = [(a, b) for a in rb for b in rb]
    assert pairs == [(1, 1), (1, 2), (2, 1), (2, 2)]


def test_indexing() -> None:
    rb = filled(10, 20, 30)
    assert rb[0] == 10
    assert rb[2] == 30
    assert rb[-1] == 30
    assert rb[-3] == 10


def test_indexing_after_wraparound() -> None:
    rb = filled(1, 2, 3, capacity=3)
    rb.pop()
    rb.push(4)
    assert [rb[0], rb[1], rb[2]] == [2, 3, 4]
    assert rb[-1] == 4


@pytest.mark.parametrize("index", [3, -4, 100])
def test_index_out_of_range(index: int) -> None:
    # 容量は 4、要素は 3 個。位置 3 は配列の中だが、要素はない。
    rb = filled(10, 20, 30)
    with pytest.raises(IndexError):
        rb[index]


def test_membership_and_reversed_come_for_free() -> None:
    rb = filled(1, 2, 3)
    assert 2 in rb
    assert 9 not in rb
    assert list(reversed(rb)) == [3, 2, 1]


def test_repr() -> None:
    assert repr(filled(1, 2, 3)) == "RingBuffer([1, 2, 3], capacity=4)"
    assert repr(RingBuffer(2)) == "RingBuffer([], capacity=2)"
    assert repr(filled("a", capacity=1)) == "RingBuffer(['a'], capacity=1)"


def test_equality() -> None:
    assert filled(1, 2) == filled(1, 2)
    assert filled(1, 2) != filled(1, 3)
    assert filled(1, 2) != filled(1, 2, capacity=8)


def test_equality_ignores_internal_position() -> None:
    plain = filled(2, 3, capacity=3)
    wrapped = filled(1, 2, capacity=3)
    wrapped.pop()
    wrapped.push(3)  # 中身は [2, 3] だが、内部の先頭位置は plain と違う
    assert wrapped == plain


def test_equality_with_other_types() -> None:
    rb = filled(1, 2)
    assert rb != [1, 2]
    result: object = rb.__eq__([1, 2])
    assert result is NotImplemented


def test_not_hashable() -> None:
    # __eq__ を定義した可変オブジェクトは、dict のキーや set の要素にできない。
    with pytest.raises(TypeError):
        hash(RingBuffer(2))


# --- プロパティとクラスメソッド ---


def test_capacity_is_read_only() -> None:
    rb = RingBuffer(2)
    name = "capacity"
    with pytest.raises(AttributeError):
        setattr(rb, name, 10)
    assert rb.capacity == 2


def test_is_full_is_a_property() -> None:
    rb = filled(1, capacity=1)
    assert rb.is_full is True
    rb.pop()
    assert rb.is_full is False


def test_from_iterable() -> None:
    rb = RingBuffer.from_iterable([1, 2, 3])
    assert isinstance(rb, RingBuffer)
    assert list(rb) == [1, 2, 3]
    assert rb.capacity == 3
    assert rb.is_full


def test_from_iterable_with_capacity() -> None:
    rb = RingBuffer.from_iterable("ab", capacity=5)
    assert list(rb) == ["a", "b"]
    assert rb.capacity == 5


def test_from_iterable_accepts_a_generator() -> None:
    rb = RingBuffer.from_iterable(n * n for n in range(3))
    assert list(rb) == [0, 1, 4]


def test_from_iterable_too_many_items() -> None:
    with pytest.raises(BufferFullError):
        RingBuffer.from_iterable([1, 2, 3], capacity=2)


def test_from_iterable_empty_without_capacity() -> None:
    with pytest.raises(ValueError):
        RingBuffer.from_iterable([])
