# To stay consistent, we keep all symbols in the following order where possible:
# <space>
# <newline>
# "\!&|?();[],_+-*/%^=<>:@{}`'~#
# abcdefghijklmnopqrstuvwxyz
# ABCDEFGHIJKLMNOPQRSTUVWXYZ
# <.symbols>


VARIABLES = ['a', 'b', 'c', 'd', 'e', 'w', 'x', 'y', 'z', '$a', '$q', '$A', '$Q']
NO_AUTOPRINT = {'=', 'p'}
BLOCK_TOKS = 'FB'
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
    '=':  2,
    '<':  2,
    '>':  2,
    '`':  1,
    '}':  2,
    'h':  1,
    'l':  1,
    'm':  2,
    'o':  2,
    'p':  1,
    'q':  2,
    's':  1,
    't':  1,
    'L':  1,
    'S':  1,
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
    def __init__(self, type, data, children=None, attrib=None):
        self.type = type
        self.data = data
        self.children = children or []
        self.attrib = attrib or {}

    def __repr__(self):
        return 'ASTNode({!r}, {!r}, {!r})'.format(self.type, self.data, self.children)


class Parser:
    def __init__(self, lex):
        self.lex = lex
        self.seen_init = set()

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

        if tok.data not in ARITIES:
            raise ParserError("symbol not implemented: '{}'".format(tok.data))

        if tok.data == '=':
            return self._parse_assign()

        data = tok.data
        children = []
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

            children.append(self._parse_expr())
            arity -= 1

        return ASTNode('expr', data, children)

    def _parse_assign(self):
        assign_var = self.lex.get_token()
        if assign_var.type != 'symb':
            raise ParserError("expected symbol after '='")

        if assign_var.data in VARIABLES:
            return ASTNode('expr', '=', [ASTNode('lit', assign_var.data, []), self._parse_expr()])

        start_tok = assign_var
        if start_tok.data not in ARITIES or ARITIES[start_tok.data] < 1 or start_tok.data == '=':
            raise ParserError("expected function after '='")

        # We peek to keep the variable in the lexer as first argument.
        assign_var = self.lex.peek_token()
        if assign_var.type != 'symb' or assign_var.data not in VARIABLES:
            raise ParserError("expected variable after '={}'".format(start_tok.data))

        return ASTNode('expr', '=', [ASTNode('lit', assign_var.data, []), self._parse_expr(start_tok)])

    def _parse_init(self, tok):
        self.seen_init.add(tok.data)
        init_expr = self._parse_expr()
        actual_expr = self._parse_expr(tok)
        return ASTNode('expr', 'init-' + tok.data, [init_expr] + actual_expr.children)

    def _parse_block(self, root=False):
        implicit_print = True

        if not root:
            block_tok = self.lex.get_token()

        block = ASTNode('block', 'root' if root else block_tok.data)

        if block.data == 'F':
            block.iterable = self._parse_expr()

        while self.lex.has_token():
            tok = self.lex.peek_token()

            # Suppress autoprint.
            if tok.type == 'symb' and tok.data == ' ':
                self.lex.get_token()
                implicit_print = False

            # Handle break.
            elif tok.type == 'symb' and tok.data in 'B':
                self.lex.get_token()
                block.children.append((ASTNode('block', 'B'), False))
                implicit_print = True

                if not root:
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
                if expr.data.startswith('init-') and len(expr.children) == 1:
                    implicit_print = False
                if tok.type == 'symb' and tok.data in NO_AUTOPRINT:
                    implicit_print = False

                block.children.append((expr, implicit_print))
                implicit_print = True

        return block
