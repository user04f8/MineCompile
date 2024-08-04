import ast
from typing import TextIO
import re

from pegen.tokenizer import tokenize, Tokenizer
from parse import GeneratedParser
# python -m pegen mcpy.gram

CODE_BLOCK_PLACEHOLDER = '__CODE_BLOCK__'

class Parser:
    def __init__(self):
        pass

    def preprocess(self, code: str):
        pattern = re.compile(r'`([^`]*)`')
        def replacement(match: re.Match[str]) -> str:
            content = match.group(1)
            escaped_content = repr(content)
            return f'{CODE_BLOCK_PLACEHOLDER}({escaped_content})'
        
        return pattern.sub(replacement, code)

    def parse(self, file: TextIO):
        tokengen = tokenize.generate_tokens(file.readline)
        tokenizer = Tokenizer(tokengen, verbose=False)
        parser = GeneratedParser(tokenizer, verbose=False)
        tree = parser.start()

        print(tree)
        print(ast.dump(tree))
