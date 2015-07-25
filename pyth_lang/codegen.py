import collections


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
    '&': {2: '({} and {})'},
    '|': {2: '({} or {})'},
    '?': {3: '({1} if {0} else {2})'},
    '=': {2: "assign('{}', {})"},
}

# Variables to cycle through for lambda functions.
EXPR_LAMBDA_VAR = {
    'm': ('d', 'k', 'b'),
    'o': ('N', 'Z'),
}

# Lambda pattern. 0 is the lambda variable(s), the rest are arguments.
EXPR_LAMBDA_PATTERNS = {
    'm': {2: '[{2} for {0} in makeiter({1})]'},
    'o': {2: 'order_by({1}, lambda {0}: {2})'},
}


class CodegenError(Exception):
    pass


class Codegen:
    def __init__(self, parser):
        self.ast = parser.parse()
        self.arity_seen = set()
        self.lambda_var_cycle = collections.defaultdict(int)

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

        if node.data == 'L' and 'L' not in self.arity_seen:
            self.arity_seen.add('L')
            code = "assign('L', lambda b: {})".format(self._gen_expr(node.children[0]))
            if len(node.children) > 1:
                code += '({})'.format(', '.join(map(self._gen_expr, node.children[1:])))
            return code

        if node.data in EXPR_LAMBDA_PATTERNS:
            patterns = EXPR_LAMBDA_PATTERNS[node.data]
            if len(node.children) not in patterns:
                raise CodegenError("arity of '{}' must be one of {}".format(node.data, sorted(patterns.keys())))
            var_cycle = EXPR_LAMBDA_VAR[node.data]
            var = var_cycle[self.lambda_var_cycle[node.data] % len(var_cycle)]
            self.lambda_var_cycle[node.data] += 1
            exprs = [self._gen_expr(child) for child in node.children]
            self.lambda_var_cycle[node.data] -= 1
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

        return node.data
