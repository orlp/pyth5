import unittest

import pyth


class PythTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_auto(self):
        tests = [test.strip() for test in self.__doc__.split("\n\n")]
        for test in tests:
            source, expected = test.split("\n")
            result, error = pyth.run_code(source.strip())
            if error is not None:
                raise error
            self.assertEqual(expected.strip(), result)


class Add(PythTest):
    """
    +3 5
    8
    """


def run_all_tests():
    # print(pyth.run_code("+3 5"))
    unittest.main()


if __name__ == "__main__":
    run_all_tests()
