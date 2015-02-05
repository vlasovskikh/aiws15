from abc import abstractmethod, ABCMeta
import functools

MAX_RECURSIONS = 100


class FixedPointNotReached(Exception):
    pass


def fixed_point(f):

    def g(x):
        for i in range(MAX_RECURSIONS):
            y = f(x)
            if y == x:
                return y
            else:
                x = y

        raise FixedPointNotReached(x)

    return g


@functools.total_ordering
class Lattice(metaclass=ABCMeta):
    @property
    @abstractmethod
    def bottom(self):
        pass

    @abstractmethod
    def __le__(self, other):
        pass

    @abstractmethod
    def join(self, other):
        pass

    def __eq__(self, other):
        return type(self) == type(other)
