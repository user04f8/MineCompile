from langcraft.globals import GLOBALS

from .utils import tests

def run_tests():

    print(f'Running tests. . .')
    for i, test in enumerate(tests):
        
        test()
        print(f' - test completed ({i+1}/{len(tests)})')

        GLOBALS._reset()
