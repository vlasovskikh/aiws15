"""Exercise 2. 3 Counters Machine and the Parity domain.

Usage:
    exercise02 [options] PATH


Options:
    --input VALUE   Input value of x (non-negative) [default: 0]
    --trace         Trace machine execution
    --help          Show help message
"""

import unittest
import sys
import functools

from docopt import docopt
from threecm import Inc, Dec, Zero, Stop, parse


def check_pc_out_of_bounds(program):
    maximum = len(program)

    def valid(instruction):
        if isinstance(instruction, Zero):
            return (0 < instruction.pc1 <= maximum and
                    0 < instruction.pc2 <= maximum)

    return all(valid(i) for i in program)


def evaluate(program, input, trace=False):
    print('Running with input {}'.format(input))
    pc = 1
    x, y, z = input, 0, 0
    if trace:
        print('Trace: ({}, {}, {}, {})'.format(pc, x, y, z))
    while True:
        if pc > len(program) or pc <= 0:
            return None
        i = program[pc - 1]
        if trace:
            print('Instruction: {}'.format(i))
        if isinstance(i, Stop):
            return y
        elif isinstance(i, Inc):
            if i.v == 'x':
                x += 1
            elif i.v == 'y':
                y += 1
            elif i.v == 'z':
                z += 1
            else:
                return None
            pc += 1
        elif isinstance(i, Dec):
            if i.v == 'x' and x > 0:
                x -= 1
            elif i.v == 'y' and y > 0:
                y -= 1
            elif i.v == 'z' and z > 0:
                z -= 1
            else:
                return None
            pc += 1
        elif isinstance(i, Zero):
            if i.v == 'x':
                pc = i.pc1 if x == 0 else i.pc2
            elif i.v == 'y':
                pc = i.pc1 if y == 0 else i.pc2
            elif i.v == 'z':
                pc = i.pc1 if z == 0 else i.pc2
            else:
                return None
        else:
            return None


@functools.total_ordering
class Parity:
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


def non_zero(p: Parity) -> Parity:
    return p


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


class ParityTest(unittest.TestCase):
    def test_le(self):
        self.assertLess(Bottom(), Even())
        self.assertGreater(Top(), Odd())


def main(argv):
    opts = docopt(__doc__, argv=argv)
    with open(opts['PATH'], 'r') as fd:
        data = fd.read()
    program = parse(data)
    result = evaluate(program, int(opts['--input']), trace=opts['--trace'])
    print('Result: {}'.format(result))


if __name__ == '__main__':
    pass
    main(sys.argv[1:])