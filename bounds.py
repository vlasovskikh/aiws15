"""Exercise 3.1. Bounds analysis for 3 Counter Machine

Usage:
    bounds [options] PATH


Options:
    --help          Show help message
"""


import functools
from docopt import docopt
import sys
from funcutils import fixed_point
from threecm import Inc, Dec, Zero, Stop, parse, Instruction


@functools.total_ordering
class Bounds:
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


def analyze_bounds(program):
    """Perform bounds analysis.

    :type program: list[Instruction]
    :rtype: dict[int, (Bounds, Bounds, Bounds)]
    """

    def instruction(pc):
        return program[pc - 1]

    def var_function(f, v, states):
        x, y, z = states
        if v == 'x':
            return f(x), y, z
        elif v == 'y':
            return x, f(y), z
        elif v == 'z':
            return x, y, f(z)
        else:
            raise ValueError('unknown variable: {}'.format(v))

    def f_hat(s_hat):
        """

        :type s_hat: dict[int, (Bounds, Bounds, Bounds)]
        :rtype: dict[int, (Bounds, Bounds, Bounds)]
        """

        result = bottom_hat.copy()
        result[1] = Top(), ZeroBound(), ZeroBound()

        def map_and_join(index, f):
            x, y, z = f(s_hat[pc])
            rx, ry, rz = result[index]
            return rx.join(x), ry.join(y), rz.join(z)

        for pc, i in instructions.items():
            if isinstance(i, Inc):
                index = pc + 1
                function = functools.partial(var_function, plus_1, i.v)
                result[index] = map_and_join(index, function)
            elif isinstance(i, Dec):
                index = pc + 1
                function = functools.partial(var_function, minus_1, i.v)
                result[index] = map_and_join(index, function)
            elif isinstance(i, Zero):
                index1 = i.pc1
                function1 = functools.partial(var_function, is_zero, i.v)
                result[index1] = map_and_join(index1, function1)

                index2 = i.pc2
                function2 = functools.partial(var_function, non_zero, i.v)
                result[index2] = map_and_join(index2, function2)
            elif isinstance(i, Stop):
                pass
            else:
                raise ValueError('unknown instruction: {}'.format(i))

        return result

    pcs = set(range(1, len(program) + 1))
    instructions = {pc: instruction(pc) for pc in pcs}
    bottom_hat = {pc: (Bottom(), Bottom(), Bottom()) for pc in pcs}
    return fixed_point(f_hat)(bottom_hat)


def main(argv):
    opts = docopt(__doc__, argv=argv)
    with open(opts['PATH'], 'r') as fd:
        data = fd.read()
    program = parse(data)
    result = analyze_bounds(program)
    for i, instruction in enumerate(program):
        print('{} {}'.format(repr(instruction).ljust(30), result[i + 1]))


if __name__ == '__main__':
    main(sys.argv[1:])
