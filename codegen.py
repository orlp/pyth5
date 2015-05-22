class CodegenError(Exception):
    pass


def gen_preamble(ast):
    return ""


def gen_expr(ast):
    return ""


def gen_block(ast, level=0):
    assert ast.type == "block"

    lines = []
    for child, implicit_print in ast.children:
        if child.type == "block":
            child_code = gen_block(child)
        elif child.type == "expr":
            child_code = gen_expr(child)
        elif child.type == "lit":
            child_code = child
        else:
            raise CodegenError("unknown child type: '{}'".format(child.type))

        if implicit_print:
            child_code = "Pprint(" + child_code + ")"

        lines.append(child_code)

    return "\n".join(lines)


def gen_code(ast):
    assert ast.type == "block" and ast.data == "root"
    return gen_preamble(ast) + gen_block(ast)
