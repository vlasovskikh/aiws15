"""Exercise 1.

http://janmidtgaard.dk/aiws15/exercises1.pdf
"""


import unittest
from funcutils import FixedPointNotReached, fixed_point


# 1. Give an example of a transition system that converges (i.e., reaches a
# stuck or final state in a finite number of steps)


def fibonacci(n):
    """An ordinary imperative Fibonacci function.

    :type n: int
    :rtype: int
    """
    a, b = 0, 1
    i = 0
    while i < n:
        a, b = b, (a + b)
        i += 1
    return b


def fibonacci_transitions(state):
    """Fibonacci function as a function for a transition system.

    :type state: (int, int, int, int)
    :rtype: set[(int, int, int, int)]
    """
    a, b, i, n = state
    if i < n:
        return b, a + b, i + 1, n
    else:
        return state


# 2. Give an example of a transition system that doesn't converge and whose
# reachable states collecting semantics converges (i.e., reaches a fixed point
# in a finite number of steps)


class TransitionSystem:
    @property
    def init_states(self):
        return set()

    @staticmethod
    def next(state):
        return set()


def invert(state):
    """Doesn't converge, but its reachable states collecting semantics does."""
    x, = state
    return -x,


class InvertTransitions(TransitionSystem):
    """Reachable states collecting semantics for invert(state)."""

    init_states = {(1,)}

    @staticmethod
    def next(state):
        x, = state
        return {(-x,)}


# 3. Give an example of a transition system that doesn't converge and whose
# reachable states collecting semantics doesn't converge


def increment(state):
    """Both the function and its reachable states don't converge."""
    x, = state
    return x + 1,


class IncrementTransitions(TransitionSystem):
    """Reachable states collecting semantics for increment(state)."""

    init_states = {(0,)}

    @staticmethod
    def next(state):
        x, = state
        return {(x + 1,)}


class ReachingStates:
    def __init__(self, transition_system):
        self.transition_system = transition_system

    def transition(self, states):
        """Transition function for collecting semantics.

        :type states: set[T]
        :rtype: set[T]
        """
        new_states = {new_state
                      for state in states
                      for new_state in self.transition_system.next(state)}
        return self.transition_system.init_states | new_states


class Test(unittest.TestCase):
    def test_converging_transition_system(self):
        # 1, 1, 2, 3, 5, 8
        f = fixed_point(fibonacci_transitions)
        self.assertEqual((0, 1, 0, 0), f((0, 1, 0, 0)))
        self.assertEqual((5, 8, 5, 5), f((0, 1, 0, 5)))

    def test_converging_reachable_states(self):
        self.assertRaises(FixedPointNotReached, fixed_point(invert), (1,))

        f = fixed_point(ReachingStates(InvertTransitions).transition)
        self.assertEqual({(1,), (-1,)}, f(set()))

    def test_non_converging_reachable_states(self):
        self.assertRaises(FixedPointNotReached, fixed_point(increment), (0,))

        f = fixed_point(ReachingStates(IncrementTransitions).transition)
        self.assertRaises(FixedPointNotReached, f, set())
