import os
import sys
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import time

from collections import defaultdict
from collections import OrderedDict
from random import randint, random

# the purpose of this script is to re-learn how to fit a polynomial to a set 
# of points. why is it included under 'random'? this was motivated by a passage 
# in http://www.mail-archive.com/cryptography@c2.net/msg01708.html, namely:

# "(...) This use of deltas is approximately the same as attempting to fit an n
# degree polynomial to the previous n+1 points, then looking to see how far
# the new point is from the best prediction based on the previous n points.
# The minimum of the deltas is used, which has the effect of taking the best
# fit of a 0th, 1st or 2nd degree polynomial, and using that one."

# this was a bit confusing to me at first (being the math illiterate that i am...), 
# but after searching a bit i've figured out this refers to the method of 'finite 
# differences' (see this http://mathforum.org/library/drmath/view/56953.html for 
# an explanation).

def linear_regression(input_data, poly_order):

    # we now generate A and B matrices, to solve a systems of eqs. Ax = B. A 
    # and B encode the n + 1 partial derivatives of the squared error at each 
    # data point. the error is:
    #
    # sqrd_err = sum^n (y_i - f(x_i))^2 = sum^n (y_i - (a_0 + a_1*x_i + a_2*x_i^2 + ... + a_n*x_i^n))^2

    # save array of sums of powers for x
    powers_x = []   
    # first sum of powers is sum^n (x^0) = n
    powers_x.append(len(input_data))
    for p in np.arange(1, (2 * poly_order) + 1):
        powers_x.append(sum(np.power(input_data['X'], p)))

    # build the A matrix
    A = np.array(powers_x[0:(poly_order + 1)])
    for i in np.arange(1, (poly_order + 1)):
        A = np.vstack((A, powers_x[i:(i + poly_order + 1)]))

    # build the B matrix
    B = np.array(sum(input_data['Y']))
    for p in np.arange(1, poly_order + 1):
        B = np.vstack((B, sum(input_data['Y'] * np.power(input_data['X'], p))))

    # finally, use numpy's numpy.linalg.solve to solve the system of eqs., 
    # giving you the coefficients for the n-degree polynomial

    # FIXME: it would be great to implement your own method of solving this, 
    # through Gaussian elimination
    s = np.linalg.solve(A, B)
    f = np.poly1d(s[::-1,0])

    # return the polynomial coefficients
    return f

def calc_finite_diffs(sequence, poly_order):

    # we save the i-th order differences as lists in a dictionary. key i (0 to 
    # poly_order) holds the row of i-th differences
    diffs = OrderedDict()
    # we define the 0-th differences as the sequence itself (N = len(sequence) values)
    diffs[0] = list(sequence)

    # fill in the remaining d-th order differences (each with N - d values)
    for i, n in enumerate(sequence):

        if i < 1:
            continue

        for d in np.arange(1, min(poly_order, i) + 1):

            if d not in diffs:
                diffs[d] = []

            diffs[d].append(abs(diffs[d - 1][i - (d - 1)] - diffs[d - 1][i - d]))

    return diffs

def finite_differences(sequence, poly_order):

    diffs = calc_finite_diffs(sequence, poly_order + 1)

    for d in diffs:
        print("diffs[%d] = %s" % (d, str(diffs[d])))

    return 0

def gen_random_seq(size, max_int):

    random_seq = []

    for i in np.arange(size):
        random_seq.append(randint(1, max_int))

    return random_seq

if __name__ == "__main__":

    # use an ArgumentParser for a nice CLI
    parser = argparse.ArgumentParser()
    # options (self-explanatory)
    parser.add_argument(
        "--input-data", 
         help = """input file w/ points to fit (.tsv format)""")

    parser.add_argument(
        "--degree", 
         help = """degree of polynomial for fitting""")

    args = parser.parse_args()

    if not args.input_data:
        sys.stderr.write("""%s: [ERROR] no input data provided\n""" % sys.argv[0])
        parser.print_help()
        sys.exit(-1)

    # degree of polynomial to fit
    degree = int(args.degree)

    # read input data from a .tsv file ('tab separated'), basically with 
    # x and y columns, e.g.:
    #
    # 	X	Y
    #	0 	2
    #	1   10
    # 	2   5
    #	...
    input_data = pd.read_csv(args.input_data, sep="\t")

    # plot data points and fitted curves
    fig = plt.figure(figsize=(15,4))
    colors = ['blue', 'red', 'green', 'orange']

    # first, let's do a typical linear regression, considering all points
    ax1 = fig.add_subplot(131)
    ax1.grid(True)

    ax1.plot(input_data['X'], input_data['Y'], 'o', color = 'black')

    for d in np.arange(1, degree + 1):

        # linear regression w/ polynomial of degree d
        poly = linear_regression(input_data, d)

        # expand the nr. of points in the x axis in-between x_min and x_max
        x_new = np.linspace(0, len(input_data), 50)
        # plot the fitted curve
        ax1.plot(x_new, poly(x_new), '-', color = colors[d - 1])

    ax2 = fig.add_subplot(132)
    ax2.grid(True)

    # plot the polynomial fitting for degrees 1 to degree
    y_new = defaultdict(list)

    for d in np.arange(1, degree + 1):

        # linear regression w/ polynomial of degree d
        poly = linear_regression(input_data.iloc[:len(input_data) - 1], d)

        # expand the nr. of points in the x axis in-between x_min and x_max
        x_new = np.linspace(0, len(input_data), 50)
        # save the fitted points
        y_new[d] = poly(x_new)

        # plot the fitted curve
        ax2.plot(x_new, y_new[d], '-', color = colors[d - 1])
        ax2.plot([x_new[-1:] - 1, x_new[-1:]], poly([x_new[-1:] - 1, x_new[-1:]]), 'o', color = colors[d - 1])

    # plot the data points
    ax2.plot(input_data['X'], input_data['Y'], 'o', color = 'black')
    
    plt.savefig("entropy-estimation.pdf", bbox_inches='tight', format = 'pdf')

    # # after the initial exercise on 'typical' curve fitting (using linear 
    # # regression), we now explore a bit more the relationship between 
    # # finite differences and entropy estimation
    # fig = plt.figure(figsize=(10,4))
    # ax2 = fig.add_subplot(121)
    # ax2.grid(True)

    # # first, let's take one of the fundamental assumptions of the estimator: 
    # # the timing events from which randomness is gathered are 'expected' to occur 
    # # on a low degree polynomial. for our case, let's assume the polynomial 
    # # which is 'expected' by an attacker is the one found just above via 
    # # linear regression
    # x_new = np.linspace(0, 10, 50)
    # y_new = f(x_new)
    # ax2.plot(x_new, y_new, '-')

    # # # now, apply some random +- variance to f(x_new)
    # # y_random = []
    # # for y in f(input_data['X']):
    # #     y_random.append(y + (random()))

    # # ax2.plot(input_data['X'], y_random, 'o', color = 'red')

    # finite_differences(f(input_data['X']), poly_order)

    # plt.savefig("entropy-estimation.pdf", bbox_inches='tight', format = 'pdf')