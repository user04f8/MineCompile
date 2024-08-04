import ast

from pegen.tokenizer import tokenize, Tokenizer
from parse import GeneratedParser
# python -m pegen mcpy.gram

class Parser:
    def __init__(self):
        pass

    def parse(self, file):
        tokengen = tokenize.generate_tokens(file.readline)
        tokenizer = Tokenizer(tokengen, verbose=False)
        parser = GeneratedParser(tokenizer, verbose=False)
        tree = parser.start()

        print(tree)
        print(ast.dump(tree))
