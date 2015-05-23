import collections.abc
import itertools


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

        a = any
        r = real
        s = str
        l = list
        q = seq
    """

    assert(len(pattern) == len(objs))

    checkers = {
        'a': lambda o: True,
        'r': isreal,
        's': isstr,
        'l': islist,
        'q': isseq,
    }

    return all(checkers[t](o) for t, o in zip(pattern, objs))


# !
# '
# #
# $
# %
# &
# '
# (
# )
# *
def mul(a, b):
    if issig('rr', a, b):
        return a * b

    if issig('rq', a, b):
        return int(a) * b

    if issig('qr', a, b):
        return a * int(b)

    if issig('qq', a, b):
        return [list(tup) for tup in itertools.product(a, b)]

    raise BadTypeCombinationError('mul', a, b)


# +
def add(a, b):
    if type(a) is type(b):
        return a + b

    if issig('al', a, b):
        return [a] + b

    if issig('la', a, b):
        return a + [b]

    if issig('rs', a, b) or issig('sr', a, b):
        return str(a) + str(b)

    raise BadTypeCombinationError('add', a, b)


# ,
# -
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
def one_list(a):
    return [a]


# ^
# _
# `
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
# i
# j
# k
# l
# m
# n
# o
# p
def Pprint(a, b='\n'):
    print(a, end=b)


# q
# r
# s
# t
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
# ."
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
    blacklist = ['collections', 'itertools',
                 'BadTypeCombinationError',
                 'isreal', 'isstr', 'islist', 'isseq', 'issig',
                 'make_env', 'run']

    env = {'__builtins__': {}}
    env.update({k: v for k, v in globals().items() if k not in blacklist and not k.startswith('_')})

    return env


def run(code, env=None):
    if env is None:
        env = make_env()

    exec(code, env)
