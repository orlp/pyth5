import argparse
import io
import sys

from .lexer import Lexer
from .parser import Parser
from .codegen import Codegen
from . import env


__version__ = '5.0preview0'


def interpret(source):
    lexer = Lexer(source)
    parser = Parser(lexer)
    codegen = Codegen(parser)
    env.run(codegen.gen_code())


def run_code(source, stdin=''):
    error = None

    try:
        sys.stdout = io.StringIO()
        sys.stdin = io.StringIO(stdin)
        interpret(source.encode('utf-8'))
    except SystemExit:
        pass
    except Exception as e:
        error = e
    finally:
        result = sys.stdout.getvalue()
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__

    return result, error


def cli():
    argparser = argparse.ArgumentParser("pyth", description='Pyth interpreter.')
    argparser.add_argument("file", nargs="?", default="", help='Pyth file to run')
    argparser.add_argument("-c", "--code", help='Pyth code to run. Only used if file is not given.')
    argparser.add_argument("-d", "--debug", action="store_true", help='Show input and generated code.')
    argparser.set_defaults(debug=False)
    args = argparser.parse_args()

    assert args.file or args.code

    if args.file:
        with open(args.file, 'rb') as source:
            lex = lexer.Lexer(source.read())
    elif args.code:
        lex = lexer.Lexer(bytes(args.code, 'utf-8'))

    if args.debug:
        src = lexer.preprocessed_source()
        print('{:=^50}'.format(' ' + str(len(src)) + ' bytes '))
        print(src.decode(sys.stdout.encoding, errors='ignore'))
        print('='*50)

    parser = Parser(lexer)
    codegen = Codegen(parser)
    code = codegen.gen_code()

    if args.debug:
        print(code)
        print('='*50)

    env.run(code)

if __name__ == '__main__':
    cli()
