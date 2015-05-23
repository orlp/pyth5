import unittest

from . import pyth


class PythTestBase:
    def assert_expected(self, source, expected, stdin=""):
        try:
            result, error = pyth.run_code(source, stdin)
            if error is not None:
                raise error

            # Strip trailing newline.
            if result.endswith('\n'):
                result = result[:-1]

            self.assertEqual(expected, result)
        except Exception as e:
            msg = e.args[0]
            msg += '\n-- source --\n{}'.format(source)
            if stdin:
                msg += '\n-- stdin --\n{}'.format(stdin)
            e.args = (msg,) + e.args[1:]
            raise e


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
            self.assert_expected(source, expected)

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
        self.assert_expected("1\n2", "1\n2")


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
    """


# /
# :
# ;
# <
# =
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
