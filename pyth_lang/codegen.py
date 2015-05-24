EXPR_FUNC = {
    '!': 'Pnot',
    '*': 'times',
    '+': 'plus',
    ',': 'pair',
    '-': 'minus',
    ']': 'one_list',
    '_': 'neg',
    '`': 'Prepr',
    'h': 'head',
    'l': 'Plen',
    'p': 'Pprint',
    't': 'tail',
    'L': 'L',
}


class CodegenError(Exception):
    pass


class Codegen:
    def __init__(self, parser):
        self.ast = parser.parse()
        self.seen_lambda = set()

    def gen_code(self):
        return self._gen_block(self.ast)

    def _gen_block(self, node, level=0):
        assert node.type == 'block'

        lines = []
        for child, implicit_print in node.children:
            if child.type == 'block':
                child_code = self._gen_block(child)
            elif child.type == 'expr':
                child_code = self._gen_expr(child)
            elif child.type == 'lit':
                child_code = child.data
            else:
                raise CodegenError("unknown child type: '{}'".format(child.type))

            if implicit_print:
                child_code = 'autoprint(' + child_code + ')'

            lines.append(child_code)

        return '\n'.join(lines)

    def _gen_expr(self, node):
        assert node.type == 'expr' or node.type == 'lit'

        if node.type == 'lit':
            return node.data
        if node.data == '[':
            return '[{}]'.format(', '.join(map(self._gen_expr, node.children)))
        if node.data == '=':
            return "assign('{}', {})".format(node.children[0].data, self._gen_expr(node.children[1]))
        if node.data == 'L' and 'L' not in self.seen_lambda:
            self.seen_lambda.add('L')
            return "def L(b):\n    return {}".format(self._gen_expr(node.children[0]))
        if node.data in EXPR_FUNC:
            children = map(self._gen_expr, node.children)
            return '{}({})'.format(EXPR_FUNC[node.data], ', '.join(children))

        raise CodegenError("AST node ('{}', '{}') not implemented".format(node.type, node.data))
