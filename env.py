import collections.abc


# Helper functions.
def isint(obj):
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
        i = int
        s = str
        l = list
        q = seq
    """

    assert(len(pattern) == len(objs))

    checkers = {
        "a": lambda o: True,
        "i": isint,
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

    if issig("is", a, b) or issig("si", a, b):
        return str(a) + str(b)




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
