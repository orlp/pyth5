import unittest
import sys

from . import pyth


class PythAssertionError(AssertionError):
    def __init__(self, orig_except, source, expected, stdin):
        self.orig_except = orig_except
        self.source = source
        self.expected = expected
        self.stdin = stdin

    def __str__(self):
        msg = "\n{}: {}".format(type(self.orig_except).__name__, str(self.orig_except))
        msg += '\n\n-- source --\n{}'.format(self.source)
        if self.stdin:
            msg += '\n-- stdin --\n{}'.format(self.stdin)

        return msg


class PythTestBase:
    def assert_pyth(self, source, expected, stdin=""):
        try:
            result, error = pyth.run_code(source, stdin)
            if error is not None:
                raise error

            # Strip trailing newline.
            if result.endswith('\n'):
                result = result[:-1]

            self.assertEqual(expected, result)
        except Exception as e:
            orig_tb = sys.exc_info()[2]
            raise PythAssertionError(e, source, expected, stdin).with_traceback(orig_tb) from None


class PythTest(type):
    def __new__(cls, name, bases, classdict):
        bases = bases + (unittest.TestCase, PythTestBase)

        if '__doc__' in classdict:
            actual_text = '\n'.join(line[4:] for line in classdict['__doc__'].split('\n')[1:-1])
            auto_tests = actual_text.split('\n---\n')

            for testnr, test in enumerate(auto_tests):
                source, *expected = test.split('\n')
                expected = '\n'.join(expected)
                classdict['test{}'.format(testnr + 1)] = cls.gen_test(source, expected)

        return super().__new__(cls, name, bases, classdict)

    @classmethod
    def gen_test(cls, source, expected):
        def test_code(self):
            self.assert_pyth(source, expected)

        return test_code


#
class Blank(metaclass=PythTest):
    r"""
     1
    ---
     "test"
    """


# \n
class Newline(metaclass=PythTest):
    def test_newline(self):
        self.assert_pyth("1\n2", "1\n2")


# !
class Not(metaclass=PythTest):
    r"""
    !0
    1
    ---
    !]
    1
    ---
    !""
    1
    ---
    !42
    0
    ---
    !]]
    0
    ---
    !"foo"
    0
    """


# "
class String(metaclass=PythTest):
    r"""
    ""

    ---
    "test"
    test
    ---
    "ye
    ye
    """


# #
# $
# %
# &
# '
# (
# )
class Close(metaclass=PythTest):
    r"""
    [5)10
    [5]
    10
    ---
    [[5)10
    [[5], 10]
    """


# *
class Times(metaclass=PythTest):
    r"""
    *3 5
    15
    ---
    *3"ni"
    ninini
    ---
    *." "5
    [32, 32, 32, 32, 32]
    ---
    *[10 20)[40 10)
    [[10, 40], [10, 10], [20, 40], [20, 10]]
    ---
    *"foo""bar"
    ['fb', 'fa', 'fr', 'ob', 'oa', 'or', 'ob', 'oa', 'or']
    """


# +
class Plus(metaclass=PythTest):
    r"""
    +3 5
    8
    ---
    ++"hello"", ""world"
    hello, world
    ---
    +"the answer is "42
    the answer is 42
    ---
    +99" bottles"
    99 bottles
    ---
    +"test"[42 10 5
    ['test', 42, 10, 5]
    ---
    +[3 2 1)"go"
    [3, 2, 1, 'go']
    ---
    +[3 2 1)]]"go
    [3, 2, 1, ['go']]
    ---
    +_42)
    42
    ---
    +10
    10
    ---
    +)
    inf
    """


# ,
class Pair(metaclass=PythTest):
    r"""
    ,
    []
    ---
    ,42
    [42]
    ---
    ,"foo""bar"
    ['foo', 'bar']
    ---
    ,,42 5
    [[42, 5]]
    """


