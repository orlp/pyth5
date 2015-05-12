# "(":    I
# "#":    S
# "D":    S
# "E":    S
# "F":    S
# "I":    S
# "V":    S
# "W":    S
# "[":    X


BLOCK_TOKS = "#DEFIVW"

ARITIES = [
    "!":   1,
    "%":   2,
    "&":   2,
    "'":   1,
    "*":   2,
    "+":   2,
    ",":   2,
    "-":   2,
    "/":   2,
    ":":   3,
    "<":   2,
    "=":   2,
    ">":   2,
    "?":   3,
    "@":   2,
    "A":   3,
    "B":   0,
    "C":   1,
    "G":   0,
    "H":   0,
    "J":   1,
    "K":   1,
    "L":   1,
    "M":   1,
    "N":   0,
    "O":   1,
    "P":   1,
    "Q":   0,
    "R":   1,
    "S":   1,
    "T":   0,
    "U":   1,
    "X":   3,
    "Y":   0,
    "Z":   0,
    "]":   1,
    "^":   2,
    "_":   1,
    "`":   1,
    "a":   2,
    "b":   0,
    "c":   2,
    "d":   0,
    "e":   1,
    "f":   2,
    "g":   2,
    "h":   1,
    "i":   2,
    "j":   2,
    "k":   0,
    "l":   1,
    "m":   2,
    "n":   2,
    "o":   2,
    "p":   2,
    "q":   2,
    "r":   2,
    "s":   1,
    "t":   1,
    "u":   3,
    "v":   1,
    "w":   0,
    "x":   2,
    "y":   1,
    "z":   0,
    "{":   1,
    "|":   2,
    "}":   2,
    "~":   1,
    ".a":  1,
    ".A":  1,
    ".B":  1,
    ".c":  2,
    ".C":  2,
    ".d":  1,
    ".D":  2,
    ".e":  2,
    ".E":  1,
    ".f":  1,
    ".F":  2,
    ".h":  1,
    ".H":  1,
    ".l":  2,
    ".m":  2,
    ".M":  2,
    ".n":  1,
    ".N":  1,
    ".O":  1,
    ".p":  1,
    ".P":  2,
    ".q":  0,
    ".Q":  0,
    ".r":  1,
    ".R":  2,
    ".s":  2,
    ".S":  1,
    ".t":  2,
    ".u":  1,
    ".x":  1,
    ".z":  0,
    ".^":  3,
    ".&":  2,
    ".|":  2,
    ".<":  2,
    ".>":  2,
    ".*":  1,
    ".)":  1,
    ".(":  2,
    "._":  1,
    ".:":  2,
]


class ASTNode:
    def __init__(self, type, data, children=None):
        self.type = type
        self.data = data
        self.children = children or []


class Parser:
    def __init__(self, lex):
        self.lex = lex
        pass

    def parse(self):
        return parse_block(True)

    def parse_block(self, root=False):
        implicit_print = True
        children = []

        if not root:
            block = self.lex.get_token()

        while self.lex.has_token():
            tok = self.lex.peek_token()

            if tok.type == "symb" and tok.data == " ":
                implicit_print = False
                self.lex.get_token()
            elif tok.type == "symb" and tok.data in ");":
                if root:
                    self.lex.get_token()
                    continue

                if tok.data == ")": self.lex.get_token()
                break
            elif tok.type == "symb" and tok.data in BLOCK_TOKS:
                children.append((self.parse_block(), False))
                implicit_print = True
            else:
                children.append((self.parse_symbol(), implicit_print))
                implicit_print = True

        return ASTNode("block", "root" if root else block.data, children)

    def parse_symbol(self):
        tok = self.lex.get_token()

        if tok.type == "lit":
            return ASTNode("lit", tok.data)

        if tok.type == "symb" and tok.data in BLOCK_TOKS:
            raise RuntimeError(
                "error while parsing, block ({}) found, expression expected".format(tok.data)
            )

        children = []
        arity = ARITIES[tok.data]
        while arity:
            tok = self.lex.peek_token()

            if tok.type == "symb" and tok.data in ");":
                if tok.data == ")": self.lex.get_token()
                break

            children.append(self.parse_symbol())
            arity -= 1

        return ASTNode("expr", tok.data, children)
