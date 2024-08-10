from dataclasses import dataclass
from interpret import parse_interp

import token

# example usage:
# python test.py malpy.gram

EXAMPLE_FILENAME = r'example.malpy'

if __name__ == '__main__':
    try:
        from pegen.__main__ import main as pegen_main
        pegen_main()
    except BaseException as e:
        print(f'WARN: pegen failed with {e}')
    
    parse_interp(EXAMPLE_FILENAME)