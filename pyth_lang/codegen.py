# Simple one-to-one function translation.
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
    'n':  'not_equals',
    'p':  'Pprint',
    'q':  'equals',
    's':  'Psum',
    't':  'tail',
    'H':  'end',
    'L':  'L',
    'S':  'Psorted',
    'T':  'pop',
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
    '~':       {2: "post_assign('{}', {})"},
    'init-x':  {1: "assign('x', {})"},
    'init-y':  {1: "assign('y', {})"},
}

# Lambda pattern. 0 is the lambda variable(s) separated by commas, the rest are arguments.
LAMBDA_VARS = 'abcde'
EXPR_LAMBDA_PATTERNS = {
    'f':       {1: 'Pfilter(Real(1), lambda {0}: {1})',
                2: 'Pfilter({1}, lambda {0}: {2})'},
    'm':       {2: '[{2} for {0} in makeiter({1})]'},
    'o':       {2: 'order_by({1}, lambda {0}: {2})'},
    'init-L':  {1: "assign('L', lambda {0}: {1})",
                2: "assign('L', lambda {0}: {1})({2})"}
}

# Block patterns. In order: block indentation, prologue and epilogue. Arguments are given through format parameters.
BLOCK_PATTERNS = {
    'I': [1, ['if {0}:'], []],
    '#': [2, ['while True:', '    try:'], ['    except Exception:', '        break']],
    'B': [0, [], ['break']],
    'F': [1, ['for {0} in makeiter({1}):'], []]
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

        args = [self._gen_expr(arg) for arg in node.args]

        if node.data == 'F':
            self.lambda_var += 1

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
            self.lambda_var -= 1
            args.insert(0, LAMBDA_VARS[self.lambda_var % len(LAMBDA_VARS)])

        if node.data in BLOCK_PATTERNS:
            ident, prologue, epilogue = BLOCK_PATTERNS[node.data]
            prologue = [line.format(*args) for line in prologue]
            epilogue = [line.format(*args) for line in epilogue]
            lines = prologue + [" "*(4 * ident) + line for line in lines] + epilogue
        elif node.data != 'root':
            raise CodegenError("unknown block type: '{}'".format(node.data))

        return lines

    def _gen_expr(self, node):
        assert node.type == 'expr' or node.type == 'lit'

        if node.type == 'lit':
            return self._gen_lit(node)

        if node.data == '[':
            return '[{}]'.format(', '.join(map(self._gen_expr, node.args)))

        if node.data in EXPR_LAMBDA_PATTERNS:
            patterns = EXPR_LAMBDA_PATTERNS[node.data]
            if len(node.args) not in patterns:
                raise CodegenError("arity of '{}' must be one of {}".format(node.data, sorted(patterns.keys())))
            var = LAMBDA_VARS[self.lambda_var % len(LAMBDA_VARS)]
            self.lambda_var += 1
            exprs = [self._gen_expr(arg) for arg in node.args]
            self.lambda_var -= 1
            return patterns[len(node.args)].format(var, *exprs)

        if node.data in EXPR_PATTERNS:
            patterns = EXPR_PATTERNS[node.data]
            if len(node.args) not in patterns:
                raise CodegenError("arity of '{}' must be one of {}".format(node.data, sorted(patterns.keys())))
            return patterns[len(node.args)].format(*map(self._gen_expr, node.args))

        if node.data in EXPR_FUNC:
            args = map(self._gen_expr, node.args)
            return '{}({})'.format(EXPR_FUNC[node.data], ', '.join(args))

        raise CodegenError("AST node ('{}', '{}') not implemented".format(node.type, node.data))

    def _gen_lit(self, node):
        if node.data[-1] in '0123456789.':
            return "Real('{}')".format(node.data)

        if node.data.startswith('$'):
            return 'dollar_' + node.data[1:]

        return node.data
