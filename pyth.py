import argparse

import lexer
import parser
import codegen
import env


def cli():
    argparser = argparse.ArgumentParser(description="Pyth interpreter.")
    argparser.add_argument("file", help="Pyth file to run")
    args = argparser.parse_args()

    with open(args.file, "rb") as source:
        lex = lexer.Lexer(source.read())
        ast = parser.parse(lex)
        code = codegen.gen_code(ast)
        env.run(code)

if __name__ == "__main__":
    cli()

