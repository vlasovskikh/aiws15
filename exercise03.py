import functools
from funcutils import Lattice
from threecm import Analysis


@functools.total_ordering
class Parity(Lattice):
    @property
    def bottom(self):
        return Bottom()

    def __le__(self, other):
        pass

    def join(self, other):
        pass

    def __eq__(self, other):
        return type(self) == type(other)


@functools.total_ordering
class Top(Parity):
    def __le__(self, other):
        return isinstance(other, Top)

    def join(self, other):
        return self

    def __repr__(self):
        return 'Top()'


@functools.total_ordering
class Odd(Parity):
    def __le__(self, other):
        return isinstance(other, (Bottom, Odd))

    def join(self, other):
        if isinstance(other, (Odd, Bottom)):
            return self
        else:
            return Top()

    def __repr__(self):
        return 'Odd()'


@functools.total_ordering
class Even(Parity):
    def __le__(self, other):
        return isinstance(other, (Bottom, Even))

    def join(self, other):
        if isinstance(other, (Even, Bottom)):
            return self
        else:
            return Top()

    def __repr__(self):
        return 'Even()'


@functools.total_ordering
class Bottom(Parity):
    def __le__(self, other):
        return True

    def join(self, other):
        return other

    def __repr__(self):
        return 'Bottom()'


class ParityAnalysis(Analysis):
    bottom = Bottom()
    initial = Top(), Even(), Even()

    @staticmethod
    def non_zero(p: Parity) -> Parity:
        return p

    @staticmethod
    def is_zero(p: Parity) -> Parity:
        if isinstance(p, Bottom):
            return p
        elif isinstance(p, Even):
            return p
        elif isinstance(p, Odd):
            return Bottom()
        elif isinstance(p, Top):
            return Even()
        else:
            raise TypeError('not a Parity element: {!r}'.format(p))

    @staticmethod
    def plus_1(p: Parity) -> Parity:
        if isinstance(p, Bottom):
            return p
        elif isinstance(p, Even):
            return Odd()
        elif isinstance(p, Odd):
            return Even()
        elif isinstance(p, Top):
            return p
        else:
            raise TypeError('not a Parity element: {!r}'.format(p))

    minus_1 = plus_1
