from dataclasses import dataclass
from pegen.__main__ import main as pegen_main
from interpret import parse_interp

import token

# example usage:
# python test.py malpy.gram

EXAMPLE_FILENAME = r'example.malpy'

def pegen_gen():
    # @dataclass
    # class PegenArg:
    #     grammar_filename: str = 'malpy.gram'
    #     output: str = 'parse.py'
    #     quiet: bool = False
    #     verbose: bool = False
    #     skip_actions: bool = False
        

    # class PegenArgParser:
    #     @staticmethod
    #     def parse_args():
    #         return PegenArg()
    
    # argparser = PegenArgParser()
    pegen_main()

if __name__ == '__main__':
    pegen_main()
    parse_interp(EXAMPLE_FILENAME)