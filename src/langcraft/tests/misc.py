from langcraft import *
from langcraft.base import PublicFun
from .utils import test
test = test(__name__)

@test
def test0():
    @public
    def debug():
        Debug()

@test
def test1():
    @fun
    def callee():
        Statement('say here')

    @public
    def caller():
        callee()

@test
def nested():
    with Fun() as f:
        Statement('say hi')
        with Fun() as g:
            f()
        g()

    with PublicFun('main'):
        f()
        g()


@test
def test2():
    with Fun() as recursive:
        Statement('say here')
        @fun
        def nested():
            Statement('say there')
            with If(Condition('block ~ ~ ~ air')):
                recursive()

        Statement('say here again')

        nested()


    @lambda_metafun()
    def parametric(x):
        Statement(f'say {x}')

    @public
    def caller():
        recursive()

        parametric('asdf')

