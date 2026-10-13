"""Part 1: 予想クイズの答えを書く。

テストを実行する「前に」、README.md の各問の予想を書く。
UNSET を、予想した値（リストやタプル）に書き換える。
"""

# 「まだ答えていない」ことを表す目印。これ自体は書き換えない。
UNSET: object = object()

Q1: object = UNSET  # a = [1, 2]; b = a; b.append(3) のあとの a
Q2: object = UNSET  # a = [1, 2]; b = a; b = b + [3] のあとの a
Q3: object = UNSET  # a = [1, 2]; b = a; b += [3] のあとの a
Q4: object = UNSET  # grid = [[0] * 2] * 2; grid[0][0] = 1 のあとの grid
Q5: object = UNSET  # a = [[1], [2]]; b = a.copy(); b.append([3]); b[0].append(9) のあとの a
Q6: object = UNSET  # def add(x, acc=[]) を add(1)、add(2) の順に呼んだときの、2 回目の戻り値
Q7: object = UNSET  # t = ([1], 2); t[0].append(3) のあとの t
Q8: object = UNSET  # a = [1, 2]; b = [1, 2] のときの (a == b, a is b)
