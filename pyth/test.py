import unittest

from . import pyth


class PythTest(type):
    def __new__(cls, name, bases, classdict):
        bases = bases + (unittest.TestCase,)
        if "__doc__" in classdict:
            actual_text = "\n".join(line[4:] for line in classdict["__doc__"].split("\n")[1:-1])
            auto_tests = actual_text.split("\n---\n")

            for testnr, test in enumerate(auto_tests):
                source, *expected = test.split("\n")
                expected = "\n".join(expected)
                classdict["test{}".format(testnr + 1)] = cls.gen_test(source, expected)

        return super().__new__(cls, name, bases, classdict)

    @classmethod
    def gen_test(cls, source, expected):
        def test_code(self):
            result, error = pyth.run_code(source)
            if error is not None:
                raise error

            # Strip trailing newline.
            if result.endswith("\n"):
                result = result[:-1]

            self.assertEqual(expected, result, source)

        return test_code


# " and \
class String(metaclass=PythTest):
    r"""
    ""

    ---
    "test"
    test
    ---
    "ye
    ye
    ---
    \a
    a
    ---
    \\
    \
    """


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


# +
class Add(metaclass=PythTest):
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


# *
class Mul(metaclass=PythTest):
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


if __name__ == "__main__":
    unittest.main()