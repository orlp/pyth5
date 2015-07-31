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
    ---
    ,1 2
    [1, 2]
    """


# \n
class Newline(metaclass=PythTest):
    def test_newline(self):
        self.assert_pyth("1\n2", "1\n2")


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


# \
class OneString(metaclass=PythTest):
    r"""
    \a
    a
    ---
    \\
    \
    """


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


# &
class And(metaclass=PythTest):
    r"""
    &1 2
    2
    ---
    &0 3
    0
    ---
    &])"foo"
    []
    ---
    &""p"noeval
    """


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


# ?
class Ternary(metaclass=PythTest):
    r"""
    ?])2 3
    3
    ---
    ?0"test""foo"
    foo
    ---
    ?"test"1 3
    1
    ---
    ?0p"noeval""yay"
    yay
    """


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


# /
# %
# ^
class Power(metaclass=PythTest):
    r"""
    ^.04 .5
    0.2
    ---
    ^50 0
    1
    ---
    ^"bar"2
    ['bb', 'ba', 'br', 'ab', 'aa', 'ar', 'rb', 'ra', 'rr']
    ---
    ^U2 3
    [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 1, 1], [1, 0, 0], [1, 0, 1], [1, 1, 0], [1, 1, 1]]
    """


# =
class Assign(metaclass=PythTest):
    r"""
    =a5a
    5
    ---
    z+3=z5z
    0
    8
    5
    ---
    =+z5z
    5
    ---
    =z5=.!zz
    120
    """


# <
class LessThan(metaclass=PythTest):
    r"""
    <5 10
    1
    ---
    <5 5
    0
    ---
    <-)0
    1
    ---
    <0+)
    1
    ---
    <-)+)
    1
    ---
    <+)-)
    0
    ---
    <[1 2)[3 1)
    1
    ---
    <[3 1)[1 2)
    0
    ---
    <"nini"3
    nin
    ---
    <"foobar"0
    ---
    <3"nini"
    n
    """


# >
class GreaterThan(metaclass=PythTest):
    r"""
    >5 10
    0
    ---
    >5 5
    0
    ---
    >-)0
    0
    ---
    >0+)
    0
    ---
    >-)+)
    0
    ---
    >+)-)
    1
    ---
    >[1 2)[3 1)
    0
    ---
    >[3 1)[1 2)
    1
    ---
    >"nini"1
    ini
    ---
    >"foobar"_2
    ar
    ---
    >2"foobar"
    ar
    """


# :
# @
# {
# }
class In(metaclass=PythTest):
    r"""
    }5 .15
    1
    ---
    }3 42
    0
    ---
    }20"120"
    1
    ---
    }23"32"
    0
    ---
    }"test"["testing""bar"
    0
    ---
    }"test"["foo""test"
    1
    ---
    }3U4
    1
    ---
    }4U4
    0
    ---
    },1 2[,0 1,1 2,3 4
    1
    ---
    }[1)U4
    0
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
    `[5 [3"test"
    [5, [3, 'test']]
    """


# '
# ~
class PostAssign(metaclass=PythTest):
    r"""
    +2~+z3z
    2
    3
    ---
    ~+z10
    """


# #
class Forever(metaclass=PythTest):
    r"""
    #1B
    1
    ---
    #1hw)2
    1
    2
    """


# $
# a
class Alphabet(metaclass=PythTest):
    r"""
    a
    abcdefghijklmnopqrstuvwxyz
    ---
    =a5a
    5
    """


# b
class LineBreak(metaclass=PythTest):
    r"""
    42b5
    42


    5
    """


# c
class Space(metaclass=PythTest):
    r"""
    +c"foo
     foo
    ---
    =c5c
    5
    """


# d
class EmptyString(metaclass=PythTest):
    r"""
    s["foo"d"bar"
    foobar
    ---
    ld
    0
    """


# e
class Ten(metaclass=PythTest):
    r"""
    e
    10
    ---
    =e*e2e
    20
    """


# f
class Filter(metaclass=PythTest):
    r"""
    fU10<a5
    [0, 1, 2, 3, 4]
    ---
    fq.!a120
    5
    ---
    f2!-ae
    10
    """


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
    0
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
class Map(metaclass=PythTest):
    r"""
    m[1 2)a
    [1, 2]
    ---
    m5a
    [0, 1, 2, 3, 4]
    ---
    m5mab
    [[], [0], [0, 1], [0, 1, 2], [0, 1, 2, 3]]
    ---
    m3am3a
    [0, 1, 2]
    [0, 1, 2]
    """


# n
class NotEquals(metaclass=PythTest):
    r"""
    n00
    0
    ---
    n01
    1
    ---
    n"1"1
    1
    """


# o
class OrderBy(metaclass=PythTest):
    r"""
    o["cc""b""aaa")la
    ['b', 'cc', 'aaa']
    """


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
    ---
    +5p3
    38
    """


# q
class Equals(metaclass=PythTest):
    r"""
    q2 5
    0
    ---
    q3 3
    1
    ---
    q0 0
    1
    ---
    q"foo"+\f"oo"
    1
    ---
    q"foo""bar"
    0
    ---
    q,2"a"[2"a"
    1
    ---
    q[)]3
    0
    """


# r
# s
class Sum(metaclass=PythTest):
    r"""
    s.5
    0
    ---
    s_.5
    -1
    ---
    s1
    1
    ---
    s"1.5"
    1.5
    ---
    s"01"
    1
    ---
    sU5
    10
    ---
    s["foo""bar""ni""spam")
    foobarnispam
    ---
    s["foo"0"bar"1)
    foo0bar1
    ---
    s[
    0
    """


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
class EmptyList(metaclass=PythTest):
    r"""
    w
    []
    ---
    =w5w
    5
    """


# x
# y
class AutoAssign(metaclass=PythTest):
    r"""
    +x5xx
    10
    5
    ---
    *y10+y3y
    130
    10
    ---
    x3
    ---
    y10
    """


# z
class Zero(metaclass=PythTest):
    r"""
    z
    0
    ---
    +z2
    2
    ---
    z"test"
    0
    test
    """


# A
# B
class Break(metaclass=PythTest):
    r"""
    F[1 2)aB
    1
    ---
    F"test"F"12"+abB
    t1
    e1
    s1
    t1
    ---
    F"test"F"12"+ab)B
    t1
    t2
    """


# C
# D
# E
class Else(metaclass=PythTest):
    r"""
    I0p8 10E5
    5
    ---
    I8p3E5
    3
    ---
    F9Iqa5BE1
    ---
    F4Iqa5BE1
    1
    """


# F
class For(metaclass=PythTest):
    r"""
    F10)
    ---
    F[1 42 30 3)+a5a)10
    6
    1
    47
    42
    35
    30
    8
    3
    10
    ---
    F"test"+"ni"a
    nit
    nie
    nis
    nit
    ---
    F5^a3
    0
    1
    8
    27
    64
    ---
    F2F3,ab
    [0, 0]
    [0, 1]
    [0, 2]
    [1, 0]
    [1, 1]
    [1, 2]
    """


# G
# H
class End(metaclass=PythTest):
    r"""
    H[0 1 2)
    2
    ---
    H"abcd"
    d
    """


# I
class If(metaclass=PythTest):
    r"""
    I0p8 10)5
    5
    ---
    I8p3)5
    35
    """


# J
# K
# L
class Lambda(metaclass=PythTest):
    r"""
    L*5a2L50
    10
    250
    ---
    L0
    ---
    L|<a1*aLta5
    120
    ---
    L0)L"test"
    0
    ---
    +L+2*3a5L10L30
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
class Sorted(metaclass=PythTest):
    r"""
    S5
    [1, 2, 3, 4, 5]
    ---
    S_3
    [-2, -1, 0]
    ---
    S"test"
    estt
    ---
    S[1 5 2 0 9
    [0, 1, 2, 5, 9]
    ---
    S["foo""bar"
    ['bar', 'foo']
    """


# T
class Pop(metaclass=PythTest):
    r"""
    T[0 1 2)
    [0, 1]
    ---
    T"test"
    tes
    ---
    T13
    3
    ---
    T19.3
    9.3
    """


# U
class UnaryRange(metaclass=PythTest):
    r"""
    U[5 1 3
    [0, 1, 2]
    ---
    U4
    [0, 1, 2, 3]
    ---
    U_4
    [-4, -3, -2, -1]
    """


# V
# W
# X
# Y
# Z
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


# .\
# .!
class Factorial(metaclass=PythTest):
    r"""
    .!5
    120
    ---
    .!0
    1
    ---
    .!.5
    0.88622692545275801365
    """


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
class Leftshift(metaclass=PythTest):
    r"""
    .<3 3
    24
    ---
    .<0 10
    0
    ---
    .<1 8
    256
    ---
    .<"foobar"2
    obarfo
    ---
    .<U10 3
    [3, 4, 5, 6, 7, 8, 9, 0, 1, 2]
    """


# .>
class Rightshift(metaclass=PythTest):
    r"""
    .>24 3
    3
    ---
    .>0 10
    0
    ---
    .>256 8
    1
    ---
    .>7 1
    3
    ---
    .>"foobar"2
    arfoob
    ---
    .>U10 3
    [7, 8, 9, 0, 1, 2, 3, 4, 5, 6]
    """


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
class AlphabetDollar(metaclass=PythTest):
    r"""
    =a5$a
    abcdefghijklmnopqrstuvwxyz
    ---
    =$a5$a
    5
    """


# $A
class ALPHABET(metaclass=PythTest):
    r"""
    $A
    ABCDEFGHIJKLMNOPQRSTUVWXYZ
    ---
    =$a5$a
    5
    """


# $q
class Qwerty(metaclass=PythTest):
    r"""
    $q
    qwertyuiopasdfghjklzxcvbnm
    ---
    =$q5$q
    5
    """


# $Q
class QWERTY(metaclass=PythTest):
    r"""
    $Q
    QWERTYUIOPASDFGHJKLZXCVBNM
    ---
    =$Q5$Q
    5
    """
