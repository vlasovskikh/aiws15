from collections import namedtuple
import unittest
from funcparserlib.lexer import make_tokenizer
from funcparserlib.parser import some, skip, many, finished


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


class Analysis:
    bottom = None
    initial = None

    @staticmethod
    def plus_1(x):
        pass

    @staticmethod
    def minus_1(x):
        pass

    @staticmethod
    def is_zero(x):
        pass

    @staticmethod
    def non_zero(x):
        pass

    @staticmethod
    def widen(x):
        return x