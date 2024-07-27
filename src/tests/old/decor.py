from langcraft import *

@metafun()
def test(x):
    Statement(f'say {x}')

@public
def main():
    test('Hello, world!')
    Statement(f'execute run {test("bye", __lambda__=True)}')

display_all()
