import json
import sys

from parse import parse
from tex_ast import serialization
import argparse

def dump_ast(tex: str):
    ast = parse.parse_program(tex)

    print(json.dumps(ast, indent=4, cls=serialization.ASTNodeEncoder))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--ast', action='store_true')
    args = parser.parse_args()

    # TODO: No args, read stdin instead
    if args.ast:
        #with open(sys.stdin, 'r') as f:
        #    dump_ast(f.read())
        dump_ast(sys.stdin.read())