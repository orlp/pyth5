import collections.abc


class BadTypeCombinationError(Exception):
    def __init__(self, func, *args):
        self.func = func
        self.args = args

    def __str__(self):
        error_message = "\n    function '{}'".format(self.func)
        for i, arg in enumerate(self.args):
            error_message += "\n    arg {}: {!r}, type {}.".format(i + 1, arg, type(arg).__name__)
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

        a = any
        r = real
        s = str
        l = list
        q = seq
    """

    assert(len(pattern) == len(objs))

    checkers = {
        "a": lambda o: True,
        "r": isreal,
        "s": isstr,
        "l": islist,
        "q": isseq,
    }

    return all(checkers[t](o) for t, o in zip(pattern, objs))


# +.
def add(a, b):
    if type(a) is type(b):
        return a + b

    if issig("al", a, b):
        return [a] + b

    if issig("la", a, b):
        return a + [b]

    if issig("rs", a, b) or issig("sr", a, b):
        return str(a) + str(b)

    raise BadTypeCombinationError("add", a, b)


# *.
def mul(a, b):
    return a * b


# p.
def Pprint(a, b="\n"):
    print(a, end=b)


def make_env():
    env = {"__builtins__": {}}
    env["add"] = add
    env["mul"] = mul
    env["Pprint"] = Pprint
    return env


def run(code, env=None):
    if env is None:
        env = make_env()

    exec(code, env)
