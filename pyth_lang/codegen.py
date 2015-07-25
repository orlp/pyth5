EXPR_FUNC = {
    '!':  'Pnot',
    ']':  'one_list',
    ',':  'pair',
    '_':  'neg',
    '+':  'plus',
    '-':  'minus',
    '*':  'times',
    '^':  'power',
    '<':  'less_than',
    '>':  'greater_than',
    '`':  'Prepr',
    '}':  'Pin',
    'h':  'head',
    'l':  'Plen',
    'p':  'Pprint',
    'q':  'equals',
    's':  'Psum',
    't':  'tail',
    'L':  'L',
    'S':  'Psorted',
    'U':  'unary_range',
    '.!': 'factorial',
    '.<':  'leftshift',
    '.>':  'rightshift',
}

# Simple patterns.
EXPR_PATTERNS = {
    '&':       {2: '({} and {})'},
    '|':       {2: '({} or {})'},
    '?':       {3: '({1} if {0} else {2})'},
    '=':       {2: "assign('{}', {})"},
    'init-x':  {1: "assign('x', {})"},
    'init-y':  {1: "assign('y', {})"},
}

# Lambda pattern. 0 is the lambda variable(s) separated by commas, the rest are arguments.
LAMBDA_VARS = "abcde"
EXPR_LAMBDA_PATTERNS = {
    'm':       {2: '[{2} for {0} in makeiter({1})]'},
    'o':       {2: 'order_by({1}, lambda {0}: {2})'},
    'init-L':  {1: "assign('L', lambda {0}: {1})",
                2: "assign('L', lambda {0}: {1})({2})"}
}


class CodegenError(Exception):
    pass


class Codegen:
    def __init__(self, parser):
        self.ast = parser.parse()
        self.arity_seen = set()
        self.lambda_var = 0

    def gen_code(self):
        return "\n".join(self._gen_block(self.ast))

    def _gen_block(self, node, level=0):
        assert node.type == 'block'

        lines = []
        for child, implicit_print in node.children:
            if child.type == 'block':
                child_code = self._gen_block(child)
            elif child.type == 'expr':
                child_code = self._gen_expr(child)
            elif child.type == 'lit':
                child_code = self._gen_lit(child)
            else:
                raise CodegenError("unknown child type: '{}'".format(child.type))

            if implicit_print:
                child_code = 'autoprint(' + child_code + ')'

            if child.type == 'block':
                lines += child_code
            else:
                lines.append(child_code)

        if node.data == 'F':
            lines = [" "*4 + line for line in lines]
            lines = ['for {} in makeiter({}):'.format(node.variable.data, self._gen_expr(node.iterable))] + lines
        elif node.data == 'B':
            lines = ['break']
        elif node.data != 'root':
            raise CodegenError("unknown block type: '{}'".format(node.data))

        return lines

    def _gen_expr(self, node):
        assert node.type == 'expr' or node.type == 'lit'

        if node.type == 'lit':
            return self._gen_lit(node)

        if node.data == '[':
            return '[{}]'.format(', '.join(map(self._gen_expr, node.children)))

        if node.data in EXPR_LAMBDA_PATTERNS:
            patterns = EXPR_LAMBDA_PATTERNS[node.data]
            if len(node.children) not in patterns:
                raise CodegenError("arity of '{}' must be one of {}".format(node.data, sorted(patterns.keys())))
            var = LAMBDA_VARS[self.lambda_var % len(LAMBDA_VARS)]
            self.lambda_var += 1
            exprs = [self._gen_expr(child) for child in node.children]
            self.lambda_var -= 1
            return patterns[len(node.children)].format(var, *exprs)

        if node.data in EXPR_PATTERNS:
            patterns = EXPR_PATTERNS[node.data]
            if len(node.children) not in patterns:
                raise CodegenError("arity of '{}' must be one of {}".format(node.data, sorted(patterns.keys())))
            return patterns[len(node.children)].format(*map(self._gen_expr, node.children))

        if node.data in EXPR_FUNC:
            children = map(self._gen_expr, node.children)
            return '{}({})'.format(EXPR_FUNC[node.data], ', '.join(children))

        raise CodegenError("AST node ('{}', '{}') not implemented".format(node.type, node.data))

    def _gen_lit(self, node):
        if node.data[-1] in '0123456789.':
            return "Real('{}')".format(node.data)

        if node.data.startswith('$'):
            return 'dollar_' + node.data[1:]

        return node.data
