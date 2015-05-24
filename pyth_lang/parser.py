# To stay consistent, we keep all symbols in the following order where possible:
# <space>
# <newline>
# !"#$%&'()*+,-/:;<=>?@[\]^_`{|}~abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ
# <.symbols>


BLOCK_TOKS = ''

ARITIES = {
    '!': 1,
    '*': 2,
    '+': 2,
    ',': 2,
    '-': 2,
    '[': -1,
    ']': 1,
    '_': 1,
    '`': 1,
    'h': 1,
    'l': 1,
    'p': 1,
    't': 1,
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


def parse_symbol(lex):
    tok = lex.get_token()

    if tok.type == 'lit':
        return ASTNode('lit', tok.data)

    if tok.type == 'symb' and tok.data in BLOCK_TOKS:
        raise ParserError(
            'error while parsing, block ({}) found, expression expected'
            .format(tok.data)
        )

    if tok.data not in ARITIES:
        raise ParserError("symbol not implemented: '{}'".format(tok.data))

    data = tok.data
    children = []
    arity = ARITIES[tok.data]
    while arity and lex.has_token():
        tok = lex.peek_token()

        # Handle early symbol close );.
        if tok.type == 'symb' and tok.data in ');':
            # Do not consume ; - it let trickle up to the root.
            if tok.data == ')':
                lex.get_token()
            break

        # Ignore spaces - only used to seperate tokens.
        if tok.type == 'symb' and tok.data == ' ':
            lex.get_token()
            continue

        children.append(parse_symbol(lex))
        arity -= 1

    return ASTNode('expr', data, children)


def parse_block(lex, root=False):
    implicit_print = True
    children = []

    if not root:
        block = lex.get_token()

    while lex.has_token():
        tok = lex.peek_token()

        if tok.type == 'symb' and tok.data == ' ':
            implicit_print = False
            lex.get_token()
        elif tok.type == 'symb' and tok.data in ');':
            # Ignore symbol exit if we're root.
            if root:
                lex.get_token()
                continue

            # Do not consume ; - it let trickle up to the root.
            if tok.data == ')':
                lex.get_token()
            break
        elif tok.type == 'symb' and tok.data in BLOCK_TOKS:
            children.append((parse_block(lex), False))
            implicit_print = True
        else:
            children.append((parse_symbol(lex), implicit_print))
            implicit_print = True

    return ASTNode('block', 'root' if root else block.data, children)


def parse(lex):
    return parse_block(lex, True)
