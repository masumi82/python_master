"""Part 1: 例外の階層と、原因を残した送出。"""


class ConfigError(Exception):
    """この課題の例外すべての親。提供済み。"""


# ここに、次の 2 つの例外クラスを定義する。どちらも ConfigError の子にする。
#   MissingKeyError    必要な key がない
#   InvalidValueError  値の形式が正しくない


def parse_config(text: str) -> dict[str, str]:
    """ "key = value" 形式のテキストを、辞書にして返す。

    - 行の前後の空白を取り除いてから判定する。空行と、"#" で始まる行は読み飛ばす
    - "=" は最初の 1 つで区切る（value は "=" を含んでよい）
    - key と value の前後の空白は取り除く。value は空でもよい
    - "=" がない行と、key が空の行は ConfigError。メッセージに行番号を含める
      （行番号は 1 始まりで、空行やコメント行も 1 行に数える）
    - 同じ key が 2 回出たら、後の値で上書きする
    """
    raise NotImplementedError


def get_int(config: dict[str, str], key: str) -> int:
    """config[key] を int に変換して返す。

    - key がなければ MissingKeyError。メッセージに key を含める
    - int に変換できなければ InvalidValueError。メッセージに key を含め、
      元の ValueError を原因（__cause__）として残す
    """
    raise NotImplementedError
