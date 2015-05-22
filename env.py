# +.
def add(a, b):
    return a + b


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
