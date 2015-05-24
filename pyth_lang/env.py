import collections.abc
import itertools
import math


class BadTypeCombinationError(Exception):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __str__(self):
        error_message = "\n    function '{}'".format(self.func)
        for i, arg in enumerate(self.args):
            error_message += '\n    arg {}: {!r}, type {}.'.format(i + 1, arg, type(arg).__name__)
        return error_message


# Helper functions.
def isreal(obj):
    return isinstance(obj, int)


def isstr(obj):
    return isinstance(obj, str)


def islist(obj):
    return isinstance(obj, list)


def isseq(obj):
    return isinstance(obj, collections.abc.Sequence)


def issig(pattern, *objs):
    """Helper function to check the signature of the objects.

    Type codes:

        _ = None
        a = any (not None)
        r = real
        s = str
        l = list
        q = seq
    """

    assert(len(pattern) == len(objs))

    checkers = {
        '_': lambda o: o is None,
        'a': lambda o: o is not None,
        'r': isreal,
        's': isstr,
        'l': islist,
        'q': isseq,
    }

    return all(checkers[t](o) for t, o in zip(pattern, objs))


def real_to_range(r):
    n = math.floor(r)
    if n < 0:
        return range(n, 0)
    return range(0, n)


def autoprint(a):
    if a is not None:
        print(a)


# !
def Pnot(a):
    return int(not a)


# '
# #
# $
# %
# &
# '
# (
# )
# *
def times(a, b):
    if issig('rr', a, b):
        return a * b

    if issig('rq', a, b):
        return int(a) * b

    if issig('qr', a, b):
        return a * int(b)

    if issig('ss', a, b):
        return [p + q for p, q in itertools.product(a, b)]

    if issig('qq', a, b):
        return [list(tup) for tup in itertools.product(a, b)]

    raise BadTypeCombinationError('times', a, b)


# +
def plus(a=None, b=None):
    if issig('__', a, b):
        return float('inf')

    if issig('r_', a, b):
        return abs(a)

    if type(a) is type(b):
        return a + b

    if issig('al', a, b):
        return [a] + b

    if issig('la', a, b):
        return a + [b]

    if issig('rs', a, b) or issig('sr', a, b):
        return str(a) + str(b)

    raise BadTypeCombinationError('plus', a, b)


# ,
def pair(a=None, b=None):
    if issig('__', a, b):
        return []

    if issig('a_', a, b):
        return [a]

    return [a, b]


# -
def minus(a=None, b=None):
    if issig('__', a, b):
        return -float('inf')

    if issig('r_', a, b):
        return -abs(a)

    if issig('rr', a, b):
        return a - b

    if issig('rl', a, b):
        return [el for el in real_to_range(a) if el not in b]

    if issig('lr', a, b) or issig('ls', a, b):
        return [el for el in a if el != b]

    if issig('ll', a, b):
        return [el for el in a if el not in b]

    if issig('ss', a, b) or issig('sr', a, b) or issig('rs', a, b):
        return str(a).replace(str(b), '')

    if issig('sl', a, b):
        for el in b:
            a = a.replace(str(el), '')
        return a

    raise BadTypeCombinationError('minus', a, b)


# /
# :
# ;
# <
# =
# >
# ?
# @
# [
# \
# ]
def one_list(a=None):
    if a is None:
        return []

    return [a]


# ^
# _
def neg(a):
    if isreal(a):
        return -a

    if isseq(a):
        return a[::-1]

    raise BadTypeCombinationError('neg', a)


# `
Prepr = repr


# {
# |
# }
# ~
# a
# b
# c
# d
# e
# f
# g
# h
def head(a):
    if isseq(a):
        return a[0]

    if isreal(a):
        return a + 1

    raise BadTypeCombinationError('head', a)


# i
# j
# k
# l
def Plen(a):
    if isseq(a):
        return len(a)

    if isreal(a):
        return math.log(a, 2)

    raise BadTypeCombinationError('Plen', a)
# m
# n
# o
# p
def Pprint(a=None):
    if a is not None:
        print(a, end="")


# q
# r
# s
# t
def tail(a):
    if isseq(a):
        return a[1:]

    if isreal(a):
        return a - 1

    raise BadTypeCombinationError('tail', a)


# u
# v
# w
# x
# y
# z
# A
# B
# C
# D
# E
# F
# G
# H
# I
# J
# K
# L
# M
# N
# O
# P
# Q
# R
# S
# T
# U
# V
# W
# X
# Y
# Z
# .!
# .#
# .$
# .%
# .&
# .'
# .(
# .)
# .*
# .+
# .,
# .-
# ./
# .:
# .;
# .<
# .=
# .>
# .?
# .@
# .[
# .\
# .]
# .^
# ._
# .`
# .{
# .|
# .}
# .~
# .a
# .b
# .c
# .d
# .e
# .f
# .g
# .h
# .i
# .j
# .k
# .l
# .m
# .n
# .o
# .p
# .q
# .r
# .s
# .t
# .u
# .v
# .w
# .x
# .y
# .z
# .A
# .B
# .C
# .D
# .E
# .F
# .G
# .H
# .I
# .J
# .K
# .L
# .M
# .N
# .O
# .P
# .Q
# .R
# .S
# .T
# .U
# .V
# .W
# .X
# .Y
# .Z


def make_env():
    blacklist = ['collections', 'itertools', 'math'
                 'BadTypeCombinationError',
                 'isreal', 'isstr', 'islist', 'isseq', 'issig', 'real_to_range',
                 'make_env', 'run']

    env = {'__builtins__': {}}
    env.update({k: v for k, v in globals().items() if k not in blacklist and not k.startswith('_')})

    return env


def run(code, env=None):
    if env is None:
        env = make_env()

    exec(code, env)
