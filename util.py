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