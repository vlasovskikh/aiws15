"""Interval analysis of 3 Counter Machine"""


from functools import total_ordering
from numbers import Number
from funcutils import Lattice
from threecm import Analysis


@total_ordering
class Interval(Lattice):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def bottom(self):
        return Bottom()

    def join(self, other):
        if isinstance(other, Bottom):
            return self
        else:
            return Interval(min(self.left, other.left),
                            max(self.right, other.right))

    def __le__(self, other):
        if isinstance(other, Bottom):
            return False
        elif self.left >= other.left and self.right <= other.right:
            return True
        else:
            return False

    def __eq__(self, other):
        return (super().__eq__(other) and self.left == other.left and
                self.right == other.right)

    def widen(self, other):
        if isinstance(other, Bottom):
            return self
        else:
            left = float('-inf') if other.left < self.left else self.left
            right = float('+inf') if other.right > self.right else self.right
            return Interval(left, right)

    def __repr__(self):
        return 'Interval({}, {})'.format(self.left, self.right)

    def __contains__(self, x):
        if isinstance(x, Number):
            return self.left <= x <= self.right


@total_ordering
class Bottom(Interval):
    def __init__(self):
        super().__init__(0, 0)

    def join(self, other):
        return other

    def __le__(self, other):
        return True

    def __repr__(self):
        return 'Bottom()'

    def __contains__(self, item):
        return False

    def widen(self, other):
        return other


top = Interval(float('-inf'), float('+inf'))


class IntervalAnalysis(Analysis):
    bottom = Bottom()
    initial = top, Interval(0, 0), Interval(0, 0)

    @staticmethod
    def non_zero(x: Interval) -> Interval:
        if 0 in x:
            return top
        else:
            return x

    @staticmethod
    def is_zero(x: Interval) -> Interval:
        return Interval(0, 0)

    @staticmethod
    def minus_1(x: Interval) -> Interval:
        return Interval(x.left - 1, x.right - 1)

    @staticmethod
    def plus_1(x: Interval) -> Interval:
        return Interval(x.left + 1, x.right + 1)

    @staticmethod
    def widen(previous, next):
        """
        :type previous: dict[int, (Interval, Interval, Interval)]
        :type next: dict[int, (Interval, Interval, Interval)]
        :rtype: dict[int, (Interval, Interval, Interval)]
        """
        result = {}
        for pc, (x_1, y_1, z_1) in previous.items():
            x_2, y_2, z_2 = next[pc]
            result[pc] = x_1.widen(x_2), y_1.widen(y_2), z_1.widen(z_2)
        return result
