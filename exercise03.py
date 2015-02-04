"""Exercise 3. Parity analysis for 3 Counter Machine

Usage:
    exercise03 [options] PATH


Options:
    --help          Show help message
"""


import functools
from docopt import docopt
import sys
from funcutils import fixed_point
from parity import Top, Even, Bottom, is_zero, non_zero, plus_1, minus_1
from threecm import Inc, Dec, Zero, Stop, parse, Instruction


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


def main(argv):
    opts = docopt(__doc__, argv=argv)
    with open(opts['PATH'], 'r') as fd:
        data = fd.read()
    program = parse(data)
    result = analyze_parity(program)
    for i, instruction in enumerate(program):
        print('{} {}'.format(repr(instruction).ljust(30), result[i + 1]))


if __name__ == '__main__':
    main(sys.argv[1:])
