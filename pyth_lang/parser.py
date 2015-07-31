# To stay consistent, we keep all symbols in the following order where possible:
# <space>
# <newline>
# "\!&|?();[],_+-*/%^=<>:@{}`'~#
# abcdefghijklmnopqrstuvwxyz
# ABCDEFGHIJKLMNOPQRSTUVWXYZ
# <.symbols>


VARIABLES = ['a', 'b', 'c', 'd', 'e', 'w', 'x', 'y', 'z', '$a', '$q', '$A', '$Q']
NO_AUTOPRINT = {'=', '~', 'p'}
BLOCK_TOKS = '#BEFI'
INIT_FIRST_TIME = {'x', 'y', 'L'}

ARITIES = {
    '!':  1,
    '&':  2,
    '|':  2,
    '?':  3,
    '[': -1,
    ']':  1,
    ',':  2,
    '_':  1,
    '+':  2,
    '-':  2,
    '*':  2,
    '^':  2,
    '<':  2,
    '>':  2,
    '`':  1,
    '}':  2,
    'f':  2,
    'h':  1,
    'l':  1,
    'm':  2,
    'n':  2,
    'o':  2,
    'p':  1,
    'q':  2,
    's':  1,
    't':  1,
    'H':  1,
    'L':  1,
    'S':  1,
    'T':  1,
    'U':  1,
    '.!': 1,
    '.<': 2,
    '.>': 2,
}

for var in VARIABLES:
    ARITIES[var] = 0


class ParserError(Exception):
    pass


class ASTNode:
    def __init__(self, type, data, args=None, children=None):
        self.type = type
        self.data = data
        self.args = args or []
        self.children = children or []

    def __repr__(self):
        return 'ASTNode({!r}, {!r}, {!r})'.format(self.type, self.data, self.args)


class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.seen_init = set()
        self.else_propagate = False

    def parse(self):
        return self._parse_block(True)

    def _parse_expr(self, start_tok=None):
        tok = start_tok or self.lex.get_token()

        if tok.data in INIT_FIRST_TIME and tok.data not in self.seen_init:
            return self._parse_init(tok)

        if tok.type == 'lit' or tok.type == 'symb' and tok.data in VARIABLES:
            return ASTNode('lit', tok.data)

        if tok.data in BLOCK_TOKS:
            raise ParserError(
                'error while parsing, block ({}) found, expression expected'
                .format(tok.data)
            )

        if tok.data in '=~':
            return self._parse_assign(tok.data)

        if tok.data not in ARITIES:
            raise ParserError("symbol not implemented: '{}'".format(tok.data))

        data = tok.data
        args = []
        arity = ARITIES[tok.data]

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

            args.append(self._parse_expr())
            arity -= 1

        return ASTNode('expr', data, args)

    def _parse_assign(self, data):
        assign_var = self.lex.get_token()
        if assign_var.type != 'symb':
            raise ParserError("expected symbol after '{}'".format(data))

        if assign_var.data in VARIABLES:
            return ASTNode('expr', data, [ASTNode('lit', assign_var.data, []), self._parse_expr()])

        start_tok = assign_var
        if start_tok.data not in ARITIES or ARITIES[start_tok.data] < 1:
            raise ParserError("expected variable or function after '{}'".format(data))

        # We peek to keep the variable in the lexer as first argument.
        assign_var = self.lex.peek_token()
        if assign_var.type != 'symb' or assign_var.data not in VARIABLES:
            raise ParserError("expected variable after '{}{}'".format(data, start_tok.data))

        return ASTNode('expr', data, [ASTNode('lit', assign_var.data, []), self._parse_expr(start_tok)])

    def _parse_init(self, tok):
        self.seen_init.add(tok.data)
        init_expr = self._parse_expr()
        actual_expr = self._parse_expr(tok)
        return ASTNode('expr', 'init-' + tok.data, [init_expr] + actual_expr.args)

    def _parse_block(self, root=False):
        implicit_print = True

        if not root:
            block_tok = self.lex.get_token()

        block = ASTNode('block', 'root' if root else block_tok.data)

        if block.data in 'IF':
            block.args = [self._parse_expr()]

        while self.lex.has_token():
            tok = self.lex.peek_token()

            # Suppress autoprint.
            if tok.type == 'symb' and tok.data == ' ':
                self.lex.get_token()
                implicit_print = False

            # Handle break.
            elif tok.type == 'symb' and tok.data == 'B':
                self.lex.get_token()
                block.children.append((ASTNode('block', 'B'), False))
                implicit_print = True
                break

            # Handle else.
            elif tok.type == 'symb' and tok.data == 'E':
                # Either we're in stage two of the implicit ) of E, or we are right after a break.
                after_break = (block.children and block.children[-1][0].children
                               and block.children[-1][0].children[-1][0].data == 'B')
                if self.else_propagate or after_break:
                    block.children.append((self._parse_block(), False))
                    implicit_print = True
                    self.else_propagate = False
                else:
                    if root:
                        raise ParserError('else used at root level')
                    self.else_propagate = True
                    break

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
                block.children.append((self._parse_block(), False))
                implicit_print = True
            else:
                expr = self._parse_expr()
                # Don't autoprint if we're only defining.
                if expr.data.startswith('init-') and len(expr.args) == 1:
                    implicit_print = False
                if tok.type == 'symb' and tok.data in NO_AUTOPRINT:
                    implicit_print = False

                block.children.append((expr, implicit_print))
                implicit_print = True

        return block
