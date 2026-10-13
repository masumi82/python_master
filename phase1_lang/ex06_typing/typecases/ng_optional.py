"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import find_user, greeting

users = {1: "Ann"}
name: str = find_user(users, 1)  # NG
length: int = len(find_user(users, 2))  # NG
find_user(users, "1")  # NG
greeting(users, "3")  # NG
count: int = greeting(users, 1)  # NG
