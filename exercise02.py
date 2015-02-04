"""Exercise 2. 3CountersMachine and Parity domain.

Usage:
    exercise02 [options] PATH


Options:
    --input VALUE   Input value of x (non-negative) [default: 0]
    --trace         Trace machine execution
    --analyze       Perform parity analysis
    --help          Show help message

"""


from collections import namedtuple
import unittest
from funcparserlib.lexer import make_tokenizer
from funcparserlib.parser import some, many, finished, skip
import sys

from docopt import docopt
import functools

from util import fixed_point


class Instruction:
    pass


class Inc(Instruction, namedtuple('Inc', 'v')):
    pass


class Dec(Instruction, namedtuple('Dec', 'v')):
    pass


class Zero(Instruction, namedtuple('Zero', 'v pc1 pc2')):
    pass


class Stop(Instruction, namedtuple('Stop', '')):
    pass


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


def tokenize(s):
    specs = [
        ('whitespace', (r'[ \t]',)),
        ('newline', (r'[\n]',)),
        ('instruction', (r'(inc|dec|zero|else|stop|else)',)),
        ('variable', (r'[xyz]',)),
        ('number', (r'[0-9]+',)),
    ]
    f = make_tokenizer(specs)
    return [t for t in f(s) if t.type != 'whitespace']


def parse(s):
    def value(t):
        return t.value

    def token(type):
        return some(lambda t: t.type == type)

    def instruction(name):
        return some(lambda t: t.type == 'instruction' and t.value == name)

    def unarg(f):
        return lambda args: f(*args)

    newline = token('newline')
    variable = token('variable') >> value
    number = token('number') >> value >> int
    increment = skip(instruction('inc')) + variable >> Inc
    decrement = skip(instruction('dec')) + variable >> Dec
    zero = (skip(instruction('zero')) + variable + number +
            skip(instruction('else')) + number >> unarg(Zero))
    stop = instruction('stop') >> (lambda x: Stop())

    instruction = increment | decrement | zero | stop
    top_level = many(instruction + skip(newline)) + skip(finished)

    tokens = tokenize(s)
    return top_level.parse(tokens)


class ParseTest(unittest.TestCase):
    def test_parse_0(self):
        self.assertEqual([Stop()],
                         parse('stop\n'))

    def test_parse_1(self):
        self.assertEqual([Inc('x'), Stop()],
                         parse('inc x\n'
                               'stop\n'))

    def test_parse_2(self):
        self.assertEqual([Dec('y'), Stop()],
                         parse('dec y\n'
                               'stop\n'))

    def test_parse_3(self):
        self.assertEqual([Dec('y'), Zero('y', 1, 3), Stop()],
                         parse('dec y\n'
                               'zero y 1 else 3\n'
                               'stop\n'))


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


def analyze_parity(program):
    """Perform parity analysis.

    :type program: list[Instruction]
    :rtype: dict[int, (Parity, Parity, Parity)]
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

        :type s_hat: dict[int, (Parity, Parity, Parity)]
        :rtype: dict[int, (Parity, Parity, Parity)]
        """

        result = bottom_hat.copy()
        result[1] = Top(), Even(), Even()

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


class ParityTest(unittest.TestCase):
    def test_le(self):
        self.assertLess(Bottom(), Even())
        self.assertGreater(Top(), Odd())


def main(argv):
    opts = docopt(__doc__, argv=argv)
    with open(opts['PATH'], 'r') as fd:
        data = fd.read()
    program = parse(data)
    if opts['--analyze']:
        result = analyze_parity(program)
        for i, instruction in enumerate(program):
            print('{} {}'.format(repr(instruction).ljust(30), result[i + 1]))
    else:
        result = evaluate(program, int(opts['--input']), trace=opts['--trace'])
        print('Result: {}'.format(result))


if __name__ == '__main__':
    pass
    main(sys.argv[1:])