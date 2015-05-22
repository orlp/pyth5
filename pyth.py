import argparse
import io
import sys

import lexer
import parser
import codegen
import env


def run_code(source, stdin=""):
    error = None

    try:
        sys.stdout = io.StringIO()
        sys.stdin = io.StringIO(stdin)
        interpret(source.encode("utf-8"))
    except SystemExit:
        pass
    except Exception as e:
        error = e
    finally:
        result = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

    print(result)

    return result, error


def interpret(source):
    lex = lexer.Lexer(source)
    print(parser)
    ast = parser.parse(lex)
    code = codegen.gen_code(ast)
    env.run(code)


def cli():
    argparser = argparse.ArgumentParser(description="Pyth interpreter.")
    argparser.add_argument("file", help="Pyth file to run")
    args = argparser.parse_args()

    with open(args.file, "rb") as source:
        interpret(source)

if __name__ == "__main__":
    cli()
