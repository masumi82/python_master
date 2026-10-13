"""型ヒントを書く課題。このファイルには、わざと型ヒントを書いていない。

本体は、1 か所を除いてすでに動く。やることは 4 つ。
  1. すべての関数とメソッドに型ヒントを書く
  2. Stack をジェネリックにする（Stack[int] と Stack[str] を区別できるように）
  3. Shape を Protocol として定義する
  4. 型ヒントを書くと mypy が見つけるバグを 1 つ直す
"""


def first(items):
    """items の先頭の要素を返す。空なら None を返す。list でも tuple でも受け取れる。"""
    if not items:
        return None
    return items[0]


def find_user(users, user_id):
    """users（ID の整数 → 名前の文字列）から名前を探す。なければ None を返す。"""
    return users.get(user_id)


def greeting(users, user_id):
    """ "Hello, <名前>!" を返す。user_id が users になければ "Hello, guest!" を返す。"""
    name = find_user(users, user_id)
    return "Hello, " + name + "!"


class Stack:
    """後入れ先出しのスタック。"""

    def __init__(self):
        self._items = []

    def push(self, item):
        self._items.append(item)

    def pop(self):
        """最後に積んだ要素を取り出して返す。空なら IndexError。"""
        return self._items.pop()

    def peek(self):
        """最後に積んだ要素を、取り出さずに返す。空なら None。"""
        if not self._items:
            return None
        return self._items[-1]

    def __len__(self):
        return len(self._items)


# ここに Shape を Protocol として定義する。
# 「引数なしで呼べて float を返す area() を持つもの」が Shape。


def total_area(shapes):
    """shapes に含まれる図形の面積の合計を返す。"""
    return sum(shape.area() for shape in shapes)
