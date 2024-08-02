from .utils import tests

def run_tests():

    
    for i, test in enumerate(tests):
        print(f'Running test {i+1}/{len(tests)}')
        test()

