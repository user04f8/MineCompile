import ast
import sys
import traceback
from typing import Literal, TextIO
import re

from pegen.tokenizer import tokenize, Tokenizer
from parse import MALpyParser
# python -m pegen mcpy.gram

CODE_BLOCK_OPEN = '__CODE_BLOCK_OPEN__'
CODE_BLOCK_CLOSE = '__CODE_BLOCK_CLOSE__'
DOLLAR_SIGN_TOKEN = '__HOOK__ '

class Parser:
    def __init__(self):
        pass

    def preprocess(self, code: str):
        def code_block_replacement(match: re.Match[str]) -> str:
            content = match.group(1)
            escaped_content = repr(content)
            return f'{CODE_BLOCK_OPEN}{escaped_content}{CODE_BLOCK_CLOSE}'
        
        code = re.compile(r'`([^`]*)`').sub(code_block_replacement, code)
        
        code = re.compile(r'\$').sub(DOLLAR_SIGN_TOKEN, code)
        
        return code

    def parse(self, code: str, filename: str = '', debug: Literal[0, 1, 2]=1):
        with open('tmp.malpytmp', 'w') as f:
            f.write(self.preprocess(code))
        with open('tmp.malpytmp', 'r') as f:
            tokengen = tokenize.generate_tokens(f.readline)
            tokenizer = Tokenizer(tokengen, verbose=debug >= 2)
            parser = MALpyParser(tokenizer, verbose=debug >= 2)
            tree = parser.start()

        if not tree:
            err = parser.make_syntax_error(filename)
            traceback.print_exception(err.__class__, err, None)
            sys.exit(1)

        if debug >= 1:
            print('Generated tree:')
            print(ast.dump(tree))

        return tree


