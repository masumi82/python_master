import pytest

import config


def test_exception_hierarchy() -> None:
    assert issubclass(config.ConfigError, Exception)
    assert issubclass(config.MissingKeyError, config.ConfigError)
    assert issubclass(config.InvalidValueError, config.ConfigError)
    assert not issubclass(config.MissingKeyError, config.InvalidValueError)
    assert not issubclass(config.InvalidValueError, config.MissingKeyError)


def test_parse_config() -> None:
    text = """
    # サーバの設定
    host = example.com
    port=8080

    url = http://example.com/?a=1
    """
    assert config.parse_config(text) == {
        "host": "example.com",
        "port": "8080",
        "url": "http://example.com/?a=1",
    }


def test_parse_config_empty_text() -> None:
    assert config.parse_config("") == {}


def test_parse_config_later_value_wins() -> None:
    assert config.parse_config("a = 1\na = 2") == {"a": "2"}


def test_parse_config_allows_empty_value() -> None:
    assert config.parse_config("name =") == {"name": ""}


@pytest.mark.parametrize(
    ("text", "line_number"),
    [
        ("host example.com", "1"),  # "=" がない
        ("a = 1\n\n= 5", "3"),  # key が空。空行も 1 行に数える
        ("a = 1\nb = 2\noops\nc = 3", "3"),
    ],
)
def test_parse_config_reports_line_number(text: str, line_number: str) -> None:
    with pytest.raises(config.ConfigError, match=line_number):
        config.parse_config(text)


def test_get_int() -> None:
    assert config.get_int({"port": "8080"}, "port") == 8080
    assert config.get_int({"offset": " -5 "}, "offset") == -5


def test_get_int_missing_key() -> None:
    with pytest.raises(config.MissingKeyError, match="port"):
        config.get_int({"host": "example.com"}, "port")


def test_get_int_invalid_value_keeps_cause() -> None:
    with pytest.raises(config.InvalidValueError, match="port") as excinfo:
        config.get_int({"port": "80a"}, "port")
    assert isinstance(excinfo.value.__cause__, ValueError)


def test_errors_can_be_caught_as_config_error() -> None:
    missing: dict[str, str] = {}
    invalid = {"port": "x"}
    for cfg in [missing, invalid]:
        with pytest.raises(config.ConfigError):
            config.get_int(cfg, "port")
