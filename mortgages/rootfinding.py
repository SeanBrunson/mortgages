# Class to setup root finding algorithm for practice. One could use
# the Scipy package for more optimized methods.

import numpy as np


class OptimalRoots(object):
    """
    Class to hold values from a root finding algorithm.

    Parameters
    ----------
    root_value: float
        Value of the root.
    func_value: float
        Value of the function.
        Should be close to 0.
    iteration: int
        Number of iterations.
    """

    def __init__(self, root_value, func_value, iteration):
        self.root_value = root_value
        self.func_value = func_value
        self.iteration = iteration


def brent(f, a, b, args=(), max_iteration=100, tolerance=1e-8):
    """
    Calculate roots using Brent's method.

    Parameters
    ----------
    f: function
        Objective function.
    a: float
        Lower bound for the roots.
    b: float
        Upper bound for the roots.
    args: tuple, optional
        Additional arguments for the function.
    max_iteration: int, optional
        Max number of iterations for the root finding algorithm.
    tolerance: float, optional
        Tolerance criteria for the root finding algorithm.

    Returns
    -------
    root_value: float
        Value of the root.
    func_value: float
        Value of the function.
        Should be close to 0.
    iteration: int
        Number of iterations.

    """

    # Calculate end points:
    fa = f(*((a,) + args))
    fb = f(*((b,) + args))

    # Check if fa is less than fb
    if abs(fa) < abs(fb):
        a, b = b, a
        fa, fb, = fb, fa

    # Create point c and d:
    c = a
    fc = fa
    d = 0.0

    # Loop until root found:
    loop_counter = 0
    mflag = 1

    while loop_counter <= max_iteration:
        # Update counter:
        loop_counter = loop_counter + 1

        # Update point:
        if (fa != fc) and (fb != fc):
            # Inverse quadratic interpolation:
            term_one = (a*fb*fc) / ((fa - fb)*(fa - fc))
            term_two = (b*fa*fc) / ((fb - fa)*(fb - fc))
            term_three = (c*fa*fb) / ((fc - fa)*(fc - fb))

            s = term_one + term_two + term_three
        else:
            # Secant method:
            s = b - (fb*(b - a)/(fb - fa))

        # Setup some conditions:
        between_numbers = np.sort([(3.0*a + b)/4.0, b])
        condition_one = (s < between_numbers[0]) and \
                        (s > between_numbers[1])
        condition_two = (mflag == 1) and \
                        (abs(s-b) >= (abs(b-c) * 0.5))
        condition_three = (mflag == 0) and \
                          (abs(s-b) >= (abs(c-d) * 0.5))
        condition_four = (mflag == 1) and (abs(b-c) < abs(tolerance))
        condition_five = (mflag == 0) and (abs(c-d) < abs(tolerance))

        # Check conditions:
        if condition_one or condition_two or condition_three or \
                condition_four or condition_five:
            # Bisection method:
            s = 0.5 * (a+b)
            mflag = 1
        else:
            mflag = 0

        # Calculate f(s):
        fs = f(*((s,) + args))

        # Update points:
        d = c
        c = b
        fc = fb

        if (fa * fs) < 0.0:
            b = s
            fb = fs
        else:
            a = s
            fa = fs

        # Check if fa is less than fb:
        if abs(fa) < abs(fb):
            a, b = b, a
            fa, fb, = fb, fa

        # Check convergence:
        if (abs(fb) <= tolerance) or (abs(fs) <= tolerance) or (
                abs(b-a) <= tolerance):
            return OptimalRoots(s, fs, loop_counter)

        if loop_counter == max_iteration:
            return OptimalRoots(s, fs, loop_counter)
