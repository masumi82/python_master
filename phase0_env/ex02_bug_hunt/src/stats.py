"""測定値を扱う小さな関数群。

このファイルには 3 つのバグがある。README の手順で、道具に見つけさせること。
各関数の docstring（仕様）は正しい。
"""


def collect(value: float, samples: list[float] = []) -> list[float]:
    """value を samples の末尾に加え、その samples を返す。

    samples を省略したときは、毎回新しい空のリストから始める。
    """
    samples.append(value)
    return samples


def first_above(samples: list[float], threshold: float) -> int | None:
    """threshold を超える最初の要素の位置を返す。なければ None を返す。"""
    for i, x in enumerate(samples):
        if x > threshold:
            return i
    return None


def time_to_threshold(samples: list[float], threshold: float, dt: float) -> float:
    """測定値が初めて threshold を超えるまでの時間（位置 × dt）を返す。

    一度も超えないときは -1.0 を返す。
    """
    return first_above(samples, threshold) * dt


def load_samples(path: str) -> list[float]:
    """1 行に 1 つ数値が書かれたテキストファイルを読み、リストで返す。"""
    f = open(path)
    return [float(line) for line in f]
