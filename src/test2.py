from langcraft import *

class Test:
    def __init__(self):
        with Fun('asdfjkl') as self.f:
            Statement('say hi')

Test().f()

with TickingFun():
    Teleport(Loc(y=1))
    

display_all()