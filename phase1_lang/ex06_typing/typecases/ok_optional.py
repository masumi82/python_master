"""mypy --strict を通らなければならない使い方。"""

from typed import find_user, greeting

users = {1: "Ann", 2: "Bob"}
name: str | None = find_user(users, 1)
message: str = greeting(users, 3)
if name is not None:
    upper: str = name.upper()
