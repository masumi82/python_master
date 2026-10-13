"""mypy --strict を通らなければならない使い方。"""

from typed import Stack, first

numbers: Stack[int] = Stack()
numbers.push(1)
n: int = numbers.pop()
top: int | None = numbers.peek()
size: int = len(numbers)

words: Stack[str] = Stack()
words.push("a")
w: str = words.pop()

head_int: int | None = first([1, 2, 3])
head_str: str | None = first(("a", "b"))