# -
class Minus(metaclass=PythTest):
    r"""
    -10 5
    5
    ---
    -10)
    -10
    ---
    -_42
    -42
    ---
    -)
    -inf
    ---
    -10[3 6 1)
    [0, 2, 4, 5, 7, 8, 9]
    ---
    -_7[3 "test" _2)
    [-7, -6, -5, -4, -3, -1]
    ---
    -["test" 42 5)5
    ['test', 42]
    ---
    -[0 "bar" 1 "foo" 2)"foo"
    [0, 'bar', 1, 2]
    ---
    -[0 1 2 3)[2 "foo" 3)
    [0, 1]
    ---
    -["foo" "test" 24 3),24"test"
    ['foo', 3]
    ---
    -"1250821084802134"1
    2508208480234
    ---
    -`"101015"101
    '015'
    ---
    -42"2"
    4
    ---
    -"8805808"80
    858
    ---
    -"testest""test"
    est
    ---
    -"nininini""ni"
    ---
    -"nfooninibaro"["ni""foobar")
    no
    """


# /
# :
# ;
class CloseAll(metaclass=PythTest):
    r"""
    [[5;10
    [[5]]
    10
    ---
    -+10;5
    -10
    5
    """


# <
# =
class Assign(metaclass=PythTest):
    r"""
    =Z5Z
    5
    ---
    Z+3=Z5Z
    0
    8
    5
    """


# >
# ?
# @
# [
class List(metaclass=PythTest):
    r"""
    [
    []
    ---
    [0
    [0]
    ---
    ["foo""bar")[10 20
    ['foo', 'bar']
    [10, 20]
    """


# \
class OneString(metaclass=PythTest):
    r"""
    \a
    a
    ---
    \\
    \
    """


# ]
class OneList(metaclass=PythTest):
    r"""
    ]5
    [5]
    ---
    ]]]"test"
    [[['test']]]
    ---
    ]
    []
    ---
    ]]
    [[]]
    """


# ^
# _
class Neg(metaclass=PythTest):
    r"""
    _5
    -5
    ---
    __42
    42
    ---
    _"foobar
    raboof
    ---
    __"ni
    ni
    ---
    _,2 3
    [3, 2]
    """


# `
class Repr(metaclass=PythTest):
    r"""
    `5
    5
    ---
    `"foo"
    'foo'
    ---
    `p""
    None
    """


# {
# |
class Or(metaclass=PythTest):
    r"""
    |3"test"
    3
    ---
    |0"foobar"
    foobar
    ---
    |1p"noeval"
    1
    """


# }
# ~
# a
# b
class LineBreak(metaclass=PythTest):
    r"""
    42b5
    42


    5
    """


# c
# d
# e
# f
# g
# h
class Head(metaclass=PythTest):
    r"""
    h0
    1
    ---
    h"test"
    t
    ---
    h[2 3 4
    2
    """


# i
# j
# k
# l
class Len(metaclass=PythTest):
    r"""
    l1
    0.0
    ---
    l"abd"
    3
    ---
    l"
    0
    ---
    l[1 2 3
    3
    """


# m
# n
# o
# p
class Print(metaclass=PythTest):
    r"""
    p10
    10
    ---
    p]10
    [10]
    ---
    p"test"
    test
    ---
    p10"test"
    10test
    ---
    p"foo""bar"
    foobar
    ---
    p"pier "10
    pier 10
    ---
    p"no ""newline,""please
    no newline,
    please
    """


# q
# r
# s
# t
class Tail(metaclass=PythTest):
    r"""
    t0
    -1
    ---
    t"test"
    est
    ---
    t[1 4 9)
    [4, 9]
    """


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
class Lambda(metaclass=PythTest):
    # TODO: recursion testcase.
    r"""
    L*5b2L50
    10
    250
    ---
    L0
    ---
    L0)L"test"
    0
    ---
    +L+2*3b5L10L30
    49
    92
    """


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
class Zero(metaclass=PythTest):
    r"""
    Z
    0
    ---
    +Z2
    2
    ---
    Z"test"
    0
    test
    """


# .!
# ."
class BinString(metaclass=PythTest):
    r"""
    .""
    []
    ---
    ." "
    [32]
    ---
    ."test"
    [116, 101, 115, 116]
    """


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
