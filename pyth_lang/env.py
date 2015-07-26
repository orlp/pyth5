import collections.abc
import itertools
import functools
import copy
import sympy as sym

from sympy import Rational as Real


class BadTypeCombinationError(Exception):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __str__(self):
        error_message = "\n    function '{}'".format(self.func)
        for i, arg in enumerate(self.args):
            error_message += '\n    arg {}: {!r}, type {}.'.format(i + 1, arg, type(arg).__name__)
        return error_message


# The environment of Pyth.
environment = {}
precision = Real(20)


# Helper functions.
def isreal(obj):
    return isinstance(obj, sym.Expr)


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
    n = sym.floor(r)
    if n < 0:
        return sym.Range(n, 0)
    return sym.Range(0, n)


def Pstr(a):
    if isreal(a):
        if a == sym.oo:
            return 'inf'
        if a == -sym.oo:
            return '-inf'
        if a.is_integer:
            return str(a)

        s = str(a.evalf(precision)).rstrip('0').rstrip('.')
        return s or '0'

    if islist(a):
        return '[{}]'.format(', '.join(map(Prepr, a)))

    return str(a)


def autoprint(a):
    if a is not None:
        print(Pstr(a))


def makeiter(r):
    if isreal(r):
        return real_to_range(r)

    return r


# !
def Pnot(a):
    return Real(not a)


# &
# |
# ?
# (
# )
# ;
# [
# ]
def one_list(a=None):
    if a is None:
        return []

    return [a]


# ,
def pair(a=None, b=None):
    if issig('__', a, b):
        return []

    if issig('a_', a, b):
        return [a]

    return [a, b]


# _
def neg(a):
    if isreal(a):
        return -a

    if isseq(a):
        return a[::-1]

    raise BadTypeCombinationError('neg', a)


# +
def plus(a=None, b=None):
    if issig('__', a, b):
        return sym.oo

    if issig('r_', a, b):
        return sym.Abs(a)

    if issig('rr', a, b) or type(a) is type(b):
        return a + b

    if issig('al', a, b):
        return [a] + b

    if issig('la', a, b):
        return a + [b]

    if issig('rs', a, b) or issig('sr', a, b):
        return Pstr(a) + Pstr(b)

    raise BadTypeCombinationError('plus', a, b)


# -
def minus(a=None, b=None):
    if issig('__', a, b):
        return -sym.oo

    if issig('r_', a, b):
        return -sym.Abs(a)

    if issig('rr', a, b):
        return a - b

    if issig('rl', a, b):
        return [el for el in real_to_range(a) if el not in b]

    if issig('lr', a, b) or issig('ls', a, b):
        return [el for el in a if el != b]

    if issig('ll', a, b):
        return [el for el in a if el not in b]

    if issig('ss', a, b) or issig('sr', a, b) or issig('rs', a, b):
        return Pstr(a).replace(Pstr(b), '')

    if issig('sl', a, b):
        for el in b:
            a = a.replace(Pstr(el), '')
        return a

    raise BadTypeCombinationError('minus', a, b)


# *
def times(a, b):
    if issig('rr', a, b):
        return a * b

    if issig('rq', a, b):
        return sym.floor(a) * b

    if issig('qr', a, b):
        return a * sym.floor(b)

    if issig('ss', a, b):
        return [p + q for p, q in itertools.product(a, b)]

    if issig('qq', a, b):
        return [list(tup) for tup in itertools.product(a, b)]

    raise BadTypeCombinationError('times', a, b)


# /
# %
# ^
def power(a, b):
    if issig('rr', a, b):
        return sym.Pow(a, b)

    if issig('sr', a, b):
        return [p + q for p, q in itertools.product(a, repeat=sym.floor(b))]

    if issig('qr', a, b):
        return [list(tup) for tup in itertools.product(a, repeat=sym.floor(b))]

    raise BadTypeCombinationError('power', a, b)


# =
def assign(a, b):
    if not isstr(a):
        raise BadTypeCombinationError('assign', a, b)

    environment[a] = b
    return b


# ~
def post_assign(a, b):
    if not isstr(a):
        raise BadTypeCombinationError('post-assign', a, b)

    old = environment[a]
    environment[a] = b
    return old


# <
def less_than(a, b):
    if issig('qr', a, b):
        return a[:sym.floor(b)]

    if issig('rq', a, b):
        return b[:-sym.floor(a)]

    if issig('rr', a, b) or issig('ll', a, b) or issig('ss', a, b):
        return Real(bool(a < b))

    raise BadTypeCombinationError('less_than', a, b)


