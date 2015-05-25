# To stay consistent, we keep all symbols in the following order where possible:
# <space>
# <newline>
# !"#$%&'()*+,-/:;<=>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# <.symbols>

VARIABLES = 'bZ'
NEVER_PRINT = {'='}
BLOCK_TOKS = ''
LAMBDA_TOKS = {'L'}

ARITIES = {
    '!': 1,
    '&': 2,
    '*': 2,
    '+': 2,
    ',': 2,
    '-': 2,
    '<': 2,
    '=': 2,
    '?': 3,
    '[': -1,
    ']': 1,
    '^': 2,
    '_': 1,
    '`': 1,
    '|': 2,
    'b': 0,
    'h': 1,
    'l': 1,
    'p': 1,
    'q': 2,
    't': 1,
    'L': 1,
    'U': 1,
    'Z': 0,
}


class ParserError(Exception):
    pass


class ASTNode:
    def __init__(self, type, data, children=None):
        self.type = type
        self.data = data
        self.children = children or []

    def __str__(self, level=0):
        r = '  ' * level + '{} {}'.format(self.type, self.data)
        for child in self.children:
            if self.type == 'block':
                child = child[0]
            r += '\n' + child.__str__(level + 1)
        return r

    def __repr__(self):
        return 'ASTNode({!r}, {!r}, {!r})'.format(self.type, self.data, self.children)


class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.seen_lambda = set()

    def parse(self):
        return self._parse_block(True)

    def _parse_expr(self):
        tok = self.lex.get_token()

        if tok.type == 'lit' or tok.type == 'symb' and tok.data in VARIABLES:
            return ASTNode('lit', tok.data)

        if tok.data in BLOCK_TOKS:
            raise ParserError(
                'error while parsing, block ({}) found, expression expected'
                .format(tok.data)
            )

        if tok.data == '=':
            var = self.lex.peek_token()
            if var.type != 'symb' or var.data not in VARIABLES:
                raise ParserError("expected variable after '='")

        if tok.data not in ARITIES:
            raise ParserError("symbol not implemented: '{}'".format(tok.data))

        data = tok.data
        children = []
        arity = ARITIES[tok.data]

        if tok.data in LAMBDA_TOKS and tok.data not in self.seen_lambda:
            self.seen_lambda.add(tok.data)
            arity += 1

        while arity and self.lex.has_token():
            tok = self.lex.peek_token()

            # Handle early symbol close );.
            if tok.type == 'symb' and tok.data in ');':
                # Do not consume ; - let it trickle up to the root.
                if tok.data == ')':
                    self.lex.get_token()
                break

            # Ignore spaces - only used to seperate tokens.
            if tok.type == 'symb' and tok.data == ' ':
                self.lex.get_token()
                continue

            children.append(self._parse_expr())
            arity -= 1

        return ASTNode('expr', data, children)

    def _parse_block(self, root=False):
        implicit_print = True
        children = []

        if not root:
            block = self.lex.get_token()

        while self.lex.has_token():
            tok = self.lex.peek_token()

            if tok.type == 'symb' and tok.data == ' ':
                implicit_print = False
                self.lex.get_token()
            elif tok.type == 'symb' and tok.data in ');':
                # Ignore symbol exit if we're root.
                if root:
                    self.lex.get_token()
                    continue

                # Do not consume ; - let it trickle up to the root.
                if tok.data == ')':
                    self.lex.get_token()
                break
            elif tok.type == 'symb' and tok.data in BLOCK_TOKS:
                children.append((self._parse_block(), False))
                implicit_print = True
            else:
                if tok.type == 'symb' and tok.data in LAMBDA_TOKS and tok.data not in self.seen_lambda:
                    expr = self._parse_expr()
                    if len(expr.children) == 1:
                        implicit_print = False
                else:
                    expr = self._parse_expr()

                if tok.type == 'symb' and tok.data in NEVER_PRINT:
                    implicit_print = False
                children.append((expr, implicit_print))
                implicit_print = True

        return ASTNode('block', 'root' if root else block.data, children)
