"""mypy --strict を通らなければならない使い方。"""

from typed import Shape, total_area


class Circle:
    def __init__(self, radius: float) -> None:
        self.radius = radius

    def area(self) -> float:
        return 3.14159 * self.radius**2


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


# Circle も Square も Shape を継承していない。area() を持つので、Shape として通る。
total: float = total_area([Circle(1.0), Square(2.0)])
total_from_generator: float = total_area(Square(float(n)) for n in range(3))
one: Shape = Circle(1.0)
