import lexer
import parser
import codegen


lex = lexer.Lexer(open("test.pyth", "rb").read())
ast = parser.parse(lex)


print(ast)
print(codegen.gen_code(ast))
