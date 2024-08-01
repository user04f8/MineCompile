from langcraft import *
from .utils import test

@test()
def test0():
    @public
    def debug():
        Debug()

@test()
def test1():
    @fun
    def callee():
        Statement('say here')

    @public
    def caller():
        callee()

