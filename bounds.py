"""Exercise 3.1. Bounds analysis for 3 Counter Machine"""

import functools
from funcutils import Lattice

from threecm import Analysis


@functools.total_ordering
class Bounds(Lattice):
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
class Bottom(Bounds):
    def __le__(self, other):
        return True

    def join(self, other):
        return other

    def __repr__(self):
        return 'Bottom()'


@functools.total_ordering
class Top(Bounds):
    def __le__(self, other):
        return isinstance(other, Top)

    def join(self, other):
        return self

    def __repr__(self):
        return 'Top()'


@functools.total_ordering
class ZeroBound(Bounds):
    def __le__(self, other):
        return isinstance(other, (ZeroBound, Top))

    def join(self, other):
        if isinstance(other, (ZeroBound, Bottom)):
            return self
        else:
            return Top()

    def __repr__(self):
        return 'ZeroBound()'


@functools.total_ordering
class OneBound(Bounds):
    def __le__(self, other):
        return isinstance(other, (OneBound, Top))

    def join(self, other):
        if isinstance(other, (OneBound, Bottom)):
            return self
        else:
            return Top()

    def __repr__(self):
        return 'OneBound()'


@functools.total_ordering
class Regular(Bounds):
    def __le__(self, other):
        return isinstance(other, (Regular, Top))

    def join(self, other):
        if isinstance(other, (Regular, Bottom)):
            return self
        else:
            return Top()

    def __repr__(self):
        return 'Regular()'


class BoundsAnalysis(Analysis):
    bottom = Bottom()
    initial = Top(), ZeroBound(), ZeroBound()

    @staticmethod
    def plus_1(x):
        if isinstance(x, Bottom):
            return x
        elif isinstance(x, ZeroBound):
            return OneBound()
        elif isinstance(x, OneBound):
            return Regular()
        elif isinstance(x, Regular):
            return Regular()
        elif isinstance(x, Top):
            return x
        else:
            raise TypeError('not a Bounds element: {!r}'.format(x))

    @staticmethod
    def minus_1(x):
        if isinstance(x, Bottom):
            return x
        elif isinstance(x, ZeroBound):
            return Bottom()
        elif isinstance(x, OneBound):
            return ZeroBound()
        elif isinstance(x, Regular):
            return Top()
        elif isinstance(x, Top):
            return x
        else:
            raise TypeError('not a Bounds element: {!r}'.format(x))

    @staticmethod
    def is_zero(x):
        if isinstance(x, Bottom):
            return x
        elif isinstance(x, ZeroBound):
            return x
        elif isinstance(x, OneBound):
            return Bottom()
        elif isinstance(x, Regular):
            return Bottom()
        elif isinstance(x, Top):
            return ZeroBound()
        else:
            raise TypeError('not a Bounds element: {!r}'.format(x))

    @staticmethod
    def non_zero(x):
        if isinstance(x, Bottom):
            return x
        elif isinstance(x, ZeroBound):
            return Bottom()
        elif isinstance(x, OneBound):
            return x
        elif isinstance(x, Regular):
            return x
        elif isinstance(x, Top):
            return x
        else:
            raise TypeError('not a Bounds element: {!r}'.format(x))