# >
def greater_than(a, b):
    if issig('qr', a, b):
        return a[sym.floor(b):]

    if issig('rq', a, b):
        return b[-sym.floor(a):]

    if issig('rr', a, b) or issig('ll', a, b) or issig('ss', a, b):
        return Real(bool(a > b))

    raise BadTypeCombinationError('greater_than', a, b)


# :
# @
# {
# }
def Pin(a, b):
    if issig('al', a, b):
        return Real(a in b)

    if issig('rr', a, b) or issig('rs', a, b) or issig('sr', a, b) or issig('ss', a, b):
        return Real(Pstr(a) in Pstr(b))

    raise BadTypeCombinationError('Pin', a, b)


# `
def Prepr(a):
    if isstr(a):
        return "'{}'".format(a)

    return Pstr(a)


# '
# #
# $
# a
a = "abcdefghijklmnopqrstuvwxyz"


# b
b = "\n"


# c
c = " "


# d
d = ""


# e
e = Real(10)


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
k = ""


# l
def Plen(a):
    if isseq(a):
        return Real(len(a))

    if isreal(a):
        return sym.log(a, 2)

    raise BadTypeCombinationError('Plen', a)


# m
# n
# o
def order_by(a, b):
    if isstr(a):
        return "".join(sorted(a, key=b))

    return list(sorted(makeiter(a), key=b))


# p
def Pprint(a):
    print(Pstr(a), end="")
    return a


# q
def equals(a, b):
    return Real(bool(a == b))


# r
# s
def Psum(a):
    if isstr(a):
        return Real(a)

    if islist(a):
        if a:
            return functools.reduce(plus, a)

        return Real(0)

    if isreal(a):
        return sym.floor(a)

    raise BadTypeCombinationError('Psum', a)


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
w = []


# x - intentionally left undefined.
# y - intentionally left undefined.
# z
z = Real(0)


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
def Psorted(a):
    if isreal(a):
        a = sym.floor(a)
        if a < 0:
            return list(sym.Range(1+a, 1))
        return list(sym.Range(1, 1+a))

    if islist(a):
        return list(sorted(a))

    if isstr(a):
        return "".join(sorted(a))

    raise BadTypeCombinationError('Psorted', a)


# T
# U
def unary_range(a):
    if isreal(a):
        return list(real_to_range(a))

    if isseq(a):
        return list(range(len(a)))

    raise BadTypeCombinationError('unary_range', a)


# V
# W
# X
# Y
# Z
# .!
def factorial(a):
    if isreal(a):
        if not a.is_integer:
            a = a.evalf(precision)

        return sym.factorial(a)

    raise BadTypeCombinationError('factorial', a)


# .&
# .|
# .?
# .(
# .)
# .;
# .[
# .]
# .,
# ._
# .+
# .-
# .*
# ./
# .%
# .^
# .=
# .<
def leftshift(a, b):
    if issig('rr', a, b):
        return Real(int(sym.floor(a)) << int(sym.floor(b)))

    if issig('qr', a, b):
        b = sym.floor(b)
        return a[b:] + a[:b]

    raise BadTypeCombinationError('leftshift', a, b)


# .>
def rightshift(a, b):
    if issig('rr', a, b):
        return Real(int(sym.floor(a)) >> int(sym.floor(b)))

    if issig('qr', a, b):
        b = sym.floor(b)
        return a[-b:] + a[:-b]

    raise BadTypeCombinationError('rightshift', a, b)


# .:
# .@
# .{
# .}
# .`
# .'
# .~
# .#
# .$
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
# $a
dollar_a = 'abcdefghijklmnopqrstuvwxyz'


# $q
dollar_q = 'qwertyuiopasdfghjklzxcvbnm'


# $A
dollar_A = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


# $Q
dollar_Q = 'QWERTYUIOPASDFGHJKLZXCVBNM'


def run(code):
    blacklist = {'collections', 'itertools', 'copy', 'sym', 'functools',
                 'BadTypeCombinationError',
                 'isreal', 'isstr', 'islist', 'isseq', 'issig', 'real_to_range',
                 'run'}
    environment.clear()
    clean_env = {k: copy.deepcopy(v) for k, v in globals().items() if k not in blacklist and not k.startswith('_')}
    environment.update(clean_env)

    exec(code, environment)
