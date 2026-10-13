"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import Stack, first

numbers: Stack[int] = Stack()
numbers.push("one")  # NG
text: str = numbers.pop()  # NG
value: int = first([1, 2, 3])  # NG
