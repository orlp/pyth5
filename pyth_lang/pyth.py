import argparse
import io
import sys

from . import lexer
from . import parser
from . import codegen
from . import env


__version__ = "5.0preview0"


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

    return result, error


def interpret(source):
    lex = lexer.Lexer(source)
    ast = parser.parse(lex)
    code = codegen.gen_code(ast)
    env.run(code)


def cli():
    argparser = argparse.ArgumentParser(description="Pyth interpreter.")
    argparser.add_argument("file", help="Pyth file to run")
    args = argparser.parse_args()

    with open(args.file, "rb") as source:
        interpret(source.read())

if __name__ == "__main__":
    cli()
