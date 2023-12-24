import math

# prints this beauty
# ```
#    ─┼───┼───┼───┼───┼───┼─
#     │   │   │   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
# │   │   │   │   │   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
# │   │   │   │   │   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
# │   │   │   ├ + ┤   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
# │   │   │   │   │   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
# │   │   │   │   │   │   │   │
# ┼───┼───┼───┼───┼───┼───┼───┼
#     │   │   │   │   │   │
#    ─┼───┼───┼───┼───┼───┼─
# ```


class Radar:
    def __init__(self, length: int, center, range, others):
        if length % 2 != 1:
            raise ValueError("length must be odd.")

        self.length = length
        self.center = center
        self.range = range

        # others format:
        # .. [0]: char
        # .. [1]: position
        # .. [1][0]: x
        # .. [1][1]: y
        # .. [2]: player name
        self.others = others
        # cursor to know the current row globally
        self._ix = -1 * self.length // 2 + 1
        self._iy = -1 * self.length // 2 + 1

    @property
    def ix(self):
        return self._ix

    @ix.setter
    def ix(self, ix):
        self._ix = ix

    @property
    def iy(self):
        return self._iy

    @iy.setter
    def iy(self, iy):
        self._ix = -1 * self.length // 2 + 1
        self._iy = iy

    def char_from_others(self, default: str = " ") -> str:
        """Returns a string based on match at the current coordinate."""
        char = ""
        num = 0
        for other in self.others:
            if (self.ix, self.iy) == other[1]:
                if char:
                    if char != other[0]:
                        char = "p"
                else:
                    char = other[0]

                # number of players at that coordinate
                num += 1

        if not char:
            char = default

        if num < 2:
            n = " "
        elif num > 9:
            n = "+9"
        else:
            n = str(num)

        return f"{n}{char}".ljust(3)

    def cell(self, reverse: bool = False, end=True) -> str:
        """Prints a cell of the radar, this is the most important function."""

        s = self.char_from_others()

        self.ix += 1
        if end is False:
            return s
        if reverse:
            return "│" + s
        return s + "│"

    def middle_cell(self) -> str:
        s = "├" + self.char_from_others(default="+") + "┤"
        self.ix += 1
        return s

    def crosses(self) -> str:
        return "┼───" * self.length + "┼" + "\n"

    def top_crosses(self) -> str:
        return " " * 3 + "─" + "┼───" * (self.length - 2) + "┼─" "\n"

    def middle_row(self):
        s = ""
        for _ in range(self.length // 2):
            s += self.cell(reverse=True)
        s += self.middle_cell()
        for _ in range(self.length // 2):
            s += self.cell()
        return s + "\n"

    def row(self):
        s = ""
        for _ in range(self.length):
            s += self.cell(reverse=True)
        s += "│"
        return s + "\n"

    def top_row(self):
        s = " "
        for _ in range(self.length - 1):
            s += self.cell()
        s += self.cell(end=False)
        return s + "\n"

    def grid(self):
        grid_str = ""

        # grid_str += self.crosses()
        grid_str += self.top_crosses()
        grid_str += self.top_row()
        self.iy += 1
        grid_str += self.crosses()

        for _ in range((self.length // 2) - 1):
            grid_str += self.row()
            grid_str += self.crosses()
            self.iy += 1

        grid_str += self.middle_row()
        self.iy += 1

        for _ in range((self.length // 2) - 1):
            grid_str += self.crosses()
            grid_str += self.row()
            self.iy += 1

        grid_str += self.crosses()
        grid_str += self.top_row()
        grid_str += self.top_crosses()
        self.iy += 1

        return grid_str

    def others_to_relative(self) -> list:
        """Transform self.others to have relative positions to center, upscaled to make range math length."""
        # fmt:off
        relative_others = [
            (other[0],
             (other[1][0] - self.center[0],
              other[1][1] - self.center[1]),
             other[2])
            for other in self.others
        ]
        # fmt:on

        # grid boundaries go from -x to x with 0,0 in the middle
        l = self.length // 2 - 1

        # fmt:off
        relative_others_upscaled = [
            (other[0],
             (math.ceil(other[1][0] / self.range * l),
                 math.ceil(other[1][1] / self.range * l)),
             other[2])
            for other in relative_others
        ]
        # fmt:on

        self.others = relative_others_upscaled


def surround(f, **kwargs) -> str:
    return "```\n" + f(**kwargs) + "```"


def main():
    others = [("e", (33, 7)), ("f", (0, -17)), ("e", (43, 28))]
    r = Radar(length=7, center=(3, 4), range=50, others=others)
    r.others_to_relative()
    print(surround(r.grid))


if __name__ == "__main__":
    main()
