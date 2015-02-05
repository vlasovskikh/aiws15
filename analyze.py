"""Run an analysis for 3 Counter Machine

Usage:
    analyze [options] (parity|bounds) PATH


Options:
    --help          Show help message
"""


import functools
import sys

from docopt import docopt
from bounds import BoundsAnalysis

from funcutils import fixed_point
from exercise03 import ParityAnalysis
from threecm import Inc, Dec, Zero, Stop, parse, Instruction, Analysis


def analyze(program, analysis):
    """Perform program analysis.

    :type program: list[Instruction]
    :type analysis: Analysis
    :rtype: dict[int, (Lattice, Lattice, Lattice)]
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

        :type s_hat: dict[int, (Lattice, Lattice, Lattice)]
        :rtype: dict[int, (Lattice, Lattice, Lattice)]
        """

        result = bottom_hat.copy()
        result[1] = analysis.initial

        def map_and_join(index, f):
            x, y, z = f(s_hat[pc])
            rx, ry, rz = result[index]
            return rx.join(x), ry.join(y), rz.join(z)

        for pc, i in instructions.items():
            if isinstance(i, Inc):
                index = pc + 1
                function = functools.partial(var_function, analysis.plus_1, i.v)
                result[index] = map_and_join(index, function)
            elif isinstance(i, Dec):
                index = pc + 1
                function = functools.partial(var_function, analysis.minus_1,
                                             i.v)
                result[index] = map_and_join(index, function)
            elif isinstance(i, Zero):
                index1 = i.pc1
                function1 = functools.partial(var_function, analysis.is_zero,
                                              i.v)
                result[index1] = map_and_join(index1, function1)

                index2 = i.pc2
                function2 = functools.partial(var_function, analysis.non_zero,
                                              i.v)
                result[index2] = map_and_join(index2, function2)
            elif isinstance(i, Stop):
                pass
            else:
                raise ValueError('unknown instruction: {}'.format(i))

        return result

    pcs = set(range(1, len(program) + 1))
    instructions = {pc: instruction(pc) for pc in pcs}
    bottom_hat = {pc: (analysis.bottom, analysis.bottom, analysis.bottom)
                  for pc in pcs}
    return fixed_point(f_hat)(bottom_hat)


def main(argv):
    opts = docopt(__doc__, argv=argv)
    with open(opts['PATH'], 'r') as fd:
        data = fd.read()
    program = parse(data)
    if opts['parity']:
        analysis = ParityAnalysis()
    elif opts['bounds']:
        analysis = BoundsAnalysis()
    else:
        raise ValueError('specify an analysis to run')
    result = analyze(program, analysis)
    for i, instruction in enumerate(program):
        print('{} {}'.format(repr(instruction).ljust(30), result[i + 1]))


if __name__ == '__main__':
    main(sys.argv[1:])
