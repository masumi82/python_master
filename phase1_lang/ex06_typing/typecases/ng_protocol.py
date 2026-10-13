"""mypy がエラーにしなければならない使い方。「# NG」の行だけがエラーになること。"""

from typed import Shape, total_area


class Line:
    def __init__(self, length: float) -> None:
        self.length = length


class Label:
    def area(self) -> str:
        return "big"


total_area([1, 2, 3])  # NG
total_area([Line(1.0)])  # NG
bad: Shape = Label()  # NG
label: str = total_area([])  # NG
