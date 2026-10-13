import pytest

from resources import Transaction, temporary_attr

# --- Transaction ---


def test_transaction_commits_on_success() -> None:
    settings = {"host": "a", "port": "80"}
    with Transaction(settings) as draft:
        draft["port"] = "8080"
        draft["debug"] = "1"
        del draft["host"]
        assert settings == {"host": "a", "port": "80"}  # まだ反映されない
    assert settings == {"port": "8080", "debug": "1"}


def test_transaction_draft_is_a_copy() -> None:
    settings = {"a": "1"}
    with Transaction(settings) as draft:
        assert draft == {"a": "1"}
        assert draft is not settings


def test_transaction_rolls_back_on_error() -> None:
    settings = {"host": "a"}
    with pytest.raises(RuntimeError, match="途中で失敗"):
        with Transaction(settings) as draft:
            draft["host"] = "b"
            raise RuntimeError("途中で失敗")
    assert settings == {"host": "a"}


def test_transaction_can_be_used_repeatedly() -> None:
    settings = {"n": "0"}
    for value in ["1", "2"]:
        with Transaction(settings) as draft:
            draft["n"] = value
    assert settings == {"n": "2"}


def test_transaction_object_can_be_reused_after_rollback() -> None:
    settings = {"n": "0"}
    transaction = Transaction(settings)
    with pytest.raises(RuntimeError):
        with transaction as draft:
            draft["n"] = "bad"
            raise RuntimeError("失敗")
    # 捨てた変更は、次に入ったときの作業用の辞書に残っていない。
    with transaction as draft:
        assert draft == {"n": "0"}
    assert settings == {"n": "0"}


# --- temporary_attr ---


class Screen:
    def __init__(self) -> None:
        self.color = "white"


def test_temporary_attr_sets_and_restores() -> None:
    screen = Screen()
    with temporary_attr(screen, "color", "red"):
        assert screen.color == "red"
    assert screen.color == "white"


def test_temporary_attr_restores_on_error() -> None:
    screen = Screen()
    with pytest.raises(KeyError):
        with temporary_attr(screen, "color", "red"):
            raise KeyError("boom")
    assert screen.color == "white"


def test_temporary_attr_requires_existing_attribute() -> None:
    screen = Screen()
    with pytest.raises(AttributeError):
        with temporary_attr(screen, "size", 10):
            pytest.fail("ブロックに入ってはいけない")
    assert not hasattr(screen, "size")


def test_temporary_attr_can_nest() -> None:
    screen = Screen()
    with temporary_attr(screen, "color", "red"):
        with temporary_attr(screen, "color", "blue"):
            assert screen.color == "blue"
        assert screen.color == "red"
    assert screen.color == "white"
